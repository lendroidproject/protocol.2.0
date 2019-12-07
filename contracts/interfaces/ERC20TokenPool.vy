# Functions

@constant
@public
def borrowable_amount() -> uint256:
    pass

@public
def initialize(_token: address) -> bool:
    pass

@public
def release(_to: address, _value: uint256) -> bool:
    pass

@public
def destroy() -> bool:
    pass

@constant
@public
def owner() -> address:
    pass

@constant
@public
def token() -> address:
    pass
