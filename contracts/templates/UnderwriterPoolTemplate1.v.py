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
    i_currency_cost_per_day: uint256
    s_currency_cost_per_day: uint256
    is_active: bool
    hash: bytes32


owner: public(address)
protocol_dao_address: public(address)
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
i_currency_operator_fee_percentage: public(uint256)
s_currency_operator_fee_percentage: public(uint256)
operator_earnings: public(uint256)
expiries: public(map(bytes32, Expiry))

is_initialized: public(bool)
accepts_public_contributions: public(bool)

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
def initialize(_accepts_public_contributions: bool,
    _operator: address,
    _i_currency_operator_fee_percentage: uint256,
    _s_currency_operator_fee_percentage: uint256,
    _name: string[64], _symbol: string[32], _initial_exchange_rate: uint256,
    _currency_address: address,
    _l_currency_address: address, _i_currency_address: address,
    _s_currency_address: address, _u_currency_address: address,
    _dao_address_protocol: address,
    _erc20_currency_template_address: address) -> bool:
    assert not self.is_initialized
    self.is_initialized = True
    self.owner = msg.sender
    self.protocol_dao_address = _dao_address_protocol
    self.operator = _operator
    self.name = _name
    self.initial_exchange_rate = _initial_exchange_rate
    self.currency_address = _currency_address
    self.i_currency_operator_fee_percentage = _i_currency_operator_fee_percentage
    self.s_currency_operator_fee_percentage = _s_currency_operator_fee_percentage
    # erc20 token
    _pool_currency_address: address = create_forwarder_to(_erc20_currency_template_address)
    self.pool_currency_address = _pool_currency_address
    assert_modifiable(ERC20(_pool_currency_address).initialize(_name, _symbol, 18, 0))

    self.l_currency_address = _l_currency_address
    self.i_currency_address = _i_currency_address
    self.s_currency_address = _s_currency_address
    self.u_currency_address = _u_currency_address

    self.ERC1155_ACCEPTED = "0xf23a6e61"# bytes4(keccak256("onERC1155Received(address,address,uint256,uint256,bytes)"))
    self.ERC1155_BATCH_ACCEPTED = "0xbc197c81"# bytes4(keccak256("onERC1155BatchReceived(address,address,uint256[],uint256[],bytes)"))

    return True


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
@constant
def _expiry_hash(_expiry: timestamp, _underlying_address: address, _strike_price: uint256) -> bytes32:
    return self._shield_market_hash(self.currency_address, _expiry, _underlying_address, _strike_price)


@private
@constant
def _l_currency_balance() -> uint256:
    return as_unitless_number(ERC20(self.l_currency_address).balanceOf(self)) - as_unitless_number(self.operator_earnings)


@private
@constant
def _i_currency_balance(_expiry: timestamp, _underlying_address: address, _strike_price: uint256) -> uint256:
    _expiry_hash: bytes32 = self._expiry_hash(_expiry, _underlying_address, _strike_price)
    return ERC1155(self.i_currency_address).balanceOf(self, self.expiries[_expiry_hash].i_currency_id)


@private
@constant
def _s_currency_balance(_expiry: timestamp, _underlying_address: address, _strike_price: uint256) -> uint256:
    _expiry_hash: bytes32 = self._expiry_hash(_expiry, _underlying_address, _strike_price)
    return ERC1155(self.s_currency_address).balanceOf(self, self.expiries[_expiry_hash].s_currency_id)


@private
@constant
def _u_currency_balance(_expiry: timestamp, _underlying_address: address, _strike_price: uint256) -> uint256:
    _expiry_hash: bytes32 = self._expiry_hash(_expiry, _underlying_address, _strike_price)
    return ERC1155(self.u_currency_address).balanceOf(self, self.expiries[_expiry_hash].u_currency_id)


@private
@constant
def _total_pool_currency_supply() -> uint256:
    return ERC20(self.pool_currency_address).totalSupply()


@private
@constant
def _exchange_rate() -> uint256:
    if (self._total_pool_currency_supply() == 0) or (as_unitless_number(self._l_currency_balance()) == 0):
        return self.initial_exchange_rate
    return as_unitless_number(self._total_pool_currency_supply()) / as_unitless_number(self._l_currency_balance())


@private
@constant
def _estimated_pool_tokens(_l_currency_value: uint256) -> uint256:
    return as_unitless_number(self._exchange_rate()) * as_unitless_number(_l_currency_value)


@public
@constant
def expiry_hash(_expiry: timestamp, _underlying_address: address, _strike_price: uint256) -> bytes32:
    return self._expiry_hash(_expiry, _underlying_address, _strike_price)


@public
@constant
def total_pool_currency_supply() -> uint256:
    return self._total_pool_currency_supply()


@public
@constant
def l_currency_balance() -> uint256:
    return self._l_currency_balance()


@public
@constant
def i_currency_balance(_expiry: timestamp, _underlying_address: address, _strike_price: uint256) -> uint256:
    return self._i_currency_balance(_expiry, _underlying_address, _strike_price)


@public
@constant
def s_currency_balance(_expiry: timestamp, _underlying_address: address, _strike_price: uint256) -> uint256:
    return self._s_currency_balance(_expiry, _underlying_address, _strike_price)


@public
@constant
def u_currency_balance(_expiry: timestamp, _underlying_address: address, _strike_price: uint256) -> uint256:
    return self._u_currency_balance(_expiry, _underlying_address, _strike_price)


@public
@constant
def exchange_rate() -> uint256:
    return self._exchange_rate()


@private
@constant
def _i_currency_fee(_expiry: timestamp, _underlying_address: address, _strike_price: uint256) -> uint256:
    if _expiry < block.timestamp:
        return 0
    else:
        _expiry_hash: bytes32 = self._expiry_hash(_expiry, _underlying_address, _strike_price)
        return (self.expiries[_expiry_hash].i_currency_cost_per_day * (as_unitless_number(_expiry) - as_unitless_number(block.timestamp))) / (60 * 60 * 24)


@private
@constant
def _s_currency_fee(_expiry: timestamp, _underlying_address: address, _strike_price: uint256) -> uint256:
    if _expiry < block.timestamp:
        return 0
    else:
        _expiry_hash: bytes32 = self._expiry_hash(_expiry, _underlying_address, _strike_price)
        return (self.expiries[_expiry_hash].s_currency_cost_per_day * (as_unitless_number(_expiry) - as_unitless_number(block.timestamp))) / (60 * 60 * 24)


@public
@constant
def estimated_pool_tokens(_l_currency_value: uint256) -> uint256:
    return self._estimated_pool_tokens(_l_currency_value)


@public
@constant
def i_currency_fee(_expiry: timestamp, _underlying_address: address, _strike_price: uint256) -> uint256:
    return self._i_currency_fee(_expiry, _underlying_address, _strike_price)


@public
@constant
def s_currency_fee(_expiry: timestamp, _underlying_address: address, _strike_price: uint256) -> uint256:
    return self._s_currency_fee(_expiry, _underlying_address, _strike_price)


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


# Admin operations


@public
def set_public_contribution_acceptance(_acceptance: bool) -> bool:
    assert self.is_initialized
    assert msg.sender == self.operator
    self.accepts_public_contributions = _acceptance

    return True


@public
def register_expiry(_expiry: timestamp, _underlying_address: address, _strike_price: uint256,
    _i_currency_cost_per_day: uint256, _s_currency_cost_per_day: uint256) -> bool:
    assert self.is_initialized
    assert msg.sender == self.operator
    _expiry_hash: bytes32 = self._expiry_hash(_expiry, _underlying_address, _strike_price)
    _external_call_successful: bool = False
    _i_hash: bytes32 = EMPTY_BYTES32
    _s_hash: bytes32 = EMPTY_BYTES32
    _u_hash: bytes32 = EMPTY_BYTES32
    _i_id: uint256 = 0
    _s_id: uint256 = 0
    _u_id: uint256 = 0
    _external_call_successful, _i_hash, _s_hash, _u_hash, _i_id, _s_id, _u_id = UnderwriterPoolDao(self.owner).register_expiry(self.name, _expiry, _underlying_address, _strike_price)
    assert _external_call_successful
    self.expiries[_expiry_hash] = Expiry({
        expiry_timestamp: _expiry,
        i_currency_hash: _i_hash,
        i_currency_id: _i_id,
        s_currency_hash: _s_hash,
        s_currency_id: _s_id,
        u_currency_hash: _u_hash,
        u_currency_id: _u_id,
        i_currency_cost_per_day: _i_currency_cost_per_day,
        s_currency_cost_per_day: _s_currency_cost_per_day,
        is_active: True,
        hash: _expiry_hash
    })

    return True


@public
def remove_expiry(_expiry: timestamp, _underlying_address: address, _strike_price: uint256) -> bool:
    assert self.is_initialized
    assert msg.sender == self.operator
    _expiry_hash: bytes32 = self._expiry_hash(_expiry, _underlying_address, _strike_price)
    self.expiries[_expiry_hash].is_active = False
    assert_modifiable(UnderwriterPoolDao(self.owner).remove_expiry(
        self.name, self.currency_address, _expiry, _underlying_address, _strike_price
    ))

    return True


@public
def set_i_currency_cost_per_day(_expiry: timestamp, _underlying_address: address, _strike_price: uint256, _value: uint256) -> bool:
    assert self.is_initialized
    assert msg.sender == self.operator
    _expiry_hash: bytes32 = self._expiry_hash(_expiry, _underlying_address, _strike_price)
    self.expiries[_expiry_hash].i_currency_cost_per_day = _value

    return True


@public
def set_s_currency_cost_per_day(_expiry: timestamp, _underlying_address: address, _strike_price: uint256, _value: uint256) -> bool:
    assert self.is_initialized
    assert msg.sender == self.operator
    _expiry_hash: bytes32 = self._expiry_hash(_expiry, _underlying_address, _strike_price)
    self.expiries[_expiry_hash].s_currency_cost_per_day = _value

    return True


@public
def set_i_currency_operator_fee_percentage(_expiry: timestamp, _underlying_address: address, _strike_price: uint256, _value: uint256) -> bool:
    assert self.is_initialized
    assert msg.sender == self.operator
    _expiry_hash: bytes32 = self._expiry_hash(_expiry, _underlying_address, _strike_price)
    self.i_currency_operator_fee_percentage = _value

    return True


@public
def set_s_currency_operator_fee_percentage(_expiry: timestamp, _underlying_address: address, _strike_price: uint256, _value: uint256) -> bool:
    assert self.is_initialized
    assert msg.sender == self.operator
    _expiry_hash: bytes32 = self._expiry_hash(_expiry, _underlying_address, _strike_price)
    self.s_currency_operator_fee_percentage = _value

    return True


@public
def withdraw_earnings() -> bool:
    assert self.is_initialized
    assert msg.sender == self.operator
    if as_unitless_number(self.operator_earnings) > 0:
        assert_modifiable(ERC20(self.l_currency_address).transfer(
            self.operator, self.operator_earnings
        ))

    return True


@public
def increment_i_currency_supply(_expiry: timestamp, _underlying_address: address, _strike_price: uint256, _l_currency_value: uint256) -> bool:
    assert self.is_initialized
    # validate _l_currency_value
    assert self._l_currency_balance() >= _l_currency_value
    # validate sender
    assert msg.sender == self.operator
    # validate expiry
    _expiry_hash: bytes32 = self._expiry_hash(_expiry, _underlying_address, _strike_price)
    assert self.expiries[_expiry_hash].is_active == True, "expiry is not offered"
    assert_modifiable(UnderwriterPoolDao(self.owner).l_currency_to_i_and_s_and_u_currency(
        self.currency_address, _expiry, _underlying_address, _strike_price,
        _l_currency_value
    ))

    return True


@public
def decrement_i_currency_supply(_expiry: timestamp, _underlying_address: address, _strike_price: uint256, _l_currency_value: uint256) -> bool:
    assert self.is_initialized
    # validate _l_currency_value
    assert self._i_currency_balance(_expiry, _underlying_address, _strike_price) >= _l_currency_value
    # validate sender
    assert msg.sender == self.operator
    # validate expiry
    _expiry_hash: bytes32 = self._expiry_hash(_expiry, _underlying_address, _strike_price)
    assert self.expiries[_expiry_hash].is_active == True, "expiry is not offered"
    assert_modifiable(UnderwriterPoolDao(self.owner).l_currency_from_i_and_s_and_u_currency(
        self.currency_address, _expiry, _underlying_address, _strike_price,
        _l_currency_value))

    return True


# Non-admin operations


@public
def purchase_pool_currency(_l_currency_value: uint256) -> bool:
    assert self.is_initialized
    # verify msg.sender can participate in this operation
    if not self.accepts_public_contributions:
        assert msg.sender == self.operator
    # ask UnderwriterPoolDao to deposit l_tokens to self
    assert_modifiable(UnderwriterPoolDao(self.owner).deposit_l_currency(
        self.name, msg.sender, _l_currency_value))
    # authorize CurrencyDao to handle _l_currency_value quantity of l_currency
    assert_modifiable(ERC20(self.l_currency_address).approve(
        UnderwriterPoolDao(self.owner).currency_dao_address(), _l_currency_value))
    # mint pool tokens to msg.sender
    assert_modifiable(ERC20(self.pool_currency_address).mintAndAuthorizeMinter(
        msg.sender, self._estimated_pool_tokens(_l_currency_value)))

    return True


@public
def redeem_pool_currency(_expiry: timestamp, _underlying_address: address, _strike_price: uint256, _pool_currency_value: uint256) -> bool:
    assert self.is_initialized
    # validate expiry
    _expiry_hash: bytes32 = self._expiry_hash(_expiry, _underlying_address, _strike_price)
    assert self.expiries[_expiry_hash].is_active == True, "expiry is not offered"
    assert not self.expiries[_expiry_hash].i_currency_id == 0, "expiry does not have a valid i_currency id"
    assert not self.expiries[_expiry_hash].s_currency_id == 0, "expiry does not have a valid s_currency id"
    assert not self.expiries[_expiry_hash].u_currency_id == 0, "expiry does not have a valid u_currency id"

    # calculate l_tokens to be transferred
    _l_currency_transfer_value: uint256 = as_unitless_number(_pool_currency_value) * self._l_currency_balance() / as_unitless_number(self._total_pool_currency_supply())
    # calculate f_tokens to be transferred
    _i_currency_transfer_value: uint256 = as_unitless_number(_pool_currency_value) * self._i_currency_balance(_expiry, _underlying_address, _strike_price) / as_unitless_number(self._total_pool_currency_supply())
    # calculate s_tokens to be transferred
    _s_currency_transfer_value: uint256 = as_unitless_number(_pool_currency_value) * self._s_currency_balance(_expiry, _underlying_address, _strike_price) / as_unitless_number(self._total_pool_currency_supply())
    # calculate u_tokens to be transferred
    _u_currency_transfer_value: uint256 = as_unitless_number(_pool_currency_value) * self._u_currency_balance(_expiry, _underlying_address, _strike_price) / as_unitless_number(self._total_pool_currency_supply())

    # burn pool_tokens from msg.sender by self
    assert_modifiable(ERC20(self.pool_currency_address).burnFrom(
        msg.sender, _pool_currency_value))
    # transfer l_tokens from self to msg.sender
    if as_unitless_number(_l_currency_transfer_value) > 0:
        assert_modifiable(ERC20(self.l_currency_address).transfer(
            msg.sender, _pool_currency_value))
    # transfer i_tokens from self to msg.sender
    if as_unitless_number(_i_currency_transfer_value) > 0:
        assert_modifiable(ERC1155(self.i_currency_address).safeTransferFrom(
            self, msg.sender,
            self.expiries[_expiry_hash].i_currency_id,
            _i_currency_transfer_value, EMPTY_BYTES32))
    # transfer s_tokens from self to msg.sender
    if as_unitless_number(_s_currency_transfer_value) > 0:
        assert_modifiable(ERC1155(self.s_currency_address).safeTransferFrom(
            self, msg.sender,
            self.expiries[_expiry_hash].s_currency_id,
            _s_currency_transfer_value, EMPTY_BYTES32))
    # transfer u_tokens from self to msg.sender
    if as_unitless_number(_u_currency_transfer_value) > 0:
        assert_modifiable(ERC1155(self.u_currency_address).safeTransferFrom(
            self, msg.sender,
            self.expiries[_expiry_hash].u_currency_id,
            _u_currency_transfer_value, EMPTY_BYTES32))

    return True


@public
def purchase_i_currency(_expiry: timestamp, _underlying_address: address, _strike_price: uint256, _i_currency_value: uint256, _fee_in_l_currency: uint256) -> bool:
    assert self.is_initialized
    # validate expiry
    _expiry_hash: bytes32 = self._expiry_hash(_expiry, _underlying_address, _strike_price)
    assert self.expiries[_expiry_hash].is_active == True, "expiry is not offered"
    assert not self.expiries[_expiry_hash].i_currency_id == 0, "expiry does not have a valid i_currency id"
    # validate _i_currency_value
    assert self._i_currency_balance(_expiry, _underlying_address, _strike_price) >= _i_currency_value
    # transfer l_tokens as fee from msg.sender to self
    assert as_unitless_number(_fee_in_l_currency) > 0
    _operator_fee: uint256 = (as_unitless_number(_fee_in_l_currency) * self.i_currency_operator_fee_percentage) / 100
    self.operator_earnings += as_unitless_number(_operator_fee)
    assert_modifiable(ERC20(self.l_currency_address).transferFrom(
        msg.sender, self, _fee_in_l_currency))
    # transfer i_tokens from self to msg.sender
    assert_modifiable(ERC1155(self.i_currency_address).safeTransferFrom(
        self, msg.sender,
        self.expiries[_expiry_hash].i_currency_id,
        _i_currency_value, EMPTY_BYTES32))

    return True


@public
def purchase_s_currency(_expiry: timestamp, _underlying_address: address, _strike_price: uint256, _s_currency_value: uint256, _fee_in_l_currency: uint256) -> bool:
    assert self.is_initialized
    # validate expiry
    _expiry_hash: bytes32 = self._expiry_hash(_expiry, _underlying_address, _strike_price)
    assert self.expiries[_expiry_hash].is_active == True, "expiry is not offered"
    assert not self.expiries[_expiry_hash].s_currency_id == 0, "expiry does not have a valid s_currency id"
    # validate _s_currency_value
    assert self._s_currency_balance(_expiry, _underlying_address, _strike_price) >= _s_currency_value
    # transfer l_tokens as fee from msg.sender to self
    assert as_unitless_number(_fee_in_l_currency) > 0
    _operator_fee: uint256 = (as_unitless_number(_fee_in_l_currency) * self.s_currency_operator_fee_percentage) / 100
    self.operator_earnings += as_unitless_number(_operator_fee)
    assert_modifiable(ERC20(self.l_currency_address).transferFrom(
        msg.sender, self, _fee_in_l_currency))
    # transfer s_tokens from self to msg.sender
    assert_modifiable(ERC1155(self.s_currency_address).safeTransferFrom(
        self, msg.sender,
        self.expiries[_expiry_hash].s_currency_id,
        _s_currency_value, EMPTY_BYTES32))

    return True


@public
def exercise_u_currency(_expiry: timestamp, _underlying_address: address, _strike_price: uint256, _u_currency_value: uint256) -> bool:
    assert self.is_initialized
    # validate sender
    assert msg.sender == self.operator
    # validate expiry
    _expiry_hash: bytes32 = self._expiry_hash(_expiry, _underlying_address, _strike_price)
    assert self.expiries[_expiry_hash].is_active == True, "expiry is not offered"
    assert_modifiable(UnderwriterPoolDao(self.owner).exercise_underwriter_currency(
        self.name,
        self.currency_address, _expiry, _underlying_address, _strike_price,
        _u_currency_value
    ))

    return True
