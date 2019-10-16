# Events

PoolRegistered: event({_operator: address, _currency_address: address, _pool_address: address})

# Functions

@public
def initialize(_owner: address, _protocol_currency_address: address, _dao_address_currency: address, _template_address_interest_pool: address, _template_address_currency_erc20: address) -> bool:
    pass

@constant
@public
def currency_dao_address() -> address:
    pass

@constant
@public
def offer_registration_fee() -> uint256:
    pass

@constant
@public
def pool_hash(_currency_address: address, _pool_address: address) -> bytes32:
    pass

@public
def set_offer_registration_fee_lookup(_minimum_fee: uint256, _minimum_interval: uint256(sec), _fee_multiplier: uint256, _fee_multiplier_decimals: uint256) -> bool:
    pass

@public
def set_template(_template_type: uint256, _address: address) -> bool:
    pass

@public
def register_pool(_currency_address: address, _name: string[62], _symbol: string[32], _initial_exchange_rate: uint256) -> bool:
    pass

@public
def register_expiry(_pool_hash: bytes32, _expiry: uint256(sec, positional)) -> (bool, bytes32, bytes32, uint256, uint256):
    pass

@public
def deposit_l_currency(_pool_hash: bytes32, _from: address, _value: uint256) -> bool:
    pass

@public
def l_currency_to_i_and_f_currency(_pool_hash: bytes32, _i_hash: bytes32, _f_hash: bytes32, _value: uint256) -> bool:
    pass

@public
def l_currency_from_i_and_f_currency(_pool_hash: bytes32, _i_hash: bytes32, _f_hash: bytes32, _value: uint256) -> bool:
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
def templates(arg0: uint256) -> address:
    pass

@constant
@public
def pools__currency_address(arg0: bytes32) -> address:
    pass

@constant
@public
def pools__pool_name(arg0: bytes32) -> string[64]:
    pass

@constant
@public
def pools__pool_address(arg0: bytes32) -> address:
    pass

@constant
@public
def pools__pool_operator(arg0: bytes32) -> address:
    pass

@constant
@public
def pools__hash(arg0: bytes32) -> bytes32:
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
def offer_registration_fee_lookup__minimum_fee(arg0: address) -> uint256:
    pass

@constant
@public
def offer_registration_fee_lookup__minimum_interval(arg0: address) -> uint256(sec):
    pass

@constant
@public
def offer_registration_fee_lookup__fee_multiplier(arg0: address) -> uint256:
    pass

@constant
@public
def offer_registration_fee_lookup__fee_multiplier_decimals(arg0: address) -> uint256:
    pass

@constant
@public
def offer_registration_fee_lookup__last_registered_at(arg0: address) -> uint256(sec, positional):
    pass

@constant
@public
def offer_registration_fee_lookup__last_paid_fee(arg0: address) -> uint256:
    pass

@constant
@public
def DAO_TYPE_CURRENCY() -> uint256:
    pass

@constant
@public
def TEMPLATE_TYPE_INTEREST_POOL() -> uint256:
    pass

@constant
@public
def TEMPLATE_TYPE_CURRENCY_ERC20() -> uint256:
    pass

@constant
@public
def initialized() -> bool:
    pass
