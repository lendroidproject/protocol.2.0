# @version 0.1.0b14
# @notice Implementation of Lendroid v2 - Interest Pool DAO
# @dev THIS CONTRACT HAS NOT BEEN AUDITED
# @author Vignesh (Vii) Meenakshi Sundaram (@vignesh-msundaram)
# Lendroid Foundation


from ...interfaces import ERC20Interface
from ...interfaces import MultiFungibleTokenInterface
from ...interfaces import CurrencyDaoInterface
from ...interfaces import InterestPoolInterface
from ...interfaces import PoolNameRegistryInterface

from ...interfaces import ProtocolDaoInterface


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
# dao_type => dao_address
daos: public(map(int128, address))
# registry_type => registry_address
registries: public(map(int128, address))
# template_name => template_contract_address
templates: public(map(int128, address))
# name => Pool
pools: public(map(string[64], Pool))
# pool id => pool name
pool_id_to_name: public(map(uint256, string[64]))
# pool id counter
next_pool_id: public(uint256)
# _mft_hash => MFT
mfts: public(map(bytes32, MFT))
# mft_count => fee_multiplier
fee_multiplier_per_mft_count: public(map(uint256, uint256))
minimum_mft_fee: public(uint256)
# pool name => (_market_hash => stake)
LST_staked_per_mft: public(map(string[64], map(bytes32, uint256)))
maximum_mft_support_count: public(uint256)
FEE_MULTIPLIER_DECIMALS: constant(uint256) = 100

REGISTRY_POOL_NAME: constant(int128) = 1

DAO_CURRENCY: constant(int128) = 1

TEMPLATE_INTEREST_POOL: constant(int128) = 2
TEMPLATE_ERC20: constant(int128) = 6
TEMPLATE_ERC20_POOL_TOKEN: constant(int128) = 9

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
        _registry_pool_name: address,
        _dao_currency: address,
        _template_interest_pool: address,
        _template_token_erc20: address,
        _template_erc20_pool_token: address
        ) -> bool:
    assert not self.initialized
    self.initialized = True
    self.protocol_dao = msg.sender
    self.LST = _LST

    self.registries[REGISTRY_POOL_NAME] = _registry_pool_name

    self.daos[DAO_CURRENCY] = _dao_currency

    self.templates[TEMPLATE_INTEREST_POOL] = _template_interest_pool
    self.templates[TEMPLATE_ERC20] = _template_token_erc20
    self.templates[TEMPLATE_ERC20_POOL_TOKEN] = _template_erc20_pool_token

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
def _market_hash(_currency: address, _expiry: timestamp) -> bytes32:
    """
        @dev Function to get the hash of a currency market, given the currency
             and expiry.
        @param _currency The address of the currency.
        @param _expiry The timestamp when the currency market expires.
        @return A unique bytes32 representing the currency market.
    """
    return keccak256(
        concat(
            convert(self.protocol_dao, bytes32),
            convert(_currency, bytes32),
            convert(_expiry, bytes32),
            convert(ZERO_ADDRESS, bytes32),
            convert(0, bytes32)
        )
    )


@private
def _validate_pool(_name: string[64], _address: address):
    assert self.pools[_name].address_ == _address


@private
@constant
def _LST_stake_value(_name: string[64]) -> uint256:
    if self.pools[_name].mft_count == 0:
        return self.minimum_mft_fee
    _multiplier: uint256 = self.fee_multiplier_per_mft_count[self.pools[_name].mft_count]
    if _multiplier == 0:
        _multiplier = self.fee_multiplier_per_mft_count[0]
    return as_unitless_number(self.minimum_mft_fee) + as_unitless_number(as_unitless_number(self.pools[_name].mft_count) * as_unitless_number(_multiplier) / as_unitless_number(FEE_MULTIPLIER_DECIMALS))


@private
def _stake_LST(_name: string[64], _expiry: timestamp):
    _LST_value: uint256 = self._LST_stake_value(_name)
    assert as_unitless_number(_LST_value) > 0
    self.pools[_name].LST_staked += _LST_value
    self.pools[_name].mft_count += 1
    _market_hash: bytes32 = self._market_hash(self.pools[_name].currency, _expiry)
    self.LST_staked_per_mft[_name][_market_hash] = _LST_value
    assert_modifiable(CurrencyDaoInterface(self.daos[DAO_CURRENCY]).authorized_transfer_erc20(
        self.LST, self.pools[_name].operator, self, _LST_value))


@private
def _release_staked_LST(_name: string[64], _expiry: timestamp):
    # release staked LST to support currency market
    _market_hash: bytes32 = self._market_hash(self.pools[_name].currency, _expiry)
    _LST_value: uint256 = self.LST_staked_per_mft[_name][_market_hash]
    assert as_unitless_number(_LST_value) > 0
    self.pools[_name].LST_staked -= _LST_value
    self.pools[_name].mft_count -= 1
    clear(self.LST_staked_per_mft[_name][_market_hash])
    assert_modifiable(ERC20Interface(self.LST).transfer(
        self.pools[_name].operator, _LST_value
    ))


@public
@constant
def currency_dao() -> address:
    return self.daos[DAO_CURRENCY]


@public
@constant
def LST_stake_value(_name: string[64]) -> uint256:
    return self._LST_stake_value(_name)


# admin functions


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
    assert _template_type == TEMPLATE_INTEREST_POOL
    self.templates[_template_type] = _address
    return True


@public
def set_minimum_mft_fee(_value: uint256) -> bool:
    """
        @dev Function to set the minimum stake required to support a MFT by an
             Interest Pool. Only the Protocol DAO can call this function.
        @param _value The stake value.
        @return A bool with a value of "True" indicating the stake for MFT support
            has been set.
    """
    assert self.initialized
    assert msg.sender == self.protocol_dao
    self.minimum_mft_fee = _value

    return True


@public
def set_fee_multiplier_per_mft_count(
    _mft_count: uint256, _value: uint256) -> bool:
    """
        @dev Function to set the multiplier for every time an Interest Pool
             increases the MFTs it supports. Only the Protocol DAO can call this
             function.
        @param _mft_count The number of MFTs the Interest Pool supports.
        @param _value The multplier for the MFT count of the Interest Pool.
        @return A bool with a value of "True" indicating the multiplier for MFT
             support has been set.
    """
    assert self.initialized
    assert msg.sender == self.protocol_dao
    self.fee_multiplier_per_mft_count[_mft_count] = _value

    return True


@public
def set_maximum_mft_support_count(_value: uint256) -> bool:
    """
        @dev Function to set the maximum number of MFTs an Interest Pool can
             support. Only the Protocol DAO can call this function.
        @param _value The maximum value.
        @return A bool with a value of "True" indicating the maxmimum number for
             MFT support has been set.
    """
    assert self.initialized
    assert msg.sender == self.protocol_dao
    self.maximum_mft_support_count = _value

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
    assert_modifiable(ERC20Interface(_token).transfer(
        ProtocolDaoInterface(self.protocol_dao).authorized_callers(CALLER_ESCAPE_HATCH_TOKEN_HOLDER),
        ERC20Interface(_token).balanceOf(self)
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
    _id: uint256 = MultiFungibleTokenInterface(_token).hash_to_id(_mft_hash)
    _balance: uint256 = MultiFungibleTokenInterface(_token).balanceOf(self, _id)
    assert_modifiable(MultiFungibleTokenInterface(_token).safeTransferFrom(
        self,
        ProtocolDaoInterface(self.protocol_dao).authorized_callers(CALLER_ESCAPE_HATCH_TOKEN_HOLDER),
        _id, _balance, EMPTY_BYTES32
    ))


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
        CurrencyDaoInterface(self.daos[DAO_CURRENCY]).token_addresses__l(_currency)
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
        _token = CurrencyDaoInterface(self.daos[DAO_CURRENCY]).token_addresses__f(_currency)
    if _mft_type == MFT_TYPE_I:
        _token = CurrencyDaoInterface(self.daos[DAO_CURRENCY]).token_addresses__i(_currency)
    if _mft_type == MFT_TYPE_S:
        _token = CurrencyDaoInterface(self.daos[DAO_CURRENCY]).token_addresses__s(_currency)
    if _mft_type == MFT_TYPE_U:
        _token = CurrencyDaoInterface(self.daos[DAO_CURRENCY]).token_addresses__u(_currency)
    assert not _token == ZERO_ADDRESS
    self._transfer_balance_mft(_token, _currency, _expiry, _underlying, _strike_price)
    return True


# Non-admin functions


@public
def register_pool(
    _accepts_public_contributions: bool,
    _currency: address, _name: string[64],
    _initial_exchange_rate: uint256,
    _fee_percentage_per_i_token: uint256,
    _mft_expiry_limit: uint256
    ) -> bool:
    assert self.initialized
    assert not self.paused
    # validate currency
    assert CurrencyDaoInterface(self.daos[DAO_CURRENCY]).is_token_supported(_currency)
    # Increment active pool count if pool name is already registered.
    # Otherwise, register pool name and increment active pool count
    if PoolNameRegistryInterface(self.registries[REGISTRY_POOL_NAME]).name_exists(_name):
        assert_modifiable(PoolNameRegistryInterface(self.registries[REGISTRY_POOL_NAME]).register_pool(_name, msg.sender))
    else:
        assert_modifiable(PoolNameRegistryInterface(self.registries[REGISTRY_POOL_NAME]).register_name_and_pool(_name, msg.sender))
    # initialize pool
    _l_address: address = ZERO_ADDRESS
    _i_address: address = ZERO_ADDRESS
    _f_address: address = ZERO_ADDRESS
    _s_address: address = ZERO_ADDRESS
    _u_address: address = ZERO_ADDRESS
    _address: address = create_forwarder_to(self.templates[TEMPLATE_INTEREST_POOL])
    assert _address.is_contract
    _l_address, _i_address, _f_address, _s_address, _u_address = CurrencyDaoInterface(self.daos[DAO_CURRENCY]).mft_addresses(_currency)
    _allow_public_contribution: bool = _accepts_public_contributions
    if not ProtocolDaoInterface(self.protocol_dao).public_contributions_activated():
        _allow_public_contribution = False
    assert_modifiable(InterestPoolInterface(_address).initialize(
        self.protocol_dao,
        _allow_public_contribution, msg.sender,
        _fee_percentage_per_i_token,
        _mft_expiry_limit,
        _name, _initial_exchange_rate,
        _currency, _l_address, _i_address, _f_address,
        self.templates[TEMPLATE_ERC20_POOL_TOKEN]))

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
    assert_modifiable(PoolNameRegistryInterface(self.registries[REGISTRY_POOL_NAME]).deregister_pool(_name, self.pools[_name].operator))
    # log PoolDeRegistered event
    log.PoolDeRegistered(self.pools[_name].operator, self.pools[_name].currency,
        msg.sender)

    return True


@public
def register_mft_support(_name: string[64], _expiry: timestamp,
    _f_address: address, _i_address: address) -> (bool, uint256, uint256):
    assert self.initialized
    assert not self.paused
    self._validate_pool(_name, msg.sender)
    _currency: address = self.pools[_name].currency
    assert CurrencyDaoInterface(self.daos[DAO_CURRENCY]).is_token_supported(_currency)
    _f_hash: bytes32 = self._mft_hash(_f_address, _currency, _expiry, ZERO_ADDRESS, 0)
    _i_hash: bytes32 = self._mft_hash(_i_address, _currency, _expiry, ZERO_ADDRESS, 0)
    _f_id: uint256 = self.mfts[_f_hash].id
    _i_id: uint256 = self.mfts[_i_hash].id
    # stake LST to support currency market
    self._stake_LST(_name, _expiry)

    if not self.mfts[_f_hash].has_id:
        _f_id = MultiFungibleTokenInterface(_f_address).get_or_create_id(_currency, _expiry, ZERO_ADDRESS, 0, "")
        self.mfts[_f_hash] = MFT({
            address_: _f_address,
            currency: _currency,
            expiry: _expiry,
            underlying: ZERO_ADDRESS,
            strike_price: 0,
            has_id: True,
            id: _f_id,
            hash: _f_hash
        })
    if not self.mfts[_i_hash].has_id:
        _i_id = MultiFungibleTokenInterface(_i_address).get_or_create_id(_currency, _expiry, ZERO_ADDRESS, 0, "")
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

    # log MFTSupportRegistered event
    log.MFTSupportRegistered(_name, msg.sender,
        _currency, _expiry, ZERO_ADDRESS, 0,
        self.pools[_name].operator)

    return True, _f_id, _i_id


@public
def deregister_mft_support(_name: string[64], _currency: address, _expiry: timestamp) -> bool:
    assert self.initialized
    assert not self.paused
    self._validate_pool(_name, msg.sender)
    self._release_staked_LST(_name, _expiry)

    # log MFTSupportDeRegistered event
    log.MFTSupportDeRegistered(_name, msg.sender,
        _currency, _expiry, ZERO_ADDRESS, 0,
        self.pools[_name].operator)

    return True


@public
def deposit_l(_name: string[64], _from: address, _value: uint256) -> bool:
    assert self.initialized
    assert not self.paused
    self._validate_pool(_name, msg.sender)
    # validate currency
    assert CurrencyDaoInterface(self.daos[DAO_CURRENCY]).is_token_supported(self.pools[_name].currency)
    assert_modifiable(CurrencyDaoInterface(self.daos[DAO_CURRENCY]).authorized_transfer_l(
        self.pools[_name].currency, _from, msg.sender, _value))

    return True


@private
def _l_to_f_and_i(_currency: address, _expiry: timestamp,
    _value: uint256, _from: address, _to: address):
    _l_address: address = ZERO_ADDRESS
    _i_address: address = ZERO_ADDRESS
    _f_address: address = ZERO_ADDRESS
    _s_address: address = ZERO_ADDRESS
    _u_address: address = ZERO_ADDRESS
    _l_address, _i_address, _f_address, _s_address, _u_address = CurrencyDaoInterface(self.daos[DAO_CURRENCY]).mft_addresses(_currency)
    _i_id: uint256 = MultiFungibleTokenInterface(_i_address).get_or_create_id(_currency, _expiry, ZERO_ADDRESS, 0, "")
    _f_id: uint256 = MultiFungibleTokenInterface(_f_address).get_or_create_id(_currency, _expiry, ZERO_ADDRESS, 0, "")
    assert (not _i_id == 0) and (not _f_id == 0)
    # burn l_token from _from account
    assert_modifiable(CurrencyDaoInterface(self.daos[DAO_CURRENCY]).burn_as_self_authorized_erc20(_l_address, _from, _value))
    if _expiry > block.timestamp:
        # mint i_token into _to account
        assert_modifiable(MultiFungibleTokenInterface(_i_address).mint(_i_id, _to, _value))
    # mint f_token into _to account
    assert_modifiable(MultiFungibleTokenInterface(_f_address).mint(_f_id, _to, _value))


@public
def split(_currency: address, _expiry: timestamp, _value: uint256) -> bool:
    assert self.initialized
    assert not self.paused
    assert CurrencyDaoInterface(self.daos[DAO_CURRENCY]).is_token_supported(_currency)
    self._l_to_f_and_i(_currency, _expiry, _value, msg.sender, msg.sender)

    return True


@private
def _i_and_f_to_l(_currency: address, _expiry: timestamp,
    _value: uint256, _from: address, _to: address):
    _l_address: address = ZERO_ADDRESS
    _i_address: address = ZERO_ADDRESS
    _f_address: address = ZERO_ADDRESS
    _s_address: address = ZERO_ADDRESS
    _u_address: address = ZERO_ADDRESS
    _l_address, _i_address, _f_address, _s_address, _u_address = CurrencyDaoInterface(self.daos[DAO_CURRENCY]).mft_addresses(_currency)
    _i_id: uint256 = MultiFungibleTokenInterface(_i_address).id(_currency, _expiry, ZERO_ADDRESS, 0)
    _f_id: uint256 = MultiFungibleTokenInterface(_f_address).id(_currency, _expiry, ZERO_ADDRESS, 0)
    assert (not _i_id == 0) and (not _f_id == 0)
    if _expiry > block.timestamp:
        # burn i_token from _from account
        assert_modifiable(MultiFungibleTokenInterface(_i_address).burn(_i_id, _from, _value))
    # burn f_token from _from account
    assert_modifiable(MultiFungibleTokenInterface(_f_address).burn(_f_id, _from, _value))
    # mint l_token into _to account
    assert_modifiable(CurrencyDaoInterface(self.daos[DAO_CURRENCY]).mint_and_self_authorize_erc20(_l_address, _to, _value))


@public
def fuse(_currency: address, _expiry: timestamp, _value: uint256) -> bool:
    assert self.initialized
    assert not self.paused
    assert CurrencyDaoInterface(self.daos[DAO_CURRENCY]).is_token_supported(_currency)
    self._i_and_f_to_l(_currency, _expiry, _value, msg.sender, msg.sender)

    return True
