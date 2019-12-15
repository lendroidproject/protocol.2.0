# Functions

@public
def initialize(_LST: address, _dao_address_market: address) -> bool:
    pass

@public
def pause() -> bool:
    pass

@public
def unpause() -> bool:
    pass

@public
def avail_loan(_currency_address: address, _expiry: uint256(sec, positional), _underlying_address: address, _strike_price: uint256, _currency_value: uint256) -> bool:
    pass

@public
def repay_loan(_position_id: uint256, _pay_value: uint256) -> bool:
    pass

@public
def close_liquidated_loan(_position_id: uint256) -> bool:
    pass

@constant
@public
def LST() -> address:
    pass

@constant
@public
def protocol_dao() -> address:
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
def positions__currency(arg0: uint256) -> address:
    pass

@constant
@public
def positions__underlying(arg0: uint256) -> address:
    pass

@constant
@public
def positions__currency_value(arg0: uint256) -> uint256:
    pass

@constant
@public
def positions__underlying_value(arg0: uint256) -> uint256:
    pass

@constant
@public
def positions__repaid_value(arg0: uint256) -> uint256:
    pass

@constant
@public
def positions__status(arg0: uint256) -> uint256:
    pass

@constant
@public
def positions__expiry(arg0: uint256) -> uint256(sec, positional):
    pass

@constant
@public
def positions__strike_price(arg0: uint256) -> uint256:
    pass

@constant
@public
def positions__shield_market_hash(arg0: uint256) -> bytes32:
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
def initialized() -> bool:
    pass

@constant
@public
def paused() -> bool:
    pass
