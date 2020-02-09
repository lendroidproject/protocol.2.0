# @version 0.1.0b16
# @notice Implementation of Lendroid v2 - Interest Pool. This Template will be provided by the Lendroid Team.
# @dev THIS CONTRACT IS CURRENTLY UNDER AUDIT
# @author Vignesh (Vii) Meenakshi Sundaram (@vignesh-msundaram)
# Lendroid Foundation


from ...interfaces import ERC20Interface
from ...interfaces import LERC20Interface
from ...interfaces import ERC20PoolTokenInterface
from ...interfaces import MultiFungibleTokenInterface
from ...interfaces import InterestPoolDaoInterface


struct Market:
    expiry: timestamp
    i_id: uint256
    f_id: uint256
    i_cost_per_day: uint256
    is_active: bool
    id: int128
    hash: bytes32


protocol_dao: public(address)
owner: public(address)
name: public(string[64])
symbol: public(string[32])
initial_exchange_rate: public(uint256)
currency: public(address)
l_address: public(address)
i_address: public(address)
f_address: public(address)
pool_share_token: public(address)
fee_percentage_per_i_token: public(uint256)
mft_expiry_limit_days: public(uint256)
operator_unwithdrawn_earnings: public(uint256)
markets: public(map(bytes32, Market))
# token balances
l_balance: uint256
i_balance: map(uint256, uint256)
f_balance: map(uint256, uint256)
f_total_balance: uint256
# market id => _market_hash
market_id_to_hash: public(map(int128, bytes32))
# market id counter
next_market_id: public(int128)

# dao_type => dao_address
daos: public(map(uint256, address))

initialized: public(bool)
accepts_public_contributions: public(bool)

DAO_INTEREST_POOL: constant(int128) = 2

DECIMALS: constant(uint256) = 10 ** 18
SECONDS_PER_DAY: constant(uint256) = 24 * 60 * 60
MAXIMUM_ALLOWED_MARKETS: constant(uint256) = 1000


@public
def initialize(
    _dao_protocol: address,
    _accepts_public_contributions: bool, _operator: address,
    _fee_percentage_per_i_token: uint256,
    _mft_expiry_limit: uint256,
    _name: string[64], _initial_exchange_rate: uint256,
    _currency: address,
    _l_address: address, _i_address: address, _f_address: address,
    _erc20_pool_token_template_address: address) -> bool:
    # validate inputs
    assert _dao_protocol.is_contract
    assert _currency.is_contract
    assert _l_address.is_contract
    assert _i_address.is_contract
    assert _f_address.is_contract
    assert _erc20_pool_token_template_address.is_contract
    assert as_unitless_number(_mft_expiry_limit) > 0
    assert as_unitless_number(_initial_exchange_rate) > 0
    assert not self.initialized
    self.initialized = True
    self.protocol_dao = _dao_protocol
    self.owner = _operator
    self.accepts_public_contributions = _accepts_public_contributions
    self.name = _name
    self.initial_exchange_rate = _initial_exchange_rate
    self.currency = _currency
    self.fee_percentage_per_i_token = _fee_percentage_per_i_token
    self.mft_expiry_limit_days = _mft_expiry_limit
    # erc20 token
    _pool_share_token: address = create_forwarder_to(_erc20_pool_token_template_address)
    self.pool_share_token = _pool_share_token
    assert_modifiable(ERC20PoolTokenInterface(_pool_share_token).initialize(_name,
        concat(_name, ".RF.", ERC20Interface(_currency).symbol()), 18, 0))

    self.l_address = _l_address
    self.f_address = _f_address
    self.i_address = _i_address

    self.daos[DAO_INTEREST_POOL] = msg.sender

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
    return ERC20PoolTokenInterface(self.pool_share_token).totalSupply()


@private
@constant
def _total_active_contributions() -> uint256:
    return as_unitless_number(self.l_balance) + as_unitless_number(self.f_total_balance)


@private
@constant
def _exchange_rate() -> uint256:
    if (self._total_pool_share_token_supply() == 0) or (as_unitless_number(self._total_active_contributions()) == 0):
        return self.initial_exchange_rate
    return (as_unitless_number(self._total_pool_share_token_supply()) * as_unitless_number(DECIMALS)) / as_unitless_number(self._total_active_contributions())


@private
@constant
def _i_token_fee(_expiry: timestamp) -> uint256:
    if _expiry < block.timestamp:
        return 0
    else:
        return (self.markets[self._market_hash(_expiry)].i_cost_per_day * (as_unitless_number(_expiry) - as_unitless_number(block.timestamp))) / as_unitless_number(SECONDS_PER_DAY)


@private
@constant
def _estimated_pool_share_tokens(_l_token_value: uint256) -> uint256:
    """
      Return the number of Pool Share Tokens for the given purchase price (L Token value) and current exchange rate
    """
    return (as_unitless_number(_l_token_value) * as_unitless_number(self._exchange_rate())) / as_unitless_number(DECIMALS)


@public
@constant
def market_hash(_expiry: timestamp) -> bytes32:
    return self._market_hash(_expiry)


@public
@constant
def total_pool_share_token_supply() -> uint256:
    return self._total_pool_share_token_supply()


@public
@constant
def l_token_balance() -> uint256:
    return self.l_balance


@public
@constant
def i_token_balance(_expiry: timestamp) -> uint256:
    if _expiry <= block.timestamp:
        return 0
    return self.i_balance[self.markets[self._market_hash(_expiry)].i_id]


@public
@constant
def f_token_balance(_expiry: timestamp) -> uint256:
    return self.f_balance[self.markets[self._market_hash(_expiry)].f_id]


@public
@constant
def total_f_token_balance() -> uint256:
    return self.f_total_balance


@public
@constant
def total_active_contributions() -> uint256:
    return self._total_active_contributions()


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


# Admin operations


@public
def set_public_contribution_acceptance(_acceptance: bool) -> bool:
    assert self.initialized
    assert msg.sender == self.owner
    self.accepts_public_contributions = _acceptance

    return True


@public
def set_mft_expiry_limit(_days: uint256) -> bool:
    assert self.initialized
    assert msg.sender == self.owner
    # verify current limit is zero / not been previously set
    assert as_unitless_number(self.mft_expiry_limit_days) == 0
    # validate _days
    assert as_unitless_number(_days) > 0
    self.mft_expiry_limit_days = _days

    return True


@public
def support_mft(_expiry: timestamp, _i_cost_per_day: uint256) -> bool:
    # validate that pool has not exceeded maximum MFT support count
    assert self.next_market_id < MAXIMUM_ALLOWED_MARKETS
    assert self.initialized
    assert msg.sender == self.owner
    _market_hash: bytes32 = self._market_hash(_expiry)
    assert self.markets[_market_hash].hash == EMPTY_BYTES32
    # verify mft_expiry_limit_days has been set
    assert self.mft_expiry_limit_days > 0
    # verify _expiry is within supported mft_expiry_limit_days
    _rolling_window: uint256 = as_unitless_number(self.mft_expiry_limit_days) * as_unitless_number(SECONDS_PER_DAY)
    assert _expiry <= block.timestamp + _rolling_window
    _external_call_successful: bool = False
    _f_id: uint256 = 0
    _i_id: uint256 = 0
    _external_call_successful, _f_id, _i_id = InterestPoolDaoInterface(self.daos[DAO_INTEREST_POOL]).register_mft_support(
        self.name, _expiry, self.f_address, self.i_address)
    assert _external_call_successful
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

    # set default balances for i_tokens and f_tokens
    self.i_balance[self.markets[_market_hash].i_id] = 0
    self.f_balance[self.markets[_market_hash].f_id] = 0

    return True


@public
def withdraw_mft_support(_expiry: timestamp) -> bool:
    assert self.initialized
    assert msg.sender == self.owner
    # validate expiry
    _market_hash: bytes32 = self._market_hash(_expiry)
    assert self.markets[_market_hash].is_active == True, "expiry is not offered"
    # validate balances of i_tokens and f_tokens
    assert self.i_balance[self.markets[_market_hash].i_id] == 0
    assert self.f_balance[self.markets[_market_hash].f_id] == 0
    # invalidate market support
    self.markets[_market_hash].is_active = False
    assert_modifiable(InterestPoolDaoInterface(self.daos[DAO_INTEREST_POOL]).deregister_mft_support(
        self.name, self.currency, _expiry
    ))

    return True


@public
def set_i_cost_per_day(_expiry: timestamp, _value: uint256) -> bool:
    # validate inputs
    assert as_unitless_number(_expiry) > 0
    assert self.initialized
    assert msg.sender == self.owner
    self.markets[self._market_hash(_expiry)].i_cost_per_day = _value

    return True


@public
def decrease_fee_percentage_per_i_token(_value: uint256) -> bool:
    assert self.initialized
    assert msg.sender == self.owner
    # only decrease
    if as_unitless_number(self.fee_percentage_per_i_token) > 0:
        assert as_unitless_number(_value) < as_unitless_number(self.fee_percentage_per_i_token)
    self.fee_percentage_per_i_token = _value

    return True


@public
def withdraw_earnings() -> bool:
    assert self.initialized
    assert msg.sender == self.owner
    if as_unitless_number(self.operator_unwithdrawn_earnings) > 0:
        _l_token_value: uint256 = self.operator_unwithdrawn_earnings
        # reset earnings
        self.operator_unwithdrawn_earnings = 0
        # transfer earnings
        assert_modifiable(LERC20Interface(self.l_address).transfer(
            self.owner, _l_token_value
        ))

    return True


@public
def deregister() -> bool:
    assert self.initialized
    assert msg.sender == self.owner
    # validate balances of l_tokens and total_f_tokens
    assert as_unitless_number(self.l_balance) + as_unitless_number(self.f_total_balance) == 0
    assert_modifiable(InterestPoolDaoInterface(self.daos[DAO_INTEREST_POOL]).deregister_pool(self.name))

    return True


@public
def increment_i_tokens(_expiry: timestamp, _l_token_value: uint256) -> bool:
    assert self.initialized
    # validate _l_token_value
    assert as_unitless_number(self.l_balance) >= _l_token_value
    # validate sender
    assert msg.sender == self.owner
    # validate expiry
    _market_hash: bytes32 = self._market_hash(_expiry)
    assert self.markets[_market_hash].is_active == True, "expiry is not offered"
    # adjust balances of l_tokens, i_tokens, f_tokens, and total_f_tokens
    self.l_balance -= as_unitless_number(_l_token_value)
    self.i_balance[self.markets[_market_hash].i_id] += as_unitless_number(_l_token_value)
    self.f_balance[self.markets[_market_hash].f_id] += as_unitless_number(_l_token_value)
    self.f_total_balance += as_unitless_number(_l_token_value)
    assert_modifiable(InterestPoolDaoInterface(self.daos[DAO_INTEREST_POOL]).split(
        self.currency, _expiry, _l_token_value))

    return True


@public
def decrement_i_tokens(_expiry: timestamp, _l_token_value: uint256) -> bool:
    assert self.initialized
    # validate sender
    assert msg.sender == self.owner
    # validate expiry
    _market_hash: bytes32 = self._market_hash(_expiry)
    assert self.markets[_market_hash].is_active == True, "expiry is not offered"
    # validate _l_token_value
    assert as_unitless_number(self.i_balance[self.markets[_market_hash].i_id]) >= _l_token_value
    # adjust balances of l_tokens, i_tokens, f_tokens, and total_f_tokens
    self.l_balance += as_unitless_number(_l_token_value)
    self.i_balance[self.markets[_market_hash].i_id] -= as_unitless_number(_l_token_value)
    self.f_balance[self.markets[_market_hash].f_id] -= as_unitless_number(_l_token_value)
    self.f_total_balance -= as_unitless_number(_l_token_value)
    assert_modifiable(InterestPoolDaoInterface(self.daos[DAO_INTEREST_POOL]).fuse(
        self.currency, _expiry, _l_token_value))

    return True


@public
def exercise_f_tokens(_expiry: timestamp, _f_token_value: uint256) -> bool:
    assert self.initialized
    # validate sender
    assert msg.sender == self.owner
    # validate expiry
    _market_hash: bytes32 = self._market_hash(_expiry)
    assert self.markets[_market_hash].is_active == True, "expiry is not offered"
    # adjust balances of l_tokens, f_tokens, and total_f_tokens
    self.l_balance += as_unitless_number(_f_token_value)
    self.f_balance[self.markets[_market_hash].f_id] -= as_unitless_number(_f_token_value)
    self.f_total_balance -= as_unitless_number(_f_token_value)
    assert_modifiable(InterestPoolDaoInterface(self.daos[DAO_INTEREST_POOL]).fuse(
        self.currency, _expiry, _f_token_value))

    return True


# Non-admin operations


@public
def contribute(_l_token_value: uint256) -> bool:
    assert self.initialized
    # verify msg.sender can participate in this operation
    if not self.accepts_public_contributions:
        assert msg.sender == self.owner
    assert as_unitless_number(_l_token_value) > 0
    # calculate pool_share_tokens to mint
    _supply: uint256 = ERC20PoolTokenInterface(self.pool_share_token).totalSupply()
    _contributions: uint256 = as_unitless_number(self.l_balance) + as_unitless_number(self.f_total_balance)
    _pool_share_token_value: uint256 = 0
    if (as_unitless_number(_supply) == 0) or (as_unitless_number(_contributions) == 0):
        _pool_share_token_value = as_unitless_number(_l_token_value) * as_unitless_number(self.initial_exchange_rate) / as_unitless_number(DECIMALS)
    else:
        _pool_share_token_value = as_unitless_number(_l_token_value) * as_unitless_number(_supply) / as_unitless_number(_contributions)
    # adjust balance of l_tokens
    self.l_balance += as_unitless_number(_l_token_value)
    # mint pool tokens to msg.sender
    assert_modifiable(ERC20PoolTokenInterface(self.pool_share_token).mintAndAuthorizeMinter(msg.sender, _pool_share_token_value))
    # ask InterestPoolDaoInterface to deposit l_tokens to self
    assert_modifiable(InterestPoolDaoInterface(self.daos[DAO_INTEREST_POOL]).deposit_l(self.name, msg.sender, _l_token_value))
    # authorize CurrencyDao to handle _l_token_value quantity of l_token
    assert_modifiable(LERC20Interface(self.l_address).approve(InterestPoolDaoInterface(self.daos[DAO_INTEREST_POOL]).currency_dao(), _l_token_value))

    return True


@public
def withdraw_contribution(_pool_share_token_value: uint256) -> bool:
    assert self.initialized
    assert as_unitless_number(_pool_share_token_value) > 0
    _supply: uint256 = ERC20PoolTokenInterface(self.pool_share_token).totalSupply()

    if as_unitless_number(self.l_balance) > 0:
        # calculate l_tokens to be transferred
        _l_token_value: uint256 = (as_unitless_number(_pool_share_token_value) * as_unitless_number(self.l_balance)) / as_unitless_number(_supply)
        # adjust balance of l_tokens
        self.l_balance -= as_unitless_number(_l_token_value)
        # transfer l_tokens from self to msg.sender
        assert_modifiable(LERC20Interface(self.l_address).transfer(msg.sender, _l_token_value))

    # burn pool_share_tokens from msg.sender by self
    assert_modifiable(ERC20PoolTokenInterface(self.pool_share_token).burnFrom(
        msg.sender, _pool_share_token_value))

    # calculate f_tokens and i_tokens to be transferred
    _f_token_value: uint256 = 0
    _i_token_value: uint256 = 0
    _market_hash: bytes32 = EMPTY_BYTES32
    _expiry: timestamp = block.timestamp

    for _market_id in range(MAXIMUM_ALLOWED_MARKETS):
        if _market_id == self.next_market_id:
            break
        _market_hash = self.market_id_to_hash[_market_id]
        assert not self.markets[_market_hash].f_id == 0, "expiry does not have a valid f_token id"
        assert not self.markets[_market_hash].i_id == 0, "expiry does not have a valid i_token id"
        # calculate f_tokens to be transferred
        _f_token_value = as_unitless_number(_pool_share_token_value) * self.f_balance[self.markets[_market_hash].f_id] / as_unitless_number(_supply)
        # calculate i_tokens to be transferred
        _i_token_value = as_unitless_number(_pool_share_token_value) * self.i_balance[self.markets[_market_hash].i_id] / as_unitless_number(_supply)
        # transfer f_tokens from self to msg.sender
        if as_unitless_number(_f_token_value) > 0:
            # adjust balance of f_tokens and total_f_tokens
            self.f_balance[self.markets[_market_hash].f_id] -= as_unitless_number(_f_token_value)
            self.f_total_balance -= as_unitless_number(_f_token_value)
            assert_modifiable(MultiFungibleTokenInterface(self.f_address).safeTransferFrom(
                self, msg.sender, self.markets[_market_hash].f_id,
                _f_token_value, EMPTY_BYTES32))
        # transfer i_tokens from self to msg.sender
        if as_unitless_number(_i_token_value) > 0:
            # adjust balance of i_tokens
            self.i_balance[self.markets[_market_hash].i_id] -= as_unitless_number(_i_token_value)
            assert_modifiable(MultiFungibleTokenInterface(self.i_address).safeTransferFrom(
                self, msg.sender, self.markets[_market_hash].i_id,
                _i_token_value, EMPTY_BYTES32))


    return True


@public
def purchase_i_tokens(_expiry: timestamp, _fee_in_l_token: uint256) -> bool:
    assert self.initialized
    # validate expiry
    _market_hash: bytes32 = self._market_hash(_expiry)
    assert self.markets[_market_hash].is_active == True, "expiry is not offered"
    assert not self.markets[_market_hash].i_id == 0, "expiry does not have a valid i_token id"
    # validate _i_token_value
    assert as_unitless_number(_fee_in_l_token) > 0
    assert as_unitless_number(self._i_token_fee(_expiry)) > 0
    _i_token_value: uint256 = as_unitless_number(_fee_in_l_token) / as_unitless_number(self._i_token_fee(_expiry))
    assert as_unitless_number(self.i_balance[self.markets[_market_hash].i_id]) >= _i_token_value
    # calculate operator fee
    _operator_fee: uint256 = (as_unitless_number(_fee_in_l_token) * self.fee_percentage_per_i_token) / 100
    # update earnings
    self.operator_unwithdrawn_earnings += as_unitless_number(_operator_fee)
    # adjust balance of l_tokens
    self.l_balance += as_unitless_number(_fee_in_l_token) - as_unitless_number(_operator_fee)
    # transfer l_tokens as fee from msg.sender to self
    assert_modifiable(LERC20Interface(self.l_address).transferFrom(
        msg.sender, self, _fee_in_l_token
    ))
    # adjust balance of i_tokens
    self.i_balance[self.markets[_market_hash].i_id] -= as_unitless_number(_i_token_value)
    # transfer i_tokens from self to msg.sender
    assert_modifiable(MultiFungibleTokenInterface(self.i_address).safeTransferFrom(
        self, msg.sender, self.markets[_market_hash].i_id,
        _i_token_value, EMPTY_BYTES32))

    return True
