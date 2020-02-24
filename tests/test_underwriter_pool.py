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


# def test_increment_i_tokens(accounts,
#         Whale, Deployer, Governor,
#         LST_token, Lend_token, Borrow_token,
#         get_ERC20_contract, get_ERC20_Pool_Token_contract, get_MFT_contract,
#         get_PoolNameRegistry_contract, get_MarketDao_contract, get_UnderwriterPool_contract,
#         get_CurrencyDao_contract, get_UnderwriterPoolDao_contract,
#         ProtocolDaoContract):
#     anyone = accounts[-1]
#     # get CurrencyDaoContract
#     CurrencyDaoContract = get_CurrencyDao_contract(address=ProtocolDaoContract.daos(PROTOCOL_CONSTANTS['DAO_CURRENCY']))
#     # get UnderwriterPoolDaoContract
#     UnderwriterPoolDaoContract = get_UnderwriterPoolDao_contract(address=ProtocolDaoContract.daos(PROTOCOL_CONSTANTS['DAO_UNDERWRITER_POOL']))
#     # get PoolNameRegistryContract
#     PoolNameRegistryContract = get_PoolNameRegistry_contract(address=ProtocolDaoContract.registries(PROTOCOL_CONSTANTS['REGISTRY_POOL_NAME']))
#     # get MarketDaoContract
#     MarketDaoContract = get_MarketDao_contract(address=ProtocolDaoContract.daos(PROTOCOL_CONSTANTS['DAO_MARKET']))
#     # assign one of the accounts as _pool_owner
#     _pool_owner = accounts[6]
#     # initialize PoolNameRegistryContract
#     ProtocolDaoContract.initialize_pool_name_registry(Web3.toWei(POOL_NAME_REGISTRATION_MIN_STAKE_LST, 'ether'), {'from': Deployer})
#     # initialize CurrencyDaoContract
#     ProtocolDaoContract.initialize_currency_dao({'from': Deployer})
#     # initialize UnderwriterPoolDaoContract
#     ProtocolDaoContract.initialize_underwriter_pool_dao({'from': Deployer})
#     # initialize MarketDaoContract
#     ProtocolDaoContract.initialize_market_dao({'from': Deployer})
#     # initialize ShieldPayoutDaoContract
#     ProtocolDaoContract.initialize_shield_payout_dao({'from': Deployer})
#     # set support for Lend_token
#     ProtocolDaoContract.set_token_support(Lend_token.address, True, {'from': Governor, 'gas': 2000000})
#     # set support for Borrow_token
#     ProtocolDaoContract.set_token_support(Borrow_token.address, True, {'from': Governor})
#     # get L_Lend_token
#     L_lend_token = get_ERC20_contract(address=CurrencyDaoContract.token_addresses__l(Lend_token.address, {'from': anyone}))
#     # get F_Lend_token
#     F_lend_token = get_MFT_contract(address=CurrencyDaoContract.token_addresses__f(Lend_token.address, {'from': anyone}))
#     # get I_lend_token
#     I_lend_token = get_MFT_contract(address=CurrencyDaoContract.token_addresses__i(Lend_token.address, {'from': anyone}))
#     # _pool_owner buys 1000 lend token from a 3rd party exchange
#     Lend_token.transfer(_pool_owner, Web3.toWei(1000, 'ether'), {'from': Whale})
#     # _pool_owner authorizes CurrencyDaoContract to spend 800 Lend_token
#     Lend_token.approve(CurrencyDaoContract.address, Web3.toWei(800, 'ether'), {'from': _pool_owner})
#     # _pool_owner wraps 800 Lend_token to L_lend_token
#     CurrencyDaoContract.wrap(Lend_token.address, Web3.toWei(800, 'ether'), {'from': _pool_owner, 'gas': 145000})
#     # _pool_owner buys POOL_NAME_REGISTRATION_MIN_STAKE_LST LST_token from a 3rd party exchange
#     LST_token.transfer(_pool_owner, Web3.toWei(POOL_NAME_REGISTRATION_MIN_STAKE_LST, 'ether'), {'from': Whale})
#     # _pool_owner authorizes CurrencyDaoContract to spend POOL_NAME_REGISTRATION_MIN_STAKE_LST LST_token
#     LST_token.approve(CurrencyDaoContract.address, Web3.toWei(POOL_NAME_REGISTRATION_MIN_STAKE_LST, 'ether'), {'from': _pool_owner})
#     # _pool_owner registers _pool_name POOL_NAME_LIONFURY at the UnderwriterPoolDaoContract
#     _pool_name = POOL_NAME_LIONFURY
#     UnderwriterPoolDaoContract.register_pool(
#         False, Lend_token.address, _pool_name, Web3.toWei(50, 'ether'), 1, 1, 90, {'from': _pool_owner, 'gas': 1200000})
#     # get InterestPoolContract
#     UnderwriterPoolContract = get_UnderwriterPool_contract(address=UnderwriterPoolDaoContract.pools__address_(_pool_name, {'from': anyone}))
#     ProtocolDaoContract.set_minimum_mft_fee(
#         PROTOCOL_CONSTANTS['DAO_UNDERWRITER_POOL'],
#         Web3.toWei(INTEREST_POOL_DAO_MIN_MFT_FEE, 'ether'),
#         {'from': Governor})
#     # set MFT multiplier
#     ProtocolDaoContract.set_fee_multiplier_per_mft_count(
#         PROTOCOL_CONSTANTS['DAO_UNDERWRITER_POOL'], Web3.toWei(0, 'ether'),
#         Web3.toWei(INTEREST_POOL_DAO_FEE_MULTIPLIER_PER_MFT_COUNT, 'ether'),
#         {'from': Governor, 'gas': 75000})
#     # set support for expiry H20
#     ProtocolDaoContract.set_expiry_support(H20, "H20", True, {'from': Governor})
#     # _pool_owner buys UNDWRITER_POOL_DAO_MIN_MFT_FEE LST_token from a 3rd party exchange
#     LST_token.transfer(_pool_owner, Web3.toWei(INTEREST_POOL_DAO_MIN_MFT_FEE, 'ether'), {'from': Whale})
#     # _pool_owner authorizes CurrencyDaoContract to spend UNDWRITER_POOL_DAO_MIN_MFT_FEE LST_token
#     LST_token.approve(CurrencyDaoContract.address, Web3.toWei(INTEREST_POOL_DAO_MIN_MFT_FEE, 'ether'), {'from': _pool_owner})
#     # set support for MFT H20
#     UnderwriterPoolContract.support_mft(H20, Borrow_token.address, STRIKE_125,
#         Web3.toWei(0.025, 'ether'), Web3.toWei(0.05, 'ether'), {'from': _pool_owner, 'gas': 2500000})
#     # get _shield_market_hash
#     _shield_market_hash = MarketDaoContract.shield_market_hash(Lend_token.address, H20, Borrow_token.address, STRIKE_125, {'from': anyone})
#     _u_id = UnderwriterPoolContract.markets__u_id(_shield_market_hash, {'from': anyone})
#     _i_id = UnderwriterPoolContract.markets__i_id(_shield_market_hash, {'from': anyone})
#     _s_id = UnderwriterPoolContract.markets__s_id(_shield_market_hash, {'from': anyone})
#     # _pool_owner contributes 500 L_lend_token to his own pool _pool_name
#     UnderwriterPoolContract.contribute(Web3.toWei(500, 'ether'), {'from': _pool_owner, 'gas': 300000})
#     assert UnderwriterPoolContract.i_token_balance(H20, Borrow_token.address, STRIKE_125, {'from': anyone}) == 0
#     assert I_lend_token.balanceOf(UnderwriterPoolContract.address, _i_id, {'from': anyone}) == 0
#     assert UnderwriterPoolContract.u_token_balance(H20, Borrow_token.address, STRIKE_125, {'from': anyone}) == 0
#     assert U_lend_token.balanceOf(UnderwriterPoolContract.address, _u_id, {'from': anyone}) == 0
#     assert UnderwriterPoolContract.s_token_balance(H20, Borrow_token.address, STRIKE_125, {'from': anyone}) == 0
#     assert S_lend_token.balanceOf(UnderwriterPoolContract.address, _s_id, {'from': anyone}) == 0
#     assert UnderwriterPoolContract.total_u_token_balance({'from': anyone}) == 0
#     assert U_lend_token.totalBalanceOf(UnderwriterPoolContract.address, {'from': anyone}) == 0
#     assert UnderwriterPoolContract.l_token_balance({'from': anyone}) == Web3.toWei(500, 'ether')
#     assert UnderwriterPoolContract.total_active_contributions({'from': anyone}) == Web3.toWei(500, 'ether')
#     # _pool_owner increments ITokens by converting 300 L_lend_token to 300 ITokens and 300 FTokens
#     UnderwriterPoolContract.increment_i_tokens(H20, Web3.toWei(300, 'ether'), {'from': _pool_owner, 'gas': 300000})
#     assert UnderwriterPoolContract.i_token_balance(H20, {'from': anyone}) == Web3.toWei(300, 'ether')
#     assert I_lend_token.balanceOf(UnderwriterPoolContract.address, _i_id, {'from': anyone}) == Web3.toWei(300, 'ether')
#     assert UnderwriterPoolContract.u_token_balance(H20, {'from': anyone}) == Web3.toWei(300, 'ether')
#     assert U_lend_token.balanceOf(UnderwriterPoolContract.address, _u_id, {'from': anyone}) == Web3.toWei(300, 'ether')
#     assert UnderwriterPoolContract.total_u_token_balance({'from': anyone}) == Web3.toWei(300, 'ether')
#     assert UnderwriterPoolContract.s_token_balance(H20, {'from': anyone}) == Web3.toWei(300, 'ether')
#     assert S_lend_token.balanceOf(UnderwriterPoolContract.address, _s_id, {'from': anyone}) == Web3.toWei(300, 'ether')
#     assert U_lend_token.totalBalanceOf(UnderwriterPoolContract.address, {'from': anyone}) == Web3.toWei(300, 'ether')
#     assert UnderwriterPoolContract.l_token_balance({'from': anyone}) == Web3.toWei(200, 'ether')
#     assert UnderwriterPoolContract.total_active_contributions({'from': anyone}) == Web3.toWei(500, 'ether')


# def test_purchase_i_currency(w3, get_contract, get_logs,
#         LST_token, Lend_token, Borrow_token, Malicious_token,
#         ERC20_library, ERC1155_library,
#         CurrencyPool_library, CurrencyDao,
#         InterestPool_library, InterestPoolDao,
#         UnderwriterPool_library, UnderwriterPoolDao,
#         CollateralAuctionGraph_Library, CollateralAuctionDao,
#         ShieldPayoutDao,
#         PositionRegistry,
#         PriceFeed,
#         PriceOracle,
#         MarketDao
#     ):
#     owner = w3.eth.accounts[0]
#     _initialize_all_daos(owner, w3,
#         LST_token, Lend_token, Borrow_token,
#         ERC20_library, ERC1155_library,
#         CurrencyPool_library, CurrencyDao,
#         InterestPool_library, InterestPoolDao,
#         UnderwriterPool_library, UnderwriterPoolDao,
#         CollateralAuctionGraph_Library, CollateralAuctionDao,
#         ShieldPayoutDao,
#         PositionRegistry,
#         PriceOracle,
#         MarketDao
#     )
#     # set_offer_registration_fee_lookup()
#     _minimum_fee = 100
#     _minimum_interval = 10
#     _fee_multiplier = 2000
#     _fee_multiplier_decimals = 1000
#     tx_3_hash = UnderwriterPoolDao.set_offer_registration_fee_lookup(_minimum_fee,
#         _minimum_interval, _fee_multiplier, _fee_multiplier_decimals,
#         transact={'from': owner})
#     tx_3_receipt = w3.eth.waitForTransactionReceipt(tx_3_hash)
#     assert tx_3_receipt['status'] == 1
#     # set_currency_support for Lend_token in CurrencyDao
#     tx_4_hash = CurrencyDao.set_currency_support(Lend_token.address, True,
#         transact={'from': owner, 'gas': 1570000})
#     tx_4_receipt = w3.eth.waitForTransactionReceipt(tx_4_hash)
#     assert tx_4_receipt['status'] == 1
#     # set_currency_support for Borrow_token in CurrencyDao
#     tx_5_hash = CurrencyDao.set_currency_support(Borrow_token.address, True,
#         transact={'from': owner, 'gas': 1570000})
#     tx_5_receipt = w3.eth.waitForTransactionReceipt(tx_5_hash)
#     assert tx_5_receipt['status'] == 1
#     # register_pool for Lend_token
#     pool_owner = w3.eth.accounts[1]
#     tx_6_hash = UnderwriterPoolDao.register_pool(Lend_token.address,
#         'Underwriter Pool A', 'UPA', 50,
#         transact={'from': pool_owner, 'gas': 850000})
#     tx_6_receipt = w3.eth.waitForTransactionReceipt(tx_6_hash)
#     assert tx_6_receipt['status'] == 1
#     # get UnderwriterPool contract
#     logs_6 = get_logs(tx_6_hash, UnderwriterPoolDao, "PoolRegistered")
#     _pool_hash = UnderwriterPoolDao.pool_hash(Lend_token.address, logs_6[0].args._pool_address)
#     UnderwriterPool = get_contract(
#         'contracts/templates/UnderwriterPoolTemplate1.v.py',
#         interfaces=['ERC20', 'ERC1155', 'ERC1155TokenReceiver', 'UnderwriterPoolDao'],
#         address=UnderwriterPoolDao.pools__pool_address(_pool_hash)
#     )
#     # get UnderwriterPoolCurrency
#     UnderwriterPoolCurrency = get_contract(
#         'contracts/templates/ERC20Template1.v.py',
#         address=UnderwriterPool.pool_currency_address()
#     )
#     # pool_owner buys LST from a 3rd party
#     LST_token.transfer(pool_owner, 1000 * 10 ** 18, transact={'from': owner})
#     # pool_owner authorizes CurrencyDao to spend LST required for offer_registration_fee
#     tx_7_hash = LST_token.approve(CurrencyDao.address, UnderwriterPoolDao.offer_registration_fee() * (10 ** 18),
#         transact={'from': pool_owner})
#     tx_7_receipt = w3.eth.waitForTransactionReceipt(tx_7_hash)
#     assert tx_7_receipt['status'] == 1
#     # pool_owner registers an expiry : Last Thursday of December 2019, i.e., December 26th, 2019, i.e., Z19
#     _strike_price = 200 * 10 ** 18
#     tx_8_hash = UnderwriterPool.register_expiry(Z19, Borrow_token.address,
#         _strike_price, transact={'from': pool_owner, 'gas': 2600000})
#     tx_8_receipt = w3.eth.waitForTransactionReceipt(tx_8_hash)
#     assert tx_8_receipt['status'] == 1
#     # get L_token
#     L_token_address = CurrencyDao.currencies__l_currency_address(Lend_token.address)
#     L_token = get_contract(
#         'contracts/templates/ERC20Template1.v.py',
#         address=L_token_address
#     )
#     # assign one of the accounts as a lender
#     lender = w3.eth.accounts[2]
#     # lender buys 1000 lend token from a 3rd party exchange
#     tx_9_hash = Lend_token.transfer(lender, 1000 * 10 ** 18, transact={'from': owner})
#     tx_9_receipt = w3.eth.waitForTransactionReceipt(tx_9_hash)
#     assert tx_9_receipt['status'] == 1
#     # lender authorizes CurrencyDao to spend 800 lend currency
#     tx_10_hash = Lend_token.approve(CurrencyDao.address, 800 * (10 ** 18),
#         transact={'from': lender})
#     tx_10_receipt = w3.eth.waitForTransactionReceipt(tx_10_hash)
#     assert tx_10_receipt['status'] == 1
#     # lender deposits Lend_token to Currency Pool and gets l_tokens
#     tx_11_hash = CurrencyDao.currency_to_l_currency(Lend_token.address, 600 * 10 ** 18,
#         transact={'from': lender, 'gas': 200000})
#     tx_11_receipt = w3.eth.waitForTransactionReceipt(tx_11_hash)
#     assert tx_11_receipt['status'] == 1
#     # lender purchases UnderwriterPoolCurrency for 600 L_tokens
#     # lender gets 30000 UnderwriterPoolCurrency tokens
#     # 600 L_tokens are deposited into UnderwriterPool account
#     tx_12_hash = UnderwriterPool.purchase_pool_currency(600 * 10 ** 18, transact={'from': lender})
#     tx_12_receipt = w3.eth.waitForTransactionReceipt(tx_12_hash)
#     assert tx_12_receipt['status'] == 1
#     assert UnderwriterPool.l_currency_balance() == 600 * 10 ** 18
#     multi_fungible_addresses = CurrencyDao.multi_fungible_addresses(Lend_token.address)
#     _s_hash = UnderwriterPoolDao.multi_fungible_currency_hash(
#         multi_fungible_addresses[3], Lend_token.address, Z19,
#         Borrow_token.address, _strike_price)
#     # pool_owner initiates offer of 400 I_tokens from the UnderwriterPool
#     # 400 L_tokens burned from UnderwriterPool account
#     # 400 I_tokens, 2 S_tokens, and 2 U_tokens minted to UnderwriterPool account
#     tx_14_hash = UnderwriterPool.increment_i_currency_supply(
#         Z19, Borrow_token.address, _strike_price, 400 * 10 ** 18,
#         transact={'from': pool_owner, 'gas': 600000})
#     tx_14_receipt = w3.eth.waitForTransactionReceipt(tx_14_hash)
#     assert tx_14_receipt['status'] == 1
#     # get I_token
#     I_token = get_contract(
#         'contracts/templates/ERC1155Template2.v.py',
#         interfaces=['ERC1155TokenReceiver'],
#         address=CurrencyDao.currencies__i_currency_address(Lend_token.address)
#     )
#     # assign one of the accounts as a High_Risk_Insurer
#     High_Risk_Insurer = w3.eth.accounts[2]
#     # verify UnderwriterPool balances of l, i, s, u tokens
#     assert UnderwriterPool.l_currency_balance() == 200 * 10 ** 18
#     assert UnderwriterPool.i_currency_balance(Z19, Borrow_token.address, _strike_price) == 400 * 10 ** 18
#     assert UnderwriterPool.s_currency_balance(Z19, Borrow_token.address, _strike_price) == 2 * 10 ** 18
#     assert UnderwriterPool.u_currency_balance(Z19, Borrow_token.address, _strike_price) == 2 * 10 ** 18
#     # verify High_Risk_Insurer balance of i tokens
#     _expiry_hash = UnderwriterPool.expiry_hash(Z19, Borrow_token.address,
#         _strike_price)
#     assert I_token.balanceOf(High_Risk_Insurer, UnderwriterPool.expiries__i_currency_id(_expiry_hash)) == 0
#     # High_Risk_Insurer purchases 50 i_tokens from UnderwriterPool
#     tx_15_hash = UnderwriterPool.purchase_i_currency(Z19, Borrow_token.address,
#         _strike_price, 50 * 10 ** 18, 0, transact={'from': High_Risk_Insurer})
#     tx_15_receipt = w3.eth.waitForTransactionReceipt(tx_15_hash)
#     assert tx_15_receipt['status'] == 1
#     # verify UnderwriterPool balances of l, i, s, u tokens
#     assert UnderwriterPool.l_currency_balance() == 200 * 10 ** 18
#     assert UnderwriterPool.i_currency_balance(Z19, Borrow_token.address, _strike_price) == 350 * 10 ** 18
#     assert UnderwriterPool.s_currency_balance(Z19, Borrow_token.address, _strike_price) == 2 * 10 ** 18
#     assert UnderwriterPool.u_currency_balance(Z19, Borrow_token.address, _strike_price) == 2 * 10 ** 18
#     # verify High_Risk_Insurer balance of i tokens
#     assert I_token.balanceOf(High_Risk_Insurer, UnderwriterPool.expiries__i_currency_id(_expiry_hash)) == 50 * 10 ** 18
#
#
# def test_purchase_s_currency(w3, get_contract, get_logs,
#         LST_token, Lend_token, Borrow_token, Malicious_token,
#         ERC20_library, ERC1155_library,
#         CurrencyPool_library, CurrencyDao,
#         InterestPool_library, InterestPoolDao,
#         UnderwriterPool_library, UnderwriterPoolDao,
#         CollateralAuctionGraph_Library, CollateralAuctionDao,
#         ShieldPayoutDao,
#         PositionRegistry,
#         PriceFeed,
#         PriceOracle,
#         MarketDao
#     ):
#     owner = w3.eth.accounts[0]
#     _initialize_all_daos(owner, w3,
#         LST_token, Lend_token, Borrow_token,
#         ERC20_library, ERC1155_library,
#         CurrencyPool_library, CurrencyDao,
#         InterestPool_library, InterestPoolDao,
#         UnderwriterPool_library, UnderwriterPoolDao,
#         CollateralAuctionGraph_Library, CollateralAuctionDao,
#         ShieldPayoutDao,
#         PositionRegistry,
#         PriceOracle,
#         MarketDao
#     )
#     # set_offer_registration_fee_lookup()
#     _minimum_fee = 100
#     _minimum_interval = 10
#     _fee_multiplier = 2000
#     _fee_multiplier_decimals = 1000
#     tx_3_hash = UnderwriterPoolDao.set_offer_registration_fee_lookup(_minimum_fee,
#         _minimum_interval, _fee_multiplier, _fee_multiplier_decimals,
#         transact={'from': owner})
#     tx_3_receipt = w3.eth.waitForTransactionReceipt(tx_3_hash)
#     assert tx_3_receipt['status'] == 1
#     # set_currency_support for Lend_token in CurrencyDao
#     tx_4_hash = CurrencyDao.set_currency_support(Lend_token.address, True,
#         transact={'from': owner, 'gas': 1570000})
#     tx_4_receipt = w3.eth.waitForTransactionReceipt(tx_4_hash)
#     assert tx_4_receipt['status'] == 1
#     # set_currency_support for Borrow_token in CurrencyDao
#     tx_5_hash = CurrencyDao.set_currency_support(Borrow_token.address, True,
#         transact={'from': owner, 'gas': 1570000})
#     tx_5_receipt = w3.eth.waitForTransactionReceipt(tx_5_hash)
#     assert tx_5_receipt['status'] == 1
#     # register_pool for Lend_token
#     pool_owner = w3.eth.accounts[1]
#     tx_6_hash = UnderwriterPoolDao.register_pool(Lend_token.address,
#         'Underwriter Pool A', 'UPA', 50,
#         transact={'from': pool_owner, 'gas': 850000})
#     tx_6_receipt = w3.eth.waitForTransactionReceipt(tx_6_hash)
#     assert tx_6_receipt['status'] == 1
#     # get UnderwriterPool contract
#     logs_6 = get_logs(tx_6_hash, UnderwriterPoolDao, "PoolRegistered")
#     _pool_hash = UnderwriterPoolDao.pool_hash(Lend_token.address, logs_6[0].args._pool_address)
#     UnderwriterPool = get_contract(
#         'contracts/templates/UnderwriterPoolTemplate1.v.py',
#         interfaces=['ERC20', 'ERC1155', 'ERC1155TokenReceiver', 'UnderwriterPoolDao'],
#         address=UnderwriterPoolDao.pools__pool_address(_pool_hash)
#     )
#     # get UnderwriterPoolCurrency
#     UnderwriterPoolCurrency = get_contract(
#         'contracts/templates/ERC20Template1.v.py',
#         address=UnderwriterPool.pool_currency_address()
#     )
#     # pool_owner buys LST from a 3rd party
#     LST_token.transfer(pool_owner, 1000 * 10 ** 18, transact={'from': owner})
#     # pool_owner authorizes CurrencyDao to spend LST required for offer_registration_fee
#     tx_7_hash = LST_token.approve(CurrencyDao.address, UnderwriterPoolDao.offer_registration_fee() * (10 ** 18),
#         transact={'from': pool_owner})
#     tx_7_receipt = w3.eth.waitForTransactionReceipt(tx_7_hash)
#     assert tx_7_receipt['status'] == 1
#     # pool_owner registers an expiry : Last Thursday of December 2019, i.e., December 26th, 2019, i.e., Z19
#     _strike_price = 200 * 10 ** 18
#     tx_8_hash = UnderwriterPool.register_expiry(Z19, Borrow_token.address,
#         _strike_price, transact={'from': pool_owner, 'gas': 2600000})
#     tx_8_receipt = w3.eth.waitForTransactionReceipt(tx_8_hash)
#     assert tx_8_receipt['status'] == 1
#     # get L_token
#     L_token_address = CurrencyDao.currencies__l_currency_address(Lend_token.address)
#     L_token = get_contract(
#         'contracts/templates/ERC20Template1.v.py',
#         address=L_token_address
#     )
#     # assign one of the accounts as a lender
#     lender = w3.eth.accounts[2]
#     # lender buys 1000 lend token from a 3rd party exchange
#     tx_9_hash = Lend_token.transfer(lender, 1000 * 10 ** 18, transact={'from': owner})
#     tx_9_receipt = w3.eth.waitForTransactionReceipt(tx_9_hash)
#     assert tx_9_receipt['status'] == 1
#     # lender authorizes CurrencyDao to spend 800 lend currency
#     tx_10_hash = Lend_token.approve(CurrencyDao.address, 1000 * (10 ** 18),
#         transact={'from': lender})
#     tx_10_receipt = w3.eth.waitForTransactionReceipt(tx_10_hash)
#     assert tx_10_receipt['status'] == 1
#     # lender deposits Lend_token to Currency Pool and gets l_tokens
#     tx_11_hash = CurrencyDao.currency_to_l_currency(Lend_token.address, 800 * 10 ** 18,
#         transact={'from': lender, 'gas': 200000})
#     tx_11_receipt = w3.eth.waitForTransactionReceipt(tx_11_hash)
#     assert tx_11_receipt['status'] == 1
#     # lender purchases UnderwriterPoolCurrency for 800 L_tokens
#     # lender gets 40000 UnderwriterPoolCurrency tokens
#     # 800 L_tokens are deposited into UnderwriterPool account
#     tx_12_hash = UnderwriterPool.purchase_pool_currency(800 * 10 ** 18, transact={'from': lender})
#     tx_12_receipt = w3.eth.waitForTransactionReceipt(tx_12_hash)
#     assert tx_12_receipt['status'] == 1
#     assert UnderwriterPool.l_currency_balance() == 800 * 10 ** 18
#     # vefiry shield_currency_price is not set
#     multi_fungible_addresses = CurrencyDao.multi_fungible_addresses(Lend_token.address)
#     _s_hash = UnderwriterPoolDao.multi_fungible_currency_hash(
#         multi_fungible_addresses[3], Lend_token.address, Z19,
#         Borrow_token.address, _strike_price)
#     # pool_owner initiates offer of 600 I_tokens from the UnderwriterPool
#     # 600 L_tokens burned from UnderwriterPool account
#     # 600 I_tokens, 3 S_tokens, and 3 U_tokens minted to UnderwriterPool account
#     tx_14_hash = UnderwriterPool.increment_i_currency_supply(
#         Z19, Borrow_token.address, _strike_price, 600 * 10 ** 18,
#         transact={'from': pool_owner, 'gas': 600000})
#     tx_14_receipt = w3.eth.waitForTransactionReceipt(tx_14_hash)
#     assert tx_14_receipt['status'] == 1
#     # get S_token and U_token
#     S_token = get_contract(
#         'contracts/templates/ERC1155Template2.v.py',
#         interfaces=['ERC1155TokenReceiver'],
#         address=CurrencyDao.currencies__s_currency_address(Lend_token.address)
#     )
#     U_token = get_contract(
#         'contracts/templates/ERC1155Template2.v.py',
#         interfaces=['ERC1155TokenReceiver'],
#         address=CurrencyDao.currencies__u_currency_address(Lend_token.address)
#     )
#     # assign one of the accounts as a High_Risk_Insurer
#     High_Risk_Insurer = w3.eth.accounts[2]
#     # verify UnderwriterPool balances of l, i, s, u tokens
#     assert UnderwriterPool.l_currency_balance() == 200 * 10 ** 18
#     assert UnderwriterPool.i_currency_balance(Z19, Borrow_token.address, _strike_price) == 600 * 10 ** 18
#     assert UnderwriterPool.s_currency_balance(Z19, Borrow_token.address, _strike_price) == 3 * 10 ** 18
#     assert UnderwriterPool.u_currency_balance(Z19, Borrow_token.address, _strike_price) == 3 * 10 ** 18
#     # verify High_Risk_Insurer balance of s and u tokens
#     _expiry_hash = UnderwriterPool.expiry_hash(Z19, Borrow_token.address,
#         _strike_price)
#     assert S_token.balanceOf(High_Risk_Insurer, UnderwriterPool.expiries__i_currency_id(_expiry_hash)) == 0
#     assert U_token.balanceOf(High_Risk_Insurer, UnderwriterPool.expiries__i_currency_id(_expiry_hash)) == 0
#     # High_Risk_Insurer purchases 2 s_tokens from UnderwriterPool
#     tx_15_hash = UnderwriterPool.purchase_s_currency(Z19, Borrow_token.address,
#         _strike_price, 2 * 10 ** 18, 0, transact={'from': High_Risk_Insurer})
#     tx_15_receipt = w3.eth.waitForTransactionReceipt(tx_15_hash)
#     assert tx_15_receipt['status'] == 1
#     # verify UnderwriterPool balances of l, i, s, u tokens
#     assert UnderwriterPool.l_currency_balance() == 200 * 10 ** 18
#     assert UnderwriterPool.i_currency_balance(Z19, Borrow_token.address, _strike_price) == 600 * 10 ** 18
#     assert UnderwriterPool.s_currency_balance(Z19, Borrow_token.address, _strike_price) == 1 * 10 ** 18
#     assert UnderwriterPool.u_currency_balance(Z19, Borrow_token.address, _strike_price) == 3 * 10 ** 18
#     # verify High_Risk_Insurer balance of s and u tokens
#     assert S_token.balanceOf(High_Risk_Insurer, UnderwriterPool.expiries__i_currency_id(_expiry_hash)) == 2 * 10 ** 18
#     assert U_token.balanceOf(High_Risk_Insurer, UnderwriterPool.expiries__i_currency_id(_expiry_hash)) == 0
