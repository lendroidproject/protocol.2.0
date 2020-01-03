import pytest

from web3 import Web3

from conftest import (
    PROTOCOL_CONSTANTS,
    POOL_NAME_REGISTRATION_MIN_STAKE_LST,
    ZERO_ADDRESS
)


def test_initialize(w3, Deployer, get_CurrencyDao_contract, ProtocolDao):
    CurrencyDao = get_CurrencyDao_contract(address=ProtocolDao.daos(PROTOCOL_CONSTANTS['DAO_CURRENCY']))
    assert not CurrencyDao.initialized()
    tx_hash = ProtocolDao.initialize_currency_dao(transact={'from': Deployer})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    assert CurrencyDao.initialized()


def test_wrap(w3, get_logs, get_ERC20_contract, get_CurrencyDao_contract,
    Deployer, Governor,
    Whale, Lend_token,
    ProtocolDao):
    # get CurrencyDao
    CurrencyDao = get_CurrencyDao_contract(address=ProtocolDao.daos(PROTOCOL_CONSTANTS['DAO_CURRENCY']))
    # assign one of the accounts as _lend_token_holder
    _lend_token_holder = w3.eth.accounts[5]
    # initialize CurrencyDao
    tx_hash = ProtocolDao.initialize_currency_dao(transact={'from': Deployer})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    tx_hash = ProtocolDao.set_token_support(Lend_token.address, True, transact={'from': Governor, 'gas': 2000000})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    # _lend_token_holder buys 1000 lend token from a 3rd party exchange
    assert Lend_token.balanceOf(_lend_token_holder) == 0
    tx_hash = Lend_token.transfer(_lend_token_holder, Web3.toWei(1000, 'ether'), transact={'from': Whale})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    assert Lend_token.balanceOf(_lend_token_holder) == Web3.toWei(1000, 'ether')
    # get L_Lend_token
    L_lend_token = get_ERC20_contract(address=CurrencyDao.token_addresses__l(Lend_token.address))
    # _lend_token_holder authorizes CurrencyDao to spend 500 Lend_token
    assert Lend_token.allowance(_lend_token_holder, CurrencyDao.address) == 0
    tx_hash = Lend_token.approve(CurrencyDao.address, Web3.toWei(800, 'ether'), transact={'from': _lend_token_holder})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    assert Lend_token.allowance(_lend_token_holder, CurrencyDao.address) == Web3.toWei(800, 'ether')
    # _lend_token_holder wraps 800 Lend_token to L_lend_token
    assert L_lend_token.balanceOf(_lend_token_holder) == 0
    tx_hash = CurrencyDao.wrap(Lend_token.address, Web3.toWei(800, 'ether'), transact={'from': _lend_token_holder, 'gas': 145000})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    # verify allowance, balances of Lend_token and L_lend_token
    assert Lend_token.allowance(_lend_token_holder, CurrencyDao.address) == 0
    assert Lend_token.balanceOf(_lend_token_holder) == Web3.toWei(200, 'ether')
    assert L_lend_token.balanceOf(_lend_token_holder) == Web3.toWei(800, 'ether')


def test_unwrap(w3, get_logs, get_ERC20_contract, get_CurrencyDao_contract,
    Deployer, Governor,
    Whale, Lend_token,
    ProtocolDao):
    # get CurrencyDao
    CurrencyDao = get_CurrencyDao_contract(address=ProtocolDao.daos(PROTOCOL_CONSTANTS['DAO_CURRENCY']))
    # assign one of the accounts as _lend_token_holder
    _lend_token_holder = w3.eth.accounts[5]
    # initialize CurrencyDao
    tx_hash = ProtocolDao.initialize_currency_dao(transact={'from': Deployer})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    tx_hash = ProtocolDao.set_token_support(Lend_token.address, True, transact={'from': Governor, 'gas': 2000000})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    # _lend_token_holder buys 1000 lend token from a 3rd party exchange
    assert Lend_token.balanceOf(_lend_token_holder) == 0
    tx_hash = Lend_token.transfer(_lend_token_holder, Web3.toWei(1000, 'ether'), transact={'from': Whale})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    assert Lend_token.balanceOf(_lend_token_holder) == Web3.toWei(1000, 'ether')
    # get L_Lend_token
    L_lend_token = get_ERC20_contract(address=CurrencyDao.token_addresses__l(Lend_token.address))
    # _lend_token_holder authorizes CurrencyDao to spend 500 Lend_token
    tx_hash = Lend_token.approve(CurrencyDao.address, Web3.toWei(800, 'ether'), transact={'from': _lend_token_holder})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    # _lend_token_holder wraps 800 Lend_token to L_lend_token
    tx_hash = CurrencyDao.wrap(Lend_token.address, Web3.toWei(800, 'ether'), transact={'from': _lend_token_holder, 'gas': 145000})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    # _lend_token_holder wraps 800 Lend_token to L_lend_token
    tx_hash = CurrencyDao.unwrap(Lend_token.address, Web3.toWei(800, 'ether'), transact={'from': _lend_token_holder, 'gas': 100000})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    # verify balances of Lend_token and L_lend_token
    assert Lend_token.balanceOf(_lend_token_holder) == Web3.toWei(1000, 'ether')
    assert L_lend_token.balanceOf(_lend_token_holder) == 0
