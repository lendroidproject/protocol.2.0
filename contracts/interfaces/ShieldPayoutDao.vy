# Functions

@public
def initialize(_owner: address, _protocol_currency_address: address, _dao_address_currency: address, _dao_address_underwriter_pool: address, _template_address_shield_payout_erc20: address) -> bool:
    pass

@public
def initialize_payout_graph(_currency_address: address, _underlying_address: address, _expiry: uint256(sec, positional), _strike_price: uint256, _s_hash: bytes32, _u_hash: bytes32) -> bool:
    pass

@public
def l_currency_from_s_currency(_currency_address: address, _s_hash: bytes32, _s_token_id: uint256, _currency_quantity: uint256) -> bool:
    pass

@public
def l_currency_from_u_currency(_currency_address: address, _u_hash: bytes32, _u_token_id: uint256, _currency_quantity: uint256) -> bool:
    pass

@constant
@public
def shield_payout(_s_hash: bytes32) -> uint256:
    pass

@constant
@public
def underwriter_payout(_u_hash: bytes32) -> uint256:
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
def payout_graph_addresses(arg0: bytes32) -> address:
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
def daos(arg0: uint256) -> address:
    pass

@constant
@public
def TEMPLATE_TYPE_SHIELD_PAYOUT_ERC20() -> uint256:
    pass

@constant
@public
def templates(arg0: uint256) -> address:
    pass

@constant
@public
def initialized() -> bool:
    pass
