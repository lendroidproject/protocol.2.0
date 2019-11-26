# Functions

@public
def initialize(_currency_address: address, _underlying_address: address, _expiry: uint256(sec, positional), _dao_address_market: address) -> bool:
    pass

@constant
@public
def auction_expiry() -> uint256(sec, positional):
    pass

@constant
@public
def lot() -> uint256:
    pass

@constant
@public
def slope() -> uint256:
    pass

@constant
@public
def current_price() -> uint256:
    pass

@public
def start(_price_of_underlying_per_currency_at_expiry: uint256, _currency_value: uint256, _underlying_value: uint256) -> bool:
    pass

@public
def purchase(_to: address, _underlying_value: uint256) -> bool:
    pass

@constant
@public
def owner() -> address:
    pass

@constant
@public
def currency_address() -> address:
    pass

@constant
@public
def underlying_address() -> address:
    pass

@constant
@public
def expiry() -> uint256(sec, positional):
    pass

@constant
@public
def max_supply() -> uint256:
    pass

@constant
@public
def currency_value_remaining() -> uint256:
    pass

@constant
@public
def start_price() -> uint256:
    pass

@constant
@public
def end_price() -> uint256:
    pass

@constant
@public
def is_active() -> bool:
    pass

@constant
@public
def daos(arg0: uint256) -> address:
    pass

@constant
@public
def DAO_TYPE_MARKET() -> uint256:
    pass

@constant
@public
def SLIPPAGE_PERCENTAGE() -> uint256:
    pass

@constant
@public
def MAXIMUM_DISCOUNT_PERCENTAGE() -> uint256:
    pass

@constant
@public
def AUCTION_DURATION() -> uint256(sec):
    pass
