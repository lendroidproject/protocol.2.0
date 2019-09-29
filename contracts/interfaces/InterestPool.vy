# Functions

@public
def initialize(_operator: address, _name: string[64], _symbol: string[32], _initial_exchange_rate: uint256, _currency_address: address, _l_token_address: address, _i_token_address: address, _f_token_address: address, _erc20_token_template_address: address) -> bool:
    pass

@public
def offer_new_expiry(_expiry_label: string[3]) -> bool:
    pass

@public
def remove_expiry(_expiry_label: string[3]) -> bool:
    pass

@constant
@public
def exchange_rate() -> uint256:
    pass

@constant
@public
def estimated_pool_tokens(_l_token_value: uint256) -> uint256:
    pass

@public
def setShouldReject(_value: bool):
    pass

@public
def purchase_pool_tokens(_l_token_value: uint256) -> bool:
    pass

@public
def increment_i_tokens_offered(_expiry_label: string[3], _l_token_value: uint256) -> bool:
    pass

@public
def decrement_i_tokens_offered(_expiry_label: string[3], _l_token_value: uint256) -> bool:
    pass

@public
def purchase_i_tokens(_expiry_label: string[3], _i_token_value: uint256, _l_token_fee: uint256) -> bool:
    pass

@public
def redeem_f_tokens(_expiry_label: string[3], _pool_token_value: uint256) -> bool:
    pass

@constant
@public
def owner() -> address:
    pass

@constant
@public
def operator() -> address:
    pass

@constant
@public
def name() -> string[64]:
    pass

@constant
@public
def symbol() -> string[32]:
    pass

@constant
@public
def initial_exchange_rate() -> uint256:
    pass

@constant
@public
def total_l_token_balance() -> uint256:
    pass

@constant
@public
def currency_address() -> address:
    pass

@constant
@public
def l_token_address() -> address:
    pass

@constant
@public
def i_token_address() -> address:
    pass

@constant
@public
def f_token_address() -> address:
    pass

@constant
@public
def pool_token_address() -> address:
    pass

@constant
@public
def expiries_offered(arg0: string[3]) -> bool:
    pass

@constant
@public
def sufi_token_offered_expiries__has_id(arg0: address, arg1: string[3]) -> bool:
    pass

@constant
@public
def sufi_token_offered_expiries__erc1155_id(arg0: address, arg1: string[3]) -> uint256:
    pass

@constant
@public
def shouldReject() -> bool:
    pass

@constant
@public
def lastData() -> bytes32:
    pass

@constant
@public
def lastOperator() -> address:
    pass

@constant
@public
def lastFrom() -> address:
    pass

@constant
@public
def lastId() -> uint256:
    pass

@constant
@public
def lastValue() -> uint256:
    pass
