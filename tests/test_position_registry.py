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


def test_initialize(w3, Deployer, get_PositionRegistry_contract, ProtocolDao):
    # get PositionRegistry
    PositionRegistry = get_PositionRegistry_contract(address=ProtocolDao.registries(PROTOCOL_CONSTANTS['REGISTRY_POSITION']))
    assert not PositionRegistry.initialized()
    # initialize PositionRegistry
    tx_hash = ProtocolDao.initialize_position_registry(transact={'from': Deployer})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    assert PositionRegistry.initialized()


def test_pause_and_unpause(w3, Deployer, EscapeHatchManager, get_PositionRegistry_contract, ProtocolDao):
    # get PositionRegistry
    PositionRegistry = get_PositionRegistry_contract(address=ProtocolDao.registries(PROTOCOL_CONSTANTS['REGISTRY_POSITION']))
    # initialize PositionRegistry
    tx_hash = ProtocolDao.initialize_position_registry(transact={'from': Deployer})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    assert not PositionRegistry.paused()
    tx_hash = ProtocolDao.toggle_registry_pause(PROTOCOL_CONSTANTS['REGISTRY_POSITION'], True, transact={'from': EscapeHatchManager})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    assert PositionRegistry.paused()
    tx_hash = ProtocolDao.toggle_registry_pause(PROTOCOL_CONSTANTS['REGISTRY_POSITION'], False, transact={'from': EscapeHatchManager})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    assert not PositionRegistry.paused()
