# Functions

@public
def initialize(_owner: address, _protocol_currency_address: address, _dao_address_currency: address, _dao_address_interest_pool: address, _dao_address_underwriter_pool: address) -> bool:
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
def create_offer(_multi_fungible_currency_s_hash: bytes32, _multi_fungible_currency_i_hash: bytes32, _multi_fungible_currency_s_quantity: uint256, _multi_fungible_currency_i_quantity: uint256, _multi_fungible_currency_i_unit_price_in_wei: uint256(wei)) -> bool:
    pass

@public
def update_offer(_id: uint256, _multi_fungible_currency_s_quantity: uint256, _multi_fungible_currency_i_quantity: uint256) -> bool:
    pass

@public
def remove_offer(_id: uint256) -> bool:
    pass

@public
def loan_and_collateral_amount(_offer_id: uint256) -> (uint256, uint256):
    pass

@public
def avail_loan(_offer_id: uint256) -> bool:
    pass

@public
def repay_loan(_position_id: uint256) -> bool:
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
def last_position_id() -> uint256:
    pass

@constant
@public
def positions__borrower(arg0: uint256) -> address:
    pass

@constant
@public
def positions__multi_fungible_currency_hash(arg0: uint256) -> bytes32:
    pass

@constant
@public
def positions__status(arg0: uint256) -> uint256:
    pass

@constant
@public
def positions__id(arg0: uint256) -> uint256:
    pass

@constant
@public
def borrow_position_count(arg0: address) -> uint256:
    pass

@constant
@public
def borrow_position_index(arg0: address, arg1: uint256) -> uint256:
    pass

@constant
@public
def borrow_position(arg0: address, arg1: uint256) -> uint256:
    pass

@constant
@public
def last_offer_index() -> uint256:
    pass

@constant
@public
def offers__creator(arg0: uint256) -> address:
    pass

@constant
@public
def offers__multi_fungible_currency_s_hash(arg0: uint256) -> bytes32:
    pass

@constant
@public
def offers__multi_fungible_currency_i_hash(arg0: uint256) -> bytes32:
    pass

@constant
@public
def offers__multi_fungible_currency_s_quantity(arg0: uint256) -> uint256:
    pass

@constant
@public
def offers__multi_fungible_currency_i_quantity(arg0: uint256) -> uint256:
    pass

@constant
@public
def offers__multi_fungible_currency_i_unit_price_in_wei(arg0: uint256) -> uint256(wei):
    pass

@constant
@public
def offers__id(arg0: uint256) -> uint256:
    pass

@constant
@public
def DAO_TYPE_CURRENCY() -> uint256:
    pass

@constant
@public
def DAO_TYPE_INTEREST_POOL() -> uint256:
    pass

@constant
@public
def DAO_TYPE_UNDERWRITER_POOL() -> uint256:
    pass

@constant
@public
def LOAN_STATUS_ACTIVE() -> uint256:
    pass

@constant
@public
def LOAN_STATUS_LIQUIDATED() -> uint256:
    pass

@constant
@public
def LOAN_STATUS_CLOSED() -> uint256:
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
