# Vyper version of the Lendroid protocol v2
# THIS CONTRACT HAS NOT BEEN AUDITED!


owner: public(address)
CURRENCY_ADDRESS: public(address)
UNDERLYING_ADDRESS: public(address)
EXPIRY: public(timestamp)
STRIKE_PRICE: public(uint256)
PRICE_AT_EXPIRY: public(uint256)
SHIELD_PAYOUT_VALUE: public(uint256)
UNDERWRITER_PAYOUT_VALUE: public(uint256)


@public
def initialize(_currency_address: address, _underlying_address: address,
    _expiry: timestamp, _strike_price: uint256) -> bool:
    self.owner = msg.sender
    self.CURRENCY_ADDRESS = _currency_address
    self.UNDERLYING_ADDRESS = _underlying_address
    self.EXPIRY = _expiry
    self.STRIKE_PRICE = _strike_price

    return True


@public
def set_price_at_expiry(_price: uint256) -> bool:
    assert msg.sender == self.owner
    assert self.EXPIRY > block.timestamp
    assert self.PRICE_AT_EXPIRY == 0
    self.PRICE_AT_EXPIRY = _price
    if self.PRICE_AT_EXPIRY >= self.STRIKE_PRICE:
        self.SHIELD_PAYOUT_VALUE = 0
    else:
        self.SHIELD_PAYOUT_VALUE = as_unitless_number(self.STRIKE_PRICE) - as_unitless_number(self.PRICE_AT_EXPIRY)
    self.UNDERWRITER_PAYOUT_VALUE = as_unitless_number(self.STRIKE_PRICE) - as_unitless_number(self.SHIELD_PAYOUT_VALUE)

    return True
