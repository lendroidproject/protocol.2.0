# @version 0.1.0b16
# @notice Implementation of Lendroid v2 - Protocol DAO
# @dev THIS CONTRACT IS CURRENTLY UNDER AUDIT
# @author Vignesh (Vii) Meenakshi Sundaram (@vignesh-msundaram)
# Lendroid Foundation


from ...interfaces import CurrencyDaoInterface
from ...interfaces import InterestPoolDaoInterface
from ...interfaces import UnderwriterPoolDaoInterface
from ...interfaces import MarketDaoInterface
from ...interfaces import ShieldPayoutDaoInterface

from ...interfaces import PoolNameRegistryInterface
from ...interfaces import PositionRegistryInterface


# Structs

struct Expiry:
    expiry_timestamp: timestamp
    expiry_label: string[3]
    is_active: bool


# Events

DAOInitialized: event({_setter: indexed(address), _dao_type: indexed(int128), _dao_address: address})
RegistryInitialized: event({_setter: indexed(address), _template_type: indexed(int128), _registry_address: indexed(address)})
TemplateSettingsUpdated: event({_setter: indexed(address), _template_type: indexed(int128), _template_address: address})
AuthorizedCallerUpdated: event({_caller_type: indexed(int128), _caller: indexed(address), _authorized_caller: indexed(address)})
SystemSettingsUpdated: event({_setter: indexed(address)})


# Variables

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
# initial settings
public_contributions_activated: public(bool)
non_standard_expiries_activated: public(bool)

initialized: public(bool)

# Constants used throughout the System

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
TEMPLATE_LERC20: constant(int128) = 8
TEMPLATE_ERC20_POOL_TOKEN: constant(int128) = 9

CALLER_GOVERNOR: constant(int128) = 1
CALLER_ESCAPE_HATCH_MANAGER: constant(int128) = 2
CALLER_ESCAPE_HATCH_TOKEN_HOLDER: constant(int128) = 3
CALLER_DEPLOYER: constant(int128) = 7

MFT_TYPE_F: constant(int128) = 1
MFT_TYPE_I: constant(int128) = 2
MFT_TYPE_S: constant(int128) = 3
MFT_TYPE_U: constant(int128) = 4


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
        _template_position_registry: address,
        _template_token_pool: address,
        _template_interest_pool: address,
        _template_underwriter_pool: address,
        _template_price_oracle: address,
        _template_collateral_auction: address,
        _template_erc20: address,
        _template_mft: address,
        _template_lerc20: address,
        _template_erc20_pool_token: address
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
    # validate inputs
    assert _LST.is_contract
    assert _template_dao_currency.is_contract
    assert _template_dao_interest_pool.is_contract
    assert _template_dao_underwriter_pool.is_contract
    assert _template_dao_market.is_contract
    assert _template_dao_shield_payout.is_contract
    assert _template_pool_name_registry.is_contract
    assert _template_position_registry.is_contract
    assert _template_token_pool.is_contract
    assert _template_interest_pool.is_contract
    assert _template_price_oracle.is_contract
    assert _template_collateral_auction.is_contract
    assert _template_erc20.is_contract
    assert _template_mft.is_contract
    assert _template_lerc20.is_contract
    assert _template_erc20_pool_token.is_contract
    assert not self.initialized
    self.initialized = True

    self.LST = _LST

    # initial settings
    self.public_contributions_activated = False

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
    # LERC20
    assert _template_lerc20.is_contract
    self.templates[TEMPLATE_LERC20] = _template_lerc20
    # ERC20PoolToken
    assert _template_erc20_pool_token.is_contract
    self.templates[TEMPLATE_ERC20_POOL_TOKEN] = _template_erc20_pool_token


### Internal functions ###


@private
@constant
def _mft_hash(_address: address, _currency: address, _expiry: timestamp, _underlying: address, _strike_price: uint256) -> bytes32:
    """
        @dev Function to get the hash of a MFT, given its address and indicators.
             This is an internal function and is used only within the context of
             this contract.
        @param _address The address of the MFT.
        @param _currency The address of the currency token in the MFT.
        @param _expiry The timestamp when the MFT expires.
        @param _underlying The address of the underlying token in the MFT.
        @param _strike_price The price of the underlying per currency at _expiry.
        @return A unique bytes32 representing the MFT at the given address and indicators.
    """
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
    """
        @dev Function to validate if a given address is an authorized caller.
             This is an internal function and is used only within the context of
             this contract.
        @param _caller The address of the caller.
        @param _caller_type The type of caller supported by the system.
    """
    assert self.initialized
    assert _caller == self.authorized_callers[_caller_type]


### External functions ###


# Admin functions

@public
def change_governor(_address: address) -> bool:
    """
        @dev Function to change the Governor of the system.
             Only the Governor can call this function.
        @param _address The address of the new Governor.
        @return A bool with a value of "True" indicating the change has been made.
    """
    self._validate_caller(msg.sender, CALLER_GOVERNOR)
    # MAKE THAT CHANGE!
    self.authorized_callers[CALLER_GOVERNOR] = _address

    log.AuthorizedCallerUpdated(CALLER_GOVERNOR, msg.sender, _address)

    return True


@public
def change_escape_hatch_manager(_address: address) -> bool:
    """
        @dev Function to change the Escape Hatch Manager of the system.
             Only the Governor can call this function.
        @param _address The address of the new Escape Hatch Manager.
        @return A bool with a value of "True" indicating the change has been made.
    """
    self._validate_caller(msg.sender, CALLER_GOVERNOR)
    # MAKE THAT CHANGE!
    self.authorized_callers[CALLER_ESCAPE_HATCH_MANAGER] = _address

    log.AuthorizedCallerUpdated(CALLER_ESCAPE_HATCH_MANAGER, msg.sender, _address)

    return True


@public
def change_escape_hatch_token_holder(_address: address) -> bool:
    """
        @dev Function to change the Escape Hatch Token Holder of the system.
             Only the Governor can call this function.
        @param _address The address of the new Escape Hatch Token Holder.
        @return A bool with a value of "True" indicating the change has been made.
    """
    self._validate_caller(msg.sender, CALLER_GOVERNOR)
    # MAKE THAT CHANGE!
    self.authorized_callers[CALLER_ESCAPE_HATCH_TOKEN_HOLDER] = _address

    log.AuthorizedCallerUpdated(CALLER_ESCAPE_HATCH_TOKEN_HOLDER, msg.sender, _address)

    return True


## Initialization - Performed by only Deployer ##

#. Registries - Pool Name
@public
def initialize_pool_name_registry(
    _pool_name_registration_minimum_stake: uint256
) -> bool:
    """
        @dev Function to initialize the Pool Name Registry.
             Only the current Deployer can call this function.
        @param _pool_name_registration_minimum_stake The minimum stake value.
        @return A bool with a value of "True" indicating the Pool Name Registry
             has been initialized.
    """
    self._validate_caller(msg.sender, CALLER_DEPLOYER)
    # initialize pool name registry
    assert_modifiable(PoolNameRegistryInterface(self.registries[REGISTRY_POOL_NAME]).initialize(
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
    """
        @dev Function to initialize the Position Registry.
             Only the current Deployer can call this function.
        @return A bool with a value of "True" indicating the Position Registry
             has been initialized.
    """
    self._validate_caller(msg.sender, CALLER_DEPLOYER)
    # initialize position registry
    assert_modifiable(PositionRegistryInterface(self.registries[REGISTRY_POSITION]).initialize(
        self.LST, self.daos[DAO_MARKET]
    ))

    log.RegistryInitialized(msg.sender, REGISTRY_POSITION, self.registries[REGISTRY_POSITION])

    return True

#. DAOS - Currency DAO
@public
def initialize_currency_dao() -> bool:
    """
        @dev Function to initialize the Currency DAO.
             Only the current Deployer can call this function.
        @return A bool with a value of "True" indicating the Currency DAO
             has been initialized.
    """
    self._validate_caller(msg.sender, CALLER_DEPLOYER)
    # initialize currency dao
    assert_modifiable(CurrencyDaoInterface(self.daos[DAO_CURRENCY]).initialize(
        self.LST,
        self.templates[TEMPLATE_TOKEN_POOL],
        self.templates[TEMPLATE_ERC20],
        self.templates[TEMPLATE_MFT],
        self.templates[TEMPLATE_LERC20],
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
    """
        @dev Function to initialize the Interest Pool DAO.
             Only the current Deployer can call this function.
        @return A bool with a value of "True" indicating the Interest Pool DAO
             has been initialized.
    """
    self._validate_caller(msg.sender, CALLER_DEPLOYER)
    # initialize interest pool dao
    assert_modifiable(InterestPoolDaoInterface(self.daos[DAO_INTEREST_POOL]).initialize(
        self.LST,
        self.registries[REGISTRY_POOL_NAME],
        self.daos[DAO_CURRENCY],
        self.templates[TEMPLATE_INTEREST_POOL],
        self.templates[TEMPLATE_ERC20],
        self.templates[TEMPLATE_ERC20_POOL_TOKEN]
    ))

    log.DAOInitialized(msg.sender, DAO_INTEREST_POOL, self.daos[DAO_INTEREST_POOL])

    return True

#. DAOS - Underwriter Pool DAO
@public
def initialize_underwriter_pool_dao() -> bool:
    """
        @dev Function to initialize the Underwriter Pool DAO.
             Only the current Deployer can call this function.
        @return A bool with a value of "True" indicating the Underwriter Pool DAO
             has been initialized.
    """
    self._validate_caller(msg.sender, CALLER_DEPLOYER)
    # initialize underwriter pool dao
    assert_modifiable(UnderwriterPoolDaoInterface(self.daos[DAO_UNDERWRITER_POOL]).initialize(
        self.LST,
        self.registries[REGISTRY_POOL_NAME],
        self.daos[DAO_CURRENCY],
        self.daos[DAO_MARKET],
        self.daos[DAO_SHIELD_PAYOUT],
        self.templates[TEMPLATE_UNDERWRITER_POOL],
        self.templates[TEMPLATE_ERC20],
        self.templates[TEMPLATE_ERC20_POOL_TOKEN]
    ))

    log.DAOInitialized(msg.sender, DAO_UNDERWRITER_POOL, self.daos[DAO_UNDERWRITER_POOL])

    return True

#. DAOS - Market DAO
@public
def initialize_market_dao() -> bool:
    """
        @dev Function to initialize the Market DAO.
             Only the current Deployer can call this function.
        @return A bool with a value of "True" indicating the Market DAO
             has been initialized.
    """
    self._validate_caller(msg.sender, CALLER_DEPLOYER)
    # initialize market dao
    assert_modifiable(MarketDaoInterface(self.daos[DAO_MARKET]).initialize(
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
    """
        @dev Function to initialize the Shield Payout DAO.
             Only the current Deployer can call this function.
        @return A bool with a value of "True" indicating the Shield Payout DAO
             has been initialized.
    """
    self._validate_caller(msg.sender, CALLER_DEPLOYER)
    # initialize shield payout dao
    assert_modifiable(ShieldPayoutDaoInterface(self.daos[DAO_SHIELD_PAYOUT]).initialize(
        self.LST,
        self.daos[DAO_CURRENCY],
        self.daos[DAO_MARKET]
    ))

    log.DAOInitialized(msg.sender, DAO_SHIELD_PAYOUT, self.daos[DAO_SHIELD_PAYOUT])

    return True


## SETTINGS - Performed by only Governor ##


@public
def activate_public_contributions() -> bool:
    self._validate_caller(msg.sender, CALLER_GOVERNOR)
    self.public_contributions_activated = True

    return True


@public
def activate_non_standard_expiries() -> bool:
    self._validate_caller(msg.sender, CALLER_GOVERNOR)
    self.non_standard_expiries_activated = True

    return True


@public
def set_expiry_support(_timestamp: timestamp, _label: string[3], _is_active: bool) -> bool:
    """
        @dev Function to toggle support of an expiry across the system. Only the
             Governor can call this function.
        @param _timestamp The timestmap indicating the expiry.
        @param _label The 3-character label according to the prescribed expiry
             nomenclature.
        @param _is_active Bool indicating whether the expiry should be supported
             or not.
        @return A bool with a value of "True" indicating the expiry support has
             been toggled.
    """
    # validate inputs
    assert as_unitless_number(_timestamp) > 0
    self._validate_caller(msg.sender, CALLER_GOVERNOR)
    self.expiries[_timestamp] = Expiry({
        expiry_timestamp: _timestamp,
        expiry_label: _label,
        is_active: _is_active
    })
    return True


@public
def set_registry(_dao_type: int128, _registry_type: int128, _address: address) -> bool:
    """
        @dev Function to set / change the Registry address across the system.
             Only the Governor can call this function.
        @param _dao_type The type of DAO on which the change has to be made.
        @param _registry_type The type of the Registry that has to be changed.
        @param _address The address of the new Registry contract.
        @return A bool with a value of "True" indicating the registry change
            has been made on the specified DAO.
    """
    # validate inputs
    assert _dao_type in [DAO_CURRENCY, DAO_INTEREST_POOL, DAO_UNDERWRITER_POOL, DAO_MARKET, DAO_SHIELD_PAYOUT]
    assert _registry_type in [REGISTRY_POOL_NAME, REGISTRY_POSITION]
    assert _address.is_contract
    self._validate_caller(msg.sender, CALLER_GOVERNOR)

    if _dao_type == DAO_MARKET and _registry_type == REGISTRY_POSITION:
        assert_modifiable(MarketDaoInterface(self.daos[_dao_type]).set_registry(_registry_type, _address))

    log.SystemSettingsUpdated(msg.sender)

    return True


@public
def set_template(_template_type: int128, _address: address) -> bool:
    """
        @dev Function to set / change the Template address across the system.
             Only the Governor can call this function.
        @param _template_type The type of the Template that has to be changed.
        @param _address The address of the new Template contract.
        @return A bool with a value of "True" indicating the template change
            has been made across all DAOs.
    """
    # validate inputs
    assert _template_type in [TEMPLATE_TOKEN_POOL, TEMPLATE_ERC20, TEMPLATE_MFT, TEMPLATE_INTEREST_POOL, TEMPLATE_UNDERWRITER_POOL, TEMPLATE_COLLATERAL_AUCTION]
    assert _address.is_contract
    self._validate_caller(msg.sender, CALLER_GOVERNOR)
    self.templates[_template_type] = _address
    if _template_type == TEMPLATE_TOKEN_POOL or \
           _template_type == TEMPLATE_ERC20 or \
           _template_type == TEMPLATE_MFT:
        assert_modifiable(CurrencyDaoInterface(self.daos[DAO_CURRENCY]).set_template(
            _template_type, _address
        ))
    if _template_type == TEMPLATE_INTEREST_POOL:
        assert_modifiable(InterestPoolDaoInterface(self.daos[DAO_INTEREST_POOL]).set_template(
            _template_type, _address
        ))
    if _template_type == TEMPLATE_UNDERWRITER_POOL:
        assert_modifiable(UnderwriterPoolDaoInterface(self.daos[DAO_UNDERWRITER_POOL]).set_template(
            _template_type, _address
        ))
    if _template_type == TEMPLATE_COLLATERAL_AUCTION:
        assert_modifiable(MarketDaoInterface(self.daos[DAO_MARKET]).set_template(
            _template_type, _address
        ))

    log.TemplateSettingsUpdated(msg.sender, _template_type, _address)
    return True


#. Registries - Pool Name
@public
def set_pool_name_registration_minimum_stake(_value: uint256) -> bool:
    """
        @dev Function to set the minimum stake required to register a pool name
             across the system. Only the Governor can call this function.
        @param _value The minimum stake value.
        @return A bool with a value of "True" indicating the minimum stake
            has been set within the Pool Name Registry.
    """
    # validate input
    assert as_unitless_number(_value) > 0
    self._validate_caller(msg.sender, CALLER_GOVERNOR)

    assert_modifiable(PoolNameRegistryInterface(self.registries[REGISTRY_POOL_NAME]).set_name_registration_minimum_stake(_value))

    log.SystemSettingsUpdated(msg.sender)

    return True


@public
def set_pool_name_registration_stake_lookup(_name_length: int128, _value: uint256) -> bool:
    """
        @dev Function to set the stake required for a pool name with a specified
             length across the system. For eg, 3-character Pool names need a
             higher stake than 4-character, which in turn need a higher stake
             than a 5-character name, and so on. Only the Governor can call this
             function.
        @param _name_length The character length of a pool name.
        @param _value The stake required for the given pool name character length.
        @return A bool with a value of "True" indicating the minimum stake
            has been set within the Pool Name Registry.
    """
    # validate inputs
    assert _name_length > 0
    assert as_unitless_number(_value) > 0
    self._validate_caller(msg.sender, CALLER_GOVERNOR)

    assert_modifiable(PoolNameRegistryInterface(self.registries[REGISTRY_POOL_NAME]).set_name_registration_stake_lookup(_name_length, _value))

    log.SystemSettingsUpdated(msg.sender)

    return True


#. DAOS - Currency DAO
@public
def set_token_support(_token: address, _is_active: bool) -> bool:
    """
        @dev Function to toggle support of a token across the system. Only the
             Governor can call this function.
        @param _token The address of the token.
        @param _is_active Bool indicating whether the token should be supported
             or not.
        @return A bool with a value of "True" indicating the token support has
             been toggled.
    """
    # validate input
    assert _token.is_contract
    self._validate_caller(msg.sender, CALLER_GOVERNOR)

    assert_modifiable(CurrencyDaoInterface(self.daos[DAO_CURRENCY]).set_token_support(_token, _is_active))

    log.SystemSettingsUpdated(msg.sender)

    return True


#. DAOS - InterestPool DAO & UnderwriterPool DAO
@public
def set_minimum_mft_fee(_dao_type: int128, _value: uint256) -> bool:
    """
        @dev Function to set the minimum stake required to support a MFT by an
             Interest / Underwriter Pool. Only the Governor can call this
             function.
        @param _dao_type The DAO where the stake value whould be set.
        @param _value The stake value.
        @return A bool with a value of "True" indicating the stake for MFT support
            has been set within the given DAO.
    """
    # validate inputs
    assert _dao_type in [DAO_INTEREST_POOL, DAO_UNDERWRITER_POOL]
    assert as_unitless_number(_value) > 0
    self._validate_caller(msg.sender, CALLER_GOVERNOR)
    if _dao_type == DAO_INTEREST_POOL:
        assert_modifiable(InterestPoolDaoInterface(self.daos[_dao_type]).set_minimum_mft_fee(_value))
    if _dao_type == DAO_UNDERWRITER_POOL:
        assert_modifiable(UnderwriterPoolDaoInterface(self.daos[_dao_type]).set_minimum_mft_fee(_value))

    log.SystemSettingsUpdated(msg.sender)

    return True


@public
def set_fee_multiplier_per_mft_count(_dao_type: int128, _mft_count: uint256, _value: uint256) -> bool:
    """
        @dev Function to set the multiplier for every time a Pool increases the
             MFTs it supports. Only the Governor can call this function.
        @param _dao_type The DAO where the multiplier whould be set.
        @param _mft_count The number of MFTs the pool supports.
        @param _value The multplier for the MFT count of the pool.
        @return A bool with a value of "True" indicating the multiplier for MFT
             support has been set within the given DAO.
    """
    # validate inputs
    assert _dao_type in [DAO_INTEREST_POOL, DAO_UNDERWRITER_POOL]
    assert as_unitless_number(_mft_count) >= 0
    assert as_unitless_number(_value) > 0
    self._validate_caller(msg.sender, CALLER_GOVERNOR)
    if _dao_type == DAO_INTEREST_POOL:
        assert_modifiable(InterestPoolDaoInterface(self.daos[_dao_type]).set_fee_multiplier_per_mft_count(_mft_count, _value))
    if _dao_type == DAO_UNDERWRITER_POOL:
        assert_modifiable(UnderwriterPoolDaoInterface(self.daos[_dao_type]).set_fee_multiplier_per_mft_count(_mft_count, _value))

    log.SystemSettingsUpdated(msg.sender)

    return True


@public
def set_maximum_mft_support_count(_dao_type: int128, _value: uint256) -> bool:
    """
        @dev Function to set the maximum number of MFTs an Interest / Underwriter
             Pool can support. Only the Governor can call this
             function.
        @param _dao_type The DAO where the maximum value can be set.
        @param _value The maximum value.
        @return A bool with a value of "True" indicating the maxmimum number for
             MFT support has been set within the given DAO.
    """
    # validate inputs
    assert _dao_type in [DAO_INTEREST_POOL, DAO_UNDERWRITER_POOL]
    assert as_unitless_number(_value) > 0
    self._validate_caller(msg.sender, CALLER_GOVERNOR)
    if _dao_type == DAO_INTEREST_POOL:
        assert_modifiable(InterestPoolDaoInterface(self.daos[_dao_type]).set_maximum_mft_support_count(_value))
    if _dao_type == DAO_UNDERWRITER_POOL:
        assert_modifiable(UnderwriterPoolDaoInterface(self.daos[_dao_type]).set_maximum_mft_support_count(_value))

    log.SystemSettingsUpdated(msg.sender)

    return True


#. DAOS - Market DAO
@public
def set_price_oracle(_currency: address, _underlying: address, _oracle: address) -> bool:
    """
        @dev Function to set the address of the Price Oracle contract across the
             system for a given currency-underlying pair. Only the Governor can
             call this function.
        @param _currency The currency token in the currency-underlying pair.
        @param _underlying The underlying token in the currency-underlying pair.
        @param _oracle The address of the Price Oracle.
        @return A bool with a value of "True" indicating the Price Oracle address
             has been set within the Market DAO for the currency-underlying pair.
    """
    # validate inputs
    assert _currency.is_contract
    assert _underlying.is_contract
    assert _oracle.is_contract
    self._validate_caller(msg.sender, CALLER_GOVERNOR)

    assert_modifiable(MarketDaoInterface(self.daos[DAO_MARKET]).set_price_oracle(_currency, _underlying, _oracle))

    log.SystemSettingsUpdated(msg.sender)

    return True


@public
def set_maximum_liability_for_currency_market(_currency: address, _expiry: timestamp, _value: uint256) -> bool:
    """
        @dev Function to set the maximum currency liability that the system can
             accommodate until a certain expiry. Only the Governor can call this
             function.
        @param _currency The currency token.
        @param _expiry The expiry until which the maximum liability can be
             accommodated.
        @param _value The maximum liability value
        @return A bool with a value of "True" indicating the maximum currency
             liability until the given expiry has been set within the Market DAO.
    """
    # validate inputs
    assert _currency.is_contract
    assert as_unitless_number(_expiry) > 0
    assert as_unitless_number(_value) > 0
    self._validate_caller(msg.sender, CALLER_GOVERNOR)

    assert_modifiable(MarketDaoInterface(self.daos[DAO_MARKET]).set_maximum_liability_for_currency_market(_currency, _expiry, _value))

    log.SystemSettingsUpdated(msg.sender)

    return True


@public
def set_maximum_liability_for_loan_market(_currency: address, _expiry: timestamp, _underlying: address, _value: uint256) -> bool:
    """
        @dev Function to set the maximum currency liability that the system can
             accommodate until a certain expiry for a specific underlying. Only
             the Governor can call this function.
        @param _currency The currency token.
        @param _expiry The expiry until which the maximum liability can be
             accommodated.
        @param _underlying The underlying token.
        @param _value The maximum liability value
        @return A bool with a value of "True" indicating the maximum currency
             liability until the given expiry for the given underlying has been
             set within the Market DAO.
    """
    # validate inputs
    assert _currency.is_contract
    assert as_unitless_number(_expiry) > 0
    assert _underlying.is_contract
    assert as_unitless_number(_value) > 0
    self._validate_caller(msg.sender, CALLER_GOVERNOR)

    assert_modifiable(MarketDaoInterface(self.daos[DAO_MARKET]).set_maximum_liability_for_loan_market(_currency, _expiry, _underlying, _value))

    log.SystemSettingsUpdated(msg.sender)

    return True


@public
def set_auction_slippage_percentage(_value: uint256) -> bool:
    """
        @dev Function to set the slippage percentage when calculating the start
             prices in all upcoming auctions across the system. Only the
             Governor can call this function.
        @param _value The slippage percentage
        @return A bool with a value of "True" indicating the slippage percentage
             has been set within the Market DAO.
    """
    # validate input
    assert as_unitless_number(_value) > 0
    self._validate_caller(msg.sender, CALLER_GOVERNOR)

    assert_modifiable(MarketDaoInterface(self.daos[DAO_MARKET]).set_auction_slippage_percentage(_value))

    log.SystemSettingsUpdated(msg.sender)

    return True


@public
def set_auction_maximum_discount_percentage(_value: uint256) -> bool:
    """
        @dev Function to set the maximum discount percentage when calculating
             the final discounted prices in all upcoming auctions across the
             system. Only the Governor can call this function.
        @param _value The maximum discount percentage
        @return A bool with a value of "True" indicating the maximum discount
             percentage has been set within the Market DAO.
    """
    # validate input
    assert as_unitless_number(_value) > 0
    self._validate_caller(msg.sender, CALLER_GOVERNOR)

    assert_modifiable(MarketDaoInterface(self.daos[DAO_MARKET]).set_auction_maximum_discount_percentage(_value))

    log.SystemSettingsUpdated(msg.sender)

    return True


@public
def set_auction_discount_duration(_value: timedelta) -> bool:
    """
        @dev Function to set the duration in seconds when the underlying is
             sold at a discount in all upcoming auctions across the
             system. Only the Governor can call this function.
        @param _value The duration in seconds
        @return A bool with a value of "True" indicating the discount duration
             has been set within the Market DAO.
    """
    # validate input
    assert as_unitless_number(_value) > 0
    self._validate_caller(msg.sender, CALLER_GOVERNOR)

    assert_modifiable(MarketDaoInterface(self.daos[DAO_MARKET]).set_auction_discount_duration(_value))

    log.SystemSettingsUpdated(msg.sender)

    return True


## ESCAPE HATCHES - Performed by only Escape Hatch Manager ##

# DAOS - Pause / Unpause
@public
def toggle_dao_pause(_dao_type: int128, _pause: bool) -> bool:
    """
        @dev Escape hatch function to pause / unpause a given DAO. Only the
             Escape Hatch Manager can call this function.
        @param _dao_type The DAO on which the pause has to be toggled.
        @param _pause The toggle option
        @return A bool with a value of "True" indicating the given DAO has been
             paused / unpaused.
    """
    self._validate_caller(msg.sender, CALLER_ESCAPE_HATCH_MANAGER)
    if _dao_type == DAO_CURRENCY:
        if _pause:
            assert_modifiable(CurrencyDaoInterface(self.daos[_dao_type]).pause())
        else:
            assert_modifiable(CurrencyDaoInterface(self.daos[_dao_type]).unpause())
        return True
    if _dao_type == DAO_INTEREST_POOL:
        if _pause:
            assert_modifiable(InterestPoolDaoInterface(self.daos[_dao_type]).pause())
        else:
            assert_modifiable(InterestPoolDaoInterface(self.daos[_dao_type]).unpause())
        return True
    if _dao_type == DAO_UNDERWRITER_POOL:
        if _pause:
            assert_modifiable(UnderwriterPoolDaoInterface(self.daos[_dao_type]).pause())
        else:
            assert_modifiable(UnderwriterPoolDaoInterface(self.daos[_dao_type]).unpause())
        return True
    if _dao_type == DAO_MARKET:
        if _pause:
            assert_modifiable(MarketDaoInterface(self.daos[_dao_type]).pause())
        else:
            assert_modifiable(MarketDaoInterface(self.daos[_dao_type]).unpause())
        return True
    if _dao_type == DAO_SHIELD_PAYOUT:
        if _pause:
            assert_modifiable(ShieldPayoutDaoInterface(self.daos[_dao_type]).pause())
        else:
            assert_modifiable(ShieldPayoutDaoInterface(self.daos[_dao_type]).unpause())
        return True

    raise("Invalid dao type")

# Registries - Pause / Unpause
@public
def toggle_registry_pause(_registry_type: int128, _pause: bool) -> bool:
    """
        @dev Escape hatch function to pause / unpause a given Registry. Only the
             Escape Hatch Manager can call this function.
        @param _registry_type The Registry on which the pause has to be toggled.
        @param _pause The toggle option
        @return A bool with a value of "True" indicating the given Registry has
             been paused / unpaused.
    """
    self._validate_caller(msg.sender, CALLER_ESCAPE_HATCH_MANAGER)

    if _registry_type == REGISTRY_POOL_NAME:
        if _pause:
            assert_modifiable(PoolNameRegistryInterface(self.registries[_registry_type]).pause())
        else:
            assert_modifiable(PoolNameRegistryInterface(self.registries[_registry_type]).unpause())
        return True
    if _registry_type == REGISTRY_POSITION:
        if _pause:
            assert_modifiable(PositionRegistryInterface(self.registries[_registry_type]).pause())
        else:
            assert_modifiable(PositionRegistryInterface(self.registries[_registry_type]).unpause())
        return True

    raise("Invalid registry type")

# DAOS - Escape hatch ERC20
@public
def escape_hatch_dao_erc20(_dao_type: int128, _currency: address, _is_l: bool) -> bool:
    """
        @dev Escape hatch function to transfer all tokens of an ERC20 address
             from the given DAO to the Escape Hatch Token Holder. Only the
             Escape Hatch Manager can call this function.
        @param _dao_type The DAO from which the ERC20 transfer will be made.
        @param _currency The address of the ERC20 token
        @param _is_l A bool indicating if the ERC20 token is an L Token
        @return A bool with a value of "True" indicating the ERC20 transfer has
             been made from the given DAO.
    """
    self._validate_caller(msg.sender, CALLER_ESCAPE_HATCH_MANAGER)
    if _dao_type == DAO_CURRENCY:
        assert_modifiable(CurrencyDaoInterface(self.daos[_dao_type]).escape_hatch_erc20(_currency, _is_l))
        return True
    if _dao_type == DAO_INTEREST_POOL:
        assert_modifiable(InterestPoolDaoInterface(self.daos[_dao_type]).escape_hatch_erc20(_currency, _is_l))
        return True
    if _dao_type == DAO_UNDERWRITER_POOL:
        assert_modifiable(UnderwriterPoolDaoInterface(self.daos[_dao_type]).escape_hatch_erc20(_currency, _is_l))
        return True
    if _dao_type == DAO_MARKET:
        assert_modifiable(MarketDaoInterface(self.daos[_dao_type]).escape_hatch_erc20(_currency, _is_l))
        return True
    if _dao_type == DAO_SHIELD_PAYOUT:
        assert_modifiable(ShieldPayoutDaoInterface(self.daos[_dao_type]).escape_hatch_erc20(_currency, _is_l))
        return True

    raise("Invalid dao type")


# Registries - Escape hatch ERC20
@public
def escape_hatch_registry_erc20(_registry_type: int128, _currency: address) -> bool:
    """
        @dev Escape hatch function to transfer all tokens of an ERC20 address
             from the given Registry to the Escape Hatch Token Holder. Only the
             Escape Hatch Manager can call this function.
        @param _registry_type The Registry from which the ERC20 transfer will be made.
        @param _currency The address of the ERC20 token
        @return A bool with a value of "True" indicating the ERC20 transfer has
             been made from the given Registry.
    """
    self._validate_caller(msg.sender, CALLER_ESCAPE_HATCH_MANAGER)
    if _registry_type == REGISTRY_POOL_NAME:
        assert_modifiable(PoolNameRegistryInterface(self.registries[_registry_type]).escape_hatch_erc20(_currency))
        return True

    raise("Invalid registry type")


# DAOS - Escape hatch MFT
@public
def escape_hatch_dao_mft(_dao_type: int128, _mft_type: int128, _currency: address, _expiry: timestamp, _underlying: address, _strike_price: uint256) -> bool:
    """
        @dev Escape hatch function to transfer all tokens of a MFT with given
             parameters from the given DAO to the Escape Hatch Token Holder.
             Only the Escape Hatch Manager can call this function.
        @param _dao_type The DAO from which the ERC20 transfer will be made.
        @param _mft_type The MFT type (L, I, S, or U) from which the MFT address
             could be deduced.
        @param _currency The address of the currency token in the MFT.
        @param _expiry The timestamp when the MFT expires.
        @param _underlying The address of the underlying token in the MFT.
        @param _strike_price The price of the underlying per currency at _expiry.
        @return A bool with a value of "True" indicating the MFT transfer has
             been made from the given DAO.
    """
    self._validate_caller(msg.sender, CALLER_ESCAPE_HATCH_MANAGER)
    assert _mft_type == MFT_TYPE_F or _mft_type == MFT_TYPE_I or \
           _mft_type == MFT_TYPE_S or _mft_type == MFT_TYPE_U

    if _dao_type == DAO_CURRENCY:
        assert_modifiable(CurrencyDaoInterface(self.daos[_dao_type]).escape_hatch_mft(_mft_type, _currency, _expiry, _underlying, _strike_price))
        return True
    if _dao_type == DAO_INTEREST_POOL:
        assert_modifiable(InterestPoolDaoInterface(self.daos[_dao_type]).escape_hatch_mft(_mft_type, _currency, _expiry, _underlying, _strike_price))
        return True
    if _dao_type == DAO_UNDERWRITER_POOL:
        assert_modifiable(UnderwriterPoolDaoInterface(self.daos[_dao_type]).escape_hatch_mft(_mft_type, _currency, _expiry, _underlying, _strike_price))
        return True
    if _dao_type == DAO_MARKET:
        assert_modifiable(MarketDaoInterface(self.daos[_dao_type]).escape_hatch_mft(_mft_type, _currency, _expiry, _underlying, _strike_price))
        return True
    if _dao_type == DAO_SHIELD_PAYOUT:
        assert_modifiable(ShieldPayoutDaoInterface(self.daos[_dao_type]).escape_hatch_mft(_mft_type, _currency, _expiry, _underlying, _strike_price))
        return True

    raise("Invalid dao type")


# Market DAO - Escape hatch Auction
@public
def escape_hatch_auction(_currency: address, _expiry: timestamp, _underlying: address) -> bool:
    """
        @dev Escape hatch function to transfer all tokens of the underlying MFT
             type F from the auction contract for the given loan market
             indicators, to the Escape Hatch Token Holder.
             Only the Escape Hatch Manager can call this function.
        @param _currency The currency token in the loan market.
        @param _expiry The timstamp of loan market expiry.
        @param _underlying TThe underlying token in the loan market.
        @return A bool with a value of "True" indicating the MFT transfer has
             been made from the corresponding auction contract.
    """
    self._validate_caller(msg.sender, CALLER_ESCAPE_HATCH_MANAGER)

    assert_modifiable(MarketDaoInterface(self.daos[DAO_MARKET]).escape_hatch_auction(_currency, _expiry, _underlying))
    return True
