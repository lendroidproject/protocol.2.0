# Vyper version of the Lendroid protocol v2
# THIS CONTRACT HAS NOT BEEN AUDITED!


from contracts.interfaces import MarketDao


# Structs
struct Offer:
    creator: address
    lend_currency_value: uint256
    borrow_currency_value: uint256
    i_parent_address: address
    i_token_id: uint256
    s_quantity: uint256
    i_quantity: uint256
    i_unit_price_in_wei: wei_value
    expiry: timestamp
    shield_market_hash: bytes32
    id: uint256


struct Position:
    borrower: address
    lend_currency_value: uint256
    borrow_currency_value: uint256
    i_parent_address: address
    i_token_id: uint256
    i_quantity: uint256
    s_quantity: uint256
    status: uint256
    expiry: timestamp
    shield_market_hash: bytes32
    id: uint256


protocol_currency_address: public(address)
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
# offer_hash => Offer
offers: public(map(uint256, Offer))
# index per offer
last_offer_index: public(uint256)
# nonreentrant locks for positions, inspired from https://github.com/ethereum/vyper/issues/1204
nonreentrant_offer_locks: map(uint256, bool)

DAO_TYPE_MARKET: public(uint256)

LOAN_STATUS_ACTIVE: public(uint256)
LOAN_STATUS_LIQUIDATED: public(uint256)
LOAN_STATUS_CLOSED: public(uint256)

initialized: public(bool)


@private
@constant
def _is_initialized() -> bool:
    return self.initialized == True


@public
def initialize(
        _owner: address,
        _protocol_currency_address: address,
        _dao_address_market: address
    ) -> bool:
    assert not self._is_initialized()
    self.initialized = True
    self.owner = _owner
    self.protocol_dao_address = msg.sender
    self.protocol_currency_address = _protocol_currency_address

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
def _loan_and_collateral_amount(_shield_market_hash: bytes32, _s_quantity: uint256) -> (uint256, uint256):
    _strike_price: uint256 = MarketDao(self.daos[self.DAO_TYPE_MARKET]).shield_markets__strike_price(_shield_market_hash)
    _loan_amount: uint256 = as_unitless_number(_strike_price) * as_unitless_number(_s_quantity)
    _collateral_amount: uint256 = as_unitless_number(MarketDao(self.daos[self.DAO_TYPE_MARKET]).shield_markets__minimum_collateral_value(_shield_market_hash)) * as_unitless_number(_s_quantity) * (10 ** 18) / as_unitless_number(_strike_price)
    return _loan_amount, _collateral_amount


@private
def _lock_offer(_id: uint256):
    assert self.nonreentrant_offer_locks[_id] == False
    self.nonreentrant_offer_locks[_id] = True


@private
def _unlock_offer(_id: uint256):
    assert self.nonreentrant_offer_locks[_id] == True
    self.nonreentrant_offer_locks[_id] = False


@private
def _create_offer(
    _creator: address,
    _currency_address: address, _expiry: timestamp, _underlying_address: address, _strike_price: uint256,
    _s_quantity: uint256, _i_quantity: uint256, _i_unit_price_in_wei: wei_value):
    _shield_market_hash: bytes32 = self._shield_market_hash(_currency_address, _expiry, _underlying_address, _strike_price)
    _i_parent_address: address = ZERO_ADDRESS
    _i_token_id: uint256 = 0
    _i_parent_address, _i_token_id = MarketDao(self.daos[self.DAO_TYPE_MARKET]).i_currency_for_offer_creation(
        _creator,
        _s_quantity,
        _currency_address, _expiry, _underlying_address, _strike_price
    )
    _loan_amount: uint256 = 0
    _collateral_amount: uint256 = 0
    _loan_amount, _collateral_amount = self._loan_and_collateral_amount(_shield_market_hash, _s_quantity)
    self.offers[self.last_offer_index] = Offer({
        creator: _creator,
        lend_currency_value: _loan_amount,
        borrow_currency_value: _collateral_amount,
        i_parent_address: _i_parent_address,
        i_token_id: _i_token_id,
        s_quantity: _s_quantity,
        i_quantity: _i_quantity,
        i_unit_price_in_wei: _i_unit_price_in_wei,
        expiry: _expiry,
        shield_market_hash: _shield_market_hash,
        id: self.last_offer_index
    })
    self.last_offer_index += 1


@private
def _update_offer(_offer_id: uint256, _s_quantity: uint256, _i_quantity: uint256):
    _loan_amount: uint256 = 0
    _collateral_amount: uint256 = 0
    _loan_amount, _collateral_amount = self._loan_and_collateral_amount(
        self.offers[_offer_id].shield_market_hash, _s_quantity)
    self.offers[_offer_id].s_quantity = _s_quantity
    self.offers[_offer_id].i_quantity = _i_quantity
    self.offers[_offer_id].lend_currency_value = _loan_amount
    self.offers[_offer_id].borrow_currency_value = _collateral_amount


@private
def _remove_offer(_offer_id: uint256):
    if _offer_id < self.last_offer_index:
        self.offers[_offer_id] = Offer({
            creator: self.offers[self.last_offer_index].creator,
            lend_currency_value: self.offers[self.last_offer_index].lend_currency_value,
            borrow_currency_value: self.offers[self.last_offer_index].borrow_currency_value,
            i_parent_address: self.offers[self.last_offer_index].i_parent_address,
            i_token_id: self.offers[self.last_offer_index].i_token_id,
            s_quantity: self.offers[self.last_offer_index].s_quantity,
            i_quantity: self.offers[self.last_offer_index].i_quantity,
            i_unit_price_in_wei: self.offers[self.last_offer_index].i_unit_price_in_wei,
            expiry: self.offers[self.last_offer_index].expiry,
            shield_market_hash: self.offers[self.last_offer_index].shield_market_hash,
            id: _offer_id
        })
    clear(self.offers[self.last_offer_index])
    if self.last_offer_index > 0:
        self.last_offer_index -= 1


@private
def _open_position(_borrower: address, _offer_id: uint256):
    self.last_position_id += 1

    self.positions[self.last_position_id] = Position({
        borrower: _borrower,
        lend_currency_value: self.offers[_offer_id].lend_currency_value,
        borrow_currency_value: self.offers[_offer_id].borrow_currency_value,
        i_parent_address: self.offers[_offer_id].i_parent_address,
        i_token_id: self.offers[_offer_id].i_token_id,
        i_quantity: self.offers[_offer_id].i_quantity,
        s_quantity: self.offers[_offer_id].s_quantity,
        status: self.LOAN_STATUS_ACTIVE,
        expiry: self.offers[_offer_id].expiry,
        shield_market_hash: self.offers[_offer_id].shield_market_hash,
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
def _close_position(_position_id: uint256):
    self.positions[_position_id].status = self.LOAN_STATUS_CLOSED
    self._remove_position(_position_id)


@private
def _liquidate_position(_position_id: uint256):
    self.positions[_position_id].status = self.LOAN_STATUS_LIQUIDATED
    self._remove_position(_position_id)


@public
def create_offer(_currency_address: address, _expiry: timestamp, _underlying_address: address, _strike_price: uint256,
    _s_quantity: uint256, _i_quantity: uint256, _i_unit_price_in_wei: wei_value) -> bool:
    assert block.timestamp < _expiry
    self._create_offer(
        msg.sender,
        _currency_address, _expiry, _underlying_address, _strike_price,
        _s_quantity, _i_quantity, _i_unit_price_in_wei)

    return True


@public
def update_offer(_offer_id: uint256, _s_quantity: uint256, _i_quantity: uint256) -> bool:
    assert block.timestamp < self.offers[_offer_id].expiry
    assert self.offers[_offer_id].creator == msg.sender
    assert _offer_id <= self.last_offer_index
    self._lock_offer(_offer_id)
    self._update_offer(_offer_id, _s_quantity, _i_quantity)
    self._unlock_offer(_offer_id)

    return True


@public
def remove_offer(_offer_id: uint256) -> bool:
    assert self.offers[_offer_id].creator == msg.sender
    assert _offer_id <= self.last_offer_index
    self._lock_offer(_offer_id)
    self._remove_offer(_offer_id)
    self._unlock_offer(_offer_id)

    return True


@public
@payable
def avail_loan(_offer_id: uint256) -> bool:
    assert block.timestamp < self.offers[_offer_id].expiry
    assert msg.value == as_unitless_number(self.offers[_offer_id].i_unit_price_in_wei) * as_unitless_number(self.offers[_offer_id].i_quantity)
    self._lock_offer(_offer_id)
    # create position
    self._open_position(msg.sender, _offer_id)
    assert_modifiable(MarketDao(self.daos[self.DAO_TYPE_MARKET]).open_position(
        self.offers[_offer_id].shield_market_hash,
        self.offers[_offer_id].creator,
        self.offers[_offer_id].i_parent_address,
        self.offers[_offer_id].i_token_id,
        self.offers[_offer_id].i_quantity,
        self.offers[_offer_id].s_quantity,
        self.offers[_offer_id].lend_currency_value,
        self.offers[_offer_id].borrow_currency_value,
        msg.sender
    ))
    send(self.offers[_offer_id].creator, msg.value)
    self._remove_offer(_offer_id)
    self._unlock_offer(_offer_id)

    return True


@public
def repay_loan(_position_id: uint256) -> bool:
    assert block.timestamp < self.positions[_position_id].expiry
    # validate borrower
    assert self.positions[_position_id].borrower == msg.sender
    # validate position currencies
    assert_modifiable(MarketDao(self.daos[self.DAO_TYPE_MARKET]).close_position(
        self.positions[_position_id].shield_market_hash,
        self.positions[_position_id].i_parent_address,
        self.positions[_position_id].i_token_id,
        self.positions[_position_id].i_quantity,
        self.positions[_position_id].s_quantity,
        self.positions[_position_id].lend_currency_value,
        self.positions[_position_id].borrow_currency_value,
        self.positions[_position_id].borrower
    ))
    # close position
    self._close_position(_position_id)

    return True


@public
def close_liquidated_loan(_position_id: uint256) -> bool:
    assert block.timestamp > self.positions[_position_id].expiry
    # validate position currencies
    assert_modifiable(MarketDao(self.daos[self.DAO_TYPE_MARKET]).close_liquidated_position(
        self.positions[_position_id].shield_market_hash,
        self.positions[_position_id].s_quantity,
        self.positions[_position_id].lend_currency_value,
        self.positions[_position_id].borrow_currency_value,
        self.positions[_position_id].borrower
    ))
    # liquidate position
    self._liquidate_position(_position_id)

    return True
