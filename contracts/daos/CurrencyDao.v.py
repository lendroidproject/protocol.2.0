# Vyper version of the Lendroid protocol v2
# THIS CONTRACT HAS NOT BEEN AUDITED!


from contracts.interfaces import ERC20
from contracts.interfaces import LERC20
from contracts.interfaces import MultiFungibleToken
from contracts.interfaces import ERC20TokenPool

from contracts.interfaces import ProtocolDao


# Structs
struct TokenAddress:
    eth: address
    l: address
    i: address
    f: address
    s: address
    u: address


struct Pool:
    currency: address
    name: string[64]
    address_: address
    operator: address
    hash: bytes32


LST: public(address)
protocol_dao: public(address)
# eth address of token => TokenAddress
token_addresses: public(map(address, TokenAddress))
# pool_hash => Pool
pools: public(map(bytes32, Pool))
# dao_type => dao_address
daos: public(map(int128, address))
# registry_type => registry_address
registries: public(map(int128, address))
# template_name => template_contract_address
templates: public(map(int128, address))

DAO_INTEREST_POOL: constant(int128) = 2
DAO_UNDERWRITER_POOL: constant(int128) = 3
DAO_MARKET: constant(int128) = 4
DAO_SHIELD_PAYOUT: constant(int128) = 5

REGISTRY_POOL_NAME: constant(int128) = 1

TEMPLATE_TOKEN_POOL: constant(int128) = 1
TEMPLATE_ERC20: constant(int128) = 6
TEMPLATE_MFT: constant(int128) = 7
TEMPLATE_LERC20: constant(int128) = 8

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
        _template_token_pool: address,
        _template_erc20: address,
        _template_mft: address,
        _template_lerc20: address,
        _pool_name_registry: address,
        _dao_interest_pool: address,
        _dao_underwriter_pool: address,
        _dao_market: address,
        _dao_shield_payout: address
        ) -> bool:
    assert not self.initialized
    self.initialized = True
    self.protocol_dao = msg.sender
    self.LST = _LST

    self.daos[DAO_INTEREST_POOL] = _dao_interest_pool
    self.daos[DAO_UNDERWRITER_POOL] = _dao_underwriter_pool
    self.daos[DAO_MARKET] = _dao_market
    self.daos[DAO_SHIELD_PAYOUT] = _dao_shield_payout

    self.registries[REGISTRY_POOL_NAME] = _pool_name_registry

    self.templates[TEMPLATE_TOKEN_POOL] = _template_token_pool
    self.templates[TEMPLATE_ERC20] = _template_erc20
    self.templates[TEMPLATE_MFT] = _template_mft
    self.templates[TEMPLATE_LERC20] = _template_lerc20

    return True


### Internal functions ###


@private
@constant
def _pool_hash(_currency: address) -> bytes32:
    """
        @dev Function to get the hash of a ERC20 Token Pool, given the ERC20
             address. This is an internal function and is used only within the
             context of this contract.
        @param _currency The address of the ERC20 Token.
        @return A unique bytes32 representing the Token Pool for the given ERC20
             address.
    """
    return keccak256(
        concat(
            convert(self.protocol_dao, bytes32),
            convert(_currency, bytes32)
        )
    )


@private
@constant
def _mft_hash(_address: address, _currency: address, _expiry: timestamp, _underlying: address, _strike_price: uint256) -> bytes32:
    """
        @dev Function to get the hash of a MFT, given its address and indicators.
             This is an internal function and is used only within the context of
             this contract.
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
def _mft_addresses(_token: address) -> (address, address, address, address, address):
    """
        @dev Function to get the L, F, I, S, and U addresses for a given ERC20
             token. This is an internal function and is used only within the
             context of this contract.
        @param _token The address of the ERC20 token.
        @return A list of 5 addresses, aka, L, F, I, S, and U addresses.
    """
    return self.token_addresses[_token].l, self.token_addresses[_token].i, self.token_addresses[_token].f, self.token_addresses[_token].s, self.token_addresses[_token].u


@private
@constant
def _is_token_supported(_token: address) -> bool:
    """
        @dev Function to verify if a given ERC20 token is supported. The given
             token is supported only if it has a corresponding Token Pool
             contract. This is an internal function and is used only within the
             context of this contract.
        @param _token The address of the ERC20 token.
        @return A bool indicating if the given ERC20 token is supported.
    """
    return self.pools[self._pool_hash(_token)].address_.is_contract


@private
def _deposit_token_to_pool(_token: address, _from: address, _value: uint256):
    """
        @dev Function to execute an ERC20 token transferFrom function to the
             corrresponding token pool. This is an internal function and is used
             only within the context of this contract.
        @param _token The address of the ERC20 token.
        @param _from The address to transfer from.
        @param _value The amount to be transferred.
        @return A bool indicating if the ERC20 token transferFrom was successful.
    """
    # validate currency address
    _pool_hash: bytes32 = self._pool_hash(_token)
    assert self.pools[_pool_hash].address_.is_contract, "token is not supported"
    # transfer currency to currency pool
    assert_modifiable(ERC20(_token).transferFrom(_from, self.pools[_pool_hash].address_, _value))


@private
def _withdraw_token_from_pool(_token: address, _to: address, _value: uint256):
    """
        @dev Function to release an ERC20 token from its corrresponding token
             pool to a given address. This is an internal function and is used
             only within the context of this contract.
        @param _token The address of the ERC20 token.
        @param _to The address to release to.
        @param _value The amount to be released.
        @return A bool indicating if the ERC20 token release was successful.
    """
    # validate currency address
    _pool_hash: bytes32 = self._pool_hash(_token)
    assert self.pools[_pool_hash].address_.is_contract, "token is not supported"
    # release token from token pool
    assert_modifiable(ERC20TokenPool(self.pools[_pool_hash].address_).release(_to, _value))


@private
def _wrap(_token: address, _from: address, _to: address, _value: uint256):
    """
        @dev Function to deposit an original ERC20 token to its corrresponding
             token pool from an address, and mint L ERC20 tokens to another
             address. Both addresses can be the same. This is an internal
             function and is used only within the context of this contract.
        @param _token The address of the ERC20 token.
        @param _from The address from which original token is deposited to its
             token pool.
        @param _to The address to which L tokens should be minted.
        @param _value The amount of original and L tokens.
        @return A bool indicating if the wrap process was successful.
    """
    # deposit currency from _from address
    self._deposit_token_to_pool(_token, _from, _value)
    # mint currency l_token to _to address
    assert_modifiable(ERC20(self.token_addresses[_token].l).mintAndAuthorizeMinter(_to, _value))


@private
def _unwrap(_token: address, _from: address, _to: address, _value: uint256):
    """
        @dev Function to burn L ERC20 tokens from an address and deposit release
             equal amount of original ERC20 tokens from the corrresponding
             token pool to another address. Both addresses can be the same. This is an internal
             function and is used only within the context of this contract.
        @param _token The address of the ERC20 token.
        @param _from The address from which L token should be burned.
        @param _to The address to which original tokens should be released from
             the token pool.
        @param _value The amount of original and L tokens.
        @return A bool indicating if the unwrap process was successful.
    """
    # burrn currency l_token from _from address
    assert_modifiable(ERC20(self.token_addresses[_token].l).burnAsAuthorizedMinter(_from, _value))
    # release currency to _to address
    self._withdraw_token_from_pool(_token, _to, _value)


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


### External functions ###


@public
@constant
def mft_hash(_address: address, _currency: address, _expiry: timestamp, _underlying: address, _strike_price: uint256) -> bytes32:
    """
        Function to get the hash of a MFT, given its address and indicators.
        @param _address The address of the MFT.
        @param _currency The address of the currency token in the MFT.
        @param _expiry The timestamp when the MFT expires.
        @param _underlying The address of the underlying token in the MFT.
        @param _strike_price The price of the underlying per currency at _expiry.
        @return The result of the internal function _mft_hash()
    """
    return self._mft_hash(_address, _currency, _expiry, _underlying, _strike_price)


@public
@constant
def is_token_supported(_token: address) -> bool:
    """
        @dev Function to verify if a given ERC20 token is supported.
        @param _token The address of the ERC20 token.
        @return The result of the internal function _is_token_supported()
    """
    return self._is_token_supported(_token)


@public
@constant
def mft_addresses(_token: address) -> (address, address, address, address, address):
    """
        @dev Function to get the L, F, I, S, and U addresses for a given ERC20
             token
        @param _token The address of the ERC20 token.
        @return The result of the internal function _mft_addresses()
    """
    return self._mft_addresses(_token)


@public
@constant
def f_token(_currency: address, _expiry: timestamp) -> (address, uint256):
    _mft_hash: bytes32 = self._mft_hash(
        self.token_addresses[_currency].f, _currency, _expiry, ZERO_ADDRESS, 0)

    return self.token_addresses[_currency].f, MultiFungibleToken(self.token_addresses[_currency].f).hash_to_id(_mft_hash)


@public
@constant
def i_token(_currency: address, _expiry: timestamp) -> (address, uint256):
    _mft_hash: bytes32 = self._mft_hash(
        self.token_addresses[_currency].i, _currency, _expiry, ZERO_ADDRESS, 0)

    return self.token_addresses[_currency].i, MultiFungibleToken(self.token_addresses[_currency].i).hash_to_id(_mft_hash)


@public
@constant
def s_token(_currency: address, _expiry: timestamp, _underlying: address, _strike_price: uint256) -> (address, uint256):
    _mft_hash: bytes32 = self._mft_hash(self.token_addresses[_currency].s,
        _currency, _expiry, _underlying, _strike_price)

    return self.token_addresses[_currency].s, MultiFungibleToken(self.token_addresses[_currency].s).hash_to_id(_mft_hash)


@public
@constant
def u_token(_currency: address, _expiry: timestamp, _underlying: address, _strike_price: uint256) -> (address, uint256):
    _mft_hash: bytes32 = self._mft_hash(self.token_addresses[_currency].u,
        _currency, _expiry, _underlying, _strike_price)

    return self.token_addresses[_currency].u, MultiFungibleToken(self.token_addresses[_currency].u).hash_to_id(_mft_hash)


@public
@constant
def pool_hash(_token: address) -> bytes32:
    """
        @dev Function to get the hash of a ERC20 Token Pool, given the ERC20
             address.
        @param _token The address of the ERC20 Token.
        @return The result of the internal function _pool_hash()
    """
    return self._pool_hash(_token)


# Admin functions


@public
def mint_and_self_authorize_erc20(_token: address, _to: address, _value: uint256) -> bool:
    assert self.initialized
    assert_modifiable(ERC20(_token).mintAndAuthorizeMinter(_to, _value))
    return True


@public
def burn_as_self_authorized_erc20(_token: address, _from: address, _value: uint256) -> bool:
    assert self.initialized
    assert_modifiable(ERC20(_token).burnAsAuthorizedMinter(_from, _value))
    return True


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
    assert _template_type == TEMPLATE_TOKEN_POOL or \
           _template_type == TEMPLATE_ERC20 or \
           _template_type == TEMPLATE_MFT or \
           _template_type == TEMPLATE_LERC20
    self.templates[_template_type] = _address
    return True


@public
def set_token_support(_token: address, _is_active: bool) -> bool:
    """
        @dev Function to toggle support of a token. Only the Protocol DAO can
             call this function.
        @param _token The address of the token.
        @param _is_active Bool indicating whether the token should be supported
             or not.
        @return A bool with a value of "True" indicating the token support has
             been toggled.
    """
    assert self.initialized
    assert not _token == self.LST
    assert msg.sender == self.protocol_dao
    assert _token.is_contract
    _pool_hash: bytes32 = self._pool_hash(_token)
    if _is_active:
        _name: string[64] = ERC20(_token).name()
        _symbol: string[32] = ERC20(_token).symbol()
        _decimals: uint256 = ERC20(_token).decimals()
        assert self.pools[_pool_hash].address_ == ZERO_ADDRESS, "token pool already exists"
        _pool_address: address = create_forwarder_to(self.templates[TEMPLATE_TOKEN_POOL])
        assert_modifiable(ERC20TokenPool(_pool_address).initialize(_token))
        # l token
        _l_address: address = create_forwarder_to(self.templates[TEMPLATE_LERC20])
        assert_modifiable(LERC20(_l_address).initialize(_name, _symbol, _decimals, 0))
        # i token
        _i_address: address = create_forwarder_to(self.templates[TEMPLATE_MFT])
        assert_modifiable(MultiFungibleToken(_i_address).initialize(self.protocol_dao, [
            self, self.daos[DAO_INTEREST_POOL], self.daos[DAO_UNDERWRITER_POOL],
            self.daos[DAO_MARKET], self.daos[DAO_SHIELD_PAYOUT]
        ]))
        # f token
        _f_address: address = create_forwarder_to(self.templates[TEMPLATE_MFT])
        assert_modifiable(MultiFungibleToken(_f_address).initialize(self.protocol_dao, [
            self, self.daos[DAO_INTEREST_POOL], self.daos[DAO_UNDERWRITER_POOL],
            self.daos[DAO_MARKET], self.daos[DAO_SHIELD_PAYOUT]
        ]))
        # s token
        _s_address: address = create_forwarder_to(self.templates[TEMPLATE_MFT])
        assert_modifiable(MultiFungibleToken(_s_address).initialize(self.protocol_dao, [
            self, self.daos[DAO_INTEREST_POOL], self.daos[DAO_UNDERWRITER_POOL],
            self.daos[DAO_MARKET], self.daos[DAO_SHIELD_PAYOUT]
        ]))
        # u token
        _u_address: address = create_forwarder_to(self.templates[TEMPLATE_MFT])
        assert_modifiable(MultiFungibleToken(_u_address).initialize(self.protocol_dao, [
            self, self.daos[DAO_INTEREST_POOL], self.daos[DAO_UNDERWRITER_POOL],
            self.daos[DAO_MARKET], self.daos[DAO_SHIELD_PAYOUT]
        ]))

        self.pools[_pool_hash] = Pool({
            currency: _token,
            name: _name,
            address_: _pool_address,
            operator: self,
            hash: _pool_hash
        })
        self.token_addresses[_token] = TokenAddress({
            eth: _token,
            l: _l_address,
            i: _i_address,
            f: _f_address,
            s: _s_address,
            u: _u_address
        })


    else:
        assert not self.pools[_pool_hash].address_ == ZERO_ADDRESS, "currency pool does not exist"
        clear(self.pools[_pool_hash].address_)
        clear(self.pools[_pool_hash].name)
        assert_modifiable(ERC20TokenPool(self.pools[_pool_hash].address_).destroy())

    return True


# Escape-hatches

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
        _token = self.token_addresses[_currency].l
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
        _token = self.token_addresses[_currency].f
    if _mft_type == MFT_TYPE_I:
        _token = self.token_addresses[_currency].i
    if _mft_type == MFT_TYPE_S:
        _token = self.token_addresses[_currency].s
    if _mft_type == MFT_TYPE_U:
        _token = self.token_addresses[_currency].u
    assert not _token == ZERO_ADDRESS
    self._transfer_balance_mft(_token, _currency, _expiry, _underlying, _strike_price)
    return True


# Non=admin functions


@public
def wrap(_token: address, _value: uint256) -> bool:
    assert self.initialized
    assert not self.paused
    self._wrap(_token, msg.sender, msg.sender, _value)

    return True


@public
def unwrap(_token: address, _value: uint256) -> bool:
    assert self.initialized
    assert not self.paused
    self._unwrap(_token, msg.sender, msg.sender, _value)

    return True


@public
def authorized_unwrap(_token: address, _to: address, _value: uint256) -> bool:
    assert self.initialized
    assert not self.paused
    assert msg.sender == self.daos[DAO_MARKET]
    self._unwrap(_token, msg.sender, _to, _value)

    return True


@public
def authorized_transfer_l(_token: address, _from: address, _to: address, _value: uint256) -> bool:
    assert self.initialized
    assert not self.paused
    assert msg.sender in [
        self.daos[DAO_INTEREST_POOL], self.daos[DAO_UNDERWRITER_POOL]
    ]
    assert_modifiable(ERC20(self.token_addresses[_token].l).transferFrom(
        _from, _to, _value))

    return True


@public
def authorized_transfer_erc20(_token: address, _from: address, _to: address, _value: uint256) -> bool:
    assert self.initialized
    assert not self.paused
    assert msg.sender in [
        self.daos[DAO_INTEREST_POOL], self.daos[DAO_UNDERWRITER_POOL],
        self.registries[REGISTRY_POOL_NAME]
    ]
    assert_modifiable(ERC20(_token).transferFrom(_from, _to, _value))
    return True


@public
def authorized_deposit_token(_token: address, _from: address, _value: uint256) -> bool:
    assert self.initialized
    assert not self.paused
    assert msg.sender == self.daos[DAO_MARKET]
    self._deposit_token_to_pool(_token, _from, _value)

    return True


@public
def authorized_withdraw_token(_token: address, _to: address, _value: uint256) -> bool:
    assert self.initialized
    assert not self.paused
    assert msg.sender == self.daos[DAO_MARKET]
    self._withdraw_token_from_pool(_token, _to, _value)
    return True
