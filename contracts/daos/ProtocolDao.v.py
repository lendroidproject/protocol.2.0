# Vyper version of the Lendroid protocol v2
# THIS CONTRACT HAS NOT BEEN AUDITED!


from contracts.interfaces import ERC20
from contracts.interfaces import MultiFungibleToken

from contracts.interfaces import CurrencyDao
from contracts.interfaces import InterestPoolDao
from contracts.interfaces import UnderwriterPoolDao
from contracts.interfaces import MarketDao
from contracts.interfaces import ShieldPayoutDao

from contracts.interfaces import PoolNameRegistry
from contracts.interfaces import PositionRegistry


# Structs

struct Expiry:
    expiry_timestamp: timestamp
    expiry_label: string[3]
    is_active: bool


# Events
DAOInitialized: event({_setter: indexed(address), _dao_type: indexed(int128), _dao_address: address})
RegistryInitialized: event({_setter: indexed(address), _template_type: indexed(int128), _registry_address: address})
TemplateSettingsUpdated: event({_setter: indexed(address), _template_type: indexed(int128), _template_address: address})
SystemSettingsUpdated: event({_setter: indexed(address)})

# Variables of the protocol.
LST: public(address)
# caller_type => caller_address
authorized_callers: public(map(int128, address))
# dao_type => dao_address
daos: public(map(int128, address))
# registry_type => registry_address
registries: public(map(int128, address))
# timestamp => Expiry
expiries: public(map(timestamp, Expiry))
# template_name => template_contract_address
templates: public(map(int128, address))

DAO_CURRENCY: constant(int128) = 1
DAO_INTEREST_POOL: constant(int128) = 2
DAO_UNDERWRITER_POOL: constant(int128) = 3
DAO_MARKET: constant(int128) = 4
DAO_SHIELD_PAYOUT: constant(int128) = 5

REGISTRY_POOL_NAME: constant(int128) = 1
REGISTRY_POSITION: constant(int128) = 2

TEMPLATE_TOKEN_POOL: constant(int128) = 1
TEMPLATE_INTEREST_POOL: constant(int128) = 2
TEMPLATE_UNDERWRITER_POOL: constant(int128) = 3
TEMPLATE_PRICE_ORACLE: constant(int128) = 4
TEMPLATE_COLLATERAL_AUCTION: constant(int128) = 5
TEMPLATE_ERC20: constant(int128) = 6
TEMPLATE_MFT: constant(int128) = 7

CALLER_GOVERNOR: constant(int128) = 1
CALLER_ESCAPE_HATCH_MANAGER: constant(int128) = 2
CALLER_ESCAPE_HATCH_TOKEN_HOLDER: constant(int128) = 3
CALLER_DEPLOYER: constant(int128) = 7

MFT_TYPE_F: constant(int128) = 1
MFT_TYPE_I: constant(int128) = 2
MFT_TYPE_S: constant(int128) = 3
MFT_TYPE_U: constant(int128) = 4

initialized: public(bool)


@public
def __init__(
        _LST: address,
        _governor: address,
        _escape_hatch_manager: address,
        _escape_hatch_token_holder: address,
        _template_dao_currency: address,
        _template_dao_interest_pool: address,
        _template_dao_underwriter_pool: address,
        _template_dao_market: address,
        _template_dao_shield_payout: address,
        _template_pool_name_registry: address,
        _template_token_pool: address,
        _template_interest_pool: address,
        _template_underwriter_pool: address,
        _template_position_registry: address,
        _template_price_oracle: address,
        _template_collateral_auction: address,
        _template_erc20: address,
        _template_mft: address,
    ):
    # Before init, need to deploy the following contracts as libraries:
    #. CurrencyDao
    #. InterestPoolDao
    #. UnderwriterPoolDao
    #. MarketDao
    #. ShieldPayoutDao
    #. PoolNameRegistryTemplate
    #. ERC20TokenPoolTemplate
    #. InterestPoolTemplate
    #. UnderwriterPoolTemplate
    #. PositionRegistryTemplate
    #. SimplePriceOracleTemplate
    #. SimpleCollateralAuctionCurveTemplate
    #. ERC20Template
    #. MultiFungibleTokenTemplate
    assert not self.initialized
    self.initialized = True

    self.LST = _LST

    # set authorized callers
    # governor
    self.authorized_callers[CALLER_GOVERNOR] = _governor
    # escape_hatch_manager
    self.authorized_callers[CALLER_ESCAPE_HATCH_MANAGER] = _escape_hatch_manager
    # escape_hatch_token_holder
    self.authorized_callers[CALLER_ESCAPE_HATCH_TOKEN_HOLDER] = _escape_hatch_token_holder
    # deployer
    self.authorized_callers[CALLER_DEPLOYER] = msg.sender

    # set DAO addresses
    # Currency DAO
    _dao_currency: address = create_forwarder_to(_template_dao_currency)
    assert _dao_currency.is_contract
    self.daos[DAO_CURRENCY] = _dao_currency
    # Interest Pool DAO
    _dao_interest_pool: address = create_forwarder_to(_template_dao_interest_pool)
    assert _dao_interest_pool.is_contract
    self.daos[DAO_INTEREST_POOL] = _dao_interest_pool
    # Underwriter Pool DAO
    _dao_underwriter_pool: address = create_forwarder_to(_template_dao_underwriter_pool)
    assert _dao_underwriter_pool.is_contract
    self.daos[DAO_UNDERWRITER_POOL] = _dao_underwriter_pool
    # Market DAO
    _dao_market: address = create_forwarder_to(_template_dao_market)
    assert _dao_market.is_contract
    self.daos[DAO_MARKET] = _dao_market
    # Shield Payout DAO
    _dao_shield_payout: address = create_forwarder_to(_template_dao_shield_payout)
    assert _dao_shield_payout.is_contract
    self.daos[DAO_SHIELD_PAYOUT] = _dao_shield_payout

    # set Registry addresses
    # Pool Name Registry
    _pool_name_registry: address = create_forwarder_to(_template_pool_name_registry)
    assert _pool_name_registry.is_contract
    self.registries[REGISTRY_POOL_NAME] = _pool_name_registry
    # Position Registry
    _position_registry: address = create_forwarder_to(_template_position_registry)
    assert _position_registry.is_contract
    self.registries[REGISTRY_POSITION] = _position_registry

    # set Template addresses
    # Token Pool
    assert _template_token_pool.is_contract
    self.templates[TEMPLATE_TOKEN_POOL] = _template_token_pool
    # Interest Pool
    assert _template_interest_pool.is_contract
    self.templates[TEMPLATE_INTEREST_POOL] = _template_interest_pool
    # Underwriter Pool
    assert _template_underwriter_pool.is_contract
    self.templates[TEMPLATE_UNDERWRITER_POOL] = _template_underwriter_pool
    # Price Oracle
    assert _template_price_oracle.is_contract
    self.templates[TEMPLATE_PRICE_ORACLE] = _template_price_oracle
    # Collateral Auction
    assert _template_collateral_auction.is_contract
    self.templates[TEMPLATE_COLLATERAL_AUCTION] = _template_collateral_auction
    # ERC20
    assert _template_erc20.is_contract
    self.templates[TEMPLATE_ERC20] = _template_erc20
    # MFT
    assert _template_mft.is_contract
    self.templates[TEMPLATE_MFT] = _template_mft


@private
@constant
def _mft_hash(_address: address, _currency: address, _expiry: timestamp, _underlying: address, _strike_price: uint256) -> bytes32:
    return keccak256(
        concat(
            convert(self, bytes32),
            convert(_address, bytes32),
            convert(_currency, bytes32),
            convert(_expiry, bytes32),
            convert(_underlying, bytes32),
            convert(_strike_price, bytes32)
        )
    )


@private
def _validate_caller(_caller: address, _caller_type: int128):
    assert self.initialized
    assert _caller == self.authorized_callers[_caller_type]


# Admin functions

@public
def change_governor(_address: address) -> bool:
    self._validate_caller(msg.sender, CALLER_GOVERNOR)
    # MAKE THAT CHANGE!
    self.authorized_callers[CALLER_GOVERNOR] = _address

    return True


@public
def change_escape_hatch_manager(_address: address) -> bool:
    self._validate_caller(msg.sender, CALLER_GOVERNOR)
    # MAKE THAT CHANGE!
    self.authorized_callers[CALLER_ESCAPE_HATCH_MANAGER] = _address

    return True


@public
def change_escape_hatch_token_holder(_address: address) -> bool:
    self._validate_caller(msg.sender, CALLER_GOVERNOR)
    # MAKE THAT CHANGE!
    self.authorized_callers[CALLER_ESCAPE_HATCH_TOKEN_HOLDER] = _address

    return True


### Initialization ###

#. Registries - Pool Name
@public
def initialize_pool_name_registry(
    _pool_name_registration_minimum_stake: uint256
) -> bool:
    self._validate_caller(msg.sender, CALLER_DEPLOYER)
    # initialize pool name registry
    assert_modifiable(PoolNameRegistry(self.registries[REGISTRY_POOL_NAME]).initialize(
        self.LST,
        self.daos[DAO_CURRENCY],
        self.daos[DAO_INTEREST_POOL],
        self.daos[DAO_UNDERWRITER_POOL],
        _pool_name_registration_minimum_stake
    ))

    log.RegistryInitialized(msg.sender, REGISTRY_POOL_NAME, self.registries[REGISTRY_POOL_NAME])

    return True

#. Registries - Position
@public
def initialize_position_registry() -> bool:
    self._validate_caller(msg.sender, CALLER_DEPLOYER)
    # initialize position registry
    assert_modifiable(PositionRegistry(self.registries[REGISTRY_POSITION]).initialize(
        self.LST, self.daos[DAO_MARKET]
    ))

    log.RegistryInitialized(msg.sender, REGISTRY_POSITION, self.registries[REGISTRY_POSITION])

    return True

#. DAOS - Currency DAO
@public
def initialize_currency_dao() -> bool:
    self._validate_caller(msg.sender, CALLER_DEPLOYER)
    # initialize currency dao
    assert_modifiable(CurrencyDao(self.daos[DAO_CURRENCY]).initialize(
        self.LST,
        self.templates[TEMPLATE_TOKEN_POOL],
        self.templates[TEMPLATE_ERC20],
        self.templates[TEMPLATE_MFT],
        self.registries[REGISTRY_POOL_NAME],
        self.daos[DAO_INTEREST_POOL],
        self.daos[DAO_UNDERWRITER_POOL],
        self.daos[DAO_MARKET],
        self.daos[DAO_SHIELD_PAYOUT]
    ))

    log.DAOInitialized(msg.sender, DAO_CURRENCY, self.daos[DAO_CURRENCY])

    return True

#. DAOS - Interest Pool DAO
@public
def initialize_interest_pool_dao() -> bool:
    self._validate_caller(msg.sender, CALLER_DEPLOYER)
    # initialize interest pool dao
    assert_modifiable(InterestPoolDao(self.daos[DAO_INTEREST_POOL]).initialize(
        self.LST,
        self.registries[REGISTRY_POOL_NAME],
        self.daos[DAO_CURRENCY],
        self.templates[TEMPLATE_INTEREST_POOL],
        self.templates[TEMPLATE_ERC20]
    ))

    log.DAOInitialized(msg.sender, DAO_INTEREST_POOL, self.daos[DAO_INTEREST_POOL])

    return True

#. DAOS - Underwriter Pool DAO
@public
def initialize_underwriter_pool_dao() -> bool:
    self._validate_caller(msg.sender, CALLER_DEPLOYER)
    # initialize underwriter pool dao
    assert_modifiable(UnderwriterPoolDao(self.daos[DAO_UNDERWRITER_POOL]).initialize(
        self.LST,
        self.registries[REGISTRY_POOL_NAME],
        self.daos[DAO_CURRENCY],
        self.daos[DAO_MARKET],
        self.daos[DAO_SHIELD_PAYOUT],
        self.templates[TEMPLATE_UNDERWRITER_POOL],
        self.templates[TEMPLATE_ERC20]
    ))

    log.DAOInitialized(msg.sender, DAO_UNDERWRITER_POOL, self.daos[DAO_UNDERWRITER_POOL])

    return True

#. DAOS - Market DAO
@public
def initialize_market_dao() -> bool:
    self._validate_caller(msg.sender, CALLER_DEPLOYER)
    # initialize market dao
    assert_modifiable(MarketDao(self.daos[DAO_MARKET]).initialize(
        self.LST,
        self.daos[DAO_CURRENCY],
        self.daos[DAO_INTEREST_POOL],
        self.daos[DAO_UNDERWRITER_POOL],
        self.daos[DAO_SHIELD_PAYOUT],
        self.registries[REGISTRY_POSITION],
        self.templates[TEMPLATE_COLLATERAL_AUCTION]
    ))

    log.DAOInitialized(msg.sender, DAO_MARKET, self.daos[DAO_MARKET])

    return True

#. DAOS - Shield Payout DAO
@public
def initialize_shield_payout_dao() -> bool:
    self._validate_caller(msg.sender, CALLER_DEPLOYER)
    # initialize shield payout dao
    assert_modifiable(ShieldPayoutDao(self.daos[DAO_SHIELD_PAYOUT]).initialize(
        self.LST,
        self.daos[DAO_CURRENCY],
        self.daos[DAO_MARKET]
    ))

    log.DAOInitialized(msg.sender, DAO_SHIELD_PAYOUT, self.daos[DAO_SHIELD_PAYOUT])

    return True


### SETTINGS ###


@public
def set_expiry_support(_timestamp: timestamp, _label: string[3], _is_active: bool) -> bool:
    self._validate_caller(msg.sender, CALLER_GOVERNOR)
    self.expiries[_timestamp] = Expiry({
        expiry_timestamp: _timestamp,
        expiry_label: _label,
        is_active: _is_active
    })
    return True


@public
def set_registry(_dao_type: int128, _registry_type: uint256, _address: address) -> bool:
    self._validate_caller(msg.sender, CALLER_GOVERNOR)

    if _dao_type == DAO_MARKET and _registry_type == REGISTRY_POSITION:
        assert_modifiable(MarketDao(self.daos[_dao_type]).set_registry(_registry_type, _address))

    log.SystemSettingsUpdated(msg.sender)

    return True


@public
def set_template(_template_type: int128, _address: address) -> bool:
    self._validate_caller(msg.sender, CALLER_GOVERNOR)
    self.templates[_template_type] = _address
    if _template_type == TEMPLATE_TOKEN_POOL or \
           _template_type == TEMPLATE_ERC20 or \
           _template_type == TEMPLATE_MFT:
        assert_modifiable(CurrencyDao(self.daos[DAO_CURRENCY]).set_template(
            _template_type, _address
        ))
    if _template_type == TEMPLATE_INTEREST_POOL:
        assert_modifiable(InterestPoolDao(self.daos[DAO_INTEREST_POOL]).set_template(
            _template_type, _address
        ))
    if _template_type == TEMPLATE_UNDERWRITER_POOL:
        assert_modifiable(UnderwriterPoolDao(self.daos[DAO_UNDERWRITER_POOL]).set_template(
            _template_type, _address
        ))
    if _template_type == TEMPLATE_COLLATERAL_AUCTION:
        assert_modifiable(MarketDao(self.daos[DAO_MARKET]).set_template(
            _template_type, _address
        ))

    log.TemplateSettingsUpdated(msg.sender, _template_type, _address)
    return True


#. Registries - Pool Name
@public
def set_pool_name_registration_minimum_stake(_value: uint256) -> bool:
    self._validate_caller(msg.sender, CALLER_GOVERNOR)

    assert_modifiable(PoolNameRegistry(self.registries[REGISTRY_POOL_NAME]).set_name_registration_minimum_stake(_value))

    log.SystemSettingsUpdated(msg.sender)

    return True


@public
def set_pool_name_registration_stake_lookup(_name_length: int128, _value: uint256) -> bool:
    self._validate_caller(msg.sender, CALLER_GOVERNOR)

    assert_modifiable(PoolNameRegistry(self.registries[REGISTRY_POOL_NAME]).set_name_registration_stake_lookup(_name_length, _value))

    log.SystemSettingsUpdated(msg.sender)

    return True


#. DAOS - Currency DAO
@public
def set_token_support(_token: address, _is_active: bool) -> bool:
    self._validate_caller(msg.sender, CALLER_GOVERNOR)

    assert_modifiable(CurrencyDao(self.daos[DAO_CURRENCY]).set_token_support(_token, _is_active))

    log.SystemSettingsUpdated(msg.sender)

    return True


#. DAOS - InterestPool DAO & UnderwriterPool DAO
@public
def set_minimum_mft_fee(_dao_type: int128, _value: uint256) -> bool:
    self._validate_caller(msg.sender, CALLER_GOVERNOR)
    if _dao_type == DAO_INTEREST_POOL:
        assert_modifiable(InterestPoolDao(self.daos[_dao_type]).set_minimum_mft_fee(_value))
    if _dao_type == DAO_UNDERWRITER_POOL:
        assert_modifiable(UnderwriterPoolDao(self.daos[_dao_type]).set_minimum_mft_fee(_value))

    log.SystemSettingsUpdated(msg.sender)

    return True


@public
def set_fee_multiplier_per_mft_count(_dao_type: int128, _mft_count: uint256, _value: uint256) -> bool:
    self._validate_caller(msg.sender, CALLER_GOVERNOR)
    if _dao_type == DAO_INTEREST_POOL:
        assert_modifiable(InterestPoolDao(self.daos[_dao_type]).set_fee_multiplier_per_mft_count(_mft_count, _value))
    if _dao_type == DAO_UNDERWRITER_POOL:
        assert_modifiable(UnderwriterPoolDao(self.daos[_dao_type]).set_fee_multiplier_per_mft_count(_mft_count, _value))

    log.SystemSettingsUpdated(msg.sender)

    return True


@public
def set_maximum_mft_support_count(_dao_type: int128, _value: uint256) -> bool:
    self._validate_caller(msg.sender, CALLER_GOVERNOR)
    if _dao_type == DAO_INTEREST_POOL:
        assert_modifiable(InterestPoolDao(self.daos[_dao_type]).set_maximum_mft_support_count(_value))
    if _dao_type == DAO_UNDERWRITER_POOL:
        assert_modifiable(UnderwriterPoolDao(self.daos[_dao_type]).set_maximum_mft_support_count(_value))

    log.SystemSettingsUpdated(msg.sender)

    return True


#. DAOS - Market DAO
@public
def set_price_oracle(_currency: address, _underlying: address, _oracle: address) -> bool:
    self._validate_caller(msg.sender, CALLER_GOVERNOR)

    assert_modifiable(MarketDao(self.daos[DAO_MARKET]).set_price_oracle(_currency, _underlying, _oracle))

    log.SystemSettingsUpdated(msg.sender)

    return True


@public
def set_maximum_liability_for_currency_market(_currency: address, _expiry: timestamp, _value: uint256) -> bool:
    self._validate_caller(msg.sender, CALLER_GOVERNOR)

    assert_modifiable(MarketDao(self.daos[DAO_MARKET]).set_maximum_liability_for_currency_market(_currency, _expiry, _value))

    log.SystemSettingsUpdated(msg.sender)

    return True


@public
def set_maximum_liability_for_loan_market(_currency: address, _expiry: timestamp, _underlying: address, _value: uint256) -> bool:
    self._validate_caller(msg.sender, CALLER_GOVERNOR)

    assert_modifiable(MarketDao(self.daos[DAO_MARKET]).set_maximum_liability_for_loan_market(_currency, _expiry, _underlying, _value))

    log.SystemSettingsUpdated(msg.sender)

    return True


@public
def set_auction_slippage_percentage(_value: uint256) -> bool:
    self._validate_caller(msg.sender, CALLER_GOVERNOR)

    assert_modifiable(MarketDao(self.daos[DAO_MARKET]).set_auction_slippage_percentage(_value))

    log.SystemSettingsUpdated(msg.sender)

    return True


@public
def set_auction_maximum_discount_percentage(_value: uint256) -> bool:
    self._validate_caller(msg.sender, CALLER_GOVERNOR)

    assert_modifiable(MarketDao(self.daos[DAO_MARKET]).set_auction_maximum_discount_percentage(_value))

    log.SystemSettingsUpdated(msg.sender)

    return True


@public
def set_auction_discount_duration(_value: timedelta) -> bool:
    self._validate_caller(msg.sender, CALLER_GOVERNOR)

    assert_modifiable(MarketDao(self.daos[DAO_MARKET]).set_auction_discount_duration(_value))

    log.SystemSettingsUpdated(msg.sender)

    return True


### ESCAPE HATCHES ###

# DAOS - Pause / Unpause
@public
def toggle_dao_pause(_dao_type: int128, _pause: bool) -> bool:
    self._validate_caller(msg.sender, CALLER_ESCAPE_HATCH_MANAGER)
    if _dao_type == DAO_CURRENCY:
        if _pause:
            assert_modifiable(CurrencyDao(self.daos[_dao_type]).pause())
        else:
            assert_modifiable(CurrencyDao(self.daos[_dao_type]).unpause())
        return True
    if _dao_type == DAO_INTEREST_POOL:
        if _pause:
            assert_modifiable(InterestPoolDao(self.daos[_dao_type]).pause())
        else:
            assert_modifiable(InterestPoolDao(self.daos[_dao_type]).unpause())
        return True
    if _dao_type == DAO_UNDERWRITER_POOL:
        if _pause:
            assert_modifiable(UnderwriterPoolDao(self.daos[_dao_type]).pause())
        else:
            assert_modifiable(UnderwriterPoolDao(self.daos[_dao_type]).unpause())
        return True
    if _dao_type == DAO_MARKET:
        if _pause:
            assert_modifiable(MarketDao(self.daos[_dao_type]).pause())
        else:
            assert_modifiable(MarketDao(self.daos[_dao_type]).unpause())
        return True
    if _dao_type == DAO_SHIELD_PAYOUT:
        if _pause:
            assert_modifiable(ShieldPayoutDao(self.daos[_dao_type]).pause())
        else:
            assert_modifiable(ShieldPayoutDao(self.daos[_dao_type]).unpause())
        return True

    raise("Invalid dao type")

# Registries - Pause / Unpause
@public
def toggle_registry_pause(_registry_type: int128, _pause: bool) -> bool:
    self._validate_caller(msg.sender, CALLER_ESCAPE_HATCH_MANAGER)

    if _registry_type == REGISTRY_POOL_NAME:
        if _pause:
            assert_modifiable(PoolNameRegistry(self.registries[_registry_type]).pause())
        else:
            assert_modifiable(PoolNameRegistry(self.registries[_registry_type]).unpause())
        return True
    if _registry_type == REGISTRY_POSITION:
        if _pause:
            assert_modifiable(PositionRegistry(self.registries[_registry_type]).pause())
        else:
            assert_modifiable(PositionRegistry(self.registries[_registry_type]).unpause())
        return True

    raise("Invalid registry type")

# DAOS - Escape hatch ERC20
@public
def escape_hatch_dao_erc20(_dao_type: int128, _currency: address, _is_l: bool) -> bool:
    self._validate_caller(msg.sender, CALLER_ESCAPE_HATCH_MANAGER)
    if _dao_type == DAO_CURRENCY:
        assert_modifiable(CurrencyDao(self.daos[_dao_type]).escape_hatch_erc20(_currency, _is_l))
        return True
    if _dao_type == DAO_INTEREST_POOL:
        assert_modifiable(InterestPoolDao(self.daos[_dao_type]).escape_hatch_erc20(_currency, _is_l))
        return True
    if _dao_type == DAO_UNDERWRITER_POOL:
        assert_modifiable(UnderwriterPoolDao(self.daos[_dao_type]).escape_hatch_erc20(_currency, _is_l))
        return True
    if _dao_type == DAO_MARKET:
        assert_modifiable(MarketDao(self.daos[_dao_type]).escape_hatch_erc20(_currency, _is_l))
        return True
    if _dao_type == DAO_SHIELD_PAYOUT:
        assert_modifiable(ShieldPayoutDao(self.daos[_dao_type]).escape_hatch_erc20(_currency, _is_l))
        return True

    raise("Invalid dao type")


# Registries - Escape hatch ERC20
@public
def escape_hatch_registry_erc20(_registry_type: int128, _currency: address) -> bool:
    self._validate_caller(msg.sender, CALLER_ESCAPE_HATCH_MANAGER)
    if _registry_type == REGISTRY_POOL_NAME:
        assert_modifiable(PoolNameRegistry(self.registries[_registry_type]).escape_hatch_erc20(_currency))
        return True

    raise("Invalid registry type")


# DAOS - Escape hatch MFT
@public
def escape_hatch_dao_mft(_dao_type: int128, _mft_type: int128, _currency: address, _expiry: timestamp, _underlying: address, _strike_price: uint256) -> bool:
    self._validate_caller(msg.sender, CALLER_ESCAPE_HATCH_MANAGER)
    assert _mft_type == MFT_TYPE_F or _mft_type == MFT_TYPE_I or \
           _mft_type == MFT_TYPE_S or _mft_type == MFT_TYPE_U

    if _dao_type == DAO_CURRENCY:
        assert_modifiable(CurrencyDao(self.daos[_dao_type]).escape_hatch_mft(_mft_type, _currency, _expiry, _underlying, _strike_price))
        return True
    if _dao_type == DAO_INTEREST_POOL:
        assert_modifiable(InterestPoolDao(self.daos[_dao_type]).escape_hatch_mft(_mft_type, _currency, _expiry, _underlying, _strike_price))
        return True
    if _dao_type == DAO_UNDERWRITER_POOL:
        assert_modifiable(UnderwriterPoolDao(self.daos[_dao_type]).escape_hatch_mft(_mft_type, _currency, _expiry, _underlying, _strike_price))
        return True
    if _dao_type == DAO_MARKET:
        assert_modifiable(MarketDao(self.daos[_dao_type]).escape_hatch_mft(_mft_type, _currency, _expiry, _underlying, _strike_price))
        return True
    if _dao_type == DAO_SHIELD_PAYOUT:
        assert_modifiable(ShieldPayoutDao(self.daos[_dao_type]).escape_hatch_mft(_mft_type, _currency, _expiry, _underlying, _strike_price))
        return True

    raise("Invalid dao type")


# Market DAO - Escape hatch Auction
@public
def escape_hatch_auction(_currency: address, _expiry: timestamp, _underlying: address) -> bool:
    self._validate_caller(msg.sender, CALLER_ESCAPE_HATCH_MANAGER)

    assert_modifiable(MarketDao(self.daos[DAO_MARKET]).escape_hatch_auction(_currency, _expiry, _underlying))
    return True
