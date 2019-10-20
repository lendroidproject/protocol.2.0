# Vyper version of the Lendroid protocol v2
# THIS CONTRACT HAS NOT BEEN AUDITED!


from contracts.interfaces import ERC20
from contracts.interfaces import ERC1155TokenReceiver
from contracts.interfaces import CurrencyDao
from contracts.interfaces import InterestPoolDao
from contracts.interfaces import UnderwriterPoolDao


implements: ERC1155TokenReceiver


# Structs
struct Offer:
    creator: address
    multi_fungible_currency_s_hash: bytes32
    multi_fungible_currency_i_hash: bytes32
    multi_fungible_currency_s_quantity: uint256
    multi_fungible_currency_i_quantity: uint256
    multi_fungible_currency_i_unit_price_in_wei: wei_value
    id: uint256


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
# nonce per offer
last_offer_index: public(uint256)
# offer_hash => Offer
offers: public(map(uint256, Offer))
# nonreentrant locks for positions, inspired from https://github.com/ethereum/vyper/issues/1204
nonreentrant_offer_locks: map(uint256, bool)

DAO_TYPE_CURRENCY: public(uint256)
DAO_TYPE_INTEREST_POOL: public(uint256)
DAO_TYPE_UNDERWRITER_POOL: public(uint256)

LOAN_STATUS_ACTIVE: public(uint256)
LOAN_STATUS_LIQUIDATED: public(uint256)
LOAN_STATUS_CLOSED: public(uint256)

# ERC1155TokenReceiver interface variables
shouldReject: public(bool)
lastData: public(bytes32)
lastOperator: public(address)
lastFrom: public(address)
lastId: public(uint256)
lastValue: public(uint256)
ERC1155_ACCEPTED: bytes[10]
ERC1155_BATCH_ACCEPTED: bytes[10]


@public
def initialize(
        _owner: address,
        _protocol_currency_address: address,
        _dao_address_currency: address,
        _dao_address_interest_pool: address,
        _dao_address_underwriter_pool: address) -> bool:
    self.owner = _owner
    self.protocol_dao_address = msg.sender
    self.protocol_currency_address = _protocol_currency_address

    self.DAO_TYPE_CURRENCY = 1
    self.daos[self.DAO_TYPE_CURRENCY] = _dao_address_currency
    self.DAO_TYPE_INTEREST_POOL = 2
    self.daos[self.DAO_TYPE_INTEREST_POOL] = _dao_address_interest_pool
    self.DAO_TYPE_UNDERWRITER_POOL = 3
    self.daos[self.DAO_TYPE_UNDERWRITER_POOL] = _dao_address_underwriter_pool

    self.LOAN_STATUS_ACTIVE = 1
    self.LOAN_STATUS_LIQUIDATED = 2
    self.LOAN_STATUS_CLOSED = 3

    # bytes4(keccak256("onERC1155Received(address,address,uint256,uint256,bytes)"))
    self.ERC1155_ACCEPTED = "0xf23a6e61"
    # bytes4(keccak256("onERC1155BatchReceived(address,address,uint256[],uint256[],bytes)"))
    self.ERC1155_BATCH_ACCEPTED = "0xbc197c81"
    self.shouldReject = False

    return True


@private
@constant
def _is_currency_valid(_currency_address: address) -> bool:
    return CurrencyDao(self.daos[self.DAO_TYPE_CURRENCY]).is_currency_valid(_currency_address)


@private
def _deposit_multi_fungible_l_currency(_currency_address: address, _from: address, _to: address, _value: uint256):
    assert_modifiable(CurrencyDao(self.daos[self.DAO_TYPE_CURRENCY]).deposit_multi_fungible_l_currency(
        _currency_address, _from, _to, _value))


@private
def _release_currency_from_pool(_currency_address: address, _to: address, _value: uint256):
    assert_modifiable(CurrencyDao(self.daos[self.DAO_TYPE_CURRENCY]).release_currency_from_pool(
        _currency_address, _to, _value))


@private
def _deposit_currency_to_pool(_currency_address: address, _from: address, _value: uint256):
    assert_modifiable(CurrencyDao(self.daos[self.DAO_TYPE_CURRENCY]).deposit_currency_to_pool(
        _currency_address, _from, _value))


@private
def _transfer_erc20(_currency_address: address, _to: address, _value: uint256):
    assert_modifiable(ERC20(_currency_address).transfer(_to, _value))


@private
def _burn_erc1155(_currency_address: address, _id: uint256, _from: address, _value: uint256):
    assert_modifiable(CurrencyDao(self.daos[self.DAO_TYPE_CURRENCY]).burn_erc1155(_currency_address, _id, _from, _value))


@private
def _transfer_as_self_authorized_erc1155_and_authorize(_from: address, _to: address, _currency_address: address, _id: uint256, _value: uint256):
    assert_modifiable(CurrencyDao(self.daos[self.DAO_TYPE_CURRENCY]).transfer_as_self_authorized_erc1155_and_authorize(_from, _to, _currency_address, _id, _value))


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


@private
def _lock_offer(_id: uint256):
    assert self.nonreentrant_offer_locks[_id] == False
    self.nonreentrant_offer_locks[_id] = True


@private
def _unlock_offer(_id: uint256):
    assert self.nonreentrant_offer_locks[_id] == True
    self.nonreentrant_offer_locks[_id] = False


@private
def _remove_offer(_id: uint256):
    if _id < self.last_offer_index:
        self.offers[_id] = Offer({
            creator: self.offers[self.last_offer_index].creator,
            multi_fungible_currency_s_hash: self.offers[self.last_offer_index].multi_fungible_currency_s_hash,
            multi_fungible_currency_i_hash: self.offers[self.last_offer_index].multi_fungible_currency_i_hash,
            multi_fungible_currency_s_quantity: self.offers[self.last_offer_index].multi_fungible_currency_s_quantity,
            multi_fungible_currency_i_quantity: self.offers[self.last_offer_index].multi_fungible_currency_i_quantity,
            multi_fungible_currency_i_unit_price_in_wei: self.offers[self.last_offer_index].multi_fungible_currency_i_unit_price_in_wei,
            id: _id
        })
    clear(self.offers[self.last_offer_index])
    self.last_offer_index -= 1


@private
def _loan_and_collateral_amount(_offer_id: uint256) -> (uint256, uint256):
    _s_hash: bytes32 = self.offers[_offer_id].multi_fungible_currency_s_hash
    _s_quantity: uint256 = self.offers[_offer_id].multi_fungible_currency_s_quantity
    _minimum_collateral_value: uint256 = UnderwriterPoolDao(self.daos[self.DAO_TYPE_UNDERWRITER_POOL]).shield_currency_minimum_collateral_values(_s_hash)
    _total_minimum_collateral_value: uint256 = as_unitless_number(_minimum_collateral_value) * as_unitless_number(_s_quantity)
    _strike_price: uint256 = UnderwriterPoolDao(self.daos[self.DAO_TYPE_UNDERWRITER_POOL]).multi_fungible_currencies__strike_price(_s_hash)
    _loan_amount: uint256 = as_unitless_number(_strike_price) * as_unitless_number(_s_quantity)
    _collateral_amount: uint256 = as_unitless_number(_total_minimum_collateral_value) / as_unitless_number(_loan_amount)
    return _loan_amount, _collateral_amount


# START of ERC1155TokenReceiver interface functions
@public
def setShouldReject(_value: bool):
    assert msg.sender == self.owner
    self.shouldReject = _value


@public
@constant
def supportsInterface(interfaceID: bytes[10]) -> bool:
    # ERC165 or ERC1155_ACCEPTED ^ ERC1155_BATCH_ACCEPTED
    return interfaceID == "0x01ffc9a7" or interfaceID == "0x4e2312e0"


@public
def onERC1155Received(_operator: address, _from: address, _id: uint256, _value: uint256, _data: bytes32) -> bytes[10]:
    self.lastOperator = _operator
    self.lastFrom = _from
    self.lastId = _id
    self.lastValue = _value
    self.lastData = _data
    if self.shouldReject:
        raise("onERC1155Received: transfer not accepted")
    else:
        return self.ERC1155_ACCEPTED


@public
def onERC1155BatchReceived(_operator: address, _from: address, _ids: uint256[5], _values: uint256[5], _data: bytes32) -> bytes[10]:
    self.lastOperator = _operator
    self.lastFrom = _from
    self.lastId = _ids[0]
    self.lastValue = _values[0]
    self.lastData = _data
    if self.shouldReject:
        raise("onERC1155BatchReceived: transfer not accepted")
    else:
        return self.ERC1155_BATCH_ACCEPTED


# END of ERC1155TokenReceiver interface functions


@public
def create_offer(_multi_fungible_currency_s_hash: bytes32, _multi_fungible_currency_i_hash: bytes32,
    _multi_fungible_currency_s_quantity: uint256, _multi_fungible_currency_i_quantity: uint256,
    _multi_fungible_currency_i_unit_price_in_wei: wei_value) -> bool:
    assert UnderwriterPoolDao(self.daos[self.DAO_TYPE_UNDERWRITER_POOL]).multi_fungible_currencies__has_id(_multi_fungible_currency_s_hash)
    assert UnderwriterPoolDao(self.daos[self.DAO_TYPE_UNDERWRITER_POOL]).multi_fungible_currencies__has_id(_multi_fungible_currency_i_hash) or \
           InterestPoolDao(self.daos[self.DAO_TYPE_INTEREST_POOL]).multi_fungible_currencies__has_id(_multi_fungible_currency_i_hash)
    self.last_offer_index += 1
    self.offers[self.last_offer_index] = Offer({
        creator: msg.sender,
        multi_fungible_currency_s_hash: _multi_fungible_currency_s_hash,
        multi_fungible_currency_i_hash: _multi_fungible_currency_i_hash,
        multi_fungible_currency_s_quantity: _multi_fungible_currency_s_quantity,
        multi_fungible_currency_i_quantity: _multi_fungible_currency_i_quantity,
        multi_fungible_currency_i_unit_price_in_wei: _multi_fungible_currency_i_unit_price_in_wei,
        id: self.last_offer_index
    })

    return True


@public
def update_offer(_id: uint256, _multi_fungible_currency_s_quantity: uint256,
    _multi_fungible_currency_i_quantity: uint256) -> bool:
    assert _id <= self.last_offer_index
    self.offers[_id].multi_fungible_currency_s_quantity = _multi_fungible_currency_s_quantity
    self.offers[_id].multi_fungible_currency_i_quantity = _multi_fungible_currency_i_quantity

    return True


@public
def remove_offer(_id: uint256) -> bool:
    self._lock_offer(_id)
    self._remove_offer(_id)
    self._unlock_offer(_id)

    return True


@public
def loan_and_collateral_amount(_offer_id: uint256) -> (uint256, uint256):
    return self._loan_and_collateral_amount(_offer_id)


@public
@payable
def avail_loan(_offer_id: uint256) -> bool:
    self._lock_offer(_offer_id)
    assert msg.value == as_unitless_number(self.offers[_offer_id].multi_fungible_currency_i_unit_price_in_wei) * as_unitless_number(self.offers[_offer_id].multi_fungible_currency_i_quantity)
    _s_hash: bytes32 = self.offers[_offer_id].multi_fungible_currency_s_hash
    _i_hash: bytes32 = self.offers[_offer_id].multi_fungible_currency_i_hash
    assert UnderwriterPoolDao(self.daos[self.DAO_TYPE_UNDERWRITER_POOL]).multi_fungible_currencies__has_id(_s_hash)
    _lend_currency_address: address = UnderwriterPoolDao(self.daos[self.DAO_TYPE_UNDERWRITER_POOL]).multi_fungible_currencies__currency_address(_s_hash)
    _borrow_currency_address: address = UnderwriterPoolDao(self.daos[self.DAO_TYPE_UNDERWRITER_POOL]).multi_fungible_currencies__underlying_address(_s_hash)
    _multi_fungible_currency_s_parent_address: address = UnderwriterPoolDao(self.daos[self.DAO_TYPE_UNDERWRITER_POOL]).multi_fungible_currencies__parent_currency_address(_s_hash)
    _multi_fungible_currency_s_token_id: uint256 = UnderwriterPoolDao(self.daos[self.DAO_TYPE_UNDERWRITER_POOL]).multi_fungible_currencies__token_id(_s_hash)
    _multi_fungible_currency_i_parent_address: address = ZERO_ADDRESS
    _multi_fungible_currency_i_token_id: uint256 = 0
    if UnderwriterPoolDao(self.daos[self.DAO_TYPE_UNDERWRITER_POOL]).multi_fungible_currencies__has_id(_i_hash):
        _multi_fungible_currency_i_parent_address = UnderwriterPoolDao(self.daos[self.DAO_TYPE_UNDERWRITER_POOL]).multi_fungible_currencies__parent_currency_address(_i_hash)
        _multi_fungible_currency_i_token_id = UnderwriterPoolDao(self.daos[self.DAO_TYPE_UNDERWRITER_POOL]).multi_fungible_currencies__token_id(_i_hash)
    else:
        _multi_fungible_currency_i_parent_address = InterestPoolDao(self.daos[self.DAO_TYPE_INTEREST_POOL]).multi_fungible_currencies__parent_currency_address(_i_hash)
        _multi_fungible_currency_i_token_id = InterestPoolDao(self.daos[self.DAO_TYPE_INTEREST_POOL]).multi_fungible_currencies__token_id(_i_hash)
    assert not _multi_fungible_currency_i_parent_address == ZERO_ADDRESS
    assert as_unitless_number(_multi_fungible_currency_i_token_id) > 0
    assert self._is_currency_valid(_lend_currency_address)
    assert self._is_currency_valid(_borrow_currency_address)
    # create position
    self._create_position(msg.sender, _s_hash)
    # get _loan_amount and _collateral_amount
    _loan_amount: uint256 = 0
    _collateral_amount: uint256 = 0
    _loan_amount, _collateral_amount = self._loan_and_collateral_amount(_offer_id)
    # self._burn_erc1155(_multi_fungible_currency_i_parent_address,
    #     _multi_fungible_currency_i_token_id,
    #     self.offers[_offer_id].creator,
    #     self.offers[_offer_id].multi_fungible_currency_i_quantity
    # )
    # transfer i_lend_currency from offer_creator to self
    self._transfer_as_self_authorized_erc1155_and_authorize(
        self.offers[_offer_id].creator,
        self,
        _multi_fungible_currency_i_parent_address,
        _multi_fungible_currency_i_token_id,
        self.offers[_offer_id].multi_fungible_currency_i_quantity
    )
    # transfer s_lend_currency from offer_creator to self
    self._transfer_as_self_authorized_erc1155_and_authorize(
        self.offers[_offer_id].creator,
        self,
        _multi_fungible_currency_s_parent_address,
        _multi_fungible_currency_s_token_id,
        self.offers[_offer_id].multi_fungible_currency_s_quantity
    )
    # transfer l_borrow_currency from borrower to self
    self._deposit_multi_fungible_l_currency(_borrow_currency_address, msg.sender, self, _collateral_amount)
    # transfer lend_currency to msg.sender
    self._release_currency_from_pool(_lend_currency_address, msg.sender, as_unitless_number(_loan_amount))
    send(self.offers[_offer_id].creator, msg.value)
    self._remove_offer(_offer_id)
    self._unlock_offer(_offer_id)

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
    _shield_price: uint256 = UnderwriterPoolDao(self.daos[self.DAO_TYPE_UNDERWRITER_POOL]).shield_currency_minimum_collateral_values(_s_hash)
    _strike_price: uint256 = UnderwriterPoolDao(self.daos[self.DAO_TYPE_UNDERWRITER_POOL]).multi_fungible_currencies__strike_price(_s_hash)
    _collateral_amount: uint256 = as_unitless_number(_shield_price) / as_unitless_number(_strike_price)
    # transfer l_borrow_currency to msg.sender
    self._transfer_erc20(
        CurrencyDao(self.daos[self.DAO_TYPE_CURRENCY]).currencies__l_currency_address(_borrow_currency_address),
        msg.sender, _collateral_amount)
    # transfer lend_currency from msg.sender to currency_pool
    self._deposit_currency_to_pool(_lend_currency_address, msg.sender, as_unitless_number(_strike_price))

    return True
