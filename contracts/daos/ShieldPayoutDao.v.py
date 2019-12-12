# Vyper version of the Lendroid protocol v2
# THIS CONTRACT HAS NOT BEEN AUDITED!


from contracts.interfaces import ERC20
from contracts.interfaces import MultiFungibleToken
from contracts.interfaces import UnderwriterPool
from contracts.interfaces import CurrencyDao
from contracts.interfaces import UnderwriterPoolDao
from contracts.interfaces import MarketDao


LST: public(address)
protocol_dao: public(address)
owner: public(address)
# dao_type => dao_address
daos: public(map(uint256, address))
# shield_market_hash => graph_address
registered_shield_markets: public(map(bytes32, bool))

DAO_TYPE_CURRENCY: public(uint256)
DAO_TYPE_UNDERWRITER_POOL: public(uint256)
DAO_TYPE_MARKET: public(uint256)

initialized: public(bool)
paused: public(bool)


@public
def initialize(
        _owner: address,
        _LST: address,
        _dao_currency: address,
        _dao_underwriter_pool: address,
        _dao_market: address
        ) -> bool:
    assert not self.initialized
    self.initialized = True
    self.owner = _owner
    self.protocol_dao = msg.sender
    self.LST = _LST

    self.DAO_TYPE_CURRENCY = 1
    self.daos[self.DAO_TYPE_CURRENCY] = _dao_currency
    self.DAO_TYPE_UNDERWRITER_POOL = 2
    self.daos[self.DAO_TYPE_UNDERWRITER_POOL] = _dao_underwriter_pool
    self.DAO_TYPE_MARKET = 3
    self.daos[self.DAO_TYPE_MARKET] = _dao_market

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
def _is_token_supported(_token: address) -> bool:
    return CurrencyDao(self.daos[self.DAO_TYPE_CURRENCY]).is_token_supported(_token)


@private
@constant
def _mft_addresses(_token: address) -> (address, address, address, address, address):
    return CurrencyDao(self.daos[self.DAO_TYPE_CURRENCY]).mft_addresses(_token)


@private
def _validate_underwriter_pool(_name: string[64], _address: address):
    assert UnderwriterPool(_address).owner() == self.daos[self.DAO_TYPE_UNDERWRITER_POOL]
    assert UnderwriterPoolDao(self.daos[self.DAO_TYPE_UNDERWRITER_POOL]).pools__address_(_name) == _address


@private
def _mint_and_self_authorize_erc20(_token: address, _to: address, _value: uint256):
    assert_modifiable(CurrencyDao(self.daos[self.DAO_TYPE_CURRENCY]).mint_and_self_authorize_erc20(_token, _to, _value))


@private
def _burn_mft(_token: address, _id: uint256, _from: address, _value: uint256):
    assert_modifiable(MultiFungibleToken(_token).burn(_id, _from, _value))


@private
@constant
def _s_payoff(_currency: address, _expiry: timestamp, _underlying: address, _strike_price: uint256) -> uint256:
    return MarketDao(self.daos[self.DAO_TYPE_MARKET]).s_payoff(_currency, _expiry, _underlying, _strike_price)


@private
@constant
def _u_payoff(_currency: address, _expiry: timestamp, _underlying: address, _strike_price: uint256) -> uint256:
    return MarketDao(self.daos[self.DAO_TYPE_MARKET]).u_payoff(_currency, _expiry, _underlying, _strike_price)


@private
def _settle_s(
    _currency: address, _expiry: timestamp, _underlying: address, _strike_price: uint256,
    _currency_quantity: uint256, _from: address, _to: address):
    # validate currency
    assert self._is_token_supported(_currency)
    # validate underlying
    assert self._is_token_supported(_underlying)
    _loan_market_hash: bytes32 = self._loan_market_hash(_currency, _expiry, _underlying)
    assert MarketDao(self.daos[self.DAO_TYPE_MARKET]).loan_markets__status(_loan_market_hash) == MarketDao(self.daos[self.DAO_TYPE_MARKET]).LOAN_MARKET_STATUS_CLOSED()
    _shield_market_hash: bytes32 = self._shield_market_hash(_currency, _expiry, _underlying, _strike_price)
    assert self.registered_shield_markets[_shield_market_hash]
    _l_address: address = ZERO_ADDRESS
    _i_address: address = ZERO_ADDRESS
    _f_address: address = ZERO_ADDRESS
    _s_address: address = ZERO_ADDRESS
    _u_address: address = ZERO_ADDRESS
    _l_address, _i_address, _f_address, _s_address, _u_address = self._mft_addresses(_currency)
    # mint _payout in l_currency
    _payout: uint256 = self._s_payoff(_currency, _expiry, _underlying, _strike_price)
    assert as_unitless_number(_payout) > 0
    # burn s_token from _from account
    self._burn_mft(
        MarketDao(self.daos[self.DAO_TYPE_MARKET]).shield_markets__s_address(_shield_market_hash),
        MarketDao(self.daos[self.DAO_TYPE_MARKET]).shield_markets__s_id(_shield_market_hash),
        _from,
        as_unitless_number(_currency_quantity) * (10 ** 18)
    )
    # mint l_token to _to account
    self._mint_and_self_authorize_erc20(_l_address, _to,
        as_unitless_number(_payout) * as_unitless_number(_currency_quantity))


@private
def _settle_u(_currency: address, _expiry: timestamp, _underlying: address, _strike_price: uint256,
    _currency_quantity: uint256, _from: address, _to: address):
    # validate currency
    assert self._is_token_supported(_currency)
    # validate underlying
    assert self._is_token_supported(_underlying)
    _loan_market_hash: bytes32 = self._loan_market_hash(_currency, _expiry, _underlying)
    assert MarketDao(self.daos[self.DAO_TYPE_MARKET]).loan_markets__status(_loan_market_hash) == MarketDao(self.daos[self.DAO_TYPE_MARKET]).LOAN_MARKET_STATUS_CLOSED()
    _shield_market_hash: bytes32 = self._shield_market_hash(_currency, _expiry, _underlying, _strike_price)
    assert self.registered_shield_markets[_shield_market_hash]
    _l_address: address = ZERO_ADDRESS
    _i_address: address = ZERO_ADDRESS
    _f_address: address = ZERO_ADDRESS
    _s_address: address = ZERO_ADDRESS
    _u_address: address = ZERO_ADDRESS
    _l_address, _i_address, _f_address, _s_address, _u_address = self._mft_addresses(_currency)
    # mint _payout in l_currency
    _payout: uint256 = self._u_payoff(_currency, _expiry, _underlying, _strike_price)
    assert as_unitless_number(_payout) > 0
    # burn s_token from _from account
    self._burn_mft(
        MarketDao(self.daos[self.DAO_TYPE_MARKET]).shield_markets__u_address(_shield_market_hash),
        MarketDao(self.daos[self.DAO_TYPE_MARKET]).shield_markets__u_id(_shield_market_hash),
        _from,
        as_unitless_number(_currency_quantity) * (10 ** 18)
    )
    # mint l_token to _to account
    self._mint_and_self_authorize_erc20(_l_address, _to,
        as_unitless_number(_payout) * as_unitless_number(_currency_quantity))


@public
@constant
def shield_market_hash(_currency: address, _expiry: timestamp, _underlying: address, _strike_price: uint256) -> bytes32:
    return self._shield_market_hash(_currency, _expiry, _underlying, _strike_price)


@public
@constant
def s_payoff(_currency: address, _expiry: timestamp, _underlying: address, _strike_price: uint256) -> uint256:
    return self._s_payoff(_currency, _expiry, _underlying, _strike_price)


@public
@constant
def u_payoff(_currency: address, _expiry: timestamp, _underlying: address, _strike_price: uint256) -> uint256:
    return self._u_payoff(_currency, _expiry, _underlying, _strike_price)



# Admin functions
@public
def register_shield_market(_currency: address, _expiry: timestamp, _underlying: address, _strike_price: uint256) -> bool:
    assert msg.sender == self.daos[self.DAO_TYPE_MARKET]
    _shield_market_hash: bytes32 = self._shield_market_hash(_currency, _expiry, _underlying, _strike_price)
    self.registered_shield_markets[_shield_market_hash] = True

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


# non-admin functions
@public
def exercise_s(_currency: address, _expiry: timestamp, _underlying: address, _strike_price: uint256,
    _quantity: uint256) -> bool:
    assert self.initialized
    assert not self.paused
    assert block.timestamp > _expiry
    _shield_market_hash: bytes32 = self._shield_market_hash(_currency, _expiry, _underlying, _strike_price)
    assert self.registered_shield_markets[_shield_market_hash]
    self._settle_s(_currency, _expiry, _underlying, _strike_price, _quantity, msg.sender, msg.sender)

    return True


@public
def exercise_u(_currency: address, _expiry: timestamp, _underlying: address, _strike_price: uint256,
    _quantity: uint256) -> bool:
    assert self.initialized
    assert not self.paused
    assert block.timestamp > _expiry
    _shield_market_hash: bytes32 = self._shield_market_hash(_currency, _expiry, _underlying, _strike_price)
    assert self.registered_shield_markets[_shield_market_hash]
    self._settle_u(_currency, _expiry, _underlying, _strike_price, _quantity, msg.sender, msg.sender)

    return True
