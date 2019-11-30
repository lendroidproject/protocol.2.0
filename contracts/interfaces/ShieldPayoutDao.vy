# Functions

@public
def initialize(_owner: address, _protocol_currency_address: address, _dao_address_currency: address, _dao_address_underwriter_pool: address, _dao_address_market: address) -> bool:
    pass

@constant
@public
def shield_market_hash(_currency_address: address, _expiry: uint256(sec, positional), _underlying_address: address, _strike_price: uint256) -> bytes32:
    pass

@constant
@public
def shield_payout(_currency_address: address, _expiry: uint256(sec, positional), _underlying_address: address, _strike_price: uint256) -> uint256:
    pass

@constant
@public
def underwriter_payout(_currency_address: address, _expiry: uint256(sec, positional), _underlying_address: address, _strike_price: uint256) -> uint256:
    pass

@public
def register_shield_market(_currency_address: address, _expiry: uint256(sec, positional), _underlying_address: address, _strike_price: uint256) -> bool:
    pass

@public
def exercise_shield_currency(_currency_address: address, _expiry: uint256(sec, positional), _underlying_address: address, _strike_price: uint256, _currency_quantity: uint256) -> bool:
    pass

@public
def exercise_underwriter_currency(_currency_address: address, _expiry: uint256(sec, positional), _underlying_address: address, _strike_price: uint256, _currency_quantity: uint256, _recipient: address, _pool_address: address) -> bool:
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
