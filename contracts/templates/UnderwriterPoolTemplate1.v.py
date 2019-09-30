# Vyper version of the Lendroid protocol v2
# THIS CONTRACT HAS NOT BEEN AUDITED!


from contracts.interfaces import ERC20
from contracts.interfaces import ERC1155
from contracts.interfaces import ERC1155TokenReceiver
from contracts.interfaces import Dao


implements: ERC1155TokenReceiver


struct SUFITokenOfferedExpiryStat:
    has_id: bool
    erc1155_id: uint256

owner: public(address)
operator: public(address)
name: public(string[64])
symbol: public(string[32])
initial_exchange_rate: public(uint256)
total_l_currency_balance: public(uint256)
lend_currency_address: public(address)
collateral_currency_address: public(address)
l_currency_address: public(address)
i_currency_address: public(address)
s_currency_address: public(address)
u_currency_address: public(address)
pool_currency_address: public(address)

expiries_offered: public(map(bytes32, bool))
sufi_currency_offered_expiries: public(map(address, map(string[3], SUFITokenOfferedExpiryStat)))

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
def initialize(_operator: address,
    _name: string[64], _symbol: string[32], _initial_exchange_rate: uint256,
    _lend_currency_address: address, _collateral_currency_address: address,
    _l_currency_address: address, _i_currency_address: address,
    _s_currency_address: address, _u_currency_address: address,
    _erc20_currency_template_address: address) -> bool:
    self.owner = msg.sender
    self.operator = _operator
    self.name = _name
    self.initial_exchange_rate = _initial_exchange_rate
    self.total_l_currency_balance = 0
    self.lend_currency_address = _lend_currency_address
    self.collateral_currency_address = _collateral_currency_address
    # erc20 token
    _pool_currency_address: address = create_forwarder_to(_erc20_currency_template_address)
    self.pool_currency_address = _pool_currency_address
    _external_call_successful: bool = ERC20(_pool_currency_address).initialize(_name, _symbol, 18, 0)
    assert _external_call_successful

    self.l_currency_address = _l_currency_address
    self.s_currency_address = _s_currency_address
    self.u_currency_address = _u_currency_address
    self.i_currency_address = _i_currency_address

    self.ERC1155_ACCEPTED = "0xf23a6e61"# bytes4(keccak256("onERC1155Received(address,address,uint256,uint256,bytes)"))
    self.ERC1155_BATCH_ACCEPTED = "0xbc197c81"# bytes4(keccak256("onERC1155BatchReceived(address,address,uint256[],uint256[],bytes)"))

    return True


@private
@constant
def _shield_hash(_expiry_label: string[3], _strike_price: uint256) -> bytes32:
    return Dao(self.owner).shield_hash(self.lend_currency_address, self.collateral_currency_address, _strike_price, _expiry_label)


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
def _u_currency_balance(_erc1155_id: uint256) -> uint256:
    return ERC1155(self.u_currency_address).balanceOf(self, _erc1155_id)


@private
@constant
def _s_currency_balance(_erc1155_id: uint256) -> uint256:
    return ERC1155(self.s_currency_address).balanceOf(self, _erc1155_id)


@private
@constant
def _exchange_rate() -> uint256:
    if (as_unitless_number(self.total_l_currency_balance) == 0) or (ERC20(self.pool_currency_address).totalSupply() == 0):
        return self.initial_exchange_rate
    return as_unitless_number(self.total_l_currency_balance) / as_unitless_number(ERC20(self.pool_currency_address).totalSupply())


@private
@constant
def _estimated_pool_tokens(_l_currency_value: uint256) -> uint256:
    return as_unitless_number(self._exchange_rate()) * as_unitless_number(_l_currency_value)


@private
def _set_expiry_status(_sender: address, _expiry_label: string[3], _strike_price: uint256, _status: bool):
    assert _sender == self.operator
    _shield_hash: bytes32 = self._shield_hash(_expiry_label, _strike_price)
    self.expiries_offered[_shield_hash] = _status


@public
@constant
def exchange_rate() -> uint256:
    return self._exchange_rate()


@public
@constant
def estimated_pool_tokens(_l_currency_value: uint256) -> uint256:
    return self._estimated_pool_tokens(_l_currency_value)


# START OF ERC1155TokenReceiver interface functions
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


# START OF ERC1155TokenReceiver interface functions


@public
def offer_new_expiry(_expiry_label: string[3], _strike_price: uint256) -> bool:
    self._set_expiry_status(msg.sender, _expiry_label, _strike_price, True)
    _external_call_successful: bool = False
    _s_currency_expiry_id: uint256 = 0
    _u_currency_expiry_id: uint256 = 0
    _i_currency_expiry_id: uint256 = 0
    _external_call_successful, _s_currency_expiry_id, _u_currency_expiry_id, _i_currency_expiry_id = Dao(self.owner).register_expiry_offer_from_underwriter_pool(self.lend_currency_address, self.collateral_currency_address, _expiry_label, _strike_price)
    assert _external_call_successful
    self.sufi_currency_offered_expiries[self.s_currency_address][_expiry_label] = SUFITokenOfferedExpiryStat({
        has_id: True,
        erc1155_id: _s_currency_expiry_id
    })
    self.sufi_currency_offered_expiries[self.u_currency_address][_expiry_label] = SUFITokenOfferedExpiryStat({
        has_id: True,
        erc1155_id: _u_currency_expiry_id
    })
    self.sufi_currency_offered_expiries[self.i_currency_address][_expiry_label] = SUFITokenOfferedExpiryStat({
        has_id: True,
        erc1155_id: _i_currency_expiry_id
    })

    return True


@public
def remove_expiry(_expiry_label: string[3], _strike_price: uint256) -> bool:
    self._set_expiry_status(msg.sender, _expiry_label, _strike_price, False)
    _external_call_successful: bool = Dao(self.owner).remove_expiry_offer_from_underwriter_pool(self.lend_currency_address, self.collateral_currency_address, _expiry_label, _strike_price)
    assert _external_call_successful

    return True


@public
def purchase_pool_tokens(_l_currency_value: uint256) -> bool:
    # increment self.total_l_currency_balance
    self.total_l_currency_balance += _l_currency_value
    # ask Dao to deposit l_tokens to self
    _external_call_successful: bool = Dao(self.owner).deposit_l_tokens_to_underwriter_pool(self.lend_currency_address, msg.sender, _l_currency_value)
    assert _external_call_successful
    # mint pool tokens to msg.sender
    _external_call_successful = ERC20(self.pool_currency_address).mintAndAuthorizeMinter(
        msg.sender, self._estimated_pool_tokens(_l_currency_value))
    assert _external_call_successful

    return True


@public
def increment_i_tokens_offered(_expiry_label: string[3], _strike_price: uint256, _l_currency_value: uint256) -> bool:
    # decrement self.total_l_currency_balance
    assert self.total_l_currency_balance >= _l_currency_value
    self.total_l_currency_balance -= _l_currency_value
    # validate sender
    assert msg.sender == self.operator
    # validate expiry
    _shield_hash: bytes32 = self._shield_hash(_expiry_label, _strike_price)
    assert self.expiries_offered[_shield_hash] == True, "expiry is not offered"
    _external_call_successful: bool = Dao(self.owner).l_currency_to_i_and_s_and_u_currency(self.lend_currency_address, self.collateral_currency_address, _expiry_label, _strike_price, _l_currency_value)
    assert _external_call_successful

    return True
