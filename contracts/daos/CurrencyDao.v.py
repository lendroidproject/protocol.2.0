# Vyper version of the Lendroid protocol v2
# THIS CONTRACT HAS NOT BEEN AUDITED!


from contracts.interfaces import ERC20
from contracts.interfaces import MultiFungibleToken
from contracts.interfaces import ERC20TokenPool


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
owner: public(address)
# eth address of token => TokenAddress
token_addresses: public(map(address, TokenAddress))
# pool_hash => Pool
pools: public(map(bytes32, Pool))
# dao_type => dao_address
daos: public(map(uint256, address))
# registry_type => registry_address
registries: public(map(uint256, address))
# template_name => template_contract_address
templates: public(map(uint256, address))

DAO_INTEREST_POOL: public(uint256)
DAO_UNDERWRITER_POOL: public(uint256)
DAO_MARKET: public(uint256)

REGISTRY_POOL_NAME: public(uint256)

TEMPLATE_TYPE_TOKEN_POOL: public(uint256)
TEMPLATE_TYPE_TOKEN_ERC20: public(uint256)
TEMPLATE_TYPE_TOKEN_MULTI_FUNGIBLE: public(uint256)

initialized: public(bool)
paused: public(bool)


@public
def initialize(
        _owner: address,
        _LST: address,
        _template_token_pool: address,
        _template_erc20: address,
        _template_mft: address,
        _pool_name_registry: address,
        _dao_interest_pool: address,
        _dao_underwriter_pool: address,
        _dao_market: address
        ) -> bool:
    assert not self.initialized
    self.initialized = True
    self.owner = _owner
    self.protocol_dao = msg.sender
    self.LST = _LST

    self.DAO_INTEREST_POOL = 1
    self.daos[self.DAO_INTEREST_POOL] = _dao_interest_pool
    self.DAO_UNDERWRITER_POOL = 2
    self.daos[self.DAO_UNDERWRITER_POOL] = _dao_underwriter_pool
    self.DAO_MARKET = 3
    self.daos[self.DAO_MARKET] = _dao_market

    self.REGISTRY_POOL_NAME = 1
    self.registries[self.REGISTRY_POOL_NAME] = _pool_name_registry

    self.TEMPLATE_TYPE_TOKEN_POOL = 1
    self.TEMPLATE_TYPE_TOKEN_ERC20 = 2
    self.TEMPLATE_TYPE_TOKEN_MULTI_FUNGIBLE = 3

    self.templates[self.TEMPLATE_TYPE_TOKEN_POOL] = _template_token_pool
    self.templates[self.TEMPLATE_TYPE_TOKEN_ERC20] = _template_erc20
    self.templates[self.TEMPLATE_TYPE_TOKEN_MULTI_FUNGIBLE] = _template_mft

    return True


@private
@constant
def _pool_hash(_currency: address) -> bytes32:
    return keccak256(
        concat(
            convert(self.protocol_dao, bytes32),
            convert(_currency, bytes32)
        )
    )


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
def _is_token_supported(_token: address) -> bool:
    return self.pools[self._pool_hash(_token)].address_.is_contract


@private
def _transfer_erc20(_token: address, _from: address, _to: address, _value: uint256):
    assert_modifiable(ERC20(_token).transferFrom(_from, _to, _value))


@private
def _deposit_token_to_pool(_token: address, _from: address, _value: uint256):
    # validate currency address
    _pool_hash: bytes32 = self._pool_hash(_token)
    assert self.pools[_pool_hash].address_.is_contract, "token is not supported"
    # transfer currency to currency pool
    self._transfer_erc20(_token, _from, self.pools[_pool_hash].address_, _value)


@private
def _withdraw_token_from_pool(_token: address, _to: address, _value: uint256):
    # validate currency address
    _pool_hash: bytes32 = self._pool_hash(_token)
    assert self.pools[_pool_hash].address_.is_contract, "token is not supported"
    # release token from token pool
    assert_modifiable(ERC20TokenPool(self.pools[_pool_hash].address_).release(_to, _value))


@private
def _mint_and_self_authorize_erc20(_token: address, _to: address, _value: uint256):
    assert_modifiable(ERC20(_token).mintAndAuthorizeMinter(_to, _value))


@private
def _burn_as_self_authorized_erc20(_token: address, _to: address, _value: uint256):
    assert_modifiable(ERC20(_token).burnAsAuthorizedMinter(_to, _value))


@private
@constant
def _mft_addresses(_token: address) -> (address, address, address, address, address):
    return self.token_addresses[_token].l, self.token_addresses[_token].i, self.token_addresses[_token].f, self.token_addresses[_token].s, self.token_addresses[_token].u


@private
def _wrap(_token: address, _from: address, _to: address, _value: uint256):
    # deposit currency from _from address
    self._deposit_token_to_pool(_token, _from, _value)
    # mint currency l_token to _to address
    self._mint_and_self_authorize_erc20(self.token_addresses[_token].l, _to, _value)


@private
def _unwrap(_token: address, _from: address, _to: address, _value: uint256):
    # burrn currency l_token from _from address
    self._burn_as_self_authorized_erc20(self.token_addresses[_token].l, _from, _value)
    # release currency to _to address
    self._withdraw_token_from_pool(_token, _to, _value)


@public
@constant
def mft_hash(_address: address, _currency: address, _expiry: timestamp, _underlying: address, _strike_price: uint256) -> bytes32:
    return self._mft_hash(_address, _currency, _expiry, _underlying, _strike_price)


@public
@constant
def is_token_supported(_token: address) -> bool:
    return self._is_token_supported(_token)


@public
@constant
def mft_addresses(_token: address) -> (address, address, address, address, address):
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
def mint_and_self_authorize_erc20(_token: address, _to: address, _value: uint256) -> bool:
    assert self.initialized
    self._mint_and_self_authorize_erc20(_token, _to, _value)
    return True


@public
def burn_as_self_authorized_erc20(_token: address, _to: address, _value: uint256) -> bool:
    assert self.initialized
    self._burn_as_self_authorized_erc20(_token, _to, _value)
    return True


@public
@constant
def pool_hash(_token: address) -> bytes32:
    return self._pool_hash(_token)


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
        _token = self.token_addresses[_currency].l
    self._transfer_balance_erc20(_currency)
    return True


@public
def escape_hatch_sufi(_sufi_type: int128, _currency: address, _expiry: timestamp, _underlying: address, _strike_price: uint256) -> bool:
    assert self.initialized
    assert msg.sender == self.owner
    _token: address = ZERO_ADDRESS
    if _sufi_type == 1:
        _token = self.token_addresses[_currency].f
    if _sufi_type == 2:
        _token = self.token_addresses[_currency].i
    if _sufi_type == 3:
        _token = self.token_addresses[_currency].s
    if _sufi_type == 4:
        _token = self.token_addresses[_currency].u
    assert not _token == ZERO_ADDRESS
    self._transfer_balance_mft(_token, _currency, _expiry, _underlying, _strike_price)
    return True


@public
def set_template(_template_type: uint256, _address: address) -> bool:
    assert self.initialized
    assert msg.sender == self.owner
    assert _template_type == self.TEMPLATE_TYPE_TOKEN_POOL or \
           _template_type == self.TEMPLATE_TYPE_TOKEN_ERC20 or \
           _template_type == self.TEMPLATE_TYPE_TOKEN_MULTI_FUNGIBLE
    self.templates[_template_type] = _address
    return True


@public
def set_token_support(_token: address, _is_active: bool) -> bool:
    assert self.initialized
    assert not _token == self.LST
    assert msg.sender == self.owner
    assert _token.is_contract
    _pool_hash: bytes32 = self._pool_hash(_token)
    if _is_active:
        _name: string[64] = ERC20(_token).name()
        _symbol: string[32] = ERC20(_token).symbol()
        _decimals: uint256 = ERC20(_token).decimals()
        assert self.pools[_pool_hash].address_ == ZERO_ADDRESS, "token pool already exists"
        _pool_address: address = create_forwarder_to(self.templates[self.TEMPLATE_TYPE_TOKEN_POOL])
        assert_modifiable(ERC20TokenPool(_pool_address).initialize(_token))
        # l token
        _l_address: address = create_forwarder_to(self.templates[self.TEMPLATE_TYPE_TOKEN_ERC20])
        # _l_currency_name: string[64] = concat("L ", slice(_name, start=0, len=62))
        # _l_currency_symbol: string[32] = concat("L", slice(_symbol, start=0, len=31))
        assert_modifiable(ERC20(_l_address).initialize(
            _name, _symbol, _decimals, 0))
        # i token
        _i_address: address = create_forwarder_to(self.templates[self.TEMPLATE_TYPE_TOKEN_MULTI_FUNGIBLE])
        assert_modifiable(MultiFungibleToken(_i_address).initialize(self.protocol_dao, [
            self.daos[self.DAO_MARKET],
            ZERO_ADDRESS, ZERO_ADDRESS, ZERO_ADDRESS, ZERO_ADDRESS
        ]))
        # f token
        _f_address: address = create_forwarder_to(self.templates[self.TEMPLATE_TYPE_TOKEN_MULTI_FUNGIBLE])
        assert_modifiable(MultiFungibleToken(_f_address).initialize(self.protocol_dao, [
            self.daos[self.DAO_MARKET],
            ZERO_ADDRESS, ZERO_ADDRESS, ZERO_ADDRESS, ZERO_ADDRESS
        ]))
        # s token
        _s_address: address = create_forwarder_to(self.templates[self.TEMPLATE_TYPE_TOKEN_MULTI_FUNGIBLE])
        assert_modifiable(MultiFungibleToken(_s_address).initialize(self.protocol_dao, [
            self.daos[self.DAO_MARKET],
            ZERO_ADDRESS, ZERO_ADDRESS, ZERO_ADDRESS, ZERO_ADDRESS
        ]))
        # u token
        _u_address: address = create_forwarder_to(self.templates[self.TEMPLATE_TYPE_TOKEN_MULTI_FUNGIBLE])
        assert_modifiable(MultiFungibleToken(_u_address).initialize(self.protocol_dao, [
            self.daos[self.DAO_MARKET],
            ZERO_ADDRESS, ZERO_ADDRESS, ZERO_ADDRESS, ZERO_ADDRESS
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
    assert msg.sender == self.daos[self.DAO_MARKET]
    self._unwrap(_token, msg.sender, _to, _value)

    return True


@public
def authorized_transfer_l(_token: address, _from: address, _to: address, _value: uint256) -> bool:
    assert self.initialized
    assert not self.paused
    assert msg.sender in [
        self.daos[self.DAO_INTEREST_POOL], self.daos[self.DAO_UNDERWRITER_POOL]
    ]
    self._transfer_erc20(self.token_addresses[_token].l, _from, _to, _value)
    return True


@public
def authorized_transfer_erc20(_token: address, _from: address, _to: address, _value: uint256) -> bool:
    assert self.initialized
    assert not self.paused
    assert msg.sender in [
        self.daos[self.DAO_INTEREST_POOL], self.daos[self.DAO_UNDERWRITER_POOL],
        self.registries[self.REGISTRY_POOL_NAME]
    ]
    self._transfer_erc20(_token, _from, _to, _value)
    return True


@public
def authorized_deposit_token(_token: address, _from: address, _value: uint256) -> bool:
    assert self.initialized
    assert not self.paused
    assert msg.sender == self.daos[self.DAO_MARKET]
    self._deposit_token_to_pool(_token, _from, _value)

    return True


@public
def authorized_withdraw_token(_token: address, _to: address, _value: uint256) -> bool:
    assert self.initialized
    assert not self.paused
    assert msg.sender == self.daos[self.DAO_MARKET]
    self._withdraw_token_from_pool(_token, _to, _value)
    return True
