import os

import pytest

from web3 import Web3

from conftest import (
    PROTOCOL_CONSTANTS,
    POOL_NAME_REGISTRATION_MIN_STAKE_LST, POOL_NAME_LIONFURY,
    ZERO_ADDRESS, EMPTY_BYTES32,
    INTEREST_POOL_DAO_MIN_MFT_FEE, INTEREST_POOL_DAO_FEE_MULTIPLIER_PER_MFT_COUNT,
    STRIKE_150, H20
)


def test_initialize(w3, Deployer, get_UnderwriterPoolDao_contract, ProtocolDao):
    UnderwriterPoolDao = get_UnderwriterPoolDao_contract(address=ProtocolDao.daos(PROTOCOL_CONSTANTS['DAO_UNDERWRITER_POOL']))
    assert not UnderwriterPoolDao.initialized()
    tx_hash = ProtocolDao.initialize_underwriter_pool_dao(transact={'from': Deployer})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    assert UnderwriterPoolDao.initialized()


def test_split(w3,
        Whale, Deployer, Governor,
        Lend_token, Borrow_token,
        get_ERC20_contract, get_MFT_contract,
        get_CurrencyDao_contract, get_UnderwriterPoolDao_contract,
        ProtocolDao):
    # get CurrencyDao
    CurrencyDao = get_CurrencyDao_contract(address=ProtocolDao.daos(PROTOCOL_CONSTANTS['DAO_CURRENCY']))
    # get UnderwriterPoolDao
    UnderwriterPoolDao = get_UnderwriterPoolDao_contract(address=ProtocolDao.daos(PROTOCOL_CONSTANTS['DAO_UNDERWRITER_POOL']))
    # assign one of the accounts as _lend_token_holder
    _lend_token_holder = w3.eth.accounts[5]
    # initialize CurrencyDao
    tx_hash = ProtocolDao.initialize_currency_dao(transact={'from': Deployer})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    # initialize UnderwriterPoolDao
    tx_hash = ProtocolDao.initialize_underwriter_pool_dao(transact={'from': Deployer})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    # set support for Lend_token
    tx_hash = ProtocolDao.set_token_support(Lend_token.address, True, transact={'from': Governor, 'gas': 2000000})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    # set support for Borrow_token
    tx_hash = ProtocolDao.set_token_support(Borrow_token.address, True, transact={'from': Governor, 'gas': 2000000})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    # get L_Lend_token
    L_lend_token = get_ERC20_contract(address=CurrencyDao.token_addresses__l(Lend_token.address))
    # get I_Lend_token
    I_lend_token = get_MFT_contract(address=CurrencyDao.token_addresses__i(Lend_token.address))
    # get S_Lend_token
    S_lend_token = get_MFT_contract(address=CurrencyDao.token_addresses__s(Lend_token.address))
    # get U_Lend_token
    U_lend_token = get_MFT_contract(address=CurrencyDao.token_addresses__u(Lend_token.address))
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
    # _lend_token_holder splits 600 L_lend_tokens into 600 I_lend_tokens and 600 S_lend_tokens and 600 U_lend_tokens for H20, Borrow_token, and STRIKE_150
    tx_hash = UnderwriterPoolDao.split(Lend_token.address, H20, Borrow_token.address, STRIKE_150, Web3.toWei(600, 'ether'), transact={'from': _lend_token_holder, 'gas': 1100000})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    assert L_lend_token.balanceOf(_lend_token_holder) == Web3.toWei(200, 'ether')
    _i_id = I_lend_token.id(Lend_token.address, H20, ZERO_ADDRESS, 0)
    _s_id = S_lend_token.id(Lend_token.address, H20, Borrow_token.address, STRIKE_150)
    _u_id = U_lend_token.id(Lend_token.address, H20, Borrow_token.address, STRIKE_150)
    assert I_lend_token.balanceOf(_lend_token_holder, _i_id) == Web3.toWei(600, 'ether')
    assert S_lend_token.balanceOf(_lend_token_holder, _s_id) == Web3.toWei(600, 'ether')
    assert U_lend_token.balanceOf(_lend_token_holder, _u_id) == Web3.toWei(600, 'ether')


def test_fuse(w3,
        Whale, Deployer, Governor,
        Lend_token, Borrow_token,
        get_ERC20_contract, get_MFT_contract,
        get_CurrencyDao_contract, get_UnderwriterPoolDao_contract,
        ProtocolDao):
    # get CurrencyDao
    CurrencyDao = get_CurrencyDao_contract(address=ProtocolDao.daos(PROTOCOL_CONSTANTS['DAO_CURRENCY']))
    # get UnderwriterPoolDao
    UnderwriterPoolDao = get_UnderwriterPoolDao_contract(address=ProtocolDao.daos(PROTOCOL_CONSTANTS['DAO_UNDERWRITER_POOL']))
    # assign one of the accounts as _lend_token_holder
    _lend_token_holder = w3.eth.accounts[5]
    # initialize CurrencyDao
    tx_hash = ProtocolDao.initialize_currency_dao(transact={'from': Deployer})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    # initialize UnderwriterPoolDao
    tx_hash = ProtocolDao.initialize_underwriter_pool_dao(transact={'from': Deployer})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    # set support for Lend_token
    tx_hash = ProtocolDao.set_token_support(Lend_token.address, True, transact={'from': Governor, 'gas': 2000000})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    # set support for Borrow_token
    tx_hash = ProtocolDao.set_token_support(Borrow_token.address, True, transact={'from': Governor, 'gas': 2000000})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    # get L_Lend_token
    L_lend_token = get_ERC20_contract(address=CurrencyDao.token_addresses__l(Lend_token.address))
    # get I_Lend_token
    I_lend_token = get_MFT_contract(address=CurrencyDao.token_addresses__i(Lend_token.address))
    # get S_Lend_token
    S_lend_token = get_MFT_contract(address=CurrencyDao.token_addresses__s(Lend_token.address))
    # get U_Lend_token
    U_lend_token = get_MFT_contract(address=CurrencyDao.token_addresses__u(Lend_token.address))
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
    # _lend_token_holder splits 600 L_lend_tokens into 600 I_lend_tokens and 600 S_lend_tokens and 600 U_lend_tokens for H20, Borrow_token, and STRIKE_150
    tx_hash = UnderwriterPoolDao.split(Lend_token.address, H20, Borrow_token.address, STRIKE_150, Web3.toWei(600, 'ether'), transact={'from': _lend_token_holder, 'gas': 1100000})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    assert L_lend_token.balanceOf(_lend_token_holder) == Web3.toWei(200, 'ether')
    _i_id = I_lend_token.id(Lend_token.address, H20, ZERO_ADDRESS, 0)
    _s_id = S_lend_token.id(Lend_token.address, H20, Borrow_token.address, STRIKE_150)
    _u_id = U_lend_token.id(Lend_token.address, H20, Borrow_token.address, STRIKE_150)
    assert I_lend_token.balanceOf(_lend_token_holder, _i_id) == Web3.toWei(600, 'ether')
    assert S_lend_token.balanceOf(_lend_token_holder, _s_id) == Web3.toWei(600, 'ether')
    assert U_lend_token.balanceOf(_lend_token_holder, _u_id) == Web3.toWei(600, 'ether')
    # _lend_token_holder fuses 400 I_lend_tokens and 400 S_lend_tokens and 400 U_lend_tokens for H20, Borrow_token, and STRIKE_150 into 400 L_lend_tokens
    tx_hash = UnderwriterPoolDao.fuse(Lend_token.address, H20, Borrow_token.address, STRIKE_150, Web3.toWei(400, 'ether'), transact={'from': _lend_token_holder, 'gas': 200000})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    assert L_lend_token.balanceOf(_lend_token_holder) == Web3.toWei(600, 'ether')
    _i_id = I_lend_token.id(Lend_token.address, H20, ZERO_ADDRESS, 0)
    _s_id = S_lend_token.id(Lend_token.address, H20, Borrow_token.address, STRIKE_150)
    _u_id = U_lend_token.id(Lend_token.address, H20, Borrow_token.address, STRIKE_150)
    assert I_lend_token.balanceOf(_lend_token_holder, _i_id) == Web3.toWei(200, 'ether')
    assert S_lend_token.balanceOf(_lend_token_holder, _s_id) == Web3.toWei(200, 'ether')
    assert U_lend_token.balanceOf(_lend_token_holder, _u_id) == Web3.toWei(200, 'ether')


def test_register_pool(w3, get_logs,
        Whale, Deployer, Governor,
        Lend_token, LST_token,
        get_ERC20_contract, get_MFT_contract,
        get_PoolNameRegistry_contract,
        get_CurrencyDao_contract, get_UnderwriterPoolDao_contract,
        get_UnderwriterPool_contract, get_ERC20_Pool_Token_contract,
        ProtocolDao):
        # get CurrencyDao
        CurrencyDao = get_CurrencyDao_contract(address=ProtocolDao.daos(PROTOCOL_CONSTANTS['DAO_CURRENCY']))
        # get UnderwriterPoolDao
        UnderwriterPoolDao = get_UnderwriterPoolDao_contract(address=ProtocolDao.daos(PROTOCOL_CONSTANTS['DAO_UNDERWRITER_POOL']))
        # get PoolNameRegistry
        PoolNameRegistry = get_PoolNameRegistry_contract(address=ProtocolDao.registries(PROTOCOL_CONSTANTS['REGISTRY_POOL_NAME']))
        # assign one of the accounts as _lend_token_holder
        _lend_token_holder = w3.eth.accounts[5]
        # assign one of the accounts as _pool_owner
        _pool_owner = w3.eth.accounts[6]
        # initialize PoolNameRegistry
        tx_hash = ProtocolDao.initialize_pool_name_registry(Web3.toWei(POOL_NAME_REGISTRATION_MIN_STAKE_LST, 'ether'), transact={'from': Deployer})
        tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
        assert tx_receipt['status'] == 1
        # initialize CurrencyDao
        tx_hash = ProtocolDao.initialize_currency_dao(transact={'from': Deployer})
        tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
        assert tx_receipt['status'] == 1
        # initialize UnderwriterPoolDao
        tx_hash = ProtocolDao.initialize_underwriter_pool_dao(transact={'from': Deployer})
        tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
        assert tx_receipt['status'] == 1
        # set support for Lend_token
        tx_hash = ProtocolDao.set_token_support(Lend_token.address, True, transact={'from': Governor, 'gas': 2000000})
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
        # _pool_owner registers _pool_name POOL_NAME_LIONFURY
        _pool_name = POOL_NAME_LIONFURY
        assert UnderwriterPoolDao.next_pool_id() == 0
        assert UnderwriterPoolDao.pools__name(_pool_name) in (None, "")
        tx_hash = UnderwriterPoolDao.register_pool(
            False, Lend_token.address, _pool_name, Web3.toWei(50, 'ether'), 1, 1, 90, transact={'from': _pool_owner, 'gas': 1200000})
        tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
        assert tx_receipt['status'] == 1
        assert UnderwriterPoolDao.next_pool_id() == 1
        assert UnderwriterPoolDao.pools__name(_pool_name) == _pool_name
        assert UnderwriterPoolDao.pools__currency(_pool_name) == Lend_token.address
        assert UnderwriterPoolDao.pools__operator(_pool_name) == _pool_owner
        assert UnderwriterPoolDao.pools__id(_pool_name) == 0
        # verify logs
        logs = get_logs(tx_hash, UnderwriterPoolDao, "PoolRegistered")
        assert logs[0].args._operator == _pool_owner
        assert logs[0].args._currency == Lend_token.address
        assert logs[0].args.address_ == UnderwriterPoolDao.pools__address_(_pool_name)
        # get UnderwriterPool
        UnderwriterPool = get_UnderwriterPool_contract(address=UnderwriterPoolDao.pools__address_(_pool_name))
        assert UnderwriterPool.initialized()
        assert UnderwriterPool.owner() == _pool_owner
        assert UnderwriterPool.protocol_dao() == ProtocolDao.address
        assert UnderwriterPool.name() == _pool_name
        assert UnderwriterPool.initial_exchange_rate() == Web3.toWei(50, 'ether')
        assert UnderwriterPool.currency() == Lend_token.address
        assert UnderwriterPool.fee_percentage_per_i_token() == 1
        assert UnderwriterPool.fee_percentage_per_s_token() == 1
        assert UnderwriterPool.mft_expiry_limit_days() == 90
        assert not UnderwriterPool.pool_share_token() in (None, ZERO_ADDRESS)
        # get UnderwriterPoolToken
        UnderwriterPoolToken = get_ERC20_Pool_Token_contract(address=UnderwriterPool.pool_share_token())
        assert UnderwriterPoolToken.name() == _pool_name
        assert UnderwriterPoolToken.symbol() == "{0}.RU.{1}".format(_pool_name, Lend_token.symbol())


def test_register_mft_support(w3, get_logs,
        Whale, Deployer, Governor,
        Lend_token, Borrow_token, LST_token,
        get_ERC20_contract, get_MFT_contract,
        get_PoolNameRegistry_contract,
        get_CurrencyDao_contract, get_UnderwriterPoolDao_contract,
        get_MarketDao_contract,
        get_UnderwriterPool_contract,
        ProtocolDao):
        # get CurrencyDao
        CurrencyDao = get_CurrencyDao_contract(address=ProtocolDao.daos(PROTOCOL_CONSTANTS['DAO_CURRENCY']))
        # get UnderwriterPoolDao
        UnderwriterPoolDao = get_UnderwriterPoolDao_contract(address=ProtocolDao.daos(PROTOCOL_CONSTANTS['DAO_UNDERWRITER_POOL']))
        # get MarketDao
        MarketDao = get_MarketDao_contract(address=ProtocolDao.daos(PROTOCOL_CONSTANTS['DAO_MARKET']))
        # get PoolNameRegistry
        PoolNameRegistry = get_PoolNameRegistry_contract(address=ProtocolDao.registries(PROTOCOL_CONSTANTS['REGISTRY_POOL_NAME']))
        # assign one of the accounts as _lend_token_holder
        _lend_token_holder = w3.eth.accounts[5]
        # assign one of the accounts as _pool_owner
        _pool_owner = w3.eth.accounts[6]
        # initialize PoolNameRegistry
        tx_hash = ProtocolDao.initialize_pool_name_registry(Web3.toWei(POOL_NAME_REGISTRATION_MIN_STAKE_LST, 'ether'), transact={'from': Deployer})
        tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
        assert tx_receipt['status'] == 1
        # initialize CurrencyDao
        tx_hash = ProtocolDao.initialize_currency_dao(transact={'from': Deployer})
        tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
        assert tx_receipt['status'] == 1
        # initialize UnderwriterPoolDao
        tx_hash = ProtocolDao.initialize_underwriter_pool_dao(transact={'from': Deployer})
        tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
        assert tx_receipt['status'] == 1
        # initialize MarketDao
        tx_hash = ProtocolDao.initialize_market_dao(transact={'from': Deployer})
        tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
        assert tx_receipt['status'] == 1
        # initialize ShieldPayoutDao
        tx_hash = ProtocolDao.initialize_shield_payout_dao(transact={'from': Deployer})
        tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
        assert tx_receipt['status'] == 1
        # set support for Lend_token
        tx_hash = ProtocolDao.set_token_support(Lend_token.address, True, transact={'from': Governor, 'gas': 2000000})
        tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
        assert tx_receipt['status'] == 1
        # get I_Lend_token
        I_lend_token = get_MFT_contract(address=CurrencyDao.token_addresses__i(Lend_token.address))
        # get S_Lend_token
        S_lend_token = get_MFT_contract(address=CurrencyDao.token_addresses__s(Lend_token.address))
        # get U_Lend_token
        U_lend_token = get_MFT_contract(address=CurrencyDao.token_addresses__u(Lend_token.address))
        # set support for Borrow_token
        tx_hash = ProtocolDao.set_token_support(Borrow_token.address, True, transact={'from': Governor, 'gas': 2000000})
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
        # _pool_owner registers _pool_name POOL_NAME_LIONFURY
        _pool_name = POOL_NAME_LIONFURY
        tx_hash = UnderwriterPoolDao.register_pool(
            False, Lend_token.address, _pool_name, Web3.toWei(50, 'ether'), 1, 1, 90, transact={'from': _pool_owner, 'gas': 1200000})
        tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
        assert tx_receipt['status'] == 1
        assert UnderwriterPoolDao.pools__name(_pool_name) == _pool_name
        # get UnderwriterPool
        UnderwriterPool = get_UnderwriterPool_contract(address=UnderwriterPoolDao.pools__address_(_pool_name))
        tx_hash = ProtocolDao.set_minimum_mft_fee(
            PROTOCOL_CONSTANTS['DAO_UNDERWRITER_POOL'],
            Web3.toWei(INTEREST_POOL_DAO_MIN_MFT_FEE, 'ether'),
            transact={'from': Governor})
        tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
        assert tx_receipt['status'] == 1
        # set MFT multiplier
        tx_hash = ProtocolDao.set_fee_multiplier_per_mft_count(
            PROTOCOL_CONSTANTS['DAO_UNDERWRITER_POOL'], Web3.toWei(0, 'ether'),
            Web3.toWei(INTEREST_POOL_DAO_FEE_MULTIPLIER_PER_MFT_COUNT, 'ether'),
            transact={'from': Governor, 'gas': 75000})
        tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
        assert tx_receipt['status'] == 1
        # set support for expiry H20
        tx_hash = ProtocolDao.set_expiry_support(H20, "H20", True, transact={'from': Governor})
        tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
        assert tx_receipt['status'] == 1
        # _pool_owner buys INTEREST_POOL_DAO_MIN_MFT_FEE LST_token from a 3rd party exchange
        tx_hash = LST_token.transfer(_pool_owner, Web3.toWei(INTEREST_POOL_DAO_MIN_MFT_FEE, 'ether'), transact={'from': Whale})
        tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
        assert tx_receipt['status'] == 1
        assert LST_token.balanceOf(_pool_owner) == Web3.toWei(INTEREST_POOL_DAO_MIN_MFT_FEE, 'ether')
        # _pool_owner authorizes CurrencyDao to spend INTEREST_POOL_DAO_MIN_MFT_FEE LST_token
        tx_hash = LST_token.approve(CurrencyDao.address, Web3.toWei(INTEREST_POOL_DAO_MIN_MFT_FEE, 'ether'), transact={'from': _pool_owner})
        tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
        assert tx_receipt['status'] == 1
        assert LST_token.allowance(_pool_owner, CurrencyDao.address) == Web3.toWei(INTEREST_POOL_DAO_MIN_MFT_FEE, 'ether')
        # set support for MFT H20
        assert MarketDao.expiry_markets__expiry(H20) in (None, 0)
        _loan_market_hash = MarketDao.loan_market_hash(Lend_token.address, H20, Borrow_token.address)
        assert MarketDao.loan_markets__hash(_loan_market_hash) in (None, EMPTY_BYTES32)
        _shield_market_hash = MarketDao.shield_market_hash(Lend_token.address, H20, Borrow_token.address, STRIKE_150)
        assert MarketDao.shield_markets__hash(_shield_market_hash) in (None, EMPTY_BYTES32)
        assert UnderwriterPoolDao.pools__mft_count(_pool_name) == 0
        assert UnderwriterPoolDao.pools__LST_staked(_pool_name) == 0
        assert UnderwriterPoolDao.LST_stake_value(_pool_name) == Web3.toWei(INTEREST_POOL_DAO_MIN_MFT_FEE, 'ether')
        tx_hash = UnderwriterPool.support_mft(H20, Borrow_token.address, STRIKE_150,
            Web3.toWei(0.025, 'ether'), Web3.toWei(0.05, 'ether'), transact={'from': _pool_owner, 'gas': 2500000})
        tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
        assert tx_receipt['status'] == 1
        assert UnderwriterPoolDao.pools__mft_count(_pool_name) == 1
        assert UnderwriterPoolDao.pools__LST_staked(_pool_name) == Web3.toWei(INTEREST_POOL_DAO_MIN_MFT_FEE, 'ether')
        assert MarketDao.expiry_markets__expiry(H20) == H20
        assert MarketDao.loan_markets__hash(_loan_market_hash) == _loan_market_hash
        assert MarketDao.shield_markets__hash(_shield_market_hash) == _shield_market_hash
        # verify logs
        logs = get_logs(tx_hash, UnderwriterPoolDao, "MFTSupportRegistered")
        assert Web3.toText(logs[0].args._name) == "Lion Fury\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
        assert logs[0].args._pool == UnderwriterPoolDao.pools__address_(_pool_name)
        assert logs[0].args._currency == Lend_token.address
        assert logs[0].args._expiry == H20
        assert logs[0].args._underlying == Borrow_token.address
        assert logs[0].args._strike_price == STRIKE_150
        assert logs[0].args._operator == _pool_owner
        logs = get_logs(tx_hash, I_lend_token, "TransferSingle")
        assert logs[0].args._operator == UnderwriterPoolDao.address
        assert logs[0].args._from == ZERO_ADDRESS
        assert logs[0].args._to == UnderwriterPoolDao.address
        assert logs[0].args._id == I_lend_token.nonce()
        assert logs[0].args._value == 0
        logs = get_logs(tx_hash, S_lend_token, "TransferSingle")
        assert logs[0].args._operator == UnderwriterPoolDao.address
        assert logs[0].args._from == ZERO_ADDRESS
        assert logs[0].args._to == UnderwriterPoolDao.address
        assert logs[0].args._id == S_lend_token.nonce()
        assert logs[0].args._value == 0
        logs = get_logs(tx_hash, U_lend_token, "TransferSingle")
        assert logs[0].args._operator == UnderwriterPoolDao.address
        assert logs[0].args._from == ZERO_ADDRESS
        assert logs[0].args._to == UnderwriterPoolDao.address
        assert logs[0].args._id == U_lend_token.nonce()
        assert logs[0].args._value == 0
        logs = get_logs(tx_hash, LST_token, "Transfer")
        assert logs[0].args._from == _pool_owner
        assert logs[0].args._to == UnderwriterPoolDao.address
        assert logs[0].args._value == Web3.toWei(INTEREST_POOL_DAO_MIN_MFT_FEE, 'ether')
