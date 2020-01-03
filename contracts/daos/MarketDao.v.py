# Vyper version of the Lendroid protocol v2
# THIS CONTRACT HAS NOT BEEN AUDITED!


from contracts.interfaces import ERC20
from contracts.interfaces import MultiFungibleToken
from contracts.interfaces import CurrencyDao
from contracts.interfaces import ShieldPayoutDao
from contracts.interfaces import CollateralAuctionCurve
from contracts.interfaces import SimplePriceOracle

from contracts.interfaces import ProtocolDao

# Structs
struct ExpiryMarket:
    expiry: timestamp
    id: uint256


struct LoanMarket:
    currency: address
    expiry: timestamp
    underlying: address
    settlement_price: uint256
    status: uint256
    liability: uint256
    collateral: uint256
    auction_curve: address
    auction_currency_raised: uint256
    auction_underlying_sold: uint256
    shield_market_count: uint256
    hash: bytes32
    id: uint256


struct ShieldMarket:
    currency: address
    expiry: timestamp
    underlying: address
    strike_price: uint256
    s_address: address
    s_id: uint256
    u_address: address
    u_id: uint256
    hash: bytes32
    id: uint256


LST: public(address)
protocol_dao: public(address)
# dao_type => dao_address
daos: public(map(int128, address))
# registry_type => registry_address
registries: public(map(int128, address))
# template_name => template_contract_address
templates: public(map(int128, address))
# expiry_market_timestammp => ExpiryMarket
expiry_markets: public(map(timestamp, ExpiryMarket))
# index per ExpiryMarket
next_expiry_market_id: public(uint256)
# expiry_market_id => expiry_market_timestammp
expiry_market_id_to_timestamp: public(map(uint256, timestamp))
# loan_market_hash => LoanMarket
loan_markets: public(map(bytes32, LoanMarket))
# expiry_timestamp => index per LoanMarket
next_loan_market_id: public(map(timestamp, uint256))
# expiry_timestamp => (loan_market_id => loan_market_hash)
loan_market_id_to_hash: public(map(timestamp, map(uint256, bytes32)))
# shield_market_hash => ShieldMarket
shield_markets: public(map(bytes32, ShieldMarket))
# expiry_timestamp => index per ShieldMarket
next_shield_market_id: public(map(timestamp, uint256))
# expiry_timestamp => (market_id => shield_market_hash)
shield_market_id_to_hash: public(map(timestamp, map(uint256, bytes32)))
# currency_underlying_pair_hash => price_oracle_address
price_oracles: public(map(bytes32, address))
maximum_market_liabilities: public(map(bytes32, uint256))
# auction settings
auction_slippage_percentage: public(uint256)
auction_maximum_discount_percentage: public(uint256)
auction_discount_duration: public(timedelta)

REGISTRY_POSITION: constant(int128) = 2

DAO_CURRENCY: constant(int128) = 1
DAO_INTEREST_POOL: constant(int128) = 2
DAO_UNDERWRITER_POOL: constant(int128) = 3
DAO_SHIELD_PAYOUT: constant(int128) = 5

TEMPLATE_COLLATERAL_AUCTION: constant(int128) = 5

LOAN_MARKET_STATUS_OPEN: public(uint256)
LOAN_MARKET_STATUS_SETTLING: public(uint256)
LOAN_MARKET_STATUS_CLOSED: public(uint256)

CALLER_ESCAPE_HATCH_TOKEN_HOLDER: constant(int128) = 3

MFT_TYPE_F: constant(int128) = 1
MFT_TYPE_I: constant(int128) = 2
MFT_TYPE_S: constant(int128) = 3
MFT_TYPE_U: constant(int128) = 4

initialized: public(bool)
paused: public(bool)


@public
def initialize(
        _LST: address,
        _dao_currency: address,
        _dao_interest_pool: address,
        _dao_underwriter_pool: address,
        _dao_shield_payout: address,
        _registry_position: address,
        _template_auction_erc20: address) -> bool:
    assert not self.initialized
    self.initialized = True
    self.protocol_dao = msg.sender
    self.LST = _LST

    self.registries[REGISTRY_POSITION] = _registry_position

    self.daos[DAO_CURRENCY] = _dao_currency
    self.daos[DAO_INTEREST_POOL] = _dao_interest_pool
    self.daos[DAO_UNDERWRITER_POOL] = _dao_underwriter_pool
    self.daos[DAO_SHIELD_PAYOUT] = _dao_shield_payout

    self.templates[TEMPLATE_COLLATERAL_AUCTION] = _template_auction_erc20

    self.LOAN_MARKET_STATUS_OPEN = 1
    self.LOAN_MARKET_STATUS_SETTLING = 2
    self.LOAN_MARKET_STATUS_CLOSED = 3

    return True


@private
@constant
def _mft_hash(_address: address, _currency: address, _expiry: timestamp, _underlying: address, _strike_price: uint256) -> bytes32:
    """
        @dev Function to get the hash of a MFT, given its address and indicators.
        @param _address The address of the MFT.
        @param _currency The address of the currency token in the MFT.
        @param _expiry The timestamp when the MFT expires.
        @param _underlying The address of the underlying token in the MFT.
        @param _strike_price The price of the underlying per currency at _expiry.
        @return A unique bytes32 representing the MFT at the given address and indicators.
    """
    return keccak256(
        concat(
            convert(self.protocol_dao, bytes32),
            convert(_address, bytes32),
            convert(_currency, bytes32),
            convert(_expiry, bytes32),
            convert(_underlying, bytes32),
            convert(_strike_price, bytes32)
        )
    )


@private
@constant
def _shield_market_hash(_currency: address, _expiry: timestamp, _underlying: address, _strike_price: uint256) -> bytes32:
    """
        @dev Function to get the hash of a shield market, given the currency,
             expiry, underlying, and strike price.
        @param _currency The address of the currency.
        @param _expiry The timestamp when the shield market expires.
        @param _underlying The address of the underlying.
        @param _strike_price The price of the underlying per currency at _expiry.
        @return A unique bytes32 representing the shield market.
    """
    return keccak256(
        concat(
            convert(self.protocol_dao, bytes32),
            convert(_currency, bytes32),
            convert(_expiry, bytes32),
            convert(_underlying, bytes32),
            convert(_strike_price, bytes32)
        )
    )


@private
@constant
def _currency_market_hash(_currency: address, _expiry: timestamp) -> bytes32:
    """
        @dev Function to get the hash of a currency market, given the currency
             and expiry.
        @param _currency The address of the currency.
        @param _expiry The timestamp when the currency market expires.
        @return A unique bytes32 representing the currency market.
    """
    return self._shield_market_hash(_currency, _expiry, ZERO_ADDRESS, 0)


@private
@constant
def _loan_market_hash(_currency: address, _expiry: timestamp, _underlying: address) -> bytes32:
    """
        @dev Function to get the hash of a loan market, given the currency,
             expiry, and underlying.
        @param _currency The address of the currency.
        @param _expiry The timestamp when the loan market expires.
        @param _underlying The address of the underlying.
        @return A unique bytes32 representing the loan market.
    """
    return self._shield_market_hash(_currency, _expiry, _underlying, 0)


@private
@constant
def _currency_underlying_pair_hash(_currency: address, _underlying: address) -> bytes32:
    """
        @dev Function to get the hash of a currency-underlying pair, given the
             currency and the underlying.
        @param _currency The address of the currency.
        @param _underlying The address of the underlying.
        @return A unique bytes32 representing the currency underlying pair.
    """
    return keccak256(
        concat(
            convert(self.protocol_dao, bytes32),
            convert(_currency, bytes32),
            convert(_underlying, bytes32)
        )
    )


@private
@constant
def _s_payoff(
        _currency: address, _expiry: timestamp,
        _underlying: address, _strike_price: uint256) -> uint256:
    _settlement_price: uint256 = self.loan_markets[self._loan_market_hash(_currency, _expiry, _underlying)].settlement_price
    if as_unitless_number(_settlement_price) >= as_unitless_number(_strike_price):
        return 0
    else:
        return (as_unitless_number(_strike_price) - as_unitless_number(_settlement_price)) / as_unitless_number(_strike_price)


@private
@constant
def _u_payoff(
    _currency: address, _expiry: timestamp,
    _underlying: address, _strike_price: uint256) -> uint256:
    _settlement_price: uint256 = self.loan_markets[self._loan_market_hash(_currency, _expiry, _underlying)].settlement_price
    if as_unitless_number(_settlement_price) >= as_unitless_number(_strike_price):
        return 1
    else:
        return as_unitless_number(_settlement_price) / as_unitless_number(_strike_price)


@public
@constant
def s_payoff(_currency: address, _expiry: timestamp, _underlying: address, _strike_price: uint256) -> uint256:
    if not self.loan_markets[self._loan_market_hash(_currency, _expiry, _underlying)].status == self.LOAN_MARKET_STATUS_CLOSED:
        return 0
    return self._s_payoff(_currency, _expiry, _underlying, _strike_price)


@public
@constant
def u_payoff(_currency: address, _expiry: timestamp, _underlying: address, _strike_price: uint256) -> uint256:
    _loan_market_hash: bytes32 = self._loan_market_hash(_currency, _expiry, _underlying)
    if not self.loan_markets[self._loan_market_hash(_currency, _expiry, _underlying)].status == self.LOAN_MARKET_STATUS_CLOSED:
        return 0
    return self._u_payoff(_currency, _expiry, _underlying, _strike_price)


@private
def _transfer_f_underlying(_currency: address, _expiry: timestamp, _from: address, _to: address, _value: uint256):
    _token: address = CurrencyDao(self.daos[DAO_CURRENCY]).token_addresses__f(_currency)
    assert not _token == ZERO_ADDRESS
    _id: uint256 = MultiFungibleToken(_token).id(_currency, _expiry, ZERO_ADDRESS, 0)
    assert not _id == 0
    assert_modifiable(MultiFungibleToken(_token).safeTransferFrom(_from, _to, _id, _value, EMPTY_BYTES32))


@private
def _open_expiry_market(_expiry: timestamp):
    assert _expiry > block.timestamp
    self.expiry_market_id_to_timestamp[self.next_expiry_market_id] = _expiry
    self.expiry_markets[_expiry] = ExpiryMarket({
        expiry: _expiry,
        id: self.next_expiry_market_id
    })
    self.next_expiry_market_id += 1


@private
def _open_loan_market(_currency: address, _expiry: timestamp, _underlying: address):
    assert _expiry > block.timestamp
    assert self.expiry_markets[_expiry].expiry == _expiry
    _loan_market_hash: bytes32 = self._loan_market_hash(_currency, _expiry, _underlying)
    self.loan_market_id_to_hash[_expiry][self.next_loan_market_id[_expiry]] = _loan_market_hash
    self.loan_markets[_loan_market_hash] = LoanMarket({
        currency: _currency,
        expiry: _expiry,
        underlying: _underlying,
        settlement_price: 0,
        status: self.LOAN_MARKET_STATUS_OPEN,
        liability: 0,
        collateral: 0,
        auction_curve: ZERO_ADDRESS,
        auction_currency_raised: 0,
        auction_underlying_sold: 0,
        shield_market_count: 0,
        hash: _loan_market_hash,
        id: self.next_loan_market_id[_expiry]
    })
    self.next_loan_market_id[_expiry] += 1


@private
def _settle_loan_market(_loan_market_hash: bytes32):
    # set _underlying_price_per_currency_at_expiry from an external price-feed oracle
    _currency_underlying_pair_hash: bytes32 = self._currency_underlying_pair_hash(
        self.loan_markets[_loan_market_hash].currency,
        self.loan_markets[_loan_market_hash].underlying
    )
    assert self.price_oracles[_currency_underlying_pair_hash].is_contract
    self.loan_markets[_loan_market_hash].settlement_price = SimplePriceOracle(self.price_oracles[_currency_underlying_pair_hash]).get_price()
    if as_unitless_number(self.loan_markets[_loan_market_hash].liability) > 0:
        # deploy and start collateral auction
        _auction: address = create_forwarder_to(self.templates[TEMPLATE_COLLATERAL_AUCTION])
        assert _auction.is_contract
        self.loan_markets[_loan_market_hash].auction_curve = _auction
        self.loan_markets[_loan_market_hash].status = self.LOAN_MARKET_STATUS_SETTLING
        # start collateral auction
        _f_underlying: address = CurrencyDao(self.daos[DAO_CURRENCY]).token_addresses__f(self.loan_markets[_loan_market_hash].underlying)
        assert not _f_underlying == ZERO_ADDRESS
        _f_id_underlying: uint256 = MultiFungibleToken(_f_underlying).id(
            self.loan_markets[_loan_market_hash].underlying,
            self.loan_markets[_loan_market_hash].expiry, ZERO_ADDRESS, 0)
        assert not _f_id_underlying == 0
        assert_modifiable(CollateralAuctionCurve(_auction).start(
            self.protocol_dao,
            self.loan_markets[_loan_market_hash].currency,
            self.loan_markets[_loan_market_hash].expiry,
            self.loan_markets[_loan_market_hash].underlying,
            _f_underlying, _f_id_underlying,
            self.loan_markets[_loan_market_hash].settlement_price,
            self.loan_markets[_loan_market_hash].liability,
            self.loan_markets[_loan_market_hash].collateral,
            self.auction_slippage_percentage,
            self.auction_maximum_discount_percentage,
            self.auction_discount_duration
        ))

        # send oustanding_value of f_tokens to auction contract
        self._transfer_f_underlying(
            self.loan_markets[_loan_market_hash].underlying,
            self.loan_markets[_loan_market_hash].expiry,
            self,
            _auction,
            self.loan_markets[_loan_market_hash].collateral
        )
    else:
        self.loan_markets[_loan_market_hash].status = self.LOAN_MARKET_STATUS_CLOSED


@private
def _open_shield_market(_currency: address, _expiry: timestamp, _underlying: address, _strike_price: uint256,
    _s_address: address, _s_id: uint256,
    _u_address: address, _u_id: uint256):
    assert block.timestamp < _expiry
    _shield_market_hash: bytes32 = self._shield_market_hash(_currency, _expiry, _underlying, _strike_price)
    self.shield_market_id_to_hash[_expiry][self.next_shield_market_id[_expiry]] = _shield_market_hash
    # register shield_market
    assert_modifiable(ShieldPayoutDao(self.daos[DAO_SHIELD_PAYOUT]).register_shield_market(
        _currency, _expiry, _underlying, _strike_price
    ))

    # save shield market
    self.shield_markets[_shield_market_hash] = ShieldMarket({
        currency: _currency,
        expiry: _expiry,
        underlying: _underlying,
        strike_price: _strike_price,
        s_address: _s_address,
        s_id: _s_id,
        u_address: _u_address,
        u_id: _u_id,
        hash: _shield_market_hash,
        id: self.next_shield_market_id[_expiry]
    })
    self.next_shield_market_id[_expiry] += 1
    # update loan market
    _loan_market_hash: bytes32 = self._loan_market_hash(_currency, _expiry, _underlying)
    self.loan_markets[_loan_market_hash].shield_market_count += 1


@public
@constant
def shield_market_hash(_currency: address, _expiry: timestamp, _underlying: address, _strike_price: uint256) -> bytes32:
    return self._shield_market_hash(_currency, _expiry, _underlying, _strike_price)


@public
@constant
def loan_market_hash(_currency: address, _expiry: timestamp, _underlying: address) -> bytes32:
    return self._loan_market_hash(_currency, _expiry, _underlying)


@public
@constant
def currency_underlying_pair_hash(_currency: address, _underlying: address) -> bytes32:
    return self._currency_underlying_pair_hash(_currency, _underlying)


# Admin functions


@public
def set_template(_template_type: int128, _address: address) -> bool:
    """
        @dev Function to set / change the Template address. Only the Protocol
             DAO can call this function.
        @param _template_type The type of the Template that has to be changed.
        @param _address The address of the new Template contract.
        @return A bool with a value of "True" indicating the template change
            has been made.
    """
    assert self.initialized
    assert msg.sender == self.protocol_dao
    assert _template_type == TEMPLATE_COLLATERAL_AUCTION
    self.templates[_template_type] = _address
    return True


@public
def set_registry(_registry_type: int128, _address: address) -> bool:
    """
        @dev Function to set / change a Registry address. Only the Protocol DAO
             can call this function.
        @param _registry_type The type of the Registry that has to be changed.
        @param _address The address of the new Registry contract.
        @return A bool with a value of "True" indicating the registry change
             has been made.
    """
    assert self.initialized
    assert msg.sender == self.protocol_dao
    assert _registry_type == REGISTRY_POSITION
    self.registries[_registry_type] = _address
    return True


@public
def set_price_oracle(_currency: address, _underlying: address, _oracle: address) -> bool:
    """
        @dev Function to set the address of the Price Oracle contract for a
             given currency-underlying pair. Only the Protocol DAO can call this
             function.
        @param _currency The currency token in the currency-underlying pair.
        @param _underlying The underlying token in the currency-underlying pair.
        @param _oracle The address of the Price Oracle.
        @return A bool with a value of "True" indicating the Price Oracle address
             has been set for the currency-underlying pair.
    """
    assert self.initialized
    assert msg.sender == self.protocol_dao
    assert _currency.is_contract
    assert _underlying.is_contract
    assert _oracle.is_contract
    _currency_underlying_pair_hash: bytes32 = self._currency_underlying_pair_hash(_currency, _underlying)
    self.price_oracles[_currency_underlying_pair_hash] = _oracle

    return True


@public
@constant
def maximum_liability_for_currency_market(_currency: address, _expiry: timestamp) -> uint256:
    return self.maximum_market_liabilities[self._currency_market_hash(_currency, _expiry)]


@public
def set_maximum_liability_for_currency_market(_currency: address, _expiry: timestamp, _value: uint256) -> bool:
    """
        @dev Function to set the maximum currency liability that the system can
             accommodate until a certain expiry. Only the Protocol DAO can call
             this function.
        @param _currency The currency token.
        @param _expiry The expiry until which the maximum liability can be
             accommodated.
        @param _value The maximum liability value
        @return A bool with a value of "True" indicating the maximum currency
             liability until the given expiry has been set.
    """
    assert self.initialized
    assert msg.sender == self.protocol_dao
    self.maximum_market_liabilities[self._currency_market_hash(_currency, _expiry)] = _value

    return True


@public
@constant
def maximum_liability_for_loan_market(_currency: address, _expiry: timestamp, _underlying: address) -> uint256:
    return self.maximum_market_liabilities[self._loan_market_hash(_currency, _expiry, _underlying)]


@public
def set_maximum_liability_for_loan_market(_currency: address, _expiry: timestamp, _underlying: address, _value: uint256) -> bool:
    """
        @dev Function to set the maximum currency liability that the system can
             accommodate until a certain expiry for a specific underlying. Only
             the Protocol DAO can call this function.
        @param _currency The currency token.
        @param _expiry The expiry until which the maximum liability can be
             accommodated.
        @param _underlying The underlying token.
        @param _value The maximum liability value
        @return A bool with a value of "True" indicating the maximum currency
             liability until the given expiry for the given underlying has been
             set.
    """
    assert self.initialized
    assert msg.sender == self.protocol_dao
    self.maximum_market_liabilities[self._loan_market_hash(_currency, _expiry, _underlying)] = _value

    return True


@public
def set_auction_slippage_percentage(_value: uint256) -> bool:
    """
        @dev Function to set the slippage percentage when calculating the start
             prices in all upcoming collateral auctions. Only the Protocol DAO
             can call this function.
        @param _value The slippage percentage
        @return A bool with a value of "True" indicating the slippage percentage
             has been set.
    """
    assert self.initialized
    assert msg.sender == self.protocol_dao
    self.auction_slippage_percentage = _value

    return True


@public
def set_auction_maximum_discount_percentage(_value: uint256) -> bool:
    """
        @dev Function to set the maximum discount percentage when calculating
             the final discounted prices in all upcoming collateral auctions.
             Only the Protocol DAO can call this function.
        @param _value The maximum discount percentage
        @return A bool with a value of "True" indicating the maximum discount
             percentage has been set.
    """
    assert self.initialized
    assert msg.sender == self.protocol_dao
    self.auction_maximum_discount_percentage = _value

    return True


@public
def set_auction_discount_duration(_value: timedelta) -> bool:
    """
        @dev Function to set the duration in seconds when the underlying is
             sold at a discount in all upcoming collateral auctions. Only the
             Protocol DAO can call this function.
        @param _value The duration in seconds
        @return A bool with a value of "True" indicating the discount duration
             has been set.
    """
    assert self.initialized
    assert msg.sender == self.protocol_dao
    self.auction_discount_duration = _value

    return True


# Escape-hatches

@private
def _pause():
    """
        @dev Internal function to pause this contract.
    """
    assert not self.paused
    self.paused = True


@private
def _unpause():
    """
        @dev Internal function to unpause this contract.
    """
    assert self.paused
    self.paused = False

@public
def pause() -> bool:
    """
        @dev Escape hatch function to pause this contract. Only the Protocol DAO
             can call this function.
        @return A bool with a value of "True" indicating this contract has been
             paused.
    """
    assert self.initialized
    assert msg.sender == self.protocol_dao
    self._pause()
    return True


@public
def unpause() -> bool:
    """
        @dev Escape hatch function to unpause this contract. Only the Protocol
             DAO can call this function.
        @return A bool with a value of "True" indicating this contract has been
             unpaused.
    """
    assert self.initialized
    assert msg.sender == self.protocol_dao
    self._unpause()
    return True


@private
def _transfer_balance_erc20(_token: address):
    """
        @dev Internal function to transfer this contract's balance of the given
             ERC20 token to the Escape Hatch Token Holder.
        @param _token The address of the ERC20 token.
    """
    assert_modifiable(ERC20(_token).transfer(
        ProtocolDao(self.protocol_dao).authorized_callers(CALLER_ESCAPE_HATCH_TOKEN_HOLDER),
        ERC20(_token).balanceOf(self)
    ))


@private
def _transfer_balance_mft(_token: address,
    _currency: address, _expiry: timestamp, _underlying: address, _strike_price: uint256):
    """
        @dev Internal function to transfer this contract's balance of MFT based
             on the given indicators to the Escape Hatch Token Holder.
        @param _token The address of the MFT.
        @param _currency The address of the currency token in the MFT.
        @param _expiry The timestamp when the MFT expires.
        @param _underlying The address of the underlying token in the MFT.
        @param _strike_price The price of the underlying per currency at _expiry.
    """
    _mft_hash: bytes32 = self._mft_hash(_token, _currency, _expiry, _underlying, _strike_price)
    _id: uint256 = MultiFungibleToken(_token).hash_to_id(_mft_hash)
    _balance: uint256 = MultiFungibleToken(_token).balanceOf(self, _id)
    assert_modifiable(MultiFungibleToken(_token).safeTransferFrom(
        self,
        ProtocolDao(self.protocol_dao).authorized_callers(CALLER_ESCAPE_HATCH_TOKEN_HOLDER),
        _id, _balance, EMPTY_BYTES32
    ))


@public
def escape_hatch_auction(_currency: address, _expiry: timestamp, _underlying: address) -> bool:
    """
        @dev Escape hatch function to transfer all tokens of the underlying MFT
             type F from the auction contract for the given loan market
             indicators, to the Escape Hatch Token Holder.
             Only the Protocol DAO can call this function.
        @param _currency The currency token in the loan market.
        @param _expiry The timstamp of loan market expiry.
        @param _underlying TThe underlying token in the loan market.
        @return A bool with a value of "True" indicating the MFT transfer has
             been made from the corresponding auction contract.
    """
    assert self.initialized
    assert msg.sender == self.protocol_dao
    _loan_market_hash: bytes32 = self._loan_market_hash(_currency, _expiry, _underlying)
    assert_modifiable(CollateralAuctionCurve(self.loan_markets[_loan_market_hash].auction_curve).escape_hatch_underlying_f())
    return True


@public
def escape_hatch_erc20(_currency: address, _is_l: bool) -> bool:
    """
        @dev Escape hatch function to transfer all tokens of an ERC20 address
             from this contract to the Escape Hatch Token Holder. Only the
             Protocol DAO can call this function.
        @param _currency The address of the ERC20 token
        @param _is_l A bool indicating if the ERC20 token is an L Token
        @return A bool with a value of "True" indicating the ERC20 transfer has
             been made to the Escape Hatch Token Holder.
    """
    assert self.initialized
    assert msg.sender == self.protocol_dao
    _token: address = _currency
    if _is_l:
        CurrencyDao(self.daos[DAO_CURRENCY]).token_addresses__l(_currency)
    self._transfer_balance_erc20(_currency)
    return True


@public
def escape_hatch_mft(_mft_type: int128, _currency: address, _expiry: timestamp, _underlying: address, _strike_price: uint256) -> bool:
    """
        @dev Escape hatch function to transfer all tokens of a MFT with given
             parameters from this contract to the Escape Hatch Token Holder.
             Only the Protocol DAO can call this function.
        @param _mft_type The MFT type (L, I, S, or U) from which the MFT address
             could be deduced.
        @param _currency The address of the currency token in the MFT.
        @param _expiry The timestamp when the MFT expires.
        @param _underlying The address of the underlying token in the MFT.
        @param _strike_price The price of the underlying per currency at _expiry.
        @return A bool with a value of "True" indicating the MFT transfer has
             been made to the Escape Hatch Token Holder.
    """
    assert self.initialized
    assert msg.sender == self.protocol_dao
    _token: address = ZERO_ADDRESS
    if _mft_type == MFT_TYPE_F:
        CurrencyDao(self.daos[DAO_CURRENCY]).token_addresses__f(_currency)
    if _mft_type == MFT_TYPE_I:
        CurrencyDao(self.daos[DAO_CURRENCY]).token_addresses__i(_currency)
    if _mft_type == MFT_TYPE_S:
        CurrencyDao(self.daos[DAO_CURRENCY]).token_addresses__s(_currency)
    if _mft_type == MFT_TYPE_U:
        CurrencyDao(self.daos[DAO_CURRENCY]).token_addresses__u(_currency)
    assert not _token == ZERO_ADDRESS
    self._transfer_balance_mft(_token, _currency, _expiry, _underlying, _strike_price)
    return True


# Non-admin functions


@public
def open_shield_market(_currency: address, _expiry: timestamp, _underlying: address, _strike_price: uint256,
    _s_address: address, _s_id: uint256,
    _u_address: address, _u_id: uint256) -> bool:
    assert self.initialized
    assert msg.sender == self.daos[DAO_UNDERWRITER_POOL]
    # create expiry market if it does not exist
    if not self.expiry_markets[_expiry].expiry == _expiry:
        self._open_expiry_market(_expiry)
    # create loan market if it does not exist
    if self.loan_markets[self._loan_market_hash(_currency, _expiry, _underlying)].hash == EMPTY_BYTES32:
        self._open_loan_market(_currency, _expiry, _underlying)
    # create shield market if it does not exist
    if self.shield_markets[self._shield_market_hash(_currency, _expiry, _underlying, _strike_price)].hash == EMPTY_BYTES32:
        self._open_shield_market(_currency, _expiry, _underlying, _strike_price,
            _s_address, _s_id, _u_address, _u_id)

    return True


@public
def settle_loan_market(_loan_market_hash: bytes32):
    assert self.initialized
    assert not self.paused
    assert block.timestamp >= self.loan_markets[_loan_market_hash].expiry
    assert self.loan_markets[_loan_market_hash].status == self.LOAN_MARKET_STATUS_OPEN
    self._settle_loan_market(_loan_market_hash)


@public
def process_auction_purchase(
    _currency: address, _expiry: timestamp, _underlying: address,
    _purchaser: address, _currency_value: uint256, _underlying_value: uint256,
    _is_auction_active: bool
    ) -> bool:
    assert self.initialized
    assert not self.paused
    _loan_market_hash: bytes32 = self._loan_market_hash(_currency, _expiry, _underlying)
    assert msg.sender == self.loan_markets[_loan_market_hash].auction_curve
    assert_modifiable(CurrencyDao(self.daos[DAO_CURRENCY]).authorized_deposit_token(
        _currency, _purchaser, _currency_value))
    self.loan_markets[_loan_market_hash].auction_currency_raised += _currency_value
    self.loan_markets[_loan_market_hash].auction_underlying_sold += _underlying_value
    if not _is_auction_active:
        self.loan_markets[_loan_market_hash].status = self.LOAN_MARKET_STATUS_CLOSED
        self.loan_markets[_loan_market_hash].settlement_price = (as_unitless_number(self.loan_markets[_loan_market_hash].auction_currency_raised) * (10 ** 18)) / as_unitless_number(self.loan_markets[_loan_market_hash].auction_underlying_sold)

    return True


@public
def open_position(
    _borrower: address, _currency_value: uint256,
    _currency: address, _expiry: timestamp, _underlying: address, _strike_price: uint256
    ) -> bool:
    assert self.initialized
    assert not self.paused
    # validate caller
    assert msg.sender == self.registries[REGISTRY_POSITION]
    _shield_market_hash: bytes32 = self._shield_market_hash(_currency, _expiry, _underlying, _strike_price)
    assert self.shield_markets[_shield_market_hash].currency == _currency
    assert self.shield_markets[_shield_market_hash].underlying == _underlying
    assert self.shield_markets[_shield_market_hash].expiry == _expiry
    assert self.shield_markets[_shield_market_hash].strike_price == _strike_price
    # validate tokens
    assert CurrencyDao(self.daos[DAO_CURRENCY]).is_token_supported(_currency)
    assert CurrencyDao(self.daos[DAO_CURRENCY]).is_token_supported(_underlying)

    _loan_market_hash: bytes32 = self._loan_market_hash(
        _currency,
        _expiry,
        _underlying
    )
    assert self.loan_markets[_loan_market_hash].status == self.LOAN_MARKET_STATUS_OPEN
    assert as_unitless_number(self.loan_markets[_loan_market_hash].liability) + as_unitless_number(_currency_value) <= as_unitless_number(self.maximum_market_liabilities[_loan_market_hash])
    _underlying_value: uint256 = as_unitless_number(_currency_value) / as_unitless_number(_strike_price)
    self.loan_markets[_loan_market_hash].liability += _currency_value
    self.loan_markets[_loan_market_hash].collateral += _underlying_value
    # transfer i_lend_currency from _borrower to self
    _i_address: address = ZERO_ADDRESS
    _i_id: uint256 = 0
    _i_address, _i_id = CurrencyDao(self.daos[DAO_CURRENCY]).i_token(_currency, _expiry)
    # transfer i_lend_currency from _borrower to self
    assert_modifiable(MultiFungibleToken(_i_address).safeTransferFrom(_borrower, self, _i_id, _currency_value, EMPTY_BYTES32))
    # transfer s_lend_currency from _borrower to self
    assert_modifiable(MultiFungibleToken(self.shield_markets[_shield_market_hash].s_address).safeTransferFrom(
        _borrower, self, self.shield_markets[_shield_market_hash].s_id, _currency_value, EMPTY_BYTES32
    ))
    # transfer f_borrow_currency from borrower to self
    self._transfer_f_underlying(_underlying, _expiry, _borrower, self, _underlying_value)
    # transfer lend_currency to _borrower
    assert_modifiable(CurrencyDao(self.daos[DAO_CURRENCY]).authorized_withdraw_token(
        _currency, _borrower, _currency_value))

    return True


@public
def close_position(
    _borrower: address, _currency_value: uint256,
    _currency: address, _expiry: timestamp, _underlying: address, _strike_price: uint256
    ) -> bool:
    assert self.initialized
    assert not self.paused
    # validate caller
    assert msg.sender == self.registries[REGISTRY_POSITION]
    _shield_market_hash: bytes32 = self._shield_market_hash(_currency, _expiry, _underlying, _strike_price)
    assert self.shield_markets[_shield_market_hash].currency == _currency
    assert self.shield_markets[_shield_market_hash].underlying == _underlying
    assert self.shield_markets[_shield_market_hash].expiry == _expiry
    assert self.shield_markets[_shield_market_hash].strike_price == _strike_price
    # validate tokens
    assert CurrencyDao(self.daos[DAO_CURRENCY]).is_token_supported(_currency)
    assert CurrencyDao(self.daos[DAO_CURRENCY]).is_token_supported(_underlying)
    _loan_market_hash: bytes32 = self._loan_market_hash(
        _currency,
        _expiry,
        _underlying
    )
    assert self.loan_markets[_loan_market_hash].status == self.LOAN_MARKET_STATUS_OPEN
    _underlying_value: uint256 = as_unitless_number(_currency_value) / as_unitless_number(_strike_price)
    self.loan_markets[_loan_market_hash].liability -= _currency_value
    self.loan_markets[_loan_market_hash].collateral -= _underlying_value
    # transfer i_lend_currency from self to _borrower
    _i_address: address = ZERO_ADDRESS
    _i_id: uint256 = 0
    _i_address, _i_id = CurrencyDao(self.daos[DAO_CURRENCY]).i_token(_currency, _expiry)
    assert_modifiable(MultiFungibleToken(_i_address).safeTransferFrom(self, _borrower, _i_id, _currency_value, EMPTY_BYTES32))
    # transfer s_lend_currency from self to _borrower
    assert_modifiable(MultiFungibleToken(self.shield_markets[_shield_market_hash].s_address).safeTransferFrom(
        self, _borrower, self.shield_markets[_shield_market_hash].s_id, _currency_value, EMPTY_BYTES32
    ))
    # transfer f_borrow_currency to _borrower
    self._transfer_f_underlying(_underlying, _expiry, self, _borrower, _underlying_value)
    # transfer lend_currency from _borrower to currency_pool
    assert_modifiable(CurrencyDao(self.daos[DAO_CURRENCY]).authorized_deposit_token(
        _currency, _borrower, _currency_value))

    return True


@public
def close_liquidated_position(
    _borrower: address, _currency_value: uint256,
    _currency: address, _expiry: timestamp, _underlying: address, _strike_price: uint256
    ) -> bool:
    assert self.initialized
    assert not self.paused
    # validate caller
    assert msg.sender == self.registries[REGISTRY_POSITION]
    # validate tokens
    _shield_market_hash: bytes32 = self._shield_market_hash(_currency, _expiry, _underlying, _strike_price)
    assert self.shield_markets[_shield_market_hash].currency == _currency
    assert self.shield_markets[_shield_market_hash].underlying == _underlying
    assert self.shield_markets[_shield_market_hash].expiry == _expiry
    assert self.shield_markets[_shield_market_hash].strike_price == _strike_price
    assert CurrencyDao(self.daos[DAO_CURRENCY]).is_token_supported(_currency)
    assert CurrencyDao(self.daos[DAO_CURRENCY]).is_token_supported(self.shield_markets[_shield_market_hash].underlying)
    _loan_market_hash: bytes32 = self._loan_market_hash(
        _currency,
        _expiry,
        _underlying
    )
    assert self.loan_markets[_loan_market_hash].status == self.LOAN_MARKET_STATUS_CLOSED
    # burn s_lend_currency from self
    assert_modifiable(MultiFungibleToken(self.shield_markets[_shield_market_hash].s_address).burn(
        self.shield_markets[_shield_market_hash].s_id,
        self, _currency_value
    ))
    # transfer f_borrow_currency to _borrower
    if as_unitless_number(self.loan_markets[_loan_market_hash].settlement_price) > self.shield_markets[_shield_market_hash].strike_price:
        _underlying_value: uint256 = as_unitless_number(_currency_value) / as_unitless_number(_strike_price)
        _underlying_value_to_transfer: uint256 = as_unitless_number(_underlying_value) * as_unitless_number(self._s_payoff(
            _currency,
            _expiry,
            _underlying,
            _strike_price
        ))
        # transfer f_borrow_currency to _borrower
        self._transfer_f_underlying(_underlying, _expiry, self, _borrower, _underlying_value_to_transfer)

    return True
