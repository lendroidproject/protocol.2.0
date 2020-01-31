# @version 0.1.0b14
# @notice Implementation of Lendroid v2 - Simple Price Oracle
# @dev THIS CONTRACT HAS NOT BEEN AUDITED
# @author Vignesh (Vii) Meenakshi Sundaram (@vignesh-msundaram)
# Lendroid Foundation


from ...interfaces import SimplePriceOracleInterface

implements: SimplePriceOracleInterface


contract Feed:
    def read() -> bytes32: constant


owner: public(address)
currency: public(address)
underlying: public(address)
feed_address: public(address)
current_price: public(uint256)


@public
def __init__(_currency: address, _underlying: address, _feed_address: address):
    # verify inputs
    assert _currency.is_contract
    assert _underlying.is_contract
    assert _feed_address.is_contract
    # set parameters
    self.owner = msg.sender
    self.currency = _currency
    self.underlying = _underlying
    self.feed_address = _feed_address


@public
def get_price() -> uint256:
    _raw_value: bytes32 = Feed(self.feed_address).read()
    self.current_price = convert(_raw_value, uint256)
    return self.current_price
