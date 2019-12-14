# Functions

@public
def start(_currency: address, _expiry: uint256(sec, positional), _underlying: address, _f_underlying: address, _f_id_underlying: uint256, _expiry_price: uint256, _currency_value: uint256, _underlying_value: uint256) -> bool:
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
def current_price() -> uint256:
    pass

@public
def escape_hatch_underlying_f() -> bool:
    pass

@public
def purchase(_underlying_value: uint256) -> bool:
    pass

@public
def purchase_for_remaining_currency() -> bool:
    pass

@public
def purchase_remaining_underlying() -> bool:
    pass

@constant
@public
def owner() -> address:
    pass

@constant
@public
def currency() -> address:
    pass

@constant
@public
def underlying() -> address:
    pass

@constant
@public
def f_underlying() -> address:
    pass

@constant
@public
def f_id_underlying() -> uint256:
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
def currency_remaining() -> uint256:
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
