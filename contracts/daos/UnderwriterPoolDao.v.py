# Vyper version of the Lendroid protocol v2
# THIS CONTRACT HAS NOT BEEN AUDITED!


from contracts.interfaces import CurrencyDao
from contracts.interfaces import UnderwriterPool


# structs
struct Pool:
    currency_address: address
    pool_name: string[64]
    pool_address: address
    pool_operator: address
    hash: bytes32

struct MultiFungibleCurrency:
    parent_currency_address: address
    currency_address: address
    expiry_timestamp: timestamp
    underlying_address: address
    strike_price: uint256
    has_id: bool
    token_id: uint256
    hash: bytes32

struct OfferRegistrationFeeLookup:
    minimum_fee: uint256
    minimum_interval: timestamp
    fee_multiplier: uint256
    fee_multiplier_decimals: uint256
    last_registered_at: timestamp
    last_paid_fee: uint256

protocol_currency_address: public(address)
protocol_dao_address: public(address)
owner: public(address)
# dao_type => dao_address
daos: public(map(uint256, address))
# template_name => template_contract_address
templates: public(map(uint256, address))
# pool_hash => Pool
pools: public(map(bytes32, Pool))
# currency_hash => MultiFungibleCurrency
multi_fungible_currencies: public(map(bytes32, MultiFungibleCurrency))
# lookup_key => lookup_value
offer_registration_fee_lookup: public(map(address, OfferRegistrationFeeLookup))
# currency_hash => quantity per currency_address
shield_currency_prices: public(map(bytes32, uint256))

DAO_TYPE_CURRENCY: public(uint256)

TEMPLATE_TYPE_UNDERWRITER_POOL: public(uint256)
TEMPLATE_TYPE_CURRENCY_ERC20: public(uint256)


@public
def initialize(
        _owner: address,
        _protocol_currency_address: address,
        _dao_address_currency: address,
        _template_address_underwriter_pool: address,
        _template_address_currency_erc20: address,
        ) -> bool:
    self.owner = _owner
    self.protocol_dao_address = msg.sender
    self.protocol_currency_address = _protocol_currency_address

    self.DAO_TYPE_CURRENCY = 1
    self.daos[self.DAO_TYPE_CURRENCY] = _dao_address_currency

    self.TEMPLATE_TYPE_UNDERWRITER_POOL = 1
    self.TEMPLATE_TYPE_CURRENCY_ERC20 = 2
    self.templates[self.TEMPLATE_TYPE_UNDERWRITER_POOL] = _template_address_underwriter_pool
    self.templates[self.TEMPLATE_TYPE_CURRENCY_ERC20] = _template_address_currency_erc20

    return True


@private
@constant
def _pool_hash(_currency_address: address, _pool_address: address) -> bytes32:
    return keccak256(
        concat(
            convert(self.protocol_dao_address, bytes32),
            convert(_currency_address, bytes32),
            convert(_pool_address, bytes32)
        )
    )


@private
@constant
def _multi_fungible_currency_hash(parent_currency_address: address, _currency_address: address, _expiry: timestamp, _underlying_address: address, _strike_price: uint256) -> bytes32:
    return keccak256(
        concat(
            convert(self, bytes32),
            convert(parent_currency_address, bytes32),
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
def _validate_pool(_pool_hash: bytes32, _pool_address: address):
    assert self.pools[_pool_hash].pool_address == _pool_address


@private
def _deposit_multi_fungible_l_currency(_currency_address: address, _from: address, _to: address, _value: uint256):
    _external_call_successful: bool = CurrencyDao(self.daos[self.DAO_TYPE_CURRENCY]).deposit_multi_fungible_l_currency(
        _currency_address, _from, _to, _value)
    assert _external_call_successful


@private
def _deposit_erc20(_currency_address: address, _from: address, _to: address, _value: uint256):
    _external_call_successful: bool = CurrencyDao(self.daos[self.DAO_TYPE_CURRENCY]).deposit_erc20(
        _currency_address, _from, _to, _value)
    assert _external_call_successful


@private
def _create_erc1155_type(_currency_address: address, _expiry_label: string[3]) -> uint256:
    return CurrencyDao(self.daos[self.DAO_TYPE_CURRENCY]).create_erc1155_type(_currency_address, _expiry_label)


@private
def _mint_and_self_authorize_erc20(_currency_address: address, _to: address, _value: uint256):
    _external_call_successful: bool = CurrencyDao(self.daos[self.DAO_TYPE_CURRENCY]).mint_and_self_authorize_erc20(_currency_address, _to, _value)
    assert _external_call_successful


@private
def _burn_as_self_authorized_erc20(_currency_address: address, _to: address, _value: uint256):
    _external_call_successful: bool = CurrencyDao(self.daos[self.DAO_TYPE_CURRENCY]).burn_as_self_authorized_erc20(_currency_address, _to, _value)
    assert _external_call_successful


@private
def _mint_erc1155(_currency_address: address, _id: uint256, _to: address, _value: uint256):
    _external_call_successful: bool = CurrencyDao(self.daos[self.DAO_TYPE_CURRENCY]).mint_erc1155(_currency_address, _id, _to, _value)
    assert _external_call_successful


@private
def _burn_erc1155(_currency_address: address, _id: uint256, _to: address, _value: uint256):
    _external_call_successful: bool = CurrencyDao(self.daos[self.DAO_TYPE_CURRENCY]).burn_erc1155(_currency_address, _id, _to, _value)
    assert _external_call_successful


@private
@constant
def _duration_since_last_offer_registration() -> uint256:
    return as_unitless_number(block.timestamp - self.offer_registration_fee_lookup[self].last_registered_at)


@private
@constant
def _offer_registration_fee() -> uint256:
    if self._duration_since_last_offer_registration() >= self.offer_registration_fee_lookup[self].minimum_interval:
        return self.offer_registration_fee_lookup[self].minimum_fee
    else:
        return as_unitless_number(self.offer_registration_fee_lookup[self].last_paid_fee) * as_unitless_number(self.offer_registration_fee_lookup[self].fee_multiplier) / self.offer_registration_fee_lookup[self].fee_multiplier_decimals


@private
def _process_fee_for_offer_creation(_from: address):
    _fee_amount: uint256 = self._offer_registration_fee()
    if as_unitless_number(_fee_amount) > 0:
        self._deposit_erc20(self.protocol_currency_address, _from, self, _fee_amount)


# admin functions
@public
def set_offer_registration_fee_lookup(_fee_multiplier: uint256,
    _minimum_fee: uint256, _fee_multiplier_decimals: uint256,
    _minimum_interval: timestamp, _last_registered_at: timestamp, _last_paid_fee: uint256
    ) -> bool:
    assert msg.sender == self.owner or msg.sender == self.protocol_dao_address
    self.offer_registration_fee_lookup[self] = OfferRegistrationFeeLookup({
        minimum_fee: _minimum_fee,
        minimum_interval: _minimum_interval,
        fee_multiplier: _fee_multiplier,
        fee_multiplier_decimals: _fee_multiplier_decimals,
        last_registered_at: _last_registered_at,
        last_paid_fee: _last_paid_fee
    })
    return True


@public
def set_shield_currency_price(_currency_address: address, _expiry: timestamp, _underlying_address: address, _strike_price: uint256, _price: uint256) -> bool:
    assert msg.sender == self.owner or msg.sender == self.protocol_dao_address
    _l_currency_address: address = ZERO_ADDRESS
    _i_currency_address: address = ZERO_ADDRESS
    _f_currency_address: address = ZERO_ADDRESS
    _s_currency_address: address = ZERO_ADDRESS
    _u_currency_address: address = ZERO_ADDRESS
    _l_currency_address, _i_currency_address, _f_currency_address, _s_currency_address, _u_currency_address = self._multi_fungible_addresses(_currency_address)
    _s_hash: bytes32 = self._multi_fungible_currency_hash(_s_currency_address, _currency_address, _expiry, _underlying_address, _strike_price)
    self.shield_currency_prices[_s_hash] = _price

    return True


@public
def set_template(_template_type: uint256, _address: address) -> bool:
    assert msg.sender == self.owner or msg.sender == self.protocol_dao_address
    assert _template_type == self.TEMPLATE_TYPE_UNDERWRITER_POOL
    self.templates[_template_type] = _address
    return True


@public
def register_pool( _currency_address: address, _name: string[62], _symbol: string[32], _initial_exchange_rate: uint256) -> bytes32:
    # validate currency
    assert self._is_currency_valid(_currency_address)
    # initialize pool
    _pool_address: address = ZERO_ADDRESS
    _l_currency_address: address = ZERO_ADDRESS
    _i_currency_address: address = ZERO_ADDRESS
    _f_currency_address: address = ZERO_ADDRESS
    _s_currency_address: address = ZERO_ADDRESS
    _u_currency_address: address = ZERO_ADDRESS
    _external_call_successful: bool = False
    _pool_hash: bytes32 = EMPTY_BYTES32
    _pool_address = create_forwarder_to(self.templates[self.TEMPLATE_TYPE_UNDERWRITER_POOL])
    assert _pool_address.is_contract
    _l_currency_address, _i_currency_address, _f_currency_address, _s_currency_address, _u_currency_address = self._multi_fungible_addresses(_currency_address)
    _pool_hash = self._pool_hash(_currency_address, _pool_address)
    _external_call_successful = UnderwriterPool(_pool_address).initialize(
        _pool_hash, msg.sender,
        _name, _symbol, _initial_exchange_rate,
        _currency_address,
        _l_currency_address,
        _i_currency_address,
        _s_currency_address,
        _u_currency_address,
        self.templates[self.TEMPLATE_TYPE_CURRENCY_ERC20])
    assert _external_call_successful

    # save pool metadata
    self.pools[_pool_hash] = Pool({
        currency_address: _currency_address,
        pool_name: _name,
        pool_address: _pool_address,
        pool_operator: msg.sender,
        hash: _pool_hash
    })

    return _pool_hash


@public
def deposit_l_currency(_pool_hash: bytes32, _from: address, _value: uint256) -> bool:
    self._validate_pool(_pool_hash, msg.sender)
    # validate currency
    assert self._is_currency_valid(self.pools[_pool_hash].currency_address)
    self._deposit_multi_fungible_l_currency(self.pools[_pool_hash].currency_address, _from, msg.sender, _value)

    return True


@public
def register_expiry(_pool_hash: bytes32, _expiry: timestamp, _underlying_address: address, _strike_price: uint256) -> (bool, bytes32, bytes32, bytes32, uint256, uint256, uint256):
    self._validate_pool(_pool_hash, msg.sender)
    _currency_address: address = self.pools[_pool_hash].currency_address
    assert self._is_currency_valid(_currency_address)
    _l_currency_address: address = ZERO_ADDRESS
    _i_currency_address: address = ZERO_ADDRESS
    _f_currency_address: address = ZERO_ADDRESS
    _s_currency_address: address = ZERO_ADDRESS
    _u_currency_address: address = ZERO_ADDRESS
    _l_currency_address, _i_currency_address, _f_currency_address, _s_currency_address, _u_currency_address = self._multi_fungible_addresses(_currency_address)
    _i_hash: bytes32 = self._multi_fungible_currency_hash(_i_currency_address, _currency_address, _expiry, ZERO_ADDRESS, 0)
    _s_hash: bytes32 = self._multi_fungible_currency_hash(_s_currency_address, _currency_address, _expiry, _underlying_address, _strike_price)
    _u_hash: bytes32 = self._multi_fungible_currency_hash(_u_currency_address, _currency_address, _expiry, _underlying_address, _strike_price)
    _i_id: uint256 = self.multi_fungible_currencies[_i_hash].token_id
    _s_id: uint256 = self.multi_fungible_currencies[_s_hash].token_id
    _u_id: uint256 = self.multi_fungible_currencies[_u_hash].token_id
    # pay lst as fee to create fi currency if it has not been created
    if not self.multi_fungible_currencies[_i_hash].has_id or \
       not self.multi_fungible_currencies[_s_hash].has_id or \
       not self.multi_fungible_currencies[_u_hash].has_id:
       self._process_fee_for_offer_creation(self.pools[_pool_hash].pool_operator)

    if not self.multi_fungible_currencies[_i_hash].has_id:
        _i_id = self._create_erc1155_type(_i_currency_address, "")
        self.multi_fungible_currencies[_i_hash] = MultiFungibleCurrency({
            parent_currency_address: _i_currency_address,
            currency_address: _currency_address,
            expiry_timestamp: _expiry,
            underlying_address: ZERO_ADDRESS,
            strike_price: 0,
            has_id: True,
            token_id: _i_id,
            hash: _i_hash
        })
    if not self.multi_fungible_currencies[_s_hash].has_id:
        _s_id = self._create_erc1155_type(_s_currency_address, "")
        self.multi_fungible_currencies[_s_hash] = MultiFungibleCurrency({
            parent_currency_address: _s_currency_address,
            currency_address: _currency_address,
            expiry_timestamp: _expiry,
            underlying_address: _underlying_address,
            strike_price: _strike_price,
            has_id: True,
            token_id: _s_id,
            hash: _s_hash
        })
    if not self.multi_fungible_currencies[_u_hash].has_id:
        _u_id = self._create_erc1155_type(_u_currency_address, "")
        self.multi_fungible_currencies[_u_hash] = MultiFungibleCurrency({
            parent_currency_address: _u_currency_address,
            currency_address: _currency_address,
            expiry_timestamp: _expiry,
            underlying_address: _underlying_address,
            strike_price: _strike_price,
            has_id: True,
            token_id: _u_id,
            hash: _u_hash
        })

    return True, _i_hash, _s_hash, _u_hash, _i_id, _s_id, _u_id


@public
def l_currency_to_i_and_s_and_u_currency(_pool_hash: bytes32, _s_hash: bytes32, _u_hash: bytes32, _i_hash: bytes32, _value: uint256) -> bool:
    self._validate_pool(_pool_hash, msg.sender)
    _currency_address: address = self.pools[_pool_hash].currency_address
    assert self._is_currency_valid(_currency_address)
    # validate i, s, and u token types exists for combination of expiry, underlying, and strike
    assert self.multi_fungible_currencies[_s_hash].has_id and \
           self.multi_fungible_currencies[_u_hash].has_id and \
           self.multi_fungible_currencies[_i_hash].has_id and \
           self.multi_fungible_currencies[_s_hash].currency_address == _currency_address and \
           self.multi_fungible_currencies[_u_hash].currency_address == _currency_address and \
           self.multi_fungible_currencies[_i_hash].currency_address == _currency_address and \
           self.multi_fungible_currencies[_s_hash].underlying_address == self.multi_fungible_currencies[_u_hash].underlying_address
    # validate underlying
    assert self._is_currency_valid(self.multi_fungible_currencies[_s_hash].underlying_address)
    _l_currency_address: address = ZERO_ADDRESS
    _i_currency_address: address = ZERO_ADDRESS
    _f_currency_address: address = ZERO_ADDRESS
    _s_currency_address: address = ZERO_ADDRESS
    _u_currency_address: address = ZERO_ADDRESS
    _l_currency_address, _i_currency_address, _f_currency_address, _s_currency_address, _u_currency_address = self._multi_fungible_addresses(_currency_address)
    # burn l_token from interest_pool account
    self._burn_as_self_authorized_erc20(_l_currency_address, msg.sender, _value)
    # calculate su currency quantitites to be minted
    assert not as_unitless_number(self.shield_currency_prices[_s_hash]) == 0, "shield price has not been set"
    _su_currencies_to_mint: uint256 = as_unitless_number(_value) / as_unitless_number(self.shield_currency_prices[_s_hash])
    # mint i_token into interest_pool account
    self._mint_erc1155(
        _i_currency_address,
        self.multi_fungible_currencies[_i_hash].token_id,
        msg.sender,
        _value
    )
    self._mint_erc1155(
        _s_currency_address,
        self.multi_fungible_currencies[_s_hash].token_id,
        msg.sender,
        _su_currencies_to_mint
    )
    self._mint_erc1155(
        _u_currency_address,
        self.multi_fungible_currencies[_u_hash].token_id,
        msg.sender,
        _su_currencies_to_mint
    )

    return True


@public
def l_currency_from_i_and_s_and_u_currency(_pool_hash: bytes32, _s_hash: bytes32, _u_hash: bytes32, _i_hash: bytes32, _value: uint256) -> bool:
    self._validate_pool(_pool_hash, msg.sender)
    _currency_address: address = self.pools[_pool_hash].currency_address
    assert self._is_currency_valid(_currency_address)
    # validate i, s, and u token types exists for combination of expiry, underlying, and strike
    assert self.multi_fungible_currencies[_s_hash].has_id and \
           self.multi_fungible_currencies[_u_hash].has_id and \
           self.multi_fungible_currencies[_i_hash].has_id and \
           self.multi_fungible_currencies[_s_hash].currency_address == _currency_address and \
           self.multi_fungible_currencies[_u_hash].currency_address == _currency_address and \
           self.multi_fungible_currencies[_i_hash].currency_address == _currency_address and \
           self.multi_fungible_currencies[_s_hash].underlying_address == self.multi_fungible_currencies[_u_hash].underlying_address
    # validate underlying
    assert self._is_currency_valid(self.multi_fungible_currencies[_s_hash].underlying_address)
    _l_currency_address: address = ZERO_ADDRESS
    _i_currency_address: address = ZERO_ADDRESS
    _f_currency_address: address = ZERO_ADDRESS
    _s_currency_address: address = ZERO_ADDRESS
    _u_currency_address: address = ZERO_ADDRESS
    _l_currency_address, _i_currency_address, _f_currency_address, _s_currency_address, _u_currency_address = self._multi_fungible_addresses(_currency_address)
    # burn l_token from interest_pool account
    self._mint_and_self_authorize_erc20(_l_currency_address, msg.sender, _value)
    # calculate su currency quantitites to be minted
    assert not as_unitless_number(self.shield_currency_prices[_s_hash]) == 0, "shield price has not been set"
    _su_currencies_to_burn: uint256 = as_unitless_number(_value) / as_unitless_number(self.shield_currency_prices[_s_hash])
    # mint i_token into interest_pool account
    self._burn_erc1155(
        _s_currency_address,
        self.multi_fungible_currencies[_s_hash].token_id,
        msg.sender,
        _su_currencies_to_burn
    )
    self._burn_erc1155(
        _u_currency_address,
        self.multi_fungible_currencies[_u_hash].token_id,
        msg.sender,
        _su_currencies_to_burn
    )
    self._burn_erc1155(
        _i_currency_address,
        self.multi_fungible_currencies[_i_hash].token_id,
        msg.sender,
        _value
    )

    return True
