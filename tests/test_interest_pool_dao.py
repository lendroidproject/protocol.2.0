import os

import pytest

from web3 import Web3

from conftest import (
    PROTOCOL_CONSTANTS,
    POOL_NAME_REGISTRATION_MIN_STAKE_LST,
    ZERO_ADDRESS, EMPTY_BYTES32, H20
)


def test_initialize(accounts, Deployer, get_InterestPoolDao_contract, ProtocolDaoContract):
    anyone = accounts[-1]
    InterestPoolDaoContract = get_InterestPoolDao_contract(address=ProtocolDaoContract.daos(PROTOCOL_CONSTANTS['DAO_INTEREST_POOL']))
    assert not InterestPoolDaoContract.initialized({'from': anyone})
    ProtocolDaoContract.initialize_interest_pool_dao({'from': Deployer})
    assert InterestPoolDaoContract.initialized({'from': anyone})


def test_pause_and_unpause(accounts, Deployer, EscapeHatchManager, get_InterestPoolDao_contract, ProtocolDaoContract):
    anyone = accounts[-1]
    InterestPoolDaoContract = get_InterestPoolDao_contract(address=ProtocolDaoContract.daos(PROTOCOL_CONSTANTS['DAO_INTEREST_POOL']))
    ProtocolDaoContract.initialize_interest_pool_dao({'from': Deployer})
    assert not InterestPoolDaoContract.paused({'from': anyone})
    ProtocolDaoContract.toggle_dao_pause(PROTOCOL_CONSTANTS['DAO_INTEREST_POOL'], True, {'from': EscapeHatchManager})
    assert InterestPoolDaoContract.paused({'from': anyone})
    ProtocolDaoContract.toggle_dao_pause(PROTOCOL_CONSTANTS['DAO_INTEREST_POOL'], False, {'from': EscapeHatchManager})
    assert not InterestPoolDaoContract.paused({'from': anyone})


def test_pause_failed_when_paused(accounts, assert_tx_failed, Deployer, EscapeHatchManager, get_InterestPoolDao_contract, ProtocolDaoContract):
    anyone = accounts[-1]
    InterestPoolDaoContract = get_InterestPoolDao_contract(address=ProtocolDaoContract.daos(PROTOCOL_CONSTANTS['DAO_INTEREST_POOL']))
    ProtocolDaoContract.initialize_interest_pool_dao({'from': Deployer})
    ProtocolDaoContract.toggle_dao_pause(PROTOCOL_CONSTANTS['DAO_INTEREST_POOL'], True, {'from': EscapeHatchManager})
    assert_tx_failed(lambda: ProtocolDaoContract.toggle_dao_pause(PROTOCOL_CONSTANTS['DAO_INTEREST_POOL'], True, {'from': EscapeHatchManager}))


def test_pause_failed_when_uninitialized(accounts, assert_tx_failed, Deployer, EscapeHatchManager, get_InterestPoolDao_contract, ProtocolDaoContract):
    anyone = accounts[-1]
    InterestPoolDaoContract = get_InterestPoolDao_contract(address=ProtocolDaoContract.daos(PROTOCOL_CONSTANTS['DAO_INTEREST_POOL']))
    assert_tx_failed(lambda: ProtocolDaoContract.toggle_dao_pause(PROTOCOL_CONSTANTS['DAO_INTEREST_POOL'], True, {'from': EscapeHatchManager}))


def test_pause_failed_when_called_by_non_protocol_dao(accounts, assert_tx_failed, Deployer, EscapeHatchManager, get_InterestPoolDao_contract, ProtocolDaoContract):
    anyone = accounts[-1]
    InterestPoolDaoContract = get_InterestPoolDao_contract(address=ProtocolDaoContract.daos(PROTOCOL_CONSTANTS['DAO_INTEREST_POOL']))
    ProtocolDaoContract.initialize_interest_pool_dao({'from': Deployer})
    # Tx failed
    for account in accounts:
        assert_tx_failed(lambda: InterestPoolDaoContract.pause({'from': account}))


def test_unpause_failed_when_unpaused(accounts, assert_tx_failed, Deployer, EscapeHatchManager, get_InterestPoolDao_contract, ProtocolDaoContract):
    anyone = accounts[-1]
    InterestPoolDaoContract = get_InterestPoolDao_contract(address=ProtocolDaoContract.daos(PROTOCOL_CONSTANTS['DAO_INTEREST_POOL']))
    ProtocolDaoContract.initialize_interest_pool_dao({'from': Deployer})
    assert_tx_failed(lambda: ProtocolDaoContract.toggle_dao_pause(PROTOCOL_CONSTANTS['DAO_INTEREST_POOL'], False, {'from': EscapeHatchManager}))


def test_unpause_failed_when_uninitialized(accounts, assert_tx_failed, Deployer, EscapeHatchManager, get_InterestPoolDao_contract, ProtocolDaoContract):
    anyone = accounts[-1]
    InterestPoolDaoContract = get_InterestPoolDao_contract(address=ProtocolDaoContract.daos(PROTOCOL_CONSTANTS['DAO_INTEREST_POOL']))
    assert_tx_failed(lambda: ProtocolDaoContract.toggle_dao_pause(PROTOCOL_CONSTANTS['DAO_INTEREST_POOL'], False, {'from': EscapeHatchManager}))


def test_unpause_failed_when_called_by_non_protocol_dao(accounts, assert_tx_failed, Deployer, EscapeHatchManager, get_InterestPoolDao_contract, ProtocolDaoContract):
    anyone = accounts[-1]
    InterestPoolDaoContract = get_InterestPoolDao_contract(address=ProtocolDaoContract.daos(PROTOCOL_CONSTANTS['DAO_INTEREST_POOL']))
    ProtocolDaoContract.initialize_interest_pool_dao({'from': Deployer})
    # Tx failed
    for account in accounts:
        assert_tx_failed(lambda: InterestPoolDaoContract.unpause({'from': account}))


def test_split(accounts, assert_tx_failed,
        Whale, Deployer, Governor,
        Lend_token,
        get_ERC20_contract, get_MFT_contract,
        get_CurrencyDao_contract, get_InterestPoolDao_contract,
        ProtocolDaoContract):
    anyone = accounts[-1]
    # get CurrencyDao
    CurrencyDao = get_CurrencyDao_contract(address=ProtocolDaoContract.daos(PROTOCOL_CONSTANTS['DAO_CURRENCY']))
    # get InterestPoolDaoContract
    InterestPoolDaoContract = get_InterestPoolDao_contract(address=ProtocolDaoContract.daos(PROTOCOL_CONSTANTS['DAO_INTEREST_POOL']))
    # assign one of the accounts as _lend_token_holder
    _lend_token_holder = accounts[5]
    # Tx fails when calling split() and InterestPoolDaoContract is not initialized
    assert_tx_failed(lambda: InterestPoolDaoContract.split(Lend_token.address, H20, Web3.toWei(600, 'ether'), {'from': _lend_token_holder, 'gas': 145000}))
    # initialize CurrencyDao
    ProtocolDaoContract.initialize_currency_dao({'from': Deployer})
    # initialize InterestPoolDaoContract
    ProtocolDaoContract.initialize_interest_pool_dao({'from': Deployer})
    # set support for Lend_token
    ProtocolDaoContract.set_token_support(Lend_token.address, True, {'from': Governor, 'gas': 2000000})
    # get L_Lend_token
    L_lend_token = get_ERC20_contract(address=CurrencyDao.token_addresses__l(Lend_token.address, {'from': anyone}))
    # get F_Lend_token
    F_lend_token = get_MFT_contract(address=CurrencyDao.token_addresses__f(Lend_token.address, {'from': anyone}))
    # get I_Lend_token
    I_lend_token = get_MFT_contract(address=CurrencyDao.token_addresses__i(Lend_token.address, {'from': anyone}))
    # _lend_token_holder buys 1000 lend token from a 3rd party exchange
    Lend_token.transfer(_lend_token_holder, Web3.toWei(1000, 'ether'), {'from': Whale})
    assert Lend_token.balanceOf(_lend_token_holder, {'from': anyone}) == Web3.toWei(1000, 'ether')
    # _lend_token_holder authorizes CurrencyDao to spend 800 Lend_token
    Lend_token.approve(CurrencyDao.address, Web3.toWei(800, 'ether'), {'from': _lend_token_holder})
    assert Lend_token.allowance(_lend_token_holder, CurrencyDao.address, {'from': anyone}) == Web3.toWei(800, 'ether')
    # _lend_token_holder wraps 800 Lend_token to L_lend_token
    assert L_lend_token.balanceOf(_lend_token_holder, {'from': anyone}) == 0
    CurrencyDao.wrap(Lend_token.address, Web3.toWei(800, 'ether'), {'from': _lend_token_holder, 'gas': 145000})
    assert L_lend_token.balanceOf(_lend_token_holder, {'from': anyone}) == Web3.toWei(800, 'ether')
    # _lend_token_holder splits 600 L_lend_tokens into 600 F_lend_tokens and 600 I_lend_tokens for H20
    InterestPoolDaoContract.split(Lend_token.address, H20, Web3.toWei(600, 'ether'), {'from': _lend_token_holder, 'gas': 700000})
    # # Tx fails when calling split() and InterestPoolDaoContract is paused
    # assert_tx_failed(lambda: InterestPoolDaoContract.split(Lend_token.address, H20, Web3.toWei(600, 'ether'), {'from': _lend_token_holder, 'gas': 145000}))
    assert L_lend_token.balanceOf(_lend_token_holder, {'from': anyone}) == Web3.toWei(200, 'ether')
    _f_id = F_lend_token.id(Lend_token.address, H20, ZERO_ADDRESS, 0, {'from': anyone})
    _i_id = I_lend_token.id(Lend_token.address, H20, ZERO_ADDRESS, 0, {'from': anyone})
    assert F_lend_token.balanceOf(_lend_token_holder, _f_id, {'from': anyone}) == Web3.toWei(600, 'ether')
    assert I_lend_token.balanceOf(_lend_token_holder, _i_id, {'from': anyone}) == Web3.toWei(600, 'ether')


def test_fuse(accounts,
        Whale, Deployer, Governor,
        Lend_token,
        get_ERC20_contract, get_MFT_contract,
        get_CurrencyDao_contract, get_InterestPoolDao_contract,
        ProtocolDaoContract):
    anyone = accounts[-1]
    # get CurrencyDao
    CurrencyDao = get_CurrencyDao_contract(address=ProtocolDaoContract.daos(PROTOCOL_CONSTANTS['DAO_CURRENCY']))
    # get InterestPoolDaoContract
    InterestPoolDaoContract = get_InterestPoolDao_contract(address=ProtocolDaoContract.daos(PROTOCOL_CONSTANTS['DAO_INTEREST_POOL']))
    # assign one of the accounts as _lend_token_holder
    _lend_token_holder = accounts[5]
    # initialize CurrencyDao
    ProtocolDaoContract.initialize_currency_dao({'from': Deployer})
    # initialize InterestPoolDaoContract
    ProtocolDaoContract.initialize_interest_pool_dao({'from': Deployer})
    # set support for Lend_token
    ProtocolDaoContract.set_token_support(Lend_token.address, True, {'from': Governor, 'gas': 2000000})
    # get L_Lend_token
    L_lend_token = get_ERC20_contract(address=CurrencyDao.token_addresses__l(Lend_token.address, {'from': anyone}))
    # get F_Lend_token
    F_lend_token = get_MFT_contract(address=CurrencyDao.token_addresses__f(Lend_token.address, {'from': anyone}))
    # get I_Lend_token
    I_lend_token = get_MFT_contract(address=CurrencyDao.token_addresses__i(Lend_token.address, {'from': anyone}))
    # _lend_token_holder buys 1000 lend token from a 3rd party exchange
    Lend_token.transfer(_lend_token_holder, Web3.toWei(1000, 'ether'), {'from': Whale})
    # _lend_token_holder authorizes CurrencyDao to spend 800 Lend_token
    Lend_token.approve(CurrencyDao.address, Web3.toWei(800, 'ether'), {'from': _lend_token_holder})
    # _lend_token_holder wraps 800 Lend_token to L_lend_token
    assert L_lend_token.balanceOf(_lend_token_holder, {'from': anyone}) == 0
    CurrencyDao.wrap(Lend_token.address, Web3.toWei(800, 'ether'), {'from': _lend_token_holder, 'gas': 145000})
    # _lend_token_holder splits 600 L_lend_tokens into 600 F_lend_tokens and 600 I_lend_tokens for H20
    InterestPoolDaoContract.split(Lend_token.address, H20, Web3.toWei(600, 'ether'), {'from': _lend_token_holder, 'gas': 700000})
    _f_id = F_lend_token.id(Lend_token.address, H20, ZERO_ADDRESS, 0, {'from': anyone})
    _i_id = I_lend_token.id(Lend_token.address, H20, ZERO_ADDRESS, 0, {'from': anyone})
    assert L_lend_token.balanceOf(_lend_token_holder, {'from': anyone}) == Web3.toWei(200, 'ether')
    _f_id = F_lend_token.id(Lend_token.address, H20, ZERO_ADDRESS, 0, {'from': anyone})
    _i_id = I_lend_token.id(Lend_token.address, H20, ZERO_ADDRESS, 0, {'from': anyone})
    assert F_lend_token.balanceOf(_lend_token_holder, _f_id, {'from': anyone}) == Web3.toWei(600, 'ether')
    assert I_lend_token.balanceOf(_lend_token_holder, _i_id, {'from': anyone}) == Web3.toWei(600, 'ether')
    # _lend_token_holder fuses 400 F_lend_tokens and 400 I_lend_tokens for H20 into 400 L_lend_tokens
    InterestPoolDaoContract.fuse(Lend_token.address, H20, Web3.toWei(400, 'ether'), {'from': _lend_token_holder, 'gas': 150000})
    assert L_lend_token.balanceOf(_lend_token_holder, {'from': anyone}) == Web3.toWei(600, 'ether')
    assert F_lend_token.balanceOf(_lend_token_holder, _f_id, {'from': anyone}) == Web3.toWei(200, 'ether')
    assert I_lend_token.balanceOf(_lend_token_holder, _i_id, {'from': anyone}) == Web3.toWei(200, 'ether')
