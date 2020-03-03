import pytest

from brownie.exceptions import ContractNotFound

from web3 import Web3

from conftest import (
    PROTOCOL_CONSTANTS,
    POOL_NAME_REGISTRATION_MIN_STAKE_LST,
    ZERO_ADDRESS
)


def test_initialize(accounts, assert_tx_failed, get_ERC20_contract, get_CurrencyPool_contract, get_CurrencyDao_contract,
    Deployer, Governor,
    Whale, LST_token, Lend_token,
    ProtocolDaoContract):
    anyone = accounts[-1]
    # get CurrencyDaoContract
    CurrencyDaoContract = get_CurrencyDao_contract(address=ProtocolDaoContract.daos(PROTOCOL_CONSTANTS['DAO_CURRENCY']))
    # assign one of the accounts as _lend_token_holder
    _lend_token_holder = accounts[5]
    # initialize CurrencyDaoContract
    ProtocolDaoContract.initialize_currency_dao({'from': Deployer})
    # Governor sets support for Lend_token
    ProtocolDaoContract.set_token_support(Lend_token.address, True, {'from': Governor, 'gas': 2000000})
    # get TokenPoolContract
    TokenPoolContract = get_CurrencyPool_contract(address=CurrencyDaoContract.pools__address_(CurrencyDaoContract.pool_hash(Lend_token.address, {'from': anyone}), {'from': anyone}))
    # verify details from token pool contract
    assert TokenPoolContract.initialized({'from': anyone})
    assert TokenPoolContract.owner({'from': anyone}) == CurrencyDaoContract.address
    assert TokenPoolContract.token({'from': anyone}) == Lend_token.address
    # Tx fails when trying to initialize TokenPoolContract
    assert_tx_failed(lambda: TokenPoolContract.initialize(Lend_token.address, {'from': anyone}))


def test_borrowable_amount(accounts, get_ERC20_contract, get_CurrencyPool_contract, get_CurrencyDao_contract,
    Deployer, Governor,
    Whale, LST_token, Lend_token,
    ProtocolDaoContract):
    anyone = accounts[-1]
    # get CurrencyDaoContract
    CurrencyDaoContract = get_CurrencyDao_contract(address=ProtocolDaoContract.daos(PROTOCOL_CONSTANTS['DAO_CURRENCY']))
    # assign one of the accounts as _lend_token_holder
    _lend_token_holder = accounts[5]
    # initialize CurrencyDaoContract
    ProtocolDaoContract.initialize_currency_dao({'from': Deployer})
    # Governor sets support for Lend_token
    ProtocolDaoContract.set_token_support(Lend_token.address, True, {'from': Governor, 'gas': 2000000})
    # get TokenPoolContract
    TokenPoolContract = get_CurrencyPool_contract(address=CurrencyDaoContract.pools__address_(CurrencyDaoContract.pool_hash(Lend_token.address, {'from': anyone}), {'from': anyone}))
    # _lend_token_holder buys 1000 lend token from a 3rd party exchange
    Lend_token.transfer(_lend_token_holder, Web3.toWei(1000, 'ether'), {'from': Whale})
    # get L_Lend_token
    L_lend_token = get_ERC20_contract(address=CurrencyDaoContract.token_addresses__l(Lend_token.address, {'from': anyone}))
    # _lend_token_holder authorizes CurrencyDaoContract to spend 500 Lend_token
    Lend_token.approve(CurrencyDaoContract.address, Web3.toWei(1000, 'ether'), {'from': _lend_token_holder})
    # _lend_token_holder wraps 1000 Lend_token to L_lend_token
    CurrencyDaoContract.wrap(Lend_token.address, Web3.toWei(1000, 'ether'), {'from': _lend_token_holder, 'gas': 145000})
    assert TokenPoolContract.borrowable_amount({'from': anyone}) == Web3.toWei(1000, 'ether')
    # _lend_token_holder unwraps 500 L_lend_token to Lend_token
    CurrencyDaoContract.unwrap(Lend_token.address, Web3.toWei(500, 'ether'), {'from': _lend_token_holder, 'gas': 100000})
    assert TokenPoolContract.borrowable_amount({'from': anyone}) == Web3.toWei(500, 'ether')
    # Governor withdraws support for Lend_token
    ProtocolDaoContract.set_token_support(Lend_token.address, False, {'from': Governor, 'gas': 2000000})
    with pytest.raises(ContractNotFound):
        assert TokenPoolContract.borrowable_amount({'from': anyone}) == 0


def test_release(accounts, assert_tx_failed, get_ERC20_contract, get_CurrencyPool_contract, get_CurrencyDao_contract,
    Deployer, Governor,
    Whale, LST_token, Lend_token,
    ProtocolDaoContract):
    anyone = accounts[-1]
    # get CurrencyDaoContract
    CurrencyDaoContract = get_CurrencyDao_contract(address=ProtocolDaoContract.daos(PROTOCOL_CONSTANTS['DAO_CURRENCY']))
    # assign one of the accounts as _lend_token_holder
    _lend_token_holder = accounts[5]
    # initialize CurrencyDaoContract
    ProtocolDaoContract.initialize_currency_dao({'from': Deployer})
    # Governor sets support for Lend_token
    ProtocolDaoContract.set_token_support(Lend_token.address, True, {'from': Governor, 'gas': 2000000})
    # get TokenPoolContract
    TokenPoolContract = get_CurrencyPool_contract(address=CurrencyDaoContract.pools__address_(CurrencyDaoContract.pool_hash(Lend_token.address, {'from': anyone}), {'from': anyone}))
    # _lend_token_holder buys 1000 lend token from a 3rd party exchange
    Lend_token.transfer(_lend_token_holder, Web3.toWei(1000, 'ether'), {'from': Whale})
    # get L_Lend_token
    L_lend_token = get_ERC20_contract(address=CurrencyDaoContract.token_addresses__l(Lend_token.address, {'from': anyone}))
    # _lend_token_holder authorizes CurrencyDaoContract to spend 500 Lend_token
    Lend_token.approve(CurrencyDaoContract.address, Web3.toWei(1000, 'ether'), {'from': _lend_token_holder})
    # _lend_token_holder wraps 800 Lend_token to L_lend_token
    CurrencyDaoContract.wrap(Lend_token.address, Web3.toWei(1000, 'ether'), {'from': _lend_token_holder, 'gas': 145000})
    # Tx fails when TokenPoolContract.release() is called by non-CurrencyDaoContract
    for account in accounts:
        assert_tx_failed(lambda: TokenPoolContract.release(account, Web3.toWei(1000, 'ether'), {'from': account}))
    # Tx fails when TokenPoolContract has to release() 0 tokens
    assert_tx_failed(lambda: CurrencyDaoContract.unwrap(Lend_token.address, 0, {'from': _lend_token_holder, 'gas': 100000}))
    # _lend_token_holder unwraps 800 L_lend_token to Lend_token
    CurrencyDaoContract.unwrap(Lend_token.address, Web3.toWei(1000, 'ether'), {'from': _lend_token_holder, 'gas': 100000})


def test_destroy(accounts, assert_tx_failed, get_ERC20_contract, get_CurrencyPool_contract, get_CurrencyDao_contract,
    Deployer, Governor,
    Whale, LST_token, Lend_token,
    ProtocolDaoContract):
    anyone = accounts[-1]
    # get CurrencyDaoContract
    CurrencyDaoContract = get_CurrencyDao_contract(address=ProtocolDaoContract.daos(PROTOCOL_CONSTANTS['DAO_CURRENCY']))
    # assign one of the accounts as _lend_token_holder
    _lend_token_holder = accounts[5]
    # initialize CurrencyDaoContract
    ProtocolDaoContract.initialize_currency_dao({'from': Deployer})
    # Governor registers support for Lend_token
    ProtocolDaoContract.set_token_support(Lend_token.address, True, {'from': Governor, 'gas': 2000000})
    # get TokenPoolContract
    TokenPoolContract = get_CurrencyPool_contract(address=CurrencyDaoContract.pools__address_(CurrencyDaoContract.pool_hash(Lend_token.address, {'from': anyone}), {'from': anyone}))
    # Tx fails when TokenPoolContract.destroy() is called by non-CurrencyDaoContract
    for account in accounts:
        assert_tx_failed(lambda: TokenPoolContract.destroy({'from': account}))
    # Governor withdraws support for Lend_token
    ProtocolDaoContract.set_token_support(Lend_token.address, False, {'from': Governor, 'gas': 2000000})
