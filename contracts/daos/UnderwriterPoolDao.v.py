# Vyper version of the Lendroid protocol v2
# THIS CONTRACT HAS NOT BEEN AUDITED!


from contracts.interfaces import ERC20
from contracts.interfaces import MultiFungibleToken
from contracts.interfaces import CurrencyDao
from contracts.interfaces import UnderwriterPool
from contracts.interfaces import MarketDao
from contracts.interfaces import PoolNameRegistry

# structs
struct Pool:
    currency: address
    name: string[64]
    address_: address
    operator: address
    mft_count: uint256
    LST_staked: uint256
    is_active: bool
    id: uint256


struct MFT:
    address_: address
    currency: address
    expiry: timestamp
    underlying: address
    strike_price: uint256
    has_id: bool
    id: uint256
    hash: bytes32


# Events
PoolRegistered: event({_operator: indexed(address), _currency: indexed(address), address_: indexed(address)})
PoolDeRegistered: event({_operator: indexed(address), _currency: indexed(address), address_: indexed(address)})

MFTSupportRegistered: event({_name: indexed(string[64]), _pool: indexed(address), _currency: address, _expiry: timestamp, _underlying: address, _strike_price: uint256, _operator: address})
MFTSupportDeRegistered: event({_name: indexed(string[64]), _pool: indexed(address), _currency: address, _expiry: timestamp, _underlying: address, _strike_price: uint256, _operator: address})

LST: public(address)
protocol_dao: public(address)
owner: public(address)
# dao_type => dao_address
daos: public(map(uint256, address))
# registry_type => registry_address
registries: public(map(uint256, address))
# template_name => template_contract_address
templates: public(map(uint256, address))
# name => Pool
pools: public(map(string[64], Pool))
# pool id => pool name
pool_id_to_name: public(map(uint256, string[64]))
# pool id counter
next_pool_id: public(uint256)
# mft_hash => MFT
mfts: public(map(bytes32, MFT))
# mft_count => fee_multiplier
fee_multiplier_per_mft_count: public(map(uint256, uint256))
minimum_mft_fee: public(uint256)
# name => (_market_hash => stake)
LST_staked_per_mft: public(map(string[64], map(bytes32, uint256)))
maximum_mft_support_count: public(uint256)

REGISTRY_TYPE_POOL_NAME: public(uint256)

DAO_TYPE_CURRENCY: public(uint256)
DAO_TYPE_MARKET: public(uint256)
DAO_TYPE_SHIELD_PAYOUT: public(uint256)

TEMPLATE_TYPE_UNDERWRITER_POOL: public(uint256)
TEMPLATE_TYPE_TOKEN_ERC20: public(uint256)

initialized: public(bool)
paused: public(bool)


@public
def initialize(
        _owner: address,
        _LST: address,
        _registry_address_pool_name: address,
        _dao_currency: address,
        _dao_market: address,
        _dao_shield_payout: address,
        _template_underwriter_pool: address,
        _template_token_erc20: address
        ) -> bool:
    assert not self.initialized
    self.initialized = True
    self.owner = _owner
    self.protocol_dao = msg.sender
    self.LST = _LST

    self.REGISTRY_TYPE_POOL_NAME = 1
    self.registries[self.REGISTRY_TYPE_POOL_NAME] = _registry_address_pool_name

    self.DAO_TYPE_CURRENCY = 1
    self.daos[self.DAO_TYPE_CURRENCY] = _dao_currency
    self.DAO_TYPE_MARKET = 2
    self.daos[self.DAO_TYPE_MARKET] = _dao_market
    self.DAO_TYPE_SHIELD_PAYOUT = 3
    self.daos[self.DAO_TYPE_SHIELD_PAYOUT] = _dao_shield_payout

    self.TEMPLATE_TYPE_UNDERWRITER_POOL = 1
    self.TEMPLATE_TYPE_TOKEN_ERC20 = 2
    self.templates[self.TEMPLATE_TYPE_UNDERWRITER_POOL] = _template_underwriter_pool
    self.templates[self.TEMPLATE_TYPE_TOKEN_ERC20] = _template_token_erc20

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
def _market_hash(_currency: address, _expiry: timestamp, _underlying: address, _strike_price: uint256) -> bytes32:
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
def _is_token_supported(_token: address) -> bool:
    return CurrencyDao(self.daos[self.DAO_TYPE_CURRENCY]).is_token_supported(_token)


@private
@constant
def _mft_addresses(_token: address) -> (address, address, address, address, address):
    return CurrencyDao(self.daos[self.DAO_TYPE_CURRENCY]).mft_addresses(_token)


@private
def _validate_pool(_name: string[64], _address: address):
    assert self.pools[_name].address_ == _address


@private
def _transfer_l(_token: address, _from: address, _to: address, _value: uint256):
    assert_modifiable(CurrencyDao(self.daos[self.DAO_TYPE_CURRENCY]).authorized_transfer_l(
        _token, _from, _to, _value))


@private
def _transfer_erc20(_token: address, _from: address, _to: address, _value: uint256):
    assert_modifiable(CurrencyDao(self.daos[self.DAO_TYPE_CURRENCY]).authorized_transfer_erc20(
        _token, _from, _to, _value))


@private
def _get_or_create_mft_id(_token: address, _currency: address, _expiry: timestamp, _underlying: address, _strike_price: uint256) -> uint256:
    return MultiFungibleToken(_token).get_or_create_id(_currency, _expiry, _underlying, _strike_price, "")


@private
def _mint_and_self_authorize_erc20(_token: address, _to: address, _value: uint256):
    assert_modifiable(CurrencyDao(self.daos[self.DAO_TYPE_CURRENCY]).mint_and_self_authorize_erc20(_token, _to, _value))


@private
def _burn_as_self_authorized_erc20(_token: address, _to: address, _value: uint256):
    assert_modifiable(CurrencyDao(self.daos[self.DAO_TYPE_CURRENCY]).burn_as_self_authorized_erc20(_token, _to, _value))


@private
def _mint_mft(_token: address, _id: uint256, _to: address, _value: uint256):
    assert_modifiable(MultiFungibleToken(_token).mint(_id, _to, _value))


@private
def _burn_mft(_token: address, _id: uint256, _from: address, _value: uint256):
    assert_modifiable(MultiFungibleToken(_token).burn(_id, _from, _value))


@private
@constant
def _LST_stake_value(_name: string[64]) -> uint256:
    if self.pools[_name].mft_count == 0:
        return self.minimum_mft_fee
    _multiplier: uint256 = self.fee_multiplier_per_mft_count[self.pools[_name].mft_count]
    if _multiplier == 0:
        _multiplier = self.fee_multiplier_per_mft_count[0]
    return as_unitless_number(self.minimum_mft_fee) + as_unitless_number(as_unitless_number(self.pools[_name].mft_count) * as_unitless_number(_multiplier))


@private
def _stake_LST(_name: string[64], _currency: address, _expiry: timestamp, _underlying: address, _strike_price: uint256):
    _LST_value: uint256 = self._LST_stake_value(_name)
    assert as_unitless_number(_LST_value) > 0
    _market_hash: bytes32 = self._market_hash(_currency, _expiry, _underlying, _strike_price)
    self.pools[_name].LST_staked += _LST_value
    self.pools[_name].mft_count += 1
    self.LST_staked_per_mft[_name][_market_hash] = _LST_value
    self._transfer_erc20(self.LST, self.pools[_name].operator, self, _LST_value)


@private
def _release_staked_LST(_name: string[64], _currency: address, _expiry: timestamp, _underlying: address, _strike_price: uint256):
    _market_hash: bytes32 = self._market_hash(_currency, _expiry, _underlying, _strike_price)
    # release staked LST to support shield market
    _LST_value: uint256 = self.LST_staked_per_mft[_name][_market_hash]
    assert as_unitless_number(_LST_value) > 0
    self.pools[_name].LST_staked -= _LST_value
    self.pools[_name].mft_count -= 1
    clear(self.LST_staked_per_mft[_name][_market_hash])
    assert_modifiable(ERC20(self.LST).transfer(
        self.pools[_name].operator, _LST_value
    ))


@public
@constant
def currency_dao() -> address:
    return self.daos[self.DAO_TYPE_CURRENCY]


@public
@constant
def LST_stake_value(_name: string[64]) -> uint256:
    return self._LST_stake_value(_name)


# admin functions


@public
def set_minimum_mft_fee(_value: uint256) -> bool:
    assert self.initialized
    assert msg.sender == self.owner
    self.minimum_mft_fee = _value

    return True


@public
def set_fee_multiplier_per_mft_count(
    _mft_count: uint256, _value: uint256) -> bool:
    assert self.initialized
    assert msg.sender == self.owner
    self.fee_multiplier_per_mft_count[_mft_count] = _value

    return True


@public
def set_maximum_mft_support_count(_value: uint256) -> bool:
    assert self.initialized
    assert msg.sender == self.owner
    self.maximum_mft_support_count = _value

    return True


@public
def set_template(_template_type: uint256, _address: address) -> bool:
    assert self.initialized
    assert msg.sender == self.owner
    assert _template_type == self.TEMPLATE_TYPE_UNDERWRITER_POOL
    self.templates[_template_type] = _address
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


# Non-admin functions


@public
def register_pool(
    _accepts_public_contributions: bool,
    _currency: address, _name: string[64], _symbol: string[32],
    _initial_exchange_rate: uint256,
    _fee_percentage_per_i_token: uint256, _fee_percentage_per_s_token: uint256,
    _mft_expiry_limit: uint256) -> bool:
    assert self.initialized
    assert not self.paused
    # validate currency
    assert self._is_token_supported(_currency)
    # Increment active pool count if pool name is already registered.
    # Otherwise, register pool name and increment active pool count
    if PoolNameRegistry(self.registries[self.REGISTRY_TYPE_POOL_NAME]).name_exists(_name):
        assert_modifiable(PoolNameRegistry(self.registries[self.REGISTRY_TYPE_POOL_NAME]).register_pool(_name, msg.sender))
    else:
        assert_modifiable(PoolNameRegistry(self.registries[self.REGISTRY_TYPE_POOL_NAME]).register_name_and_pool(_name, msg.sender))
    # initialize pool
    _l_address: address = ZERO_ADDRESS
    _i_address: address = ZERO_ADDRESS
    _f_address: address = ZERO_ADDRESS
    _s_address: address = ZERO_ADDRESS
    _u_address: address = ZERO_ADDRESS
    _address: address = create_forwarder_to(self.templates[self.TEMPLATE_TYPE_UNDERWRITER_POOL])
    assert _address.is_contract
    _l_address, _i_address, _f_address, _s_address, _u_address = self._mft_addresses(_currency)
    assert_modifiable(UnderwriterPool(_address).initialize(
        self.protocol_dao,
        _accepts_public_contributions, msg.sender,
        _fee_percentage_per_i_token, _fee_percentage_per_s_token,
        _mft_expiry_limit,
        _name, _symbol, _initial_exchange_rate,
        _currency, _l_address, _i_address, _s_address, _u_address,
        self.daos[self.DAO_TYPE_SHIELD_PAYOUT],
        self.templates[self.TEMPLATE_TYPE_TOKEN_ERC20]))

    # save pool metadata
    self.pools[_name] = Pool({
        currency: _currency,
        name: _name,
        address_: _address,
        operator: msg.sender,
        mft_count: 0,
        LST_staked: 0,
        is_active: True,
        id: self.next_pool_id
    })
    # map pool id counter to pool name
    self.pool_id_to_name[self.next_pool_id] = _name
    # increment pool id counter
    self.next_pool_id += 1

    # log PoolRegistered event
    log.PoolRegistered(msg.sender, _currency, _address)

    return True


@public
def deregister_pool(_name: string[64]) -> bool:
    assert self.initialized
    assert not self.paused
    self._validate_pool(_name, msg.sender)
    # validate that pool does not support any MFT
    assert self.pools[_name].mft_count == 0
    # deactivate pool
    self.pools[_name].is_active = False
    # Decrement active pool count from name registry
    assert_modifiable(PoolNameRegistry(self.registries[self.REGISTRY_TYPE_POOL_NAME]).deregister_pool(_name, self.pools[_name].operator))
    # log PoolDeRegistered event
    log.PoolDeRegistered(self.pools[_name].operator, self.pools[_name].currency,
        msg.sender)

    return True


@public
def register_mft_support(_name: string[64], _expiry: timestamp,
    _underlying: address, _strike_price: uint256,
    _i_address: address, _s_address: address, _u_address: address) -> (bool, uint256, uint256, uint256):
    assert self.initialized
    assert not self.paused
    self._validate_pool(_name, msg.sender)
    _currency: address = self.pools[_name].currency
    assert self._is_token_supported(_currency)
    assert self._is_token_supported(_underlying)
    _i_hash: bytes32 = self._mft_hash(_i_address, _currency, _expiry, ZERO_ADDRESS, 0)
    _s_hash: bytes32 = self._mft_hash(_s_address, _currency, _expiry, _underlying, _strike_price)
    _u_hash: bytes32 = self._mft_hash(_u_address, _currency, _expiry, _underlying, _strike_price)
    _i_id: uint256 = self.mfts[_i_hash].id
    _s_id: uint256 = self.mfts[_s_hash].id
    _u_id: uint256 = self.mfts[_u_hash].id
    # stake lst to support isu currency
    self._stake_LST(_name, _currency, _expiry, _underlying, _strike_price)

    if not self.mfts[_i_hash].has_id:
        _i_id = self._get_or_create_mft_id(_i_address, _currency, _expiry, ZERO_ADDRESS, 0)
        self.mfts[_i_hash] = MFT({
            address_: _i_address,
            currency: _currency,
            expiry: _expiry,
            underlying: ZERO_ADDRESS,
            strike_price: 0,
            has_id: True,
            id: _i_id,
            hash: _i_hash
        })
    if not self.mfts[_s_hash].has_id:
        _s_id = self._get_or_create_mft_id(_s_address, _currency, _expiry, _underlying, _strike_price)
        self.mfts[_s_hash] = MFT({
            address_: _s_address,
            currency: _currency,
            expiry: _expiry,
            underlying: _underlying,
            strike_price: _strike_price,
            has_id: True,
            id: _s_id,
            hash: _s_hash
        })
    if not self.mfts[_u_hash].has_id:
        _u_id = self._get_or_create_mft_id(_u_address, _currency, _expiry, _underlying, _strike_price)
        self.mfts[_u_hash] = MFT({
            address_: _u_address,
            currency: _currency,
            expiry: _expiry,
            underlying: _underlying,
            strike_price: _strike_price,
            has_id: True,
            id: _u_id,
            hash: _u_hash
        })

    # create market on MarketDao
    # deploy and initialize shield payout graph via MarketDao
    # deploy and initialize collateral auction graph via MarketDao
    assert_modifiable(MarketDao(self.daos[self.DAO_TYPE_MARKET]).open_shield_market(
        _currency, _expiry, _underlying, _strike_price,
        _s_address, _s_id,
        _u_address, _u_id
    ))

    # log MFTSupportRegistered event
    log.MFTSupportRegistered(_name, msg.sender,
        _currency, _expiry, _underlying, _strike_price,
        self.pools[_name].operator)

    return True, _i_id, _s_id, _u_id


@public
def deregister_mft_support(_name: string[64], _currency: address, _expiry: timestamp, _underlying: address, _strike_price: uint256) -> bool:
    assert self.initialized
    assert not self.paused
    self._validate_pool(_name, msg.sender)
    self._release_staked_LST(_name, _currency, _expiry, _underlying, _strike_price)

    # log MFTSupportDeRegistered event
    log.MFTSupportDeRegistered(_name, msg.sender,
        _currency, _expiry, _underlying, _strike_price,
        self.pools[_name].operator)

    return True


@public
def deposit_l(_name: string[64], _from: address, _value: uint256) -> bool:
    assert self.initialized
    assert not self.paused
    self._validate_pool(_name, msg.sender)
    # validate currency
    assert self._is_token_supported(self.pools[_name].currency)
    self._transfer_l(self.pools[_name].currency, _from, msg.sender, _value)

    return True


@private
def _l_to_i_and_s_and_u(_currency: address, _expiry: timestamp, _underlying: address, _strike_price: uint256,
    _value: uint256, _from: address, _to: address):
    _l_address: address = ZERO_ADDRESS
    _i_address: address = ZERO_ADDRESS
    _f_address: address = ZERO_ADDRESS
    _s_address: address = ZERO_ADDRESS
    _u_address: address = ZERO_ADDRESS
    _l_address, _i_address, _f_address, _s_address, _u_address = self._mft_addresses(_currency)
    _i_id: uint256 = MultiFungibleToken(_i_address).id(_currency, _expiry, ZERO_ADDRESS, 0)
    _s_id: uint256 = MultiFungibleToken(_s_address).id(_currency, _expiry, _underlying, _strike_price)
    _u_id: uint256 = MultiFungibleToken(_u_address).id(_currency, _expiry, _underlying, _strike_price)
    # validate i, s, and u token types exists for combination of expiry, underlying, and strike
    assert (not _i_id == 0) and (not _s_id == 0) and (not _u_id == 0)
    # burn l_token from _from account
    self._burn_as_self_authorized_erc20(_l_address, _from, _value)
    # mint i_token into _to account
    self._mint_mft(_i_address, _i_id, _to, _value)
    self._mint_mft(_s_address, _s_id, _to, _value)
    self._mint_mft(_u_address, _u_id, _to, _value)


@public
def split(
    _currency: address, _expiry: timestamp, _underlying: address, _strike_price: uint256,
    _value: uint256) -> bool:
    assert self.initialized
    assert not self.paused
    assert _expiry < block.timestamp
    assert self._is_token_supported(_currency)
    assert self._is_token_supported(_underlying)
    self._l_to_i_and_s_and_u(_currency, _expiry, _underlying, _strike_price,
        _value, msg.sender, msg.sender)

    return True


@private
def _i_and_s_and_u_to_l(_currency: address, _expiry: timestamp, _underlying: address, _strike_price: uint256,
    _value: uint256, _from: address, _to: address):
    _l_address: address = ZERO_ADDRESS
    _i_address: address = ZERO_ADDRESS
    _f_address: address = ZERO_ADDRESS
    _s_address: address = ZERO_ADDRESS
    _u_address: address = ZERO_ADDRESS
    _l_address, _i_address, _f_address, _s_address, _u_address = self._mft_addresses(_currency)
    _i_id: uint256 = MultiFungibleToken(_i_address).id(_currency, _expiry, ZERO_ADDRESS, 0)
    _s_id: uint256 = MultiFungibleToken(_s_address).id(_currency, _expiry, _underlying, _strike_price)
    _u_id: uint256 = MultiFungibleToken(_u_address).id(_currency, _expiry, _underlying, _strike_price)
    _i_hash: bytes32 = self._mft_hash(_i_address, _currency, _expiry, ZERO_ADDRESS, 0)
    _s_hash: bytes32 = self._mft_hash(_s_address, _currency, _expiry, _underlying, _strike_price)
    _u_hash: bytes32 = self._mft_hash(_u_address, _currency, _expiry, _underlying, _strike_price)
    # validate i, s, and u token types exists for combination of expiry, underlying, and strike
    assert (not _i_id == 0) and (not _s_id == 0) and (not _u_id == 0)
    # burn i_tokens from _from account
    self._burn_mft(_i_address, _i_id, _from, _value)
    # burn s_tokens from _from account
    self._burn_mft(_s_address, _s_id, _from, _value)
    # burn u_tokens from _from account
    self._burn_mft(_u_address, _u_id, _from, _value)
    # mint l_tokens to _to account
    self._mint_and_self_authorize_erc20(_l_address, _to, _value)


@public
def fuse(
    _currency: address, _expiry: timestamp, _underlying: address, _strike_price: uint256,
    _value: uint256) -> bool:
    assert self.initialized
    assert not self.paused
    assert _expiry < block.timestamp
    assert self._is_token_supported(_currency)
    assert self._is_token_supported(_underlying)
    self._i_and_s_and_u_to_l(_currency, _expiry, _underlying, _strike_price,
        _value, msg.sender, msg.sender)

    return True
