# Events

PoolRegistered: event({_operator: address, _currency: address, address_: address})
PoolDeRegistered: event({_operator: address, _currency: address, address_: address})

# Functions

@public
def initialize(_owner: address, _LST: address, _registry_address_pool_name: address, _dao_currency: address, _dao_market: address, _dao_shield_payout: address, _template_underwriter_pool: address, _template_token_erc20: address) -> bool:
    pass

@constant
@public
def currency_dao() -> address:
    pass

@constant
@public
def LST_stake_value(_name: string[64]) -> uint256:
    pass

@public
def set_minimum_mft_fee(_value: uint256) -> bool:
    pass

@public
def set_fee_multiplier_per_mft_count(_mft_count: uint256, _value: uint256) -> bool:
    pass

@public
def set_template(_template_type: uint256, _address: address) -> bool:
    pass

@public
def register_pool(_accepts_public_contributions: bool, _currency: address, _name: string[64], _symbol: string[32], _initial_exchange_rate: uint256, _fee_percentage_per_i_token: uint256, _fee_percentage_per_s_token: uint256) -> bool:
    pass

@public
def deregister_pool(_name: string[64]) -> bool:
    pass

@public
def register_mft_support(_name: string[64], _expiry: uint256(sec, positional), _underlying: address, _strike_price: uint256, _i_address: address, _s_address: address, _u_address: address) -> (bool, uint256, uint256, uint256):
    pass

@public
def deregister_mft_support(_name: string[64], _currency: address, _expiry: uint256(sec, positional), _underlying: address, _strike_price: uint256) -> bool:
    pass

@public
def deposit_l(_name: string[64], _from: address, _value: uint256) -> bool:
    pass

@public
def split(_currency: address, _expiry: uint256(sec, positional), _underlying: address, _strike_price: uint256, _value: uint256) -> bool:
    pass

@public
def fuse(_currency: address, _expiry: uint256(sec, positional), _underlying: address, _strike_price: uint256, _value: uint256) -> bool:
    pass

@public
def exercise_u_token(_name: string[64], _currency: address, _expiry: uint256(sec, positional), _underlying: address, _strike_price: uint256, _value: uint256) -> bool:
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
def registries(arg0: uint256) -> address:
    pass

@constant
@public
def templates(arg0: uint256) -> address:
    pass

@constant
@public
def pools__currency(arg0: string[64]) -> address:
    pass

@constant
@public
def pools__name(arg0: string[64]) -> string[64]:
    pass

@constant
@public
def pools__address_(arg0: string[64]) -> address:
    pass

@constant
@public
def pools__operator(arg0: string[64]) -> address:
    pass

@constant
@public
def pools__mft_count(arg0: string[64]) -> uint256:
    pass

@constant
@public
def pools__LST_staked(arg0: string[64]) -> uint256:
    pass

@constant
@public
def pools__is_active(arg0: string[64]) -> bool:
    pass

@constant
@public
def pools__id(arg0: string[64]) -> uint256:
    pass

@constant
@public
def pool_id_to_name(arg0: uint256) -> string[64]:
    pass

@constant
@public
def next_pool_id() -> uint256:
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
def fee_multiplier_per_mft_count(arg0: uint256) -> uint256:
    pass

@constant
@public
def minimum_mft_fee() -> uint256:
    pass

@constant
@public
def LST_staked_per_mft(arg0: string[64], arg1: bytes32) -> uint256:
    pass

@constant
@public
def REGISTRY_TYPE_POOL_NAME() -> uint256:
    pass

@constant
@public
def DAO_TYPE_CURRENCY() -> uint256:
    pass

@constant
@public
def DAO_TYPE_MARKET() -> uint256:
    pass

@constant
@public
def DAO_TYPE_SHIELD_PAYOUT() -> uint256:
    pass

@constant
@public
def TEMPLATE_TYPE_UNDERWRITER_POOL() -> uint256:
    pass

@constant
@public
def TEMPLATE_TYPE_TOKEN_ERC20() -> uint256:
    pass

@constant
@public
def initialized() -> bool:
    pass
