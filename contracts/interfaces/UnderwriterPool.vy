# Functions

@public
def initialize(_pool_type: uint256, _pool_hash: bytes32, _operator: address, _name: string[64], _symbol: string[32], _initial_exchange_rate: uint256, _currency_address: address, _l_currency_address: address, _i_currency_address: address, _s_currency_address: address, _u_currency_address: address, _erc20_currency_template_address: address) -> bool:
    pass

@constant
@public
def exchange_rate() -> uint256:
    pass

@constant
@public
def estimated_pool_tokens(_l_currency_value: uint256) -> uint256:
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
def register_expiry(_expiry: uint256(sec, positional), _underlying_address: address, _strike_price: uint256) -> bool:
    pass

@public
def remove_expiry(_expiry: uint256(sec, positional), _underlying_address: address, _strike_price: uint256) -> bool:
    pass

@public
def purchase_pool_currency(_l_currency_value: uint256) -> bool:
    pass

@public
def increment_i_currency_supply(_expiry: uint256(sec, positional), _underlying_address: address, _strike_price: uint256, _l_currency_value: uint256) -> bool:
    pass

@public
def decrement_i_currency_supply(_expiry: uint256(sec, positional), _underlying_address: address, _strike_price: uint256, _l_currency_value: uint256) -> bool:
    pass

@public
def purchase_i_currency(_expiry: uint256(sec, positional), _underlying_address: address, _strike_price: uint256, _i_currency_value: uint256, _l_currency_fee: uint256) -> bool:
    pass

@public
def purchase_s_currency(_expiry: uint256(sec, positional), _underlying_address: address, _strike_price: uint256, _s_currency_value: uint256, _l_currency_fee: uint256) -> bool:
    pass

@constant
@public
def pool_type() -> uint256:
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
def expiries__is_active(arg0: bytes32) -> bool:
    pass

@constant
@public
def expiries__hash(arg0: bytes32) -> bytes32:
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
