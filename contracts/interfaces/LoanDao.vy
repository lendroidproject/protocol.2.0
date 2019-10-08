# Functions

@public
def initialize(_owner: address, _protocol_currency_address: address, _dao_address_currency: address, _dao_address_underwriter_pool: address) -> bool:
    pass

@public
def avail_loan(_s_hash: bytes32) -> bool:
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
def DAO_TYPE_CURRENCY() -> uint256:
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
