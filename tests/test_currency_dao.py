import pytest

from web3 import Web3

from conftest import (
    PROTOCOL_CONSTANTS,
    POOL_NAME_REGISTRATION_MIN_STAKE_LST,
    ZERO_ADDRESS
)


def test_initialize(accounts, Deployer, get_CurrencyDao_contract, ProtocolDaoContract):
    anyone = accounts[-1]
    CurrencyDaoContract = get_CurrencyDao_contract(address=ProtocolDaoContract.daos(PROTOCOL_CONSTANTS['DAO_CURRENCY']))
    assert not CurrencyDaoContract.initialized({'from': anyone})
    ProtocolDaoContract.initialize_currency_dao({'from': Deployer})
    assert CurrencyDaoContract.initialized({'from': anyone})


def test_pause_and_unpause(accounts, Deployer, EscapeHatchManager, get_CurrencyDao_contract, ProtocolDaoContract):
    anyone = accounts[-1]
    CurrencyDaoContract = get_CurrencyDao_contract(address=ProtocolDaoContract.daos(PROTOCOL_CONSTANTS['DAO_CURRENCY']))
    ProtocolDaoContract.initialize_currency_dao({'from': Deployer})
    assert not CurrencyDaoContract.paused({'from': anyone})
    ProtocolDaoContract.toggle_dao_pause(PROTOCOL_CONSTANTS['DAO_CURRENCY'], True, {'from': EscapeHatchManager})
    assert CurrencyDaoContract.paused({'from': anyone})
    ProtocolDaoContract.toggle_dao_pause(PROTOCOL_CONSTANTS['DAO_CURRENCY'], False, {'from': EscapeHatchManager})
    assert not CurrencyDaoContract.paused({'from': anyone})


def test_wrap(accounts, get_ERC20_contract, get_CurrencyDao_contract,
    Deployer, Governor,
    Whale, Lend_token,
    ProtocolDaoContract):
    anyone = accounts[-1]
    # get CurrencyDaoContract
    CurrencyDaoContract = get_CurrencyDao_contract(address=ProtocolDaoContract.daos(PROTOCOL_CONSTANTS['DAO_CURRENCY']))
    # assign one of the accounts as _lend_token_holder
    _lend_token_holder = accounts[5]
    # initialize CurrencyDaoContract
    ProtocolDaoContract.initialize_currency_dao({'from': Deployer})
    ProtocolDaoContract.set_token_support(Lend_token.address, True, {'from': Governor, 'gas': 2000000})
    # _lend_token_holder buys 1000 lend token from a 3rd party exchange
    assert Lend_token.balanceOf(_lend_token_holder, {'from': anyone}) == 0
    Lend_token.transfer(_lend_token_holder, Web3.toWei(1000, 'ether'), {'from': Whale})
    assert Lend_token.balanceOf(_lend_token_holder, {'from': anyone}) == Web3.toWei(1000, 'ether')
    # get L_Lend_token
    L_lend_token = get_ERC20_contract(address=CurrencyDaoContract.token_addresses__l(Lend_token.address, {'from': anyone}))
    # _lend_token_holder authorizes CurrencyDaoContract to spend 500 Lend_token
    assert Lend_token.allowance(_lend_token_holder, CurrencyDaoContract.address, {'from': anyone}) == 0
    Lend_token.approve(CurrencyDaoContract.address, Web3.toWei(800, 'ether'), {'from': _lend_token_holder})
    assert Lend_token.allowance(_lend_token_holder, CurrencyDaoContract.address, {'from': anyone}) == Web3.toWei(800, 'ether')
    # _lend_token_holder wraps 800 Lend_token to L_lend_token
    assert L_lend_token.balanceOf(_lend_token_holder, {'from': anyone}) == 0
    CurrencyDaoContract.wrap(Lend_token.address, Web3.toWei(800, 'ether'), {'from': _lend_token_holder, 'gas': 145000})
    # verify allowance, balances of Lend_token and L_lend_token
    assert Lend_token.allowance(_lend_token_holder, CurrencyDaoContract.address, {'from': anyone}) == 0
    assert Lend_token.balanceOf(_lend_token_holder, {'from': anyone}) == Web3.toWei(200, 'ether')
    assert L_lend_token.balanceOf(_lend_token_holder, {'from': anyone}) == Web3.toWei(800, 'ether')


def test_unwrap(accounts, get_ERC20_contract, get_CurrencyDao_contract,
    Deployer, Governor,
    Whale, Lend_token,
    ProtocolDaoContract):
    anyone = accounts[-1]
    # get CurrencyDaoContract
    CurrencyDaoContract = get_CurrencyDao_contract(address=ProtocolDaoContract.daos(PROTOCOL_CONSTANTS['DAO_CURRENCY']))
    # assign one of the accounts as _lend_token_holder
    _lend_token_holder = accounts[5]
    # initialize CurrencyDaoContract
    ProtocolDaoContract.initialize_currency_dao({'from': Deployer})
    ProtocolDaoContract.set_token_support(Lend_token.address, True, {'from': Governor, 'gas': 2000000})
    # _lend_token_holder buys 1000 lend token from a 3rd party exchange
    assert Lend_token.balanceOf(_lend_token_holder, {'from': anyone}) == 0
    Lend_token.transfer(_lend_token_holder, Web3.toWei(1000, 'ether'), {'from': Whale})
    assert Lend_token.balanceOf(_lend_token_holder, {'from': anyone}) == Web3.toWei(1000, 'ether')
    # get L_Lend_token
    L_lend_token = get_ERC20_contract(address=CurrencyDaoContract.token_addresses__l(Lend_token.address, {'from': anyone}))
    # _lend_token_holder authorizes CurrencyDaoContract to spend 500 Lend_token
    Lend_token.approve(CurrencyDaoContract.address, Web3.toWei(800, 'ether'), {'from': _lend_token_holder})
    # _lend_token_holder wraps 800 Lend_token to L_lend_token
    CurrencyDaoContract.wrap(Lend_token.address, Web3.toWei(800, 'ether'), {'from': _lend_token_holder, 'gas': 145000})
    # _lend_token_holder wraps 800 Lend_token to L_lend_token
    CurrencyDaoContract.unwrap(Lend_token.address, Web3.toWei(800, 'ether'), {'from': _lend_token_holder, 'gas': 100000})
    # verify balances of Lend_token and L_lend_token
    assert Lend_token.balanceOf(_lend_token_holder, {'from': anyone}) == Web3.toWei(1000, 'ether')
    assert L_lend_token.balanceOf(_lend_token_holder, {'from': anyone}) == 0
