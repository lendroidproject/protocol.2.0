# Functions

@constant
@public
def borrowable_amount() -> uint256:
    pass

@public
def initialize(_currency_address: address) -> bool:
    pass

@constant
@public
def liquidity() -> uint256:
    pass

@public
def destroy() -> bool:
    pass

@public
def update_total_supplied(_amount: uint256) -> bool:
    pass

@public
def release_currency(_to: address, _amount: uint256) -> bool:
    pass

@constant
@public
def owner() -> address:
    pass

@constant
@public
def total_supplied() -> uint256:
    pass

@constant
@public
def total_borrowed() -> uint256:
    pass

@constant
@public
def CURRENCY_ADDRESS() -> address:
    pass
