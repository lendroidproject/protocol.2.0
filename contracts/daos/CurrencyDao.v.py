# Vyper version of the Lendroid protocol v2
# THIS CONTRACT HAS NOT BEEN AUDITED!


from contracts.interfaces import ERC20
from contracts.interfaces import ERC1155
from contracts.interfaces import ContinuousCurrencyPoolERC20


# Structs
struct Currency:
    currency_address: address
    l_currency_address: address
    i_currency_address: address
    f_currency_address: address
    s_currency_address: address
    u_currency_address: address

struct Pool:
    currency_address: address
    pool_name: string[64]
    pool_address: address
    pool_operator: address
    hash: bytes32


protocol_currency_address: public(address)
protocol_dao_address: public(address)
owner: public(address)
# currency_address => Currency
currencies: public(map(address, Currency))
# pool_hash => Pool
pools: public(map(bytes32, Pool))
# template_name => template_contract_address
templates: public(map(uint256, address))

TEMPLATE_TYPE_CURRENCY_POOL: public(uint256)
TEMPLATE_TYPE_CURRENCY_ERC20: public(uint256)
TEMPLATE_TYPE_CURRENCY_ERC1155: public(uint256)


initialized: public(bool)


@private
@constant
def _is_initialized() -> bool:
    return self.initialized == True


@public
def initialize(
        _owner: address,
        _protocol_currency_address: address,
        _template_address_currency_pool: address,
        _template_address_currency_erc20: address,
        _template_address_currency_erc1155: address
        ) -> bool:
    assert not self._is_initialized()
    self.initialized = True
    self.owner = _owner
    self.protocol_dao_address = msg.sender
    self.protocol_currency_address = _protocol_currency_address

    self.TEMPLATE_TYPE_CURRENCY_POOL = 1
    self.TEMPLATE_TYPE_CURRENCY_ERC20 = 2
    self.TEMPLATE_TYPE_CURRENCY_ERC1155 = 3

    self.templates[self.TEMPLATE_TYPE_CURRENCY_POOL] = _template_address_currency_pool
    self.templates[self.TEMPLATE_TYPE_CURRENCY_ERC20] = _template_address_currency_erc20
    self.templates[self.TEMPLATE_TYPE_CURRENCY_ERC1155] = _template_address_currency_erc1155

    return True


@private
@constant
def _pool_hash(_currency_address: address) -> bytes32:
    return keccak256(
        concat(
            convert(self.protocol_dao_address, bytes32),
            convert(_currency_address, bytes32)
        )
    )


@private
@constant
def _is_currency_valid(_currency_address: address) -> bool:
    return self.pools[self._pool_hash(_currency_address)].pool_address.is_contract


@private
def _deposit_erc20(_currency_address: address, _from: address, _to: address, _value: uint256):
    assert_modifiable(ERC20(_currency_address).transferFrom(_from, _to, _value))


@private
def _deposit_currency_to_pool(_currency_address: address, _from: address, _value: uint256):
    # validate currency address
    _pool_hash: bytes32 = self._pool_hash(_currency_address)
    assert self.pools[_pool_hash].pool_address.is_contract, "currency is not supported"
    # transfer currency to currency pool
    self._deposit_erc20(_currency_address, _from, self.pools[_pool_hash].pool_address, _value)
    # update supply in currency pool
    assert_modifiable(ContinuousCurrencyPoolERC20(self.pools[_pool_hash].pool_address).update_total_supplied(_value))


@private
def _release_currency_from_pool(_currency_address: address, _to: address, _value: uint256):
    # validate currency address
    _pool_hash: bytes32 = self._pool_hash(_currency_address)
    assert self.pools[_pool_hash].pool_address.is_contract, "currency is not supported"
    # release_currency from currency pool
    _external_call_successful: bool = ContinuousCurrencyPoolERC20(self.pools[_pool_hash].pool_address).release_currency(_to, _value)
    assert _external_call_successful


@private
def _mint_and_self_authorize_erc20(_currency_address: address, _to: address, _value: uint256):
    assert_modifiable(ERC20(_currency_address).mintAndAuthorizeMinter(_to, _value))

@private
def _burn_as_self_authorized_erc20(_currency_address: address, _to: address, _value: uint256):
    assert_modifiable(ERC20(_currency_address).burnFrom(_to, _value))


@private
def _create_erc1155_type(_currency_address: address, _expiry_label: string[3]) -> uint256:
    _expiry_id: uint256 = ERC1155(_currency_address).create_token_type(0, _expiry_label)
    assert as_unitless_number(_expiry_id) == as_unitless_number(ERC1155(_currency_address).nonce()) + 1
    return _expiry_id


@private
def _mint_erc1155(_currency_address: address, _id: uint256, _to: address, _value: uint256):
    assert_modifiable(ERC1155(_currency_address).mint(_id, _to, _value))


@private
def _burn_erc1155(_currency_address: address, _id: uint256, _to: address, _value: uint256):
    assert_modifiable(ERC1155(_currency_address).burn(_id, _to, _value))


@private
@constant
def _multi_fungible_addresses(_currency_address: address) -> (address, address, address, address, address):
    return self.currencies[_currency_address].l_currency_address, self.currencies[_currency_address].i_currency_address, self.currencies[_currency_address].f_currency_address, self.currencies[_currency_address].s_currency_address, self.currencies[_currency_address].u_currency_address


@public
@constant
def is_currency_valid(_currency_address: address) -> bool:
    return self._is_currency_valid(_currency_address)


@public
@constant
def multi_fungible_addresses(_currency_address: address) -> (address, address, address, address, address):
    return self._multi_fungible_addresses(_currency_address)


@public
def deposit_multi_fungible_l_currency(_currency_address: address, _from: address, _to: address, _value: uint256) -> bool:
    assert self._is_initialized()
    self._deposit_erc20(self.currencies[_currency_address].l_currency_address, _from, _to, _value)
    return True


@public
def deposit_erc20(_currency_address: address, _from: address, _to: address, _value: uint256) -> bool:
    assert self._is_initialized()
    self._deposit_erc20(_currency_address, _from, _to, _value)
    return True


@public
def deposit_currency_to_pool(_currency_address: address, _from: address, _value: uint256) -> bool:
    assert self._is_initialized()
    self._deposit_currency_to_pool(_currency_address, _from, _value)
    return True


@public
def release_currency_from_pool(_currency_address: address, _to: address, _value: uint256) -> bool:
    assert self._is_initialized()
    self._release_currency_from_pool(_currency_address, _to, _value)
    return True


@public
def create_erc1155_type(_currency_address: address, _expiry_label: string[3]) -> uint256:
    assert self._is_initialized()
    return self._create_erc1155_type(_currency_address, _expiry_label)


@public
def mint_and_self_authorize_erc20(_currency_address: address, _to: address, _value: uint256) -> bool:
    assert self._is_initialized()
    self._mint_and_self_authorize_erc20(_currency_address, _to, _value)
    return True


@public
def burn_as_self_authorized_erc20(_currency_address: address, _to: address, _value: uint256) -> bool:
    assert self._is_initialized()
    self._burn_as_self_authorized_erc20(_currency_address, _to, _value)
    return True


@public
def mint_erc1155(_currency_address: address, _id: uint256, _to: address, _value: uint256) -> bool:
    assert self._is_initialized()
    self._mint_erc1155(_currency_address, _id, _to, _value)
    return True


@public
def burn_erc1155(_currency_address: address, _id: uint256, _to: address, _value: uint256) -> bool:
    assert self._is_initialized()
    self._burn_erc1155(_currency_address, _id, _to, _value)
    return True


@public
@constant
def pool_hash(_currency_address: address) -> bytes32:
    return self._pool_hash(_currency_address)


@public
def set_template(_template_type: uint256, _address: address) -> bool:
    assert self._is_initialized()
    assert msg.sender == self.owner
    assert _template_type == self.TEMPLATE_TYPE_CURRENCY_POOL or \
           _template_type == self.TEMPLATE_TYPE_CURRENCY_ERC20 or \
           _template_type == self.TEMPLATE_TYPE_CURRENCY_ERC1155
    self.templates[_template_type] = _address
    return True


@public
def set_currency_support(_currency_address: address, _is_active: bool) -> bool:
    assert self._is_initialized()
    assert not _currency_address == self.protocol_currency_address
    assert msg.sender == self.owner
    assert _currency_address.is_contract
    _pool_hash: bytes32 = self._pool_hash(_currency_address)
    if _is_active:
        _currency_name: string[64] = ERC20(_currency_address).name()
        _currency_symbol: string[32] = ERC20(_currency_address).symbol()
        _currency_decimals: uint256 = ERC20(_currency_address).decimals()
        assert self.pools[_pool_hash].pool_address == ZERO_ADDRESS, "currency pool already exists"
        _pool_address: address = create_forwarder_to(self.templates[self.TEMPLATE_TYPE_CURRENCY_POOL])
        assert_modifiable(ContinuousCurrencyPoolERC20(_pool_address).initialize(_currency_address))
        # l token
        _l_currency_address: address = create_forwarder_to(self.templates[self.TEMPLATE_TYPE_CURRENCY_ERC20])
        # _l_currency_name: string[64] = concat("L ", slice(_currency_name, start=0, len=62))
        # _l_currency_symbol: string[32] = concat("L", slice(_currency_symbol, start=0, len=31))
        assert_modifiable(ERC20(_l_currency_address).initialize(
            _currency_name, _currency_symbol, _currency_decimals, 0))
        # i token
        _i_currency_address: address = create_forwarder_to(self.templates[self.TEMPLATE_TYPE_CURRENCY_ERC1155])
        assert_modifiable(ERC1155(_i_currency_address).initialize())
        # f token
        _f_currency_address: address = create_forwarder_to(self.templates[self.TEMPLATE_TYPE_CURRENCY_ERC1155])
        assert_modifiable(ERC1155(_f_currency_address).initialize())
        # s token
        _s_currency_address: address = create_forwarder_to(self.templates[self.TEMPLATE_TYPE_CURRENCY_ERC1155])
        assert_modifiable(ERC1155(_s_currency_address).initialize())
        # u token
        _u_currency_address: address = create_forwarder_to(self.templates[self.TEMPLATE_TYPE_CURRENCY_ERC1155])
        assert_modifiable(ERC1155(_u_currency_address).initialize())

        self.pools[_pool_hash] = Pool({
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
        assert_modifiable(ContinuousCurrencyPoolERC20(self.pools[_pool_hash].pool_address).destroy())

    return True


@public
def currency_to_l_currency(_currency_address: address, _value: uint256) -> bool:
    assert self._is_initialized()
    self._deposit_currency_to_pool(_currency_address, msg.sender, _value)
    # mint currency l_token to msg.sender
    self._mint_and_self_authorize_erc20(self.currencies[_currency_address].l_currency_address, msg.sender, _value)

    return True
