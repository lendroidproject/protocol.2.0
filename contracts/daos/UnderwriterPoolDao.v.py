# Vyper version of the Lendroid protocol v2
# THIS CONTRACT HAS NOT BEEN AUDITED!


from contracts.interfaces import ERC20
from contracts.interfaces import CurrencyDao
from contracts.interfaces import UnderwriterPool
from contracts.interfaces import MarketDao
from contracts.interfaces import ShieldPayoutDao
from contracts.interfaces import PoolNameRegistry

# structs
struct Pool:
    currency_address: address
    pool_name: string[64]
    pool_address: address
    pool_operator: address
    multi_fungible_currencies_supported: uint256
    protocol_currency_staked: uint256

struct MultiFungibleCurrency:
    parent_currency_address: address
    currency_address: address
    expiry_timestamp: timestamp
    underlying_address: address
    strike_price: uint256
    has_id: bool
    token_id: uint256
    hash: bytes32

# Events
PoolRegistered: event({_operator: indexed(address), _currency_address: indexed(address), _pool_address: indexed(address)})

protocol_currency_address: public(address)
protocol_dao_address: public(address)
owner: public(address)
# dao_type => dao_address
daos: public(map(uint256, address))
# registry_type => registry_address
registries: public(map(uint256, address))
# template_name => template_contract_address
templates: public(map(uint256, address))
# pool_name => Pool
pools: public(map(string[64], Pool))
# currency_hash => MultiFungibleCurrency
multi_fungible_currencies: public(map(bytes32, MultiFungibleCurrency))
# count of multi_fungible_currencies_supported => fee_multiplies
fee_multiplier_per_multi_fungible_currency_supported: public(map(uint256, uint256))
minimum_multi_fungible_currency_support_fee: public(uint256)
# pool_name => (_multi_fungible_currency_hash => stake)
protocol_currency_staked: public(map(string[64], map(bytes32, uint256)))

MULTI_FUNGIBLE_CURRENCY_DIMENSION_I: public(uint256)
MULTI_FUNGIBLE_CURRENCY_DIMENSION_F: public(uint256)
MULTI_FUNGIBLE_CURRENCY_DIMENSION_S: public(uint256)
MULTI_FUNGIBLE_CURRENCY_DIMENSION_U: public(uint256)

REGISTRY_TYPE_POOL_NAME: public(uint256)

DAO_TYPE_CURRENCY: public(uint256)
DAO_TYPE_MARKET: public(uint256)
DAO_TYPE_SHIELD_PAYOUT: public(uint256)

TEMPLATE_TYPE_UNDERWRITER_POOL: public(uint256)
TEMPLATE_TYPE_CURRENCY_ERC20: public(uint256)

initialized: public(bool)


@private
@constant
def _is_initialized() -> bool:
    return self.initialized == True


@public
def initialize(
        _owner: address,
        _protocol_currency_address: address,
        _registry_address_pool_name: address,
        _dao_address_currency: address,
        _dao_address_market: address,
        _dao_address_shield_payout: address,
        _template_address_underwriter_pool: address,
        _template_address_currency_erc20: address
        ) -> bool:
    assert not self._is_initialized()
    self.initialized = True
    self.owner = _owner
    self.protocol_dao_address = msg.sender
    self.protocol_currency_address = _protocol_currency_address

    self.MULTI_FUNGIBLE_CURRENCY_DIMENSION_I = 1
    self.MULTI_FUNGIBLE_CURRENCY_DIMENSION_F = 2
    self.MULTI_FUNGIBLE_CURRENCY_DIMENSION_S = 3
    self.MULTI_FUNGIBLE_CURRENCY_DIMENSION_U = 4

    self.REGISTRY_TYPE_POOL_NAME = 1
    self.registries[self.REGISTRY_TYPE_POOL_NAME] = _registry_address_pool_name

    self.DAO_TYPE_CURRENCY = 1
    self.daos[self.DAO_TYPE_CURRENCY] = _dao_address_currency
    self.DAO_TYPE_MARKET = 2
    self.daos[self.DAO_TYPE_MARKET] = _dao_address_market
    self.DAO_TYPE_SHIELD_PAYOUT = 3
    self.daos[self.DAO_TYPE_SHIELD_PAYOUT] = _dao_address_shield_payout

    self.TEMPLATE_TYPE_UNDERWRITER_POOL = 1
    self.TEMPLATE_TYPE_CURRENCY_ERC20 = 2
    self.templates[self.TEMPLATE_TYPE_UNDERWRITER_POOL] = _template_address_underwriter_pool
    self.templates[self.TEMPLATE_TYPE_CURRENCY_ERC20] = _template_address_currency_erc20

    return True


@private
@constant
def _multi_fungible_currency_hash(parent_currency_address: address, _currency_address: address, _expiry: timestamp, _underlying_address: address, _strike_price: uint256) -> bytes32:
    return keccak256(
        concat(
            convert(self.protocol_dao_address, bytes32),
            convert(parent_currency_address, bytes32),
            convert(_currency_address, bytes32),
            convert(_expiry, bytes32),
            convert(_underlying_address, bytes32),
            convert(_strike_price, bytes32)
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
@constant
def _is_currency_valid(_currency_address: address) -> bool:
    return CurrencyDao(self.daos[self.DAO_TYPE_CURRENCY]).is_currency_valid(_currency_address)


@private
@constant
def _multi_fungible_addresses(_currency_address: address) -> (address, address, address, address, address):
    return CurrencyDao(self.daos[self.DAO_TYPE_CURRENCY]).multi_fungible_addresses(_currency_address)


@private
def _validate_pool(_pool_name: string[64], _pool_address: address):
    assert self.pools[_pool_name].pool_address == _pool_address


@private
def _deposit_multi_fungible_l_currency(_currency_address: address, _from: address, _to: address, _value: uint256):
    assert_modifiable(CurrencyDao(self.daos[self.DAO_TYPE_CURRENCY]).deposit_multi_fungible_l_currency(
        _currency_address, _from, _to, _value))


@private
def _deposit_erc20(_currency_address: address, _from: address, _to: address, _value: uint256):
    assert_modifiable(CurrencyDao(self.daos[self.DAO_TYPE_CURRENCY]).deposit_erc20(
        _currency_address, _from, _to, _value))


@private
def _create_erc1155_type(_parent_currency_type: uint256, _currency_address: address, _expiry: timestamp, _underlying_address: address, _strike_price: uint256) -> uint256:
    return CurrencyDao(self.daos[self.DAO_TYPE_CURRENCY]).create_erc1155_type(_parent_currency_type, _currency_address, _expiry, _underlying_address, _strike_price)


@private
def _mint_and_self_authorize_erc20(_currency_address: address, _to: address, _value: uint256):
    assert_modifiable(CurrencyDao(self.daos[self.DAO_TYPE_CURRENCY]).mint_and_self_authorize_erc20(_currency_address, _to, _value))


@private
def _burn_as_self_authorized_erc20(_currency_address: address, _to: address, _value: uint256):
    assert_modifiable(CurrencyDao(self.daos[self.DAO_TYPE_CURRENCY]).burn_as_self_authorized_erc20(_currency_address, _to, _value))


@private
def _mint_and_self_authorize_erc1155(_currency_address: address, _id: uint256, _to: address, _value: uint256):
    assert_modifiable(CurrencyDao(self.daos[self.DAO_TYPE_CURRENCY]).mint_and_self_authorize_erc1155(_currency_address, _id, _to, _value))


@private
def _burn_erc1155(_currency_address: address, _id: uint256, _to: address, _value: uint256):
    assert_modifiable(CurrencyDao(self.daos[self.DAO_TYPE_CURRENCY]).burn_erc1155(_currency_address, _id, _to, _value))


@private
@constant
def _protocol_currency_stake_value(_pool_name: string[64]) -> uint256:
    if self.pools[_pool_name].multi_fungible_currencies_supported == 0:
        return self.minimum_multi_fungible_currency_support_fee
    _multiplier: uint256 = self.fee_multiplier_per_multi_fungible_currency_supported[self.pools[_pool_name].multi_fungible_currencies_supported+1]
    if _multiplier == 0:
        _multiplier = self.fee_multiplier_per_multi_fungible_currency_supported[0]
    return as_unitless_number(self.pools[_pool_name].protocol_currency_staked) * as_unitless_number(_multiplier)


@private
def _stake_protocol_currency(_pool_name: string[64], _currency_address: address, _expiry: timestamp, _underlying_address: address, _strike_price: uint256):
    _protocol_currency_value: uint256 = self._protocol_currency_stake_value(_pool_name)
    assert as_unitless_number(_protocol_currency_value) > 0
    _shield_market_hash: bytes32 = self._shield_market_hash(_currency_address, _expiry, _underlying_address, _strike_price)
    self.pools[_pool_name].protocol_currency_staked += _protocol_currency_value
    self.pools[_pool_name].multi_fungible_currencies_supported += 1
    self.protocol_currency_staked[_pool_name][_shield_market_hash] = _protocol_currency_value
    self._deposit_erc20(self.protocol_currency_address,
        self.pools[_pool_name].pool_operator, self, _protocol_currency_value)


@private
def _release_staked_protocol_currency(_pool_name: string[64], _currency_address: address, _expiry: timestamp, _underlying_address: address, _strike_price: uint256):
    _shield_market_hash: bytes32 = self._shield_market_hash(_currency_address, _expiry, _underlying_address, _strike_price)
    # release staked lst to support fi currency
    _protocol_currency_value: uint256 = self.protocol_currency_staked[_pool_name][_shield_market_hash]
    assert as_unitless_number(_protocol_currency_value) > 0
    self.pools[_pool_name].protocol_currency_staked -= _protocol_currency_value
    self.pools[_pool_name].multi_fungible_currencies_supported -= 1
    clear(self.protocol_currency_staked[_pool_name][_shield_market_hash])
    assert_modifiable(ERC20(self.protocol_currency_address).transfer(
        self.pools[_pool_name].pool_operator, _protocol_currency_value
    ))


@public
@constant
def currency_dao_address() -> address:
    return self.daos[self.DAO_TYPE_CURRENCY]


@public
@constant
def protocol_currency_stake_value(_pool_name: string[64]) -> uint256:
    return self._protocol_currency_stake_value(_pool_name)


# admin functions


@public
def set_minimum_multi_fungible_currency_support_fee(_value: uint256) -> bool:
    assert self._is_initialized()
    assert msg.sender == self.owner
    self.minimum_multi_fungible_currency_support_fee = _value

    return True


@public
def set_fee_multiplier_per_multi_fungible_currency_supported(
    _multi_fungible_currency_count: uint256, _value: uint256) -> bool:
    assert self._is_initialized()
    assert msg.sender == self.owner
    self.fee_multiplier_per_multi_fungible_currency_supported[_multi_fungible_currency_count] = _value

    return True


@public
def set_template(_template_type: uint256, _address: address) -> bool:
    assert self._is_initialized()
    assert msg.sender == self.owner
    assert _template_type == self.TEMPLATE_TYPE_UNDERWRITER_POOL
    self.templates[_template_type] = _address
    return True


@public
def register_pool(_accepts_public_contributions: bool,
    _currency_address: address, _name: string[64], _symbol: string[32],
    _initial_exchange_rate: uint256,
    _i_currency_operator_fee_percentage: uint256,
    _s_currency_operator_fee_percentage: uint256) -> bool:
    assert self._is_initialized()
    # validate currency
    assert self._is_currency_valid(_currency_address)
    # Increment active pool count if pool name is already registered.
    # Otherwise, register pool name and increment active pool count
    if PoolNameRegistry(self.registries[self.REGISTRY_TYPE_POOL_NAME]).name_exists(_name):
        assert_modifiable(PoolNameRegistry(self.registries[self.REGISTRY_TYPE_POOL_NAME]).increment_pool_count(
            self.pools[_name].pool_name
        ))
    else:
        assert_modifiable(PoolNameRegistry(self.registries[self.REGISTRY_TYPE_POOL_NAME]).register_name_and_pool(_name, msg.sender))
    # initialize pool
    _pool_address: address = ZERO_ADDRESS
    _l_currency_address: address = ZERO_ADDRESS
    _i_currency_address: address = ZERO_ADDRESS
    _f_currency_address: address = ZERO_ADDRESS
    _s_currency_address: address = ZERO_ADDRESS
    _u_currency_address: address = ZERO_ADDRESS
    _external_call_successful: bool = False
    _pool_address = create_forwarder_to(self.templates[self.TEMPLATE_TYPE_UNDERWRITER_POOL])
    assert _pool_address.is_contract
    _l_currency_address, _i_currency_address, _f_currency_address, _s_currency_address, _u_currency_address = self._multi_fungible_addresses(_currency_address)
    _external_call_successful = UnderwriterPool(_pool_address).initialize(
        _accepts_public_contributions,
        msg.sender,
        _i_currency_operator_fee_percentage,
        _s_currency_operator_fee_percentage,
        _name, _symbol, _initial_exchange_rate,
        _currency_address,
        _l_currency_address,
        _i_currency_address,
        _s_currency_address,
        _u_currency_address,
        self.protocol_dao_address,
        self.templates[self.TEMPLATE_TYPE_CURRENCY_ERC20])
    assert _external_call_successful

    # save pool metadata
    self.pools[_name] = Pool({
        currency_address: _currency_address,
        pool_name: _name,
        pool_address: _pool_address,
        pool_operator: msg.sender,
        multi_fungible_currencies_supported: 0,
        protocol_currency_staked: 0
    })

    # log PoolRegistered event
    log.PoolRegistered(msg.sender, _currency_address, _pool_address)

    return True


@public
def register_expiry(_pool_name: string[64], _expiry: timestamp, _underlying_address: address, _strike_price: uint256) -> (bool, bytes32, bytes32, bytes32, uint256, uint256, uint256):
    assert self._is_initialized()
    self._validate_pool(_pool_name, msg.sender)
    _currency_address: address = self.pools[_pool_name].currency_address
    assert self._is_currency_valid(_currency_address)
    assert self._is_currency_valid(_underlying_address)
    _l_currency_address: address = ZERO_ADDRESS
    _i_currency_address: address = ZERO_ADDRESS
    _f_currency_address: address = ZERO_ADDRESS
    _s_currency_address: address = ZERO_ADDRESS
    _u_currency_address: address = ZERO_ADDRESS
    _l_currency_address, _i_currency_address, _f_currency_address, _s_currency_address, _u_currency_address = self._multi_fungible_addresses(_currency_address)
    _i_hash: bytes32 = self._multi_fungible_currency_hash(_i_currency_address, _currency_address, _expiry, ZERO_ADDRESS, 0)
    _s_hash: bytes32 = self._multi_fungible_currency_hash(_s_currency_address, _currency_address, _expiry, _underlying_address, _strike_price)
    _u_hash: bytes32 = self._multi_fungible_currency_hash(_u_currency_address, _currency_address, _expiry, _underlying_address, _strike_price)
    _i_id: uint256 = self.multi_fungible_currencies[_i_hash].token_id
    _s_id: uint256 = self.multi_fungible_currencies[_s_hash].token_id
    _u_id: uint256 = self.multi_fungible_currencies[_u_hash].token_id
    _payout_address: address = ZERO_ADDRESS
    # stake lst to support isu currency
    self._stake_protocol_currency(_pool_name, _currency_address, _expiry, _underlying_address, _strike_price)

    if not self.multi_fungible_currencies[_i_hash].has_id:
        _i_id = self._create_erc1155_type(self.MULTI_FUNGIBLE_CURRENCY_DIMENSION_I, _currency_address, _expiry, ZERO_ADDRESS, 0)
        self.multi_fungible_currencies[_i_hash] = MultiFungibleCurrency({
            parent_currency_address: _i_currency_address,
            currency_address: _currency_address,
            expiry_timestamp: _expiry,
            underlying_address: ZERO_ADDRESS,
            strike_price: 0,
            has_id: True,
            token_id: _i_id,
            hash: _i_hash
        })
    if not self.multi_fungible_currencies[_s_hash].has_id:
        _s_id = self._create_erc1155_type(self.MULTI_FUNGIBLE_CURRENCY_DIMENSION_S, _currency_address, _expiry, _underlying_address, _strike_price)
        self.multi_fungible_currencies[_s_hash] = MultiFungibleCurrency({
            parent_currency_address: _s_currency_address,
            currency_address: _currency_address,
            expiry_timestamp: _expiry,
            underlying_address: _underlying_address,
            strike_price: _strike_price,
            has_id: True,
            token_id: _s_id,
            hash: _s_hash
        })
    if not self.multi_fungible_currencies[_u_hash].has_id:
        _u_id = self._create_erc1155_type(self.MULTI_FUNGIBLE_CURRENCY_DIMENSION_U, _currency_address, _expiry, _underlying_address, _strike_price)
        self.multi_fungible_currencies[_u_hash] = MultiFungibleCurrency({
            parent_currency_address: _u_currency_address,
            currency_address: _currency_address,
            expiry_timestamp: _expiry,
            underlying_address: _underlying_address,
            strike_price: _strike_price,
            has_id: True,
            token_id: _u_id,
            hash: _u_hash
        })

    # create market on MarketDao
    # deploy and initialize shield payout graph via MarketDao
    # deploy and initialize collateral auction graph via MarketDao
    assert_modifiable(MarketDao(self.daos[self.DAO_TYPE_MARKET]).open_shield_market(
        _currency_address, _expiry, _underlying_address, _strike_price,
        _s_hash, _s_currency_address, _s_id,
        _u_hash, _u_currency_address, _u_id
    ))

    return True, _i_hash, _s_hash, _u_hash, _i_id, _s_id, _u_id


@public
def remove_expiry(_pool_name: string[64], _currency_address: address, _expiry: timestamp, _underlying_address: address, _strike_price: uint256) -> bool:
    assert self._is_initialized()
    self._validate_pool(_pool_name, msg.sender)
    self._release_staked_protocol_currency(_pool_name, _currency_address, _expiry, _underlying_address, _strike_price)

    return True


@public
def deposit_l_currency(_pool_name: string[64], _from: address, _value: uint256) -> bool:
    assert self._is_initialized()
    self._validate_pool(_pool_name, msg.sender)
    # validate currency
    assert self._is_currency_valid(self.pools[_pool_name].currency_address)
    self._deposit_multi_fungible_l_currency(self.pools[_pool_name].currency_address, _from, msg.sender, _value)

    return True


@public
def l_currency_to_i_and_s_and_u_currency(
    _currency_address: address, _expiry: timestamp, _underlying_address: address, _strike_price: uint256,
    _value: uint256) -> bool:
    assert self._is_initialized()
    assert self._is_currency_valid(_currency_address)
    assert self._is_currency_valid(_underlying_address)
    _l_currency_address: address = ZERO_ADDRESS
    _i_currency_address: address = ZERO_ADDRESS
    _f_currency_address: address = ZERO_ADDRESS
    _s_currency_address: address = ZERO_ADDRESS
    _u_currency_address: address = ZERO_ADDRESS
    _l_currency_address, _i_currency_address, _f_currency_address, _s_currency_address, _u_currency_address = self._multi_fungible_addresses(_currency_address)
    _i_hash: bytes32 = self._multi_fungible_currency_hash(_i_currency_address, _currency_address, _expiry, ZERO_ADDRESS, 0)
    _s_hash: bytes32 = self._multi_fungible_currency_hash(_s_currency_address, _currency_address, _expiry, _underlying_address, _strike_price)
    _u_hash: bytes32 = self._multi_fungible_currency_hash(_u_currency_address, _currency_address, _expiry, _underlying_address, _strike_price)
    # validate i, s, and u token types exists for combination of expiry, underlying, and strike
    assert self.multi_fungible_currencies[_s_hash].has_id and \
           self.multi_fungible_currencies[_u_hash].has_id and \
           self.multi_fungible_currencies[_i_hash].has_id and \
           self.multi_fungible_currencies[_s_hash].currency_address == _currency_address and \
           self.multi_fungible_currencies[_u_hash].currency_address == _currency_address and \
           self.multi_fungible_currencies[_i_hash].currency_address == _currency_address and \
           self.multi_fungible_currencies[_s_hash].underlying_address == self.multi_fungible_currencies[_u_hash].underlying_address
    # burn l_token from interest_pool account
    self._burn_as_self_authorized_erc20(_l_currency_address, msg.sender, _value)
    # mint i_token into interest_pool account
    self._mint_and_self_authorize_erc1155(
        _i_currency_address,
        self.multi_fungible_currencies[_i_hash].token_id,
        msg.sender,
        _value
    )
    self._mint_and_self_authorize_erc1155(
        _s_currency_address,
        self.multi_fungible_currencies[_s_hash].token_id,
        msg.sender,
        _value
    )
    self._mint_and_self_authorize_erc1155(
        _u_currency_address,
        self.multi_fungible_currencies[_u_hash].token_id,
        msg.sender,
        _value
    )

    return True


@public
def l_currency_from_i_and_s_and_u_currency(
    _currency_address: address, _expiry: timestamp, _underlying_address: address, _strike_price: uint256,
    _value: uint256) -> bool:
    assert self._is_initialized()
    assert self._is_currency_valid(_currency_address)
    assert self._is_currency_valid(_underlying_address)
    _l_currency_address: address = ZERO_ADDRESS
    _i_currency_address: address = ZERO_ADDRESS
    _f_currency_address: address = ZERO_ADDRESS
    _s_currency_address: address = ZERO_ADDRESS
    _u_currency_address: address = ZERO_ADDRESS
    _l_currency_address, _i_currency_address, _f_currency_address, _s_currency_address, _u_currency_address = self._multi_fungible_addresses(_currency_address)
    _i_hash: bytes32 = self._multi_fungible_currency_hash(_i_currency_address, _currency_address, _expiry, ZERO_ADDRESS, 0)
    _s_hash: bytes32 = self._multi_fungible_currency_hash(_s_currency_address, _currency_address, _expiry, _underlying_address, _strike_price)
    _u_hash: bytes32 = self._multi_fungible_currency_hash(_u_currency_address, _currency_address, _expiry, _underlying_address, _strike_price)
    # validate i, s, and u token types exists for combination of expiry, underlying, and strike
    assert self.multi_fungible_currencies[_i_hash].has_id and \
           self.multi_fungible_currencies[_s_hash].has_id and \
           self.multi_fungible_currencies[_u_hash].has_id and \
           self.multi_fungible_currencies[_i_hash].currency_address == _currency_address and \
           self.multi_fungible_currencies[_s_hash].currency_address == _currency_address and \
           self.multi_fungible_currencies[_u_hash].currency_address == _currency_address and \
           self.multi_fungible_currencies[_s_hash].underlying_address == self.multi_fungible_currencies[_u_hash].underlying_address
    # mint l_tokens to underwriter_pool account
    self._mint_and_self_authorize_erc20(_l_currency_address, msg.sender, _value)
    # burn i_tokens from underwriter_pool account
    self._burn_erc1155(
        _i_currency_address,
        self.multi_fungible_currencies[_i_hash].token_id,
        msg.sender,
        _value
    )
    # burn s_tokens from underwriter_pool account
    self._burn_erc1155(
        _s_currency_address,
        self.multi_fungible_currencies[_s_hash].token_id,
        msg.sender,
        _value
    )
    # burn u_tokens from underwriter_pool account
    self._burn_erc1155(
        _u_currency_address,
        self.multi_fungible_currencies[_u_hash].token_id,
        msg.sender,
        _value
    )


    return True


@public
def exercise_underwriter_currency(_pool_name: string[64],
    _currency_address: address, _expiry: timestamp,
    _underlying_address: address, _strike_price: uint256,
    _currency_quantity: uint256) -> bool:
    assert self._is_initialized()
    self._validate_pool(_pool_name, msg.sender)
    assert_modifiable(
        ShieldPayoutDao(self.daos[self.DAO_TYPE_SHIELD_PAYOUT]).exercise_underwriter_currency(
            _currency_address, _expiry, _underlying_address, _strike_price,
            _currency_quantity, self.pools[_pool_name].pool_operator, msg.sender
        )
    )

    return True
