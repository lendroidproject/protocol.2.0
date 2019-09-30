# Functions

@public
def initialize(_operator: address, _name: string[64], _symbol: string[32], _initial_exchange_rate: uint256, _lend_currency_address: address, _collateral_currency_address: address, _l_currency_address: address, _i_currency_address: address, _s_currency_address: address, _u_currency_address: address, _erc20_currency_template_address: address) -> bool:
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
def offer_new_expiry(_expiry_label: string[3]) -> bool:
    pass

@public
def remove_expiry(_expiry_label: string[3]) -> bool:
    pass

@public
def purchase_pool_tokens(_l_currency_value: uint256) -> bool:
    pass

@public
def increment_i_tokens_offered(_expiry_label: string[3], _l_currency_value: uint256) -> bool:
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
def total_l_currency_balance() -> uint256:
    pass

@constant
@public
def lend_currency_address() -> address:
    pass

@constant
@public
def collateral_currency_address() -> address:
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
def expiries_offered(arg0: string[3]) -> bool:
    pass

@constant
@public
def sufi_currency_offered_expiries__has_id(arg0: address, arg1: string[3]) -> bool:
    pass

@constant
@public
def sufi_currency_offered_expiries__erc1155_id(arg0: address, arg1: string[3]) -> uint256:
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
