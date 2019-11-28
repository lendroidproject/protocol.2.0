# Functions

@public
def initialize(_owner: address, _protocol_currency_address: address, _dao_address_market: address, _template_address_collateral_auction_erc20: address) -> bool:
    pass

@public
def set_template(_template_type: uint256, _address: address) -> bool:
    pass

@public
def create_graph(_currency_address: address, _expiry: uint256(sec, positional), _underlying_address: address) -> address:
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
def templates(arg0: uint256) -> address:
    pass

@constant
@public
def graphs(arg0: bytes32) -> address:
    pass

@constant
@public
def DAO_TYPE_MARKET() -> uint256:
    pass

@constant
@public
def TEMPLATE_TYPE_COLLATERAL_AUCTION_ERC20() -> uint256:
    pass

@constant
@public
def initialized() -> bool:
    pass
