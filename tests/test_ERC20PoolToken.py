import pytest
from web3 import Web3
from web3.exceptions import (
    ValidationError,
)
from conftest import (
    PROTOCOL_CONSTANTS,
    MAX_UINT256,
    POOL_NAME_REGISTRATION_MIN_STAKE_LST, POOL_NAME_LIONFURY,
    ZERO_ADDRESS, EMPTY_BYTES32,
    INTEREST_POOL_DAO_MIN_MFT_FEE, INTEREST_POOL_DAO_FEE_MULTIPLIER_PER_MFT_COUNT,
    STRIKE_125, H20,
    MAX_LIABILITY_CURENCY_MARKET
)


def test_initial_state(w3,
        Whale, Deployer, Governor,
        LST_token, Lend_token,
        get_ERC20_contract, get_ERC20_Pool_Token_contract, get_MFT_contract,
        get_PoolNameRegistry_contract, get_InterestPool_contract,
        get_CurrencyDao_contract, get_InterestPoolDao_contract,
        ProtocolDao):
    a1, a2, a3 = w3.eth.accounts[1:4]
    # get CurrencyDao
    CurrencyDao = get_CurrencyDao_contract(address=ProtocolDao.daos(PROTOCOL_CONSTANTS['DAO_CURRENCY']))
    # get InterestPoolDao
    InterestPoolDao = get_InterestPoolDao_contract(address=ProtocolDao.daos(PROTOCOL_CONSTANTS['DAO_INTEREST_POOL']))
    # get PoolNameRegistry
    PoolNameRegistry = get_PoolNameRegistry_contract(address=ProtocolDao.registries(PROTOCOL_CONSTANTS['REGISTRY_POOL_NAME']))
    # assign one of the accounts as _pool_owner
    _pool_owner = w3.eth.accounts[6]
    # initialize PoolNameRegistry
    ProtocolDao.initialize_pool_name_registry(Web3.toWei(POOL_NAME_REGISTRATION_MIN_STAKE_LST, 'ether'), transact={'from': Deployer})
    # initialize CurrencyDao
    ProtocolDao.initialize_currency_dao(transact={'from': Deployer})
    # initialize InterestPoolDao
    ProtocolDao.initialize_interest_pool_dao(transact={'from': Deployer})
    # set support for Lend_token
    ProtocolDao.set_token_support(Lend_token.address, True, transact={'from': Governor, 'gas': 2000000})
    # get L_Lend_token
    L_lend_token = get_ERC20_contract(address=CurrencyDao.token_addresses__l(Lend_token.address))
    # get F_Lend_token
    F_lend_token = get_MFT_contract(address=CurrencyDao.token_addresses__f(Lend_token.address))
    # get I_lend_token
    I_lend_token = get_MFT_contract(address=CurrencyDao.token_addresses__i(Lend_token.address))
    # _pool_owner buys 1000 lend token from a 3rd party exchange
    Lend_token.transfer(_pool_owner, Web3.toWei(1000, 'ether'), transact={'from': Whale})
    # _pool_owner authorizes CurrencyDao to spend 800 Lend_token
    Lend_token.approve(CurrencyDao.address, Web3.toWei(800, 'ether'), transact={'from': _pool_owner})
    # _pool_owner wraps 800 Lend_token to L_lend_token
    CurrencyDao.wrap(Lend_token.address, Web3.toWei(800, 'ether'), transact={'from': _pool_owner, 'gas': 145000})
    # _pool_owner buys POOL_NAME_REGISTRATION_MIN_STAKE_LST LST_token from a 3rd party exchange
    LST_token.transfer(_pool_owner, Web3.toWei(POOL_NAME_REGISTRATION_MIN_STAKE_LST, 'ether'), transact={'from': Whale})
    # _pool_owner authorizes CurrencyDao to spend POOL_NAME_REGISTRATION_MIN_STAKE_LST LST_token
    LST_token.approve(CurrencyDao.address, Web3.toWei(POOL_NAME_REGISTRATION_MIN_STAKE_LST, 'ether'), transact={'from': _pool_owner})
    # _pool_owner registers _pool_name POOL_NAME_LIONFURY at the InterestPoolDao
    _pool_name = POOL_NAME_LIONFURY
    InterestPoolDao.register_pool(
        False, Lend_token.address, _pool_name, Web3.toWei(50, 'ether'), 1, 90, transact={'from': _pool_owner, 'gas': 1200000})
    # get InterestPool
    InterestPool = get_InterestPool_contract(address=InterestPoolDao.pools__address_(_pool_name))
    # get Poolshare_token
    test_token = get_ERC20_Pool_Token_contract(address=InterestPool.pool_share_token())
    tx_hash = InterestPool.contribute(Web3.toWei(500, 'ether'), transact={'from': _pool_owner, 'gas': 300000})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    # Check total supply, name, symbol and decimals are correctly set
    assert test_token.totalSupply() == Web3.toWei(25000, 'ether')
    assert test_token.name() == _pool_name
    assert test_token.symbol() == '{0}.RF.{1}'.format(_pool_name, 'DAI')
    assert test_token.decimals() == 18
    # Check several account balances as 0
    assert test_token.balanceOf(_pool_owner) == Web3.toWei(25000, 'ether')
    assert test_token.balanceOf(a2) == 0
    assert test_token.balanceOf(a3) == 0
    # Check several allowances as 0
    assert test_token.allowance(_pool_owner, _pool_owner) == 0
    assert test_token.allowance(_pool_owner, a2) == 0
    assert test_token.allowance(_pool_owner, a3) == 0
    assert test_token.allowance(a2, a3) == 0


def test_mint_and_burn(w3, assert_tx_failed,
        Whale, Deployer, Governor,
        LST_token, Lend_token,
        get_ERC20_contract, get_ERC20_Pool_Token_contract, get_MFT_contract,
        get_PoolNameRegistry_contract, get_InterestPool_contract,
        get_CurrencyDao_contract, get_InterestPoolDao_contract,
        ProtocolDao):
    # get CurrencyDao
    CurrencyDao = get_CurrencyDao_contract(address=ProtocolDao.daos(PROTOCOL_CONSTANTS['DAO_CURRENCY']))
    # get InterestPoolDao
    InterestPoolDao = get_InterestPoolDao_contract(address=ProtocolDao.daos(PROTOCOL_CONSTANTS['DAO_INTEREST_POOL']))
    # get PoolNameRegistry
    PoolNameRegistry = get_PoolNameRegistry_contract(address=ProtocolDao.registries(PROTOCOL_CONSTANTS['REGISTRY_POOL_NAME']))
    # assign one of the accounts as _pool_owner
    _pool_owner = w3.eth.accounts[6]
    # initialize PoolNameRegistry
    ProtocolDao.initialize_pool_name_registry(Web3.toWei(POOL_NAME_REGISTRATION_MIN_STAKE_LST, 'ether'), transact={'from': Deployer})
    # initialize CurrencyDao
    ProtocolDao.initialize_currency_dao(transact={'from': Deployer})
    # initialize InterestPoolDao
    ProtocolDao.initialize_interest_pool_dao(transact={'from': Deployer})
    # set support for Lend_token
    ProtocolDao.set_token_support(Lend_token.address, True, transact={'from': Governor, 'gas': 2000000})
    # get L_Lend_token
    L_lend_token = get_ERC20_contract(address=CurrencyDao.token_addresses__l(Lend_token.address))
    # get F_Lend_token
    F_lend_token = get_MFT_contract(address=CurrencyDao.token_addresses__f(Lend_token.address))
    # get I_lend_token
    I_lend_token = get_MFT_contract(address=CurrencyDao.token_addresses__i(Lend_token.address))
    # _pool_owner buys 1000 lend token from a 3rd party exchange
    Lend_token.transfer(_pool_owner, Web3.toWei(1000, 'ether'), transact={'from': Whale})
    # _pool_owner authorizes CurrencyDao to spend 800 Lend_token
    Lend_token.approve(CurrencyDao.address, Web3.toWei(800, 'ether'), transact={'from': _pool_owner})
    # _pool_owner wraps 800 Lend_token to L_lend_token
    CurrencyDao.wrap(Lend_token.address, Web3.toWei(800, 'ether'), transact={'from': _pool_owner, 'gas': 145000})
    # _pool_owner buys POOL_NAME_REGISTRATION_MIN_STAKE_LST LST_token from a 3rd party exchange
    LST_token.transfer(_pool_owner, Web3.toWei(POOL_NAME_REGISTRATION_MIN_STAKE_LST, 'ether'), transact={'from': Whale})
    # _pool_owner authorizes CurrencyDao to spend POOL_NAME_REGISTRATION_MIN_STAKE_LST LST_token
    LST_token.approve(CurrencyDao.address, Web3.toWei(POOL_NAME_REGISTRATION_MIN_STAKE_LST, 'ether'), transact={'from': _pool_owner})
    # _pool_owner registers _pool_name POOL_NAME_LIONFURY at the InterestPoolDao
    _pool_name = POOL_NAME_LIONFURY
    InterestPoolDao.register_pool(
        False, Lend_token.address, _pool_name, Web3.toWei(50, 'ether'), 1, 90, transact={'from': _pool_owner, 'gas': 1200000})
    # get InterestPool
    InterestPool = get_InterestPool_contract(address=InterestPoolDao.pools__address_(_pool_name))
    # get Poolshare_token
    test_token = get_ERC20_Pool_Token_contract(address=InterestPool.pool_share_token())
    tx_hash = InterestPool.contribute(Web3.toWei(500, 'ether'), transact={'from': _pool_owner, 'gas': 300000})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    assert test_token.balanceOf(_pool_owner) == Web3.toWei(25000, 'ether')
    test_token.burn(Web3.toWei(25000, 'ether'), transact={'from': _pool_owner})
    assert test_token.balanceOf(_pool_owner) == 0
    assert_tx_failed(lambda: test_token.burn(Web3.toWei(2, 'ether'), transact={'from': _pool_owner}))
    assert test_token.balanceOf(_pool_owner) == 0
    # Test scenario were mintes 0 to _lend_token_holder, burns (check balance consistency, false burn)
    tx_hash = CurrencyDao.wrap(Lend_token.address, 0, transact={'from': _pool_owner, 'gas': 145000})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    assert test_token.balanceOf(_pool_owner) == 0
    assert_tx_failed(lambda: test_token.burn(Web3.toWei(2, 'ether'), transact={'from': _pool_owner}))
    # Check that _lend_token_holder cannot mint
    assert_tx_failed(lambda: test_token.mint(_pool_owner, Web3.toWei(2, 'ether'), transact={'from': _pool_owner}))


def test_totalSupply(w3, assert_tx_failed,
        Whale, Deployer, Governor,
        LST_token, Lend_token,
        get_ERC20_contract, get_ERC20_Pool_Token_contract, get_MFT_contract,
        get_PoolNameRegistry_contract, get_InterestPool_contract,
        get_CurrencyDao_contract, get_InterestPoolDao_contract,
        ProtocolDao):
    # Test total supply initially, after mint, between two burns, and after failed burn
    # get CurrencyDao
    CurrencyDao = get_CurrencyDao_contract(address=ProtocolDao.daos(PROTOCOL_CONSTANTS['DAO_CURRENCY']))
    # get InterestPoolDao
    InterestPoolDao = get_InterestPoolDao_contract(address=ProtocolDao.daos(PROTOCOL_CONSTANTS['DAO_INTEREST_POOL']))
    # get PoolNameRegistry
    PoolNameRegistry = get_PoolNameRegistry_contract(address=ProtocolDao.registries(PROTOCOL_CONSTANTS['REGISTRY_POOL_NAME']))
    # assign one of the accounts as _pool_owner
    _pool_owner = w3.eth.accounts[6]
    # initialize PoolNameRegistry
    ProtocolDao.initialize_pool_name_registry(Web3.toWei(POOL_NAME_REGISTRATION_MIN_STAKE_LST, 'ether'), transact={'from': Deployer})
    # initialize CurrencyDao
    ProtocolDao.initialize_currency_dao(transact={'from': Deployer})
    # initialize InterestPoolDao
    ProtocolDao.initialize_interest_pool_dao(transact={'from': Deployer})
    # set support for Lend_token
    ProtocolDao.set_token_support(Lend_token.address, True, transact={'from': Governor, 'gas': 2000000})
    # get L_Lend_token
    L_lend_token = get_ERC20_contract(address=CurrencyDao.token_addresses__l(Lend_token.address))
    # get F_Lend_token
    F_lend_token = get_MFT_contract(address=CurrencyDao.token_addresses__f(Lend_token.address))
    # get I_lend_token
    I_lend_token = get_MFT_contract(address=CurrencyDao.token_addresses__i(Lend_token.address))
    # _pool_owner buys 1000 lend token from a 3rd party exchange
    Lend_token.transfer(_pool_owner, Web3.toWei(1000, 'ether'), transact={'from': Whale})
    # _pool_owner authorizes CurrencyDao to spend 800 Lend_token
    Lend_token.approve(CurrencyDao.address, Web3.toWei(800, 'ether'), transact={'from': _pool_owner})
    # _pool_owner wraps 800 Lend_token to L_lend_token
    CurrencyDao.wrap(Lend_token.address, Web3.toWei(800, 'ether'), transact={'from': _pool_owner, 'gas': 145000})
    # _pool_owner buys POOL_NAME_REGISTRATION_MIN_STAKE_LST LST_token from a 3rd party exchange
    LST_token.transfer(_pool_owner, Web3.toWei(POOL_NAME_REGISTRATION_MIN_STAKE_LST, 'ether'), transact={'from': Whale})
    # _pool_owner authorizes CurrencyDao to spend POOL_NAME_REGISTRATION_MIN_STAKE_LST LST_token
    LST_token.approve(CurrencyDao.address, Web3.toWei(POOL_NAME_REGISTRATION_MIN_STAKE_LST, 'ether'), transact={'from': _pool_owner})
    # _pool_owner registers _pool_name POOL_NAME_LIONFURY at the InterestPoolDao
    _pool_name = POOL_NAME_LIONFURY
    InterestPoolDao.register_pool(
        False, Lend_token.address, _pool_name, Web3.toWei(50, 'ether'), 1, 90, transact={'from': _pool_owner, 'gas': 1200000})
    # get InterestPool
    InterestPool = get_InterestPool_contract(address=InterestPoolDao.pools__address_(_pool_name))
    # get Poolshare_token
    test_token = get_ERC20_Pool_Token_contract(address=InterestPool.pool_share_token())
    assert test_token.totalSupply() == 0
    # _lend_token_holder wraps 2 Lend_token to L_lend_token
    tx_hash = InterestPool.contribute(Web3.toWei(500, 'ether'), transact={'from': _pool_owner, 'gas': 300000})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    assert test_token.totalSupply() == Web3.toWei(25000, 'ether')
    test_token.burn(Web3.toWei(1000, 'ether'), transact={'from': _pool_owner})
    assert test_token.totalSupply() == Web3.toWei(24000, 'ether')
    test_token.burn(Web3.toWei(24000, 'ether'), transact={'from': _pool_owner})
    assert test_token.totalSupply() == 0
    assert_tx_failed(lambda: test_token.burn(Web3.toWei(1, 'ether'), transact={'from': _pool_owner}))
    assert test_token.totalSupply() == 0


def test_transfer(w3, assert_tx_failed,
        Whale, Deployer, Governor,
        LST_token, Lend_token,
        get_ERC20_contract, get_ERC20_Pool_Token_contract, get_MFT_contract,
        get_PoolNameRegistry_contract, get_InterestPool_contract,
        get_CurrencyDao_contract, get_InterestPoolDao_contract,
        ProtocolDao):
    minter, a1, a2 = w3.eth.accounts[0:3]
    # get CurrencyDao
    CurrencyDao = get_CurrencyDao_contract(address=ProtocolDao.daos(PROTOCOL_CONSTANTS['DAO_CURRENCY']))
    # get InterestPoolDao
    InterestPoolDao = get_InterestPoolDao_contract(address=ProtocolDao.daos(PROTOCOL_CONSTANTS['DAO_INTEREST_POOL']))
    # get PoolNameRegistry
    PoolNameRegistry = get_PoolNameRegistry_contract(address=ProtocolDao.registries(PROTOCOL_CONSTANTS['REGISTRY_POOL_NAME']))
    # assign one of the accounts as _pool_owner
    _pool_owner = w3.eth.accounts[6]
    # initialize PoolNameRegistry
    ProtocolDao.initialize_pool_name_registry(Web3.toWei(POOL_NAME_REGISTRATION_MIN_STAKE_LST, 'ether'), transact={'from': Deployer})
    # initialize CurrencyDao
    ProtocolDao.initialize_currency_dao(transact={'from': Deployer})
    # initialize InterestPoolDao
    ProtocolDao.initialize_interest_pool_dao(transact={'from': Deployer})
    # set support for Lend_token
    ProtocolDao.set_token_support(Lend_token.address, True, transact={'from': Governor, 'gas': 2000000})
    # get L_Lend_token
    L_lend_token = get_ERC20_contract(address=CurrencyDao.token_addresses__l(Lend_token.address))
    # get F_Lend_token
    F_lend_token = get_MFT_contract(address=CurrencyDao.token_addresses__f(Lend_token.address))
    # get I_lend_token
    I_lend_token = get_MFT_contract(address=CurrencyDao.token_addresses__i(Lend_token.address))
    # _pool_owner buys 1000 lend token from a 3rd party exchange
    Lend_token.transfer(_pool_owner, Web3.toWei(1000, 'ether'), transact={'from': Whale})
    # _pool_owner authorizes CurrencyDao to spend 800 Lend_token
    Lend_token.approve(CurrencyDao.address, Web3.toWei(800, 'ether'), transact={'from': _pool_owner})
    # _pool_owner wraps 800 Lend_token to L_lend_token
    CurrencyDao.wrap(Lend_token.address, Web3.toWei(800, 'ether'), transact={'from': _pool_owner, 'gas': 145000})
    # _pool_owner buys POOL_NAME_REGISTRATION_MIN_STAKE_LST LST_token from a 3rd party exchange
    LST_token.transfer(_pool_owner, Web3.toWei(POOL_NAME_REGISTRATION_MIN_STAKE_LST, 'ether'), transact={'from': Whale})
    # _pool_owner authorizes CurrencyDao to spend POOL_NAME_REGISTRATION_MIN_STAKE_LST LST_token
    LST_token.approve(CurrencyDao.address, Web3.toWei(POOL_NAME_REGISTRATION_MIN_STAKE_LST, 'ether'), transact={'from': _pool_owner})
    # _pool_owner registers _pool_name POOL_NAME_LIONFURY at the InterestPoolDao
    _pool_name = POOL_NAME_LIONFURY
    InterestPoolDao.register_pool(
        False, Lend_token.address, _pool_name, Web3.toWei(50, 'ether'), 1, 90, transact={'from': _pool_owner, 'gas': 1200000})
    # get InterestPool
    InterestPool = get_InterestPool_contract(address=InterestPoolDao.pools__address_(_pool_name))
    # get Poolshare_token
    test_token = get_ERC20_Pool_Token_contract(address=InterestPool.pool_share_token())
    assert_tx_failed(lambda: test_token.burn(Web3.toWei(1, 'ether'), transact={'from': a2}))
    # _pool_owner wraps 500 Lend_token to L_lend_token
    tx_hash = InterestPool.contribute(Web3.toWei(500, 'ether'), transact={'from': _pool_owner, 'gas': 300000})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    test_token.burn(Web3.toWei(1000, 'ether'), transact={'from': _pool_owner})
    test_token.transfer(a2, Web3.toWei(24000, 'ether'), transact={'from': _pool_owner})
    assert_tx_failed(lambda: test_token.burn(Web3.toWei(1, 'ether'), transact={'from': _pool_owner}))
    test_token.burn(Web3.toWei(24000, 'ether'), transact={'from': a2})
    assert_tx_failed(lambda: test_token.burn(Web3.toWei(24000, 'ether'), transact={'from': a2}))
    # Ensure transfer fails with insufficient balance
    assert_tx_failed(lambda: test_token.transfer(_pool_owner, Web3.toWei(1, 'ether'), transact={'from': a2}))
    # Ensure 0-transfer always succeeds
    test_token.transfer(_pool_owner, 0, transact={'from': a2})


# def test_maxInts(w3, assert_tx_failed,
#         Whale, Deployer, Governor,
#         LST_token, Lend_token,
#         get_ERC20_contract, get_ERC20_Pool_Token_contract, get_MFT_contract,
#         get_PoolNameRegistry_contract, get_InterestPool_contract,
#         get_CurrencyDao_contract, get_InterestPoolDao_contract,
#         ProtocolDao):
#     minter, a1, a2 = w3.eth.accounts[0:3]
#     # get CurrencyDao
#     CurrencyDao = get_CurrencyDao_contract(address=ProtocolDao.daos(PROTOCOL_CONSTANTS['DAO_CURRENCY']))
#     # get InterestPoolDao
#     InterestPoolDao = get_InterestPoolDao_contract(address=ProtocolDao.daos(PROTOCOL_CONSTANTS['DAO_INTEREST_POOL']))
#     # get PoolNameRegistry
#     PoolNameRegistry = get_PoolNameRegistry_contract(address=ProtocolDao.registries(PROTOCOL_CONSTANTS['REGISTRY_POOL_NAME']))
#     # assign one of the accounts as _pool_owner
#     _pool_owner = w3.eth.accounts[6]
#     # initialize PoolNameRegistry
#     ProtocolDao.initialize_pool_name_registry(Web3.toWei(POOL_NAME_REGISTRATION_MIN_STAKE_LST, 'ether'), transact={'from': Deployer})
#     # initialize CurrencyDao
#     ProtocolDao.initialize_currency_dao(transact={'from': Deployer})
#     # initialize InterestPoolDao
#     ProtocolDao.initialize_interest_pool_dao(transact={'from': Deployer})
#     # set support for Lend_token
#     ProtocolDao.set_token_support(Lend_token.address, True, transact={'from': Governor, 'gas': 2000000})
#     # get L_Lend_token
#     L_lend_token = get_ERC20_contract(address=CurrencyDao.token_addresses__l(Lend_token.address))
#     # get F_Lend_token
#     F_lend_token = get_MFT_contract(address=CurrencyDao.token_addresses__f(Lend_token.address))
#     # get I_lend_token
#     I_lend_token = get_MFT_contract(address=CurrencyDao.token_addresses__i(Lend_token.address))
#     # _pool_owner buys 1000 lend token from a 3rd party exchange
#     Lend_token.transfer(_pool_owner, Web3.toWei(1000, 'ether'), transact={'from': Whale})
#     # _pool_owner authorizes CurrencyDao to spend 800 Lend_token
#     Lend_token.approve(CurrencyDao.address, Web3.toWei(800, 'ether'), transact={'from': _pool_owner})
#     # _pool_owner wraps 800 Lend_token to L_lend_token
#     CurrencyDao.wrap(Lend_token.address, Web3.toWei(800, 'ether'), transact={'from': _pool_owner, 'gas': 145000})
#     # _pool_owner buys POOL_NAME_REGISTRATION_MIN_STAKE_LST LST_token from a 3rd party exchange
#     LST_token.transfer(_pool_owner, Web3.toWei(POOL_NAME_REGISTRATION_MIN_STAKE_LST, 'ether'), transact={'from': Whale})
#     # _pool_owner authorizes CurrencyDao to spend POOL_NAME_REGISTRATION_MIN_STAKE_LST LST_token
#     LST_token.approve(CurrencyDao.address, Web3.toWei(POOL_NAME_REGISTRATION_MIN_STAKE_LST, 'ether'), transact={'from': _pool_owner})
#     # _pool_owner registers _pool_name POOL_NAME_LIONFURY at the InterestPoolDao
#     _pool_name = POOL_NAME_LIONFURY
#     InterestPoolDao.register_pool(
#         False, Lend_token.address, _pool_name, Web3.toWei(1, 'ether'), 1, 90, transact={'from': _pool_owner, 'gas': 1200000})
#     # get InterestPool
#     InterestPool = get_InterestPool_contract(address=InterestPoolDao.pools__address_(_pool_name))
#     # get Poolshare_token
#     test_token = get_ERC20_Pool_Token_contract(address=InterestPool.pool_share_token())
#     tx_hash = InterestPool.contribute(MAX_UINT256, transact={'from': _pool_owner, 'gas': 400000})
#     tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
#     print(tx_receipt)
#     assert tx_receipt['status'] == 1
#     # Assert that after obtaining max number of tokens, a1 can transfer those but no more
#     assert test_token.balanceOf(_pool_owner) == MAX_UINT256
#     test_token.transfer(a2, MAX_UINT256, transact={'from': _pool_owner})
#     assert test_token.balanceOf(a2) == MAX_UINT256
#     assert test_token.balanceOf(_pool_owner) == 0
#     # [ next line should never work in EVM ]
#     with pytest.raises(ValidationError):
#         test_token.transfer(_pool_owner, MAX_UINT256 + 1, transact={'from': a2})
#     # Check approve/allowance w max possible token values
#     assert test_token.balanceOf(a2) == MAX_UINT256
#     test_token.approve(_pool_owner, MAX_UINT256, transact={'from': a2})
#     test_token.transferFrom(a2, _pool_owner, MAX_UINT256, transact={'from': _pool_owner})
#     assert test_token.balanceOf(_pool_owner) == MAX_UINT256
#     assert test_token.balanceOf(a2) == 0
#     # Check that max amount can be burned
#     test_token.burn(MAX_UINT256, transact={'from': _pool_owner})
#     assert test_token.balanceOf(_pool_owner) == 0


def test_transferFrom_and_Allowance(w3, assert_tx_failed,
        Whale, Deployer, Governor,
        LST_token, Lend_token,
        get_ERC20_contract, get_ERC20_Pool_Token_contract, get_MFT_contract,
        get_PoolNameRegistry_contract, get_InterestPool_contract,
        get_CurrencyDao_contract, get_InterestPoolDao_contract,
        ProtocolDao):
    minter, a1, a2, a3 = w3.eth.accounts[0:4]
    # get CurrencyDao
    CurrencyDao = get_CurrencyDao_contract(address=ProtocolDao.daos(PROTOCOL_CONSTANTS['DAO_CURRENCY']))
    # get InterestPoolDao
    InterestPoolDao = get_InterestPoolDao_contract(address=ProtocolDao.daos(PROTOCOL_CONSTANTS['DAO_INTEREST_POOL']))
    # get PoolNameRegistry
    PoolNameRegistry = get_PoolNameRegistry_contract(address=ProtocolDao.registries(PROTOCOL_CONSTANTS['REGISTRY_POOL_NAME']))
    # assign one of the accounts as _pool_owner
    _pool_owner = w3.eth.accounts[6]
    # initialize PoolNameRegistry
    ProtocolDao.initialize_pool_name_registry(Web3.toWei(POOL_NAME_REGISTRATION_MIN_STAKE_LST, 'ether'), transact={'from': Deployer})
    # initialize CurrencyDao
    ProtocolDao.initialize_currency_dao(transact={'from': Deployer})
    # initialize InterestPoolDao
    ProtocolDao.initialize_interest_pool_dao(transact={'from': Deployer})
    # set support for Lend_token
    ProtocolDao.set_token_support(Lend_token.address, True, transact={'from': Governor, 'gas': 2000000})
    # get L_Lend_token
    L_lend_token = get_ERC20_contract(address=CurrencyDao.token_addresses__l(Lend_token.address))
    # get F_Lend_token
    F_lend_token = get_MFT_contract(address=CurrencyDao.token_addresses__f(Lend_token.address))
    # get I_lend_token
    I_lend_token = get_MFT_contract(address=CurrencyDao.token_addresses__i(Lend_token.address))
    # _pool_owner buys 1000 lend token from a 3rd party exchange
    Lend_token.transfer(_pool_owner, Web3.toWei(1000, 'ether'), transact={'from': Whale})
    # _pool_owner authorizes CurrencyDao to spend 800 Lend_token
    Lend_token.approve(CurrencyDao.address, Web3.toWei(800, 'ether'), transact={'from': _pool_owner})
    # _pool_owner wraps 800 Lend_token to L_lend_token
    CurrencyDao.wrap(Lend_token.address, Web3.toWei(800, 'ether'), transact={'from': _pool_owner, 'gas': 145000})
    # _pool_owner buys POOL_NAME_REGISTRATION_MIN_STAKE_LST LST_token from a 3rd party exchange
    LST_token.transfer(_pool_owner, Web3.toWei(POOL_NAME_REGISTRATION_MIN_STAKE_LST, 'ether'), transact={'from': Whale})
    # _pool_owner authorizes CurrencyDao to spend POOL_NAME_REGISTRATION_MIN_STAKE_LST LST_token
    LST_token.approve(CurrencyDao.address, Web3.toWei(POOL_NAME_REGISTRATION_MIN_STAKE_LST, 'ether'), transact={'from': _pool_owner})
    # _pool_owner registers _pool_name POOL_NAME_LIONFURY at the InterestPoolDao
    _pool_name = POOL_NAME_LIONFURY
    InterestPoolDao.register_pool(
        False, Lend_token.address, _pool_name, Web3.toWei(50, 'ether'), 1, 90, transact={'from': _pool_owner, 'gas': 1200000})
    # get InterestPool
    InterestPool = get_InterestPool_contract(address=InterestPoolDao.pools__address_(_pool_name))
    # get Poolshare_token
    test_token = get_ERC20_Pool_Token_contract(address=InterestPool.pool_share_token())
    # _pool_owner wraps 500 Lend_token to L_lend_token
    tx_hash = InterestPool.contribute(Web3.toWei(500, 'ether'), transact={'from': _pool_owner, 'gas': 300000})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    assert_tx_failed(lambda: test_token.burn(1, transact={'from': a2}))
    test_token.transfer(a2, 1, transact={'from': _pool_owner})
    test_token.burn(1, transact={'from': _pool_owner})
    # This should fail; no allowance or balance (0 always succeeds)
    assert_tx_failed(lambda: test_token.transferFrom(_pool_owner, a3, 1, transact={'from': a2}))
    test_token.transferFrom(_pool_owner, a3, 0, transact={'from': a2})
    # Correct call to approval should update allowance (but not for reverse pair)
    test_token.approve(a2, 1, transact={'from': _pool_owner})
    assert test_token.allowance(_pool_owner, a2) == 1
    assert test_token.allowance(a2, _pool_owner) == 0
    # transferFrom should succeed when allowed, fail with wrong sender
    assert_tx_failed(lambda: test_token.transferFrom(_pool_owner, a3, 1, transact={'from': a3}))
    assert test_token.balanceOf(a2) == 1
    test_token.approve(_pool_owner, 1, transact={'from': a2})
    test_token.transferFrom(a2, a3, 1, transact={'from': _pool_owner})
    # Allowance should be correctly updated after transferFrom
    assert test_token.allowance(a2, _pool_owner) == 0
    # transferFrom with no funds should fail despite approval
    test_token.approve(_pool_owner, 1, transact={'from': a2})
    assert test_token.allowance(a2, _pool_owner) == 1
    assert_tx_failed(lambda: test_token.transferFrom(a2, a3, 1, transact={'from': _pool_owner}))
    # 0-approve should not change balance or allow transferFrom to change balance
    test_token.transfer(a2, 1, transact={'from': _pool_owner})
    assert test_token.allowance(a2, _pool_owner) == 1
    test_token.approve(_pool_owner, 0, transact={'from': a2})
    assert test_token.allowance(a2, _pool_owner) == 0
    test_token.approve(_pool_owner, 0, transact={'from': a2})
    assert test_token.allowance(a2, _pool_owner) == 0
    assert_tx_failed(lambda: test_token.transferFrom(a2, a3, 1, transact={'from': _pool_owner}))
    # Test that if non-zero approval exists, 0-approval is NOT required to proceed
    # a non-conformant implementation is described in countermeasures at
    # https://docs.google.com/document/d/1YLPtQxZu1UAvO9cZ1O2RPXBbT0mooh4DYKjA_jp-RLM/edit#heading=h.m9fhqynw2xvt
    # the final spec insists on NOT using this behavior
    assert test_token.allowance(a2, _pool_owner) == 0
    test_token.approve(_pool_owner, 1, transact={'from': a2})
    assert test_token.allowance(a2, _pool_owner) == 1
    test_token.approve(_pool_owner, 2, transact={'from': a2})
    assert test_token.allowance(a2, _pool_owner) == 2
    # Check that approving 0 then amount also works
    test_token.approve(_pool_owner, 0, transact={'from': a2})
    assert test_token.allowance(a2, _pool_owner) == 0
    test_token.approve(_pool_owner, 5, transact={'from': a2})
    assert test_token.allowance(a2, _pool_owner) == 5


def test_burnFrom_and_Allowance(w3, assert_tx_failed,
        Whale, Deployer, Governor,
        LST_token, Lend_token,
        get_ERC20_contract, get_ERC20_Pool_Token_contract, get_MFT_contract,
        get_PoolNameRegistry_contract, get_InterestPool_contract,
        get_CurrencyDao_contract, get_InterestPoolDao_contract,
        ProtocolDao):
    minter, a1, a2, a3 = w3.eth.accounts[0:4]
    # get CurrencyDao
    CurrencyDao = get_CurrencyDao_contract(address=ProtocolDao.daos(PROTOCOL_CONSTANTS['DAO_CURRENCY']))
    # get InterestPoolDao
    InterestPoolDao = get_InterestPoolDao_contract(address=ProtocolDao.daos(PROTOCOL_CONSTANTS['DAO_INTEREST_POOL']))
    # get PoolNameRegistry
    PoolNameRegistry = get_PoolNameRegistry_contract(address=ProtocolDao.registries(PROTOCOL_CONSTANTS['REGISTRY_POOL_NAME']))
    # assign one of the accounts as _pool_owner
    _pool_owner = w3.eth.accounts[6]
    # initialize PoolNameRegistry
    ProtocolDao.initialize_pool_name_registry(Web3.toWei(POOL_NAME_REGISTRATION_MIN_STAKE_LST, 'ether'), transact={'from': Deployer})
    # initialize CurrencyDao
    ProtocolDao.initialize_currency_dao(transact={'from': Deployer})
    # initialize InterestPoolDao
    ProtocolDao.initialize_interest_pool_dao(transact={'from': Deployer})
    # set support for Lend_token
    ProtocolDao.set_token_support(Lend_token.address, True, transact={'from': Governor, 'gas': 2000000})
    # get L_Lend_token
    L_lend_token = get_ERC20_contract(address=CurrencyDao.token_addresses__l(Lend_token.address))
    # get F_Lend_token
    F_lend_token = get_MFT_contract(address=CurrencyDao.token_addresses__f(Lend_token.address))
    # get I_lend_token
    I_lend_token = get_MFT_contract(address=CurrencyDao.token_addresses__i(Lend_token.address))
    # _pool_owner buys 1000 lend token from a 3rd party exchange
    Lend_token.transfer(_pool_owner, Web3.toWei(1000, 'ether'), transact={'from': Whale})
    # _pool_owner authorizes CurrencyDao to spend 800 Lend_token
    Lend_token.approve(CurrencyDao.address, Web3.toWei(800, 'ether'), transact={'from': _pool_owner})
    # _pool_owner wraps 800 Lend_token to L_lend_token
    CurrencyDao.wrap(Lend_token.address, Web3.toWei(800, 'ether'), transact={'from': _pool_owner, 'gas': 145000})
    # _pool_owner buys POOL_NAME_REGISTRATION_MIN_STAKE_LST LST_token from a 3rd party exchange
    LST_token.transfer(_pool_owner, Web3.toWei(POOL_NAME_REGISTRATION_MIN_STAKE_LST, 'ether'), transact={'from': Whale})
    # _pool_owner authorizes CurrencyDao to spend POOL_NAME_REGISTRATION_MIN_STAKE_LST LST_token
    LST_token.approve(CurrencyDao.address, Web3.toWei(POOL_NAME_REGISTRATION_MIN_STAKE_LST, 'ether'), transact={'from': _pool_owner})
    # _pool_owner registers _pool_name POOL_NAME_LIONFURY at the InterestPoolDao
    _pool_name = POOL_NAME_LIONFURY
    InterestPoolDao.register_pool(
        False, Lend_token.address, _pool_name, Web3.toWei(50, 'ether'), 1, 90, transact={'from': _pool_owner, 'gas': 1200000})
    # get InterestPool
    InterestPool = get_InterestPool_contract(address=InterestPoolDao.pools__address_(_pool_name))
    # get Poolshare_token
    test_token = get_ERC20_Pool_Token_contract(address=InterestPool.pool_share_token())
    # _pool_owner wraps 500 Lend_token to L_lend_token
    tx_hash = InterestPool.contribute(Web3.toWei(500, 'ether'), transact={'from': _pool_owner, 'gas': 300000})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    assert_tx_failed(lambda: test_token.burn(1, transact={'from': a2}))
    test_token.transfer(a2, 1, transact={'from': _pool_owner})
    test_token.burn(1, transact={'from': _pool_owner})
    # This should fail; no allowance or balance (0 always succeeds)
    assert_tx_failed(lambda: test_token.burnFrom(_pool_owner, 1, transact={'from': a2}))
    test_token.burnFrom(_pool_owner, 0, transact={'from': a2})
    # Correct call to approval should update allowance (but not for reverse pair)
    test_token.approve(a2, 1, transact={'from': _pool_owner})
    assert test_token.allowance(_pool_owner, a2) == 1
    assert test_token.allowance(a2, _pool_owner) == 0
    # transferFrom should succeed when allowed, fail with wrong sender
    assert_tx_failed(lambda: test_token.burnFrom(a2, 1, transact={'from': a3}))
    assert test_token.balanceOf(a2) == 1
    test_token.approve(_pool_owner, 1, transact={'from': a2})
    test_token.burnFrom(a2, 1, transact={'from': _pool_owner})
    # Allowance should be correctly updated after transferFrom
    assert test_token.allowance(a2, _pool_owner) == 0
    # transferFrom with no funds should fail despite approval
    test_token.approve(_pool_owner, 1, transact={'from': a2})
    assert test_token.allowance(a2, _pool_owner) == 1
    assert_tx_failed(lambda: test_token.burnFrom(a2, 1, transact={'from': _pool_owner}))
    # 0-approve should not change balance or allow transferFrom to change balance
    test_token.transfer(a2, 1, transact={'from': _pool_owner})
    assert test_token.allowance(a2, _pool_owner) == 1
    test_token.approve(_pool_owner, 0, transact={'from': a2})
    assert test_token.allowance(a2, _pool_owner) == 0
    test_token.approve(_pool_owner, 0, transact={'from': a2})
    assert test_token.allowance(a2, _pool_owner) == 0
    assert_tx_failed(lambda: test_token.burnFrom(a2, 1, transact={'from': _pool_owner}))
    # Test that if non-zero approval exists, 0-approval is NOT required to proceed
    # a non-conformant implementation is described in countermeasures at
    # https://docs.google.com/document/d/1YLPtQxZu1UAvO9cZ1O2RPXBbT0mooh4DYKjA_jp-RLM/edit#heading=h.m9fhqynw2xvt
    # the final spec insists on NOT using this behavior
    assert test_token.allowance(a2, _pool_owner) == 0
    test_token.approve(_pool_owner, 1, transact={'from': a2})
    assert test_token.allowance(a2, _pool_owner) == 1
    test_token.approve(_pool_owner, 2, transact={'from': a2})
    assert test_token.allowance(a2, _pool_owner) == 2
    # Check that approving 0 then amount also works
    test_token.approve(_pool_owner, 0, transact={'from': a2})
    assert test_token.allowance(a2, _pool_owner) == 0
    test_token.approve(_pool_owner, 5, transact={'from': a2})
    assert test_token.allowance(a2, _pool_owner) == 5
    # Check that burnFrom to ZERO_ADDRESS failed
    assert_tx_failed(lambda: test_token.burnFrom(
        ZERO_ADDRESS, 0, transact={'from': _pool_owner}))


def test_raw_logs(w3, get_log_args, assert_tx_failed,
        Whale, Deployer, Governor,
        LST_token, Lend_token,
        get_ERC20_contract, get_ERC20_Pool_Token_contract, get_MFT_contract,
        get_PoolNameRegistry_contract, get_InterestPool_contract,
        get_CurrencyDao_contract, get_InterestPoolDao_contract,
        ProtocolDao):
    minter, a1, a2, a3 = w3.eth.accounts[0:4]
    # get CurrencyDao
    CurrencyDao = get_CurrencyDao_contract(address=ProtocolDao.daos(PROTOCOL_CONSTANTS['DAO_CURRENCY']))
    # get InterestPoolDao
    InterestPoolDao = get_InterestPoolDao_contract(address=ProtocolDao.daos(PROTOCOL_CONSTANTS['DAO_INTEREST_POOL']))
    # get PoolNameRegistry
    PoolNameRegistry = get_PoolNameRegistry_contract(address=ProtocolDao.registries(PROTOCOL_CONSTANTS['REGISTRY_POOL_NAME']))
    # assign one of the accounts as _pool_owner
    _pool_owner = w3.eth.accounts[6]
    # initialize PoolNameRegistry
    ProtocolDao.initialize_pool_name_registry(Web3.toWei(POOL_NAME_REGISTRATION_MIN_STAKE_LST, 'ether'), transact={'from': Deployer})
    # initialize CurrencyDao
    ProtocolDao.initialize_currency_dao(transact={'from': Deployer})
    # initialize InterestPoolDao
    ProtocolDao.initialize_interest_pool_dao(transact={'from': Deployer})
    # set support for Lend_token
    ProtocolDao.set_token_support(Lend_token.address, True, transact={'from': Governor, 'gas': 2000000})
    # get L_Lend_token
    L_lend_token = get_ERC20_contract(address=CurrencyDao.token_addresses__l(Lend_token.address))
    # get F_Lend_token
    F_lend_token = get_MFT_contract(address=CurrencyDao.token_addresses__f(Lend_token.address))
    # get I_lend_token
    I_lend_token = get_MFT_contract(address=CurrencyDao.token_addresses__i(Lend_token.address))
    # _pool_owner buys 1000 lend token from a 3rd party exchange
    Lend_token.transfer(_pool_owner, Web3.toWei(1000, 'ether'), transact={'from': Whale})
    # _pool_owner authorizes CurrencyDao to spend 800 Lend_token
    Lend_token.approve(CurrencyDao.address, Web3.toWei(800, 'ether'), transact={'from': _pool_owner})
    # _pool_owner wraps 800 Lend_token to L_lend_token
    CurrencyDao.wrap(Lend_token.address, Web3.toWei(800, 'ether'), transact={'from': _pool_owner, 'gas': 145000})
    # _pool_owner buys POOL_NAME_REGISTRATION_MIN_STAKE_LST LST_token from a 3rd party exchange
    LST_token.transfer(_pool_owner, Web3.toWei(POOL_NAME_REGISTRATION_MIN_STAKE_LST, 'ether'), transact={'from': Whale})
    # _pool_owner authorizes CurrencyDao to spend POOL_NAME_REGISTRATION_MIN_STAKE_LST LST_token
    LST_token.approve(CurrencyDao.address, Web3.toWei(POOL_NAME_REGISTRATION_MIN_STAKE_LST, 'ether'), transact={'from': _pool_owner})
    # _pool_owner registers _pool_name POOL_NAME_LIONFURY at the InterestPoolDao
    _pool_name = POOL_NAME_LIONFURY
    InterestPoolDao.register_pool(
        False, Lend_token.address, _pool_name, Web3.toWei(50, 'ether'), 1, 90, transact={'from': _pool_owner, 'gas': 1200000})
    # get InterestPool
    InterestPool = get_InterestPool_contract(address=InterestPoolDao.pools__address_(_pool_name))
    # get Poolshare_token
    test_token = get_ERC20_Pool_Token_contract(address=InterestPool.pool_share_token())
    # _pool_owner wraps 500 Lend_token to L_lend_token
    tx_hash = InterestPool.contribute(Web3.toWei(500, 'ether'), transact={'from': _pool_owner, 'gas': 300000})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    # Check that mint appropriately emits Transfer event
    # args = get_log_args(tx_hash, test_token, 'Transfer')
    # assert args._from == ZERO_ADDRESS
    # assert args._to == _lend_token_holder
    # assert args._value == 2

    # Check that burn appropriately emits Transfer event
    args = get_log_args(test_token.burn(1, transact={'from': _pool_owner}), test_token, 'Transfer')
    assert args._from == _pool_owner
    assert args._to == ZERO_ADDRESS
    assert args._value == 1

    args = get_log_args(test_token.burn(0, transact={'from': _pool_owner}), test_token, 'Transfer')
    assert args._from == _pool_owner
    assert args._to == ZERO_ADDRESS
    assert args._value == 0

    # Check that transfer appropriately emits Transfer event
    args = get_log_args(test_token.transfer(
        a2, 1, transact={'from': _pool_owner}), test_token, 'Transfer')
    assert args._from == _pool_owner
    assert args._to == a2
    assert args._value == 1

    args = get_log_args(test_token.transfer(
        a2, 0, transact={'from': _pool_owner}), test_token, 'Transfer')
    assert args._from == _pool_owner
    assert args._to == a2
    assert args._value == 0

    # Check that approving amount emits events
    args = get_log_args(test_token.approve(_pool_owner, 1, transact={'from': a2}), test_token, 'Approval')
    assert args._owner == a2
    assert args._spender == _pool_owner
    assert args._value == 1

    args = get_log_args(test_token.approve(a2, 0, transact={'from': a3}), test_token, 'Approval')
    assert args._owner == a3
    assert args._spender == a2
    assert args._value == 0

    # Check that transferFrom appropriately emits Transfer event
    args = get_log_args(test_token.transferFrom(
        a2, a3, 1, transact={'from': _pool_owner}), test_token, 'Transfer')
    assert args._from == a2
    assert args._to == a3
    assert args._value == 1

    args = get_log_args(test_token.transferFrom(
        a2, a3, 0, transact={'from': _pool_owner}), test_token, 'Transfer')
    assert args._from == a2
    assert args._to == a3
    assert args._value == 0
