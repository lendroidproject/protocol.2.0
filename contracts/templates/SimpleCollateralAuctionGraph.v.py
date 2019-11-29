# Vyper version of the Lendroid protocol v2
# THIS CONTRACT HAS NOT BEEN AUDITED!


from contracts.interfaces import ERC20
from contracts.interfaces import MarketDao


owner: public(address)
currency_address: public(address)
underlying_address: public(address)
expiry: public(timestamp)
max_supply: public(uint256)
currency_value_remaining: public(uint256)
start_price: public(uint256)
end_price: public(uint256)
is_active: public(bool)

# dao_type => dao_address
daos: public(map(uint256, address))

DAO_TYPE_MARKET: public(uint256)

SLIPPAGE_PERCENTAGE: public(uint256)
MAXIMUM_DISCOUNT_PERCENTAGE: public(uint256)
AUCTION_DURATION: public(timedelta)


@public
def initialize(
            _currency_address: address, _underlying_address: address,
            _expiry: timestamp,
            _dao_address_market: address
        ) -> bool:
    # verify inputs
    assert msg.sender.is_contract
    assert _currency_address.is_contract
    assert _underlying_address.is_contract
    assert as_unitless_number(_expiry) > 0
    # set parameters
    self.owner = msg.sender
    self.currency_address = _currency_address
    self.underlying_address = _underlying_address
    self.expiry = _expiry
    self.is_active = False
    self.SLIPPAGE_PERCENTAGE = 104
    self.MAXIMUM_DISCOUNT_PERCENTAGE = 40
    self.AUCTION_DURATION = 30 * 60

    self.DAO_TYPE_MARKET = 1
    self.daos[self.DAO_TYPE_MARKET] = _dao_address_market

    return True


@private
@constant
def _auction_expiry() -> timestamp:
    return self.expiry + self.AUCTION_DURATION


@private
@constant
def _lot() -> uint256:
    return ERC20(self.underlying_address).balanceOf(self)


@private
@constant
def _current_price() -> uint256:
    # verify auction has not expired
    if self.is_active:
        if block.timestamp >= self._auction_expiry():
            return self.end_price
        else:
            return (as_unitless_number(self.start_price) * as_unitless_number(self.AUCTION_DURATION) - (as_unitless_number(self.start_price) - as_unitless_number(self.end_price)) * (as_unitless_number(block.timestamp) - as_unitless_number(self.expiry))) / as_unitless_number(self.AUCTION_DURATION)
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
def current_price() -> uint256:
    return self._current_price()


@public
def start(_underlying_price_per_currency_at_expiry: uint256, _currency_value: uint256, _underlying_value: uint256) -> bool:
    assert as_unitless_number(_underlying_price_per_currency_at_expiry) > 0
    assert as_unitless_number(_currency_value) > 0
    assert as_unitless_number(_underlying_value) > 0
    assert msg.sender == self.daos[self.DAO_TYPE_MARKET]
    assert block.timestamp >= self.expiry
    assert not self.is_active
    self.max_supply = _underlying_value
    self.currency_value_remaining = _currency_value
    # set start_price
    self.start_price = (as_unitless_number(_underlying_price_per_currency_at_expiry) * as_unitless_number(self.SLIPPAGE_PERCENTAGE)) / 100
    self.end_price = as_unitless_number(self.start_price) * (100 - self.MAXIMUM_DISCOUNT_PERCENTAGE) / 100
    self.is_active = True

    return True


@public
def purchase(_underlying_value: uint256) -> bool:
    assert self.is_active
    assert as_unitless_number(_underlying_value) <= as_unitless_number(self._lot())
    _underlying_value_remaining: uint256 = as_unitless_number(self._lot()) - as_unitless_number(_underlying_value)
    _currency_value: uint256 = as_unitless_number(_underlying_value) * self._current_price()
    assert as_unitless_number(self.currency_value_remaining) >= as_unitless_number(_currency_value)
    # deactivate if auction has expired or all underlying currency has been auctioned
    if (_underlying_value_remaining == 0) or \
        (as_unitless_number(self.currency_value_remaining) - as_unitless_number(_currency_value) == 0):
        self.is_active = False
    self.currency_value_remaining -= _currency_value
    assert_modifiable(ERC20(self.underlying_address).transfer(msg.sender, _underlying_value))
    assert_modifiable(MarketDao(self.daos[self.DAO_TYPE_MARKET]).secure_currency_deposit_and_market_update_from_auction_purchase(
        self.currency_address, self.expiry, self.underlying_address,
        msg.sender, _currency_value, _underlying_value, self.is_active
    ))
    if (not self.is_active) and (_underlying_value_remaining > 0):
        assert_modifiable(ERC20(self.underlying_address).transfer(
            self.daos[self.DAO_TYPE_MARKET],
            _underlying_value_remaining
        ))
    return True
