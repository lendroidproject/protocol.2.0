# Functions

@public
def initialize(_owner: address, _LST: address, _dao_currency: address, _dao_underwriter_pool: address, _dao_market: address) -> bool:
    pass

@constant
@public
def shield_market_hash(_currency: address, _expiry: uint256(sec, positional), _underlying: address, _strike_price: uint256) -> bytes32:
    pass

@constant
@public
def s_payoff(_currency: address, _expiry: uint256(sec, positional), _underlying: address, _strike_price: uint256) -> uint256:
    pass

@constant
@public
def u_payoff(_currency: address, _expiry: uint256(sec, positional), _underlying: address, _strike_price: uint256) -> uint256:
    pass

@public
def register_shield_market(_currency: address, _expiry: uint256(sec, positional), _underlying: address, _strike_price: uint256) -> bool:
    pass

@public
def exercise_s_token(_currency: address, _expiry: uint256(sec, positional), _underlying: address, _strike_price: uint256, _quantity: uint256) -> bool:
    pass

@public
def exercise_u_token(_currency: address, _expiry: uint256(sec, positional), _underlying: address, _strike_price: uint256, _quantity: uint256, _recipient: address, _pool_address: address) -> bool:
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
def owner() -> address:
    pass

@constant
@public
def daos(arg0: uint256) -> address:
    pass

@constant
@public
def registered_shield_markets(arg0: bytes32) -> bool:
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
def DAO_TYPE_MARKET() -> uint256:
    pass

@constant
@public
def initialized() -> bool:
    pass
