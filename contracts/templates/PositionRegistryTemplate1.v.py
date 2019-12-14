# Vyper version of the Lendroid protocol v2
# THIS CONTRACT HAS NOT BEEN AUDITED!


from contracts.interfaces import MarketDao


# Structs
struct Position:
    borrower: address
    currency: address
    underlying: address
    currency_value: uint256
    underlying_value: uint256
    repaid_value: uint256
    status: uint256
    expiry: timestamp
    strike_price: uint256
    shield_market_hash: bytes32
    id: uint256


LST: public(address)
protocol_dao_address: public(address)
owner: public(address)
# dao_type => dao_address
daos: public(map(uint256, address))
# loan_id
last_position_id: public(uint256)
# expiry => (loan_id => Loan)
positions: public(map(uint256, Position))
# borrower_address => loan_count
borrow_position_count: public(map(address, uint256))
# borrower_address => (loan_id => borrow_position_count)
borrow_position_index: public(map(address, map(uint256, uint256)))
# borrower_address => (borrow_position_count => loan_id)
borrow_position: public(map(address, map(uint256, uint256)))
# nonreentrant locks for positions, inspired from https://github.com/ethereum/vyper/issues/1204
nonreentrant_position_locks: map(uint256, bool)

DAO_TYPE_MARKET: public(uint256)

LOAN_STATUS_ACTIVE: public(uint256)
LOAN_STATUS_LIQUIDATED: public(uint256)
LOAN_STATUS_CLOSED: public(uint256)

initialized: public(bool)
paused: public(bool)


@public
def initialize(
        _owner: address,
        _LST: address,
        _dao_address_market: address
    ) -> bool:
    assert not self.initialized
    self.initialized = True
    self.owner = _owner
    self.protocol_dao_address = msg.sender
    self.LST = _LST

    self.DAO_TYPE_MARKET = 1
    self.daos[self.DAO_TYPE_MARKET] = _dao_address_market

    self.LOAN_STATUS_ACTIVE = 1
    self.LOAN_STATUS_LIQUIDATED = 2
    self.LOAN_STATUS_CLOSED = 3

    return True


@private
@constant
def _loan_market_hash(_currency_address: address, _expiry: timestamp, _underlying_address: address) -> bytes32:
    return keccak256(
        concat(
            convert(self.protocol_dao_address, bytes32),
            convert(_currency_address, bytes32),
            convert(_expiry, bytes32),
            convert(_underlying_address, bytes32)
        )
    )


@private
@constant
def _shield_market_hash(_currency_address: address, _expiry: timestamp, _underlying_address: address, _strike_price: uint256) -> bytes32:
    return keccak256(
        concat(
            convert(self.protocol_dao_address, bytes32),
            convert(_currency_address, bytes32),
            convert(_expiry, bytes32),
            convert(_underlying_address, bytes32),
            convert(_strike_price, bytes32)
        )
    )


@private
def _lock_position(_id: uint256):
    assert self.nonreentrant_position_locks[_id] == False
    self.nonreentrant_position_locks[_id] = True


@private
def _unlock_position(_id: uint256):
    assert self.nonreentrant_position_locks[_id] == True
    self.nonreentrant_position_locks[_id] = False


@private
def _open_position(_borrower: address, _currency_value: uint256,
    _currency_address: address, _expiry: timestamp, _underlying_address: address, _strike_price: uint256):
    self.last_position_id += 1

    self.positions[self.last_position_id] = Position({
        borrower: _borrower,
        currency: _currency_address,
        underlying: _underlying_address,
        currency_value: _currency_value,
        underlying_value: as_unitless_number(_currency_value) / as_unitless_number(_strike_price),
        repaid_value: 0,
        status: self.LOAN_STATUS_ACTIVE,
        expiry: _expiry,
        strike_price: _strike_price,
        shield_market_hash: self._shield_market_hash(_currency_address, _expiry, _underlying_address, _strike_price),
        id: self.last_position_id
    })
    self.borrow_position_count[_borrower] += 1
    self.borrow_position_index[_borrower][self.last_position_id] = self.borrow_position_count[_borrower]
    self.borrow_position[_borrower][self.borrow_position_count[_borrower]] = self.last_position_id


@private
def _remove_position(_position_id: uint256):
    _borrower: address = self.positions[_position_id].borrower
    _current_position_index: uint256 = self.borrow_position_index[_borrower][_position_id]
    _last_position_index: uint256 = self.borrow_position_count[_borrower]
    _last_position_id: uint256 = self.borrow_position[_borrower][_last_position_index]
    self.borrow_position[_borrower][_current_position_index] = self.borrow_position[_borrower][_last_position_index]
    clear(self.borrow_position[_borrower][_last_position_index])
    clear(self.borrow_position_index[_borrower][_position_id])
    self.borrow_position_index[_borrower][_last_position_id] = _current_position_index
    self.borrow_position_count[_borrower] -= 1


@private
def _partial_or_complete_close_position(_position_id: uint256, _pay_value: uint256):
    self.positions[_position_id].repaid_value += as_unitless_number(_pay_value)
    if self.positions[_position_id].repaid_value == self.positions[_position_id].currency_value:
        self.positions[_position_id].status = self.LOAN_STATUS_CLOSED
        self._remove_position(_position_id)


@private
def _liquidate_position(_position_id: uint256):
    self.positions[_position_id].status = self.LOAN_STATUS_LIQUIDATED
    self._remove_position(_position_id)


# Admin functions

# Escape-hatches

@private
def _pause():
    assert not self.paused
    self.paused = True


@private
def _unpause():
    assert self.paused
    self.paused = False

@public
def pause() -> bool:
    assert self.initialized
    assert msg.sender == self.owner
    self._pause()
    return True


@public
def unpause() -> bool:
    assert self.initialized
    assert msg.sender == self.owner
    self._unpause()
    return True


# Non-admin functions


@public
def avail_loan(
    _currency_address: address, _expiry: timestamp, _underlying_address: address, _strike_price: uint256,
    _currency_value: uint256
    ) -> bool:
    assert self.initialized
    assert not self.paused
    assert block.timestamp < _expiry
    # create position
    self._open_position(msg.sender, _currency_value,
        _currency_address, _expiry, _underlying_address, _strike_price)
    assert_modifiable(MarketDao(self.daos[self.DAO_TYPE_MARKET]).open_position(
        msg.sender, _currency_value,
        _currency_address, _expiry, _underlying_address, _strike_price
    ))

    return True


@public
def repay_loan(_position_id: uint256, _pay_value: uint256) -> bool:
    assert self.initialized
    assert not self.paused
    assert block.timestamp < self.positions[_position_id].expiry
    # validate borrower
    assert self.positions[_position_id].borrower == msg.sender
    assert as_unitless_number(self.positions[_position_id].repaid_value) + as_unitless_number(_pay_value) <= as_unitless_number(self.positions[_position_id].currency_value)
    self._lock_position(_position_id)
    # validate position currencies
    assert_modifiable(MarketDao(self.daos[self.DAO_TYPE_MARKET]).close_position(
        self.positions[_position_id].borrower,
        _pay_value,
        self.positions[_position_id].currency,
        self.positions[_position_id].expiry,
        self.positions[_position_id].underlying,
        self.positions[_position_id].strike_price
    ))
    # close position
    self._partial_or_complete_close_position(_position_id, _pay_value)
    self._unlock_position(_position_id)

    return True


@public
def close_liquidated_loan(_position_id: uint256) -> bool:
    assert self.initialized
    assert not self.paused
    assert block.timestamp > self.positions[_position_id].expiry
    self._lock_position(_position_id)
    # validate position currencies
    _currency_value_remaining: uint256 = as_unitless_number(self.positions[_position_id].currency_value) - as_unitless_number(self.positions[_position_id].repaid_value)
    assert_modifiable(MarketDao(self.daos[self.DAO_TYPE_MARKET]).close_liquidated_position(
        self.positions[_position_id].borrower,
        _currency_value_remaining,
        self.positions[_position_id].currency,
        self.positions[_position_id].expiry,
        self.positions[_position_id].underlying,
        self.positions[_position_id].strike_price
    ))
    # liquidate position
    self._liquidate_position(_position_id)
    self._lock_position(_position_id)

    return True
