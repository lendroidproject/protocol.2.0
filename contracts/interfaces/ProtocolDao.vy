# Events

DAOInitialized: event({_setter: address, _dao_type: uint256, _dao_address: address})
TemplateSettingsUpdated: event({_setter: address, _template_type: uint256, _template_address: address})

# Functions

@public
def set_expiry_support(_timestamp: uint256(sec, positional), _label: string[3], _is_active: bool) -> bool:
    pass

@public
def set_template(_template_type: uint256, _address: address) -> bool:
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
def DAO_TYPE_CURRENCY() -> uint256:
    pass

@constant
@public
def DAO_TYPE_INTEREST_POOL() -> uint256:
    pass

@constant
@public
def DAO_TYPE_UNDERWRITER_POOL() -> uint256:
    pass

@constant
@public
def DAO_TYPE_MARKET() -> uint256:
    pass

@constant
@public
def TEMPLATE_TYPE_ERC20() -> uint256:
    pass

@constant
@public
def TEMPLATE_TYPE_MFT() -> uint256:
    pass

@constant
@public
def TEMPLATE_TYPE_TOKEN_POOL() -> uint256:
    pass

@constant
@public
def TEMPLATE_TYPE_INTEREST_POOL() -> uint256:
    pass

@constant
@public
def TEMPLATE_TYPE_UNDERWRITER_POOL() -> uint256:
    pass

@constant
@public
def initialized() -> bool:
    pass
