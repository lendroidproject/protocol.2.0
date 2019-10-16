# Vyper version of the Lendroid protocol v2
# THIS CONTRACT HAS NOT BEEN AUDITED!


from contracts.interfaces import ERC20
from contracts.interfaces import CurrencyDao
from contracts.interfaces import UnderwriterPoolDao


# Structs
struct Position:
    borrower: address
    multi_fungible_currency_hash: bytes32
    status: uint256
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

DAO_TYPE_CURRENCY: public(uint256)
DAO_TYPE_UNDERWRITER_POOL: public(uint256)

LOAN_STATUS_ACTIVE: public(uint256)
LOAN_STATUS_LIQUIDATED: public(uint256)
LOAN_STATUS_CLOSED: public(uint256)


@public
def initialize(
        _owner: address,
        _protocol_currency_address: address,
        _dao_address_currency: address,
        _dao_address_underwriter_pool: address) -> bool:
    # self.owner = _owner
    # self.protocol_dao_address = msg.sender
    # self.protocol_currency_address = _protocol_currency_address
    #
    # self.DAO_TYPE_CURRENCY = 1
    # self.daos[self.DAO_TYPE_CURRENCY] = _dao_address_currency
    # self.DAO_TYPE_UNDERWRITER_POOL = 2
    # self.daos[self.DAO_TYPE_UNDERWRITER_POOL] = _dao_address_underwriter_pool
    #
    # self.LOAN_STATUS_ACTIVE = 1
    # self.LOAN_STATUS_LIQUIDATED = 2
    # self.LOAN_STATUS_CLOSED = 3

    return True


@private
@constant
def _is_currency_valid(_currency_address: address) -> bool:
    return CurrencyDao(self.daos[self.DAO_TYPE_CURRENCY]).is_currency_valid(_currency_address)


@private
def _deposit_multi_fungible_l_currency(_currency_address: address, _from: address, _to: address, _value: uint256):
    _external_call_successful: bool = CurrencyDao(self.daos[self.DAO_TYPE_CURRENCY]).deposit_multi_fungible_l_currency(
        _currency_address, _from, _to, _value)
    assert _external_call_successful


@private
def _release_currency_from_pool(_currency_address: address, _to: address, _value: uint256):
    _external_call_successful: bool = CurrencyDao(self.daos[self.DAO_TYPE_CURRENCY]).release_currency_from_pool(_currency_address, _to, _value)
    assert _external_call_successful


@private
def _deposit_currency_to_pool(_currency_address: address, _from: address, _value: uint256):
    _external_call_successful: bool = CurrencyDao(self.daos[self.DAO_TYPE_CURRENCY]).deposit_currency_to_pool(_currency_address, _from, _value)
    assert _external_call_successful


@private
def _transfer_erc20(_currency_address: address, _to: address, _value: uint256):
    _external_call_successful: bool = ERC20(_currency_address).transfer(_to, _value)
    assert _external_call_successful


@private
def _create_position(_borrower: address, _s_hash: bytes32):
    self.last_position_id += 1
    _position_id: uint256 = self.last_position_id

    self.positions[_position_id] = Position({
        borrower: _borrower,
        multi_fungible_currency_hash: _s_hash,
        status: self.LOAN_STATUS_ACTIVE,
        id: _position_id
    })
    self.borrow_position_count[_borrower] += 1
    self.borrow_position_index[_borrower][_position_id] = self.borrow_position_count[_borrower]
    self.borrow_position[_borrower][self.borrow_position_count[_borrower]] = _position_id


@private
def _close_position(_position_id: uint256):
    self.positions[_position_id].status = self.LOAN_STATUS_CLOSED
    _borrower: address = self.positions[_position_id].borrower
    _current_position_index: uint256 = self.borrow_position_index[_borrower][_position_id]
    _last_position_index: uint256 = self.borrow_position_count[_borrower]
    _last_position_id: uint256 = self.borrow_position[_borrower][_last_position_index]
    self.borrow_position[_borrower][_current_position_index] = self.borrow_position[_borrower][_last_position_index]
    clear(self.borrow_position[_borrower][_last_position_index])
    clear(self.borrow_position_index[_borrower][_position_id])
    self.borrow_position_index[_borrower][_last_position_id] = _current_position_index
    self.borrow_position_count[_borrower] -= 1


@public
def avail_loan(_s_hash: bytes32) -> bool:
    assert UnderwriterPoolDao(self.daos[self.DAO_TYPE_UNDERWRITER_POOL]).multi_fungible_currencies__has_id(_s_hash)
    _lend_currency_address: address = UnderwriterPoolDao(self.daos[self.DAO_TYPE_UNDERWRITER_POOL]).multi_fungible_currencies__currency_address(_s_hash)
    _borrow_currency_address: address = UnderwriterPoolDao(self.daos[self.DAO_TYPE_UNDERWRITER_POOL]).multi_fungible_currencies__underlying_address(_s_hash)
    assert self._is_currency_valid(_lend_currency_address)
    assert self._is_currency_valid(_borrow_currency_address)
    # create position
    self._create_position(msg.sender, _s_hash)
    # calculate _collateral_amount
    _shield_price: uint256 = UnderwriterPoolDao(self.daos[self.DAO_TYPE_UNDERWRITER_POOL]).shield_currency_prices(_s_hash)
    _strike_price: uint256 = UnderwriterPoolDao(self.daos[self.DAO_TYPE_UNDERWRITER_POOL]).multi_fungible_currencies__strike_price(_s_hash)
    _collateral_amount: uint256 = as_unitless_number(_shield_price) / as_unitless_number(_strike_price)
    # transfer l_borrow_currency from borrower to self
    self._deposit_multi_fungible_l_currency(_borrow_currency_address, msg.sender, self, _collateral_amount)
    # transfer lend_currency to msg.sender
    self._release_currency_from_pool(_lend_currency_address, msg.sender, as_unitless_number(_strike_price))

    return True


@public
def repay_loan(_position_id: uint256) -> bool:
    # validate borrower
    assert self.positions[_position_id].borrower == msg.sender
    # validate position currencies
    _s_hash: bytes32 = self.positions[_position_id].multi_fungible_currency_hash
    assert UnderwriterPoolDao(self.daos[self.DAO_TYPE_UNDERWRITER_POOL]).multi_fungible_currencies__has_id(_s_hash)
    _lend_currency_address: address = UnderwriterPoolDao(self.daos[self.DAO_TYPE_UNDERWRITER_POOL]).multi_fungible_currencies__currency_address(_s_hash)
    _borrow_currency_address: address = UnderwriterPoolDao(self.daos[self.DAO_TYPE_UNDERWRITER_POOL]).multi_fungible_currencies__underlying_address(_s_hash)
    assert self._is_currency_valid(_lend_currency_address)
    assert self._is_currency_valid(_borrow_currency_address)
    # close position
    self._close_position(_position_id)
    # calculate _collateral_amount
    _shield_price: uint256 = UnderwriterPoolDao(self.daos[self.DAO_TYPE_UNDERWRITER_POOL]).shield_currency_prices(_s_hash)
    _strike_price: uint256 = UnderwriterPoolDao(self.daos[self.DAO_TYPE_UNDERWRITER_POOL]).multi_fungible_currencies__strike_price(_s_hash)
    _collateral_amount: uint256 = as_unitless_number(_shield_price) / as_unitless_number(_strike_price)
    # transfer l_borrow_currency to msg.sender
    self._transfer_erc20(
        CurrencyDao(self.daos[self.DAO_TYPE_CURRENCY]).currencies__l_currency_address(_borrow_currency_address),
        msg.sender, _collateral_amount)
    # transfer lend_currency from msg.sender to currency_pool
    self._deposit_currency_to_pool(_lend_currency_address, msg.sender, as_unitless_number(_strike_price))

    return True
