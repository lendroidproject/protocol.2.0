# Vyper version of the Lendroid protocol v2
# THIS CONTRACT HAS NOT BEEN AUDITED!


from contracts.interfaces import ERC20


owner: public(address)
currency_address: public(address)
underlying_address: public(address)
market_expiry: public(timestamp)
strike_price: public(uint256)
price_at_expiry: public(uint256)
max_supply: public(uint256)
starting_price: public(uint256)
is_active: public(bool)

SLIPPAGE: public(uint256)
AUCTION_DURATION: public(timedelta)


@public
def initialize(
            _currency_address: address, _underlying_address: address,
            _market_expiry: timestamp, _strike_price: uint256
        ) -> bool:
    # verify inputs
    assert msg.sender.is_contract
    assert _currency_address.is_contract
    assert _underlying_address.is_contract
    assert as_unitless_number(_market_expiry) > 0
    assert as_unitless_number(_strike_price) > 0
    # set parameters
    self.owner = msg.sender
    self.currency_address = _currency_address
    self.underlying_address = _underlying_address
    self.market_expiry = _market_expiry
    self.strike_price = _strike_price
    self.is_active = False
    self.SLIPPAGE = 104
    self.AUCTION_DURATION = 30 * 60

    return True


@private
@constant
def _auction_expiry() -> timestamp:
    return self.market_expiry + self.AUCTION_DURATION


@private
@constant
def _lot() -> uint256:
    return ERC20(self.underlying_address).balanceOf(self)


@private
@constant
def _slope() -> uint256:
    if self.is_active:
        _price_difference: uint256 = as_unitless_number(self.price_at_expiry) - as_unitless_number(self.strike_price)
        return (as_unitless_number(self.starting_price) * as_unitless_number(_price_difference)) / (as_unitless_number(self._auction_expiry()) * self.strike_price)
    else:
        return 0


@public
@constant
def auction_expiry() -> timestamp:
    return self._auction_expiry()


@public
@constant
def lot() -> uint256:
    return self._lot()


@public
@constant
def slope() -> uint256:
    return self._slope()


@public
@constant
def current_price() -> uint256:
    # verify auction has not expired
    if self.is_active:
        return as_unitless_number(block.timestamp) * as_unitless_number(self._slope()) + as_unitless_number(self.starting_price)
    else:
        return 0


@public
def activate(_price_at_expiry: uint256, _currency_value: uint256, _underlying_value: uint256) -> bool:
    assert msg.sender == self.owner
    assert self.market_expiry > block.timestamp
    assert self.price_at_expiry == 0
    assert not self.is_active
    self.price_at_expiry = _price_at_expiry
    self.max_supply = _underlying_value
    # set starting_price
    assert as_unitless_number(_underlying_value) > 0
    self.starting_price = (as_unitless_number(_currency_value) * as_unitless_number(self.SLIPPAGE)) / (as_unitless_number(_underlying_value) * 100)
    self.is_active = True

    return True


@public
def transfer_underlying(_to: address, _value: uint256) -> bool:
    assert self.is_active
    assert msg.sender == self.owner
    assert as_unitless_number(_value) <= as_unitless_number(self._lot())
    # deactivate if auction has expired or all underlying currency has been auctioned
    if (as_unitless_number(self._lot()) - as_unitless_number(_value) == 0) or (block.timestamp >= self._auction_expiry()):
        self.is_active = False
    assert_modifiable(ERC20(self.underlying_address).transfer(_to, _value))

    return True
