# Vyper version of the Lendroid protocol v2
# THIS CONTRACT HAS NOT BEEN AUDITED!


from contracts.interfaces import CurrencyDao
from contracts.interfaces import MarketDao


protocol_currency_address: public(address)
protocol_dao_address: public(address)
owner: public(address)
# dao_type => dao_address
daos: public(map(uint256, address))
# shield_market_hash => graph_address
registered_shield_markets: public(map(bytes32, bool))

DAO_TYPE_CURRENCY: public(uint256)
DAO_TYPE_UNDERWRITER_POOL: public(uint256)
DAO_TYPE_MARKET: public(uint256)

initialized: public(bool)


@private
@constant
def _is_initialized() -> bool:
    return self.initialized == True


@public
def initialize(
        _owner: address,
        _protocol_currency_address: address,
        _dao_address_currency: address,
        _dao_address_underwriter_pool: address,
        _dao_address_market: address
        ) -> bool:
    assert not self._is_initialized()
    self.initialized = True
    self.owner = _owner
    self.protocol_dao_address = msg.sender
    self.protocol_currency_address = _protocol_currency_address

    self.DAO_TYPE_CURRENCY = 1
    self.daos[self.DAO_TYPE_CURRENCY] = _dao_address_currency
    self.DAO_TYPE_UNDERWRITER_POOL = 2
    self.daos[self.DAO_TYPE_UNDERWRITER_POOL] = _dao_address_underwriter_pool
    self.DAO_TYPE_MARKET = 3
    self.daos[self.DAO_TYPE_MARKET] = _dao_address_market

    return True


@private
@constant
def _loan_market_hash(_currency_address: address, _expiry: timestamp, _underlying_address: address) -> bytes32:
    return keccak256(
        concat(
            convert(self.protocol_dao_address, bytes32),
            convert(_currency_address, bytes32),
            convert(_expiry, bytes32),
            convert(_underlying_address, bytes32)
        )
    )


@private
@constant
def _shield_market_hash(_currency_address: address, _expiry: timestamp, _underlying_address: address, _strike_price: uint256) -> bytes32:
    return keccak256(
        concat(
            convert(self.protocol_dao_address, bytes32),
            convert(_currency_address, bytes32),
            convert(_expiry, bytes32),
            convert(_underlying_address, bytes32),
            convert(_strike_price, bytes32)
        )
    )


@private
@constant
def _is_currency_valid(_currency_address: address) -> bool:
    return CurrencyDao(self.daos[self.DAO_TYPE_CURRENCY]).is_currency_valid(_currency_address)


@private
@constant
def _multi_fungible_addresses(_currency_address: address) -> (address, address, address, address, address):
    return CurrencyDao(self.daos[self.DAO_TYPE_CURRENCY]).multi_fungible_addresses(_currency_address)


@private
def _mint_and_self_authorize_erc20(_currency_address: address, _to: address, _value: uint256):
    assert_modifiable(CurrencyDao(self.daos[self.DAO_TYPE_CURRENCY]).mint_and_self_authorize_erc20(_currency_address, _to, _value))


@private
def _burn_erc1155(_currency_address: address, _id: uint256, _to: address, _value: uint256):
    assert_modifiable(CurrencyDao(self.daos[self.DAO_TYPE_CURRENCY]).burn_erc1155(_currency_address, _id, _to, _value))


@private
@constant
def _shield_payout(_currency_address: address, _expiry: timestamp, _underlying_address: address, _strike_price: uint256) -> uint256:
    return MarketDao(self.daos[self.DAO_TYPE_MARKET]).shield_payout(_currency_address, _expiry, _underlying_address, _strike_price)


@private
@constant
def _underwriter_payout(_currency_address: address, _expiry: timestamp, _underlying_address: address, _strike_price: uint256) -> uint256:
    return MarketDao(self.daos[self.DAO_TYPE_MARKET]).underwriter_payout(_currency_address, _expiry, _underlying_address, _strike_price)


@private
def _l_currency_from_s_currency(
    _currency_address: address, _expiry: timestamp, _underlying_address: address, _strike_price: uint256,
    _currency_quantity: uint256, _recipient: address):
    assert self._is_initialized()
    # validate currency
    assert self._is_currency_valid(_currency_address)
    # validate underlying
    assert self._is_currency_valid(_underlying_address)
    _loan_market_hash: bytes32 = self._loan_market_hash(_currency_address, _expiry, _underlying_address)
    assert MarketDao(self.daos[self.DAO_TYPE_MARKET]).loan_markets__status(_loan_market_hash) == MarketDao(self.daos[self.DAO_TYPE_MARKET]).LOAN_MARKET_STATUS_CLOSED()
    _shield_market_hash: bytes32 = self._shield_market_hash(_currency_address, _expiry, _underlying_address, _strike_price)
    assert self.registered_shield_markets[_shield_market_hash]
    _l_currency_address: address = ZERO_ADDRESS
    _i_currency_address: address = ZERO_ADDRESS
    _f_currency_address: address = ZERO_ADDRESS
    _s_currency_address: address = ZERO_ADDRESS
    _u_currency_address: address = ZERO_ADDRESS
    _l_currency_address, _i_currency_address, _f_currency_address, _s_currency_address, _u_currency_address = self._multi_fungible_addresses(_currency_address)
    # mint _payout_value in l_currency
    _payout_value: uint256 = self._shield_payout(_currency_address, _expiry, _underlying_address, _strike_price)
    assert as_unitless_number(_payout_value) > 0
    self._mint_and_self_authorize_erc20(_l_currency_address, _recipient,
        as_unitless_number(_payout_value) * as_unitless_number(_currency_quantity))
    # burn s_currency
    self._burn_erc1155(
        MarketDao(self.daos[self.DAO_TYPE_MARKET]).shield_markets__s_parent_address(_shield_market_hash),
        MarketDao(self.daos[self.DAO_TYPE_MARKET]).shield_markets__s_token_id(_shield_market_hash),
        _recipient,
        as_unitless_number(_currency_quantity) * (10 ** 18)
    )


@private
def _l_currency_from_u_currency(_currency_address: address, _expiry: timestamp, _underlying_address: address, _strike_price: uint256,
    _currency_quantity: uint256, _recipient: address, _pool_address: address):
    assert self._is_initialized()
    # validate currency
    assert self._is_currency_valid(_currency_address)
    # validate underlying
    assert self._is_currency_valid(_underlying_address)
    _loan_market_hash: bytes32 = self._loan_market_hash(_currency_address, _expiry, _underlying_address)
    assert MarketDao(self.daos[self.DAO_TYPE_MARKET]).loan_markets__status(_loan_market_hash) == MarketDao(self.daos[self.DAO_TYPE_MARKET]).LOAN_MARKET_STATUS_CLOSED()
    _shield_market_hash: bytes32 = self._shield_market_hash(_currency_address, _expiry, _underlying_address, _strike_price)
    assert self.registered_shield_markets[_shield_market_hash]
    _l_currency_address: address = ZERO_ADDRESS
    _i_currency_address: address = ZERO_ADDRESS
    _f_currency_address: address = ZERO_ADDRESS
    _s_currency_address: address = ZERO_ADDRESS
    _u_currency_address: address = ZERO_ADDRESS
    _l_currency_address, _i_currency_address, _f_currency_address, _s_currency_address, _u_currency_address = self._multi_fungible_addresses(_currency_address)
    # mint _payout_value in l_currency
    _payout_value: uint256 = self._underwriter_payout(_currency_address, _expiry, _underlying_address, _strike_price)
    assert as_unitless_number(_payout_value) > 0
    self._mint_and_self_authorize_erc20(_l_currency_address, _recipient,
        as_unitless_number(_payout_value) * as_unitless_number(_currency_quantity))
    # burn s_currency
    self._burn_erc1155(
        MarketDao(self.daos[self.DAO_TYPE_MARKET]).shield_markets__u_parent_address(_shield_market_hash),
        MarketDao(self.daos[self.DAO_TYPE_MARKET]).shield_markets__u_token_id(_shield_market_hash),
        _pool_address,
        as_unitless_number(_currency_quantity) * (10 ** 18)
    )


@public
@constant
def shield_market_hash(_currency_address: address, _expiry: timestamp, _underlying_address: address, _strike_price: uint256) -> bytes32:
    return self._shield_market_hash(_currency_address, _expiry, _underlying_address, _strike_price)


@public
@constant
def shield_payout(_currency_address: address, _expiry: timestamp, _underlying_address: address, _strike_price: uint256) -> uint256:
    return self._shield_payout(_currency_address, _expiry, _underlying_address, _strike_price)


@public
@constant
def underwriter_payout(_currency_address: address, _expiry: timestamp, _underlying_address: address, _strike_price: uint256) -> uint256:
    return self._underwriter_payout(_currency_address, _expiry, _underlying_address, _strike_price)



# admin functions
@public
def register_shield_market(_currency_address: address, _expiry: timestamp, _underlying_address: address, _strike_price: uint256) -> bool:
    assert msg.sender == self.daos[self.DAO_TYPE_MARKET]
    _shield_market_hash: bytes32 = self._shield_market_hash(_currency_address, _expiry, _underlying_address, _strike_price)
    self.registered_shield_markets[_shield_market_hash] = True

    return True


# non-admin functions
@public
def exercise_shield_currency(_currency_address: address, _expiry: timestamp, _underlying_address: address, _strike_price: uint256,
    _currency_quantity: uint256) -> bool:
    assert block.timestamp > _expiry
    self._l_currency_from_s_currency(_currency_address, _expiry, _underlying_address, _strike_price, _currency_quantity, msg.sender)

    return True


@public
def exercise_underwriter_currency(_currency_address: address, _expiry: timestamp, _underlying_address: address, _strike_price: uint256,
    _currency_quantity: uint256, _recipient: address, _pool_address: address) -> bool:
    assert msg.sender == self.daos[self.DAO_TYPE_UNDERWRITER_POOL]
    assert block.timestamp > _expiry
    self._l_currency_from_u_currency(_currency_address, _expiry, _underlying_address, _strike_price, _currency_quantity, _recipient, _pool_address)

    return True
