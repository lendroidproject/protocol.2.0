# Events

DAOInitialized: event({_setter: address, _dao_type: uint256, _dao_address: address})
RegistryInitialized: event({_setter: address, _template_type: uint256, _registry_address: address})
TemplateSettingsUpdated: event({_setter: address, _template_type: uint256, _template_address: address})
SystemSettingsUpdated: event({_setter: address})

# Functions

@public
def initialize_pool_name_registry() -> bool:
    pass

@public
def set_pool_name_registration_minimum_stake(_value: uint256) -> bool:
    pass

@public
def set_pool_name_registration_stake_lookup(_name_length: int128, _value: uint256) -> bool:
    pass

@public
def initialize_position_registry() -> bool:
    pass

@public
def initialize_currency_dao() -> bool:
    pass

@public
def initialize_interest_pool_dao() -> bool:
    pass

@public
def initialize_underwriter_pool_dao() -> bool:
    pass

@public
def initialize_market_dao() -> bool:
    pass

@public
def initialize_shield_payout_dao() -> bool:
    pass

@public
def set_expiry_support(_timestamp: uint256(sec, positional), _label: string[3], _is_active: bool) -> bool:
    pass

@public
def set_template(_template_type: uint256, _address: address) -> bool:
    pass

@public
def pause_dao_currency() -> bool:
    pass

@public
def pause_dao_interest_pool() -> bool:
    pass

@public
def pause_dao_underwriter_pool() -> bool:
    pass

@public
def pause_dao_market() -> bool:
    pass

@public
def pause_dao_shield_payout() -> bool:
    pass

@public
def pause_registry_pool_name() -> bool:
    pass

@public
def pause_registry_position() -> bool:
    pass

@constant
@public
def LST() -> address:
    pass

@constant
@public
def owner() -> address:
    pass

@constant
@public
def daos(arg0: uint256) -> address:
    pass

@constant
@public
def registries(arg0: uint256) -> address:
    pass

@constant
@public
def expiries__expiry_timestamp(arg0: uint256(sec, positional)) -> uint256(sec, positional):
    pass

@constant
@public
def expiries__expiry_label(arg0: uint256(sec, positional)) -> string[3]:
    pass

@constant
@public
def expiries__is_active(arg0: uint256(sec, positional)) -> bool:
    pass

@constant
@public
def templates(arg0: uint256) -> address:
    pass

@constant
@public
def DAO_CURRENCY() -> uint256:
    pass

@constant
@public
def DAO_INTEREST_POOL() -> uint256:
    pass

@constant
@public
def DAO_UNDERWRITER_POOL() -> uint256:
    pass

@constant
@public
def DAO_MARKET() -> uint256:
    pass

@constant
@public
def DAO_SHIELD_PAYOUT() -> uint256:
    pass

@constant
@public
def REGISTRY_POOL_NAME() -> uint256:
    pass

@constant
@public
def REGISTRY_POSITION() -> uint256:
    pass

@constant
@public
def TEMPLATE_TOKEN_POOL() -> uint256:
    pass

@constant
@public
def TEMPLATE_INTEREST_POOL() -> uint256:
    pass

@constant
@public
def TEMPLATE_UNDERWRITER_POOL() -> uint256:
    pass

@constant
@public
def TEMPLATE_PRICE_ORACLE() -> uint256:
    pass

@constant
@public
def TEMPLATE_COLLATERAL_AUCTION() -> uint256:
    pass

@constant
@public
def TEMPLATE_ERC20() -> uint256:
    pass

@constant
@public
def TEMPLATE_MFT() -> uint256:
    pass

@constant
@public
def initialized() -> bool:
    pass

@constant
@public
def pool_name_registration_minimum_stake() -> uint256:
    pass
