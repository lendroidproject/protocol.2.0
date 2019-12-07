# Vyper version of the Lendroid protocol v2
# THIS CONTRACT HAS NOT BEEN AUDITED!


from contracts.interfaces import CurrencyDao
from contracts.interfaces import InterestPoolDao
from contracts.interfaces import UnderwriterPoolDao
from contracts.interfaces import MarketDao


# Structs

struct Expiry:
    expiry_timestamp: timestamp
    expiry_label: string[3]
    is_active: bool


# Events
DAOInitialized: event({_setter: indexed(address), _dao_type: indexed(uint256), _dao_address: address})
TemplateSettingsUpdated: event({_setter: indexed(address), _template_type: indexed(uint256), _template_address: address})

# Variables of the protocol.
LST: public(address)
owner: public(address)
# dao_type => dao_address
daos: public(map(uint256, address))
# timestamp => Expiry
expiries: public(map(timestamp, Expiry))
# template_name => template_contract_address
templates: public(map(uint256, address))

DAO_TYPE_CURRENCY: public(uint256)
DAO_TYPE_INTEREST_POOL: public(uint256)
DAO_TYPE_UNDERWRITER_POOL: public(uint256)
DAO_TYPE_MARKET: public(uint256)

TEMPLATE_TYPE_ERC20: public(uint256)
TEMPLATE_TYPE_MFT: public(uint256)
TEMPLATE_TYPE_TOKEN_POOL: public(uint256)
TEMPLATE_TYPE_INTEREST_POOL: public(uint256)
TEMPLATE_TYPE_UNDERWRITER_POOL: public(uint256)

initialized: public(bool)


@public
def __init__(
        _LST: address,
        _dao_currency: address,
        _template_token_pool: address,
        _dao_interest_pool: address,
        _template_interest_pool: address,
        _dao_underwriter_pool: address,
        _template_underwriter_pool: address,
        _dao_market: address,
        _template_erc20: address,
        _template_mft: address,
    ):
    # Before init, need to deploy the following template contracts:
    #. PoolNameRegistryTemplate
    #. CurrencyDao
    #. ERC20TokenPoolTemplate
    #. InterestPoolDao
    #. InterestPoolTemplate
    #. UnderwriterPoolDao
    #. UnderwriterPoolTemplate
    #. MarketDao
    #. PositionRegistryTemplate
    #. SimplePriceOracleTemplate
    #. SimpleCollateralAuctionCurveTemplate
    #. ShieldPayoutDao
    #. ERC20Template
    #. MultiFungibleTokenTemplate

    self.initialized = True
    self.owner = msg.sender
    self.LST = _LST

    self.DAO_TYPE_CURRENCY = 1
    self.DAO_TYPE_INTEREST_POOL = 2
    self.DAO_TYPE_UNDERWRITER_POOL = 3
    self.DAO_TYPE_MARKET = 4

    self.TEMPLATE_TYPE_ERC20 = 1
    self.TEMPLATE_TYPE_MFT = 2
    self.TEMPLATE_TYPE_TOKEN_POOL = 3
    self.TEMPLATE_TYPE_INTEREST_POOL = 4
    self.TEMPLATE_TYPE_UNDERWRITER_POOL = 5

    # set dao addresses
    assert _dao_currency.is_contract
    self.daos[self.DAO_TYPE_CURRENCY] = _dao_currency

    assert _dao_interest_pool.is_contract
    self.daos[self.DAO_TYPE_INTEREST_POOL] = _dao_interest_pool

    assert _dao_underwriter_pool.is_contract
    self.daos[self.DAO_TYPE_UNDERWRITER_POOL] = _dao_underwriter_pool

    assert _dao_market.is_contract
    self.daos[self.DAO_TYPE_MARKET] = _dao_market

    # set template addresses
    assert _template_erc20.is_contract
    self.templates[self.TEMPLATE_TYPE_ERC20] = _template_erc20

    assert _template_mft.is_contract
    self.templates[self.TEMPLATE_TYPE_MFT] = _template_mft

    assert _template_token_pool.is_contract
    self.templates[self.TEMPLATE_TYPE_TOKEN_POOL] = _template_token_pool

    assert _template_interest_pool.is_contract
    self.templates[self.TEMPLATE_TYPE_INTEREST_POOL] = _template_interest_pool

    assert _template_underwriter_pool.is_contract
    self.templates[self.TEMPLATE_TYPE_UNDERWRITER_POOL] = _template_underwriter_pool


@private
@constant
def _is_initialized() -> bool:
    return self.initialized == True


# Admin functions

# @public
# def initialize_currency_dao() -> bool:
#     assert self._is_initialized()
#     assert msg.sender == self.owner
#     # initialize currency dao
#     assert_modifiable(CurrencyDao(self.daos[self.DAO_TYPE_CURRENCY]).initialize(
#         self.owner, self.LST,
#         self.templates[self.TEMPLATE_TYPE_TOKEN_POOL],
#         self.templates[self.TEMPLATE_TYPE_ERC20],
#         self.templates[self.TEMPLATE_TYPE_MFT]
#     ))
#
#     log.DAOInitialized(msg.sender, self.DAO_TYPE_CURRENCY, self.daos[self.DAO_TYPE_CURRENCY])
#
#     return True


# @public
# def initialize_interest_pool_dao() -> bool:
#     assert self._is_initialized()
#     assert msg.sender == self.owner
#     # initialize interest pool dao
#     assert_modifiable(InterestPoolDao(self.daos[self.DAO_TYPE_INTEREST_POOL]).initialize(
#         self.owner, self.LST,
#         self.daos[self.DAO_TYPE_CURRENCY],
#         self.templates[self.TEMPLATE_TYPE_INTEREST_POOL],
#         self.templates[self.TEMPLATE_TYPE_ERC20]
#     ))
#
#     log.DAOInitialized(msg.sender, self.DAO_TYPE_INTEREST_POOL, self.daos[self.DAO_TYPE_INTEREST_POOL])
#
#     return True


# @public
# def initialize_underwriter_pool_dao() -> bool:
#     assert self._is_initialized()
#     assert msg.sender == self.owner
#     # initialize underwriter pool dao
#     assert_modifiable(UnderwriterPoolDao(self.daos[self.DAO_TYPE_UNDERWRITER_POOL]).initialize(
#         self.owner, self.LST,
#         self.daos[self.DAO_TYPE_CURRENCY],
#         self.templates[self.TEMPLATE_TYPE_UNDERWRITER_POOL],
#         self.templates[self.TEMPLATE_TYPE_ERC20]
#     ))
#
#     log.DAOInitialized(msg.sender, self.DAO_TYPE_UNDERWRITER_POOL, self.daos[self.DAO_TYPE_UNDERWRITER_POOL])
#
#     return True


# @public
# def initialize_loan_dao() -> bool:
#     assert self._is_initialized()
#     assert msg.sender == self.owner
#     # initialize loan dao
#     assert_modifiable(MarketDao(self.daos[self.DAO_TYPE_MARKET]).initialize(
#         self.owner, self.LST,
#         self.daos[self.DAO_TYPE_CURRENCY],
#         self.daos[self.DAO_TYPE_INTEREST_POOL],
#         self.daos[self.DAO_TYPE_UNDERWRITER_POOL]
#     ))
#
#     log.DAOInitialized(msg.sender, self.DAO_TYPE_MARKET, self.daos[self.DAO_TYPE_MARKET])
#
#     return True


@public
def set_expiry_support(_timestamp: timestamp, _label: string[3], _is_active: bool) -> bool:
    assert self._is_initialized()
    assert msg.sender == self.owner
    self.expiries[_timestamp] = Expiry({
        expiry_timestamp: _timestamp,
        expiry_label: _label,
        is_active: _is_active
    })
    return True


@public
def set_template(_template_type: uint256, _address: address) -> bool:
    assert self._is_initialized()
    assert msg.sender == self.owner
    assert _template_type == self.TEMPLATE_TYPE_ERC20 or \
           _template_type == self.TEMPLATE_TYPE_MFT or \
           _template_type == self.TEMPLATE_TYPE_TOKEN_POOL or \
           _template_type == self.TEMPLATE_TYPE_INTEREST_POOL or \
           _template_type == self.TEMPLATE_TYPE_UNDERWRITER_POOL
    self.templates[_template_type] = _address
    log.TemplateSettingsUpdated(msg.sender, _template_type, _address)
    return True
