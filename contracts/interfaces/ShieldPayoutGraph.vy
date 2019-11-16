# Functions

@public
def initialize(_currency_address: address, _underlying_address: address, _expiry: uint256(sec, positional), _strike_price: uint256) -> bool:
    pass

@public
def set_price_at_expiry(_price: uint256) -> bool:
    pass

@constant
@public
def owner() -> address:
    pass

@constant
@public
def CURRENCY_ADDRESS() -> address:
    pass

@constant
@public
def UNDERLYING_ADDRESS() -> address:
    pass

@constant
@public
def EXPIRY() -> uint256(sec, positional):
    pass

@constant
@public
def STRIKE_PRICE() -> uint256:
    pass

@constant
@public
def PRICE_AT_EXPIRY() -> uint256:
    pass

@constant
@public
def SHIELD_PAYOUT_VALUE() -> uint256:
    pass

@constant
@public
def UNDERWRITER_PAYOUT_VALUE() -> uint256:
    pass
