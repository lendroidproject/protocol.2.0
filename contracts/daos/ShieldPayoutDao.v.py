# Vyper version of the Lendroid protocol v2
# THIS CONTRACT HAS NOT BEEN AUDITED!


from contracts.interfaces import CurrencyDao
from contracts.interfaces import ShieldPayoutGraph


protocol_currency_address: public(address)
protocol_dao_address: public(address)
owner: public(address)
# currency_hash => contract_address
payout_graph_addresses: public(map(bytes32, address))
# daos
DAO_TYPE_CURRENCY: public(uint256)
DAO_TYPE_UNDERWRITER_POOL: public(uint256)
# dao_type => dao_address
daos: public(map(uint256, address))
# templates
TEMPLATE_TYPE_SHIELD_PAYOUT_ERC20: public(uint256)
# template_name => template_contract_address
templates: public(map(uint256, address))

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
        _template_address_shield_payout_erc20: address
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

    self.TEMPLATE_TYPE_SHIELD_PAYOUT_ERC20 = 1
    self.templates[self.TEMPLATE_TYPE_SHIELD_PAYOUT_ERC20] = _template_address_shield_payout_erc20

    return True


@public
def initialize_payout_graph(_currency_address: address,
    _underlying_address: address, _expiry: timestamp, _strike_price: uint256,
    _s_hash: bytes32, _u_hash: bytes32
    ) -> bool:
    assert self._is_initialized()
    assert msg.sender == self.daos[self.DAO_TYPE_UNDERWRITER_POOL]
    # deploy and initialize payout graph
    _payout_address: address = create_forwarder_to(self.templates[self.TEMPLATE_TYPE_SHIELD_PAYOUT_ERC20])
    self.payout_graph_addresses[_s_hash] = _payout_address
    self.payout_graph_addresses[_u_hash] = _payout_address
    assert_modifiable(ShieldPayoutGraph(_payout_address).initialize(
        _currency_address, _underlying_address, _expiry, _strike_price))

    return True


@private
@constant
def _multi_fungible_currency_hash(parent_currency_address: address, _currency_address: address, _expiry: timestamp, _underlying_address: address, _strike_price: uint256) -> bytes32:
    return keccak256(
        concat(
            convert(self.protocol_dao_address, bytes32),
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
@constant
def _shield_payout(_s_hash: bytes32) -> uint256:
    return ShieldPayoutGraph(self.payout_graph_addresses[_s_hash]).SHIELD_PAYOUT_VALUE()


@private
@constant
def _underwriter_payout(_u_hash: bytes32) -> uint256:
    return ShieldPayoutGraph(self.payout_graph_addresses[_u_hash]).UNDERWRITER_PAYOUT_VALUE()


@private
def _mint_and_self_authorize_erc20(_currency_address: address, _to: address, _value: uint256):
    assert_modifiable(CurrencyDao(self.daos[self.DAO_TYPE_CURRENCY]).mint_and_self_authorize_erc20(_currency_address, _to, _value))


@private
def _burn_erc1155(_currency_address: address, _id: uint256, _to: address, _value: uint256):
    assert_modifiable(CurrencyDao(self.daos[self.DAO_TYPE_CURRENCY]).burn_erc1155(_currency_address, _id, _to, _value))


@public
def l_currency_from_s_currency(_currency_address: address, _s_hash: bytes32,
    _s_token_id: uint256, _currency_quantity: uint256) -> bool:
    assert self._is_initialized()
    assert msg.sender == self.daos[self.DAO_TYPE_UNDERWRITER_POOL]
    _l_currency_address: address = ZERO_ADDRESS
    _i_currency_address: address = ZERO_ADDRESS
    _f_currency_address: address = ZERO_ADDRESS
    _s_currency_address: address = ZERO_ADDRESS
    _u_currency_address: address = ZERO_ADDRESS
    _l_currency_address, _i_currency_address, _f_currency_address, _s_currency_address, _u_currency_address = self._multi_fungible_addresses(_currency_address)
    # mint _payout_value in l_currency
    _payout_value: uint256 = self._shield_payout(_s_hash)
    assert as_unitless_number(_payout_value) > 0
    self._mint_and_self_authorize_erc20(_l_currency_address, msg.sender,
        as_unitless_number(_payout_value) * as_unitless_number(_currency_quantity))
    # burn s_currency
    self._burn_erc1155(
        _s_currency_address,
        _s_token_id,
        msg.sender,
        as_unitless_number(_currency_quantity) * (10 ** 18)
    )

    return True


@public
def l_currency_from_u_currency(_currency_address: address, _u_hash: bytes32,
    _u_token_id: uint256, _currency_quantity: uint256) -> bool:
    assert self._is_initialized()
    assert msg.sender == self.daos[self.DAO_TYPE_UNDERWRITER_POOL]
    _l_currency_address: address = ZERO_ADDRESS
    _i_currency_address: address = ZERO_ADDRESS
    _f_currency_address: address = ZERO_ADDRESS
    _s_currency_address: address = ZERO_ADDRESS
    _u_currency_address: address = ZERO_ADDRESS
    _l_currency_address, _i_currency_address, _f_currency_address, _s_currency_address, _u_currency_address = self._multi_fungible_addresses(_currency_address)
    # mint _payout_value in l_currency
    _payout_value: uint256 = self._underwriter_payout(_u_hash)
    assert as_unitless_number(_payout_value) > 0
    self._mint_and_self_authorize_erc20(_l_currency_address, msg.sender,
        as_unitless_number(_payout_value) * as_unitless_number(_currency_quantity))
    # burn s_currency
    self._burn_erc1155(
        _u_currency_address,
        _u_token_id,
        msg.sender,
        as_unitless_number(_currency_quantity) * (10 ** 18)
    )

    return True
