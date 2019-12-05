# Vyper version of the Lendroid protocol v2
# THIS CONTRACT HAS NOT BEEN AUDITED!


from contracts.interfaces import ERC20
from contracts.interfaces import CurrencyDao


# Structs
struct Name:
    name: string[64]
    operator: address
    protocol_currency_staked: uint256
    active_pools: uint256
    id: uint256


struct NameRegistrationStakeLookup:
    name_length: int128
    stake_value: uint256


protocol_currency_address: public(address)
protocol_dao_address: public(address)
owner: public(address)
# dao_type => dao_address
daos: public(map(uint256, address))
# name_id => Name
names: public(map(uint256, Name))
# name => name_id
name_to_id: public(map(string[64], uint256))
# name counter
next_name_id: public(uint256)
# lookup_key => lookup_value
name_registration_stake_lookup: public(map(int128, NameRegistrationStakeLookup))
name_registration_stake_minimum_value: public(uint256)

initialized: public(bool)

DAO_TYPE_CURRENCY: public(uint256)
DAO_TYPE_INTEREST_POOL: public(uint256)
DAO_TYPE_UNDERWRITER_POOL: public(uint256)


@public
def initialize(
        _owner: address,
        _protocol_currency_address: address,
        _dao_address_currency: address,
        _dao_address_interest_pool: address,
        _dao_address_underwriter_pool: address,
        _minimum_name_registration_stake_value: uint256
    ) -> bool:
    assert not self.initialized
    self.initialized = True
    self.owner = _owner
    self.protocol_dao_address = msg.sender
    self.protocol_currency_address = _protocol_currency_address

    self.DAO_TYPE_CURRENCY = 1
    self.daos[self.DAO_TYPE_CURRENCY] = _dao_address_currency
    self.DAO_TYPE_INTEREST_POOL = 2
    self.daos[self.DAO_TYPE_INTEREST_POOL] = _dao_address_interest_pool
    self.DAO_TYPE_UNDERWRITER_POOL = 3
    self.daos[self.DAO_TYPE_UNDERWRITER_POOL] = _dao_address_underwriter_pool

    self.name_registration_stake_minimum_value = _minimum_name_registration_stake_value

    return True


@private
def _deposit_erc20(_currency_address: address, _from: address, _to: address, _value: uint256):
    assert_modifiable(CurrencyDao(self.daos[self.DAO_TYPE_CURRENCY]).deposit_erc20(
        _currency_address, _from, _to, _value))


@private
@constant
def _name_exists(_name: string[64]) -> bool:
    return self.names[self.name_to_id[_name]].name == _name


@private
def _add_name(_name: string[64], _operator: address, _active_pools: uint256):
    self.name_to_id[_name] = self.next_name_id
    _protocol_currency_stake_value: uint256 = self.name_registration_stake_lookup[len(_name)].stake_value
    if as_unitless_number(_protocol_currency_stake_value) == 0:
        _protocol_currency_stake_value = self.name_registration_stake_minimum_value
    self.names[self.next_name_id] = Name({
        name: _name,
        operator: _operator,
        protocol_currency_staked: _protocol_currency_stake_value,
        active_pools: _active_pools,
        id: self.next_name_id
    })
    self.next_name_id += 1

    self._deposit_erc20(self.protocol_currency_address, _operator, self,
        _protocol_currency_stake_value)


@private
def _remove_name(_name: string[64], _name_id: uint256):

    assert_modifiable(ERC20(self.protocol_currency_address).transfer(
        self.names[_name_id].operator,
        self.names[_name_id].protocol_currency_staked
    ))
    clear(self.name_to_id[_name])
    if as_unitless_number(_name_id) < as_unitless_number(self.next_name_id - 1):
        self.names[_name_id] = Name({
            name: self.names[self.next_name_id - 1].name,
            operator: self.names[self.next_name_id - 1].operator,
            protocol_currency_staked: self.names[self.next_name_id - 1].protocol_currency_staked,
            active_pools: self.names[self.next_name_id - 1].active_pools,
            id: _name_id
        })
        _last_name: string[64] = self.names[self.next_name_id - 1].name
        self.name_to_id[_last_name] = _name_id

    clear(self.names[self.next_name_id - 1])
    self.next_name_id -= 1


@public
@constant
def name_exists(_name: string[64]) -> bool:
    return self._name_exists(_name)


@public
def register_name(_name: string[64]) -> bool:
    assert self.initialized
    assert not self._name_exists(_name)
    self._add_name(_name, msg.sender, 0)

    return True


@public
def register_name_and_pool(_name: string[64], _operator: address) -> bool:
    assert self.initialized
    assert msg.sender == self.daos[self.DAO_TYPE_INTEREST_POOL] or \
           msg.sender == self.daos[self.DAO_TYPE_UNDERWRITER_POOL]
    assert not self._name_exists(_name)
    self._add_name(_name, _operator, 1)

    return True


@public
def increment_pool_count(_name: string[64]) -> bool:
    assert self.initialized
    assert msg.sender == self.daos[self.DAO_TYPE_INTEREST_POOL] or \
           msg.sender == self.daos[self.DAO_TYPE_UNDERWRITER_POOL]
    assert self._name_exists(_name)
    _name_id: uint256 = self.name_to_id[_name]
    assert as_unitless_number(self.names[_name_id].protocol_currency_staked) > 0
    assert self.names[_name_id].operator == msg.sender
    self.names[_name_id].active_pools += 1

    return True


@public
def decrement_pool_count(_name: string[64]) -> bool:
    assert self.initialized
    assert msg.sender == self.daos[self.DAO_TYPE_INTEREST_POOL] or \
           msg.sender == self.daos[self.DAO_TYPE_UNDERWRITER_POOL]
    assert self._name_exists(_name)
    _name_id: uint256 = self.name_to_id[_name]
    assert as_unitless_number(self.names[_name_id].protocol_currency_staked) > 0
    assert self.names[_name_id].operator == msg.sender
    self.names[_name_id].active_pools -= 1

    return True


@public
def deregister_name(_name: string[64]) -> bool:
    assert self.initialized
    assert self._name_exists(_name)
    _name_id: uint256 = self.name_to_id[_name]
    assert self.names[_name_id].active_pools == 0
    assert _name_id < self.next_name_id
    self._remove_name(_name, _name_id)

    return True
