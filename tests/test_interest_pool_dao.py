import os

import pytest

from web3 import Web3

from conftest import (
    PROTOCOL_CONSTANTS,
    POOL_NAME_REGISTRATION_MIN_STAKE_LST,
    ZERO_ADDRESS, EMPTY_BYTES32, H20
)


def test_initialize(w3, Deployer, get_InterestPoolDao_contract, ProtocolDao):
    InterestPoolDao = get_InterestPoolDao_contract(address=ProtocolDao.daos(PROTOCOL_CONSTANTS['DAO_INTEREST_POOL']))
    assert not InterestPoolDao.initialized()
    tx_hash = ProtocolDao.initialize_interest_pool_dao(transact={'from': Deployer})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    assert InterestPoolDao.initialized()


def test_split(w3,
        Whale, Deployer, Governor,
        Lend_token,
        get_ERC20_contract, get_MFT_contract,
        get_CurrencyDao_contract, get_InterestPoolDao_contract,
        ProtocolDao):
    # get CurrencyDao
    CurrencyDao = get_CurrencyDao_contract(address=ProtocolDao.daos(PROTOCOL_CONSTANTS['DAO_CURRENCY']))
    # get InterestPoolDao
    InterestPoolDao = get_InterestPoolDao_contract(address=ProtocolDao.daos(PROTOCOL_CONSTANTS['DAO_INTEREST_POOL']))
    # assign one of the accounts as _lend_token_holder
    _lend_token_holder = w3.eth.accounts[5]
    # initialize CurrencyDao
    tx_hash = ProtocolDao.initialize_currency_dao(transact={'from': Deployer})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    # initialize InterestPoolDao
    tx_hash = ProtocolDao.initialize_interest_pool_dao(transact={'from': Deployer})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    # set support for Lend_token
    tx_hash = ProtocolDao.set_token_support(Lend_token.address, True, transact={'from': Governor, 'gas': 2000000})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    # get L_Lend_token
    L_lend_token = get_ERC20_contract(address=CurrencyDao.token_addresses__l(Lend_token.address))
    # get F_Lend_token
    F_lend_token = get_MFT_contract(address=CurrencyDao.token_addresses__f(Lend_token.address))
    # get I_Lend_token
    I_lend_token = get_MFT_contract(address=CurrencyDao.token_addresses__i(Lend_token.address))
    # _lend_token_holder buys 1000 lend token from a 3rd party exchange
    tx_hash = Lend_token.transfer(_lend_token_holder, Web3.toWei(1000, 'ether'), transact={'from': Whale})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    assert Lend_token.balanceOf(_lend_token_holder) == Web3.toWei(1000, 'ether')
    # _lend_token_holder authorizes CurrencyDao to spend 800 Lend_token
    tx_hash = Lend_token.approve(CurrencyDao.address, Web3.toWei(800, 'ether'), transact={'from': _lend_token_holder})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    assert Lend_token.allowance(_lend_token_holder, CurrencyDao.address) == Web3.toWei(800, 'ether')
    # _lend_token_holder wraps 800 Lend_token to L_lend_token
    assert L_lend_token.balanceOf(_lend_token_holder) == 0
    tx_hash = CurrencyDao.wrap(Lend_token.address, Web3.toWei(800, 'ether'), transact={'from': _lend_token_holder, 'gas': 145000})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    assert L_lend_token.balanceOf(_lend_token_holder) == Web3.toWei(800, 'ether')
    # _lend_token_holder splits 600 L_lend_tokens into 600 F_lend_tokens and 600 I_lend_tokens for H20
    tx_hash = InterestPoolDao.split(Lend_token.address, H20, Web3.toWei(600, 'ether'), transact={'from': _lend_token_holder, 'gas': 640000})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    assert L_lend_token.balanceOf(_lend_token_holder) == Web3.toWei(200, 'ether')
    _f_id = F_lend_token.id(Lend_token.address, H20, ZERO_ADDRESS, 0)
    _i_id = I_lend_token.id(Lend_token.address, H20, ZERO_ADDRESS, 0)
    assert F_lend_token.balanceOf(_lend_token_holder, _f_id) == Web3.toWei(600, 'ether')
    assert I_lend_token.balanceOf(_lend_token_holder, _i_id) == Web3.toWei(600, 'ether')


def test_fuse(w3,
        Whale, Deployer, Governor,
        Lend_token,
        get_ERC20_contract, get_MFT_contract,
        get_CurrencyDao_contract, get_InterestPoolDao_contract,
        ProtocolDao):
    # get CurrencyDao
    CurrencyDao = get_CurrencyDao_contract(address=ProtocolDao.daos(PROTOCOL_CONSTANTS['DAO_CURRENCY']))
    # get InterestPoolDao
    InterestPoolDao = get_InterestPoolDao_contract(address=ProtocolDao.daos(PROTOCOL_CONSTANTS['DAO_INTEREST_POOL']))
    # assign one of the accounts as _lend_token_holder
    _lend_token_holder = w3.eth.accounts[5]
    # initialize CurrencyDao
    tx_hash = ProtocolDao.initialize_currency_dao(transact={'from': Deployer})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    # initialize InterestPoolDao
    tx_hash = ProtocolDao.initialize_interest_pool_dao(transact={'from': Deployer})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    # set support for Lend_token
    tx_hash = ProtocolDao.set_token_support(Lend_token.address, True, transact={'from': Governor, 'gas': 2000000})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    # get L_Lend_token
    L_lend_token = get_ERC20_contract(address=CurrencyDao.token_addresses__l(Lend_token.address))
    # get F_Lend_token
    F_lend_token = get_MFT_contract(address=CurrencyDao.token_addresses__f(Lend_token.address))
    # get I_Lend_token
    I_lend_token = get_MFT_contract(address=CurrencyDao.token_addresses__i(Lend_token.address))
    # _lend_token_holder buys 1000 lend token from a 3rd party exchange
    tx_hash = Lend_token.transfer(_lend_token_holder, Web3.toWei(1000, 'ether'), transact={'from': Whale})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    # _lend_token_holder authorizes CurrencyDao to spend 800 Lend_token
    tx_hash = Lend_token.approve(CurrencyDao.address, Web3.toWei(800, 'ether'), transact={'from': _lend_token_holder})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    # _lend_token_holder wraps 800 Lend_token to L_lend_token
    assert L_lend_token.balanceOf(_lend_token_holder) == 0
    tx_hash = CurrencyDao.wrap(Lend_token.address, Web3.toWei(800, 'ether'), transact={'from': _lend_token_holder, 'gas': 145000})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    # _lend_token_holder splits 600 L_lend_tokens into 600 F_lend_tokens and 600 I_lend_tokens for H20
    tx_hash = InterestPoolDao.split(Lend_token.address, H20, Web3.toWei(600, 'ether'), transact={'from': _lend_token_holder, 'gas': 640000})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    _f_id = F_lend_token.id(Lend_token.address, H20, ZERO_ADDRESS, 0)
    _i_id = I_lend_token.id(Lend_token.address, H20, ZERO_ADDRESS, 0)
    assert L_lend_token.balanceOf(_lend_token_holder) == Web3.toWei(200, 'ether')
    _f_id = F_lend_token.id(Lend_token.address, H20, ZERO_ADDRESS, 0)
    _i_id = I_lend_token.id(Lend_token.address, H20, ZERO_ADDRESS, 0)
    assert F_lend_token.balanceOf(_lend_token_holder, _f_id) == Web3.toWei(600, 'ether')
    assert I_lend_token.balanceOf(_lend_token_holder, _i_id) == Web3.toWei(600, 'ether')
    # _lend_token_holder fuses 400 F_lend_tokens and 400 I_lend_tokens for H20 into 400 L_lend_tokens
    tx_hash = InterestPoolDao.fuse(Lend_token.address, H20, Web3.toWei(400, 'ether'), transact={'from': _lend_token_holder, 'gas': 150000})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    assert L_lend_token.balanceOf(_lend_token_holder) == Web3.toWei(600, 'ether')
    assert F_lend_token.balanceOf(_lend_token_holder, _f_id) == Web3.toWei(200, 'ether')
    assert I_lend_token.balanceOf(_lend_token_holder, _i_id) == Web3.toWei(200, 'ether')
