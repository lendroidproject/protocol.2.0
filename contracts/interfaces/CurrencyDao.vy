# Functions

@public
def initialize(_owner: address, _LST: address, _template_token_pool: address, _template_erc20: address, _template_mft: address, _dao_market: address) -> bool:
    pass

@constant
@public
def mft_hash(_address: address, _currency: address, _expiry: uint256(sec, positional), _underlying: address, _strike_price: uint256) -> bytes32:
    pass

@constant
@public
def is_token_supported(_token: address) -> bool:
    pass

@constant
@public
def mft_addresses(_token: address) -> (address, address, address, address, address):
    pass

@public
def deposit_l(_token: address, _from: address, _to: address, _value: uint256) -> bool:
    pass

@public
def deposit_erc20(_token: address, _from: address, _to: address, _value: uint256) -> bool:
    pass

@constant
@public
def f_token(_currency: address, _expiry: uint256(sec, positional)) -> (address, uint256):
    pass

@constant
@public
def i_token(_currency: address, _expiry: uint256(sec, positional)) -> (address, uint256):
    pass

@constant
@public
def s_token(_currency: address, _expiry: uint256(sec, positional), _underlying: address, _strike_price: uint256) -> (address, uint256):
    pass

@constant
@public
def u_token(_currency: address, _expiry: uint256(sec, positional), _underlying: address, _strike_price: uint256) -> (address, uint256):
    pass

@public
def mint_and_self_authorize_erc20(_token: address, _to: address, _value: uint256) -> bool:
    pass

@public
def burn_as_self_authorized_erc20(_token: address, _to: address, _value: uint256) -> bool:
    pass

@public
def mint_mft(_token: address, _id: uint256, _to: address, _value: uint256) -> bool:
    pass

@public
def burn_mft(_token: address, _id: uint256, _from: address, _value: uint256) -> bool:
    pass

@public
def transfer_mft(_from: address, _to: address, _token: address, _id: uint256, _value: uint256) -> bool:
    pass

@constant
@public
def pool_hash(_token: address) -> bytes32:
    pass

@public
def set_template(_template_type: uint256, _address: address) -> bool:
    pass

@public
def set_token_support(_token: address, _is_active: bool) -> bool:
    pass

@public
def wrap(_token: address, _value: uint256) -> bool:
    pass

@public
def unwrap(_token: address, _value: uint256) -> bool:
    pass

@public
def authorized_unwrap(_token: address, _to: address, _value: uint256) -> bool:
    pass

@public
def authorized_deposit_token(_token: address, _from: address, _value: uint256) -> bool:
    pass

@public
def authorized_withdraw_token(_token: address, _to: address, _value: uint256) -> bool:
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
def token_addresses__eth(arg0: address) -> address:
    pass

@constant
@public
def token_addresses__l(arg0: address) -> address:
    pass

@constant
@public
def token_addresses__i(arg0: address) -> address:
    pass

@constant
@public
def token_addresses__f(arg0: address) -> address:
    pass

@constant
@public
def token_addresses__s(arg0: address) -> address:
    pass

@constant
@public
def token_addresses__u(arg0: address) -> address:
    pass

@constant
@public
def pools__currency(arg0: bytes32) -> address:
    pass

@constant
@public
def pools__name(arg0: bytes32) -> string[64]:
    pass

@constant
@public
def pools__address_(arg0: bytes32) -> address:
    pass

@constant
@public
def pools__operator(arg0: bytes32) -> address:
    pass

@constant
@public
def pools__hash(arg0: bytes32) -> bytes32:
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
def mfts__address_(arg0: bytes32) -> address:
    pass

@constant
@public
def mfts__currency(arg0: bytes32) -> address:
    pass

@constant
@public
def mfts__expiry(arg0: bytes32) -> uint256(sec, positional):
    pass

@constant
@public
def mfts__underlying(arg0: bytes32) -> address:
    pass

@constant
@public
def mfts__strike_price(arg0: bytes32) -> uint256:
    pass

@constant
@public
def mfts__has_id(arg0: bytes32) -> bool:
    pass

@constant
@public
def mfts__id(arg0: bytes32) -> uint256:
    pass

@constant
@public
def mfts__hash(arg0: bytes32) -> bytes32:
    pass

@constant
@public
def MFT_DIMENSION_I() -> uint256:
    pass

@constant
@public
def MFT_DIMENSION_F() -> uint256:
    pass

@constant
@public
def MFT_DIMENSION_S() -> uint256:
    pass

@constant
@public
def MFT_DIMENSION_U() -> uint256:
    pass

@constant
@public
def DAO_TYPE_MARKET() -> uint256:
    pass

@constant
@public
def TEMPLATE_TYPE_TOKEN_POOL() -> uint256:
    pass

@constant
@public
def TEMPLATE_TYPE_TOKEN_ERC20() -> uint256:
    pass

@constant
@public
def TEMPLATE_TYPE_TOKEN_MULTI_FUNGIBLE() -> uint256:
    pass

@constant
@public
def initialized() -> bool:
    pass
