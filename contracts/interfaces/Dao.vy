# Functions

@constant
@public
def offer_registration_fee(_pool_type: uint256) -> uint256:
    pass

@public
def set_expiry_support(_timestamp: uint256(sec, positional), _label: string[3], _is_active: bool) -> bool:
    pass

@public
def set_currency_support(_currency_address: address, _is_active: bool, _pool_type: uint256, _currency_name: string[64], _currency_symbol: string[32], _currency_decimals: uint256, _supply: uint256) -> bool:
    pass

@public
def set_template(_label: string[64], _address: address) -> bool:
    pass

@public
def set_offer_registration_fee_lookup(_pool_type: uint256, _fee_multiplier: uint256, _minimum_fee: uint256, _fee_multiplier_decimals: uint256, _minimum_interval: uint256(sec, positional), _last_registered_at: uint256(sec, positional), _last_paid_fee: uint256) -> bool:
    pass

@public
def set_shield_currency_price(_currency_address: address, _expiry: uint256(sec, positional), _underlying_address: address, _strike_price: uint256, _price: uint256) -> bool:
    pass

@public
def currency_to_l_currency(_currency_address: address, _value: uint256) -> bool:
    pass

@public
def register_pool(_pool_type: uint256, _currency_address: address, _name: string[62], _symbol: string[32], _initial_exchange_rate: uint256) -> bytes32:
    pass

@public
def deposit_l_currency(_pool_hash: bytes32, _from: address, _value: uint256) -> bool:
    pass

@public
def register_expiry_from_interest_pool(_pool_hash: bytes32, _expiry: uint256(sec, positional)) -> (bool, bytes32, bytes32, uint256, uint256):
    pass

@public
def l_currency_to_i_and_f_currency(_pool_hash: bytes32, _i_hash: bytes32, _f_hash: bytes32, _value: uint256) -> bool:
    pass

@public
def l_currency_from_i_and_f_currency(_pool_hash: bytes32, _i_hash: bytes32, _f_hash: bytes32, _value: uint256) -> bool:
    pass

@public
def register_expiry_from_underwriter_pool(_pool_hash: bytes32, _expiry: uint256(sec, positional), _underlying_address: address, _strike_price: uint256) -> (bool, bytes32, bytes32, bytes32, uint256, uint256, uint256):
    pass

@public
def l_currency_to_i_and_s_and_u_currency(_pool_hash: bytes32, _s_hash: bytes32, _u_hash: bytes32, _i_hash: bytes32, _value: uint256) -> bool:
    pass

@public
def l_currency_from_i_and_s_and_u_currency(_pool_hash: bytes32, _s_hash: bytes32, _u_hash: bytes32, _i_hash: bytes32, _value: uint256) -> bool:
    pass

@constant
@public
def protocol_currency_address() -> address:
    pass

@constant
@public
def owner() -> address:
    pass

@constant
@public
def expiries__expiry_timestamp(arg0: uint256(sec, positional)) -> uint256(sec, positional):
    pass

@constant
@public
def expiries__expiry_label(arg0: uint256(sec, positional)) -> string[3]:
    pass

@constant
@public
def expiries__is_active(arg0: uint256(sec, positional)) -> bool:
    pass

@constant
@public
def currencies__currency_address(arg0: address) -> address:
    pass

@constant
@public
def currencies__l_currency_address(arg0: address) -> address:
    pass

@constant
@public
def currencies__i_currency_address(arg0: address) -> address:
    pass

@constant
@public
def currencies__f_currency_address(arg0: address) -> address:
    pass

@constant
@public
def currencies__s_currency_address(arg0: address) -> address:
    pass

@constant
@public
def currencies__u_currency_address(arg0: address) -> address:
    pass

@constant
@public
def templates(arg0: string[64]) -> address:
    pass

@constant
@public
def pools__pool_type(arg0: bytes32) -> uint256:
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
def offer_registration_fee_lookups__minimum_fee(arg0: uint256) -> uint256:
    pass

@constant
@public
def offer_registration_fee_lookups__minimum_interval(arg0: uint256) -> uint256(sec, positional):
    pass

@constant
@public
def offer_registration_fee_lookups__fee_multiplier(arg0: uint256) -> uint256:
    pass

@constant
@public
def offer_registration_fee_lookups__fee_multiplier_decimals(arg0: uint256) -> uint256:
    pass

@constant
@public
def offer_registration_fee_lookups__last_registered_at(arg0: uint256) -> uint256(sec, positional):
    pass

@constant
@public
def offer_registration_fee_lookups__last_paid_fee(arg0: uint256) -> uint256:
    pass

@constant
@public
def shield_currency_prices(arg0: bytes32) -> uint256:
    pass

@constant
@public
def REGISTRATION_TYPE_POOL() -> uint256:
    pass

@constant
@public
def REGISTRATION_TYPE_OFFER() -> uint256:
    pass

@constant
@public
def POOL_TYPE_CURRENCY_POOL() -> uint256:
    pass

@constant
@public
def POOL_TYPE_INTEREST_POOL() -> uint256:
    pass

@constant
@public
def POOL_TYPE_UNDERWRITER_POOL() -> uint256:
    pass
