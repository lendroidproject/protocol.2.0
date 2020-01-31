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
