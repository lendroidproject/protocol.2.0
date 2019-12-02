# Functions

@public
def initialize(_pool_hash: bytes32, _accepts_public_contributions: bool, _operator: address, _i_currency_operator_fee_percentage: uint256, _s_currency_operator_fee_percentage: uint256, _name: string[64], _symbol: string[32], _initial_exchange_rate: uint256, _currency_address: address, _l_currency_address: address, _i_currency_address: address, _s_currency_address: address, _u_currency_address: address, _dao_address_protocol: address, _erc20_currency_template_address: address) -> bool:
    pass

@constant
@public
def expiry_hash(_expiry: uint256(sec, positional), _underlying_address: address, _strike_price: uint256) -> bytes32:
    pass

@constant
@public
def total_pool_currency_supply() -> uint256:
    pass

@constant
@public
def l_currency_balance() -> uint256:
    pass

@constant
@public
def i_currency_balance(_expiry: uint256(sec, positional), _underlying_address: address, _strike_price: uint256) -> uint256:
    pass

@constant
@public
def s_currency_balance(_expiry: uint256(sec, positional), _underlying_address: address, _strike_price: uint256) -> uint256:
    pass

@constant
@public
def u_currency_balance(_expiry: uint256(sec, positional), _underlying_address: address, _strike_price: uint256) -> uint256:
    pass

@constant
@public
def exchange_rate() -> uint256:
    pass

@constant
@public
def estimated_pool_tokens(_l_currency_value: uint256) -> uint256:
    pass

@constant
@public
def i_currency_fee(_expiry: uint256(sec, positional), _underlying_address: address, _strike_price: uint256) -> uint256:
    pass

@constant
@public
def s_currency_fee(_expiry: uint256(sec, positional), _underlying_address: address, _strike_price: uint256) -> uint256:
    pass

@public
def setShouldReject(_value: bool):
    pass

@constant
@public
def supportsInterface(interfaceID: bytes[10]) -> bool:
    pass

@public
def onERC1155Received(_operator: address, _from: address, _id: uint256, _value: uint256, _data: bytes32) -> bytes[10]:
    pass

@public
def onERC1155BatchReceived(_operator: address, _from: address, _ids: uint256[5], _values: uint256[5], _data: bytes32) -> bytes[10]:
    pass

@public
def set_public_contribution_acceptance(_acceptance: bool) -> bool:
    pass

@public
def register_expiry(_expiry: uint256(sec, positional), _underlying_address: address, _strike_price: uint256, _i_currency_cost_per_day: uint256, _s_currency_cost_per_day: uint256) -> bool:
    pass

@public
def remove_expiry(_expiry: uint256(sec, positional), _underlying_address: address, _strike_price: uint256) -> bool:
    pass

@public
def set_i_currency_cost_per_day(_expiry: uint256(sec, positional), _underlying_address: address, _strike_price: uint256, _value: uint256) -> bool:
    pass

@public
def set_s_currency_cost_per_day(_expiry: uint256(sec, positional), _underlying_address: address, _strike_price: uint256, _value: uint256) -> bool:
    pass

@public
def set_i_currency_operator_fee_percentage(_expiry: uint256(sec, positional), _underlying_address: address, _strike_price: uint256, _value: uint256) -> bool:
    pass

@public
def set_s_currency_operator_fee_percentage(_expiry: uint256(sec, positional), _underlying_address: address, _strike_price: uint256, _value: uint256) -> bool:
    pass

@public
def withdraw_earnings() -> bool:
    pass

@public
def increment_i_currency_supply(_expiry: uint256(sec, positional), _underlying_address: address, _strike_price: uint256, _l_currency_value: uint256) -> bool:
    pass

@public
def decrement_i_currency_supply(_expiry: uint256(sec, positional), _underlying_address: address, _strike_price: uint256, _l_currency_value: uint256) -> bool:
    pass

@public
def purchase_pool_currency(_l_currency_value: uint256) -> bool:
    pass

@public
def redeem_pool_currency(_expiry: uint256(sec, positional), _underlying_address: address, _strike_price: uint256, _pool_currency_value: uint256) -> bool:
    pass

@public
def purchase_i_currency(_expiry: uint256(sec, positional), _underlying_address: address, _strike_price: uint256, _i_currency_value: uint256, _fee_in_l_currency: uint256) -> bool:
    pass

@public
def purchase_s_currency(_expiry: uint256(sec, positional), _underlying_address: address, _strike_price: uint256, _s_currency_value: uint256, _fee_in_l_currency: uint256) -> bool:
    pass

@public
def exercise_u_currency(_expiry: uint256(sec, positional), _underlying_address: address, _strike_price: uint256, _u_currency_value: uint256) -> bool:
    pass

@constant
@public
def pool_hash() -> bytes32:
    pass

@constant
@public
def owner() -> address:
    pass

@constant
@public
def protocol_dao_address() -> address:
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
def currency_address() -> address:
    pass

@constant
@public
def l_currency_address() -> address:
    pass

@constant
@public
def i_currency_address() -> address:
    pass

@constant
@public
def s_currency_address() -> address:
    pass

@constant
@public
def u_currency_address() -> address:
    pass

@constant
@public
def pool_currency_address() -> address:
    pass

@constant
@public
def i_currency_operator_fee_percentage() -> uint256:
    pass

@constant
@public
def s_currency_operator_fee_percentage() -> uint256:
    pass

@constant
@public
def operator_earnings() -> uint256:
    pass

@constant
@public
def expiries__expiry_timestamp(arg0: bytes32) -> uint256(sec, positional):
    pass

@constant
@public
def expiries__i_currency_hash(arg0: bytes32) -> bytes32:
    pass

@constant
@public
def expiries__i_currency_id(arg0: bytes32) -> uint256:
    pass

@constant
@public
def expiries__s_currency_hash(arg0: bytes32) -> bytes32:
    pass

@constant
@public
def expiries__s_currency_id(arg0: bytes32) -> uint256:
    pass

@constant
@public
def expiries__u_currency_hash(arg0: bytes32) -> bytes32:
    pass

@constant
@public
def expiries__u_currency_id(arg0: bytes32) -> uint256:
    pass

@constant
@public
def expiries__i_currency_cost_per_day(arg0: bytes32) -> uint256:
    pass

@constant
@public
def expiries__s_currency_cost_per_day(arg0: bytes32) -> uint256:
    pass

@constant
@public
def expiries__is_active(arg0: bytes32) -> bool:
    pass

@constant
@public
def expiries__hash(arg0: bytes32) -> bytes32:
    pass

@constant
@public
def is_initialized() -> bool:
    pass

@constant
@public
def accepts_public_contributions() -> bool:
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
