# Vyper version of the Lendroid protocol v2
# THIS CONTRACT HAS NOT BEEN AUDITED!


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
DAOInitialized: event({_setter: indexed(address), _dao_type: indexed(uint256), _dao_address: address})
RegistryInitialized: event({_setter: indexed(address), _template_type: indexed(uint256), _registry_address: address})
TemplateSettingsUpdated: event({_setter: indexed(address), _template_type: indexed(uint256), _template_address: address})
SystemSettingsUpdated: event({_setter: indexed(address)})

# Variables of the protocol.
LST: public(address)
owner: public(address)
# dao_type => dao_address
daos: public(map(uint256, address))
# registry_type => registry_address
registries: public(map(uint256, address))
# timestamp => Expiry
expiries: public(map(timestamp, Expiry))
# template_name => template_contract_address
templates: public(map(uint256, address))

DAO_CURRENCY: public(uint256)
DAO_INTEREST_POOL: public(uint256)
DAO_UNDERWRITER_POOL: public(uint256)
DAO_MARKET: public(uint256)
DAO_SHIELD_PAYOUT: public(uint256)

REGISTRY_POOL_NAME: public(uint256)
REGISTRY_POSITION: public(uint256)

TEMPLATE_TOKEN_POOL: public(uint256)
TEMPLATE_INTEREST_POOL: public(uint256)
TEMPLATE_UNDERWRITER_POOL: public(uint256)
TEMPLATE_PRICE_ORACLE: public(uint256)
TEMPLATE_COLLATERAL_AUCTION: public(uint256)

TEMPLATE_ERC20: public(uint256)
TEMPLATE_MFT: public(uint256)

initialized: public(bool)

# settinsg in other contracts
pool_name_registration_minimum_stake: public(uint256)


@public
def __init__(
        _LST: address,
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
    self.owner = msg.sender
    self.LST = _LST

    self.DAO_CURRENCY = 1
    self.DAO_INTEREST_POOL = 2
    self.DAO_UNDERWRITER_POOL = 3
    self.DAO_MARKET = 4
    self.DAO_SHIELD_PAYOUT = 5

    self.REGISTRY_POOL_NAME = 1
    self.REGISTRY_POSITION = 2

    self.TEMPLATE_TOKEN_POOL = 1
    self.TEMPLATE_INTEREST_POOL = 2
    self.TEMPLATE_UNDERWRITER_POOL = 3
    self.TEMPLATE_PRICE_ORACLE = 4
    self.TEMPLATE_COLLATERAL_AUCTION = 5
    self.TEMPLATE_ERC20 = 6
    self.TEMPLATE_MFT = 7

    # set DAO addresses

    # Currency DAO
    _dao_currency: address = create_forwarder_to(_template_dao_currency)
    assert _dao_currency.is_contract
    self.daos[self.DAO_CURRENCY] = _dao_currency

    # Interest Pool DAO
    _dao_interest_pool: address = create_forwarder_to(_template_dao_interest_pool)
    assert _dao_interest_pool.is_contract
    self.daos[self.DAO_INTEREST_POOL] = _dao_interest_pool

    # Underwriter Pool DAO
    _dao_underwriter_pool: address = create_forwarder_to(_template_dao_underwriter_pool)
    assert _dao_underwriter_pool.is_contract
    self.daos[self.DAO_UNDERWRITER_POOL] = _dao_underwriter_pool

    # Market DAO
    _dao_market: address = create_forwarder_to(_template_dao_market)
    assert _dao_market.is_contract
    self.daos[self.DAO_MARKET] = _dao_market

    # Shield Payout DAO
    _dao_shield_payout: address = create_forwarder_to(_template_dao_shield_payout)
    assert _dao_shield_payout.is_contract
    self.daos[self.DAO_SHIELD_PAYOUT] = _dao_shield_payout


    # set Registry addresses

    # Pool Name Registry
    _pool_name_registry: address = create_forwarder_to(_template_pool_name_registry)
    assert _pool_name_registry.is_contract
    self.registries[self.REGISTRY_POOL_NAME] = _pool_name_registry

    # Position Registry
    _position_registry: address = create_forwarder_to(_template_position_registry)
    assert _position_registry.is_contract
    self.registries[self.REGISTRY_POSITION] = _position_registry


    # set Template addresses

    # Token Pool
    assert _template_token_pool.is_contract
    self.templates[self.TEMPLATE_TOKEN_POOL] = _template_token_pool

    # Interest Pool
    assert _template_interest_pool.is_contract
    self.templates[self.TEMPLATE_INTEREST_POOL] = _template_interest_pool

    # Underwriter Pool
    assert _template_underwriter_pool.is_contract
    self.templates[self.TEMPLATE_UNDERWRITER_POOL] = _template_underwriter_pool

    # Price Oracle
    assert _template_price_oracle.is_contract
    self.templates[self.TEMPLATE_PRICE_ORACLE] = _template_price_oracle

    # Collateral Auction
    assert _template_collateral_auction.is_contract
    self.templates[self.TEMPLATE_COLLATERAL_AUCTION] = _template_collateral_auction

    # ERC20
    assert _template_erc20.is_contract
    self.templates[self.TEMPLATE_ERC20] = _template_erc20

    # MFT
    assert _template_mft.is_contract
    self.templates[self.TEMPLATE_MFT] = _template_mft


# Admin functions

# Initialize contracts

#. Registries - Pool Name
@public
def initialize_pool_name_registry() -> bool:
    assert self.initialized
    assert msg.sender == self.owner
    # initialize pool name registry
    assert_modifiable(PoolNameRegistry(self.registries[self.REGISTRY_POOL_NAME]).initialize(
        self.owner, self.LST,
        self.daos[self.DAO_CURRENCY],
        self.daos[self.DAO_INTEREST_POOL],
        self.daos[self.DAO_UNDERWRITER_POOL],
        self.pool_name_registration_minimum_stake
    ))

    log.RegistryInitialized(msg.sender, self.REGISTRY_POOL_NAME, self.registries[self.REGISTRY_POOL_NAME])

    return True


# settings - Pool Name Registry
@public
def set_pool_name_registration_minimum_stake(_value: uint256) -> bool:
    assert self.initialized
    assert msg.sender == self.owner

    self.pool_name_registration_minimum_stake = _value
    assert_modifiable(PoolNameRegistry(self.registries[self.REGISTRY_POOL_NAME]).set_name_registration_minimum_stake(_value))

    log.SystemSettingsUpdated(msg.sender)

    return True


@public
def set_pool_name_registration_stake_lookup(_name_length: int128, _value: uint256) -> bool:
    assert self.initialized
    assert msg.sender == self.owner

    assert_modifiable(PoolNameRegistry(self.registries[self.REGISTRY_POOL_NAME]).set_name_registration_stake_lookup(_name_length, _value))

    log.SystemSettingsUpdated(msg.sender)

    return True


#. Registries - Position
@public
def initialize_position_registry() -> bool:
    assert self.initialized
    assert msg.sender == self.owner
    # initialize position registry
    assert_modifiable(PositionRegistry(self.registries[self.REGISTRY_POSITION]).initialize(
        self.owner, self.LST, self.daos[self.DAO_MARKET]
    ))

    log.RegistryInitialized(msg.sender, self.REGISTRY_POSITION, self.registries[self.REGISTRY_POSITION])

    return True


#. DAOS - Currency DAO
@public
def initialize_currency_dao() -> bool:
    assert self.initialized
    assert msg.sender == self.owner
    # initialize currency dao
    assert_modifiable(CurrencyDao(self.daos[self.DAO_CURRENCY]).initialize(
        self.owner, self.LST,
        self.templates[self.TEMPLATE_TOKEN_POOL],
        self.templates[self.TEMPLATE_ERC20],
        self.templates[self.TEMPLATE_MFT],
        self.registries[self.REGISTRY_POOL_NAME],
        self.daos[self.DAO_INTEREST_POOL],
        self.daos[self.DAO_UNDERWRITER_POOL],
        self.daos[self.DAO_MARKET]
    ))

    log.DAOInitialized(msg.sender, self.DAO_CURRENCY, self.daos[self.DAO_CURRENCY])

    return True


#. DAOS - Interest Pool DAO
@public
def initialize_interest_pool_dao() -> bool:
    assert self.initialized
    assert msg.sender == self.owner
    # initialize interest pool dao
    assert_modifiable(InterestPoolDao(self.daos[self.DAO_INTEREST_POOL]).initialize(
        self.owner, self.LST,
        self.registries[self.REGISTRY_POOL_NAME],
        self.daos[self.DAO_CURRENCY],
        self.templates[self.TEMPLATE_INTEREST_POOL],
        self.templates[self.TEMPLATE_ERC20]
    ))

    log.DAOInitialized(msg.sender, self.DAO_INTEREST_POOL, self.daos[self.DAO_INTEREST_POOL])

    return True


#. DAOS - Underwriter Pool DAO
@public
def initialize_underwriter_pool_dao() -> bool:
    assert self.initialized
    assert msg.sender == self.owner
    # initialize underwriter pool dao
    assert_modifiable(UnderwriterPoolDao(self.daos[self.DAO_UNDERWRITER_POOL]).initialize(
        self.owner, self.LST,
        self.registries[self.REGISTRY_POOL_NAME],
        self.daos[self.DAO_CURRENCY],
        self.daos[self.DAO_MARKET],
        self.daos[self.DAO_SHIELD_PAYOUT],
        self.templates[self.TEMPLATE_UNDERWRITER_POOL],
        self.templates[self.TEMPLATE_ERC20]
    ))

    log.DAOInitialized(msg.sender, self.DAO_UNDERWRITER_POOL, self.daos[self.DAO_UNDERWRITER_POOL])

    return True


@public
def initialize_market_dao() -> bool:
    assert self.initialized
    assert msg.sender == self.owner
    # initialize market dao
    assert_modifiable(MarketDao(self.daos[self.DAO_MARKET]).initialize(
        self.owner, self.LST,
        self.daos[self.DAO_CURRENCY],
        self.daos[self.DAO_INTEREST_POOL],
        self.daos[self.DAO_UNDERWRITER_POOL],
        self.daos[self.DAO_SHIELD_PAYOUT],
        self.registries[self.REGISTRY_POSITION],
        self.templates[self.TEMPLATE_COLLATERAL_AUCTION]
    ))

    log.DAOInitialized(msg.sender, self.DAO_MARKET, self.daos[self.DAO_MARKET])

    return True


@public
def initialize_shield_payout_dao() -> bool:
    assert self.initialized
    assert msg.sender == self.owner
    # initialize shield payout dao
    assert_modifiable(ShieldPayoutDao(self.daos[self.DAO_SHIELD_PAYOUT]).initialize(
        self.owner, self.LST,
        self.daos[self.DAO_CURRENCY],
        self.daos[self.DAO_UNDERWRITER_POOL],
        self.daos[self.DAO_MARKET]
    ))

    log.DAOInitialized(msg.sender, self.DAO_SHIELD_PAYOUT, self.daos[self.DAO_SHIELD_PAYOUT])

    return True


@public
def set_expiry_support(_timestamp: timestamp, _label: string[3], _is_active: bool) -> bool:
    assert self.initialized
    assert msg.sender == self.owner
    self.expiries[_timestamp] = Expiry({
        expiry_timestamp: _timestamp,
        expiry_label: _label,
        is_active: _is_active
    })
    return True


@public
def set_template(_template_type: uint256, _address: address) -> bool:
    assert self.initialized
    assert msg.sender == self.owner
    self.templates[_template_type] = _address
    log.TemplateSettingsUpdated(msg.sender, _template_type, _address)
    return True


# Escape-hatches
@public
def pause_dao_currency() -> bool:
    assert self.initialized
    assert msg.sender == self.owner
    assert_modifiable(CurrencyDao(self.daos[self.DAO_CURRENCY]).pause())
    return True


@public
def pause_dao_interest_pool() -> bool:
    assert self.initialized
    assert msg.sender == self.owner
    assert_modifiable(InterestPoolDao(self.daos[self.DAO_INTEREST_POOL]).pause())
    return True


@public
def pause_dao_underwriter_pool() -> bool:
    assert self.initialized
    assert msg.sender == self.owner
    assert_modifiable(UnderwriterPoolDao(self.daos[self.DAO_UNDERWRITER_POOL]).pause())
    return True


@public
def pause_dao_market() -> bool:
    assert self.initialized
    assert msg.sender == self.owner
    assert_modifiable(MarketDao(self.daos[self.DAO_MARKET]).pause())
    return True


@public
def pause_dao_shield_payout() -> bool:
    assert self.initialized
    assert msg.sender == self.owner
    assert_modifiable(ShieldPayoutDao(self.daos[self.DAO_SHIELD_PAYOUT]).pause())
    return True


@public
def pause_registry_pool_name() -> bool:
    assert self.initialized
    assert msg.sender == self.owner
    assert_modifiable(PoolNameRegistry(self.daos[self.REGISTRY_POOL_NAME]).pause())
    return True


@public
def pause_registry_position() -> bool:
    assert self.initialized
    assert msg.sender == self.owner
    assert_modifiable(PositionRegistry(self.daos[self.REGISTRY_POSITION]).pause())
    return True
