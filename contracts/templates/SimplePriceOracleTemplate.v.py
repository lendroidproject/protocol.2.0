# Vyper version of the Lendroid protocol v2
# THIS CONTRACT HAS NOT BEEN AUDITED!


from contracts.interfaces import SimplePriceOracle

implements: SimplePriceOracle


contract Feed:
    def read() -> bytes32: constant


owner: public(address)
currency_address: public(address)
underlying_address: public(address)
feed_address: public(address)
current_price: public(uint256)


@public
def __init__(
            _currency_address: address, _underlying_address: address,
            _feed_address: address
        ):
    # verify inputs
    assert _currency_address.is_contract
    assert _underlying_address.is_contract
    # set parameters
    self.owner = msg.sender
    self.currency_address = _currency_address
    self.underlying_address = _underlying_address
    self.feed_address = _feed_address


@public
def get_price() -> uint256:
    _raw_value: bytes32 = Feed(self.feed_address).read()
    self.current_price = convert(_raw_value, uint256)
    return self.current_price
