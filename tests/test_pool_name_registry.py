import os

import pytest

from web3 import Web3

from conftest import (
    PROTOCOL_CONSTANTS,
    POOL_NAME_REGISTRATION_MIN_STAKE_LST,
    POOL_NAME_REGISTRATION_LST_STAKE_PER_NAME_LENGTH,
    POOL_NAME_LIONFURY, POOL_NAME_ABCD, POOL_NAME_ABC, POOL_NAME_AB, POOL_NAME_A,
    ZERO_ADDRESS, EMPTY_BYTES32
)


def test_initialize(w3, Deployer, get_PoolNameRegistry_contract, ProtocolDao):
    # get PoolNameRegistry
    PoolNameRegistry = get_PoolNameRegistry_contract(address=ProtocolDao.registries(PROTOCOL_CONSTANTS['REGISTRY_POOL_NAME']))
    assert not PoolNameRegistry.initialized()
    # initialize PoolNameRegistry
    tx_hash = ProtocolDao.initialize_pool_name_registry(Web3.toWei(POOL_NAME_REGISTRATION_MIN_STAKE_LST, 'ether'), transact={'from': Deployer})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    assert PoolNameRegistry.initialized()
    assert PoolNameRegistry.name_registration_minimum_stake() == Web3.toWei(POOL_NAME_REGISTRATION_MIN_STAKE_LST, 'ether')


def test_pause_and_unpause(w3, Deployer, EscapeHatchManager, get_PoolNameRegistry_contract, ProtocolDao):
    # get PoolNameRegistry
    PoolNameRegistry = get_PoolNameRegistry_contract(address=ProtocolDao.registries(PROTOCOL_CONSTANTS['REGISTRY_POOL_NAME']))
    # initialize PoolNameRegistry
    tx_hash = ProtocolDao.initialize_pool_name_registry(Web3.toWei(POOL_NAME_REGISTRATION_MIN_STAKE_LST, 'ether'), transact={'from': Deployer})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    assert not PoolNameRegistry.paused()
    tx_hash = ProtocolDao.toggle_registry_pause(PROTOCOL_CONSTANTS['REGISTRY_POOL_NAME'], True, transact={'from': EscapeHatchManager})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    assert PoolNameRegistry.paused()
    tx_hash = ProtocolDao.toggle_registry_pause(PROTOCOL_CONSTANTS['REGISTRY_POOL_NAME'], False, transact={'from': EscapeHatchManager})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    assert not PoolNameRegistry.paused()

def test_set_name_registration_stake_lookup(w3,
    Deployer, Governor,
    get_PoolNameRegistry_contract, ProtocolDao):
    # get PoolNameRegistry
    PoolNameRegistry = get_PoolNameRegistry_contract(address=ProtocolDao.registries(PROTOCOL_CONSTANTS['REGISTRY_POOL_NAME']))
    # initialize PoolNameRegistry
    tx_hash = ProtocolDao.initialize_pool_name_registry(Web3.toWei(POOL_NAME_REGISTRATION_MIN_STAKE_LST, 'ether'), transact={'from': Deployer})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    # set stake lookup for name lengths
    for _name_length, _stake_amount in POOL_NAME_REGISTRATION_LST_STAKE_PER_NAME_LENGTH.items():
        _name_length = int(_name_length)
        assert PoolNameRegistry.name_registration_stake_lookup__stake(_name_length) == 0
        tx_hash = ProtocolDao.set_pool_name_registration_stake_lookup(_name_length, Web3.toWei(_stake_amount, 'ether'), transact={'from': Governor})
        tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
        assert tx_receipt['status'] == 1
        assert PoolNameRegistry.name_registration_stake_lookup__stake(_name_length) == Web3.toWei(_stake_amount, 'ether')


def test_register_names_with_variable_lengths(w3,
    Whale, Deployer, Governor,
    LST_token,
    get_PoolNameRegistry_contract, get_CurrencyDao_contract,
    ProtocolDao):
    # get CurrencyDao
    CurrencyDao = get_CurrencyDao_contract(address=ProtocolDao.daos(PROTOCOL_CONSTANTS['DAO_CURRENCY']))
    # get PoolNameRegistry
    PoolNameRegistry = get_PoolNameRegistry_contract(address=ProtocolDao.registries(PROTOCOL_CONSTANTS['REGISTRY_POOL_NAME']))
    # assign one of the accounts as _pool_owner
    _pool_owner = w3.eth.accounts[5]
    # initialize CurrencyDao
    tx_hash = ProtocolDao.initialize_currency_dao(transact={'from': Deployer})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    # initialize PoolNameRegistry
    tx_hash = ProtocolDao.initialize_pool_name_registry(Web3.toWei(POOL_NAME_REGISTRATION_MIN_STAKE_LST, 'ether'), transact={'from': Deployer})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    # _pool_owner buys 16750000 LST_token from a 3rd party exchange
    tx_hash = LST_token.transfer(_pool_owner, Web3.toWei(16750000, 'ether'), transact={'from': Whale})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    assert LST_token.balanceOf(_pool_owner) == Web3.toWei(16750000, 'ether')
    # _pool_owner authorizes CurrencyDao to spend 16750000 LST_token
    tx_hash = LST_token.approve(CurrencyDao.address, Web3.toWei(16750000, 'ether'), transact={'from': _pool_owner})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    assert LST_token.allowance(_pool_owner, CurrencyDao.address) == Web3.toWei(16750000, 'ether')
    # set stake lookup for and register name for names of lengths 1 to 4
    _pool_name = None
    _next_name_id = PoolNameRegistry.next_name_id()
    # verify _next_name_id
    assert _next_name_id == 0
    for _name_length, _stake_amount in POOL_NAME_REGISTRATION_LST_STAKE_PER_NAME_LENGTH.items():
        _name_length = int(_name_length)
        tx_hash = ProtocolDao.set_pool_name_registration_stake_lookup(_name_length, Web3.toWei(_stake_amount, 'ether'), transact={'from': Governor})
        tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
        assert tx_receipt['status'] == 1
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
        tx_hash = PoolNameRegistry.register_name(_pool_name, transact={'from': _pool_owner, 'gas': 250000})
        tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
        assert tx_receipt['status'] == 1
        # verify registerd_name stats
        assert PoolNameRegistry.name_to_id(_pool_name) == _next_name_id
        assert PoolNameRegistry.names__id(_next_name_id) == _next_name_id
        assert PoolNameRegistry.names__name(_next_name_id) == _pool_name
        assert PoolNameRegistry.names__operator(_next_name_id) == _pool_owner
        assert PoolNameRegistry.names__LST_staked(_next_name_id) == PoolNameRegistry.name_registration_stake_lookup__stake(_name_length)
        # verify _next_name_id
        _next_name_id += 1
        assert _next_name_id == PoolNameRegistry.next_name_id()

    _pool_name = POOL_NAME_LIONFURY
    # _pool_owner registers the pool name
    tx_hash = PoolNameRegistry.register_name(_pool_name, transact={'from': _pool_owner, 'gas': 250000})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    # verify registerd_name stats
    assert PoolNameRegistry.name_to_id(_pool_name) == _next_name_id
    assert PoolNameRegistry.names__id(_next_name_id) == _next_name_id
    assert PoolNameRegistry.names__name(_next_name_id) == _pool_name
    assert PoolNameRegistry.names__operator(_next_name_id) == _pool_owner
    assert PoolNameRegistry.names__LST_staked(_next_name_id) == PoolNameRegistry.name_registration_minimum_stake()
    assert PoolNameRegistry.names__interest_pool_registered(_next_name_id) == False
    assert PoolNameRegistry.names__underwriter_pool_registered(_next_name_id) == False
    # verify next_name_id
    _next_name_id += 1
    assert _next_name_id == PoolNameRegistry.next_name_id()
    # verify LST balance of _pool_owner
    assert LST_token.balanceOf(_pool_owner) == 0
    # verify LST balance of PoolNameRegistry
    assert LST_token.balanceOf(PoolNameRegistry.address) == Web3.toWei(16750000, 'ether')


def test_fail_when_registering_duplicate_names(w3,
    Whale, Deployer, Governor,
    LST_token,
    get_PoolNameRegistry_contract, get_CurrencyDao_contract,
    ProtocolDao):
    # get CurrencyDao
    CurrencyDao = get_CurrencyDao_contract(address=ProtocolDao.daos(PROTOCOL_CONSTANTS['DAO_CURRENCY']))
    # get PoolNameRegistry
    PoolNameRegistry = get_PoolNameRegistry_contract(address=ProtocolDao.registries(PROTOCOL_CONSTANTS['REGISTRY_POOL_NAME']))
    # assign one of the accounts as _pool_owner
    _pool_owner = w3.eth.accounts[5]
    # assign one of the accounts as _pool_owner_2
    _pool_owner_2 = w3.eth.accounts[6]
    # initialize CurrencyDao
    tx_hash = ProtocolDao.initialize_currency_dao(transact={'from': Deployer})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    # initialize PoolNameRegistry
    tx_hash = ProtocolDao.initialize_pool_name_registry(Web3.toWei(POOL_NAME_REGISTRATION_MIN_STAKE_LST, 'ether'), transact={'from': Deployer})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    # _pool_owner buys POOL_NAME_REGISTRATION_MIN_STAKE_LST LST_token from a 3rd party exchange
    tx_hash = LST_token.transfer(_pool_owner, Web3.toWei(POOL_NAME_REGISTRATION_MIN_STAKE_LST, 'ether'), transact={'from': Whale})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    assert LST_token.balanceOf(_pool_owner) == Web3.toWei(POOL_NAME_REGISTRATION_MIN_STAKE_LST, 'ether')
    # _pool_owner authorizes CurrencyDao to spend POOL_NAME_REGISTRATION_MIN_STAKE_LST LST_token
    tx_hash = LST_token.approve(CurrencyDao.address, Web3.toWei(POOL_NAME_REGISTRATION_MIN_STAKE_LST, 'ether'), transact={'from': _pool_owner})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    assert LST_token.allowance(_pool_owner, CurrencyDao.address) == Web3.toWei(POOL_NAME_REGISTRATION_MIN_STAKE_LST, 'ether')
    # _pool_owner registers the POOL_NAME_LIONFURY
    _pool_name = POOL_NAME_LIONFURY
    tx_hash = PoolNameRegistry.register_name(_pool_name, transact={'from': _pool_owner, 'gas': 250000})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    # _pool_owner_2 buys POOL_NAME_REGISTRATION_MIN_STAKE_LST LST_token from a 3rd party exchange
    tx_hash = LST_token.transfer(_pool_owner_2, Web3.toWei(POOL_NAME_REGISTRATION_MIN_STAKE_LST, 'ether'), transact={'from': Whale})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    assert LST_token.balanceOf(_pool_owner_2) == Web3.toWei(POOL_NAME_REGISTRATION_MIN_STAKE_LST, 'ether')
    # _pool_owner_2 authorizes CurrencyDao to spend POOL_NAME_REGISTRATION_MIN_STAKE_LST LST_token
    tx_hash = LST_token.approve(CurrencyDao.address, Web3.toWei(POOL_NAME_REGISTRATION_MIN_STAKE_LST, 'ether'), transact={'from': _pool_owner_2})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    assert LST_token.allowance(_pool_owner_2, CurrencyDao.address) == Web3.toWei(POOL_NAME_REGISTRATION_MIN_STAKE_LST, 'ether')
    # _pool_owner_2 registers the POOL_NAME_LIONFURY
    assert PoolNameRegistry.name_exists(_pool_name)
    tx_hash = PoolNameRegistry.register_name(_pool_name, transact={'from': _pool_owner_2, 'gas': 250000})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 0


def test_deregister_names_with_variable_lengths(w3,
    Whale, Deployer, Governor,
    LST_token,
    get_PoolNameRegistry_contract, get_CurrencyDao_contract,
    ProtocolDao):
    # get CurrencyDao
    CurrencyDao = get_CurrencyDao_contract(address=ProtocolDao.daos(PROTOCOL_CONSTANTS['DAO_CURRENCY']))
    # get PoolNameRegistry
    PoolNameRegistry = get_PoolNameRegistry_contract(address=ProtocolDao.registries(PROTOCOL_CONSTANTS['REGISTRY_POOL_NAME']))
    # assign one of the accounts as _pool_owner
    _pool_owner = w3.eth.accounts[5]
    # initialize CurrencyDao
    tx_hash = ProtocolDao.initialize_currency_dao(transact={'from': Deployer})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    # initialize PoolNameRegistry
    tx_hash = ProtocolDao.initialize_pool_name_registry(Web3.toWei(POOL_NAME_REGISTRATION_MIN_STAKE_LST, 'ether'), transact={'from': Deployer})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    # _pool_owner buys 16750000 LST_token from a 3rd party exchange
    tx_hash = LST_token.transfer(_pool_owner, Web3.toWei(16750000, 'ether'), transact={'from': Whale})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    assert LST_token.balanceOf(_pool_owner) == Web3.toWei(16750000, 'ether')
    # _pool_owner authorizes CurrencyDao to spend 16750000 LST_token
    tx_hash = LST_token.approve(CurrencyDao.address, Web3.toWei(16750000, 'ether'), transact={'from': _pool_owner})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    assert LST_token.allowance(_pool_owner, CurrencyDao.address) == Web3.toWei(16750000, 'ether')
    # set stake lookup for and register name for names of lengths 1 to 4
    _pool_name = None
    # verify _next_name_id
    assert PoolNameRegistry.next_name_id() == 0
    for _name_length, _stake_amount in POOL_NAME_REGISTRATION_LST_STAKE_PER_NAME_LENGTH.items():
        _name_length = int(_name_length)
        tx_hash = ProtocolDao.set_pool_name_registration_stake_lookup(_name_length, Web3.toWei(_stake_amount, 'ether'), transact={'from': Governor})
        tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
        assert tx_receipt['status'] == 1
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
        tx_hash = PoolNameRegistry.register_name(_pool_name, transact={'from': _pool_owner, 'gas': 250000})
        tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
        assert tx_receipt['status'] == 1

    _pool_name = POOL_NAME_LIONFURY
    # _pool_owner registers the pool name
    tx_hash = PoolNameRegistry.register_name(_pool_name, transact={'from': _pool_owner, 'gas': 250000})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    # verify _next_name_id
    assert PoolNameRegistry.next_name_id() == 5
    # verify LST balance of _pool_owner
    assert LST_token.balanceOf(_pool_owner) == 0
    # verify LST balance of PoolNameRegistry
    assert LST_token.balanceOf(PoolNameRegistry.address) == Web3.toWei(16750000, 'ether')
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
        tx_hash = PoolNameRegistry.deregister_name(_pool_name, transact={'from': _pool_owner, 'gas': 250000})
        tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
        assert tx_receipt['status'] == 1
    _pool_name = POOL_NAME_LIONFURY
    # _pool_owner de-registers the pool name
    tx_hash = PoolNameRegistry.deregister_name(_pool_name, transact={'from': _pool_owner, 'gas': 250000})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    # verify _next_name_id
    assert PoolNameRegistry.next_name_id() == 0
    # verify LST balance of _pool_owner
    assert LST_token.balanceOf(_pool_owner) == Web3.toWei(16750000, 'ether')
    # verify LST balance of PoolNameRegistry
    assert LST_token.balanceOf(PoolNameRegistry.address) == 0
