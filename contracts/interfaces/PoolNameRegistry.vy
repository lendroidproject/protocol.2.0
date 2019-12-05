# Functions

@public
def initialize(_owner: address, _protocol_currency_address: address, _dao_address_currency: address, _dao_address_interest_pool: address, _dao_address_underwriter_pool: address, _minimum_name_registration_stake_value: uint256) -> bool:
    pass

@constant
@public
def name_exists(_name: string[64]) -> bool:
    pass

@public
def register_name(_name: string[64]) -> bool:
    pass

@public
def register_name_and_pool(_name: string[64], _operator: address) -> bool:
    pass

@public
def increment_pool_count(_name: string[64]) -> bool:
    pass

@public
def decrement_pool_count(_name: string[64]) -> bool:
    pass

@public
def deregister_name(_name: string[64]) -> bool:
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
def names__name(arg0: uint256) -> string[64]:
    pass

@constant
@public
def names__operator(arg0: uint256) -> address:
    pass

@constant
@public
def names__protocol_currency_staked(arg0: uint256) -> uint256:
    pass

@constant
@public
def names__active_pools(arg0: uint256) -> uint256:
    pass

@constant
@public
def names__id(arg0: uint256) -> uint256:
    pass

@constant
@public
def name_to_id(arg0: string[64]) -> uint256:
    pass

@constant
@public
def next_name_id() -> uint256:
    pass

@constant
@public
def name_registration_stake_lookup__name_length(arg0: int128) -> int128:
    pass

@constant
@public
def name_registration_stake_lookup__stake_value(arg0: int128) -> uint256:
    pass

@constant
@public
def minimum_name_registration_stake_value() -> uint256:
    pass

@constant
@public
def initialized() -> bool:
    pass

@constant
@public
def DAO_TYPE_CURRENCY() -> uint256:
    pass

@constant
@public
def DAO_TYPE_INTEREST_POOL() -> uint256:
    pass

@constant
@public
def DAO_TYPE_UNDERWRITER_POOL() -> uint256:
    pass
