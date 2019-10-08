# Vyper version of the Lendroid protocol v2
# THIS CONTRACT HAS NOT BEEN AUDITED!


from contracts.interfaces import ERC20
from contracts.interfaces import ERC1155
from contracts.interfaces import ERC1155TokenReceiver
from contracts.interfaces import UnderwriterPoolDao


implements: ERC1155TokenReceiver


struct Expiry:
    expiry_timestamp: timestamp
    i_currency_hash: bytes32
    i_currency_id: uint256
    s_currency_hash: bytes32
    s_currency_id: uint256
    u_currency_hash: bytes32
    u_currency_id: uint256
    is_active: bool
    hash: bytes32


pool_hash: public(bytes32)
owner: public(address)
operator: public(address)
name: public(string[64])
symbol: public(string[32])
initial_exchange_rate: public(uint256)
currency_address: public(address)
l_currency_address: public(address)
i_currency_address: public(address)
s_currency_address: public(address)
u_currency_address: public(address)
pool_currency_address: public(address)

expiries: public(map(bytes32, Expiry))

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
def initialize(_pool_hash: bytes32, _operator: address,
    _name: string[64], _symbol: string[32], _initial_exchange_rate: uint256,
    _currency_address: address,
    _l_currency_address: address, _i_currency_address: address,
    _s_currency_address: address, _u_currency_address: address,
    _erc20_currency_template_address: address) -> bool:
    self.owner = msg.sender
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
    self.i_currency_address = _i_currency_address
    self.s_currency_address = _s_currency_address
    self.u_currency_address = _u_currency_address

    self.ERC1155_ACCEPTED = "0xf23a6e61"# bytes4(keccak256("onERC1155Received(address,address,uint256,uint256,bytes)"))
    self.ERC1155_BATCH_ACCEPTED = "0xbc197c81"# bytes4(keccak256("onERC1155BatchReceived(address,address,uint256[],uint256[],bytes)"))

    return True


@private
@constant
def _expiry_hash(_expiry: timestamp, _underlying_address: address, _strike_price: uint256) -> bytes32:
    return keccak256(
        concat(
            convert(self, bytes32),
            convert(self.currency_address, bytes32),
            convert(_expiry, bytes32),
            convert(_underlying_address, bytes32),
            convert(_strike_price, bytes32)
        )
    )


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
def _s_currency_balance(_erc1155_id: uint256) -> uint256:
    return ERC1155(self.s_currency_address).balanceOf(self, _erc1155_id)


@private
@constant
def _u_currency_balance(_erc1155_id: uint256) -> uint256:
    return ERC1155(self.u_currency_address).balanceOf(self, _erc1155_id)


@private
@constant
def _exchange_rate() -> uint256:
    if (as_unitless_number(self._l_currency_balance()) == 0) or (ERC20(self.pool_currency_address).totalSupply() == 0):
        return self.initial_exchange_rate
    return as_unitless_number(self._l_currency_balance()) / as_unitless_number(ERC20(self.pool_currency_address).totalSupply())


@private
@constant
def _estimated_pool_tokens(_l_currency_value: uint256) -> uint256:
    return as_unitless_number(self._exchange_rate()) * as_unitless_number(_l_currency_value)


@public
@constant
def exchange_rate() -> uint256:
    return self._exchange_rate()


@public
@constant
def estimated_pool_tokens(_l_currency_value: uint256) -> uint256:
    return self._estimated_pool_tokens(_l_currency_value)


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
def register_expiry(_expiry: timestamp, _underlying_address: address, _strike_price: uint256) -> bool:
    assert msg.sender == self.operator
    _expiry_hash: bytes32 = self._expiry_hash(_expiry, _underlying_address, _strike_price)
    _external_call_successful: bool = False
    _i_hash: bytes32 = EMPTY_BYTES32
    _s_hash: bytes32 = EMPTY_BYTES32
    _u_hash: bytes32 = EMPTY_BYTES32
    _i_id: uint256 = 0
    _s_id: uint256 = 0
    _u_id: uint256 = 0
    _external_call_successful, _i_hash, _s_hash, _u_hash, _i_id, _s_id, _u_id = UnderwriterPoolDao(self.owner).register_expiry(self.pool_hash, _expiry, _underlying_address, _strike_price)
    assert _external_call_successful
    self.expiries[_expiry_hash] = Expiry({
        expiry_timestamp: _expiry,
        i_currency_hash: _i_hash,
        i_currency_id: _i_id,
        s_currency_hash: _s_hash,
        s_currency_id: _s_id,
        u_currency_hash: _u_hash,
        u_currency_id: _u_id,
        is_active: True,
        hash: _expiry_hash
    })

    return True


@public
def remove_expiry(_expiry: timestamp, _underlying_address: address, _strike_price: uint256) -> bool:
    assert msg.sender == self.operator
    _expiry_hash: bytes32 = self._expiry_hash(_expiry, _underlying_address, _strike_price)
    self.expiries[_expiry_hash].is_active = False

    return True


@public
def purchase_pool_currency(_l_currency_value: uint256) -> bool:
    # ask UnderwriterPoolDao to deposit l_tokens to self
    _external_call_successful: bool = UnderwriterPoolDao(self.owner).deposit_l_currency(self.pool_hash, msg.sender, _l_currency_value)
    assert _external_call_successful
    # mint pool tokens to msg.sender
    _external_call_successful = ERC20(self.pool_currency_address).mintAndAuthorizeMinter(
        msg.sender, self._estimated_pool_tokens(_l_currency_value))
    assert _external_call_successful

    return True


@public
def increment_i_currency_supply(_expiry: timestamp, _underlying_address: address, _strike_price: uint256, _l_currency_value: uint256) -> bool:
    # validate _l_currency_value
    assert self._l_currency_balance() >= _l_currency_value
    # validate sender
    assert msg.sender == self.operator
    # validate expiry
    _expiry_hash: bytes32 = self._expiry_hash(_expiry, _underlying_address, _strike_price)
    assert self.expiries[_expiry_hash].is_active == True, "expiry is not offered"
    _external_call_successful: bool = UnderwriterPoolDao(self.owner).l_currency_to_i_and_s_and_u_currency(
        self.pool_hash, self.expiries[_expiry_hash].s_currency_hash,
        self.expiries[_expiry_hash].u_currency_hash,
        self.expiries[_expiry_hash].i_currency_hash, _l_currency_value)
    assert _external_call_successful

    return True


@public
def decrement_i_currency_supply(_expiry: timestamp, _underlying_address: address, _strike_price: uint256, _l_currency_value: uint256) -> bool:
    # validate sender
    assert msg.sender == self.operator
    # validate expiry
    _expiry_hash: bytes32 = self._expiry_hash(_expiry, _underlying_address, _strike_price)
    assert self.expiries[_expiry_hash].is_active == True, "expiry is not offered"
    _external_call_successful: bool = UnderwriterPoolDao(self.owner).l_currency_from_i_and_s_and_u_currency(
        self.pool_hash, self.expiries[_expiry_hash].s_currency_hash,
        self.expiries[_expiry_hash].u_currency_hash,
        self.expiries[_expiry_hash].i_currency_hash, _l_currency_value)
    assert _external_call_successful

    return True


@public
def purchase_i_currency(_expiry: timestamp, _underlying_address: address, _strike_price: uint256, _i_currency_value: uint256, _l_currency_fee: uint256) -> bool:
    # validate expiry
    _expiry_hash: bytes32 = self._expiry_hash(_expiry, _underlying_address, _strike_price)
    assert self.expiries[_expiry_hash].is_active == True, "expiry is not offered"
    assert not self.expiries[_expiry_hash].i_currency_id == 0, "expiry does not have a valid i_currency id"
    _external_call_successful: bool = False
    # transfer l_tokens as fee from msg.sender to self
    if as_unitless_number(_l_currency_fee) > 0:
        _external_call_successful = ERC20(self.l_currency_address).transferFrom(
            msg.sender, self, _l_currency_fee)
        assert _external_call_successful
    # transfer i_tokens from self to msg.sender
    _external_call_successful = ERC1155(self.i_currency_address).safeTransferFrom(
        self, msg.sender,
        self.expiries[_expiry_hash].i_currency_id,
        _i_currency_value, EMPTY_BYTES32)
    assert _external_call_successful

    return True


@public
def purchase_s_currency(_expiry: timestamp, _underlying_address: address, _strike_price: uint256, _s_currency_value: uint256, _l_currency_fee: uint256) -> bool:
    # validate expiry
    _expiry_hash: bytes32 = self._expiry_hash(_expiry, _underlying_address, _strike_price)
    assert self.expiries[_expiry_hash].is_active == True, "expiry is not offered"
    assert not self.expiries[_expiry_hash].s_currency_id == 0, "expiry does not have a valid s_currency id"
    _external_call_successful: bool = False
    # transfer l_tokens as fee from msg.sender to self
    if as_unitless_number(_l_currency_fee) > 0:
        _external_call_successful = ERC20(self.l_currency_address).transferFrom(
            msg.sender, self, _l_currency_fee)
        assert _external_call_successful
    # transfer s_tokens from self to msg.sender
    _external_call_successful = ERC1155(self.s_currency_address).safeTransferFrom(
        self, msg.sender,
        self.expiries[_expiry_hash].s_currency_id,
        _s_currency_value, EMPTY_BYTES32)
    assert _external_call_successful
    # transfer u_tokens from self to msg.sender
    _external_call_successful = ERC1155(self.u_currency_address).safeTransferFrom(
        self, msg.sender,
        self.expiries[_expiry_hash].u_currency_id,
        _s_currency_value, EMPTY_BYTES32)
    assert _external_call_successful

    return True
