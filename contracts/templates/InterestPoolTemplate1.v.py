# Vyper version of the Lendroid protocol v2
# THIS CONTRACT HAS NOT BEEN AUDITED!


from contracts.interfaces import ERC20
from contracts.interfaces import ERC1155
from contracts.interfaces import ERC1155TokenReceiver
from contracts.interfaces import InterestPoolDao


implements: ERC1155TokenReceiver


struct Expiry:
    expiry_timestamp: timestamp
    i_currency_hash: bytes32
    i_currency_id: uint256
    f_currency_hash: bytes32
    f_currency_id: uint256
    i_currency_cost_per_day: uint256
    is_active: bool


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
i_currency_operator_fee_percentage: public(uint256)
operator_earnings: public(uint256)
expiries: public(map(timestamp, Expiry))

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
    _operator: address, _i_currency_operator_fee_percentage: uint256,
    _name: string[64], _symbol: string[32], _initial_exchange_rate: uint256,
    _currency_address: address,
    _l_currency_address: address, _i_currency_address: address, _f_currency_address: address,
    _erc20_currency_template_address: address) -> bool:
    assert not self.is_initialized
    self.is_initialized = True
    self.owner = msg.sender
    self.accepts_public_contributions = _accepts_public_contributions
    self.operator = _operator
    self.name = _name
    self.initial_exchange_rate = _initial_exchange_rate
    self.currency_address = _currency_address
    self.i_currency_operator_fee_percentage = _i_currency_operator_fee_percentage
    # erc20 token
    _pool_currency_address: address = create_forwarder_to(_erc20_currency_template_address)
    self.pool_currency_address = _pool_currency_address
    assert_modifiable(ERC20(_pool_currency_address).initialize(_name, _symbol, 18, 0))

    self.l_currency_address = _l_currency_address
    self.f_currency_address = _f_currency_address
    self.i_currency_address = _i_currency_address

    # bytes4(keccak256("onERC1155Received(address,address,uint256,uint256,bytes)"))
    self.ERC1155_ACCEPTED = "0xf23a6e61"
    # bytes4(keccak256("onERC1155BatchReceived(address,address,uint256[],uint256[],bytes)"))
    self.ERC1155_BATCH_ACCEPTED = "0xbc197c81"
    self.shouldReject = False

    return True


@private
@constant
def _total_pool_currency_supply() -> uint256:
    return ERC20(self.pool_currency_address).totalSupply()


@private
@constant
def _l_currency_balance() -> uint256:
    return as_unitless_number(ERC20(self.l_currency_address).balanceOf(self)) - as_unitless_number(self.operator_earnings)


@private
@constant
def _i_currency_balance(_expiry: timestamp) -> uint256:
    return ERC1155(self.i_currency_address).balanceOf(self, self.expiries[_expiry].i_currency_id)


@private
@constant
def _f_currency_balance(_expiry: timestamp) -> uint256:
    return ERC1155(self.f_currency_address).balanceOf(self, self.expiries[_expiry].f_currency_id)


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
    if (self._total_pool_currency_supply() == 0) or (as_unitless_number(self._total_l_currency_balance()) == 0):
        return self.initial_exchange_rate
    return as_unitless_number(self._total_pool_currency_supply()) / as_unitless_number(self._total_l_currency_balance())


@private
@constant
def _i_currency_fee(_expiry: timestamp) -> uint256:
    if _expiry < block.timestamp:
        return 0
    else:
        return (self.expiries[_expiry].i_currency_cost_per_day * (as_unitless_number(_expiry) - as_unitless_number(block.timestamp))) / (60 * 60 * 24)


@private
@constant
def _estimated_pool_tokens(_l_currency_value: uint256) -> uint256:
    return as_unitless_number(self._exchange_rate()) * as_unitless_number(_l_currency_value)


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
def i_currency_balance(_expiry: timestamp) -> uint256:
    return self._i_currency_balance(_expiry)


@public
@constant
def f_currency_balance(_expiry: timestamp) -> uint256:
    return self._f_currency_balance(_expiry)


@public
@constant
def total_f_currency_balance() -> uint256:
    return self._total_f_currency_balance()


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


@public
@constant
def i_currency_fee(_expiry: timestamp) -> uint256:
    return self._i_currency_fee(_expiry)


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
def register_expiry(_expiry: timestamp, _i_currency_cost_per_day: uint256) -> bool:
    assert self.is_initialized
    assert msg.sender == self.operator
    _external_call_successful: bool = False
    _f_hash: bytes32 = EMPTY_BYTES32
    _i_hash: bytes32 = EMPTY_BYTES32
    _f_id: uint256 = 0
    _i_id: uint256 = 0
    _external_call_successful, _f_hash, _i_hash, _f_id, _i_id = InterestPoolDao(self.owner).register_expiry(self.name, _expiry)
    assert _external_call_successful
    self.expiries[_expiry] = Expiry({
        expiry_timestamp: _expiry,
        i_currency_hash: _i_hash,
        i_currency_id: _i_id,
        f_currency_hash: _f_hash,
        f_currency_id: _f_id,
        i_currency_cost_per_day: _i_currency_cost_per_day,
        is_active: True
    })

    return True


@public
def remove_expiry(_expiry: timestamp) -> bool:
    assert self.is_initialized
    assert msg.sender == self.operator
    self.expiries[_expiry].is_active = False
    assert_modifiable(InterestPoolDao(self.owner).remove_expiry(
        self.name, _expiry
    ))

    return True


@public
def set_i_currency_cost_per_day(_expiry: timestamp, _value: uint256) -> bool:
    assert self.is_initialized
    assert msg.sender == self.operator
    self.expiries[_expiry].i_currency_cost_per_day = _value

    return True


@public
def set_i_currency_operator_fee_percentage(_expiry: timestamp, _value: uint256) -> bool:
    assert self.is_initialized
    assert msg.sender == self.operator
    self.i_currency_operator_fee_percentage = _value

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
def increment_i_currency_supply(_expiry: timestamp, _l_currency_value: uint256) -> bool:
    assert self.is_initialized
    # validate _l_currency_value
    assert self._l_currency_balance() >= _l_currency_value
    # validate sender
    assert msg.sender == self.operator
    # validate expiry
    assert self.expiries[_expiry].is_active == True, "expiry is not offered"
    assert_modifiable(InterestPoolDao(self.owner).l_currency_to_i_and_f_currency(
        self.currency_address, _expiry, _l_currency_value))

    return True


@public
def decrement_i_currency_supply(_expiry: timestamp, _l_currency_value: uint256) -> bool:
    assert self.is_initialized
    # validate _l_currency_value
    assert self._i_currency_balance(_expiry) >= _l_currency_value
    # validate sender
    assert msg.sender == self.operator
    # validate expiry
    assert self.expiries[_expiry].is_active == True, "expiry is not offered"
    assert_modifiable(InterestPoolDao(self.owner).l_currency_from_i_and_f_currency(
        self.currency_address, _expiry, _l_currency_value))

    return True


# Non-admin operations


@public
def purchase_pool_currency(_l_currency_value: uint256) -> bool:
    assert self.is_initialized
    # verify msg.sender can participate in this operation
    if not self.accepts_public_contributions:
        assert msg.sender == self.operator
    # ask InterestPoolDao to deposit l_tokens to self
    assert_modifiable(InterestPoolDao(self.owner).deposit_l_currency(self.name, msg.sender, _l_currency_value))
    # authorize CurrencyDao to handle _l_currency_value quantity of l_currency
    assert_modifiable(ERC20(self.l_currency_address).approve(InterestPoolDao(self.owner).currency_dao_address(), _l_currency_value))
    # mint pool tokens to msg.sender
    assert_modifiable(ERC20(self.pool_currency_address).mintAndAuthorizeMinter(
        msg.sender, self._estimated_pool_tokens(_l_currency_value)))

    return True


@public
def redeem_pool_currency(_expiry: timestamp, _pool_currency_value: uint256) -> bool:
    assert self.is_initialized
    # validate expiry
    assert self.expiries[_expiry].is_active == True, "expiry is not offered"
    assert not self.expiries[_expiry].f_currency_id == 0, "expiry does not have a valid f_currency id"
    assert not self.expiries[_expiry].i_currency_id == 0, "expiry does not have a valid f_currency id"
    # calculate l_tokens to be transferred
    _l_currency_transfer_value: uint256 = as_unitless_number(_pool_currency_value) * self._l_currency_balance() / as_unitless_number(self._total_pool_currency_supply())
    # calculate f_tokens to be transferred
    _f_currency_transfer_value: uint256 = as_unitless_number(_pool_currency_value) * self._f_currency_balance(_expiry) / as_unitless_number(self._total_pool_currency_supply())
    # calculate i_tokens to be transferred
    _i_currency_transfer_value: uint256 = as_unitless_number(_pool_currency_value) * self._i_currency_balance(_expiry) / as_unitless_number(self._total_pool_currency_supply())

    # burn pool_tokens from msg.sender by self
    assert_modifiable(ERC20(self.pool_currency_address).burnFrom(
        msg.sender, _pool_currency_value))
    # transfer l_tokens from self to msg.sender
    if as_unitless_number(_l_currency_transfer_value) > 0:
        assert_modifiable(ERC20(self.l_currency_address).transfer(
            msg.sender, _pool_currency_value))
    # transfer f_tokens from self to msg.sender
    assert_modifiable(ERC1155(self.f_currency_address).safeTransferFrom(
        self, msg.sender,
        self.expiries[_expiry].f_currency_id,
        _f_currency_transfer_value, EMPTY_BYTES32))
    # transfer i_tokens from self to msg.sender
    if as_unitless_number(_i_currency_transfer_value) > 0:
        assert_modifiable(ERC1155(self.i_currency_address).safeTransferFrom(
            self, msg.sender,
            self.expiries[_expiry].i_currency_id,
            _i_currency_transfer_value, EMPTY_BYTES32))

    return True


@public
def purchase_i_currency(_expiry: timestamp, _i_currency_value: uint256, _fee_in_l_currency: uint256) -> bool:
    assert self.is_initialized
    # validate expiry
    assert self.expiries[_expiry].is_active == True, "expiry is not offered"
    assert not self.expiries[_expiry].i_currency_id == 0, "expiry does not have a valid i_currency id"
    # validate _i_currency_value
    assert self._i_currency_balance(_expiry) >= _i_currency_value
    # transfer l_tokens as fee from msg.sender to self
    assert as_unitless_number(_fee_in_l_currency) > 0
    _operator_fee: uint256 = (as_unitless_number(_fee_in_l_currency) * self.i_currency_operator_fee_percentage) / 100
    self.operator_earnings += as_unitless_number(_operator_fee)
    assert_modifiable(ERC20(self.l_currency_address).transferFrom(
        msg.sender, self, _fee_in_l_currency
    ))
    # transfer i_tokens from self to msg.sender
    assert_modifiable(ERC1155(self.i_currency_address).safeTransferFrom(
        self, msg.sender,
        self.expiries[_expiry].i_currency_id,
        _i_currency_value, EMPTY_BYTES32))

    return True
