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


def test_initialize(accounts, Deployer, get_UnderwriterPoolDao_contract, ProtocolDaoContract):
    anyone = accounts[-1]
    UnderwriterPoolDaoContract = get_UnderwriterPoolDao_contract(address=ProtocolDaoContract.daos(PROTOCOL_CONSTANTS['DAO_UNDERWRITER_POOL']))
    assert not UnderwriterPoolDaoContract.initialized({'from': anyone})
    ProtocolDaoContract.initialize_underwriter_pool_dao({'from': Deployer})
    assert UnderwriterPoolDaoContract.initialized({'from': anyone})


def test_pause_and_unpause(accounts, Deployer, EscapeHatchManager, get_UnderwriterPoolDao_contract, ProtocolDaoContract):
    anyone = accounts[-1]
    UnderwriterPoolDaoContract = get_UnderwriterPoolDao_contract(address=ProtocolDaoContract.daos(PROTOCOL_CONSTANTS['DAO_UNDERWRITER_POOL']))
    ProtocolDaoContract.initialize_underwriter_pool_dao({'from': Deployer})
    assert not UnderwriterPoolDaoContract.paused({'from': anyone})
    ProtocolDaoContract.toggle_dao_pause(PROTOCOL_CONSTANTS['DAO_UNDERWRITER_POOL'], True, {'from': EscapeHatchManager})
    assert UnderwriterPoolDaoContract.paused({'from': anyone})
    ProtocolDaoContract.toggle_dao_pause(PROTOCOL_CONSTANTS['DAO_UNDERWRITER_POOL'], False, {'from': EscapeHatchManager})
    assert not UnderwriterPoolDaoContract.paused({'from': anyone})


def test_pause_failed_when_paused(accounts, assert_tx_failed, Deployer, EscapeHatchManager, get_UnderwriterPoolDao_contract, ProtocolDaoContract):
    anyone = accounts[-1]
    UnderwriterPoolDaoContract = get_UnderwriterPoolDao_contract(address=ProtocolDaoContract.daos(PROTOCOL_CONSTANTS['DAO_UNDERWRITER_POOL']))
    ProtocolDaoContract.initialize_underwriter_pool_dao({'from': Deployer})
    ProtocolDaoContract.toggle_dao_pause(PROTOCOL_CONSTANTS['DAO_UNDERWRITER_POOL'], True, {'from': EscapeHatchManager})
    assert_tx_failed(lambda: ProtocolDaoContract.toggle_dao_pause(PROTOCOL_CONSTANTS['DAO_UNDERWRITER_POOL'], True, {'from': EscapeHatchManager}))


def test_pause_failed_when_uninitialized(accounts, assert_tx_failed, Deployer, EscapeHatchManager, get_UnderwriterPoolDao_contract, ProtocolDaoContract):
    anyone = accounts[-1]
    UnderwriterPoolDaoContract = get_UnderwriterPoolDao_contract(address=ProtocolDaoContract.daos(PROTOCOL_CONSTANTS['DAO_UNDERWRITER_POOL']))
    assert_tx_failed(lambda: ProtocolDaoContract.toggle_dao_pause(PROTOCOL_CONSTANTS['DAO_UNDERWRITER_POOL'], True, {'from': EscapeHatchManager}))


def test_pause_failed_when_called_by_non_protocol_dao(accounts, assert_tx_failed, Deployer, EscapeHatchManager, get_UnderwriterPoolDao_contract, ProtocolDaoContract):
    anyone = accounts[-1]
    UnderwriterPoolDaoContract = get_UnderwriterPoolDao_contract(address=ProtocolDaoContract.daos(PROTOCOL_CONSTANTS['DAO_UNDERWRITER_POOL']))
    ProtocolDaoContract.initialize_underwriter_pool_dao({'from': Deployer})
    # Tx failed
    for account in accounts:
        assert_tx_failed(lambda: UnderwriterPoolDaoContract.pause({'from': account}))


def test_unpause_failed_when_unpaused(accounts, assert_tx_failed, Deployer, EscapeHatchManager, get_UnderwriterPoolDao_contract, ProtocolDaoContract):
    anyone = accounts[-1]
    UnderwriterPoolDaoContract = get_UnderwriterPoolDao_contract(address=ProtocolDaoContract.daos(PROTOCOL_CONSTANTS['DAO_UNDERWRITER_POOL']))
    ProtocolDaoContract.initialize_underwriter_pool_dao({'from': Deployer})
    assert_tx_failed(lambda: ProtocolDaoContract.toggle_dao_pause(PROTOCOL_CONSTANTS['DAO_UNDERWRITER_POOL'], False, {'from': EscapeHatchManager}))


def test_unpause_failed_when_uninitialized(accounts, assert_tx_failed, Deployer, EscapeHatchManager, get_UnderwriterPoolDao_contract, ProtocolDaoContract):
    anyone = accounts[-1]
    UnderwriterPoolDaoContract = get_UnderwriterPoolDao_contract(address=ProtocolDaoContract.daos(PROTOCOL_CONSTANTS['DAO_UNDERWRITER_POOL']))
    assert_tx_failed(lambda: ProtocolDaoContract.toggle_dao_pause(PROTOCOL_CONSTANTS['DAO_UNDERWRITER_POOL'], False, {'from': EscapeHatchManager}))


def test_unpause_failed_when_called_by_non_protocol_dao(accounts, assert_tx_failed, Deployer, EscapeHatchManager, get_UnderwriterPoolDao_contract, ProtocolDaoContract):
    anyone = accounts[-1]
    UnderwriterPoolDaoContract = get_UnderwriterPoolDao_contract(address=ProtocolDaoContract.daos(PROTOCOL_CONSTANTS['DAO_UNDERWRITER_POOL']))
    ProtocolDaoContract.initialize_underwriter_pool_dao({'from': Deployer})
    # Tx failed
    for account in accounts:
        assert_tx_failed(lambda: UnderwriterPoolDaoContract.unpause({'from': account}))


def test_split(accounts, assert_tx_failed,
        Whale, Deployer, EscapeHatchManager, Governor,
        Lend_token, Borrow_token,
        get_ERC20_contract, get_MFT_contract,
        get_CurrencyDao_contract, get_UnderwriterPoolDao_contract,
        ProtocolDaoContract):
    anyone = accounts[-1]
    # get CurrencyDao
    CurrencyDao = get_CurrencyDao_contract(address=ProtocolDaoContract.daos(PROTOCOL_CONSTANTS['DAO_CURRENCY']))
    # get UnderwriterPoolDaoContract
    UnderwriterPoolDaoContract = get_UnderwriterPoolDao_contract(address=ProtocolDaoContract.daos(PROTOCOL_CONSTANTS['DAO_UNDERWRITER_POOL']))
    # assign one of the accounts as _lend_token_holder
    _lend_token_holder = accounts[5]
    # Tx fails when calling split() and UnderwriterPoolDaoContract is not initialized
    assert_tx_failed(lambda: UnderwriterPoolDaoContract.split(Lend_token.address, H20, Borrow_token.address, STRIKE_150, Web3.toWei(600, 'ether'), {'from': _lend_token_holder, 'gas': 145000}))
    # initialize CurrencyDao
    ProtocolDaoContract.initialize_currency_dao({'from': Deployer})
    # initialize UnderwriterPoolDaoContract
    ProtocolDaoContract.initialize_underwriter_pool_dao({'from': Deployer})
    # Tx fails when calling split() and UnderwriterPoolDaoContract is not initialized
    assert_tx_failed(lambda: UnderwriterPoolDaoContract.split(Lend_token.address, H20, Borrow_token.address, STRIKE_150, Web3.toWei(600, 'ether'), {'from': _lend_token_holder, 'gas': 145000}))
    # set support for Lend_token
    ProtocolDaoContract.set_token_support(Lend_token.address, True, {'from': Governor, 'gas': 2000000})
    # Tx fails when calling split() and UnderwriterPoolDaoContract is not initialized
    assert_tx_failed(lambda: UnderwriterPoolDaoContract.split(Lend_token.address, H20, Borrow_token.address, STRIKE_150, Web3.toWei(600, 'ether'), {'from': _lend_token_holder, 'gas': 145000}))
    # set support for Borrow_token
    ProtocolDaoContract.set_token_support(Borrow_token.address, True, {'from': Governor, 'gas': 2000000})
    # get L_Lend_token
    L_lend_token = get_ERC20_contract(address=CurrencyDao.token_addresses__l(Lend_token.address, {'from': anyone}))
    # get I_Lend_token
    I_lend_token = get_MFT_contract(address=CurrencyDao.token_addresses__i(Lend_token.address, {'from': anyone}))
    # get S_Lend_token
    S_lend_token = get_MFT_contract(address=CurrencyDao.token_addresses__s(Lend_token.address, {'from': anyone}))
    # get U_Lend_token
    U_lend_token = get_MFT_contract(address=CurrencyDao.token_addresses__u(Lend_token.address, {'from': anyone}))
    # _lend_token_holder buys 1000 lend token from a 3rd party exchange
    Lend_token.transfer(_lend_token_holder, Web3.toWei(1000, 'ether'), {'from': Whale})
    assert Lend_token.balanceOf(_lend_token_holder) == Web3.toWei(1000, 'ether')
    # _lend_token_holder authorizes CurrencyDao to spend 800 Lend_token
    Lend_token.approve(CurrencyDao.address, Web3.toWei(800, 'ether'), {'from': _lend_token_holder})
    assert Lend_token.allowance(_lend_token_holder, CurrencyDao.address, {'from': anyone}) == Web3.toWei(800, 'ether')
    # _lend_token_holder wraps 800 Lend_token to L_lend_token
    assert L_lend_token.balanceOf(_lend_token_holder, {'from': anyone}) == 0
    CurrencyDao.wrap(Lend_token.address, Web3.toWei(800, 'ether'), {'from': _lend_token_holder, 'gas': 145000})
    assert L_lend_token.balanceOf(_lend_token_holder, {'from': anyone}) == Web3.toWei(800, 'ether')
    # _lend_token_holder splits 600 L_lend_tokens into 600 I_lend_tokens and 600 S_lend_tokens and 600 U_lend_tokens for H20, Borrow_token, and STRIKE_150
    UnderwriterPoolDaoContract.split(Lend_token.address, H20, Borrow_token.address, STRIKE_150, Web3.toWei(600, 'ether'), {'from': _lend_token_holder, 'gas': 1100000})
    assert L_lend_token.balanceOf(_lend_token_holder, {'from': anyone}) == Web3.toWei(200, 'ether')
    _i_id = I_lend_token.id(Lend_token.address, H20, ZERO_ADDRESS, 0, {'from': anyone})
    _s_id = S_lend_token.id(Lend_token.address, H20, Borrow_token.address, STRIKE_150, {'from': anyone})
    _u_id = U_lend_token.id(Lend_token.address, H20, Borrow_token.address, STRIKE_150, {'from': anyone})
    assert I_lend_token.balanceOf(_lend_token_holder, _i_id, {'from': anyone}) == Web3.toWei(600, 'ether')
    assert S_lend_token.balanceOf(_lend_token_holder, _s_id, {'from': anyone}) == Web3.toWei(600, 'ether')
    assert U_lend_token.balanceOf(_lend_token_holder, _u_id, {'from': anyone}) == Web3.toWei(600, 'ether')
    # EscapeHatchManager pauses UnderwriterPoolDaoContract
    ProtocolDaoContract.toggle_dao_pause(PROTOCOL_CONSTANTS['DAO_UNDERWRITER_POOL'], True, {'from': EscapeHatchManager})
    # Tx fails when calling split() and UnderwriterPoolDaoContract is paused
    assert_tx_failed(lambda: UnderwriterPoolDaoContract.split(Lend_token.address, H20, Borrow_token.address, STRIKE_150, Web3.toWei(600, 'ether'), {'from': _lend_token_holder, 'gas': 145000}))


def test_fuse(accounts, assert_tx_failed,
        Whale, Deployer, EscapeHatchManager, Governor,
        Lend_token, Borrow_token,
        get_ERC20_contract, get_MFT_contract,
        get_CurrencyDao_contract, get_UnderwriterPoolDao_contract,
        ProtocolDaoContract):
    anyone = accounts[-1]
    # get CurrencyDao
    CurrencyDao = get_CurrencyDao_contract(address=ProtocolDaoContract.daos(PROTOCOL_CONSTANTS['DAO_CURRENCY']))
    # get UnderwriterPoolDaoContract
    UnderwriterPoolDaoContract = get_UnderwriterPoolDao_contract(address=ProtocolDaoContract.daos(PROTOCOL_CONSTANTS['DAO_UNDERWRITER_POOL']))
    # assign one of the accounts as _lend_token_holder
    _lend_token_holder = accounts[5]
    # Tx fails when calling split() and UnderwriterPoolDaoContract is not initialized
    assert_tx_failed(lambda: UnderwriterPoolDaoContract.fuse(Lend_token.address, H20, Borrow_token.address, STRIKE_150, Web3.toWei(600, 'ether'), {'from': _lend_token_holder, 'gas': 145000}))
    # initialize CurrencyDao
    ProtocolDaoContract.initialize_currency_dao({'from': Deployer})
    # initialize UnderwriterPoolDaoContract
    ProtocolDaoContract.initialize_underwriter_pool_dao({'from': Deployer})
    # Tx fails when calling split() and UnderwriterPoolDaoContract is not initialized
    assert_tx_failed(lambda: UnderwriterPoolDaoContract.fuse(Lend_token.address, H20, Borrow_token.address, STRIKE_150, Web3.toWei(600, 'ether'), {'from': _lend_token_holder, 'gas': 145000}))
    # set support for Lend_token
    ProtocolDaoContract.set_token_support(Lend_token.address, True, {'from': Governor, 'gas': 2000000})
    # Tx fails when calling split() and UnderwriterPoolDaoContract is not initialized
    assert_tx_failed(lambda: UnderwriterPoolDaoContract.fuse(Lend_token.address, H20, Borrow_token.address, STRIKE_150, Web3.toWei(600, 'ether'), {'from': _lend_token_holder, 'gas': 145000}))
    # set support for Borrow_token
    ProtocolDaoContract.set_token_support(Borrow_token.address, True, {'from': Governor, 'gas': 2000000})
    # get L_Lend_token
    L_lend_token = get_ERC20_contract(address=CurrencyDao.token_addresses__l(Lend_token.address, {'from': anyone}))
    # get I_Lend_token
    I_lend_token = get_MFT_contract(address=CurrencyDao.token_addresses__i(Lend_token.address, {'from': anyone}))
    # get S_Lend_token
    S_lend_token = get_MFT_contract(address=CurrencyDao.token_addresses__s(Lend_token.address, {'from': anyone}))
    # get U_Lend_token
    U_lend_token = get_MFT_contract(address=CurrencyDao.token_addresses__u(Lend_token.address, {'from': anyone}))
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
    # _lend_token_holder splits 600 L_lend_tokens into 600 I_lend_tokens and 600 S_lend_tokens and 600 U_lend_tokens for H20, Borrow_token, and STRIKE_150
    UnderwriterPoolDaoContract.split(Lend_token.address, H20, Borrow_token.address, STRIKE_150, Web3.toWei(600, 'ether'), {'from': _lend_token_holder, 'gas': 1100000})
    assert L_lend_token.balanceOf(_lend_token_holder, {'from': anyone}) == Web3.toWei(200, 'ether')
    _i_id = I_lend_token.id(Lend_token.address, H20, ZERO_ADDRESS, 0, {'from': anyone})
    _s_id = S_lend_token.id(Lend_token.address, H20, Borrow_token.address, STRIKE_150, {'from': anyone})
    _u_id = U_lend_token.id(Lend_token.address, H20, Borrow_token.address, STRIKE_150, {'from': anyone})
    assert I_lend_token.balanceOf(_lend_token_holder, _i_id, {'from': anyone}) == Web3.toWei(600, 'ether')
    assert S_lend_token.balanceOf(_lend_token_holder, _s_id, {'from': anyone}) == Web3.toWei(600, 'ether')
    assert U_lend_token.balanceOf(_lend_token_holder, _u_id, {'from': anyone}) == Web3.toWei(600, 'ether')
    # _lend_token_holder fuses 400 I_lend_tokens and 400 S_lend_tokens and 400 U_lend_tokens for H20, Borrow_token, and STRIKE_150 into 400 L_lend_tokens
    UnderwriterPoolDaoContract.fuse(Lend_token.address, H20, Borrow_token.address, STRIKE_150, Web3.toWei(400, 'ether'), {'from': _lend_token_holder, 'gas': 200000})
    assert L_lend_token.balanceOf(_lend_token_holder, {'from': anyone}) == Web3.toWei(600, 'ether')
    _i_id = I_lend_token.id(Lend_token.address, H20, ZERO_ADDRESS, 0, {'from': anyone})
    _s_id = S_lend_token.id(Lend_token.address, H20, Borrow_token.address, STRIKE_150, {'from': anyone})
    _u_id = U_lend_token.id(Lend_token.address, H20, Borrow_token.address, STRIKE_150, {'from': anyone})
    assert I_lend_token.balanceOf(_lend_token_holder, _i_id, {'from': anyone}) == Web3.toWei(200, 'ether')
    assert S_lend_token.balanceOf(_lend_token_holder, _s_id, {'from': anyone}) == Web3.toWei(200, 'ether')
    assert U_lend_token.balanceOf(_lend_token_holder, _u_id, {'from': anyone}) == Web3.toWei(200, 'ether')
    # EscapeHatchManager pauses UnderwriterPoolDaoContract
    ProtocolDaoContract.toggle_dao_pause(PROTOCOL_CONSTANTS['DAO_UNDERWRITER_POOL'], True, {'from': EscapeHatchManager})
    # Tx fails when calling split() and UnderwriterPoolDaoContract is paused
    assert_tx_failed(lambda: UnderwriterPoolDaoContract.fuse(Lend_token.address, H20, Borrow_token.address, STRIKE_150, Web3.toWei(600, 'ether'), {'from': _lend_token_holder, 'gas': 145000}))


def test_register_pool(accounts, get_log_args,
        Whale, Deployer, Governor,
        Lend_token, LST_token,
        get_ERC20_contract, get_MFT_contract,
        get_PoolNameRegistry_contract,
        get_CurrencyDao_contract, get_UnderwriterPoolDao_contract,
        get_UnderwriterPool_contract, get_ERC20_Pool_Token_contract,
        ProtocolDaoContract):
        anyone = accounts[-1]
        # get CurrencyDao
        CurrencyDao = get_CurrencyDao_contract(address=ProtocolDaoContract.daos(PROTOCOL_CONSTANTS['DAO_CURRENCY']))
        # get UnderwriterPoolDaoContract
        UnderwriterPoolDaoContract = get_UnderwriterPoolDao_contract(address=ProtocolDaoContract.daos(PROTOCOL_CONSTANTS['DAO_UNDERWRITER_POOL']))
        # get PoolNameRegistry
        PoolNameRegistry = get_PoolNameRegistry_contract(address=ProtocolDaoContract.registries(PROTOCOL_CONSTANTS['REGISTRY_POOL_NAME']))
        # assign one of the accounts as _lend_token_holder
        _lend_token_holder = accounts[5]
        # assign one of the accounts as _pool_owner
        _pool_owner = accounts[6]
        # initialize PoolNameRegistry
        ProtocolDaoContract.initialize_pool_name_registry(Web3.toWei(POOL_NAME_REGISTRATION_MIN_STAKE_LST, 'ether'), {'from': Deployer})
        # initialize CurrencyDao
        ProtocolDaoContract.initialize_currency_dao({'from': Deployer})
        # initialize UnderwriterPoolDaoContract
        ProtocolDaoContract.initialize_underwriter_pool_dao({'from': Deployer})
        # set support for Lend_token
        ProtocolDaoContract.set_token_support(Lend_token.address, True, {'from': Governor, 'gas': 2000000})
        # _pool_owner buys POOL_NAME_REGISTRATION_MIN_STAKE_LST LST_token from a 3rd party exchange
        LST_token.transfer(_pool_owner, Web3.toWei(POOL_NAME_REGISTRATION_MIN_STAKE_LST, 'ether'), {'from': Whale})
        assert LST_token.balanceOf(_pool_owner, {'from': anyone}) == Web3.toWei(POOL_NAME_REGISTRATION_MIN_STAKE_LST, 'ether')
        # _pool_owner authorizes CurrencyDao to spend POOL_NAME_REGISTRATION_MIN_STAKE_LST LST_token
        LST_token.approve(CurrencyDao.address, Web3.toWei(POOL_NAME_REGISTRATION_MIN_STAKE_LST, 'ether'), {'from': _pool_owner})
        assert LST_token.allowance(_pool_owner, CurrencyDao.address, {'from': anyone}) == Web3.toWei(POOL_NAME_REGISTRATION_MIN_STAKE_LST, 'ether')
        # _pool_owner registers _pool_name POOL_NAME_LIONFURY
        _pool_name = POOL_NAME_LIONFURY
        assert UnderwriterPoolDaoContract.next_pool_id({'from': anyone}) == 0
        assert UnderwriterPoolDaoContract.pools__name(_pool_name, {'from': anyone}) in (None, "")
        tx = UnderwriterPoolDaoContract.register_pool(
            False, Lend_token.address, _pool_name, Web3.toWei(50, 'ether'), 1, 1, 90, {'from': _pool_owner, 'gas': 1200000})
        assert UnderwriterPoolDaoContract.next_pool_id({'from': anyone}) == 1
        assert UnderwriterPoolDaoContract.pools__name(_pool_name, {'from': anyone}) == _pool_name
        assert UnderwriterPoolDaoContract.pools__currency(_pool_name, {'from': anyone}) == Lend_token.address
        assert UnderwriterPoolDaoContract.pools__operator(_pool_name, {'from': anyone}) == _pool_owner
        assert UnderwriterPoolDaoContract.pools__id(_pool_name, {'from': anyone}) == 0
        # verify logs
        args = get_log_args(tx, 'PoolRegistered')
        assert args['_operator'] == _pool_owner
        assert args['_currency'] == Lend_token.address
        assert args['address_'] == UnderwriterPoolDaoContract.pools__address_(_pool_name, {'from': anyone})
        # get UnderwriterPool
        UnderwriterPool = get_UnderwriterPool_contract(address=UnderwriterPoolDaoContract.pools__address_(_pool_name, {'from': anyone}))
        assert UnderwriterPool.initialized({'from': anyone})
        assert UnderwriterPool.owner({'from': anyone}) == _pool_owner
        assert UnderwriterPool.protocol_dao({'from': anyone}) == ProtocolDaoContract.address
        assert UnderwriterPool.name({'from': anyone}) == _pool_name
        assert UnderwriterPool.initial_exchange_rate({'from': anyone}) == Web3.toWei(50, 'ether')
        assert UnderwriterPool.currency({'from': anyone}) == Lend_token.address
        assert UnderwriterPool.fee_percentage_per_i_token({'from': anyone}) == 1
        assert UnderwriterPool.fee_percentage_per_s_token({'from': anyone}) == 1
        assert UnderwriterPool.mft_expiry_limit_days({'from': anyone}) == 90
        assert not UnderwriterPool.pool_share_token({'from': anyone}) == ZERO_ADDRESS
        # get UnderwriterPoolToken
        UnderwriterPoolToken = get_ERC20_Pool_Token_contract(address=UnderwriterPool.pool_share_token({'from': anyone}))
        assert UnderwriterPoolToken.name({'from': anyone}) == _pool_name
        assert UnderwriterPoolToken.symbol({'from': anyone}) == "{0}.RU.{1}".format(_pool_name, Lend_token.symbol({'from': anyone}))


def test_register_mft_support(accounts, get_log_args,
        Whale, Deployer, Governor,
        Lend_token, Borrow_token, LST_token,
        get_ERC20_contract, get_MFT_contract,
        get_PoolNameRegistry_contract,
        get_CurrencyDao_contract, get_UnderwriterPoolDao_contract,
        get_MarketDao_contract,
        get_UnderwriterPool_contract,
        ProtocolDaoContract):
        anyone = accounts[-1]
        # get CurrencyDao
        CurrencyDao = get_CurrencyDao_contract(address=ProtocolDaoContract.daos(PROTOCOL_CONSTANTS['DAO_CURRENCY']))
        # get UnderwriterPoolDaoContract
        UnderwriterPoolDaoContract = get_UnderwriterPoolDao_contract(address=ProtocolDaoContract.daos(PROTOCOL_CONSTANTS['DAO_UNDERWRITER_POOL']))
        # get MarketDao
        MarketDao = get_MarketDao_contract(address=ProtocolDaoContract.daos(PROTOCOL_CONSTANTS['DAO_MARKET']))
        # get PoolNameRegistry
        PoolNameRegistry = get_PoolNameRegistry_contract(address=ProtocolDaoContract.registries(PROTOCOL_CONSTANTS['REGISTRY_POOL_NAME']))
        # assign one of the accounts as _lend_token_holder
        _lend_token_holder = accounts[5]
        # assign one of the accounts as _pool_owner
        _pool_owner = accounts[6]
        # initialize PoolNameRegistry
        ProtocolDaoContract.initialize_pool_name_registry(Web3.toWei(POOL_NAME_REGISTRATION_MIN_STAKE_LST, 'ether'), {'from': Deployer})
        # initialize CurrencyDao
        ProtocolDaoContract.initialize_currency_dao({'from': Deployer})
        # initialize UnderwriterPoolDaoContract
        ProtocolDaoContract.initialize_underwriter_pool_dao({'from': Deployer})
        # initialize MarketDao
        ProtocolDaoContract.initialize_market_dao({'from': Deployer})
        # initialize ShieldPayoutDao
        ProtocolDaoContract.initialize_shield_payout_dao({'from': Deployer})
        # set support for Lend_token
        ProtocolDaoContract.set_token_support(Lend_token.address, True, {'from': Governor, 'gas': 2000000})
        # get I_Lend_token
        I_lend_token = get_MFT_contract(address=CurrencyDao.token_addresses__i(Lend_token.address, {'from': anyone}))
        # get S_Lend_token
        S_lend_token = get_MFT_contract(address=CurrencyDao.token_addresses__s(Lend_token.address, {'from': anyone}))
        # get U_Lend_token
        U_lend_token = get_MFT_contract(address=CurrencyDao.token_addresses__u(Lend_token.address, {'from': anyone}))
        # set support for Borrow_token
        ProtocolDaoContract.set_token_support(Borrow_token.address, True, {'from': Governor, 'gas': 2000000})
        # _pool_owner buys POOL_NAME_REGISTRATION_MIN_STAKE_LST LST_token from a 3rd party exchange
        LST_token.transfer(_pool_owner, Web3.toWei(POOL_NAME_REGISTRATION_MIN_STAKE_LST, 'ether'), {'from': Whale})
        assert LST_token.balanceOf(_pool_owner) == Web3.toWei(POOL_NAME_REGISTRATION_MIN_STAKE_LST, 'ether')
        # _pool_owner authorizes CurrencyDao to spend POOL_NAME_REGISTRATION_MIN_STAKE_LST LST_token
        LST_token.approve(CurrencyDao.address, Web3.toWei(POOL_NAME_REGISTRATION_MIN_STAKE_LST, 'ether'), {'from': _pool_owner})
        assert LST_token.allowance(_pool_owner, CurrencyDao.address, {'from': anyone}) == Web3.toWei(POOL_NAME_REGISTRATION_MIN_STAKE_LST, 'ether')
        # _pool_owner registers _pool_name POOL_NAME_LIONFURY
        _pool_name = POOL_NAME_LIONFURY
        UnderwriterPoolDaoContract.register_pool(
            False, Lend_token.address, _pool_name, Web3.toWei(50, 'ether'), 1, 1, 90, {'from': _pool_owner, 'gas': 1200000})
        assert UnderwriterPoolDaoContract.pools__name(_pool_name, {'from': anyone}) == _pool_name
        # get UnderwriterPool
        UnderwriterPool = get_UnderwriterPool_contract(address=UnderwriterPoolDaoContract.pools__address_(_pool_name, {'from': anyone}))
        ProtocolDaoContract.set_minimum_mft_fee(
            PROTOCOL_CONSTANTS['DAO_UNDERWRITER_POOL'],
            Web3.toWei(INTEREST_POOL_DAO_MIN_MFT_FEE, 'ether'),
            {'from': Governor})
        # set MFT multiplier
        ProtocolDaoContract.set_fee_multiplier_per_mft_count(
            PROTOCOL_CONSTANTS['DAO_UNDERWRITER_POOL'], Web3.toWei(0, 'ether'),
            Web3.toWei(INTEREST_POOL_DAO_FEE_MULTIPLIER_PER_MFT_COUNT, 'ether'),
            {'from': Governor, 'gas': 75000})
        # set support for expiry H20
        ProtocolDaoContract.set_expiry_support(H20, "H20", True, {'from': Governor})
        # _pool_owner buys INTEREST_POOL_DAO_MIN_MFT_FEE LST_token from a 3rd party exchange
        LST_token.transfer(_pool_owner, Web3.toWei(INTEREST_POOL_DAO_MIN_MFT_FEE, 'ether'), {'from': Whale})
        assert LST_token.balanceOf(_pool_owner, {'from': anyone}) == Web3.toWei(INTEREST_POOL_DAO_MIN_MFT_FEE, 'ether')
        # _pool_owner authorizes CurrencyDao to spend INTEREST_POOL_DAO_MIN_MFT_FEE LST_token
        LST_token.approve(CurrencyDao.address, Web3.toWei(INTEREST_POOL_DAO_MIN_MFT_FEE, 'ether'), {'from': _pool_owner})
        assert LST_token.allowance(_pool_owner, CurrencyDao.address, {'from': anyone}) == Web3.toWei(INTEREST_POOL_DAO_MIN_MFT_FEE, 'ether')
        # set support for MFT H20
        assert MarketDao.expiry_markets__expiry(H20, {'from': anyone}) in (None, 0)
        _loan_market_hash = MarketDao.loan_market_hash(Lend_token.address, H20, Borrow_token.address, {'from': anyone})
        assert MarketDao.loan_markets__hash(_loan_market_hash, {'from': anyone}) == EMPTY_BYTES32
        _shield_market_hash = MarketDao.shield_market_hash(Lend_token.address, H20, Borrow_token.address, STRIKE_150, {'from': anyone})
        assert MarketDao.shield_markets__hash(_shield_market_hash, {'from': anyone}) == EMPTY_BYTES32
        assert UnderwriterPoolDaoContract.pools__mft_count(_pool_name, {'from': anyone}) == 0
        assert UnderwriterPoolDaoContract.pools__LST_staked(_pool_name, {'from': anyone}) == 0
        assert UnderwriterPoolDaoContract.LST_stake_value(_pool_name, {'from': anyone}) == Web3.toWei(INTEREST_POOL_DAO_MIN_MFT_FEE, 'ether')
        tx = UnderwriterPool.support_mft(H20, Borrow_token.address, STRIKE_150,
            Web3.toWei(0.025, 'ether'), Web3.toWei(0.05, 'ether'), {'from': _pool_owner, 'gas': 2500000})
        assert UnderwriterPoolDaoContract.pools__mft_count(_pool_name, {'from': anyone}) == 1
        assert UnderwriterPoolDaoContract.pools__LST_staked(_pool_name, {'from': anyone}) == Web3.toWei(INTEREST_POOL_DAO_MIN_MFT_FEE, 'ether')
        assert MarketDao.expiry_markets__expiry(H20, {'from': anyone}) == H20
        assert MarketDao.loan_markets__hash(_loan_market_hash, {'from': anyone}) == _loan_market_hash
        assert MarketDao.shield_markets__hash(_shield_market_hash, {'from': anyone}) == _shield_market_hash
        # # verify logs
        # args = get_log_args(tx, 'MFTSupportRegistered')
        # assert args['_name'] == "Lion Fury"
        # assert args['_pool'] == UnderwriterPoolDaoContract.pools__address_(_pool_name, {'from': anyone})
        # assert args['_currency'] == Lend_token.address
        # assert args['_expiry'] == H20
        # assert args['_underlying'] == Borrow_token.address
        # assert args['_strike_price'] == STRIKE_150
        # assert args['_operator'] == _pool_owner
        # args = get_log_args(tx, 'TransferSingle')
        # assert args['_operator'] == UnderwriterPoolDaoContract.address
        # assert args['_from'] == ZERO_ADDRESS
        # assert args['_to'] == UnderwriterPoolDaoContract.address
        # assert args['_id'] == I_lend_token.nonce({'from': anyone})
        # assert args['_value'] == 0
        # args = get_log_args(tx, 'TransferSingle', idx=1)
        # assert args['_operator'] == UnderwriterPoolDaoContract.address
        # assert args['_from'] == ZERO_ADDRESS
        # assert args['_to'] == UnderwriterPoolDaoContract.address
        # assert args['_id'] == S_lend_token.nonce({'from': anyone})
        # assert args['_value'] == 0
        # args = get_log_args(tx, 'TransferSingle', idx=2)
        # assert args['_operator'] == UnderwriterPoolDaoContract.address
        # assert args['_from'] == ZERO_ADDRESS
        # assert args['_to'] == UnderwriterPoolDaoContract.address
        # assert args['_id'] == U_lend_token.nonce({'from': anyone})
        # assert args['_value'] == 0
        # args = get_log_args(tx, 'Transfer')
        # assert args['_from'] == _pool_owner
        # assert args['_to'] == UnderwriterPoolDaoContract.address
        # assert args['_value'] == Web3.toWei(INTEREST_POOL_DAO_MIN_MFT_FEE, 'ether')
