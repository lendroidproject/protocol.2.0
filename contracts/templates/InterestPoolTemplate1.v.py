# Vyper version of the Lendroid protocol v2
# THIS CONTRACT HAS NOT BEEN AUDITED!


from contracts.interfaces import ERC20
from contracts.interfaces import ERC1155
from contracts.interfaces import ERC1155TokenReceiver
from contracts.interfaces import Dao


implements: ERC1155TokenReceiver


struct Expiry:
    expiry_timestamp: timestamp
    i_currency_hash: bytes32
    i_currency_id: uint256
    f_currency_hash: bytes32
    f_currency_id: uint256
    is_active: bool


pool_type: public(uint256)
pool_hash: public(bytes32)
owner: public(address)
operator: public(address)
name: public(string[64])
symbol: public(string[32])
initial_exchange_rate: public(uint256)
currency_address: public(address)
l_currency_address: public(address)
i_currency_address: public(address)
f_currency_address: public(address)
pool_currency_address: public(address)

expiries: public(map(timestamp, Expiry))

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
def initialize(_pool_type: uint256, _pool_hash: bytes32, _operator: address,
    _name: string[64], _symbol: string[32], _initial_exchange_rate: uint256,
    _currency_address: address,
    _l_currency_address: address, _i_currency_address: address, _f_currency_address: address,
    _erc20_currency_template_address: address) -> bool:
    self.owner = msg.sender
    self.pool_type = _pool_type
    self.pool_hash = _pool_hash
    self.operator = _operator
    self.name = _name
    self.initial_exchange_rate = _initial_exchange_rate
    self.currency_address = _currency_address
    # erc20 token
    _pool_currency_address: address = create_forwarder_to(_erc20_currency_template_address)
    self.pool_currency_address = _pool_currency_address
    _external_call_successful: bool = ERC20(_pool_currency_address).initialize(_name, _symbol, 18, 0)
    assert _external_call_successful

    self.l_currency_address = _l_currency_address
    self.f_currency_address = _f_currency_address
    self.i_currency_address = _i_currency_address

    self.ERC1155_ACCEPTED = "0xf23a6e61"# bytes4(keccak256("onERC1155Received(address,address,uint256,uint256,bytes)"))
    self.ERC1155_BATCH_ACCEPTED = "0xbc197c81"# bytes4(keccak256("onERC1155BatchReceived(address,address,uint256[],uint256[],bytes)"))

    return True


@private
@constant
def _l_currency_balance() -> uint256:
    return ERC20(self.l_currency_address).balanceOf(self)


@private
@constant
def _i_currency_balance(_erc1155_id: uint256) -> uint256:
    return ERC1155(self.i_currency_address).balanceOf(self, _erc1155_id)


@private
@constant
def _f_currency_balance(_erc1155_id: uint256) -> uint256:
    return ERC1155(self.f_currency_address).balanceOf(self, _erc1155_id)


@private
@constant
def _total_f_currency_balance() -> uint256:
    return ERC1155(self.f_currency_address).totalBalanceOf(self)


@private
@constant
def _total_l_currency_balance() -> uint256:
    return as_unitless_number(self._l_currency_balance()) + as_unitless_number(self._total_f_currency_balance())


@private
@constant
def _exchange_rate() -> uint256:
    if (as_unitless_number(self._total_l_currency_balance()) == 0) or (ERC20(self.pool_currency_address).totalSupply() == 0):
        return self.initial_exchange_rate
    return as_unitless_number(self._total_l_currency_balance()) / as_unitless_number(ERC20(self.pool_currency_address).totalSupply())


@private
@constant
def _estimated_pool_tokens(_l_currency_value: uint256) -> uint256:
    return as_unitless_number(self._exchange_rate()) * as_unitless_number(_l_currency_value)


@public
@constant
def total_l_currency_balance() -> uint256:
    return self._total_l_currency_balance()


@public
@constant
def exchange_rate() -> uint256:
    return self._exchange_rate()


@public
@constant
def estimated_pool_tokens(_l_currency_value: uint256) -> uint256:
    return self._estimated_pool_tokens(_l_currency_value)
#
#
# START of ERC1155TokenReceiver interface functions
@public
def setShouldReject(_value: bool):
    assert msg.sender == self.owner or msg.sender == self.operator
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
def register_expiry(_expiry: timestamp) -> bool:
    assert msg.sender == self.operator
    _external_call_successful: bool = False
    _f_hash: bytes32 = EMPTY_BYTES32
    _i_hash: bytes32 = EMPTY_BYTES32
    _f_id: uint256 = 0
    _i_id: uint256 = 0
    _external_call_successful, _f_hash, _i_hash, _f_id, _i_id = Dao(self.owner).register_expiry_from_interest_pool(self.pool_hash, _expiry)
    assert _external_call_successful
    self.expiries[_expiry] = Expiry({
        expiry_timestamp: _expiry,
        i_currency_hash: _i_hash,
        i_currency_id: _i_id,
        f_currency_hash: _f_hash,
        f_currency_id: _f_id,
        is_active: True
    })

    return True


@public
def remove_expiry(_expiry: timestamp) -> bool:
    assert msg.sender == self.operator
    self.expiries[_expiry].is_active = False

    return True


@public
def purchase_pool_currency(_l_currency_value: uint256) -> bool:
    # ask Dao to deposit l_tokens to self
    _external_call_successful: bool = Dao(self.owner).deposit_l_currency(self.pool_hash, msg.sender, _l_currency_value)
    assert _external_call_successful
    # mint pool tokens to msg.sender
    _external_call_successful = ERC20(self.pool_currency_address).mintAndAuthorizeMinter(
        msg.sender, self._estimated_pool_tokens(_l_currency_value))
    assert _external_call_successful

    return True


@public
def increment_i_currency_supply(_expiry: timestamp, _l_currency_value: uint256) -> bool:
    # validate _l_currency_value
    assert self._l_currency_balance() >= _l_currency_value
    # validate sender
    assert msg.sender == self.operator
    # validate expiry
    assert self.expiries[_expiry].is_active == True, "expiry is not offered"
    _external_call_successful: bool = Dao(self.owner).l_currency_to_i_and_f_currency(
        self.pool_hash, self.expiries[_expiry].i_currency_hash,
        self.expiries[_expiry].f_currency_hash, _l_currency_value)
    assert _external_call_successful

    return True


@public
def decrement_i_currency_supply(_expiry: timestamp, _l_currency_value: uint256) -> bool:
    # validate sender
    assert msg.sender == self.operator
    # validate expiry
    assert self.expiries[_expiry].is_active == True, "expiry is not offered"
    _external_call_successful: bool = Dao(self.owner).l_currency_from_i_and_f_currency(
        self.pool_hash, self.expiries[_expiry].i_currency_hash,
        self.expiries[_expiry].f_currency_hash, _l_currency_value)
    assert _external_call_successful

    return True


@public
def purchase_i_currency(_expiry: timestamp, _i_currency_value: uint256, _l_currency_fee: uint256) -> bool:
    # validate expiry
    assert self.expiries[_expiry].is_active == True, "expiry is not offered"
    assert not self.expiries[_expiry].i_currency_id == 0, "expiry does not have a valid i_currency id"
    _external_call_successful: bool = False
    # transfer l_tokens as fee from msg.sender to self
    if as_unitless_number(_l_currency_fee) > 0:
        _external_call_successful = ERC20(self.l_currency_address).transferFrom(
            msg.sender, self, _l_currency_fee)
        assert _external_call_successful
    # transfer i_tokens from self to msg.sender
    _external_call_successful = ERC1155(self.i_currency_address).safeTransferFrom(
        self, msg.sender,
        self.expiries[_expiry].i_currency_id,
        _i_currency_value, EMPTY_BYTES32)
    assert _external_call_successful

    return True


@public
def redeem_f_currency(_expiry: timestamp, _pool_currency_value: uint256) -> bool:
    # validate expiry
    assert self.expiries[_expiry].is_active == True, "expiry is not offered"
    assert not self.expiries[_expiry].f_currency_id == 0, "expiry does not have a valid f_currency id"
    # calculate f_tokens + l_tokens (if any) to be transferred
    _f_currency_transfer_value: uint256 = as_unitless_number(_pool_currency_value) / as_unitless_number(self._exchange_rate())
    _l_currency_transfer_value: uint256 = 0
    _current_f_currency_balance: uint256 = self._f_currency_balance(self.expiries[_expiry].f_currency_id)
    # THIS IS AN IMPORANT ASSUMPTION FOR THIS VERSION!
    assert as_unitless_number(self._l_currency_balance()) >= as_unitless_number(_current_f_currency_balance), "l_token balance cannot be less than f_token balance"
    if as_unitless_number(_current_f_currency_balance) < _f_currency_transfer_value:
        _f_currency_transfer_value = as_unitless_number(_current_f_currency_balance)
        _l_currency_transfer_value = as_unitless_number(self._l_currency_balance()) - as_unitless_number(_current_f_currency_balance)
    # burn pool_tokens from msg.sender by self
    _external_call_successful: bool = ERC20(self.pool_currency_address).burnFrom(
        msg.sender, _pool_currency_value)
    assert _external_call_successful
    # transfer f_tokens + l_tokens (if any) from self to msg.sender
    _external_call_successful = ERC1155(self.f_currency_address).safeTransferFrom(
        self, msg.sender,
        self.expiries[_expiry].f_currency_id,
        _f_currency_transfer_value, EMPTY_BYTES32)
    assert _external_call_successful
    if as_unitless_number(_l_currency_transfer_value) > 0:
        _external_call_successful = ERC20(self.l_currency_address).transferFrom(
            self, msg.sender, _l_currency_transfer_value)
        assert _external_call_successful

    return True
