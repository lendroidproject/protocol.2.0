# Events

StakeMinimumValueUpdated: event({_setter: address, _value: uint256})
StakeLookupUpdated: event({_setter: address, _name_length: int128, _value: uint256})

# Functions

@public
def initialize(_LST: address, _dao_currency: address, _dao_interest_pool: address, _dao_underwriter_pool: address, _name_registration_minimum_stake: uint256) -> bool:
    pass

@constant
@public
def name_exists(_name: string[64]) -> bool:
    pass

@public
def set_name_registration_minimum_stake(_value: uint256) -> bool:
    pass

@public
def set_name_registration_stake_lookup(_name_length: int128, _stake: uint256) -> bool:
    pass

@public
def pause() -> bool:
    pass

@public
def unpause() -> bool:
    pass

@public
def escape_hatch_erc20(_currency: address) -> bool:
    pass

@public
def register_name(_name: string[64]) -> bool:
    pass

@public
def register_name_and_pool(_name: string[64], _operator: address) -> bool:
    pass

@public
def register_pool(_name: string[64], _operator: address) -> bool:
    pass

@public
def deregister_pool(_name: string[64], _operator: address) -> bool:
    pass

@public
def deregister_name(_name: string[64]) -> bool:
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
def names__name(arg0: uint256) -> string[64]:
    pass

@constant
@public
def names__operator(arg0: uint256) -> address:
    pass

@constant
@public
def names__LST_staked(arg0: uint256) -> uint256:
    pass

@constant
@public
def names__interest_pool_registered(arg0: uint256) -> bool:
    pass

@constant
@public
def names__underwriter_pool_registered(arg0: uint256) -> bool:
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
def name_registration_stake_lookup__stake(arg0: int128) -> uint256:
    pass

@constant
@public
def name_registration_minimum_stake() -> uint256:
    pass

@constant
@public
def initialized() -> bool:
    pass

@constant
@public
def paused() -> bool:
    pass
