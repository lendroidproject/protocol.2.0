# @version 0.1.0b14
# @notice Implementation of Lendroid v2 - Pool Name Registry
# @dev THIS CONTRACT HAS NOT BEEN AUDITED
# @author Vignesh (Vii) Meenakshi Sundaram (@vignesh-msundaram)
# Lendroid Foundation


from ...interfaces import ERC20Interface
from ...interfaces import CurrencyDaoInterface

from ...interfaces import ProtocolDaoInterface


# Structs
struct Name:
    name: string[64]
    operator: address
    LST_staked: uint256
    interest_pool_registered: bool
    underwriter_pool_registered: bool
    id: uint256


struct NameRegistrationStakeLookup:
    name_length: int128
    stake: uint256


# Events
StakeMinimumValueUpdated: event({_setter: indexed(address), _value: indexed(uint256)})
StakeLookupUpdated: event({_setter: indexed(address), _name_length: indexed(int128), _value: indexed(uint256)})


# Variables
LST: public(address)
protocol_dao: public(address)
# dao_type => dao_address
daos: public(map(uint256, address))
# name_id => Name
names: public(map(uint256, Name))
# name => name_id
name_to_id: public(map(string[64], uint256))
# name counter
next_name_id: public(uint256)
# name_length => NameRegistrationStakeLookup
name_registration_stake_lookup: public(map(int128, NameRegistrationStakeLookup))
name_registration_minimum_stake: public(uint256)
# nonreentrant locks for pool_names, inspired from https://github.com/ethereum/vyper/issues/1204
nonreentrant_pool_name_locks: map(string[64], bool)

DAO_CURRENCY: constant(int128) = 1
DAO_INTEREST_POOL: constant(int128) = 2
DAO_UNDERWRITER_POOL: constant(int128) = 3

CALLER_ESCAPE_HATCH_TOKEN_HOLDER: constant(int128) = 3

initialized: public(bool)
paused: public(bool)


@public
def initialize(
        _LST: address,
        _dao_currency: address,
        _dao_interest_pool: address,
        _dao_underwriter_pool: address,
        _name_registration_minimum_stake: uint256
    ) -> bool:
    assert not self.initialized
    self.initialized = True
    self.protocol_dao = msg.sender
    self.LST = _LST

    self.daos[DAO_CURRENCY] = _dao_currency
    self.daos[DAO_INTEREST_POOL] = _dao_interest_pool
    self.daos[DAO_UNDERWRITER_POOL] = _dao_underwriter_pool

    self.name_registration_minimum_stake = _name_registration_minimum_stake

    return True


### Internal functions ###


@private
@constant
def _name_exists(_name: string[64]) -> bool:
    return self.names[self.name_to_id[_name]].name == _name


@private
def _lock_name(_name: string[64]):
    assert self.nonreentrant_pool_name_locks[_name] == False
    self.nonreentrant_pool_name_locks[_name] = True


@private
def _unlock_name(_name: string[64]):
    assert self.nonreentrant_pool_name_locks[_name] == True
    self.nonreentrant_pool_name_locks[_name] = False


@private
def _add_name(_name: string[64], _operator: address, _sender: address):
    self.name_to_id[_name] = self.next_name_id
    _LST_stake: uint256 = self.name_registration_stake_lookup[len(_name)].stake
    if as_unitless_number(_LST_stake) == 0:
        _LST_stake = self.name_registration_minimum_stake
    assert not as_unitless_number(_LST_stake) == 0
    self.names[self.next_name_id] = Name({
        name: _name,
        operator: _operator,
        LST_staked: _LST_stake,
        interest_pool_registered: False,
        underwriter_pool_registered: False,
        id: self.next_name_id
    })
    if _sender == self.daos[DAO_INTEREST_POOL]:
        self.names[self.next_name_id].interest_pool_registered = True
    if _sender == self.daos[DAO_UNDERWRITER_POOL]:
        self.names[self.next_name_id].underwriter_pool_registered = True
    self.next_name_id += 1
    assert_modifiable(CurrencyDaoInterface(self.daos[DAO_CURRENCY]).authorized_transfer_erc20(
        self.LST, _operator, self, _LST_stake))


@private
def _remove_name(_name: string[64], _name_id: uint256):

    # transfer staked LST back to operator
    assert_modifiable(ERC20Interface(self.LST).transfer(
        self.names[_name_id].operator,
        self.names[_name_id].LST_staked
    ))

    clear(self.name_to_id[_name])
    if as_unitless_number(_name_id) < as_unitless_number(self.next_name_id - 1):
        self.names[_name_id] = Name({
            name: self.names[self.next_name_id - 1].name,
            operator: self.names[self.next_name_id - 1].operator,
            LST_staked: self.names[self.next_name_id - 1].LST_staked,
            interest_pool_registered: self.names[self.next_name_id - 1].interest_pool_registered,
            underwriter_pool_registered: self.names[self.next_name_id - 1].underwriter_pool_registered,
            id: _name_id
        })
        _last_name: string[64] = self.names[self.next_name_id - 1].name
        self.name_to_id[_last_name] = _name_id

    clear(self.names[self.next_name_id - 1])
    self.next_name_id -= 1


@private
def _pause():
    """
        @dev Internal function to pause this contract.
    """
    assert not self.paused
    self.paused = True


@private
def _unpause():
    """
        @dev Internal function to unpause this contract.
    """
    assert self.paused
    self.paused = False


@private
def _transfer_balance_erc20(_token: address):
    """
        @dev Internal function to transfer this contract's balance of the given
             ERC20 token to the Escape Hatch Token Holder.
        @param _token The address of the ERC20 token.
    """
    assert_modifiable(ERC20Interface(_token).transfer(
        ProtocolDaoInterface(self.protocol_dao).authorized_callers(CALLER_ESCAPE_HATCH_TOKEN_HOLDER),
        ERC20Interface(_token).balanceOf(self)
    ))


### External functions ###


@public
@constant
def name_exists(_name: string[64]) -> bool:
    return self._name_exists(_name)


# Admin functions

@public
def set_name_registration_minimum_stake(_value: uint256) -> bool:
    """
        @dev Function to set the minimum stake required to register a pool name.
             Only the Protocol DAO can call this function.
        @param _value The minimum stake value.
        @return A bool with a value of "True" indicating the minimum stake
            has been set.
    """
    assert self.initialized
    assert msg.sender == self.protocol_dao
    self.name_registration_minimum_stake = _value

    log.StakeMinimumValueUpdated(msg.sender, _value)

    return True


@public
def set_name_registration_stake_lookup(_name_length: int128, _stake: uint256) -> bool:
    """
        @dev Function to set the stake required for a pool name with a specified
             character length. For eg, 3-character Pool names need a higher
             stake than 4-character, which in turn need a higher stake than a
             5-character name, and so on. Only the Protocol DAO can call this
             function.
        @param _name_length The character length of a pool name.
        @param _value The stake required for the given pool name character length.
        @return A bool with a value of "True" indicating the minimum stake
            has been set.
    """
    assert self.initialized
    assert msg.sender == self.protocol_dao
    self.name_registration_stake_lookup[_name_length] = NameRegistrationStakeLookup({
        name_length: _name_length,
        stake: _stake
    })

    log.StakeLookupUpdated(msg.sender, _name_length, _stake)

    return True


# Escape-hatches

@public
def pause() -> bool:
    """
        @dev Escape hatch function to pause this contract. Only the Protocol DAO
             can call this function.
        @return A bool with a value of "True" indicating this contract has been
             paused.
    """
    assert self.initialized
    assert msg.sender == self.protocol_dao
    self._pause()
    return True


@public
def unpause() -> bool:
    """
        @dev Escape hatch function to unpause this contract. Only the Protocol
             DAO can call this function.
        @return A bool with a value of "True" indicating this contract has been
             unpaused.
    """
    assert self.initialized
    assert msg.sender == self.protocol_dao
    self._unpause()
    return True


@public
def escape_hatch_erc20(_currency: address) -> bool:
    """
        @dev Escape hatch function to transfer all tokens of an ERC20 address
             from this contract to the Escape Hatch Token Holder. Only the
             Protocol DAO can call this function.
        @param _currency The address of the ERC20 token
        @return A bool with a value of "True" indicating the ERC20 transfer has
             been made to the Escape Hatch Token Holder.
    """
    assert self.initialized
    assert msg.sender == self.protocol_dao
    self._transfer_balance_erc20(_currency)
    return True


# Non-admin functions

@public
def register_name(_name: string[64]) -> bool:
    assert self.initialized
    assert not self.paused
    if self._name_exists(_name):
        raise "Pool name already exists"
    self._lock_name(_name)
    self._add_name(_name, msg.sender, self)
    self._unlock_name(_name)

    return True


@public
def register_name_and_pool(_name: string[64], _operator: address) -> bool:
    assert self.initialized
    assert not self.paused
    assert msg.sender == self.daos[DAO_INTEREST_POOL] or \
           msg.sender == self.daos[DAO_UNDERWRITER_POOL]
    assert not self._name_exists(_name)
    self._lock_name(_name)
    self._add_name(_name, _operator, msg.sender)
    self._unlock_name(_name)

    return True


@public
def register_pool(_name: string[64], _operator: address) -> bool:
    assert self.initialized
    assert not self.paused
    assert msg.sender == self.daos[DAO_INTEREST_POOL] or \
           msg.sender == self.daos[DAO_UNDERWRITER_POOL]
    assert self._name_exists(_name)
    _name_id: uint256 = self.name_to_id[_name]
    assert _operator == self.names[_name_id].operator

    if msg.sender == self.daos[DAO_INTEREST_POOL]:
        assert not self.names[_name_id].interest_pool_registered
        self.names[_name_id].interest_pool_registered = True

    if msg.sender == self.daos[DAO_UNDERWRITER_POOL]:
        assert not self.names[_name_id].underwriter_pool_registered
        self.names[_name_id].underwriter_pool_registered = True

    return True


@public
def deregister_pool(_name: string[64], _operator: address) -> bool:
    assert self.initialized
    assert not self.paused
    assert msg.sender == self.daos[DAO_INTEREST_POOL] or \
           msg.sender == self.daos[DAO_UNDERWRITER_POOL]
    assert self._name_exists(_name)
    _name_id: uint256 = self.name_to_id[_name]
    assert as_unitless_number(self.names[_name_id].LST_staked) > 0
    assert _operator == self.names[_name_id].operator

    if msg.sender == self.daos[DAO_INTEREST_POOL]:
        assert self.names[_name_id].interest_pool_registered
        self.names[_name_id].interest_pool_registered = False

    if msg.sender == self.daos[DAO_UNDERWRITER_POOL]:
        assert self.names[_name_id].underwriter_pool_registered
        self.names[_name_id].underwriter_pool_registered = False

    return True


@public
def deregister_name(_name: string[64]) -> bool:
    assert self.initialized
    assert not self.paused
    assert self._name_exists(_name)
    _name_id: uint256 = self.name_to_id[_name]
    assert self.names[_name_id].operator == msg.sender
    assert _name_id < self.next_name_id
    self._lock_name(_name)
    self._remove_name(_name, _name_id)
    self._unlock_name(_name)

    return True
