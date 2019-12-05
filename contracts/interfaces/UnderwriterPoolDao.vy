# Events

PoolRegistered: event({_operator: address, _currency_address: address, _pool_address: address})

# Functions

@public
def initialize(_owner: address, _protocol_currency_address: address, _registry_address_pool_name: address, _dao_address_currency: address, _dao_address_market: address, _dao_address_shield_payout: address, _template_address_underwriter_pool: address, _template_address_currency_erc20: address) -> bool:
    pass

@constant
@public
def currency_dao_address() -> address:
    pass

@constant
@public
def protocol_currency_stake_value(_pool_name: string[64]) -> uint256:
    pass

@public
def set_minimum_multi_fungible_currency_support_fee(_value: uint256) -> bool:
    pass

@public
def set_fee_multiplier_per_multi_fungible_currency_supported(_multi_fungible_currency_count: uint256, _value: uint256) -> bool:
    pass

@public
def set_template(_template_type: uint256, _address: address) -> bool:
    pass

@public
def register_pool(_accepts_public_contributions: bool, _currency_address: address, _name: string[64], _symbol: string[32], _initial_exchange_rate: uint256, _i_currency_operator_fee_percentage: uint256, _s_currency_operator_fee_percentage: uint256) -> bool:
    pass

@public
def register_expiry(_pool_name: string[64], _expiry: uint256(sec, positional), _underlying_address: address, _strike_price: uint256) -> (bool, bytes32, bytes32, bytes32, uint256, uint256, uint256):
    pass

@public
def remove_expiry(_pool_name: string[64], _currency_address: address, _expiry: uint256(sec, positional), _underlying_address: address, _strike_price: uint256) -> bool:
    pass

@public
def deposit_l_currency(_pool_name: string[64], _from: address, _value: uint256) -> bool:
    pass

@public
def l_currency_to_i_and_s_and_u_currency(_currency_address: address, _expiry: uint256(sec, positional), _underlying_address: address, _strike_price: uint256, _value: uint256) -> bool:
    pass

@public
def l_currency_from_i_and_s_and_u_currency(_currency_address: address, _expiry: uint256(sec, positional), _underlying_address: address, _strike_price: uint256, _value: uint256) -> bool:
    pass

@public
def exercise_underwriter_currency(_pool_name: string[64], _currency_address: address, _expiry: uint256(sec, positional), _underlying_address: address, _strike_price: uint256, _currency_quantity: uint256) -> bool:
    pass

@constant
@public
def protocol_currency_address() -> address:
    pass

@constant
@public
def protocol_dao_address() -> address:
    pass

@constant
@public
def owner() -> address:
    pass

@constant
@public
def daos(arg0: uint256) -> address:
    pass

@constant
@public
def registries(arg0: uint256) -> address:
    pass

@constant
@public
def templates(arg0: uint256) -> address:
    pass

@constant
@public
def pools__currency_address(arg0: string[64]) -> address:
    pass

@constant
@public
def pools__pool_name(arg0: string[64]) -> string[64]:
    pass

@constant
@public
def pools__pool_address(arg0: string[64]) -> address:
    pass

@constant
@public
def pools__pool_operator(arg0: string[64]) -> address:
    pass

@constant
@public
def pools__multi_fungible_currencies_supported(arg0: string[64]) -> uint256:
    pass

@constant
@public
def pools__protocol_currency_staked(arg0: string[64]) -> uint256:
    pass

@constant
@public
def multi_fungible_currencies__parent_currency_address(arg0: bytes32) -> address:
    pass

@constant
@public
def multi_fungible_currencies__currency_address(arg0: bytes32) -> address:
    pass

@constant
@public
def multi_fungible_currencies__expiry_timestamp(arg0: bytes32) -> uint256(sec, positional):
    pass

@constant
@public
def multi_fungible_currencies__underlying_address(arg0: bytes32) -> address:
    pass

@constant
@public
def multi_fungible_currencies__strike_price(arg0: bytes32) -> uint256:
    pass

@constant
@public
def multi_fungible_currencies__has_id(arg0: bytes32) -> bool:
    pass

@constant
@public
def multi_fungible_currencies__token_id(arg0: bytes32) -> uint256:
    pass

@constant
@public
def multi_fungible_currencies__hash(arg0: bytes32) -> bytes32:
    pass

@constant
@public
def fee_multiplier_per_multi_fungible_currency_supported(arg0: uint256) -> uint256:
    pass

@constant
@public
def minimum_multi_fungible_currency_support_fee() -> uint256:
    pass

@constant
@public
def protocol_currency_staked(arg0: string[64], arg1: bytes32) -> uint256:
    pass

@constant
@public
def MULTI_FUNGIBLE_CURRENCY_DIMENSION_I() -> uint256:
    pass

@constant
@public
def MULTI_FUNGIBLE_CURRENCY_DIMENSION_F() -> uint256:
    pass

@constant
@public
def MULTI_FUNGIBLE_CURRENCY_DIMENSION_S() -> uint256:
    pass

@constant
@public
def MULTI_FUNGIBLE_CURRENCY_DIMENSION_U() -> uint256:
    pass

@constant
@public
def REGISTRY_TYPE_POOL_NAME() -> uint256:
    pass

@constant
@public
def DAO_TYPE_CURRENCY() -> uint256:
    pass

@constant
@public
def DAO_TYPE_MARKET() -> uint256:
    pass

@constant
@public
def DAO_TYPE_SHIELD_PAYOUT() -> uint256:
    pass

@constant
@public
def TEMPLATE_TYPE_UNDERWRITER_POOL() -> uint256:
    pass

@constant
@public
def TEMPLATE_TYPE_CURRENCY_ERC20() -> uint256:
    pass

@constant
@public
def initialized() -> bool:
    pass
