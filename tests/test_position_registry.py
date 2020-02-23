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


def test_initialize(accounts, Deployer, get_PositionRegistry_contract, ProtocolDaoContract):
    anyone = accounts[-1]
    # get PositionRegistry
    PositionRegistry = get_PositionRegistry_contract(address=ProtocolDaoContract.registries(PROTOCOL_CONSTANTS['REGISTRY_POSITION']))
    assert not PositionRegistry.initialized({'from': anyone})
    # initialize PositionRegistry
    ProtocolDaoContract.initialize_position_registry({'from': Deployer})
    assert PositionRegistry.initialized({'from': anyone})


def test_pause_and_unpause(accounts, Deployer, EscapeHatchManager, get_PositionRegistry_contract, ProtocolDaoContract):
    anyone = accounts[-1]
    # get PositionRegistry
    PositionRegistry = get_PositionRegistry_contract(address=ProtocolDaoContract.registries(PROTOCOL_CONSTANTS['REGISTRY_POSITION']))
    # initialize PositionRegistry
    ProtocolDaoContract.initialize_position_registry({'from': Deployer})
    assert not PositionRegistry.paused({'from': anyone})
    ProtocolDaoContract.toggle_registry_pause(PROTOCOL_CONSTANTS['REGISTRY_POSITION'], True, {'from': EscapeHatchManager})
    assert PositionRegistry.paused({'from': anyone})
    ProtocolDaoContract.toggle_registry_pause(PROTOCOL_CONSTANTS['REGISTRY_POSITION'], False, {'from': EscapeHatchManager})
    assert not PositionRegistry.paused({'from': anyone})


def test_pause_failed_when_paused(accounts, assert_tx_failed, Deployer, EscapeHatchManager, get_PositionRegistry_contract, ProtocolDaoContract):
    anyone = accounts[-1]
    PositionRegistry = get_PositionRegistry_contract(address=ProtocolDaoContract.registries(PROTOCOL_CONSTANTS['REGISTRY_POSITION']))
    ProtocolDaoContract.initialize_position_registry({'from': Deployer})
    ProtocolDaoContract.toggle_registry_pause(PROTOCOL_CONSTANTS['REGISTRY_POSITION'], True, {'from': EscapeHatchManager})
    assert_tx_failed(lambda: ProtocolDaoContract.toggle_registry_pause(PROTOCOL_CONSTANTS['REGISTRY_POSITION'], True, {'from': EscapeHatchManager}))


def test_pause_failed_when_uninitialized(accounts, assert_tx_failed, Deployer, EscapeHatchManager, get_PositionRegistry_contract, ProtocolDaoContract):
    anyone = accounts[-1]
    PositionRegistry = get_PositionRegistry_contract(address=ProtocolDaoContract.registries(PROTOCOL_CONSTANTS['REGISTRY_POSITION']))
    assert_tx_failed(lambda: ProtocolDaoContract.toggle_registry_pause(PROTOCOL_CONSTANTS['REGISTRY_POSITION'], True, {'from': EscapeHatchManager}))


def test_pause_failed_when_called_by_non_protocol_dao(accounts, assert_tx_failed, Deployer, EscapeHatchManager, get_PositionRegistry_contract, ProtocolDaoContract):
    anyone = accounts[-1]
    PositionRegistry = get_PositionRegistry_contract(address=ProtocolDaoContract.registries(PROTOCOL_CONSTANTS['REGISTRY_POSITION']))
    ProtocolDaoContract.initialize_position_registry({'from': Deployer})
    # Tx failed
    for account in accounts:
        assert_tx_failed(lambda: PositionRegistry.pause({'from': account}))


def test_unpause_failed_when_unpaused(accounts, assert_tx_failed, Deployer, EscapeHatchManager, get_PositionRegistry_contract, ProtocolDaoContract):
    anyone = accounts[-1]
    PositionRegistry = get_PositionRegistry_contract(address=ProtocolDaoContract.registries(PROTOCOL_CONSTANTS['REGISTRY_POSITION']))
    ProtocolDaoContract.initialize_position_registry({'from': Deployer})
    assert_tx_failed(lambda: ProtocolDaoContract.toggle_registry_pause(PROTOCOL_CONSTANTS['REGISTRY_POSITION'], False, {'from': EscapeHatchManager}))


def test_unpause_failed_when_uninitialized(accounts, assert_tx_failed, Deployer, EscapeHatchManager, get_PositionRegistry_contract, ProtocolDaoContract):
    anyone = accounts[-1]
    PositionRegistry = get_PositionRegistry_contract(address=ProtocolDaoContract.registries(PROTOCOL_CONSTANTS['REGISTRY_POSITION']))
    assert_tx_failed(lambda: ProtocolDaoContract.toggle_registry_pause(PROTOCOL_CONSTANTS['REGISTRY_POSITION'], False, {'from': EscapeHatchManager}))


def test_unpause_failed_when_called_by_non_protocol_dao(accounts, assert_tx_failed, Deployer, EscapeHatchManager, get_PositionRegistry_contract, ProtocolDaoContract):
    anyone = accounts[-1]
    PositionRegistry = get_PositionRegistry_contract(address=ProtocolDaoContract.registries(PROTOCOL_CONSTANTS['REGISTRY_POSITION']))
    ProtocolDaoContract.initialize_position_registry({'from': Deployer})
    # Tx failed
    for account in accounts:
        assert_tx_failed(lambda: PositionRegistry.unpause({'from': account}))
