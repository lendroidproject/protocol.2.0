# Vyper version of the Lendroid protocol v2
# THIS CONTRACT HAS NOT BEEN AUDITED!


from contracts.interfaces import ERC20
from contracts.interfaces import MultiFungibleToken
from contracts.interfaces import MultiFungibleTokenReceiver
from contracts.interfaces import InterestPoolDao


implements: MultiFungibleTokenReceiver


struct Market:
    expiry: timestamp
    i_id: uint256
    f_id: uint256
    i_cost_per_day: uint256
    is_active: bool
    id: uint256
    hash: bytes32

protocol_dao: public(address)
owner: public(address)
operator: public(address)
name: public(string[64])
symbol: public(string[32])
initial_exchange_rate: public(uint256)
currency: public(address)
l_address: public(address)
i_address: public(address)
f_address: public(address)
pool_share_token: public(address)
fee_percentage_per_i_token: public(uint256)
operator_earnings: public(uint256)
markets: public(map(bytes32, Market))
# market id => _market_hash
market_id_to_hash: public(map(uint256, bytes32))
# market id counter
next_market_id: public(uint256)

initialized: public(bool)
accepts_public_contributions: public(bool)

# MultiFungibleTokenReceiver interface variables
shouldReject: public(bool)
lastData: public(bytes32)
lastOperator: public(address)
lastFrom: public(address)
lastId: public(uint256)
lastValue: public(uint256)

MFT_ACCEPTED: bytes[10]


@public
def initialize(
    _dao_protocol: address,
    _accepts_public_contributions: bool,
    _operator: address, _fee_percentage_per_i_token: uint256,
    _name: string[64], _symbol: string[32], _initial_exchange_rate: uint256,
    _currency: address,
    _l_address: address, _i_address: address, _f_address: address,
    _template_token_erc20: address) -> bool:
    assert not self.initialized
    self.initialized = True
    self.protocol_dao = _dao_protocol
    self.owner = msg.sender
    self.accepts_public_contributions = _accepts_public_contributions
    self.operator = _operator
    self.name = _name
    self.initial_exchange_rate = _initial_exchange_rate
    self.currency = _currency
    self.fee_percentage_per_i_token = _fee_percentage_per_i_token
    # erc20 token
    _pool_share_token: address = create_forwarder_to(_template_token_erc20)
    self.pool_share_token = _pool_share_token
    assert_modifiable(ERC20(_pool_share_token).initialize(_name, _symbol, 18, 0))

    self.l_address = _l_address
    self.f_address = _f_address
    self.i_address = _i_address

    # bytes4(keccak256("onMFTReceived(address,address,uint256,uint256,bytes)"))
    self.MFT_ACCEPTED = "0xf23a6e61"
    self.shouldReject = False

    return True


@private
@constant
def _market_hash(_expiry: timestamp) -> bytes32:
    return keccak256(
        concat(
            convert(self.protocol_dao, bytes32),
            convert(self.currency, bytes32),
            convert(_expiry, bytes32),
            convert(ZERO_ADDRESS, bytes32),
            convert(0, bytes32)
        )
    )


@private
@constant
def _total_pool_share_token_supply() -> uint256:
    return ERC20(self.pool_share_token).totalSupply()


@private
@constant
def _l_token_balance() -> uint256:
    return as_unitless_number(ERC20(self.l_address).balanceOf(self)) - as_unitless_number(self.operator_earnings)


@private
@constant
def _i_token_balance(_expiry: timestamp) -> uint256:
    return MultiFungibleToken(self.i_address).balanceOf(self, self.markets[self._market_hash(_expiry)].i_id)


@private
@constant
def _f_token_balance(_expiry: timestamp) -> uint256:
    return MultiFungibleToken(self.f_address).balanceOf(self, self.markets[self._market_hash(_expiry)].f_id)


@private
@constant
def _total_f_token_balance() -> uint256:
    return MultiFungibleToken(self.f_address).totalBalanceOf(self)


@private
@constant
def _total_l_token_balance() -> uint256:
    return as_unitless_number(self._l_token_balance()) + as_unitless_number(self._total_f_token_balance())


@private
@constant
def _exchange_rate() -> uint256:
    if (self._total_pool_share_token_supply() == 0) or (as_unitless_number(self._total_l_token_balance()) == 0):
        return self.initial_exchange_rate
    return as_unitless_number(self._total_pool_share_token_supply()) / as_unitless_number(self._total_l_token_balance())


@private
@constant
def _i_token_fee(_expiry: timestamp) -> uint256:
    if _expiry < block.timestamp:
        return 0
    else:
        return (self.markets[self._market_hash(_expiry)].i_cost_per_day * (as_unitless_number(_expiry) - as_unitless_number(block.timestamp))) / (60 * 60 * 24)


@private
@constant
def _estimated_pool_share_tokens(_l_token_value: uint256) -> uint256:
    return as_unitless_number(self._exchange_rate()) * as_unitless_number(_l_token_value)


@public
@constant
def total_pool_share_token_supply() -> uint256:
    return self._total_pool_share_token_supply()


@public
@constant
def l_token_balance() -> uint256:
    return self._l_token_balance()


@public
@constant
def i_token_balance(_expiry: timestamp) -> uint256:
    return self._i_token_balance(_expiry)


@public
@constant
def f_token_balance(_expiry: timestamp) -> uint256:
    return self._f_token_balance(_expiry)


@public
@constant
def total_f_token_balance() -> uint256:
    return self._total_f_token_balance()


@public
@constant
def total_l_token_balance() -> uint256:
    return self._total_l_token_balance()


@public
@constant
def exchange_rate() -> uint256:
    return self._exchange_rate()


@public
@constant
def estimated_pool_share_tokens(_l_token_value: uint256) -> uint256:
    return self._estimated_pool_share_tokens(_l_token_value)


@public
@constant
def i_token_fee(_expiry: timestamp) -> uint256:
    return self._i_token_fee(_expiry)


# START of MultiFungibleTokenReceiver interface functions
@public
def setShouldReject(_value: bool):
    assert msg.sender == self.owner or msg.sender == self.operator
    self.shouldReject = _value


@public
@constant
def supportsInterface(interfaceID: bytes[10]) -> bool:
    # ERC165 or MFT_ACCEPTED
    return interfaceID == "0x01ffc9a7" or interfaceID == "0x4e2312e0"


@public
def onMFTReceived(_operator: address, _from: address, _id: uint256, _value: uint256, _data: bytes32) -> bytes[10]:
    self.lastOperator = _operator
    self.lastFrom = _from
    self.lastId = _id
    self.lastValue = _value
    self.lastData = _data
    if self.shouldReject:
        raise("onMFTReceived: transfer not accepted")
    else:
        return self.MFT_ACCEPTED


# END of MultiFungibleTokenReceiver interface functions


# Admin operations


@public
def set_public_contribution_acceptance(_acceptance: bool) -> bool:
    assert self.initialized
    assert msg.sender == self.operator
    self.accepts_public_contributions = _acceptance

    return True


@public
def support_mft(_expiry: timestamp, _i_cost_per_day: uint256) -> bool:
    assert self.initialized
    assert msg.sender == self.operator
    _external_call_successful: bool = False
    _f_id: uint256 = 0
    _i_id: uint256 = 0
    _external_call_successful, _f_id, _i_id = InterestPoolDao(self.owner).register_mft_support(
        self.name, _expiry, self.f_address, self.i_address)
    assert _external_call_successful
    _market_hash: bytes32 = self._market_hash(_expiry)
    self.markets[_market_hash] = Market({
        expiry: _expiry,
        i_id: _i_id,
        f_id: _f_id,
        i_cost_per_day: _i_cost_per_day,
        is_active: True,
        id: self.next_market_id,
        hash: _market_hash
    })
    # map market id counter to _market_hash
    self.market_id_to_hash[self.next_market_id] = _market_hash
    # increment pool id counter
    self.next_market_id += 1

    return True


@public
def withdraw_mft_support(_expiry: timestamp) -> bool:
    assert self.initialized
    assert msg.sender == self.operator
    self.markets[self._market_hash(_expiry)].is_active = False
    assert_modifiable(InterestPoolDao(self.owner).deregister_mft_support(
        self.name, _expiry
    ))

    return True


@public
def set_i_cost_per_day(_expiry: timestamp, _value: uint256) -> bool:
    assert self.initialized
    assert msg.sender == self.operator
    self.markets[self._market_hash(_expiry)].i_cost_per_day = _value

    return True


@public
def set_fee_percentage_per_i_token(_value: uint256) -> bool:
    assert self.initialized
    assert msg.sender == self.operator
    self.fee_percentage_per_i_token = _value

    return True


@public
def withdraw_earnings() -> bool:
    assert self.initialized
    assert msg.sender == self.operator
    if as_unitless_number(self.operator_earnings) > 0:
        assert_modifiable(ERC20(self.l_address).transfer(
            self.operator, self.operator_earnings
        ))

    return True


@public
def deregister() -> bool:
    assert self.initialized
    assert msg.sender == self.operator
    assert as_unitless_number(self._total_l_token_balance()) == 0
    assert_modifiable(InterestPoolDao(self.owner).deregister_pool(self.name))

    return True


@public
def increment_i_tokens(_expiry: timestamp, _l_token_value: uint256) -> bool:
    assert self.initialized
    # validate _l_token_value
    assert self._l_token_balance() >= _l_token_value
    # validate sender
    assert msg.sender == self.operator
    # validate expiry
    assert self.markets[self._market_hash(_expiry)].is_active == True, "expiry is not offered"
    assert_modifiable(InterestPoolDao(self.owner).split(
        self.currency, _expiry, _l_token_value))

    return True


@public
def decrement_i_tokens(_expiry: timestamp, _l_token_value: uint256) -> bool:
    assert self.initialized
    # validate _l_token_value
    assert self._i_token_balance(_expiry) >= _l_token_value
    # validate sender
    assert msg.sender == self.operator
    # validate expiry
    assert self.markets[self._market_hash(_expiry)].is_active == True, "expiry is not offered"
    assert_modifiable(InterestPoolDao(self.owner).fuse(
        self.currency, _expiry, _l_token_value))

    return True


# Non-admin operations


@public
def contribute(_l_token_value: uint256) -> bool:
    assert self.initialized
    # verify msg.sender can participate in this operation
    if not self.accepts_public_contributions:
        assert msg.sender == self.operator
    # ask InterestPoolDao to deposit l_tokens to self
    assert_modifiable(InterestPoolDao(self.owner).deposit_l(self.name, msg.sender, _l_token_value))
    # authorize CurrencyDao to handle _l_token_value quantity of l_token
    assert_modifiable(ERC20(self.l_address).approve(InterestPoolDao(self.owner).currency_dao(), _l_token_value))
    # mint pool tokens to msg.sender
    assert_modifiable(ERC20(self.pool_share_token).mintAndAuthorizeMinter(
        msg.sender, self._estimated_pool_share_tokens(_l_token_value)))

    return True


@public
def withdraw_contribution(_expiry: timestamp, _pool_share_token_value: uint256) -> bool:
    assert self.initialized
    # validate expiry
    _market_hash: bytes32 = self._market_hash(_expiry)
    assert self.markets[_market_hash].is_active == True, "expiry is not offered"
    assert not self.markets[_market_hash].f_id == 0, "expiry does not have a valid f_token id"
    assert not self.markets[_market_hash].i_id == 0, "expiry does not have a valid i_token id"
    # calculate l_tokens to be transferred
    _l_token_value: uint256 = as_unitless_number(_pool_share_token_value) * self._l_token_balance() / as_unitless_number(self._total_pool_share_token_supply())
    # calculate f_tokens to be transferred
    _f_token_value: uint256 = as_unitless_number(_pool_share_token_value) * self._f_token_balance(_expiry) / as_unitless_number(self._total_pool_share_token_supply())
    # calculate i_tokens to be transferred
    _i_token_value: uint256 = as_unitless_number(_pool_share_token_value) * self._i_token_balance(_expiry) / as_unitless_number(self._total_pool_share_token_supply())

    # burn pool_share_tokens from msg.sender by self
    assert_modifiable(ERC20(self.pool_share_token).burnFrom(
        msg.sender, _pool_share_token_value))
    # transfer l_tokens from self to msg.sender
    if as_unitless_number(_l_token_value) > 0:
        assert_modifiable(ERC20(self.l_address).transfer(
            msg.sender, _l_token_value))
    # transfer f_tokens from self to msg.sender
    assert_modifiable(MultiFungibleToken(self.f_address).safeTransferFrom(
        self, msg.sender,
        self.markets[_market_hash].f_id,
        _f_token_value, EMPTY_BYTES32))
    # transfer i_tokens from self to msg.sender
    if as_unitless_number(_i_token_value) > 0:
        assert_modifiable(MultiFungibleToken(self.i_address).safeTransferFrom(
            self, msg.sender,
            self.markets[_market_hash].i_id,
            _i_token_value, EMPTY_BYTES32))

    return True


@public
def purchase_i_tokens(_expiry: timestamp, _i_token_value: uint256, _fee_in_l_token: uint256) -> bool:
    assert self.initialized
    # validate expiry
    _market_hash: bytes32 = self._market_hash(_expiry)
    assert self.markets[_market_hash].is_active == True, "expiry is not offered"
    assert not self.markets[_market_hash].i_id == 0, "expiry does not have a valid i_token id"
    # validate _i_token_value
    assert self._i_token_balance(_expiry) >= _i_token_value
    # transfer l_tokens as fee from msg.sender to self
    assert as_unitless_number(_fee_in_l_token) > 0
    _operator_fee: uint256 = (as_unitless_number(_fee_in_l_token) * self.fee_percentage_per_i_token) / 100
    self.operator_earnings += as_unitless_number(_operator_fee)
    assert_modifiable(ERC20(self.l_address).transferFrom(
        msg.sender, self, _fee_in_l_token
    ))
    # transfer i_tokens from self to msg.sender
    assert_modifiable(MultiFungibleToken(self.i_address).safeTransferFrom(
        self, msg.sender,
        self.markets[_market_hash].i_id,
        _i_token_value, EMPTY_BYTES32))

    return True
