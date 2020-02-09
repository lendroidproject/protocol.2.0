# @version 0.1.0b16
# @notice Implementation of Price Feed used by the SimplePriceOracleTemplate
# @dev THIS CONTRACT IS USED ONLY FOR TESTING
# @author Vignesh (Vii) Meenakshi Sundaram (@vignesh-msundaram)
# Lendroid Foundation


owner: public(address)
current_price: public(uint256)


@public
def __init__():
    # set parameters
    self.owner = msg.sender


@public
def set_price(_value: uint256) -> bool:
    assert msg.sender == self.owner
    assert as_unitless_number(_value) > 0
    self.current_price = _value

    return True


@public
def read() -> uint256:
    return self.current_price
