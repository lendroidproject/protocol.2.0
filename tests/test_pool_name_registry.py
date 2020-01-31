import os

import pytest

import brownie

from web3 import Web3

from conftest import (
    PROTOCOL_CONSTANTS,
    POOL_NAME_REGISTRATION_MIN_STAKE_LST,
    POOL_NAME_REGISTRATION_LST_STAKE_PER_NAME_LENGTH,
    POOL_NAME_LIONFURY, POOL_NAME_ABCD, POOL_NAME_ABC, POOL_NAME_AB, POOL_NAME_A,
    ZERO_ADDRESS, EMPTY_BYTES32
)


def test_initialize(accounts, Deployer, get_PoolNameRegistry_contract, ProtocolDaoContract):
    anyone = accounts[-1]
    # get PoolNameRegistry
    PoolNameRegistry = get_PoolNameRegistry_contract(address=ProtocolDaoContract.registries(PROTOCOL_CONSTANTS['REGISTRY_POOL_NAME']))
    assert not PoolNameRegistry.initialized({'from': anyone})
    # initialize PoolNameRegistry
    ProtocolDaoContract.initialize_pool_name_registry(Web3.toWei(POOL_NAME_REGISTRATION_MIN_STAKE_LST, 'ether'), {'from': Deployer})
    assert PoolNameRegistry.initialized({'from': anyone})
    assert PoolNameRegistry.name_registration_minimum_stake({'from': anyone}) == Web3.toWei(POOL_NAME_REGISTRATION_MIN_STAKE_LST, 'ether')


def test_pause_and_unpause(accounts, Deployer, EscapeHatchManager, get_PoolNameRegistry_contract, ProtocolDaoContract):
    anyone = accounts[-1]
    # get PoolNameRegistry
    PoolNameRegistry = get_PoolNameRegistry_contract(address=ProtocolDaoContract.registries(PROTOCOL_CONSTANTS['REGISTRY_POOL_NAME']))
    # initialize PoolNameRegistry
    ProtocolDaoContract.initialize_pool_name_registry(Web3.toWei(POOL_NAME_REGISTRATION_MIN_STAKE_LST, 'ether'), {'from': Deployer})
    assert not PoolNameRegistry.paused({'from': anyone})
    ProtocolDaoContract.toggle_registry_pause(PROTOCOL_CONSTANTS['REGISTRY_POOL_NAME'], True, {'from': EscapeHatchManager})
    assert PoolNameRegistry.paused({'from': anyone})
    ProtocolDaoContract.toggle_registry_pause(PROTOCOL_CONSTANTS['REGISTRY_POOL_NAME'], False, {'from': EscapeHatchManager})
    assert not PoolNameRegistry.paused({'from': anyone})


def test_set_name_registration_stake_lookup(accounts,
    Deployer, Governor,
    get_PoolNameRegistry_contract, ProtocolDaoContract):
    anyone = accounts[-1]
    # get PoolNameRegistry
    PoolNameRegistry = get_PoolNameRegistry_contract(address=ProtocolDaoContract.registries(PROTOCOL_CONSTANTS['REGISTRY_POOL_NAME']))
    # initialize PoolNameRegistry
    ProtocolDaoContract.initialize_pool_name_registry(Web3.toWei(POOL_NAME_REGISTRATION_MIN_STAKE_LST, 'ether'), {'from': Deployer})
    # set stake lookup for name lengths
    for _name_length, _stake_amount in POOL_NAME_REGISTRATION_LST_STAKE_PER_NAME_LENGTH.items():
        _name_length = int(_name_length)
        assert PoolNameRegistry.name_registration_stake_lookup__stake(_name_length, {'from': anyone}) == 0
        ProtocolDaoContract.set_pool_name_registration_stake_lookup(_name_length, Web3.toWei(_stake_amount, 'ether'), {'from': Governor})
        assert PoolNameRegistry.name_registration_stake_lookup__stake(_name_length, {'from': anyone}) == Web3.toWei(_stake_amount, 'ether')


def test_register_names_with_variable_lengths(accounts,
    Whale, Deployer, Governor,
    LST_token,
    get_PoolNameRegistry_contract, get_CurrencyDao_contract,
    ProtocolDaoContract):
    anyone = accounts[-1]
    # get CurrencyDao
    CurrencyDao = get_CurrencyDao_contract(address=ProtocolDaoContract.daos(PROTOCOL_CONSTANTS['DAO_CURRENCY']))
    # get PoolNameRegistry
    PoolNameRegistry = get_PoolNameRegistry_contract(address=ProtocolDaoContract.registries(PROTOCOL_CONSTANTS['REGISTRY_POOL_NAME']))
    # assign one of the accounts as _pool_owner
    _pool_owner = accounts[5]
    # initialize CurrencyDao
    ProtocolDaoContract.initialize_currency_dao({'from': Deployer})
    # initialize PoolNameRegistry
    ProtocolDaoContract.initialize_pool_name_registry(Web3.toWei(POOL_NAME_REGISTRATION_MIN_STAKE_LST, 'ether'), {'from': Deployer})
    # _pool_owner buys 16750000 LST_token from a 3rd party exchange
    LST_token.transfer(_pool_owner, Web3.toWei(16750000, 'ether'), {'from': Whale})
    assert LST_token.balanceOf(_pool_owner) == Web3.toWei(16750000, 'ether')
    # _pool_owner authorizes CurrencyDao to spend 16750000 LST_token
    LST_token.approve(CurrencyDao.address, Web3.toWei(16750000, 'ether'), {'from': _pool_owner})
    assert LST_token.allowance(_pool_owner, CurrencyDao.address) == Web3.toWei(16750000, 'ether')
    # set stake lookup for and register name for names of lengths 1 to 4
    _pool_name = None
    _next_name_id = PoolNameRegistry.next_name_id({'from': anyone})
    # verify _next_name_id
    assert _next_name_id == 0
    for _name_length, _stake_amount in POOL_NAME_REGISTRATION_LST_STAKE_PER_NAME_LENGTH.items():
        _name_length = int(_name_length)
        ProtocolDaoContract.set_pool_name_registration_stake_lookup(_name_length, Web3.toWei(_stake_amount, 'ether'), {'from': Governor})
        if _name_length == 4:
            _pool_name = POOL_NAME_ABCD
        elif _name_length == 3:
            _pool_name = POOL_NAME_ABC
        elif _name_length == 2:
            _pool_name = POOL_NAME_AB
        elif _name_length == 1:
            _pool_name = POOL_NAME_A
        assert not _pool_name is None
        # _pool_owner registers the pool name
        PoolNameRegistry.register_name(_pool_name, {'from': _pool_owner, 'gas': 250000})
        # verify registerd_name stats
        assert PoolNameRegistry.name_to_id(_pool_name, {'from': anyone}) == _next_name_id
        assert PoolNameRegistry.names__id(_next_name_id, {'from': anyone}) == _next_name_id
        assert PoolNameRegistry.names__name(_next_name_id, {'from': anyone}) == _pool_name
        assert PoolNameRegistry.names__operator(_next_name_id, {'from': anyone}) == _pool_owner
        assert PoolNameRegistry.names__LST_staked(_next_name_id, {'from': anyone}) == PoolNameRegistry.name_registration_stake_lookup__stake(_name_length, {'from': anyone})
        # verify _next_name_id
        _next_name_id += 1
        assert _next_name_id == PoolNameRegistry.next_name_id({'from': anyone})

    _pool_name = POOL_NAME_LIONFURY
    # _pool_owner registers the pool name
    PoolNameRegistry.register_name(_pool_name, {'from': _pool_owner, 'gas': 250000})
    # verify registerd_name stats
    assert PoolNameRegistry.name_to_id(_pool_name, {'from': anyone}) == _next_name_id
    assert PoolNameRegistry.names__id(_next_name_id, {'from': anyone}) == _next_name_id
    assert PoolNameRegistry.names__name(_next_name_id, {'from': anyone}) == _pool_name
    assert PoolNameRegistry.names__operator(_next_name_id, {'from': anyone}) == _pool_owner
    assert PoolNameRegistry.names__LST_staked(_next_name_id, {'from': anyone}) == PoolNameRegistry.name_registration_minimum_stake({'from': anyone})
    assert PoolNameRegistry.names__interest_pool_registered(_next_name_id, {'from': anyone}) == False
    assert PoolNameRegistry.names__underwriter_pool_registered(_next_name_id, {'from': anyone}) == False
    # verify next_name_id
    _next_name_id += 1
    assert _next_name_id == PoolNameRegistry.next_name_id({'from': anyone})
    # verify LST balance of _pool_owner
    assert LST_token.balanceOf(_pool_owner, {'from': anyone}) == 0
    # verify LST balance of PoolNameRegistry
    assert LST_token.balanceOf(PoolNameRegistry.address, {'from': anyone}) == Web3.toWei(16750000, 'ether')


def test_fail_when_registering_duplicate_names(accounts,
    Whale, Deployer, Governor,
    LST_token,
    get_PoolNameRegistry_contract, get_CurrencyDao_contract,
    ProtocolDaoContract):
    anyone = accounts[-1]
    # get CurrencyDao
    CurrencyDao = get_CurrencyDao_contract(address=ProtocolDaoContract.daos(PROTOCOL_CONSTANTS['DAO_CURRENCY']))
    # get PoolNameRegistry
    PoolNameRegistry = get_PoolNameRegistry_contract(address=ProtocolDaoContract.registries(PROTOCOL_CONSTANTS['REGISTRY_POOL_NAME']))
    # assign one of the accounts as _pool_owner
    _pool_owner = accounts[5]
    # assign one of the accounts as _pool_owner_2
    _pool_owner_2 = accounts[6]
    # initialize CurrencyDao
    ProtocolDaoContract.initialize_currency_dao({'from': Deployer})
    # initialize PoolNameRegistry
    ProtocolDaoContract.initialize_pool_name_registry(Web3.toWei(POOL_NAME_REGISTRATION_MIN_STAKE_LST, 'ether'), {'from': Deployer})
    # _pool_owner buys POOL_NAME_REGISTRATION_MIN_STAKE_LST LST_token from a 3rd party exchange
    LST_token.transfer(_pool_owner, Web3.toWei(POOL_NAME_REGISTRATION_MIN_STAKE_LST, 'ether'), {'from': Whale})
    assert LST_token.balanceOf(_pool_owner, {'from': anyone}) == Web3.toWei(POOL_NAME_REGISTRATION_MIN_STAKE_LST, 'ether')
    # _pool_owner authorizes CurrencyDao to spend POOL_NAME_REGISTRATION_MIN_STAKE_LST LST_token
    LST_token.approve(CurrencyDao.address, Web3.toWei(POOL_NAME_REGISTRATION_MIN_STAKE_LST, 'ether'), {'from': _pool_owner})
    assert LST_token.allowance(_pool_owner, CurrencyDao.address, {'from': anyone}) == Web3.toWei(POOL_NAME_REGISTRATION_MIN_STAKE_LST, 'ether')
    # _pool_owner registers the POOL_NAME_LIONFURY
    _pool_name = POOL_NAME_LIONFURY
    PoolNameRegistry.register_name(_pool_name, {'from': _pool_owner, 'gas': 250000})
    # _pool_owner_2 buys POOL_NAME_REGISTRATION_MIN_STAKE_LST LST_token from a 3rd party exchange
    LST_token.transfer(_pool_owner_2, Web3.toWei(POOL_NAME_REGISTRATION_MIN_STAKE_LST, 'ether'), {'from': Whale})
    assert LST_token.balanceOf(_pool_owner_2, {'from': anyone}) == Web3.toWei(POOL_NAME_REGISTRATION_MIN_STAKE_LST, 'ether')
    # _pool_owner_2 authorizes CurrencyDao to spend POOL_NAME_REGISTRATION_MIN_STAKE_LST LST_token
    LST_token.approve(CurrencyDao.address, Web3.toWei(POOL_NAME_REGISTRATION_MIN_STAKE_LST, 'ether'), {'from': _pool_owner_2})
    assert LST_token.allowance(_pool_owner_2, CurrencyDao.address, {'from': anyone}) == Web3.toWei(POOL_NAME_REGISTRATION_MIN_STAKE_LST, 'ether')
    # _pool_owner_2 registers the POOL_NAME_LIONFURY
    assert PoolNameRegistry.name_exists(_pool_name, {'from': anyone})
    with brownie.reverts("Pool name already exists"):
        PoolNameRegistry.register_name(_pool_name, {'from': _pool_owner_2, 'gas': 250000})


def test_deregister_names_with_variable_lengths(accounts,
    Whale, Deployer, Governor,
    LST_token,
    get_PoolNameRegistry_contract, get_CurrencyDao_contract,
    ProtocolDaoContract):
    anyone = accounts[-1]
    # get CurrencyDao
    CurrencyDao = get_CurrencyDao_contract(address=ProtocolDaoContract.daos(PROTOCOL_CONSTANTS['DAO_CURRENCY']))
    # get PoolNameRegistry
    PoolNameRegistry = get_PoolNameRegistry_contract(address=ProtocolDaoContract.registries(PROTOCOL_CONSTANTS['REGISTRY_POOL_NAME']))
    # assign one of the accounts as _pool_owner
    _pool_owner = accounts[5]
    # initialize CurrencyDao
    ProtocolDaoContract.initialize_currency_dao({'from': Deployer})
    # initialize PoolNameRegistry
    ProtocolDaoContract.initialize_pool_name_registry(Web3.toWei(POOL_NAME_REGISTRATION_MIN_STAKE_LST, 'ether'), {'from': Deployer})
    # _pool_owner buys 16750000 LST_token from a 3rd party exchange
    LST_token.transfer(_pool_owner, Web3.toWei(16750000, 'ether'), {'from': Whale})
    assert LST_token.balanceOf(_pool_owner) == Web3.toWei(16750000, 'ether')
    # _pool_owner authorizes CurrencyDao to spend 16750000 LST_token
    LST_token.approve(CurrencyDao.address, Web3.toWei(16750000, 'ether'), {'from': _pool_owner})
    assert LST_token.allowance(_pool_owner, CurrencyDao.address) == Web3.toWei(16750000, 'ether')
    # set stake lookup for and register name for names of lengths 1 to 4
    _pool_name = None
    # verify _next_name_id
    assert PoolNameRegistry.next_name_id({'from': anyone}) == 0
    for _name_length, _stake_amount in POOL_NAME_REGISTRATION_LST_STAKE_PER_NAME_LENGTH.items():
        _name_length = int(_name_length)
        ProtocolDaoContract.set_pool_name_registration_stake_lookup(_name_length, Web3.toWei(_stake_amount, 'ether'), {'from': Governor})
        if _name_length == 4:
            _pool_name = POOL_NAME_ABCD
        elif _name_length == 3:
            _pool_name = POOL_NAME_ABC
        elif _name_length == 2:
            _pool_name = POOL_NAME_AB
        elif _name_length == 1:
            _pool_name = POOL_NAME_A
        assert not _pool_name is None
        # _pool_owner registers the pool name
        PoolNameRegistry.register_name(_pool_name, {'from': _pool_owner, 'gas': 250000})

    _pool_name = POOL_NAME_LIONFURY
    # _pool_owner registers the pool name
    PoolNameRegistry.register_name(_pool_name, {'from': _pool_owner, 'gas': 250000})
    # verify _next_name_id
    assert PoolNameRegistry.next_name_id({'from': anyone}) == 5
    # verify LST balance of _pool_owner
    assert LST_token.balanceOf(_pool_owner, {'from': anyone}) == 0
    # verify LST balance of PoolNameRegistry
    assert LST_token.balanceOf(PoolNameRegistry.address, {'from': anyone}) == Web3.toWei(16750000, 'ether')
    # de-register names
    for _name_length, _stake_amount in POOL_NAME_REGISTRATION_LST_STAKE_PER_NAME_LENGTH.items():
        _name_length = int(_name_length)
        if _name_length == 4:
            _pool_name = POOL_NAME_ABCD
        elif _name_length == 3:
            _pool_name = POOL_NAME_ABC
        elif _name_length == 2:
            _pool_name = POOL_NAME_AB
        elif _name_length == 1:
            _pool_name = POOL_NAME_A
        assert not _pool_name is None
        # _pool_owner de-registers the pool name
        PoolNameRegistry.deregister_name(_pool_name, {'from': _pool_owner, 'gas': 250000})
    _pool_name = POOL_NAME_LIONFURY
    # _pool_owner de-registers the pool name
    PoolNameRegistry.deregister_name(_pool_name, {'from': _pool_owner, 'gas': 250000})
    # verify _next_name_id
    assert PoolNameRegistry.next_name_id({'from': anyone}) == 0
    # verify LST balance of _pool_owner
    assert LST_token.balanceOf(_pool_owner, {'from': anyone}) == Web3.toWei(16750000, 'ether')
    # verify LST balance of PoolNameRegistry
    assert LST_token.balanceOf(PoolNameRegistry.address, {'from': anyone}) == 0
