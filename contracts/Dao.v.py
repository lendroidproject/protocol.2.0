# Vyper version of the Lendroid protocol v2
# THIS CONTRACT HAS NOT BEEN AUDITED!


from contracts.interfaces import ERC20
from contracts.interfaces import ERC1155
from contracts.interfaces import ContinuousCurrencyPoolERC20
from contracts.interfaces import InterestPool
from contracts.interfaces import UnderwriterPool


# Structs
struct Currency:
    currency_address: address
    l_currency_address: address
    i_currency_address: address
    f_currency_address: address
    s_currency_address: address
    u_currency_address: address


struct Expiry:
    expiry_timestamp: timestamp
    expiry_label: string[3]
    is_active: bool


struct OfferRegistrationFeeLookup:
    minimum_fee: uint256
    minimum_interval: timestamp
    fee_multiplier: uint256
    fee_multiplier_decimals: uint256
    last_registered_at: timestamp
    last_paid_fee: uint256


struct Pool:
    pool_type: uint256
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


# Events of the protocol.

# Variables of the protocol.
protocol_currency_address: public(address)
owner: public(address)
# timestamp => Expiry
expiries: public(map(timestamp, Expiry))
# currency_address => Currency
currencies: public(map(address, Currency))
# template_name => template_contract_address
templates: public(map(string[64], address))
# pool_hash => Pool
pools: public(map(bytes32, Pool))
# pool_type => RegistrationFeeLookup
offer_registration_fee_lookups: public(map(uint256, OfferRegistrationFeeLookup))
# currency_hash => MultiFungibleCurrency
multi_fungible_currencies: map(bytes32, MultiFungibleCurrency)
# currency_hash => quantity per currency_address
shield_currency_prices: public(map(bytes32, uint256))

REGISTRATION_TYPE_POOL: public(uint256)
REGISTRATION_TYPE_OFFER: public(uint256)

POOL_TYPE_CURRENCY_POOL: public(uint256)
POOL_TYPE_INTEREST_POOL: public(uint256)
POOL_TYPE_UNDERWRITER_POOL: public(uint256)


@public
def __init__(_protocol_currency_address: address):
    self.owner = msg.sender
    self.protocol_currency_address = _protocol_currency_address
    self.REGISTRATION_TYPE_POOL = 1
    self.REGISTRATION_TYPE_OFFER = 2
    self.POOL_TYPE_CURRENCY_POOL = 1
    self.POOL_TYPE_INTEREST_POOL = 2
    self.POOL_TYPE_UNDERWRITER_POOL = 3
    # after init, need to set the following template addresses:
    #. currency_pool_template
    #. ERC20_template
    #. ERC1155_template
    #. InterestPool_template
    #. UnderwriterPool_template


@private
@constant
def _duration_since_last_offer_registration(_pool_type: uint256) -> uint256:
    return as_unitless_number(block.timestamp - self.offer_registration_fee_lookups[_pool_type].last_registered_at)


@private
@constant
def _offer_registration_fee(_pool_type: uint256) -> uint256:
    if self._duration_since_last_offer_registration(_pool_type) >= self.offer_registration_fee_lookups[_pool_type].minimum_interval:
        return self.offer_registration_fee_lookups[_pool_type].minimum_fee
    else:
        return as_unitless_number(self.offer_registration_fee_lookups[_pool_type].last_paid_fee) * as_unitless_number(self.offer_registration_fee_lookups[_pool_type].fee_multiplier) / self.offer_registration_fee_lookups[_pool_type].fee_multiplier_decimals


@public
@constant
def offer_registration_fee(_pool_type: uint256) -> uint256:
    return self._offer_registration_fee(_pool_type)


# hashes


@private
@constant
def _pool_hash(_pool_type: uint256, _currency_address: address, _pool_address: address) -> bytes32:
    return keccak256(
        concat(
            convert(self, bytes32),
            convert(_pool_type, bytes32),
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


# internal validations


@private
@constant
def validate_erc20_currency(_currency_address: address,
        _name: string[64], _symbol: string[32], _decimals: uint256) -> bool:
    assert ERC20(_currency_address).name() == _name
    assert ERC20(_currency_address).symbol() == _symbol
    assert ERC20(_currency_address).decimals() == _decimals
    return True


@private
def _validate_pool(_pool_hash: bytes32, _pool_address: address, _pool_type: uint256):
    assert self.pools[_pool_hash].pool_address == _pool_address
    assert self.pools[_pool_hash].pool_type == _pool_type


@private
def _validate_currency(_currency_address: address):
    assert not self.pools[self._pool_hash(self.POOL_TYPE_CURRENCY_POOL, _currency_address, self)].pool_address == ZERO_ADDRESS


@private
def _deposit_erc20(_currency_address: address, _from: address, _to: address, _value: uint256):
    _external_call_successful: bool = ERC20(_currency_address).transferFrom(
        _from, _to, _value)
    assert _external_call_successful


@private
def _mint_and_self_authorize_erc20(_currency_address: address, _to: address, _value: uint256):
    _external_call_successful: bool = ERC20(_currency_address).mintAndAuthorizeMinter(_to, _value)
    assert _external_call_successful


@private
def _burn_as_self_authorized_erc20(_currency_address: address, _to: address, _value: uint256):
    _external_call_successful: bool = ERC20(_currency_address).burnFrom(_to, _value)
    assert _external_call_successful


@private
def _create_erc1155_type(_currency_address: address, _expiry_label: string[3]) -> uint256:
    _expiry_id: uint256 = ERC1155(_currency_address).create_token_type(0, _expiry_label)
    assert as_unitless_number(_expiry_id) == as_unitless_number(ERC1155(_currency_address).nonce()) + 1
    return _expiry_id


@private
def _mint_erc1155(_currency_address: address, _id: uint256, _to: address, _value: uint256):
    _external_call_successful: bool = ERC1155(_currency_address).mint(_id, _to, _value)
    assert _external_call_successful


@private
def _burn_erc1155(_currency_address: address, _id: uint256, _to: address, _value: uint256):
    _external_call_successful: bool = ERC1155(_currency_address).burn(_id, _to, _value)
    assert _external_call_successful


@private
def _process_fee_for_offer_creation(_pool_type: uint256, _from: address):
    assert _pool_type == self.POOL_TYPE_INTEREST_POOL or _pool_type == self.POOL_TYPE_UNDERWRITER_POOL, "invalid pool type"
    _fee_amount: uint256 = self._offer_registration_fee(_pool_type)
    if as_unitless_number(_fee_amount) > 0:
        self._deposit_erc20(self.protocol_currency_address, _from, self, _fee_amount)


# Admin functions

@public
def set_expiry_support(_timestamp: timestamp, _label: string[3], _is_active: bool) -> bool:
    assert msg.sender == self.owner
    self.expiries[_timestamp] = Expiry({
        expiry_timestamp: _timestamp,
        expiry_label: _label,
        is_active: _is_active
    })
    return True


@public
def set_currency_support(
        _currency_address: address, _is_active: bool,
        _pool_type: uint256,
        _currency_name: string[64], _currency_symbol: string[32], _currency_decimals: uint256, _supply: uint256
        ) -> bool:
    assert not _currency_address == self.protocol_currency_address
    assert msg.sender == self.owner
    assert _currency_address.is_contract
    assert self.validate_erc20_currency(_currency_address, _currency_name, _currency_symbol, _currency_decimals)
    _pool_hash: bytes32 = self._pool_hash(self.POOL_TYPE_CURRENCY_POOL, _currency_address, self)
    if _is_active:
        assert self.pools[_pool_hash].pool_address == ZERO_ADDRESS, "currency pool already exists"
        _pool_address: address = create_forwarder_to(self.templates["currency_pool"])
        _external_call_successful: bool = ContinuousCurrencyPoolERC20(_pool_address).initialize(_currency_address)
        assert _external_call_successful
        # l token
        _l_currency_address: address = create_forwarder_to(self.templates["erc20"])
        _external_call_successful = ERC20(_l_currency_address).initialize(
            concat("L", slice(_currency_name, start=0, len=63)), _currency_symbol, _currency_decimals, 0)
        assert _external_call_successful
        # i token
        _i_currency_address: address = create_forwarder_to(self.templates["erc1155"])
        _external_call_successful = ERC1155(_i_currency_address).initialize()
        assert _external_call_successful
        # f token
        _f_currency_address: address = create_forwarder_to(self.templates["erc1155"])
        _external_call_successful = ERC1155(_f_currency_address).initialize()
        assert _external_call_successful
        # s token
        _s_currency_address: address = create_forwarder_to(self.templates["erc1155"])
        _external_call_successful = ERC1155(_s_currency_address).initialize()
        assert _external_call_successful
        # u token
        _u_currency_address: address = create_forwarder_to(self.templates["erc1155"])
        _external_call_successful = ERC1155(_u_currency_address).initialize()
        assert _external_call_successful

        self.pools[_pool_hash] = Pool({
            pool_type: self.POOL_TYPE_CURRENCY_POOL,
            currency_address: _currency_address,
            pool_name: _currency_name,
            pool_address: _pool_address,
            pool_operator: self,
            hash: _pool_hash
        })
        self.currencies[_currency_address] = Currency({
            currency_address: _currency_address,
            l_currency_address: _l_currency_address,
            i_currency_address: _i_currency_address,
            f_currency_address: _f_currency_address,
            s_currency_address: _s_currency_address,
            u_currency_address: _u_currency_address
        })


    else:
        assert not self.pools[_pool_hash].pool_address == ZERO_ADDRESS, "currency pool does not exist"
        clear(self.pools[_pool_hash].pool_address)
        clear(self.pools[_pool_hash].pool_name)
        _external_call_successful: bool = ContinuousCurrencyPoolERC20(self.pools[_pool_hash].pool_address).destroy()
        assert _external_call_successful

    return True


@public
def set_template(_label: string[64], _address: address) -> bool:
    assert msg.sender == self.owner
    self.templates[_label] = _address
    return True


@public
def set_offer_registration_fee_lookup(_pool_type: uint256, _fee_multiplier: uint256,
    _minimum_fee: uint256, _fee_multiplier_decimals: uint256,
    _minimum_interval: timestamp, _last_registered_at: timestamp, _last_paid_fee: uint256
    ) -> bool:
    self.offer_registration_fee_lookups[_pool_type] = OfferRegistrationFeeLookup({
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
    assert msg.sender == self.owner
    _s_hash: bytes32 = self._multi_fungible_currency_hash(self.currencies[_currency_address].s_currency_address, _currency_address, _expiry, _underlying_address, _strike_price)
    self.shield_currency_prices[_s_hash] = _price

    return True


# Public functions


@public
def currency_to_l_currency(_currency_address: address, _value: uint256) -> bool:
    # validate currency address
    _pool_hash: bytes32 = self._pool_hash(self.POOL_TYPE_CURRENCY_POOL, _currency_address, self)
    assert not self.pools[_pool_hash].pool_address == ZERO_ADDRESS, "currency is not supported"
    # transfer currency to currency pool
    self._deposit_erc20(_currency_address, msg.sender, self.pools[_pool_hash].pool_address, _value)
    # update supply in currency pool
    _external_call_successful: bool = ContinuousCurrencyPoolERC20(self.pools[_pool_hash].pool_address).update_total_supplied(_value)
    assert _external_call_successful
    # mint currency l_token to msg.sender
    self._mint_and_self_authorize_erc20(self.currencies[_currency_address].l_currency_address, msg.sender, _value)

    return True


# Functions that interact with both Interest and Underwriter Pools

@public
def register_pool(_pool_type: uint256, _currency_address: address, _name: string[62], _symbol: string[32], _initial_exchange_rate: uint256) -> bytes32:
    # validate pool type
    assert _pool_type == self.POOL_TYPE_INTEREST_POOL or _pool_type == self.POOL_TYPE_UNDERWRITER_POOL
    # validate currency
    self._validate_currency(_currency_address)
    # initialize pool
    _pool_address: address = ZERO_ADDRESS
    _external_call_successful: bool = False
    _pool_hash: bytes32 = EMPTY_BYTES32
    if _pool_type == self.POOL_TYPE_INTEREST_POOL:
        _pool_address = create_forwarder_to(self.templates["interest_pool"])
        assert _pool_address.is_contract
        _pool_hash = self._pool_hash(self.POOL_TYPE_CURRENCY_POOL, _currency_address, _pool_address)
        _external_call_successful = InterestPool(_pool_address).initialize(
            _pool_type, _pool_hash, msg.sender,
            _name, _symbol, _initial_exchange_rate,
            _currency_address,
            self.currencies[_currency_address].l_currency_address,
            self.currencies[_currency_address].i_currency_address,
            self.currencies[_currency_address].f_currency_address,
            self.templates["erc20"])
    else:
        _pool_address = create_forwarder_to(self.templates["underwriter_pool"])
        assert _pool_address.is_contract
        _pool_hash = self._pool_hash(self.POOL_TYPE_CURRENCY_POOL, _currency_address, _pool_address)
        _external_call_successful = InterestPool(_pool_address).initialize(
            _pool_type, _pool_hash, msg.sender,
            _name, _symbol, _initial_exchange_rate,
            _currency_address,
            self.currencies[_currency_address].l_currency_address,
            self.currencies[_currency_address].i_currency_address,
            self.currencies[_currency_address].f_currency_address,
            self.templates["erc20"])

    # save pool metadata
    self.pools[_pool_hash] = Pool({
        pool_type: _pool_type,
        currency_address: _currency_address,
        pool_name: _name,
        pool_address: _pool_address,
        pool_operator: msg.sender,
        hash: _pool_hash
    })

    return _pool_hash


@public
def deposit_l_currency(_pool_hash: bytes32, _from: address, _value: uint256) -> bool:
    assert self.pools[_pool_hash].pool_address == msg.sender
    # validate currency
    self._validate_currency(self.pools[_pool_hash].currency_address)
    self._deposit_erc20(self.currencies[self.pools[_pool_hash].currency_address].l_currency_address, _from, msg.sender, _value)

    return True


# Functions that interact with only Interest Pools


@public
def register_expiry_from_interest_pool(_pool_hash: bytes32, _expiry: timestamp) -> (bool, bytes32, bytes32, uint256, uint256):
    self._validate_pool(_pool_hash, msg.sender, self.POOL_TYPE_INTEREST_POOL)
    _currency_address: address = self.pools[_pool_hash].currency_address
    _f_hash: bytes32 = self._multi_fungible_currency_hash(self.currencies[_currency_address].f_currency_address, _currency_address, _expiry, ZERO_ADDRESS, 0)
    _i_hash: bytes32 = self._multi_fungible_currency_hash(self.currencies[_currency_address].i_currency_address, _currency_address, _expiry, ZERO_ADDRESS, 0)
    _f_id: uint256 = self.multi_fungible_currencies[_f_hash].token_id
    _i_id: uint256 = self.multi_fungible_currencies[_i_hash].token_id
    # pay lst as fee to create fi currency if it has not been created
    if not self.multi_fungible_currencies[_f_hash].has_id or \
       not self.multi_fungible_currencies[_i_hash].has_id:
       self._process_fee_for_offer_creation(self.pools[_pool_hash].pool_type, self.pools[_pool_hash].pool_operator)

    if not self.multi_fungible_currencies[_f_hash].has_id:
        _f_id = self._create_erc1155_type(self.currencies[_currency_address].f_currency_address, "")
        self.multi_fungible_currencies[_f_hash] = MultiFungibleCurrency({
            parent_currency_address: self.currencies[_currency_address].f_currency_address,
            currency_address: _currency_address,
            expiry_timestamp: _expiry,
            underlying_address: ZERO_ADDRESS,
            strike_price: 0,
            has_id: True,
            token_id: _f_id,
            hash: _f_hash
        })
    if not self.multi_fungible_currencies[_i_hash].has_id:
        _i_id = self._create_erc1155_type(self.currencies[_currency_address].i_currency_address, "")
        self.multi_fungible_currencies[_i_hash] = MultiFungibleCurrency({
            parent_currency_address: self.currencies[_currency_address].i_currency_address,
            currency_address: _currency_address,
            expiry_timestamp: _expiry,
            underlying_address: ZERO_ADDRESS,
            strike_price: 0,
            has_id: True,
            token_id: _i_id,
            hash: _i_hash
        })

    return True, _f_hash, _i_hash, _f_id, _i_id


@public
def l_currency_to_i_and_f_currency(_pool_hash: bytes32, _expiry: timestamp, _value: uint256) -> bool:
    self._validate_pool(_pool_hash, msg.sender, self.POOL_TYPE_INTEREST_POOL)
    _currency_address: address = self.pools[_pool_hash].currency_address
    self._validate_currency(_currency_address)
    # validate i and f token types exist for expiry
    _f_hash: bytes32 = self._multi_fungible_currency_hash(self.currencies[_currency_address].f_currency_address, _currency_address, _expiry, ZERO_ADDRESS, 0)
    _i_hash: bytes32 = self._multi_fungible_currency_hash(self.currencies[_currency_address].i_currency_address, _currency_address, _expiry, ZERO_ADDRESS, 0)
    assert self.multi_fungible_currencies[_f_hash].has_id and self.multi_fungible_currencies[_i_hash].has_id
    # burn l_token from interest_pool account
    self._burn_as_self_authorized_erc20(self.currencies[_currency_address].l_currency_address, msg.sender, _value)
    # mint i_token into interest_pool account
    self._mint_erc1155(
        self.currencies[_currency_address].i_currency_address,
        self.multi_fungible_currencies[_i_hash].token_id,
        msg.sender,
        _value
    )
    self._mint_erc1155(
        self.currencies[_currency_address].f_currency_address,
        self.multi_fungible_currencies[_f_hash].token_id,
        msg.sender,
        _value
    )
    return True


@public
def l_currency_from_i_and_f_currency(_pool_hash: bytes32, _expiry: timestamp, _value: uint256) -> bool:
    self._validate_pool(_pool_hash, msg.sender, self.POOL_TYPE_INTEREST_POOL)
    _currency_address: address = self.pools[_pool_hash].currency_address
    self._validate_currency(_currency_address)
    # validate i and f token types exist for expiry
    _f_hash: bytes32 = self._multi_fungible_currency_hash(self.currencies[_currency_address].f_currency_address, _currency_address, _expiry, ZERO_ADDRESS, 0)
    _i_hash: bytes32 = self._multi_fungible_currency_hash(self.currencies[_currency_address].i_currency_address, _currency_address, _expiry, ZERO_ADDRESS, 0)
    assert self.multi_fungible_currencies[_f_hash].has_id and self.multi_fungible_currencies[_i_hash].has_id
    # burn l_token from interest_pool account
    self._mint_and_self_authorize_erc20(self.currencies[_currency_address].l_currency_address, msg.sender, _value)
    # mint i_token into interest_pool account
    self._burn_erc1155(
        self.currencies[_currency_address].i_currency_address,
        self.multi_fungible_currencies[_i_hash].token_id,
        msg.sender,
        _value
    )
    self._burn_erc1155(
        self.currencies[_currency_address].f_currency_address,
        self.multi_fungible_currencies[_f_hash].token_id,
        msg.sender,
        _value
    )
    return True


# Functions that interact with only Underwriter Pools


@public
def register_expiry_from_underwriter_pool(_pool_hash: bytes32, _expiry: timestamp, _underlying_address: address, _strike_price: uint256) -> (bool, bytes32, bytes32, bytes32, uint256, uint256, uint256):
    self._validate_pool(_pool_hash, msg.sender, self.POOL_TYPE_UNDERWRITER_POOL)
    _currency_address: address = self.pools[_pool_hash].currency_address
    _i_hash: bytes32 = self._multi_fungible_currency_hash(self.currencies[_currency_address].i_currency_address, _currency_address, _expiry, ZERO_ADDRESS, 0)
    _s_hash: bytes32 = self._multi_fungible_currency_hash(self.currencies[_currency_address].s_currency_address, _currency_address, _expiry, _underlying_address, _strike_price)
    _u_hash: bytes32 = self._multi_fungible_currency_hash(self.currencies[_currency_address].u_currency_address, _currency_address, _expiry, _underlying_address, _strike_price)
    _i_id: uint256 = self.multi_fungible_currencies[_i_hash].token_id
    _s_id: uint256 = self.multi_fungible_currencies[_s_hash].token_id
    _u_id: uint256 = self.multi_fungible_currencies[_u_hash].token_id

    # pay lst as fee to create fi currency if it has not been created
    if not self.multi_fungible_currencies[_s_hash].has_id or \
       not self.multi_fungible_currencies[_u_hash].has_id or \
       not self.multi_fungible_currencies[_i_hash].has_id:
       self._process_fee_for_offer_creation(self.pools[_pool_hash].pool_type, self.pools[_pool_hash].pool_operator)

    if not self.multi_fungible_currencies[_s_hash].has_id:
        _s_id = self._create_erc1155_type(self.currencies[_currency_address].f_currency_address, "")
        self.multi_fungible_currencies[_s_hash] = MultiFungibleCurrency({
            parent_currency_address: self.currencies[_currency_address].s_currency_address,
            currency_address: _currency_address,
            expiry_timestamp: _expiry,
            underlying_address: _underlying_address,
            strike_price: _strike_price,
            has_id: True,
            token_id: _s_id,
            hash: _s_hash
        })
    if not self.multi_fungible_currencies[_u_hash].has_id:
        _u_id = self._create_erc1155_type(self.currencies[_currency_address].u_currency_address, "")
        self.multi_fungible_currencies[_u_hash] = MultiFungibleCurrency({
            parent_currency_address: self.currencies[_currency_address].u_currency_address,
            currency_address: _currency_address,
            expiry_timestamp: _expiry,
            underlying_address: _underlying_address,
            strike_price: _strike_price,
            has_id: True,
            token_id: _u_id,
            hash: _u_hash
        })
    if not self.multi_fungible_currencies[_i_hash].has_id:
        _i_id = self._create_erc1155_type(self.currencies[_currency_address].i_currency_address, "")
        self.multi_fungible_currencies[_i_hash] = MultiFungibleCurrency({
            parent_currency_address: self.currencies[_currency_address].i_currency_address,
            currency_address: _currency_address,
            expiry_timestamp: _expiry,
            underlying_address: ZERO_ADDRESS,
            strike_price: 0,
            has_id: True,
            token_id: _i_id,
            hash: _i_hash
        })

    return True, _i_hash, _s_hash, _u_hash, _i_id, _s_id, _u_id


@public
def l_currency_to_i_and_s_and_u_currency(_pool_hash: bytes32, _expiry: timestamp, _underlying_address: address, _strike_price: uint256, _value: uint256) -> bool:
    self._validate_pool(_pool_hash, msg.sender, self.POOL_TYPE_UNDERWRITER_POOL)
    _currency_address: address = self.pools[_pool_hash].currency_address
    self._validate_currency(_currency_address)
    self._validate_currency(_underlying_address)
    # validate i, s, and u token types exists for combination of expiry, underlying, and strike
    _s_hash: bytes32 = self._multi_fungible_currency_hash(self.currencies[_currency_address].s_currency_address, _currency_address, _expiry, _underlying_address, _strike_price)
    _u_hash: bytes32 = self._multi_fungible_currency_hash(self.currencies[_currency_address].u_currency_address, _currency_address, _expiry, _underlying_address, _strike_price)
    _i_hash: bytes32 = self._multi_fungible_currency_hash(self.currencies[_currency_address].i_currency_address, _currency_address, _expiry, ZERO_ADDRESS, 0)
    assert self.multi_fungible_currencies[_s_hash].has_id and \
           self.multi_fungible_currencies[_u_hash].has_id and \
           self.multi_fungible_currencies[_i_hash].has_id
    # burn l_token from interest_pool account
    self._burn_as_self_authorized_erc20(self.currencies[_currency_address].l_currency_address, msg.sender, _value)
    # calculate su currency quantitites to be minted
    assert not as_unitless_number(self.shield_currency_prices[_s_hash]) == 0, "shield price has not been set"
    _su_currencies_to_mint: uint256 = as_unitless_number(_value) / as_unitless_number(self.shield_currency_prices[_s_hash])
    # mint i_token into interest_pool account
    self._mint_erc1155(
        self.currencies[_currency_address].s_currency_address,
        self.multi_fungible_currencies[_s_hash].token_id,
        msg.sender,
        _su_currencies_to_mint
    )
    self._mint_erc1155(
        self.currencies[_currency_address].u_currency_address,
        self.multi_fungible_currencies[_u_hash].token_id,
        msg.sender,
        _su_currencies_to_mint
    )
    self._mint_erc1155(
        self.currencies[_currency_address].i_currency_address,
        self.multi_fungible_currencies[_i_hash].token_id,
        msg.sender,
        _value
    )
    return True


@public
def l_currency_from_i_and_s_and_u_currency(_pool_hash: bytes32, _expiry: timestamp, _underlying_address: address, _strike_price: uint256, _value: uint256) -> bool:
    self._validate_pool(_pool_hash, msg.sender, self.POOL_TYPE_UNDERWRITER_POOL)
    _currency_address: address = self.pools[_pool_hash].currency_address
    self._validate_currency(_currency_address)
    self._validate_currency(_underlying_address)
    # validate i, s, and u token types exists for combination of expiry, underlying, and strike
    _s_hash: bytes32 = self._multi_fungible_currency_hash(self.currencies[_currency_address].s_currency_address, _currency_address, _expiry, _underlying_address, _strike_price)
    _u_hash: bytes32 = self._multi_fungible_currency_hash(self.currencies[_currency_address].u_currency_address, _currency_address, _expiry, _underlying_address, _strike_price)
    _i_hash: bytes32 = self._multi_fungible_currency_hash(self.currencies[_currency_address].i_currency_address, _currency_address, _expiry, ZERO_ADDRESS, 0)
    assert self.multi_fungible_currencies[_s_hash].has_id and \
           self.multi_fungible_currencies[_u_hash].has_id and \
           self.multi_fungible_currencies[_i_hash].has_id
    # burn l_token from interest_pool account
    self._mint_and_self_authorize_erc20(self.currencies[_currency_address].l_currency_address, msg.sender, _value)
    # calculate su currency quantitites to be minted
    assert not as_unitless_number(self.shield_currency_prices[_s_hash]) == 0, "shield price has not been set"
    _su_currencies_to_burn: uint256 = as_unitless_number(_value) / as_unitless_number(self.shield_currency_prices[_s_hash])
    # mint i_token into interest_pool account
    self._burn_erc1155(
        self.currencies[_currency_address].s_currency_address,
        self.multi_fungible_currencies[_s_hash].token_id,
        msg.sender,
        _su_currencies_to_burn
    )
    self._burn_erc1155(
        self.currencies[_currency_address].u_currency_address,
        self.multi_fungible_currencies[_u_hash].token_id,
        msg.sender,
        _su_currencies_to_burn
    )
    self._burn_erc1155(
        self.currencies[_currency_address].i_currency_address,
        self.multi_fungible_currencies[_i_hash].token_id,
        msg.sender,
        _value
    )

    return True
