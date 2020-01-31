# @version 0.1.0b14
# @notice Implementation of Lendroid v2 - Simple Collateral Auction Curve
# @dev THIS CONTRACT HAS NOT BEEN AUDITED
# @author Vignesh (Vii) Meenakshi Sundaram (@vignesh-msundaram)
# Lendroid Foundation


from ...interfaces import MultiFungibleTokenInterface
from ...interfaces import MarketDaoInterface

from ...interfaces import ProtocolDaoInterface


owner: public(address)
protocol_dao: public(address)
currency: public(address)
underlying: public(address)
f_underlying: public(address)
f_id_underlying: public(uint256)
expiry: public(timestamp)
max_supply: public(uint256)
currency_remaining: public(uint256)
start_price: public(uint256)
end_price: public(uint256)
is_active: public(bool)
# auction settings
maximum_discount_percentage: public(uint256)
discount_duration: public(timedelta)

CALLER_ESCAPE_HATCH_TOKEN_HOLDER: constant(int128) = 3


@public
def start(
    _protocol_dao: address,
    _currency: address, _expiry: timestamp, _underlying: address,
    _f_underlying: address, _f_id_underlying: uint256,
    _start_price: uint256, _currency_value: uint256, _underlying_value: uint256,
    _maximum_discount_percentage: uint256,
    _discount_duration: timedelta
    ) -> bool:
    # verify inputs
    assert msg.sender.is_contract
    assert _protocol_dao.is_contract
    assert _currency.is_contract
    assert _underlying.is_contract
    assert as_unitless_number(_expiry) > 0
    assert block.timestamp >= _expiry
    assert as_unitless_number(_start_price) > 0
    assert as_unitless_number(_currency_value) > 0
    assert as_unitless_number(_underlying_value) > 0
    # set parameters
    assert not self.is_active
    self.is_active = True
    self.owner = msg.sender
    self.protocol_dao = _protocol_dao
    self.currency = _currency
    self.underlying = _underlying
    self.expiry = _expiry
    self.f_underlying = _f_underlying
    self.f_id_underlying = _f_id_underlying
    self.maximum_discount_percentage = _maximum_discount_percentage
    self.discount_duration = _discount_duration

    self.max_supply = _underlying_value
    self.currency_remaining = _currency_value
    # set start_price
    self.start_price = _start_price
    self.end_price = as_unitless_number(self.start_price) * (100 - self.maximum_discount_percentage) / 100

    return True


@private
@constant
def _loan_market_hash() -> bytes32:
    """
        @dev Function to get the hash of a loan market, given the currency,
             expiry, and underlying.
        @param _currency The address of the currency.
        @param _expiry The timestamp when the loan market expires.
        @param _underlying The address of the underlying.
        @return A unique bytes32 representing the loan market.
    """
    return keccak256(
        concat(
            convert(self.protocol_dao, bytes32),
            convert(self.currency, bytes32),
            convert(self.expiry, bytes32),
            convert(self.underlying, bytes32),
            convert(0, bytes32)
        )
    )


@private
@constant
def _auction_expiry() -> timestamp:
    return self.expiry + self.discount_duration


@private
@constant
def _lot() -> uint256:
    return MultiFungibleTokenInterface(self.f_underlying).balanceOf(self, self.f_id_underlying)


@private
@constant
def _current_price() -> uint256:
    # verify auction has not expired
    if self.is_active:
        if block.timestamp >= self._auction_expiry():
            return self.end_price
        else:
            return (as_unitless_number(self.start_price) * as_unitless_number(self.discount_duration) - (as_unitless_number(self.start_price) - as_unitless_number(self.end_price)) * (as_unitless_number(block.timestamp) - as_unitless_number(self.expiry))) / as_unitless_number(self.discount_duration)
    else:
        return 0


@private
def _transfer_f_underlying(_to: address, _value: uint256):
    assert_modifiable(MultiFungibleTokenInterface(self.f_underlying).safeTransferFrom(self, _to, self.f_id_underlying, _value, EMPTY_BYTES32))


@private
def _reset_currency_remaining():
    self.currency_remaining = MarketDaoInterface(self.owner).currency_remaining_for_auction(self._loan_market_hash())


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
    _external_call_successful: bool = False
    _loan_market_closed: bool = False
    _external_call_successful, _loan_market_closed = MarketDaoInterface(self.owner).process_auction_purchase(
        self.currency, self.expiry, self.underlying,
        _purchaser, _currency_value, _underlying_value, self.is_active
    )
    assert _external_call_successful
    self.is_active = not _loan_market_closed
    self._transfer_f_underlying(_purchaser, _underlying_value)
    if (not self.is_active) and (_underlying_remaining > 0):
        self._transfer_f_underlying(self.owner, _underlying_value)


# Admin actions

@public
def escape_hatch_underlying_f() -> bool:
    assert msg.sender == self.owner
    self._transfer_f_underlying(
        ProtocolDaoInterface(self.protocol_dao).authorized_callers(CALLER_ESCAPE_HATCH_TOKEN_HOLDER),
        self._lot()
    )
    return True


# Non-admin actions

@public
def purchase(_underlying_value: uint256) -> bool:
    assert self.is_active
    self._reset_currency_remaining()
    _currency_value: uint256 = as_unitless_number(_underlying_value) * as_unitless_number(self._current_price()) / 10 ** 18
    assert as_unitless_number(_underlying_value) <= as_unitless_number(self._lot())
    assert as_unitless_number(_currency_value) <= as_unitless_number(self.currency_remaining)
    self._purchase(msg.sender, _currency_value, _underlying_value)

    return True


@public
def purchase_for_remaining_currency() -> bool:
    assert self.is_active
    self._reset_currency_remaining()
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
    self._reset_currency_remaining()
    _underlying_value: uint256 = as_unitless_number(self._lot())
    _currency_value: uint256 = as_unitless_number(_underlying_value) * as_unitless_number(self._current_price()) / 10 ** 18
    if as_unitless_number(_currency_value) > as_unitless_number(self.currency_remaining):
        _underlying_value = (as_unitless_number(self.currency_remaining) * (10 ** 18)) / as_unitless_number(self._current_price())
        _currency_value = self.currency_remaining
    assert as_unitless_number(_underlying_value) <= as_unitless_number(self._lot())
    assert as_unitless_number(_currency_value) <= as_unitless_number(self.currency_remaining)
    self._purchase(msg.sender, _currency_value, _underlying_value)

    return True
