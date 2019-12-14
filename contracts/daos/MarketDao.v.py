# Vyper version of the Lendroid protocol v2
# THIS CONTRACT HAS NOT BEEN AUDITED!


from contracts.interfaces import ERC20
from contracts.interfaces import MultiFungibleToken
from contracts.interfaces import MultiFungibleTokenReceiver
from contracts.interfaces import CurrencyDao
from contracts.interfaces import ShieldPayoutDao
from contracts.interfaces import CollateralAuctionCurve
from contracts.interfaces import SimplePriceOracle


implements: MultiFungibleTokenReceiver


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
owner: public(address)
# dao_type => dao_address
daos: public(map(uint256, address))
# registry_type => registry_address
registries: public(map(uint256, address))
# template_name => template_contract_address
templates: public(map(uint256, address))
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

REGISTRY_TYPE_POSITION: public(uint256)

DAO_TYPE_CURRENCY: public(uint256)
DAO_TYPE_INTEREST_POOL: public(uint256)
DAO_TYPE_UNDERWRITER_POOL: public(uint256)
DAO_TYPE_SHIELD_PAYOUT: public(uint256)

TEMPLATE_TYPE_AUCTION_ERC20: public(uint256)

LOAN_MARKET_STATUS_OPEN: public(uint256)
LOAN_MARKET_STATUS_SETTLING: public(uint256)
LOAN_MARKET_STATUS_CLOSED: public(uint256)

# MultiFungibleTokenReceiver interface variables
shouldReject: public(bool)
lastData: public(bytes32)
lastOperator: public(address)
lastFrom: public(address)
lastId: public(uint256)
lastValue: public(uint256)
MFT_ACCEPTED: bytes[10]

initialized: public(bool)
paused: public(bool)


@public
def initialize(
        _owner: address,
        _LST: address,
        _dao_currency: address,
        _dao_interest_pool: address,
        _dao_underwriter_pool: address,
        _dao_shield_payout: address,
        _registry_position: address,
        _template_auction_erc20: address) -> bool:
    assert not self.initialized
    self.initialized = True
    self.owner = _owner
    self.protocol_dao = msg.sender
    self.LST = _LST

    self.REGISTRY_TYPE_POSITION = 1
    self.registries[self.REGISTRY_TYPE_POSITION] = _registry_position

    self.DAO_TYPE_CURRENCY = 1
    self.daos[self.DAO_TYPE_CURRENCY] = _dao_currency
    self.DAO_TYPE_INTEREST_POOL = 2
    self.daos[self.DAO_TYPE_INTEREST_POOL] = _dao_interest_pool
    self.DAO_TYPE_UNDERWRITER_POOL = 3
    self.daos[self.DAO_TYPE_UNDERWRITER_POOL] = _dao_underwriter_pool
    self.DAO_TYPE_SHIELD_PAYOUT = 4
    self.daos[self.DAO_TYPE_SHIELD_PAYOUT] = _dao_shield_payout

    self.TEMPLATE_TYPE_AUCTION_ERC20 = 1
    self.templates[self.TEMPLATE_TYPE_AUCTION_ERC20] = _template_auction_erc20

    self.LOAN_MARKET_STATUS_OPEN = 1
    self.LOAN_MARKET_STATUS_SETTLING = 2
    self.LOAN_MARKET_STATUS_CLOSED = 3

    # bytes4(keccak256("onMFTReceived(address,address,uint256,uint256,bytes)"))
    self.MFT_ACCEPTED = "0xf23a6e61"
    self.shouldReject = False

    return True


@private
@constant
def _mft_hash(_address: address, _currency: address, _expiry: timestamp, _underlying: address, _strike_price: uint256) -> bytes32:
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
def _loan_market_hash(_currency: address, _expiry: timestamp, _underlying: address) -> bytes32:
    return self._shield_market_hash(_currency, _expiry, _underlying, 0)


@private
@constant
def _currency_underlying_pair_hash(_currency: address, _underlying: address) -> bytes32:
    return keccak256(
        concat(
            convert(self.protocol_dao, bytes32),
            convert(_currency, bytes32),
            convert(_underlying, bytes32)
        )
    )


@private
@constant
def _is_token_supported(_token: address) -> bool:
    return CurrencyDao(self.daos[self.DAO_TYPE_CURRENCY]).is_token_supported(_token)


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
def _authorized_withdraw_token(_token: address, _to: address, _value: uint256):
    assert_modifiable(CurrencyDao(self.daos[self.DAO_TYPE_CURRENCY]).authorized_withdraw_token(
        _token, _to, _value))


@private
def _authorized_deposit_token(_token: address, _from: address, _value: uint256):
    assert_modifiable(CurrencyDao(self.daos[self.DAO_TYPE_CURRENCY]).authorized_deposit_token(
        _token, _from, _value))


@private
def _mint_mft(_token: address, _id: uint256, _to: address, _value: uint256):
    assert_modifiable(MultiFungibleToken(_token).mint(_id, _to, _value))


@private
def _burn_mft(_token: address, _id: uint256, _from: address, _value: uint256):
    assert_modifiable(MultiFungibleToken(_token).burn(_id, _from, _value))


@private
def _transfer_mft(_from: address, _to: address, _token: address, _id: uint256, _value: uint256):
    assert_modifiable(MultiFungibleToken(_token).safeTransferFrom(_from, _to, _id, _value, EMPTY_BYTES32))


@private
def _mint_f(_currency: address, _expiry: timestamp, _to: address, _value: uint256):
    _token: address = CurrencyDao(self.daos[self.DAO_TYPE_CURRENCY]).token_addresses__f(_currency)
    assert not _token == ZERO_ADDRESS
    _id: uint256 = MultiFungibleToken(_token).id(_currency, _expiry, ZERO_ADDRESS, 0)
    assert not _id == 0
    self._mint_mft(_token, _id, _to, _value)


@private
def _burn_f(_currency: address, _expiry: timestamp, _from: address, _value: uint256):
    _token: address = CurrencyDao(self.daos[self.DAO_TYPE_CURRENCY]).token_addresses__f(_currency)
    assert not _token == ZERO_ADDRESS
    _id: uint256 = MultiFungibleToken(_token).id(_currency, _expiry, ZERO_ADDRESS, 0)
    assert not _id == 0
    self._burn_mft(_token, _id, _from, _value)


@private
def _transfer_f(_currency: address, _expiry: timestamp, _from: address, _to: address, _value: uint256):
    _token: address = CurrencyDao(self.daos[self.DAO_TYPE_CURRENCY]).token_addresses__f(_currency)
    assert not _token == ZERO_ADDRESS
    _id: uint256 = MultiFungibleToken(_token).id(_currency, _expiry, ZERO_ADDRESS, 0)
    assert not _id == 0
    self._transfer_mft(_from, _to, _token, _id, _value)



# START of MultiFungibleTokenReceiver interface functions
@public
def setShouldReject(_value: bool):
    assert msg.sender == self.owner
    self.shouldReject = _value


@public
@constant
def supportsInterface(interfaceID: bytes[10]) -> bool:
    # ERC165 or MFT_ACCEPTED
    return interfaceID == "0x01ffc9a7" or interfaceID == "0x4e2312e0"


@public
def onMFTReceived(_operator: address, _from: address, _id: uint256, _value: uint256, _data: bytes32) -> bytes[10]:
    self.lastOperator = _operator
    self.lastFrom = _from
    self.lastId = _id
    self.lastValue = _value
    self.lastData = _data
    if self.shouldReject:
        raise("onMFTReceived: transfer not accepted")
    else:
        return self.MFT_ACCEPTED


# END of MultiFungibleTokenReceiver interface functions


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
        _auction: address = create_forwarder_to(self.templates[self.TEMPLATE_TYPE_AUCTION_ERC20])
        assert _auction.is_contract
        self.loan_markets[_loan_market_hash].auction_curve = _auction
        self.loan_markets[_loan_market_hash].status = self.LOAN_MARKET_STATUS_SETTLING
        # start collateral auction
        assert_modifiable(CollateralAuctionCurve(_auction).start(
            self.loan_markets[_loan_market_hash].currency,
            self.loan_markets[_loan_market_hash].expiry,
            self.loan_markets[_loan_market_hash].underlying,
            self.loan_markets[_loan_market_hash].settlement_price,
            self.loan_markets[_loan_market_hash].liability,
            self.loan_markets[_loan_market_hash].collateral,
            self.daos[self.DAO_TYPE_CURRENCY]
        ))
        # burn outstanding_value of underlying f_tokens
        self._burn_f(
            self.loan_markets[_loan_market_hash].underlying,
            self.loan_markets[_loan_market_hash].expiry,
            self,
            self.loan_markets[_loan_market_hash].collateral
        )
        # send oustanding_value of underlying to auction contract
        self._authorized_withdraw_token(
            self.loan_markets[_loan_market_hash].underlying,
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
    assert_modifiable(ShieldPayoutDao(self.daos[self.DAO_TYPE_SHIELD_PAYOUT]).register_shield_market(
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
def loan_market_hash(_currency: address, _expiry: timestamp, _underlying: address) -> bytes32:
    return self._loan_market_hash(_currency, _expiry, _underlying)


@public
@constant
def currency_underlying_pair_hash(_currency: address, _underlying: address) -> bytes32:
    return self._currency_underlying_pair_hash(_currency, _underlying)


# Admin functions


@public
def set_registry(_registry_type: uint256, _address: address) -> bool:
    assert self.initialized
    assert msg.sender == self.owner
    assert _registry_type == self.REGISTRY_TYPE_POSITION
    self.registries[_registry_type] = _address
    return True


@public
def set_price_oracle(_currency: address, _underlying: address, _oracle: address) -> bool:
    assert self.initialized
    assert msg.sender == self.owner
    assert _currency.is_contract
    assert _underlying.is_contract
    assert _oracle.is_contract
    _currency_underlying_pair_hash: bytes32 = self._currency_underlying_pair_hash(_currency, _underlying)
    self.price_oracles[_currency_underlying_pair_hash] = _oracle

    return True


# Escape-hatches

@private
def _pause():
    assert not self.paused
    self.paused = True


@private
def _unpause():
    assert self.paused
    self.paused = False

@public
def pause() -> bool:
    assert self.initialized
    assert msg.sender == self.owner
    self._pause()
    return True


@public
def unpause() -> bool:
    assert self.initialized
    assert msg.sender == self.owner
    self._unpause()
    return True


@private
def _transfer_balance_erc20(_token: address):
    assert_modifiable(ERC20(_token).transfer(self.owner, ERC20(_token).balanceOf(self)))


@private
def _transfer_balance_mft(_token: address,
    _currency: address, _expiry: timestamp, _underlying: address, _strike_price: uint256):
    _mft_hash: bytes32 = self._mft_hash(_token, _currency, _expiry, _underlying, _strike_price)
    _id: uint256 = MultiFungibleToken(_token).hash_to_id(_mft_hash)
    _balance: uint256 = MultiFungibleToken(_token).balanceOf(self, _id)
    assert_modifiable(MultiFungibleToken(_token).safeTransferFrom(self, self.owner, _id, _balance, EMPTY_BYTES32))


@public
def escape_hatch_auction(_currency: address, _expiry: timestamp, _underlying: address) -> bool:
    assert self.initialized
    assert msg.sender == self.owner
    _loan_market_hash: bytes32 = self._loan_market_hash(_currency, _expiry, _underlying)
    assert_modifiable(CollateralAuctionCurve(self.loan_markets[_loan_market_hash].auction_curve).escape_hatch_underlying())
    return True


@public
def escape_hatch_erc20(_currency: address, _is_l: bool) -> bool:
    assert self.initialized
    assert msg.sender == self.owner
    _token: address = _currency
    if _is_l:
        CurrencyDao(self.daos[self.DAO_TYPE_CURRENCY]).token_addresses__l(_currency)
    self._transfer_balance_erc20(_currency)
    return True


@public
def escape_hatch_sufi(_sufi_type: int128, _currency: address, _expiry: timestamp, _underlying: address, _strike_price: uint256) -> bool:
    assert self.initialized
    assert msg.sender == self.owner
    _token: address = ZERO_ADDRESS
    if _sufi_type == 1:
        CurrencyDao(self.daos[self.DAO_TYPE_CURRENCY]).token_addresses__f(_currency)
    if _sufi_type == 2:
        CurrencyDao(self.daos[self.DAO_TYPE_CURRENCY]).token_addresses__i(_currency)
    if _sufi_type == 3:
        CurrencyDao(self.daos[self.DAO_TYPE_CURRENCY]).token_addresses__s(_currency)
    if _sufi_type == 4:
        CurrencyDao(self.daos[self.DAO_TYPE_CURRENCY]).token_addresses__u(_currency)
    assert not _token == ZERO_ADDRESS
    self._transfer_balance_mft(_token, _currency, _expiry, _underlying, _strike_price)
    return True


# Non-admin functions


@public
def open_shield_market(_currency: address, _expiry: timestamp, _underlying: address, _strike_price: uint256,
    _s_address: address, _s_id: uint256,
    _u_address: address, _u_id: uint256) -> bool:
    assert self.initialized
    assert msg.sender == self.daos[self.DAO_TYPE_UNDERWRITER_POOL]
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
    self._authorized_deposit_token(_currency, _purchaser, _currency_value)
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
    assert msg.sender == self.registries[self.REGISTRY_TYPE_POSITION]
    _shield_market_hash: bytes32 = self._shield_market_hash(_currency, _expiry, _underlying, _strike_price)
    assert self.shield_markets[_shield_market_hash].currency == _currency
    assert self.shield_markets[_shield_market_hash].underlying == _underlying
    assert self.shield_markets[_shield_market_hash].expiry == _expiry
    assert self.shield_markets[_shield_market_hash].strike_price == _strike_price
    # validate tokens
    assert self._is_token_supported(_currency)
    assert self._is_token_supported(_underlying)
    _loan_market_hash: bytes32 = self._loan_market_hash(
        _currency,
        _expiry,
        _underlying
    )
    assert self.loan_markets[_loan_market_hash].status == self.LOAN_MARKET_STATUS_OPEN
    _underlying_value: uint256 = as_unitless_number(_currency_value) / as_unitless_number(_strike_price)
    self.loan_markets[_loan_market_hash].liability += _currency_value
    self.loan_markets[_loan_market_hash].collateral += _underlying_value
    # transfer i_lend_currency from _borrower to self
    _i_address: address = ZERO_ADDRESS
    _i_id: uint256 = 0
    _i_address, _i_id = CurrencyDao(self.daos[self.DAO_TYPE_CURRENCY]).i_token(_currency, _expiry)
    self._transfer_mft(
        _borrower,
        self,
        _i_address,
        _i_id,
        _currency_value
    )
    # transfer s_lend_currency from _borrower to self
    self._transfer_mft(
        _borrower,
        self,
        self.shield_markets[_shield_market_hash].s_address,
        self.shield_markets[_shield_market_hash].s_id,
        _currency_value
    )
    # transfer f_borrow_currency from borrower to self
    self._transfer_f(_underlying, _expiry, _borrower, self, _underlying_value)
    # transfer lend_currency to _borrower
    self._authorized_withdraw_token(
        _currency, _borrower, _currency_value)

    return True


@public
def close_position(
    _borrower: address, _currency_value: uint256,
    _currency: address, _expiry: timestamp, _underlying: address, _strike_price: uint256
    ) -> bool:
    assert self.initialized
    assert not self.paused
    # validate caller
    assert msg.sender == self.registries[self.REGISTRY_TYPE_POSITION]
    _shield_market_hash: bytes32 = self._shield_market_hash(_currency, _expiry, _underlying, _strike_price)
    assert self.shield_markets[_shield_market_hash].currency == _currency
    assert self.shield_markets[_shield_market_hash].underlying == _underlying
    assert self.shield_markets[_shield_market_hash].expiry == _expiry
    assert self.shield_markets[_shield_market_hash].strike_price == _strike_price
    # validate tokens
    assert self._is_token_supported(_currency)
    assert self._is_token_supported(_underlying)
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
    _i_address, _i_id = CurrencyDao(self.daos[self.DAO_TYPE_CURRENCY]).i_token(_currency, _expiry)
    self._transfer_mft(
        self,
        _borrower,
        _i_address,
        _i_id,
        _currency_value
    )
    # transfer s_lend_currency from self to _borrower
    self._transfer_mft(
        self,
        _borrower,
        self.shield_markets[_shield_market_hash].s_address,
        self.shield_markets[_shield_market_hash].s_id,
        _currency_value
    )
    # transfer f_borrow_currency to _borrower
    self._transfer_f(_underlying, _expiry, self, _borrower, _underlying_value)
    # transfer lend_currency from _borrower to currency_pool
    self._authorized_deposit_token(
        _currency, _borrower, _currency_value)

    return True


@public
def close_liquidated_position(
    _borrower: address, _currency_value: uint256,
    _currency: address, _expiry: timestamp, _underlying: address, _strike_price: uint256
    ) -> bool:
    assert self.initialized
    assert not self.paused
    # validate caller
    assert msg.sender == self.registries[self.REGISTRY_TYPE_POSITION]
    # validate tokens
    _shield_market_hash: bytes32 = self._shield_market_hash(_currency, _expiry, _underlying, _strike_price)
    assert self.shield_markets[_shield_market_hash].currency == _currency
    assert self.shield_markets[_shield_market_hash].underlying == _underlying
    assert self.shield_markets[_shield_market_hash].expiry == _expiry
    assert self.shield_markets[_shield_market_hash].strike_price == _strike_price
    assert self._is_token_supported(_currency)
    assert self._is_token_supported(self.shield_markets[_shield_market_hash].underlying)
    _loan_market_hash: bytes32 = self._loan_market_hash(
        _currency,
        _expiry,
        _underlying
    )
    assert self.loan_markets[_loan_market_hash].status == self.LOAN_MARKET_STATUS_CLOSED
    # burn s_lend_currency from self
    self._burn_mft(
        self.shield_markets[_shield_market_hash].s_address,
        self.shield_markets[_shield_market_hash].s_id,
        self,
        _currency_value
    )
    # transfer l_borrow_currency to _borrower
    if as_unitless_number(self.loan_markets[_loan_market_hash].settlement_price) > self.shield_markets[_shield_market_hash].strike_price:
        _underlying_value: uint256 = as_unitless_number(_currency_value) / as_unitless_number(_strike_price)
        _underlying_value_to_transfer: uint256 = as_unitless_number(_underlying_value) * as_unitless_number(self._s_payoff(
            _currency,
            _expiry,
            _underlying,
            _strike_price
        ))
        self._mint_f(_underlying, _expiry, _borrower, _underlying_value_to_transfer)

    return True
