# Functions

@public
def initialize(_LST: address, _dao_currency: address, _dao_market: address) -> bool:
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
def pause() -> bool:
    pass

@public
def unpause() -> bool:
    pass

@public
def escape_hatch_erc20(_currency: address, _is_l: bool) -> bool:
    pass

@public
def escape_hatch_mft(_mft_type: int128, _currency: address, _expiry: uint256(sec, positional), _underlying: address, _strike_price: uint256) -> bool:
    pass

@public
def exercise_s(_currency: address, _expiry: uint256(sec, positional), _underlying: address, _strike_price: uint256, _quantity: uint256) -> bool:
    pass

@public
def exercise_u(_currency: address, _expiry: uint256(sec, positional), _underlying: address, _strike_price: uint256, _quantity: uint256) -> bool:
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
def registered_shield_markets(arg0: bytes32) -> bool:
    pass

@constant
@public
def initialized() -> bool:
    pass

@constant
@public
def paused() -> bool:
    pass
