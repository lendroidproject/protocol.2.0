# Vyper version of the Lendroid protocol v2
# THIS CONTRACT HAS NOT BEEN AUDITED!


from contracts.interfaces import ERC20
from contracts.interfaces import MarketDao


owner: public(address)
currency: public(address)
underlying: public(address)
expiry: public(timestamp)
max_supply: public(uint256)
currency_remaining: public(uint256)
start_price: public(uint256)
end_price: public(uint256)
is_active: public(bool)

# dao_type => dao_address
daos: public(map(uint256, address))

DAO_TYPE_CURRENCY: public(uint256)

SLIPPAGE_PERCENTAGE: public(uint256)
MAXIMUM_DISCOUNT_PERCENTAGE: public(uint256)
AUCTION_DURATION: public(timedelta)


@public
def start(
    _currency: address, _expiry: timestamp, _underlying: address,
    _expiry_price: uint256, _currency_value: uint256, _underlying_value: uint256,
    _dao_currency: address
    ) -> bool:
    # verify inputs
    assert msg.sender.is_contract
    assert _currency.is_contract
    assert _underlying.is_contract
    assert as_unitless_number(_expiry) > 0
    assert block.timestamp >= _expiry
    assert as_unitless_number(_expiry_price) > 0
    assert as_unitless_number(_currency_value) > 0
    assert as_unitless_number(_underlying_value) > 0
    assert _dao_currency.is_contract
    # set parameters
    assert not self.is_active
    self.is_active = True
    self.owner = msg.sender
    self.currency = _currency
    self.underlying = _underlying
    self.expiry = _expiry
    self.SLIPPAGE_PERCENTAGE = 104
    self.MAXIMUM_DISCOUNT_PERCENTAGE = 40
    self.AUCTION_DURATION = 30 * 60

    self.max_supply = _underlying_value
    self.currency_remaining = _currency_value
    # set start_price
    self.start_price = (as_unitless_number(_expiry_price) * as_unitless_number(self.SLIPPAGE_PERCENTAGE)) / 100
    self.end_price = as_unitless_number(self.start_price) * (100 - self.MAXIMUM_DISCOUNT_PERCENTAGE) / 100

    self.DAO_TYPE_CURRENCY = 1
    self.daos[self.DAO_TYPE_CURRENCY] = _dao_currency

    return True


@private
@constant
def _auction_expiry() -> timestamp:
    return self.expiry + self.AUCTION_DURATION


@private
@constant
def _lot() -> uint256:
    return ERC20(self.underlying).balanceOf(self)


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


@private
def _purchase(_purchaser: address, _currency_value: uint256, _underlying_value: uint256):
    # deactivate if auction has expired or all underlying currency has been auctioned
    _underlying_remaining: uint256 = as_unitless_number(self._lot()) - as_unitless_number(_underlying_value)
    if (_underlying_remaining == 0) or \
        (as_unitless_number(self.currency_remaining) - as_unitless_number(_currency_value) == 0):
        self.is_active = False
    self.currency_remaining -= _currency_value
    assert_modifiable(MarketDao(self.owner).process_auction_purchase(
        self.currency, self.expiry, self.underlying,
        _purchaser, _currency_value, _underlying_value, self.is_active
    ))
    assert_modifiable(ERC20(self.underlying).transfer(_purchaser, _underlying_value))
    if (not self.is_active) and (_underlying_remaining > 0):
        assert_modifiable(ERC20(self.underlying).transfer(
            self.daos[self.DAO_TYPE_CURRENCY], _underlying_remaining
        ))


# Admin actions

@public
def escape_hatch_underlying() -> bool:
    assert msg.sender == self.owner
    assert_modifiable(ERC20(self.underlying).transfer(self.owner, self._lot()))
    return True


# Non-admin actions

@public
def purchase(_underlying_value: uint256) -> bool:
    assert self.is_active
    _currency_value: uint256 = as_unitless_number(_underlying_value) * as_unitless_number(self._current_price()) / 10 ** 18
    assert as_unitless_number(_underlying_value) <= as_unitless_number(self._lot())
    assert as_unitless_number(_currency_value) <= as_unitless_number(self.currency_remaining)
    self._purchase(msg.sender, _currency_value, _underlying_value)

    return True


@public
def purchase_for_remaining_currency() -> bool:
    assert self.is_active
    _underlying_value: uint256 = (as_unitless_number(self.currency_remaining) * (10 ** 18)) / as_unitless_number(self._current_price())
    _currency_value: uint256 = self.currency_remaining
    if as_unitless_number(_underlying_value) > as_unitless_number(self._lot()):
        _currency_value = as_unitless_number(self._lot()) * as_unitless_number(self._current_price()) / 10 ** 18
        _underlying_value = self._lot()
    assert as_unitless_number(_underlying_value) <= as_unitless_number(self._lot())
    assert as_unitless_number(_currency_value) <= as_unitless_number(self.currency_remaining)
    self._purchase(msg.sender, _currency_value, _underlying_value)

    return True


@public
def purchase_remaining_underlying() -> bool:
    assert self.is_active
    _underlying_value: uint256 = as_unitless_number(self._lot())
    _currency_value: uint256 = as_unitless_number(_underlying_value) * as_unitless_number(self._current_price()) / 10 ** 18
    if as_unitless_number(_currency_value) > as_unitless_number(self.currency_remaining):
        _underlying_value = (as_unitless_number(self.currency_remaining) * (10 ** 18)) / as_unitless_number(self._current_price())
        _currency_value = self.currency_remaining
    assert as_unitless_number(_underlying_value) <= as_unitless_number(self._lot())
    assert as_unitless_number(_currency_value) <= as_unitless_number(self.currency_remaining)
    self._purchase(msg.sender, _currency_value, _underlying_value)

    return True
