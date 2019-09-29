# Events

ProtocolParameterAddressUpdateNotification: event({_notification_key: string[64], _address: address, _notification_value: uint256})
ProtocolParameterExpiryUpdateNotification: event({_notification_key: string[64], _timestamp: uint256(sec, positional), _notification_value: uint256})

# Functions

@public
def set_template(_label: string[64], _address: address) -> bool:
    pass

@public
def set_currency_support(_currency_address: address, _is_active: bool, _currency_name: string[64], _currency_symbol: string[32], _currency_decimals: uint256, _supply: uint256) -> bool:
    pass

@public
def set_expiry_support(_expiry_timestamp: uint256(sec, positional), _expiry_label: string[3], _is_active: bool) -> bool:
    pass

@constant
@public
def sufi_currency_id_by_expiry(_sufi_currency_address: address, _expiry_label: string[3]) -> uint256:
    pass

@public
def l_currency_from_original_currency(_currency_address: address, _value: uint256) -> bool:
    pass

@public
def register_interest_pool(_currency_address: address, _name: string[62], _symbol: string[32], _initial_exchange_rate: uint256) -> bool:
    pass

@public
def register_expiry_offer_from_interest_pool(_currency_address: address, _label: string[3]) -> (bool, uint256, uint256):
    pass

@public
def remove_expiry_offer_from_interest_pool(_currency_address: address, _label: string[3]) -> bool:
    pass

@public
def l_token_balance(_currency_address: address) -> uint256:
    pass

@public
def deposit_l_tokens_to_interest_pool(_currency_address: address, _from: address, _value: uint256) -> bool:
    pass

@public
def l_currency_to_i_and_f_currency(_currency_address: address, _expiry_label: string[3], _value: uint256) -> bool:
    pass

@public
def l_currency_from_i_and_f_currency(_currency_address: address, _expiry_label: string[3], _value: uint256) -> bool:
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
def supported_expiry(arg0: uint256(sec, positional)) -> bool:
    pass

@constant
@public
def expiry_to_label(arg0: uint256(sec, positional)) -> string[3]:
    pass

@constant
@public
def label_to_expiry(arg0: string[3]) -> uint256(sec, positional):
    pass

@constant
@public
def supported_currencies(arg0: address) -> bool:
    pass

@constant
@public
def currency_pools(arg0: address) -> address:
    pass

@constant
@public
def templates(arg0: string[64]) -> address:
    pass

@constant
@public
def loan_markets__lend_currency_address(arg0: bytes32) -> address:
    pass

@constant
@public
def loan_markets__expiry(arg0: bytes32) -> uint256(sec, positional):
    pass

@constant
@public
def loan_markets__market_address(arg0: bytes32) -> address:
    pass

@constant
@public
def currencies__pool_address(arg0: address) -> address:
    pass

@constant
@public
def currencies__l_token_address(arg0: address) -> address:
    pass

@constant
@public
def currencies__i_token_address(arg0: address) -> address:
    pass

@constant
@public
def currencies__f_token_address(arg0: address) -> address:
    pass

@constant
@public
def currencies__s_token_address(arg0: address) -> address:
    pass

@constant
@public
def currencies__u_token_address(arg0: address) -> address:
    pass

@constant
@public
def currencies__is_supported(arg0: address) -> bool:
    pass

@constant
@public
def interest_pools__name(arg0: address) -> string[64]:
    pass

@constant
@public
def interest_pools__is_active(arg0: address) -> bool:
    pass

@constant
@public
def interest_pools__expiries_offered__is_active(arg0: address, arg1: string[3]) -> bool:
    pass

@constant
@public
def interest_pools__expiries_offered__has_id(arg0: address, arg1: string[3]) -> bool:
    pass

@constant
@public
def interest_pools__expiries_offered__erc1155_id(arg0: address, arg1: string[3]) -> uint256:
    pass

@constant
@public
def sufi_token_offered_expiries__has_id(arg0: address, arg1: string[3]) -> bool:
    pass

@constant
@public
def sufi_token_offered_expiries__erc1155_id(arg0: address, arg1: string[3]) -> uint256:
    pass
