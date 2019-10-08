# Functions

@public
def set_expiry_support(_timestamp: uint256(sec, positional), _label: string[3], _is_active: bool) -> bool:
    pass

@public
def set_template(_label: string[64], _address: address) -> bool:
    pass

@constant
@public
def protocol_currency_address() -> address:
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
def templates(arg0: string[64]) -> address:
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
def DAO_TYPE_LOAN() -> uint256:
    pass
