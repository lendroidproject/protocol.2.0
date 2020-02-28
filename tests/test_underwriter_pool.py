import os

import pytest

from web3 import Web3

from conftest import (
    PROTOCOL_CONSTANTS,
    POOL_NAME_REGISTRATION_MIN_STAKE_LST, POOL_NAME_LIONFURY,
    ZERO_ADDRESS, EMPTY_BYTES32,
    INTEREST_POOL_DAO_MIN_MFT_FEE, INTEREST_POOL_DAO_FEE_MULTIPLIER_PER_MFT_COUNT,
    STRIKE_125, H20,
    MAX_LIABILITY_CURENCY_MARKET
)


def test_initialize(accounts,
        Whale, Deployer, Governor,
        LST_token, Lend_token,
        get_ERC20_contract, get_ERC20_Pool_Token_contract, get_MFT_contract,
        get_PoolNameRegistry_contract, get_UnderwriterPool_contract,
        get_CurrencyDao_contract, get_UnderwriterPoolDao_contract,
        ProtocolDaoContract):
    anyone = accounts[-1]
    # get CurrencyDaoContract
    CurrencyDaoContract = get_CurrencyDao_contract(address=ProtocolDaoContract.daos(PROTOCOL_CONSTANTS['DAO_CURRENCY']))
    # get UnderwriterPoolDaoContract
    UnderwriterPoolDaoContract = get_UnderwriterPoolDao_contract(address=ProtocolDaoContract.daos(PROTOCOL_CONSTANTS['DAO_UNDERWRITER_POOL']))
    # get PoolNameRegistryContract
    PoolNameRegistryContract = get_PoolNameRegistry_contract(address=ProtocolDaoContract.registries(PROTOCOL_CONSTANTS['REGISTRY_POOL_NAME']))
    # assign one of the accounts as _pool_owner
    _pool_owner = accounts[6]
    # initialize PoolNameRegistryContract
    ProtocolDaoContract.initialize_pool_name_registry(Web3.toWei(POOL_NAME_REGISTRATION_MIN_STAKE_LST, 'ether'), {'from': Deployer})
    # initialize CurrencyDaoContract
    ProtocolDaoContract.initialize_currency_dao({'from': Deployer})
    # initialize UnderwriterPoolDaoContract
    ProtocolDaoContract.initialize_underwriter_pool_dao({'from': Deployer})
    # set support for Lend_token
    ProtocolDaoContract.set_token_support(Lend_token.address, True, {'from': Governor, 'gas': 2000000})
    # _pool_owner buys POOL_NAME_REGISTRATION_MIN_STAKE_LST LST_token from a 3rd party exchange
    LST_token.transfer(_pool_owner, Web3.toWei(POOL_NAME_REGISTRATION_MIN_STAKE_LST, 'ether'), {'from': Whale})
    # _pool_owner authorizes CurrencyDaoContract to spend POOL_NAME_REGISTRATION_MIN_STAKE_LST LST_token
    LST_token.approve(CurrencyDaoContract.address, Web3.toWei(POOL_NAME_REGISTRATION_MIN_STAKE_LST, 'ether'), {'from': _pool_owner})
    # _pool_owner registers _pool_name POOL_NAME_LIONFURY at the UnderwriterPoolDaoContract
    _pool_name = POOL_NAME_LIONFURY
    UnderwriterPoolDaoContract.register_pool(
        False, Lend_token.address, _pool_name, Web3.toWei(50, 'ether'), 1, 1, 90, {'from': _pool_owner, 'gas': 1200000})
    # get UnderwriterPoolContract
    UnderwriterPoolContract = get_UnderwriterPool_contract(address=UnderwriterPoolDaoContract.pools__address_(_pool_name, {'from': anyone}))
    assert UnderwriterPoolContract.initialized({'from': anyone})


def test_contribute(accounts,
        Whale, Deployer, Governor,
        LST_token, Lend_token,
        get_ERC20_contract, get_ERC20_Pool_Token_contract, get_MFT_contract,
        get_PoolNameRegistry_contract, get_UnderwriterPool_contract,
        get_CurrencyDao_contract, get_UnderwriterPoolDao_contract,
        ProtocolDaoContract):
    anyone = accounts[-1]
    # get CurrencyDaoContract
    CurrencyDaoContract = get_CurrencyDao_contract(address=ProtocolDaoContract.daos(PROTOCOL_CONSTANTS['DAO_CURRENCY']))
    # get UnderwriterPoolDaoContract
    UnderwriterPoolDaoContract = get_UnderwriterPoolDao_contract(address=ProtocolDaoContract.daos(PROTOCOL_CONSTANTS['DAO_UNDERWRITER_POOL']))
    # get PoolNameRegistryContract
    PoolNameRegistryContract = get_PoolNameRegistry_contract(address=ProtocolDaoContract.registries(PROTOCOL_CONSTANTS['REGISTRY_POOL_NAME']))
    # assign one of the accounts as _pool_owner
    _pool_owner = accounts[6]
    # initialize PoolNameRegistryContract
    ProtocolDaoContract.initialize_pool_name_registry(Web3.toWei(POOL_NAME_REGISTRATION_MIN_STAKE_LST, 'ether'), {'from': Deployer})
    # initialize CurrencyDaoContract
    ProtocolDaoContract.initialize_currency_dao({'from': Deployer})
    # initialize UnderwriterPoolDaoContract
    ProtocolDaoContract.initialize_underwriter_pool_dao({'from': Deployer})
    # set support for Lend_token
    ProtocolDaoContract.set_token_support(Lend_token.address, True, {'from': Governor, 'gas': 2000000})
    # get L_Lend_token
    L_lend_token = get_ERC20_contract(address=CurrencyDaoContract.token_addresses__l(Lend_token.address, {'from': anyone}))
    # get F_Lend_token
    F_lend_token = get_MFT_contract(address=CurrencyDaoContract.token_addresses__f(Lend_token.address, {'from': anyone}))
    # get I_lend_token
    I_lend_token = get_MFT_contract(address=CurrencyDaoContract.token_addresses__i(Lend_token.address, {'from': anyone}))
    # _pool_owner buys 1000 lend token from a 3rd party exchange
    Lend_token.transfer(_pool_owner, Web3.toWei(1000, 'ether'), {'from': Whale})
    # _pool_owner authorizes CurrencyDaoContract to spend 800 Lend_token
    Lend_token.approve(CurrencyDaoContract.address, Web3.toWei(800, 'ether'), {'from': _pool_owner})
    # _pool_owner wraps 800 Lend_token to L_lend_token
    CurrencyDaoContract.wrap(Lend_token.address, Web3.toWei(800, 'ether'), {'from': _pool_owner, 'gas': 145000})
    # _pool_owner buys POOL_NAME_REGISTRATION_MIN_STAKE_LST LST_token from a 3rd party exchange
    LST_token.transfer(_pool_owner, Web3.toWei(POOL_NAME_REGISTRATION_MIN_STAKE_LST, 'ether'), {'from': Whale})
    # _pool_owner authorizes CurrencyDaoContract to spend POOL_NAME_REGISTRATION_MIN_STAKE_LST LST_token
    LST_token.approve(CurrencyDaoContract.address, Web3.toWei(POOL_NAME_REGISTRATION_MIN_STAKE_LST, 'ether'), {'from': _pool_owner})
    # _pool_owner registers _pool_name POOL_NAME_LIONFURY at the UnderwriterPoolDaoContract
    _pool_name = POOL_NAME_LIONFURY
    UnderwriterPoolDaoContract.register_pool(
        False, Lend_token.address, _pool_name, Web3.toWei(50, 'ether'), 1, 1, 90, {'from': _pool_owner, 'gas': 1200000})
    # get UnderwriterPoolContract
    UnderwriterPoolContract = get_UnderwriterPool_contract(address=UnderwriterPoolDaoContract.pools__address_(_pool_name, {'from': anyone}))
    # get Poolshare_token
    Poolshare_token = get_ERC20_Pool_Token_contract(address=UnderwriterPoolContract.pool_share_token({'from': anyone}))
    # verify L_Lend_token and Poolshare_token balances
    assert L_lend_token.balanceOf(UnderwriterPoolContract.address, {'from': anyone}) == 0
    assert Poolshare_token.balanceOf(_pool_owner, {'from': anyone}) == 0
    # _pool_owner contributes 500 L_lend_token to his own pool _pool_name
    assert UnderwriterPoolContract.exchange_rate({'from': anyone}) == Web3.toWei(50, 'ether')
    assert UnderwriterPoolContract.estimated_pool_share_tokens(Web3.toWei(500, 'ether'), {'from': anyone}) == Web3.toWei(25000, 'ether')
    assert UnderwriterPoolContract.l_token_balance({'from': anyone}) == 0
    assert UnderwriterPoolContract.total_pool_share_token_supply({'from': anyone}) == 0
    UnderwriterPoolContract.contribute(Web3.toWei(500, 'ether'), {'from': _pool_owner, 'gas': 300000})
    # verify L_Lend_token and Poolshare_token balances
    assert UnderwriterPoolContract.total_pool_share_token_supply({'from': anyone}) == Web3.toWei(25000, 'ether')
    assert Poolshare_token.balanceOf(_pool_owner, {'from': anyone}) == Web3.toWei(25000, 'ether')
    # _pool_owner contributes 200 L_lend_token to his own pool _pool_name
    assert UnderwriterPoolContract.exchange_rate({'from': anyone}) == Web3.toWei(50, 'ether')
    assert UnderwriterPoolContract.estimated_pool_share_tokens(Web3.toWei(200, 'ether'), {'from': anyone}) == Web3.toWei(10000, 'ether')
    UnderwriterPoolContract.contribute(Web3.toWei(200, 'ether'), {'from': _pool_owner, 'gas': 300000})
    # verify L_Lend_token and Poolshare_token balances
    assert L_lend_token.balanceOf(UnderwriterPoolContract.address, {'from': anyone}) == Web3.toWei(700, 'ether')
    assert UnderwriterPoolContract.l_token_balance({'from': anyone}) == Web3.toWei(700, 'ether')
    assert UnderwriterPoolContract.total_pool_share_token_supply({'from': anyone}) == Web3.toWei(35000, 'ether')
    assert Poolshare_token.balanceOf(_pool_owner, {'from': anyone}) == Web3.toWei(35000, 'ether')


def test_withdraw_contribution_sans_i_token_and_s_token_purchase(accounts,
        Whale, Deployer, Governor,
        LST_token, Lend_token,
        get_ERC20_contract, get_ERC20_Pool_Token_contract, get_MFT_contract,
        get_PoolNameRegistry_contract, get_UnderwriterPool_contract,
        get_CurrencyDao_contract, get_UnderwriterPoolDao_contract,
        ProtocolDaoContract):
    anyone = accounts[-1]
    # get CurrencyDaoContract
    CurrencyDaoContract = get_CurrencyDao_contract(address=ProtocolDaoContract.daos(PROTOCOL_CONSTANTS['DAO_CURRENCY']))
    # get UnderwriterPoolDaoContract
    UnderwriterPoolDaoContract = get_UnderwriterPoolDao_contract(address=ProtocolDaoContract.daos(PROTOCOL_CONSTANTS['DAO_UNDERWRITER_POOL']))
    # get PoolNameRegistryContract
    PoolNameRegistryContract = get_PoolNameRegistry_contract(address=ProtocolDaoContract.registries(PROTOCOL_CONSTANTS['REGISTRY_POOL_NAME']))
    # assign one of the accounts as _pool_owner
    _pool_owner = accounts[6]
    # initialize PoolNameRegistryContract
    ProtocolDaoContract.initialize_pool_name_registry(Web3.toWei(POOL_NAME_REGISTRATION_MIN_STAKE_LST, 'ether'), {'from': Deployer})
    # initialize CurrencyDaoContract
    ProtocolDaoContract.initialize_currency_dao({'from': Deployer})
    # initialize UnderwriterPoolDaoContract
    ProtocolDaoContract.initialize_underwriter_pool_dao({'from': Deployer})
    # set support for Lend_token
    ProtocolDaoContract.set_token_support(Lend_token.address, True, {'from': Governor, 'gas': 2000000})
    # get L_Lend_token
    L_lend_token = get_ERC20_contract(address=CurrencyDaoContract.token_addresses__l(Lend_token.address, {'from': anyone}))
    # get F_Lend_token
    F_lend_token = get_MFT_contract(address=CurrencyDaoContract.token_addresses__f(Lend_token.address, {'from': anyone}))
    # get I_lend_token
    I_lend_token = get_MFT_contract(address=CurrencyDaoContract.token_addresses__i(Lend_token.address, {'from': anyone}))
    # _pool_owner buys 1000 lend token from a 3rd party exchange
    Lend_token.transfer(_pool_owner, Web3.toWei(1000, 'ether'), {'from': Whale})
    # _pool_owner authorizes CurrencyDaoContract to spend 800 Lend_token
    Lend_token.approve(CurrencyDaoContract.address, Web3.toWei(800, 'ether'), {'from': _pool_owner})
    # _pool_owner wraps 800 Lend_token to L_lend_token
    CurrencyDaoContract.wrap(Lend_token.address, Web3.toWei(800, 'ether'), {'from': _pool_owner, 'gas': 145000})
    # _pool_owner buys POOL_NAME_REGISTRATION_MIN_STAKE_LST LST_token from a 3rd party exchange
    LST_token.transfer(_pool_owner, Web3.toWei(POOL_NAME_REGISTRATION_MIN_STAKE_LST, 'ether'), {'from': Whale})
    # _pool_owner authorizes CurrencyDaoContract to spend POOL_NAME_REGISTRATION_MIN_STAKE_LST LST_token
    LST_token.approve(CurrencyDaoContract.address, Web3.toWei(POOL_NAME_REGISTRATION_MIN_STAKE_LST, 'ether'), {'from': _pool_owner})
    # _pool_owner registers _pool_name POOL_NAME_LIONFURY at the UnderwriterPoolDaoContract
    _pool_name = POOL_NAME_LIONFURY
    UnderwriterPoolDaoContract.register_pool(
        False, Lend_token.address, _pool_name, Web3.toWei(50, 'ether'), 1, 1, 90, {'from': _pool_owner, 'gas': 1200000})
    # get UnderwriterPoolContract
    UnderwriterPoolContract = get_UnderwriterPool_contract(address=UnderwriterPoolDaoContract.pools__address_(_pool_name, {'from': anyone}))
    # get Poolshare_token
    Poolshare_token = get_ERC20_Pool_Token_contract(address=UnderwriterPoolContract.pool_share_token({'from': anyone}))
    # verify L_Lend_token and Poolshare_token balances
    assert L_lend_token.balanceOf(UnderwriterPoolContract.address, {'from': anyone}) == 0
    assert Poolshare_token.balanceOf(_pool_owner, {'from': anyone}) == 0
    # _pool_owner contributes 500 L_lend_token to his own UnderwriterPoolContract
    UnderwriterPoolContract.contribute(Web3.toWei(500, 'ether'), {'from': _pool_owner, 'gas': 250000})
    # verify L_Lend_token and Poolshare_token balances
    assert Poolshare_token.balanceOf(_pool_owner, {'from': anyone}) == Web3.toWei(25000, 'ether')
    assert L_lend_token.balanceOf(_pool_owner, {'from': anyone}) == Web3.toWei(300, 'ether')
    assert L_lend_token.balanceOf(UnderwriterPoolContract.address, {'from': anyone}) == Web3.toWei(500, 'ether')
    # _pool_owner withdraws 12500 Poolshare_token from his own UnderwriterPoolContract
    assert UnderwriterPoolContract.exchange_rate({'from': anyone}) == Web3.toWei(50, 'ether')
    assert UnderwriterPoolContract.l_token_balance({'from': anyone}) == Web3.toWei(500, 'ether')
    assert UnderwriterPoolContract.total_pool_share_token_supply({'from': anyone}) == Web3.toWei(25000, 'ether')
    assert UnderwriterPoolContract.estimated_pool_share_tokens(Web3.toWei(250, 'ether'), {'from': anyone}) == Web3.toWei(12500, 'ether')
    UnderwriterPoolContract.withdraw_contribution(Web3.toWei(12500, 'ether'), {'from': _pool_owner, 'gas': 200000})
    # verify L_Lend_token and Poolshare_token balances
    assert Poolshare_token.balanceOf(_pool_owner, {'from': anyone}) == Web3.toWei(12500, 'ether')
    assert L_lend_token.balanceOf(_pool_owner, {'from': anyone}) == Web3.toWei(550, 'ether')
    assert L_lend_token.balanceOf(UnderwriterPoolContract.address, {'from': anyone}) == Web3.toWei(250, 'ether')
    # _pool_owner withdraws 6250 Poolshare_token from his own UnderwriterPoolContract
    assert UnderwriterPoolContract.exchange_rate({'from': anyone}) == Web3.toWei(50, 'ether')
    assert UnderwriterPoolContract.l_token_balance({'from': anyone}) == Web3.toWei(250, 'ether')
    assert UnderwriterPoolContract.total_pool_share_token_supply({'from': anyone}) == Web3.toWei(12500, 'ether')
    assert UnderwriterPoolContract.estimated_pool_share_tokens(Web3.toWei(125, 'ether'), {'from': anyone}) == Web3.toWei(6250, 'ether')
    UnderwriterPoolContract.withdraw_contribution(Web3.toWei(6250, 'ether'), {'from': _pool_owner, 'gas': 200000})
    # verify L_Lend_token and Poolshare_token balances
    assert Poolshare_token.balanceOf(_pool_owner, {'from': anyone}) == Web3.toWei(6250, 'ether')
    assert L_lend_token.balanceOf(_pool_owner, {'from': anyone}) == Web3.toWei(675, 'ether')
    assert L_lend_token.balanceOf(UnderwriterPoolContract.address, {'from': anyone}) == Web3.toWei(125, 'ether')
    # _pool_owner withdraws all remaining 6250 Poolshare_token from his own UnderwriterPoolContract
    assert UnderwriterPoolContract.exchange_rate({'from': anyone}) == Web3.toWei(50, 'ether')
    assert UnderwriterPoolContract.l_token_balance({'from': anyone}) == Web3.toWei(125, 'ether')
    assert UnderwriterPoolContract.total_pool_share_token_supply({'from': anyone}) == Web3.toWei(6250, 'ether')
    assert UnderwriterPoolContract.estimated_pool_share_tokens(Web3.toWei(125, 'ether'), {'from': anyone}) == Web3.toWei(6250, 'ether')
    UnderwriterPoolContract.withdraw_contribution(Web3.toWei(6250, 'ether'), {'from': _pool_owner, 'gas': 200000})
    # verify L_Lend_token and Poolshare_token balances
    assert Poolshare_token.balanceOf(_pool_owner, {'from': anyone}) == 0
    assert L_lend_token.balanceOf(_pool_owner, {'from': anyone}) == Web3.toWei(800, 'ether')
    assert L_lend_token.balanceOf(UnderwriterPoolContract.address, {'from': anyone}) == 0
    assert UnderwriterPoolContract.l_token_balance({'from': anyone}) == 0
    assert UnderwriterPoolContract.total_pool_share_token_supply({'from': anyone}) == 0
    # _pool_owner again contributes 200 L_lend_token to his own UnderwriterPoolContract
    UnderwriterPoolContract.contribute(Web3.toWei(200, 'ether'), {'from': _pool_owner, 'gas': 250000})
    # verify L_Lend_token and Poolshare_token balances
    assert Poolshare_token.balanceOf(_pool_owner, {'from': anyone}) == Web3.toWei(10000, 'ether')
    assert L_lend_token.balanceOf(_pool_owner, {'from': anyone}) == Web3.toWei(600, 'ether')
    assert L_lend_token.balanceOf(UnderwriterPoolContract.address, {'from': anyone}) == Web3.toWei(200, 'ether')
    assert UnderwriterPoolContract.l_token_balance({'from': anyone}) == Web3.toWei(200, 'ether')
    assert UnderwriterPoolContract.total_pool_share_token_supply({'from': anyone}) == Web3.toWei(10000, 'ether')


def test_increment_s_tokens(accounts,
        Whale, Deployer, Governor,
        LST_token, Lend_token, Borrow_token,
        get_ERC20_contract, get_ERC20_Pool_Token_contract, get_MFT_contract,
        get_PoolNameRegistry_contract, get_MarketDao_contract, get_UnderwriterPool_contract,
        get_CurrencyDao_contract, get_UnderwriterPoolDao_contract,
        ProtocolDaoContract):
    anyone = accounts[-1]
    # get CurrencyDaoContract
    CurrencyDaoContract = get_CurrencyDao_contract(address=ProtocolDaoContract.daos(PROTOCOL_CONSTANTS['DAO_CURRENCY']))
    # get UnderwriterPoolDaoContract
    UnderwriterPoolDaoContract = get_UnderwriterPoolDao_contract(address=ProtocolDaoContract.daos(PROTOCOL_CONSTANTS['DAO_UNDERWRITER_POOL']))
    # get PoolNameRegistryContract
    PoolNameRegistryContract = get_PoolNameRegistry_contract(address=ProtocolDaoContract.registries(PROTOCOL_CONSTANTS['REGISTRY_POOL_NAME']))
    # get MarketDaoContract
    MarketDaoContract = get_MarketDao_contract(address=ProtocolDaoContract.daos(PROTOCOL_CONSTANTS['DAO_MARKET']))
    # assign one of the accounts as _pool_owner
    _pool_owner = accounts[6]
    # initialize PoolNameRegistryContract
    ProtocolDaoContract.initialize_pool_name_registry(Web3.toWei(POOL_NAME_REGISTRATION_MIN_STAKE_LST, 'ether'), {'from': Deployer})
    # initialize CurrencyDaoContract
    ProtocolDaoContract.initialize_currency_dao({'from': Deployer})
    # initialize UnderwriterPoolDaoContract
    ProtocolDaoContract.initialize_underwriter_pool_dao({'from': Deployer})
    # initialize MarketDaoContract
    ProtocolDaoContract.initialize_market_dao({'from': Deployer})
    # initialize ShieldPayoutDaoContract
    ProtocolDaoContract.initialize_shield_payout_dao({'from': Deployer})
    # set support for Lend_token
    ProtocolDaoContract.set_token_support(Lend_token.address, True, {'from': Governor, 'gas': 2000000})
    # set support for Borrow_token
    ProtocolDaoContract.set_token_support(Borrow_token.address, True, {'from': Governor})
    # get L_Lend_token
    L_lend_token = get_ERC20_contract(address=CurrencyDaoContract.token_addresses__l(Lend_token.address, {'from': anyone}))
    # get I_lend_token
    I_lend_token = get_MFT_contract(address=CurrencyDaoContract.token_addresses__i(Lend_token.address, {'from': anyone}))
    # get S_lend_token
    S_lend_token = get_MFT_contract(address=CurrencyDaoContract.token_addresses__s(Lend_token.address, {'from': anyone}))
    # get U_Lend_token
    U_lend_token = get_MFT_contract(address=CurrencyDaoContract.token_addresses__u(Lend_token.address, {'from': anyone}))
    # _pool_owner buys 1000 lend token from a 3rd party exchange
    Lend_token.transfer(_pool_owner, Web3.toWei(1000, 'ether'), {'from': Whale})
    # _pool_owner authorizes CurrencyDaoContract to spend 800 Lend_token
    Lend_token.approve(CurrencyDaoContract.address, Web3.toWei(800, 'ether'), {'from': _pool_owner})
    # _pool_owner wraps 800 Lend_token to L_lend_token
    CurrencyDaoContract.wrap(Lend_token.address, Web3.toWei(800, 'ether'), {'from': _pool_owner, 'gas': 145000})
    # _pool_owner buys POOL_NAME_REGISTRATION_MIN_STAKE_LST LST_token from a 3rd party exchange
    LST_token.transfer(_pool_owner, Web3.toWei(POOL_NAME_REGISTRATION_MIN_STAKE_LST, 'ether'), {'from': Whale})
    # _pool_owner authorizes CurrencyDaoContract to spend POOL_NAME_REGISTRATION_MIN_STAKE_LST LST_token
    LST_token.approve(CurrencyDaoContract.address, Web3.toWei(POOL_NAME_REGISTRATION_MIN_STAKE_LST, 'ether'), {'from': _pool_owner})
    # _pool_owner registers _pool_name POOL_NAME_LIONFURY at the UnderwriterPoolDaoContract
    _pool_name = POOL_NAME_LIONFURY
    UnderwriterPoolDaoContract.register_pool(
        False, Lend_token.address, _pool_name, Web3.toWei(50, 'ether'), 1, 1, 90, {'from': _pool_owner, 'gas': 1200000})
    # get InterestPoolContract
    UnderwriterPoolContract = get_UnderwriterPool_contract(address=UnderwriterPoolDaoContract.pools__address_(_pool_name, {'from': anyone}))
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
    # _pool_owner buys UNDWRITER_POOL_DAO_MIN_MFT_FEE LST_token from a 3rd party exchange
    LST_token.transfer(_pool_owner, Web3.toWei(INTEREST_POOL_DAO_MIN_MFT_FEE, 'ether'), {'from': Whale})
    # _pool_owner authorizes CurrencyDaoContract to spend UNDWRITER_POOL_DAO_MIN_MFT_FEE LST_token
    LST_token.approve(CurrencyDaoContract.address, Web3.toWei(INTEREST_POOL_DAO_MIN_MFT_FEE, 'ether'), {'from': _pool_owner})
    # set support for MFT H20
    UnderwriterPoolContract.support_mft(H20, Borrow_token.address, STRIKE_125,
        Web3.toWei(0.025, 'ether'), Web3.toWei(0.05, 'ether'), {'from': _pool_owner, 'gas': 2500000})
    # get _shield_market_hash
    _shield_market_hash = MarketDaoContract.shield_market_hash(Lend_token.address, H20, Borrow_token.address, STRIKE_125, {'from': anyone})
    _u_id = UnderwriterPoolContract.markets__u_id(_shield_market_hash, {'from': anyone})
    _i_id = UnderwriterPoolContract.markets__i_id(_shield_market_hash, {'from': anyone})
    _s_id = UnderwriterPoolContract.markets__s_id(_shield_market_hash, {'from': anyone})
    # _pool_owner contributes 500 L_lend_token to his own pool _pool_name
    UnderwriterPoolContract.contribute(Web3.toWei(500, 'ether'), {'from': _pool_owner, 'gas': 300000})
    assert UnderwriterPoolContract.i_token_balance(H20, Borrow_token.address, STRIKE_125, {'from': anyone}) == 0
    assert I_lend_token.balanceOf(UnderwriterPoolContract.address, _i_id, {'from': anyone}) == 0
    assert UnderwriterPoolContract.s_token_balance(H20, Borrow_token.address, STRIKE_125, {'from': anyone}) == 0
    assert S_lend_token.balanceOf(UnderwriterPoolContract.address, _s_id, {'from': anyone}) == 0
    assert UnderwriterPoolContract.u_token_balance(H20, Borrow_token.address, STRIKE_125, {'from': anyone}) == 0
    assert U_lend_token.balanceOf(UnderwriterPoolContract.address, _u_id, {'from': anyone}) == 0
    assert UnderwriterPoolContract.total_u_token_balance({'from': anyone}) == 0
    assert U_lend_token.totalBalanceOf(UnderwriterPoolContract.address, {'from': anyone}) == 0
    assert UnderwriterPoolContract.l_token_balance({'from': anyone}) == Web3.toWei(500, 'ether')
    assert UnderwriterPoolContract.total_active_contributions({'from': anyone}) == Web3.toWei(500, 'ether')
    # _pool_owner increments ITokens by converting 300 L_lend_token to 300 ITokens and 300 FTokens
    UnderwriterPoolContract.increment_s_tokens(H20, Borrow_token.address, STRIKE_125, Web3.toWei(300, 'ether'), {'from': _pool_owner, 'gas': 400000})
    assert UnderwriterPoolContract.i_token_balance(H20, Borrow_token.address, STRIKE_125, {'from': anyone}) == Web3.toWei(300, 'ether')
    assert I_lend_token.balanceOf(UnderwriterPoolContract.address, _i_id, {'from': anyone}) == Web3.toWei(300, 'ether')
    assert UnderwriterPoolContract.s_token_balance(H20, Borrow_token.address, STRIKE_125, {'from': anyone}) == Web3.toWei(300, 'ether')
    assert S_lend_token.balanceOf(UnderwriterPoolContract.address, _s_id, {'from': anyone}) == Web3.toWei(300, 'ether')
    assert UnderwriterPoolContract.u_token_balance(H20, Borrow_token.address, STRIKE_125, {'from': anyone}) == Web3.toWei(300, 'ether')
    assert U_lend_token.balanceOf(UnderwriterPoolContract.address, _u_id, {'from': anyone}) == Web3.toWei(300, 'ether')
    assert UnderwriterPoolContract.total_u_token_balance({'from': anyone}) == Web3.toWei(300, 'ether')
    assert U_lend_token.totalBalanceOf(UnderwriterPoolContract.address, {'from': anyone}) == Web3.toWei(300, 'ether')
    assert UnderwriterPoolContract.l_token_balance({'from': anyone}) == Web3.toWei(200, 'ether')
    assert UnderwriterPoolContract.total_active_contributions({'from': anyone}) == Web3.toWei(500, 'ether')


def test_purchase_s_tokens(accounts,
        Whale, Deployer, Governor,
        LST_token, Lend_token, Borrow_token,
        get_ERC20_contract, get_ERC20_Pool_Token_contract, get_MFT_contract,
        get_PoolNameRegistry_contract, get_MarketDao_contract, get_UnderwriterPool_contract,
        get_CurrencyDao_contract, get_UnderwriterPoolDao_contract,
        ProtocolDaoContract):
    anyone = accounts[-1]
    # get CurrencyDaoContract
    CurrencyDaoContract = get_CurrencyDao_contract(address=ProtocolDaoContract.daos(PROTOCOL_CONSTANTS['DAO_CURRENCY']))
    # get UnderwriterPoolDaoContract
    UnderwriterPoolDaoContract = get_UnderwriterPoolDao_contract(address=ProtocolDaoContract.daos(PROTOCOL_CONSTANTS['DAO_UNDERWRITER_POOL']))
    # get PoolNameRegistryContract
    PoolNameRegistryContract = get_PoolNameRegistry_contract(address=ProtocolDaoContract.registries(PROTOCOL_CONSTANTS['REGISTRY_POOL_NAME']))
    # get MarketDaoContract
    MarketDaoContract = get_MarketDao_contract(address=ProtocolDaoContract.daos(PROTOCOL_CONSTANTS['DAO_MARKET']))
    # assign one of the accounts as _pool_owner
    _pool_owner = accounts[6]
    # assign one of the accounts as _borrower
    _borrower = accounts[7]
    # initialize PoolNameRegistryContract
    ProtocolDaoContract.initialize_pool_name_registry(Web3.toWei(POOL_NAME_REGISTRATION_MIN_STAKE_LST, 'ether'), {'from': Deployer})
    # initialize CurrencyDaoContract
    ProtocolDaoContract.initialize_currency_dao({'from': Deployer})
    # initialize UnderwriterPoolDaoContract
    ProtocolDaoContract.initialize_underwriter_pool_dao({'from': Deployer})
    # initialize MarketDaoContract
    ProtocolDaoContract.initialize_market_dao({'from': Deployer})
    # initialize ShieldPayoutDaoContract
    ProtocolDaoContract.initialize_shield_payout_dao({'from': Deployer})
    # set support for Lend_token
    ProtocolDaoContract.set_token_support(Lend_token.address, True, {'from': Governor, 'gas': 2000000})
    # set support for Borrow_token
    ProtocolDaoContract.set_token_support(Borrow_token.address, True, {'from': Governor})
    # get L_Lend_token
    L_lend_token = get_ERC20_contract(address=CurrencyDaoContract.token_addresses__l(Lend_token.address, {'from': anyone}))
    # get I_lend_token
    I_lend_token = get_MFT_contract(address=CurrencyDaoContract.token_addresses__i(Lend_token.address, {'from': anyone}))
    # get S_lend_token
    S_lend_token = get_MFT_contract(address=CurrencyDaoContract.token_addresses__s(Lend_token.address, {'from': anyone}))
    # get U_Lend_token
    U_lend_token = get_MFT_contract(address=CurrencyDaoContract.token_addresses__u(Lend_token.address, {'from': anyone}))
    # _pool_owner buys 1000 lend token from a 3rd party exchange
    Lend_token.transfer(_pool_owner, Web3.toWei(1000, 'ether'), {'from': Whale})
    # _pool_owner authorizes CurrencyDaoContract to spend 800 Lend_token
    Lend_token.approve(CurrencyDaoContract.address, Web3.toWei(800, 'ether'), {'from': _pool_owner})
    # _pool_owner wraps 800 Lend_token to L_lend_token
    CurrencyDaoContract.wrap(Lend_token.address, Web3.toWei(800, 'ether'), {'from': _pool_owner, 'gas': 145000})
    # _pool_owner buys POOL_NAME_REGISTRATION_MIN_STAKE_LST LST_token from a 3rd party exchange
    LST_token.transfer(_pool_owner, Web3.toWei(POOL_NAME_REGISTRATION_MIN_STAKE_LST, 'ether'), {'from': Whale})
    # _pool_owner authorizes CurrencyDaoContract to spend POOL_NAME_REGISTRATION_MIN_STAKE_LST LST_token
    LST_token.approve(CurrencyDaoContract.address, Web3.toWei(POOL_NAME_REGISTRATION_MIN_STAKE_LST, 'ether'), {'from': _pool_owner})
    # _pool_owner registers _pool_name POOL_NAME_LIONFURY at the UnderwriterPoolDaoContract
    _pool_name = POOL_NAME_LIONFURY
    UnderwriterPoolDaoContract.register_pool(
        False, Lend_token.address, _pool_name, Web3.toWei(50, 'ether'), 1, 1, 90, {'from': _pool_owner, 'gas': 1200000})
    # get InterestPoolContract
    UnderwriterPoolContract = get_UnderwriterPool_contract(address=UnderwriterPoolDaoContract.pools__address_(_pool_name, {'from': anyone}))
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
    # _pool_owner buys UNDWRITER_POOL_DAO_MIN_MFT_FEE LST_token from a 3rd party exchange
    LST_token.transfer(_pool_owner, Web3.toWei(INTEREST_POOL_DAO_MIN_MFT_FEE, 'ether'), {'from': Whale})
    # _pool_owner authorizes CurrencyDaoContract to spend UNDWRITER_POOL_DAO_MIN_MFT_FEE LST_token
    LST_token.approve(CurrencyDaoContract.address, Web3.toWei(INTEREST_POOL_DAO_MIN_MFT_FEE, 'ether'), {'from': _pool_owner})
    # set support for MFT H20
    UnderwriterPoolContract.support_mft(H20, Borrow_token.address, STRIKE_125,
        Web3.toWei(0.025, 'ether'), Web3.toWei(0.05, 'ether'), {'from': _pool_owner, 'gas': 2500000})
    # get _shield_market_hash
    _shield_market_hash = MarketDaoContract.shield_market_hash(Lend_token.address, H20, Borrow_token.address, STRIKE_125, {'from': anyone})
    _u_id = UnderwriterPoolContract.markets__u_id(_shield_market_hash, {'from': anyone})
    _i_id = UnderwriterPoolContract.markets__i_id(_shield_market_hash, {'from': anyone})
    _s_id = UnderwriterPoolContract.markets__s_id(_shield_market_hash, {'from': anyone})
    # _pool_owner contributes 500 L_lend_token to his own pool _pool_name
    UnderwriterPoolContract.contribute(Web3.toWei(500, 'ether'), {'from': _pool_owner, 'gas': 300000})
    # _pool_owner increments ITokens by converting 300 L_lend_token to 300 ITokens and 300 FTokens
    UnderwriterPoolContract.increment_s_tokens(H20, Borrow_token.address, STRIKE_125, Web3.toWei(300, 'ether'), {'from': _pool_owner, 'gas': 400000})
    # _pool_owner increments ITokens by converting 300 L_lend_token to 300 ITokens and 300 FTokens
    assert UnderwriterPoolContract.i_token_balance(H20, Borrow_token.address, STRIKE_125, {'from': anyone}) == Web3.toWei(300, 'ether')
    assert I_lend_token.balanceOf(UnderwriterPoolContract.address, _i_id, {'from': anyone}) == Web3.toWei(300, 'ether')
    assert UnderwriterPoolContract.s_token_balance(H20, Borrow_token.address, STRIKE_125, {'from': anyone}) == Web3.toWei(300, 'ether')
    assert S_lend_token.balanceOf(UnderwriterPoolContract.address, _s_id, {'from': anyone}) == Web3.toWei(300, 'ether')
    assert UnderwriterPoolContract.u_token_balance(H20, Borrow_token.address, STRIKE_125, {'from': anyone}) == Web3.toWei(300, 'ether')
    assert U_lend_token.balanceOf(UnderwriterPoolContract.address, _u_id, {'from': anyone}) == Web3.toWei(300, 'ether')
    assert UnderwriterPoolContract.total_u_token_balance({'from': anyone}) == Web3.toWei(300, 'ether')
    assert U_lend_token.totalBalanceOf(UnderwriterPoolContract.address, {'from': anyone}) == Web3.toWei(300, 'ether')
    assert UnderwriterPoolContract.l_token_balance({'from': anyone}) == Web3.toWei(200, 'ether')
    assert UnderwriterPoolContract.total_active_contributions({'from': anyone}) == Web3.toWei(500, 'ether')
    # _pool_owner sets s_cost_per_day for H20 to 0.01 l_tokens
    UnderwriterPoolContract.set_s_cost_per_day(H20, Borrow_token.address, STRIKE_125, Web3.toWei(.1, 'ether'), {'from': _pool_owner, 'gas': 400000})
    # _borrower buys 1 Lend_token from a 3rd party exchange
    Lend_token.transfer(_borrower, Web3.toWei(1, 'ether'), {'from': Whale})
    # verify Lend_token balance of _borrower
    assert Lend_token.balanceOf(_borrower, {'from': anyone}) == Web3.toWei(1, 'ether')
    # _borrower authorizes CurrencyDaoContract to spend 1 Lend_token
    Lend_token.approve(CurrencyDaoContract.address, Web3.toWei(1, 'ether'), {'from': _borrower})
    # _borrower wraps 1 Lend_token to L_lend_token
    CurrencyDaoContract.wrap(Lend_token.address, Web3.toWei(1, 'ether'), {'from': _borrower, 'gas': 145000})
    # verify L_lend_token balance of _borrower
    assert L_lend_token.balanceOf(_borrower, {'from': anyone}) == Web3.toWei(1, 'ether')
    # _borrower authorizes UnderwriterPoolContract to spend 1 L_lend_token
    L_lend_token.approve(UnderwriterPoolContract.address, Web3.toWei(1, 'ether'), {'from': _borrower})
    # _borrower purchases 10 s_tokens from UnderwriterPoolContract
    UnderwriterPoolContract.purchase_s_tokens(H20, Borrow_token.address, STRIKE_125, Web3.toWei(1, 'ether'), {'from': _borrower, 'gas': 4000000})
    # verify UnderwriterPoolContract balances of l, i, s tokens
    assert UnderwriterPoolContract.i_token_balance(H20, Borrow_token.address, STRIKE_125, {'from': anyone}) == Web3.toWei(300, 'ether')
    assert I_lend_token.balanceOf(UnderwriterPoolContract.address, _i_id, {'from': anyone}) == Web3.toWei(300, 'ether')
    assert UnderwriterPoolContract.s_token_balance(H20, Borrow_token.address, STRIKE_125, {'from': anyone}) == Web3.toWei(290, 'ether')
    assert S_lend_token.balanceOf(UnderwriterPoolContract.address, _s_id, {'from': anyone}) == Web3.toWei(290, 'ether')
    assert UnderwriterPoolContract.u_token_balance(H20, Borrow_token.address, STRIKE_125, {'from': anyone}) == Web3.toWei(300, 'ether')
    assert U_lend_token.balanceOf(UnderwriterPoolContract.address, _u_id, {'from': anyone}) == Web3.toWei(300, 'ether')
    assert UnderwriterPoolContract.total_u_token_balance({'from': anyone}) == Web3.toWei(300, 'ether')
    assert U_lend_token.totalBalanceOf(UnderwriterPoolContract.address, {'from': anyone}) == Web3.toWei(300, 'ether')
    assert UnderwriterPoolContract.l_token_balance({'from': anyone}) == Web3.toWei(200.99, 'ether')
    assert UnderwriterPoolContract.total_active_contributions({'from': anyone}) == Web3.toWei(500.99, 'ether')
    # verify _borrower balance of s tokens
    assert S_lend_token.balanceOf(_borrower, _s_id, {'from': anyone}) == Web3.toWei(10, 'ether')
