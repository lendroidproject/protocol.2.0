# Functions

@public
def initialize(_owner: address, _protocol_currency_address: address, _template_address_currency_pool: address, _template_address_currency_erc20: address, _template_address_currency_erc1155: address) -> bool:
    pass

@constant
@public
def is_currency_valid(_currency_address: address) -> bool:
    pass

@constant
@public
def multi_fungible_addresses(_currency_address: address) -> (address, address, address, address, address):
    pass

@public
def deposit_multi_fungible_l_currency(_currency_address: address, _from: address, _to: address, _value: uint256) -> bool:
    pass

@public
def deposit_erc20(_currency_address: address, _from: address, _to: address, _value: uint256) -> bool:
    pass

@public
def deposit_currency_to_pool(_currency_address: address, _from: address, _value: uint256) -> bool:
    pass

@public
def release_currency_from_pool(_currency_address: address, _to: address, _value: uint256) -> bool:
    pass

@public
def create_erc1155_type(_currency_address: address, _expiry_label: string[3]) -> uint256:
    pass

@public
def mint_and_self_authorize_erc20(_currency_address: address, _to: address, _value: uint256) -> bool:
    pass

@public
def burn_as_self_authorized_erc20(_currency_address: address, _to: address, _value: uint256) -> bool:
    pass

@public
def mint_erc1155(_currency_address: address, _id: uint256, _to: address, _value: uint256) -> bool:
    pass

@public
def burn_erc1155(_currency_address: address, _id: uint256, _to: address, _value: uint256) -> bool:
    pass

@constant
@public
def pool_hash(_currency_address: address) -> bytes32:
    pass

@public
def set_template(_template_type: uint256, _address: address) -> bool:
    pass

@public
def set_currency_support(_currency_address: address, _is_active: bool) -> bool:
    pass

@public
def currency_to_l_currency(_currency_address: address, _value: uint256) -> bool:
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
def currencies__currency_address(arg0: address) -> address:
    pass

@constant
@public
def currencies__l_currency_address(arg0: address) -> address:
    pass

@constant
@public
def currencies__i_currency_address(arg0: address) -> address:
    pass

@constant
@public
def currencies__f_currency_address(arg0: address) -> address:
    pass

@constant
@public
def currencies__s_currency_address(arg0: address) -> address:
    pass

@constant
@public
def currencies__u_currency_address(arg0: address) -> address:
    pass

@constant
@public
def pools__currency_address(arg0: bytes32) -> address:
    pass

@constant
@public
def pools__pool_name(arg0: bytes32) -> string[64]:
    pass

@constant
@public
def pools__pool_address(arg0: bytes32) -> address:
    pass

@constant
@public
def pools__pool_operator(arg0: bytes32) -> address:
    pass

@constant
@public
def pools__hash(arg0: bytes32) -> bytes32:
    pass

@constant
@public
def templates(arg0: uint256) -> address:
    pass

@constant
@public
def TEMPLATE_TYPE_CURRENCY_POOL() -> uint256:
    pass

@constant
@public
def TEMPLATE_TYPE_CURRENCY_ERC20() -> uint256:
    pass

@constant
@public
def TEMPLATE_TYPE_CURRENCY_ERC1155() -> uint256:
    pass

@constant
@public
def initialized() -> bool:
    pass