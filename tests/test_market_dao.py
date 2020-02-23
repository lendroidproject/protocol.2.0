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


def test_initialize(accounts, Deployer, get_MarketDao_contract, ProtocolDaoContract):
    anyone = accounts[-1]
    MarketDaoContract = get_MarketDao_contract(address=ProtocolDaoContract.daos(PROTOCOL_CONSTANTS['DAO_MARKET']))
    assert not MarketDaoContract.initialized({'from': anyone})
    ProtocolDaoContract.initialize_market_dao({'from': Deployer})
    assert MarketDaoContract.initialized({'from': anyone})


def test_pause_and_unpause(accounts, Deployer, EscapeHatchManager, get_MarketDao_contract, ProtocolDaoContract):
    anyone = accounts[-1]
    MarketDaoContract = get_MarketDao_contract(address=ProtocolDaoContract.daos(PROTOCOL_CONSTANTS['DAO_MARKET']))
    ProtocolDaoContract.initialize_market_dao({'from': Deployer})
    assert not MarketDaoContract.paused({'from': anyone})
    ProtocolDaoContract.toggle_dao_pause(PROTOCOL_CONSTANTS['DAO_MARKET'], True, {'from': EscapeHatchManager})
    assert MarketDaoContract.paused({'from': anyone})
    ProtocolDaoContract.toggle_dao_pause(PROTOCOL_CONSTANTS['DAO_MARKET'], False, {'from': EscapeHatchManager})
    assert not MarketDaoContract.paused({'from': anyone})


def test_pause_failed_when_paused(accounts, assert_tx_failed, Deployer, EscapeHatchManager, get_MarketDao_contract, ProtocolDaoContract):
    anyone = accounts[-1]
    MarketDaoContract = get_MarketDao_contract(address=ProtocolDaoContract.daos(PROTOCOL_CONSTANTS['DAO_MARKET']))
    ProtocolDaoContract.initialize_market_dao({'from': Deployer})
    ProtocolDaoContract.toggle_dao_pause(PROTOCOL_CONSTANTS['DAO_MARKET'], True, {'from': EscapeHatchManager})
    assert_tx_failed(lambda: ProtocolDaoContract.toggle_dao_pause(PROTOCOL_CONSTANTS['DAO_MARKET'], True, {'from': EscapeHatchManager}))


def test_pause_failed_when_uninitialized(accounts, assert_tx_failed, Deployer, EscapeHatchManager, get_MarketDao_contract, ProtocolDaoContract):
    anyone = accounts[-1]
    MarketDaoContract = get_MarketDao_contract(address=ProtocolDaoContract.daos(PROTOCOL_CONSTANTS['DAO_MARKET']))
    assert_tx_failed(lambda: ProtocolDaoContract.toggle_dao_pause(PROTOCOL_CONSTANTS['DAO_MARKET'], True, {'from': EscapeHatchManager}))


def test_pause_failed_when_called_by_non_protocol_dao(accounts, assert_tx_failed, Deployer, EscapeHatchManager, get_MarketDao_contract, ProtocolDaoContract):
    anyone = accounts[-1]
    MarketDaoContract = get_MarketDao_contract(address=ProtocolDaoContract.daos(PROTOCOL_CONSTANTS['DAO_MARKET']))
    ProtocolDaoContract.initialize_market_dao({'from': Deployer})
    # Tx failed
    for account in accounts:
        assert_tx_failed(lambda: MarketDaoContract.pause({'from': account}))


def test_unpause_failed_when_unpaused(accounts, assert_tx_failed, Deployer, EscapeHatchManager, get_MarketDao_contract, ProtocolDaoContract):
    anyone = accounts[-1]
    MarketDaoContract = get_MarketDao_contract(address=ProtocolDaoContract.daos(PROTOCOL_CONSTANTS['DAO_MARKET']))
    ProtocolDaoContract.initialize_market_dao({'from': Deployer})
    assert_tx_failed(lambda: ProtocolDaoContract.toggle_dao_pause(PROTOCOL_CONSTANTS['DAO_MARKET'], False, {'from': EscapeHatchManager}))


def test_unpause_failed_when_uninitialized(accounts, assert_tx_failed, Deployer, EscapeHatchManager, get_MarketDao_contract, ProtocolDaoContract):
    anyone = accounts[-1]
    MarketDaoContract = get_MarketDao_contract(address=ProtocolDaoContract.daos(PROTOCOL_CONSTANTS['DAO_MARKET']))
    assert_tx_failed(lambda: ProtocolDaoContract.toggle_dao_pause(PROTOCOL_CONSTANTS['DAO_MARKET'], False, {'from': EscapeHatchManager}))


def test_unpause_failed_when_called_by_non_protocol_dao(accounts, assert_tx_failed, Deployer, EscapeHatchManager, get_MarketDao_contract, ProtocolDaoContract):
    anyone = accounts[-1]
    MarketDaoContract = get_MarketDao_contract(address=ProtocolDaoContract.daos(PROTOCOL_CONSTANTS['DAO_MARKET']))
    ProtocolDaoContract.initialize_market_dao({'from': Deployer})
    # Tx failed
    for account in accounts:
        assert_tx_failed(lambda: MarketDaoContract.unpause({'from': account}))


def test_open_position_sans_poolshare_model(accounts, get_log_args,
    Whale, Deployer, Governor,
    Lend_token, Borrow_token, LST_token,
    get_ERC20_contract, get_MFT_contract,
    get_PoolNameRegistry_contract, get_PositionRegistry_contract,
    get_CurrencyDao_contract, get_InterestPoolDao_contract,
    get_UnderwriterPoolDao_contract, get_MarketDao_contract,
    get_UnderwriterPool_contract,
    ProtocolDaoContract):
    anyone = accounts[-1]
    # get CurrencyDaoContract
    CurrencyDaoContract = get_CurrencyDao_contract(address=ProtocolDaoContract.daos(PROTOCOL_CONSTANTS['DAO_CURRENCY']))
    # get InterestPoolDaoContract
    InterestPoolDaoContract = get_InterestPoolDao_contract(address=ProtocolDaoContract.daos(PROTOCOL_CONSTANTS['DAO_INTEREST_POOL']))
    # get UnderwriterPoolDaoContract
    UnderwriterPoolDaoContract = get_UnderwriterPoolDao_contract(address=ProtocolDaoContract.daos(PROTOCOL_CONSTANTS['DAO_UNDERWRITER_POOL']))
    # get MarketDaoContract
    MarketDaoContract = get_MarketDao_contract(address=ProtocolDaoContract.daos(PROTOCOL_CONSTANTS['DAO_MARKET']))
    # get PoolNameRegistryContract
    PoolNameRegistryContract = get_PoolNameRegistry_contract(address=ProtocolDaoContract.registries(PROTOCOL_CONSTANTS['REGISTRY_POOL_NAME']))
    # get PositionRegistryContract
    PositionRegistryContract = get_PositionRegistry_contract(address=ProtocolDaoContract.registries(PROTOCOL_CONSTANTS['REGISTRY_POSITION']))
    # assign one of the accounts as _lend_and_borrow_token_holder
    _lend_and_borrow_token_holder = accounts[5]
    # assign one of the accounts as _pool_owner
    _pool_owner = accounts[6]
    # initialize PoolNameRegistryContract
    ProtocolDaoContract.initialize_pool_name_registry(Web3.toWei(POOL_NAME_REGISTRATION_MIN_STAKE_LST, 'ether'), {'from': Deployer})
    # initialize PositionRegistryContract
    ProtocolDaoContract.initialize_position_registry({'from': Deployer})
    # initialize CurrencyDaoContract
    ProtocolDaoContract.initialize_currency_dao({'from': Deployer})
    # initialize InterestPoolDaoContract
    ProtocolDaoContract.initialize_interest_pool_dao({'from': Deployer})
    # initialize UnderwriterPoolDaoContract
    ProtocolDaoContract.initialize_underwriter_pool_dao({'from': Deployer})
    # initialize MarketDaoContract
    ProtocolDaoContract.initialize_market_dao({'from': Deployer})
    # initialize ShieldPayoutDaoContract
    ProtocolDaoContract.initialize_shield_payout_dao({'from': Deployer})
    # set support for Lend_token
    ProtocolDaoContract.set_token_support(Lend_token.address, True, {'from': Governor})
    # set support for Borrow_token
    ProtocolDaoContract.set_token_support(Borrow_token.address, True, {'from': Governor})
    # get L_lend_token
    L_lend_token = get_ERC20_contract(address=CurrencyDaoContract.token_addresses__l(Lend_token.address, {'from': anyone}))
    # get I_lend_token
    I_lend_token = get_MFT_contract(address=CurrencyDaoContract.token_addresses__i(Lend_token.address, {'from': anyone}))
    # get S_lend_token
    S_lend_token = get_MFT_contract(address=CurrencyDaoContract.token_addresses__s(Lend_token.address, {'from': anyone}))
    # get U_lend_token
    U_lend_token = get_MFT_contract(address=CurrencyDaoContract.token_addresses__u(Lend_token.address, {'from': anyone}))
    # get L_borrow_token
    L_borrow_token = get_ERC20_contract(address=CurrencyDaoContract.token_addresses__l(Borrow_token.address, {'from': anyone}))
    # get F_borrow_token
    F_borrow_token = get_MFT_contract(address=CurrencyDaoContract.token_addresses__f(Borrow_token.address, {'from': anyone}))
    # get I_borrow_token
    I_borrow_token = get_MFT_contract(address=CurrencyDaoContract.token_addresses__i(Borrow_token.address, {'from': anyone}))
    # get _loan_market_hash
    _loan_market_hash = MarketDaoContract.loan_market_hash(Lend_token.address, H20, Borrow_token.address, {'from': anyone})
    # get _shield_market_hash
    _shield_market_hash = MarketDaoContract.shield_market_hash(Lend_token.address, H20, Borrow_token.address, STRIKE_125, {'from': anyone})
    # set maximum_market_liability
    ProtocolDaoContract.set_maximum_liability_for_loan_market(Lend_token.address, H20, Borrow_token.address, Web3.toWei(MAX_LIABILITY_CURENCY_MARKET, 'ether'), {'from': Governor})
    assert MarketDaoContract.maximum_market_liabilities(_loan_market_hash, {'from': anyone}) == Web3.toWei(MAX_LIABILITY_CURENCY_MARKET, 'ether')
    # _pool_owner buys POOL_NAME_REGISTRATION_MIN_STAKE_LST LST_token from a 3rd party exchange
    LST_token.transfer(_pool_owner, Web3.toWei(POOL_NAME_REGISTRATION_MIN_STAKE_LST, 'ether'), {'from': Whale})
    # _pool_owner authorizes CurrencyDaoContract to spend POOL_NAME_REGISTRATION_MIN_STAKE_LST LST_token
    LST_token.approve(CurrencyDaoContract.address, Web3.toWei(POOL_NAME_REGISTRATION_MIN_STAKE_LST, 'ether'), {'from': _pool_owner})
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
    # _pool_owner authorizes CurrencyDaoContract to spend INTEREST_POOL_DAO_MIN_MFT_FEE LST_token
    LST_token.approve(CurrencyDaoContract.address, Web3.toWei(INTEREST_POOL_DAO_MIN_MFT_FEE, 'ether'), {'from': _pool_owner})
    # set support for MFT H20
    UnderwriterPool.support_mft(H20, Borrow_token.address, STRIKE_125,
        Web3.toWei(0.025, 'ether'), Web3.toWei(0.05, 'ether'), {'from': _pool_owner, 'gas': 2500000})
    # _lend_and_borrow_token_holder buys 1000 Lend_token from a 3rd party exchange
    Lend_token.transfer(_lend_and_borrow_token_holder, Web3.toWei(1000, 'ether'), {'from': Whale})
    assert Lend_token.balanceOf(_lend_and_borrow_token_holder, {'from': anyone}) == Web3.toWei(1000, 'ether')
    # _lend_and_borrow_token_holder buys 5 Borrow_token from a 3rd party exchange
    Borrow_token.transfer(_lend_and_borrow_token_holder, Web3.toWei(5, 'ether'), {'from': Whale})
    assert Borrow_token.balanceOf(_lend_and_borrow_token_holder, {'from': anyone}) == Web3.toWei(5, 'ether')
    # _lend_and_borrow_token_holder authorizes CurrencyDaoContract to spend 800 Lend_token
    Lend_token.approve(CurrencyDaoContract.address, Web3.toWei(800, 'ether'), {'from': _lend_and_borrow_token_holder})
    assert Lend_token.allowance(_lend_and_borrow_token_holder, CurrencyDaoContract.address, {'from': anyone}) == Web3.toWei(800, 'ether')
    # _lend_and_borrow_token_holder authorizes CurrencyDaoContract to spend 4 Borrow_token
    Borrow_token.approve(CurrencyDaoContract.address, Web3.toWei(4, 'ether'), {'from': _lend_and_borrow_token_holder})
    assert Borrow_token.allowance(_lend_and_borrow_token_holder, CurrencyDaoContract.address, {'from': anyone}) == Web3.toWei(4, 'ether')
    # _lend_and_borrow_token_holder wraps 800 Lend_token to L_lend_token
    CurrencyDaoContract.wrap(Lend_token.address, Web3.toWei(800, 'ether'), {'from': _lend_and_borrow_token_holder, 'gas': 145000})
    assert Lend_token.balanceOf(_lend_and_borrow_token_holder, {'from': anyone}) == Web3.toWei(200, 'ether')
    assert L_lend_token.balanceOf(_lend_and_borrow_token_holder, {'from': anyone}) == Web3.toWei(800, 'ether')
    # _lend_and_borrow_token_holder wraps 4 Borrow_tokens to 4 L_borrow_tokens
    CurrencyDaoContract.wrap(Borrow_token.address, Web3.toWei(4, 'ether'), {'from': _lend_and_borrow_token_holder, 'gas': 145000})
    assert Borrow_token.balanceOf(_lend_and_borrow_token_holder, {'from': anyone}) == Web3.toWei(1, 'ether')
    assert L_borrow_token.balanceOf(_lend_and_borrow_token_holder, {'from': anyone}) == Web3.toWei(4, 'ether')
    # _lend_and_borrow_token_holder splits 500 L_lend_tokens into 500 I_lend_tokens and 500 S_lend_tokens and 500 U_lend_tokens for H20, Borrow_token, and STRIKE_200
    UnderwriterPoolDaoContract.split(Lend_token.address, H20, Borrow_token.address, STRIKE_125, Web3.toWei(500, 'ether'), {'from': _lend_and_borrow_token_holder, 'gas': 1100000})
    assert L_lend_token.balanceOf(_lend_and_borrow_token_holder, {'from': anyone}) == Web3.toWei(300, 'ether')
    _i_lend_id = I_lend_token.id(Lend_token.address, H20, ZERO_ADDRESS, 0, {'from': anyone})
    _s_lend_id = S_lend_token.id(Lend_token.address, H20, Borrow_token.address, STRIKE_125, {'from': anyone})
    _u_lend_id = U_lend_token.id(Lend_token.address, H20, Borrow_token.address, STRIKE_125, {'from': anyone})
    assert I_lend_token.balanceOf(_lend_and_borrow_token_holder, _i_lend_id, {'from': anyone}) == Web3.toWei(500, 'ether')
    assert S_lend_token.balanceOf(_lend_and_borrow_token_holder, _s_lend_id, {'from': anyone}) == Web3.toWei(500, 'ether')
    assert U_lend_token.balanceOf(_lend_and_borrow_token_holder, _u_lend_id, {'from': anyone}) == Web3.toWei(500, 'ether')
    # _lend_and_borrow_token_holder splits 4 L_borrow_tokens into 4 F_borrow_tokens and 4 I_borrow_tokens for H20
    InterestPoolDaoContract.split(Borrow_token.address, H20, Web3.toWei(4, 'ether'), {'from': _lend_and_borrow_token_holder, 'gas': 700000})
    assert L_borrow_token.balanceOf(_lend_and_borrow_token_holder, {'from': anyone}) == 0
    _f_borrow_id = F_borrow_token.id(Borrow_token.address, H20, ZERO_ADDRESS, 0, {'from': anyone})
    _i_borrow_id = I_borrow_token.id(Borrow_token.address, H20, ZERO_ADDRESS, 0, {'from': anyone})
    assert F_borrow_token.balanceOf(_lend_and_borrow_token_holder, _f_borrow_id, {'from': anyone}) == Web3.toWei(4, 'ether')
    assert I_borrow_token.balanceOf(_lend_and_borrow_token_holder, _i_borrow_id, {'from': anyone}) == Web3.toWei(4, 'ether')
    # _lend_and_borrow_token_holder avails a loan for 500 Lend_tokens
    # For this, she places 4 F_borrow_tokens, 500 I_lend_tokens and 500 S_lend_tokens as collateral
    assert PositionRegistryContract.last_position_id({'from': anyone}) == 0
    assert PositionRegistryContract.borrow_position_count(_lend_and_borrow_token_holder, {'from': anyone}) == 0
    PositionRegistryContract.avail_loan(Lend_token.address, H20, Borrow_token.address, STRIKE_125, Web3.toWei(500, 'ether'), {'from': _lend_and_borrow_token_holder, 'gas': 1000000})
    assert Lend_token.balanceOf(_lend_and_borrow_token_holder, {'from': anyone}) == Web3.toWei(700, 'ether')
    assert F_borrow_token.balanceOf(_lend_and_borrow_token_holder, _f_borrow_id, {'from': anyone}) == 0
    assert F_borrow_token.balanceOf(MarketDaoContract.address, _f_borrow_id, {'from': anyone}) == Web3.toWei(4, 'ether')
    assert PositionRegistryContract.last_position_id({'from': anyone}) == 1
    assert PositionRegistryContract.borrow_position_count(_lend_and_borrow_token_holder, {'from': anyone}) == 1
    _position_id = PositionRegistryContract.borrow_position(_lend_and_borrow_token_holder, 1, {'from': anyone})
    assert PositionRegistryContract.positions__id(_position_id, {'from': anyone}) == _position_id
    assert PositionRegistryContract.positions__borrower(_position_id, {'from': anyone}) == _lend_and_borrow_token_holder
    assert PositionRegistryContract.positions__currency(_position_id, {'from': anyone}) == Lend_token.address
    assert PositionRegistryContract.positions__underlying(_position_id, {'from': anyone}) == Borrow_token.address
    assert PositionRegistryContract.positions__strike_price(_position_id, {'from': anyone}) == STRIKE_125
    assert PositionRegistryContract.positions__currency_value(_position_id, {'from': anyone}) == Web3.toWei(500, 'ether')
    assert PositionRegistryContract.positions__underlying_value(_position_id, {'from': anyone}) == Web3.toWei(4, 'ether')
    assert PositionRegistryContract.positions__status(_position_id, {'from': anyone}) == 1


def test_partial_close_position_sans_poolshare_model(accounts, get_log_args,
    Whale, Deployer, Governor,
    Lend_token, Borrow_token, LST_token,
    get_ERC20_contract, get_MFT_contract,
    get_PoolNameRegistry_contract, get_PositionRegistry_contract,
    get_CurrencyDao_contract, get_InterestPoolDao_contract,
    get_UnderwriterPoolDao_contract, get_MarketDao_contract,
    get_UnderwriterPool_contract,
    ProtocolDaoContract):
    anyone = accounts[-1]
    # get CurrencyDaoContract
    CurrencyDaoContract = get_CurrencyDao_contract(address=ProtocolDaoContract.daos(PROTOCOL_CONSTANTS['DAO_CURRENCY']))
    # get InterestPoolDaoContract
    InterestPoolDaoContract = get_InterestPoolDao_contract(address=ProtocolDaoContract.daos(PROTOCOL_CONSTANTS['DAO_INTEREST_POOL']))
    # get UnderwriterPoolDaoContract
    UnderwriterPoolDaoContract = get_UnderwriterPoolDao_contract(address=ProtocolDaoContract.daos(PROTOCOL_CONSTANTS['DAO_UNDERWRITER_POOL']))
    # get MarketDaoContract
    MarketDaoContract = get_MarketDao_contract(address=ProtocolDaoContract.daos(PROTOCOL_CONSTANTS['DAO_MARKET']))
    # get PoolNameRegistryContract
    PoolNameRegistryContract = get_PoolNameRegistry_contract(address=ProtocolDaoContract.registries(PROTOCOL_CONSTANTS['REGISTRY_POOL_NAME']))
    # get PositionRegistryContract
    PositionRegistryContract = get_PositionRegistry_contract(address=ProtocolDaoContract.registries(PROTOCOL_CONSTANTS['REGISTRY_POSITION']))
    # assign one of the accounts as _lend_and_borrow_token_holder
    _lend_and_borrow_token_holder = accounts[5]
    # assign one of the accounts as _pool_owner
    _pool_owner = accounts[6]
    # initialize PoolNameRegistryContract
    ProtocolDaoContract.initialize_pool_name_registry(Web3.toWei(POOL_NAME_REGISTRATION_MIN_STAKE_LST, 'ether'), {'from': Deployer})
    # initialize PositionRegistryContract
    ProtocolDaoContract.initialize_position_registry({'from': Deployer})
    # initialize CurrencyDaoContract
    ProtocolDaoContract.initialize_currency_dao({'from': Deployer})
    # initialize InterestPoolDaoContract
    ProtocolDaoContract.initialize_interest_pool_dao({'from': Deployer})
    # initialize UnderwriterPoolDaoContract
    ProtocolDaoContract.initialize_underwriter_pool_dao({'from': Deployer})
    # initialize MarketDaoContract
    ProtocolDaoContract.initialize_market_dao({'from': Deployer})
    # initialize ShieldPayoutDaoContract
    ProtocolDaoContract.initialize_shield_payout_dao({'from': Deployer})
    # set support for Lend_token
    ProtocolDaoContract.set_token_support(Lend_token.address, True, {'from': Governor})
    # set support for Borrow_token
    ProtocolDaoContract.set_token_support(Borrow_token.address, True, {'from': Governor})
    # get L_lend_token
    L_lend_token = get_ERC20_contract(address=CurrencyDaoContract.token_addresses__l(Lend_token.address, {'from': anyone}))
    # get I_lend_token
    I_lend_token = get_MFT_contract(address=CurrencyDaoContract.token_addresses__i(Lend_token.address, {'from': anyone}))
    # get S_lend_token
    S_lend_token = get_MFT_contract(address=CurrencyDaoContract.token_addresses__s(Lend_token.address, {'from': anyone}))
    # get U_lend_token
    U_lend_token = get_MFT_contract(address=CurrencyDaoContract.token_addresses__u(Lend_token.address, {'from': anyone}))
    # get L_borrow_token
    L_borrow_token = get_ERC20_contract(address=CurrencyDaoContract.token_addresses__l(Borrow_token.address, {'from': anyone}))
    # get F_borrow_token
    F_borrow_token = get_MFT_contract(address=CurrencyDaoContract.token_addresses__f(Borrow_token.address, {'from': anyone}))
    # get I_borrow_token
    I_borrow_token = get_MFT_contract(address=CurrencyDaoContract.token_addresses__i(Borrow_token.address, {'from': anyone}))
    # get _loan_market_hash
    _loan_market_hash = MarketDaoContract.loan_market_hash(Lend_token.address, H20, Borrow_token.address, {'from': anyone})
    # get _shield_market_hash
    _shield_market_hash = MarketDaoContract.shield_market_hash(Lend_token.address, H20, Borrow_token.address, STRIKE_125, {'from': anyone})
    # set maximum_market_liability
    ProtocolDaoContract.set_maximum_liability_for_loan_market(Lend_token.address, H20, Borrow_token.address, Web3.toWei(MAX_LIABILITY_CURENCY_MARKET, 'ether'), {'from': Governor})
    # _pool_owner buys POOL_NAME_REGISTRATION_MIN_STAKE_LST LST_token from a 3rd party exchange
    LST_token.transfer(_pool_owner, Web3.toWei(POOL_NAME_REGISTRATION_MIN_STAKE_LST, 'ether'), {'from': Whale})
    # _pool_owner authorizes CurrencyDaoContract to spend POOL_NAME_REGISTRATION_MIN_STAKE_LST LST_token
    LST_token.approve(CurrencyDaoContract.address, Web3.toWei(POOL_NAME_REGISTRATION_MIN_STAKE_LST, 'ether'), {'from': _pool_owner})
    # _pool_owner registers _pool_name POOL_NAME_LIONFURY
    _pool_name = POOL_NAME_LIONFURY
    UnderwriterPoolDaoContract.register_pool(
        False, Lend_token.address, _pool_name, Web3.toWei(50, 'ether'), 1, 1, 90, {'from': _pool_owner, 'gas': 1200000})
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
    # _pool_owner authorizes CurrencyDaoContract to spend INTEREST_POOL_DAO_MIN_MFT_FEE LST_token
    LST_token.approve(CurrencyDaoContract.address, Web3.toWei(INTEREST_POOL_DAO_MIN_MFT_FEE, 'ether'), {'from': _pool_owner})
    # set support for MFT H20
    UnderwriterPool.support_mft(H20, Borrow_token.address, STRIKE_125,
        Web3.toWei(0.025, 'ether'), Web3.toWei(0.05, 'ether'), {'from': _pool_owner, 'gas': 2500000})
    # _lend_and_borrow_token_holder buys 1000 Lend_token from a 3rd party exchange
    Lend_token.transfer(_lend_and_borrow_token_holder, Web3.toWei(1000, 'ether'), {'from': Whale})
    # _lend_and_borrow_token_holder buys 5 Borrow_token from a 3rd party exchange
    Borrow_token.transfer(_lend_and_borrow_token_holder, Web3.toWei(5, 'ether'), {'from': Whale})
    # _lend_and_borrow_token_holder authorizes CurrencyDaoContract to spend 800 Lend_token
    Lend_token.approve(CurrencyDaoContract.address, Web3.toWei(800, 'ether'), {'from': _lend_and_borrow_token_holder})
    # _lend_and_borrow_token_holder authorizes CurrencyDaoContract to spend 4 Borrow_token
    Borrow_token.approve(CurrencyDaoContract.address, Web3.toWei(4, 'ether'), {'from': _lend_and_borrow_token_holder})
    # _lend_and_borrow_token_holder wraps 800 Lend_token to L_lend_token
    CurrencyDaoContract.wrap(Lend_token.address, Web3.toWei(800, 'ether'), {'from': _lend_and_borrow_token_holder, 'gas': 145000})
    # _lend_and_borrow_token_holder wraps 4 Borrow_tokens to 4 L_borrow_tokens
    CurrencyDaoContract.wrap(Borrow_token.address, Web3.toWei(4, 'ether'), {'from': _lend_and_borrow_token_holder, 'gas': 145000})
    # _lend_and_borrow_token_holder splits 500 L_lend_tokens into 500 I_lend_tokens and 500 S_lend_tokens and 500 U_lend_tokens for H20, Borrow_token, and STRIKE_200
    UnderwriterPoolDaoContract.split(Lend_token.address, H20, Borrow_token.address, STRIKE_125, Web3.toWei(500, 'ether'), {'from': _lend_and_borrow_token_holder, 'gas': 1100000})
    _i_lend_id = I_lend_token.id(Lend_token.address, H20, ZERO_ADDRESS, 0, {'from': anyone})
    _s_lend_id = S_lend_token.id(Lend_token.address, H20, Borrow_token.address, STRIKE_125, {'from': anyone})
    _u_lend_id = U_lend_token.id(Lend_token.address, H20, Borrow_token.address, STRIKE_125, {'from': anyone})
    # _lend_and_borrow_token_holder splits 4 L_borrow_tokens into 4 F_borrow_tokens and 4 I_borrow_tokens for H20
    InterestPoolDaoContract.split(Borrow_token.address, H20, Web3.toWei(4, 'ether'), {'from': _lend_and_borrow_token_holder, 'gas': 700000})
    _f_borrow_id = F_borrow_token.id(Borrow_token.address, H20, ZERO_ADDRESS, 0, {'from': anyone})
    _i_borrow_id = I_borrow_token.id(Borrow_token.address, H20, ZERO_ADDRESS, 0, {'from': anyone})
    # _lend_and_borrow_token_holder avails a loan for 500 Lend_tokens
    # For this, she places 4 F_borrow_tokens, 500 I_lend_tokens and 500 S_lend_tokens as collateral
    PositionRegistryContract.avail_loan(Lend_token.address, H20, Borrow_token.address, STRIKE_125, Web3.toWei(500, 'ether'), {'from': _lend_and_borrow_token_holder, 'gas': 900000})
    _position_id = PositionRegistryContract.borrow_position(_lend_and_borrow_token_holder, 1, {'from': anyone})
    assert PositionRegistryContract.positions__status(_position_id, {'from': anyone}) == PositionRegistryContract.LOAN_STATUS_ACTIVE({'from': anyone})
    assert PositionRegistryContract.positions__repaid_value(_position_id, {'from': anyone}) == 0
    # _lend_and_borrow_token_holder authorizes CurrencyDaoContract to spend 300 Lend_token
    Lend_token.approve(CurrencyDaoContract.address, Web3.toWei(300, 'ether'), {'from': _lend_and_borrow_token_holder})
    assert Lend_token.allowance(_lend_and_borrow_token_holder, CurrencyDaoContract.address) == Web3.toWei(300, 'ether')
    # _lend_and_borrow_token_holder closes the loan
    PositionRegistryContract.repay_loan(_position_id, Web3.toWei(300, 'ether'), {'from': _lend_and_borrow_token_holder, 'gas': 400000})
    assert PositionRegistryContract.positions__status(_position_id, {'from': anyone}) == PositionRegistryContract.LOAN_STATUS_ACTIVE({'from': anyone})
    assert PositionRegistryContract.positions__repaid_value(_position_id, {'from': anyone}) == Web3.toWei(300, 'ether')


def test_full_close_position_sans_poolshare_model(accounts, get_log_args,
    Whale, Deployer, Governor,
    Lend_token, Borrow_token, LST_token,
    get_ERC20_contract, get_MFT_contract,
    get_PoolNameRegistry_contract, get_PositionRegistry_contract,
    get_CurrencyDao_contract, get_InterestPoolDao_contract,
    get_UnderwriterPoolDao_contract, get_MarketDao_contract,
    get_UnderwriterPool_contract,
    ProtocolDaoContract):
    anyone = accounts[-1]
    # get CurrencyDaoContract
    CurrencyDaoContract = get_CurrencyDao_contract(address=ProtocolDaoContract.daos(PROTOCOL_CONSTANTS['DAO_CURRENCY']))
    # get InterestPoolDaoContract
    InterestPoolDaoContract = get_InterestPoolDao_contract(address=ProtocolDaoContract.daos(PROTOCOL_CONSTANTS['DAO_INTEREST_POOL']))
    # get UnderwriterPoolDaoContract
    UnderwriterPoolDaoContract = get_UnderwriterPoolDao_contract(address=ProtocolDaoContract.daos(PROTOCOL_CONSTANTS['DAO_UNDERWRITER_POOL']))
    # get MarketDaoContract
    MarketDaoContract = get_MarketDao_contract(address=ProtocolDaoContract.daos(PROTOCOL_CONSTANTS['DAO_MARKET']))
    # get PoolNameRegistryContract
    PoolNameRegistryContract = get_PoolNameRegistry_contract(address=ProtocolDaoContract.registries(PROTOCOL_CONSTANTS['REGISTRY_POOL_NAME']))
    # get PositionRegistryContract
    PositionRegistryContract = get_PositionRegistry_contract(address=ProtocolDaoContract.registries(PROTOCOL_CONSTANTS['REGISTRY_POSITION']))
    # assign one of the accounts as _lend_and_borrow_token_holder
    _lend_and_borrow_token_holder = accounts[5]
    # assign one of the accounts as _pool_owner
    _pool_owner = accounts[6]
    # initialize PoolNameRegistryContract
    ProtocolDaoContract.initialize_pool_name_registry(Web3.toWei(POOL_NAME_REGISTRATION_MIN_STAKE_LST, 'ether'), {'from': Deployer})
    # initialize PositionRegistryContract
    ProtocolDaoContract.initialize_position_registry({'from': Deployer})
    # initialize CurrencyDaoContract
    ProtocolDaoContract.initialize_currency_dao({'from': Deployer})
    # initialize InterestPoolDaoContract
    ProtocolDaoContract.initialize_interest_pool_dao({'from': Deployer})
    # initialize UnderwriterPoolDaoContract
    ProtocolDaoContract.initialize_underwriter_pool_dao({'from': Deployer})
    # initialize MarketDaoContract
    ProtocolDaoContract.initialize_market_dao({'from': Deployer})
    # initialize ShieldPayoutDaoContract
    ProtocolDaoContract.initialize_shield_payout_dao({'from': Deployer})
    # set support for Lend_token
    ProtocolDaoContract.set_token_support(Lend_token.address, True, {'from': Governor})
    # set support for Borrow_token
    ProtocolDaoContract.set_token_support(Borrow_token.address, True, {'from': Governor})
    # get L_lend_token
    L_lend_token = get_ERC20_contract(address=CurrencyDaoContract.token_addresses__l(Lend_token.address, {'from': anyone}))
    # get I_lend_token
    I_lend_token = get_MFT_contract(address=CurrencyDaoContract.token_addresses__i(Lend_token.address, {'from': anyone}))
    # get S_lend_token
    S_lend_token = get_MFT_contract(address=CurrencyDaoContract.token_addresses__s(Lend_token.address, {'from': anyone}))
    # get U_lend_token
    U_lend_token = get_MFT_contract(address=CurrencyDaoContract.token_addresses__u(Lend_token.address, {'from': anyone}))
    # get L_borrow_token
    L_borrow_token = get_ERC20_contract(address=CurrencyDaoContract.token_addresses__l(Borrow_token.address, {'from': anyone}))
    # get F_borrow_token
    F_borrow_token = get_MFT_contract(address=CurrencyDaoContract.token_addresses__f(Borrow_token.address, {'from': anyone}))
    # get I_borrow_token
    I_borrow_token = get_MFT_contract(address=CurrencyDaoContract.token_addresses__i(Borrow_token.address, {'from': anyone}))
    # get _loan_market_hash
    _loan_market_hash = MarketDaoContract.loan_market_hash(Lend_token.address, H20, Borrow_token.address, {'from': anyone})
    # get _shield_market_hash
    _shield_market_hash = MarketDaoContract.shield_market_hash(Lend_token.address, H20, Borrow_token.address, STRIKE_125, {'from': anyone})
    # set maximum_market_liability
    ProtocolDaoContract.set_maximum_liability_for_loan_market(Lend_token.address, H20, Borrow_token.address, Web3.toWei(MAX_LIABILITY_CURENCY_MARKET, 'ether'), {'from': Governor})
    # _pool_owner buys POOL_NAME_REGISTRATION_MIN_STAKE_LST LST_token from a 3rd party exchange
    LST_token.transfer(_pool_owner, Web3.toWei(POOL_NAME_REGISTRATION_MIN_STAKE_LST, 'ether'), {'from': Whale})
    # _pool_owner authorizes CurrencyDaoContract to spend POOL_NAME_REGISTRATION_MIN_STAKE_LST LST_token
    LST_token.approve(CurrencyDaoContract.address, Web3.toWei(POOL_NAME_REGISTRATION_MIN_STAKE_LST, 'ether'), {'from': _pool_owner})
    # _pool_owner registers _pool_name POOL_NAME_LIONFURY
    _pool_name = POOL_NAME_LIONFURY
    UnderwriterPoolDaoContract.register_pool(
        False, Lend_token.address, _pool_name, Web3.toWei(50, 'ether'), 1, 1, 90, {'from': _pool_owner, 'gas': 1200000})
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
    # _pool_owner authorizes CurrencyDaoContract to spend INTEREST_POOL_DAO_MIN_MFT_FEE LST_token
    LST_token.approve(CurrencyDaoContract.address, Web3.toWei(INTEREST_POOL_DAO_MIN_MFT_FEE, 'ether'), {'from': _pool_owner})
    # set support for MFT H20
    UnderwriterPool.support_mft(H20, Borrow_token.address, STRIKE_125,
        Web3.toWei(0.025, 'ether'), Web3.toWei(0.05, 'ether'), {'from': _pool_owner, 'gas': 2500000})
    # _lend_and_borrow_token_holder buys 1000 Lend_token from a 3rd party exchange
    Lend_token.transfer(_lend_and_borrow_token_holder, Web3.toWei(1000, 'ether'), {'from': Whale})
    # _lend_and_borrow_token_holder buys 5 Borrow_token from a 3rd party exchange
    Borrow_token.transfer(_lend_and_borrow_token_holder, Web3.toWei(5, 'ether'), {'from': Whale})
    # _lend_and_borrow_token_holder authorizes CurrencyDaoContract to spend 800 Lend_token
    Lend_token.approve(CurrencyDaoContract.address, Web3.toWei(800, 'ether'), {'from': _lend_and_borrow_token_holder})
    # _lend_and_borrow_token_holder authorizes CurrencyDaoContract to spend 4 Borrow_token
    Borrow_token.approve(CurrencyDaoContract.address, Web3.toWei(4, 'ether'), {'from': _lend_and_borrow_token_holder})
    # _lend_and_borrow_token_holder wraps 800 Lend_token to L_lend_token
    CurrencyDaoContract.wrap(Lend_token.address, Web3.toWei(800, 'ether'), {'from': _lend_and_borrow_token_holder, 'gas': 145000})
    # _lend_and_borrow_token_holder wraps 4 Borrow_tokens to 4 L_borrow_tokens
    CurrencyDaoContract.wrap(Borrow_token.address, Web3.toWei(4, 'ether'), {'from': _lend_and_borrow_token_holder, 'gas': 145000})
    # _lend_and_borrow_token_holder splits 500 L_lend_tokens into 500 I_lend_tokens and 500 S_lend_tokens and 500 U_lend_tokens for H20, Borrow_token, and STRIKE_200
    UnderwriterPoolDaoContract.split(Lend_token.address, H20, Borrow_token.address, STRIKE_125, Web3.toWei(500, 'ether'), {'from': _lend_and_borrow_token_holder, 'gas': 1100000})
    _i_lend_id = I_lend_token.id(Lend_token.address, H20, ZERO_ADDRESS, 0, {'from': anyone})
    _s_lend_id = S_lend_token.id(Lend_token.address, H20, Borrow_token.address, STRIKE_125, {'from': anyone})
    _u_lend_id = U_lend_token.id(Lend_token.address, H20, Borrow_token.address, STRIKE_125, {'from': anyone})
    # _lend_and_borrow_token_holder splits 4 L_borrow_tokens into 4 F_borrow_tokens and 4 I_borrow_tokens for H20
    InterestPoolDaoContract.split(Borrow_token.address, H20, Web3.toWei(4, 'ether'), {'from': _lend_and_borrow_token_holder, 'gas': 700000})
    _f_borrow_id = F_borrow_token.id(Borrow_token.address, H20, ZERO_ADDRESS, 0, {'from': anyone})
    _i_borrow_id = I_borrow_token.id(Borrow_token.address, H20, ZERO_ADDRESS, 0, {'from': anyone})
    # _lend_and_borrow_token_holder avails a loan for 500 Lend_tokens
    # For this, she places 4 F_borrow_tokens, 500 I_lend_tokens and 500 S_lend_tokens as collateral
    PositionRegistryContract.avail_loan(Lend_token.address, H20, Borrow_token.address, STRIKE_125, Web3.toWei(500, 'ether'), {'from': _lend_and_borrow_token_holder, 'gas': 900000})
    _position_id = PositionRegistryContract.borrow_position(_lend_and_borrow_token_holder, 1, {'from': anyone})
    assert PositionRegistryContract.positions__status(_position_id, {'from': anyone}) == PositionRegistryContract.LOAN_STATUS_ACTIVE({'from': anyone})
    assert PositionRegistryContract.positions__repaid_value(_position_id, {'from': anyone}) == 0
    # _lend_and_borrow_token_holder authorizes CurrencyDaoContract to spend 300 Lend_token
    Lend_token.approve(CurrencyDaoContract.address, Web3.toWei(500, 'ether'), {'from': _lend_and_borrow_token_holder})
    assert Lend_token.allowance(_lend_and_borrow_token_holder, CurrencyDaoContract.address, {'from': anyone}) == Web3.toWei(500, 'ether')
    # _lend_and_borrow_token_holder closes the loan
    PositionRegistryContract.repay_loan(_position_id, Web3.toWei(500, 'ether'), {'from': _lend_and_borrow_token_holder, 'gas': 500000})
    assert PositionRegistryContract.positions__repaid_value(_position_id, {'from': anyone}) == Web3.toWei(500, 'ether')
    assert PositionRegistryContract.positions__status(_position_id, {'from': anyone}) == PositionRegistryContract.LOAN_STATUS_CLOSED({'from': anyone})


# def test_settle_loan_market_with_no_loans(accounts, get_contract, get_log_args, time_travel,
#         LST_token, Lend_token, Borrow_token, Malicious_token,
#         ERC20_library, ERC1155_library,
#         CurrencyPool_library, CurrencyDaoContract,
#         InterestPool_library, InterestPoolDaoContract,
#         UnderwriterPool_library, UnderwriterPoolDaoContract,
#         CollateralAuctionGraph_Library, CollateralAuctionDao,
#         ShieldPayoutDaoContract,
#         PositionRegistryContract,
#         PriceFeed,
#         PriceOracle,
#         MarketDaoContract
#     ):
#     owner = accounts[0]
#     _initialize_all_daos(owner, accounts,
#         LST_token, Lend_token, Borrow_token,
#         ERC20_library, ERC1155_library,
#         CurrencyPool_library, CurrencyDaoContract,
#         InterestPool_library, InterestPoolDaoContract,
#         UnderwriterPool_library, UnderwriterPoolDaoContract,
#         CollateralAuctionGraph_Library, CollateralAuctionDao,
#         ShieldPayoutDaoContract,
#         PositionRegistryContract,
#         PriceOracle,
#         MarketDaoContract
#     )
#     # set_offer_registration_fee_lookup()
#     _minimum_fee = 100
#     _minimum_interval = 10
#     _fee_multiplier = 2000
#     _fee_multiplier_decimals = 1000
#     tx_hash = UnderwriterPoolDaoContract.set_offer_registration_fee_lookup(_minimum_fee,
#         _minimum_interval, _fee_multiplier, _fee_multiplier_decimals,
#         {'from': owner})
#     tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
#     assert tx_receipt['status'] == 1
#     # set_currency_support for Lend_token in CurrencyDaoContract
#     tx_hash = CurrencyDaoContract.set_currency_support(Lend_token.address, True,
#         {'from': owner, 'gas': 1570000})
#     tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
#     assert tx_receipt['status'] == 1
#     # set_currency_support for Borrow_token in CurrencyDaoContract
#     tx_hash = CurrencyDaoContract.set_currency_support(Borrow_token.address, True,
#         {'from': owner, 'gas': 1570000})
#     tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
#     assert tx_receipt['status'] == 1
#     # register_pool for Lend_token
#     pool_owner = accounts[1]
#     tx_hash = UnderwriterPoolDaoContract.register_pool(Lend_token.address,
#         'Underwriter Pool A', 'UPA', 50,
#         {'from': pool_owner, 'gas': 850000})
#     tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
#     assert tx_receipt['status'] == 1
#     # get UnderwriterPool contract
#     logs_8 = get_log_args(tx_hash, UnderwriterPoolDaoContract, "PoolRegistered")
#     _pool_hash = UnderwriterPoolDaoContract.pool_hash(Lend_token.address, logs_8[0].args._pool_address)
#     UnderwriterPool = get_contract(
#         'contracts/templates/UnderwriterPoolTemplate1.v.py',
#         interfaces=[
#             'ERC20', 'ERC1155', 'ERC1155TokenReceiver', 'UnderwriterPoolDaoContract'
#         ],
#         address=UnderwriterPoolDaoContract.pools__pool_address(_pool_hash)
#     )
#     # get UnderwriterPoolCurrency
#     UnderwriterPoolCurrency = get_contract(
#         'contracts/templates/ERC20Template1.v.py',
#         address=UnderwriterPool.pool_currency_address()
#     )
#     # pool_owner buys LST from a 3rd party
#     LST_token.transfer(pool_owner, 1000 * 10 ** 18, {'from': owner})
#     # pool_owner authorizes CurrencyDaoContract to spend LST required for offer_registration_fee
#     tx_hash = LST_token.approve(CurrencyDaoContract.address, UnderwriterPoolDaoContract.offer_registration_fee() * (10 ** 18),
#         {'from': pool_owner})
#     tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
#     assert tx_receipt['status'] == 1
#     # pool_owner registers an expiry : Last Thursday of December 2019, i.e., December 26th, 2019, i.e., H20
#     _strike_price = 200 * 10 ** 18
#     tx_hash = UnderwriterPool.register_expiry(H20, Borrow_token.address,
#         _strike_price, {'from': pool_owner, 'gas': 2600000})
#     tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
#     assert tx_receipt['status'] == 1
#     # get L_currency_token
#     L_currency_token = get_contract(
#         'contracts/templates/ERC20Template1.v.py',
#         address=CurrencyDaoContract.currencies__l_currency_address(Lend_token.address)
#     )
#     # get L_underlying_token
#     L_underlying_token = get_contract(
#         'contracts/templates/ERC20Template1.v.py',
#         address=CurrencyDaoContract.currencies__l_currency_address(Borrow_token.address)
#     )
#     # assign one of the accounts as a Lender
#     Lender = accounts[2]
#     # Lender buys 1000 lend token from a 3rd party exchange
#     tx_hash = Lend_token.transfer(Lender, 1000 * 10 ** 18, {'from': owner})
#     tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
#     assert tx_receipt['status'] == 1
#     # Lender authorizes CurrencyDaoContract to spend 800 lend currency
#     tx_hash = Lend_token.approve(CurrencyDaoContract.address, 800 * (10 ** 18),
#         {'from': Lender})
#     tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
#     assert tx_receipt['status'] == 1
#     # Lender deposits 800 Lend_tokens to Currency Pool and gets l_tokens
#     tx_hash = CurrencyDaoContract.currency_to_l_currency(Lend_token.address, 800 * 10 ** 18,
#         {'from': Lender, 'gas': 200000})
#     tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
#     assert tx_receipt['status'] == 1
#     # Lender purchases UnderwriterPoolCurrency for 800 L_tokens
#     # Lender gets 40000 UnderwriterPoolCurrency tokens
#     # 800 L_tokens are deposited into UnderwriterPool account
#     tx_hash = UnderwriterPool.purchase_pool_currency(800 * 10 ** 18, {'from': Lender})
#     tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
#     assert tx_receipt['status'] == 1
#     # vefiry shield_currency_price is not set
#     multi_fungible_addresses = CurrencyDaoContract.multi_fungible_addresses(Lend_token.address)
#     _s_hash = UnderwriterPoolDaoContract.multi_fungible_currency_hash(
#         multi_fungible_addresses[3], Lend_token.address, H20,
#         Borrow_token.address, _strike_price)
#     _i_hash = UnderwriterPoolDaoContract.multi_fungible_currency_hash(
#         multi_fungible_addresses[1], Lend_token.address, H20, ZERO_ADDRESS, 0)
#     # pool_owner initiates offer of 600 I_tokens from the UnderwriterPool
#     # 600 L_tokens burned from UnderwriterPool account
#     # 600 I_tokens, 3 S_tokens, and 3 U_tokens minted to UnderwriterPool account
#     tx_hash = UnderwriterPool.increment_i_currency_supply(
#         H20, Borrow_token.address, _strike_price, 600 * 10 ** 18,
#         {'from': pool_owner, 'gas': 600000})
#     tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
#     assert tx_receipt['status'] == 1
#     # get I_token
#     I_token = get_contract(
#         'contracts/templates/ERC1155Template2.v.py',
#         interfaces=['ERC1155TokenReceiver'],
#         address=CurrencyDaoContract.currencies__i_currency_address(Lend_token.address)
#     )
#     S_token = get_contract(
#         'contracts/templates/ERC1155Template2.v.py',
#         interfaces=['ERC1155TokenReceiver'],
#         address=CurrencyDaoContract.currencies__s_currency_address(Lend_token.address)
#     )
#     U_token = get_contract(
#         'contracts/templates/ERC1155Template2.v.py',
#         interfaces=['ERC1155TokenReceiver'],
#         address=CurrencyDaoContract.currencies__u_currency_address(Lend_token.address)
#     )
#     # assign one of the accounts as a High_Risk_Insurer
#     High_Risk_Insurer = accounts[2]
#     # High_Risk_Insurer purchases 100 i_tokens from UnderwriterPool
#     tx_hash = UnderwriterPool.purchase_i_currency(H20, Borrow_token.address,
#         _strike_price, 100 * 10 ** 18, 0, {'from': High_Risk_Insurer})
#     tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
#     assert tx_receipt['status'] == 1
#     # High_Risk_Insurer purchases 2 s_tokens from UnderwriterPool
#     tx_hash = UnderwriterPool.purchase_s_currency(H20, Borrow_token.address,
#         _strike_price, 2 * 10 ** 18, 0, {'from': High_Risk_Insurer})
#     tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
#     assert tx_receipt['status'] == 1
#     # assign one of the accounts as a Borrower
#     Borrower = accounts[3]
#     # Borrower purchases 10 Borrow_tokens from a 3rd party exchange
#     tx_hash = Borrow_token.transfer(Borrower, 10 * 10 ** 18, {'from': owner})
#     tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
#     assert tx_receipt['status'] == 1
#     assert Borrow_token.balanceOf(Borrower) == 10 * 10 ** 18
#     # Borrower authorizes CurrencyDaoContract to spend 2 Borrow_tokens
#     tx_hash = Borrow_token.approve(CurrencyDaoContract.address, 3 * (10 ** 18),
#         {'from': Borrower})
#     tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
#     assert tx_receipt['status'] == 1
#     # Borrower deposits 2 Borrow_tokens to Currency Pool and gets l_tokens
#     tx_hash = CurrencyDaoContract.currency_to_l_currency(Borrow_token.address, 3 * 10 ** 18,
#         {'from': Borrower, 'gas': 200000})
#     tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
#     assert tx_receipt['status'] == 1
#     # Borrower wishes to avail a loan of 400 Lend_tokens
#     # High_Risk_Insurer authorizes CurrencyDaoContract to spend his S_token
#     tx_hash = S_token.setApprovalForAll(CurrencyDaoContract.address, True,
#         {'from': High_Risk_Insurer})
#     tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
#     assert tx_receipt['status'] == 1
#     # High_Risk_Insurer authorizes CurrencyDaoContract to spend his I_token
#     tx_hash = I_token.setApprovalForAll(CurrencyDaoContract.address, True,
#         {'from': High_Risk_Insurer})
#     tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
#     assert tx_receipt['status'] == 1
#     # High_Risk_Insurer sets an offer of 2 s_tokens for 20 i_tokens
#     assert PositionRegistryContract.last_offer_index() == 0
#     tx_hash = PositionRegistryContract.create_offer(
#         Lend_token.address, H20, Borrow_token.address, _strike_price,
#         2, 20, 5 * 10 ** 15,
#         {'from': High_Risk_Insurer, 'gas': 450000})
#     tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
#     assert tx_receipt['status'] == 1
#     # get Auction contract
#     _loan_market_hash = CollateralAuctionDao.loan_market_hash(
#         Lend_token.address, H20, Borrow_token.address
#     )
#     Auction = get_contract(
#         'contracts/templates/SimpleCollateralAuctionGraph.v.py',
#         interfaces=['ERC20', 'MarketDaoContract'],
#         address=CollateralAuctionDao.graphs(_loan_market_hash)
#     )
#     # No loans availed for the loan market
#     # Time passes, until the loan market expires
#     time_travel(H20)
#     # update price feed
#     tx_hash = PriceFeed.set_price(240 * 10 ** 18, {'from': owner})
#     tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
#     assert tx_receipt['status'] == 1
#     # assign one of the accounts as a _loan_market_settler
#     _loan_market_settler = accounts[3]
#     assert MarketDaoContract.loan_markets__status(_loan_market_hash) == MarketDaoContract.LOAN_MARKET_STATUS_OPEN()
#     assert MarketDaoContract.loan_markets__total_outstanding_currency_value_at_expiry(_loan_market_hash) == 0
#     assert MarketDaoContract.loan_markets__total_outstanding_underlying_value_at_expiry(_loan_market_hash) == 0
#     assert MarketDaoContract.loan_markets__shield_market_count(_loan_market_hash) == 1
#     tx_hash = MarketDaoContract.settle_loan_market(_loan_market_hash, {'from': _loan_market_settler, 'gas': 90000})
#     tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
#     assert tx_receipt['status'] == 1
#     assert MarketDaoContract.loan_markets__status(_loan_market_hash) == MarketDaoContract.LOAN_MARKET_STATUS_CLOSED()
#
#
# def test_settle_loan_market_with_loans(accounts, get_contract, get_log_args, time_travel,
#         LST_token, Lend_token, Borrow_token, Malicious_token,
#         ERC20_library, ERC1155_library,
#         CurrencyPool_library, CurrencyDaoContract,
#         InterestPool_library, InterestPoolDaoContract,
#         UnderwriterPool_library, UnderwriterPoolDaoContract,
#         CollateralAuctionGraph_Library, CollateralAuctionDao,
#         ShieldPayoutDaoContract,
#         PositionRegistryContract,
#         PriceFeed,
#         PriceOracle,
#         MarketDaoContract
#     ):
#     owner = accounts[0]
#     _initialize_all_daos(owner, accounts,
#         LST_token, Lend_token, Borrow_token,
#         ERC20_library, ERC1155_library,
#         CurrencyPool_library, CurrencyDaoContract,
#         InterestPool_library, InterestPoolDaoContract,
#         UnderwriterPool_library, UnderwriterPoolDaoContract,
#         CollateralAuctionGraph_Library, CollateralAuctionDao,
#         ShieldPayoutDaoContract,
#         PositionRegistryContract,
#         PriceOracle,
#         MarketDaoContract
#     )
#     # set_offer_registration_fee_lookup()
#     _minimum_fee = 100
#     _minimum_interval = 10
#     _fee_multiplier = 2000
#     _fee_multiplier_decimals = 1000
#     tx_hash = UnderwriterPoolDaoContract.set_offer_registration_fee_lookup(_minimum_fee,
#         _minimum_interval, _fee_multiplier, _fee_multiplier_decimals,
#         {'from': owner})
#     tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
#     assert tx_receipt['status'] == 1
#     # set_currency_support for Lend_token in CurrencyDaoContract
#     tx_hash = CurrencyDaoContract.set_currency_support(Lend_token.address, True,
#         {'from': owner, 'gas': 1570000})
#     tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
#     assert tx_receipt['status'] == 1
#     # set_currency_support for Borrow_token in CurrencyDaoContract
#     tx_hash = CurrencyDaoContract.set_currency_support(Borrow_token.address, True,
#         {'from': owner, 'gas': 1570000})
#     tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
#     assert tx_receipt['status'] == 1
#     # register_pool for Lend_token
#     pool_owner = accounts[1]
#     tx_hash = UnderwriterPoolDaoContract.register_pool(Lend_token.address,
#         'Underwriter Pool A', 'UPA', 50,
#         {'from': pool_owner, 'gas': 850000})
#     tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
#     assert tx_receipt['status'] == 1
#     # get UnderwriterPool contract
#     logs_8 = get_log_args(tx_hash, UnderwriterPoolDaoContract, "PoolRegistered")
#     _pool_hash = UnderwriterPoolDaoContract.pool_hash(Lend_token.address, logs_8[0].args._pool_address)
#     UnderwriterPool = get_contract(
#         'contracts/templates/UnderwriterPoolTemplate1.v.py',
#         interfaces=[
#             'ERC20', 'ERC1155', 'ERC1155TokenReceiver', 'UnderwriterPoolDaoContract'
#         ],
#         address=UnderwriterPoolDaoContract.pools__pool_address(_pool_hash)
#     )
#     # get UnderwriterPoolCurrency
#     UnderwriterPoolCurrency = get_contract(
#         'contracts/templates/ERC20Template1.v.py',
#         address=UnderwriterPool.pool_currency_address()
#     )
#     # pool_owner buys LST from a 3rd party
#     LST_token.transfer(pool_owner, 1000 * 10 ** 18, {'from': owner})
#     # pool_owner authorizes CurrencyDaoContract to spend LST required for offer_registration_fee
#     tx_hash = LST_token.approve(CurrencyDaoContract.address, UnderwriterPoolDaoContract.offer_registration_fee() * (10 ** 18),
#         {'from': pool_owner})
#     tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
#     assert tx_receipt['status'] == 1
#     # pool_owner registers an expiry : Last Thursday of December 2019, i.e., December 26th, 2019, i.e., H20
#     _strike_price = 200 * 10 ** 18
#     tx_hash = UnderwriterPool.register_expiry(H20, Borrow_token.address,
#         _strike_price, {'from': pool_owner, 'gas': 2600000})
#     tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
#     assert tx_receipt['status'] == 1
#     # get L_currency_token
#     L_currency_token = get_contract(
#         'contracts/templates/ERC20Template1.v.py',
#         address=CurrencyDaoContract.currencies__l_currency_address(Lend_token.address)
#     )
#     # get L_underlying_token
#     L_underlying_token = get_contract(
#         'contracts/templates/ERC20Template1.v.py',
#         address=CurrencyDaoContract.currencies__l_currency_address(Borrow_token.address)
#     )
#     # assign one of the accounts as a Lender
#     Lender = accounts[2]
#     # Lender buys 1000 lend token from a 3rd party exchange
#     tx_hash = Lend_token.transfer(Lender, 1000 * 10 ** 18, {'from': owner})
#     tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
#     assert tx_receipt['status'] == 1
#     # Lender authorizes CurrencyDaoContract to spend 800 lend currency
#     tx_hash = Lend_token.approve(CurrencyDaoContract.address, 800 * (10 ** 18),
#         {'from': Lender})
#     tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
#     assert tx_receipt['status'] == 1
#     # Lender deposits 800 Lend_tokens to Currency Pool and gets l_tokens
#     tx_hash = CurrencyDaoContract.currency_to_l_currency(Lend_token.address, 800 * 10 ** 18,
#         {'from': Lender, 'gas': 200000})
#     tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
#     assert tx_receipt['status'] == 1
#     # Lender purchases UnderwriterPoolCurrency for 800 L_tokens
#     # Lender gets 40000 UnderwriterPoolCurrency tokens
#     # 800 L_tokens are deposited into UnderwriterPool account
#     tx_hash = UnderwriterPool.purchase_pool_currency(800 * 10 ** 18, {'from': Lender})
#     tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
#     assert tx_receipt['status'] == 1
#     # vefiry shield_currency_price is not set
#     multi_fungible_addresses = CurrencyDaoContract.multi_fungible_addresses(Lend_token.address)
#     _s_hash = UnderwriterPoolDaoContract.multi_fungible_currency_hash(
#         multi_fungible_addresses[3], Lend_token.address, H20,
#         Borrow_token.address, _strike_price)
#     _i_hash = UnderwriterPoolDaoContract.multi_fungible_currency_hash(
#         multi_fungible_addresses[1], Lend_token.address, H20, ZERO_ADDRESS, 0)
#     # pool_owner initiates offer of 600 I_tokens from the UnderwriterPool
#     # 600 L_tokens burned from UnderwriterPool account
#     # 600 I_tokens, 3 S_tokens, and 3 U_tokens minted to UnderwriterPool account
#     tx_hash = UnderwriterPool.increment_i_currency_supply(
#         H20, Borrow_token.address, _strike_price, 600 * 10 ** 18,
#         {'from': pool_owner, 'gas': 600000})
#     tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
#     assert tx_receipt['status'] == 1
#     # get I_token
#     I_token = get_contract(
#         'contracts/templates/ERC1155Template2.v.py',
#         interfaces=['ERC1155TokenReceiver'],
#         address=CurrencyDaoContract.currencies__i_currency_address(Lend_token.address)
#     )
#     S_token = get_contract(
#         'contracts/templates/ERC1155Template2.v.py',
#         interfaces=['ERC1155TokenReceiver'],
#         address=CurrencyDaoContract.currencies__s_currency_address(Lend_token.address)
#     )
#     U_token = get_contract(
#         'contracts/templates/ERC1155Template2.v.py',
#         interfaces=['ERC1155TokenReceiver'],
#         address=CurrencyDaoContract.currencies__u_currency_address(Lend_token.address)
#     )
#     # assign one of the accounts as a High_Risk_Insurer
#     High_Risk_Insurer = accounts[2]
#     # High_Risk_Insurer purchases 100 i_tokens from UnderwriterPool
#     tx_hash = UnderwriterPool.purchase_i_currency(H20, Borrow_token.address,
#         _strike_price, 100 * 10 ** 18, 0, {'from': High_Risk_Insurer})
#     tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
#     assert tx_receipt['status'] == 1
#     # High_Risk_Insurer purchases 2 s_tokens from UnderwriterPool
#     tx_hash = UnderwriterPool.purchase_s_currency(H20, Borrow_token.address,
#         _strike_price, 2 * 10 ** 18, 0, {'from': High_Risk_Insurer})
#     tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
#     assert tx_receipt['status'] == 1
#     # assign one of the accounts as a Borrower
#     Borrower = accounts[3]
#     # Borrower purchases 10 Borrow_tokens from a 3rd party exchange
#     tx_hash = Borrow_token.transfer(Borrower, 10 * 10 ** 18, {'from': owner})
#     tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
#     assert tx_receipt['status'] == 1
#     assert Borrow_token.balanceOf(Borrower) == 10 * 10 ** 18
#     # Borrower authorizes CurrencyDaoContract to spend 2 Borrow_tokens
#     tx_hash = Borrow_token.approve(CurrencyDaoContract.address, 3 * (10 ** 18),
#         {'from': Borrower})
#     tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
#     assert tx_receipt['status'] == 1
#     # Borrower deposits 2 Borrow_tokens to Currency Pool and gets l_tokens
#     tx_hash = CurrencyDaoContract.currency_to_l_currency(Borrow_token.address, 3 * 10 ** 18,
#         {'from': Borrower, 'gas': 200000})
#     tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
#     assert tx_receipt['status'] == 1
#     # Borrower wishes to avail a loan of 400 Lend_tokens
#     # High_Risk_Insurer authorizes CurrencyDaoContract to spend his S_token
#     tx_hash = S_token.setApprovalForAll(CurrencyDaoContract.address, True,
#         {'from': High_Risk_Insurer})
#     tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
#     assert tx_receipt['status'] == 1
#     # High_Risk_Insurer authorizes CurrencyDaoContract to spend his I_token
#     tx_hash = I_token.setApprovalForAll(CurrencyDaoContract.address, True,
#         {'from': High_Risk_Insurer})
#     tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
#     assert tx_receipt['status'] == 1
#     # High_Risk_Insurer sets an offer of 2 s_tokens for 20 i_tokens
#     assert PositionRegistryContract.last_offer_index() == 0
#     tx_hash = PositionRegistryContract.create_offer(
#         Lend_token.address, H20, Borrow_token.address, _strike_price,
#         2, 20, 5 * 10 ** 15,
#         {'from': High_Risk_Insurer, 'gas': 450000})
#     tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
#     assert tx_receipt['status'] == 1
#     # Borrower purchases this offer for the amount of 0.1 ETH
#     # 20 i_tokens and 2 s_tokens are transferred from High_Risk_Insurer account to MarketDaoContract
#     tx_hash = PositionRegistryContract.avail_loan(0,
#         {'from': Borrower, 'value': 10 ** 17, 'gas': 950000})
#     tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
#     assert tx_receipt['status'] == 1
#     # verify Lend_token balance of Borrower
#     assert Lend_token.balanceOf(Borrower) == 400 * 10 ** 18
#     # get Auction contract
#     _loan_market_hash = CollateralAuctionDao.loan_market_hash(
#         Lend_token.address, H20, Borrow_token.address
#     )
#     Auction = get_contract(
#         'contracts/templates/SimpleCollateralAuctionGraph.v.py',
#         interfaces=['ERC20', 'MarketDaoContract'],
#         address=CollateralAuctionDao.graphs(_loan_market_hash)
#     )
#     # No loans availed for the loan market
#     # Time passes, until the loan market expires
#     time_travel(H20)
#     # update price feed
#     tx_hash = PriceFeed.set_price(240 * 10 ** 18, {'from': owner})
#     tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
#     assert tx_receipt['status'] == 1
#     # assign one of the accounts as a _loan_market_settler
#     _loan_market_settler = accounts[3]
#     assert MarketDaoContract.loan_markets__status(_loan_market_hash) == MarketDaoContract.LOAN_MARKET_STATUS_OPEN()
#     assert MarketDaoContract.loan_markets__total_outstanding_currency_value_at_expiry(_loan_market_hash) == 400 * 10 ** 18
#     assert MarketDaoContract.loan_markets__total_outstanding_underlying_value_at_expiry(_loan_market_hash) == 2 * 10 ** 18
#     assert MarketDaoContract.loan_markets__shield_market_count(_loan_market_hash) == 1
#     tx_hash = MarketDaoContract.settle_loan_market(_loan_market_hash, {'from': _loan_market_settler, 'gas': 280000})
#     tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
#     assert tx_receipt['status'] == 1
#     assert MarketDaoContract.loan_markets__status(_loan_market_hash) == MarketDaoContract.LOAN_MARKET_STATUS_SETTLING()
#
#
# def test_situation_after_loan_market_settlement_for_expiry_price_above_original_price(accounts, get_contract, get_log_args, time_travel,
#         LST_token, Lend_token, Borrow_token, Malicious_token,
#         ERC20_library, ERC1155_library,
#         CurrencyPool_library, CurrencyDaoContract,
#         InterestPool_library, InterestPoolDaoContract,
#         UnderwriterPool_library, UnderwriterPoolDaoContract,
#         CollateralAuctionGraph_Library, CollateralAuctionDao,
#         ShieldPayoutDaoContract,
#         PositionRegistryContract,
#         PriceFeed,
#         PriceOracle,
#         MarketDaoContract
#     ):
#     owner = accounts[0]
#     _initialize_all_daos(owner, accounts,
#         LST_token, Lend_token, Borrow_token,
#         ERC20_library, ERC1155_library,
#         CurrencyPool_library, CurrencyDaoContract,
#         InterestPool_library, InterestPoolDaoContract,
#         UnderwriterPool_library, UnderwriterPoolDaoContract,
#         CollateralAuctionGraph_Library, CollateralAuctionDao,
#         ShieldPayoutDaoContract,
#         PositionRegistryContract,
#         PriceOracle,
#         MarketDaoContract
#     )
#     # set_offer_registration_fee_lookup()
#     _minimum_fee = 100
#     _minimum_interval = 10
#     _fee_multiplier = 2000
#     _fee_multiplier_decimals = 1000
#     tx_hash = UnderwriterPoolDaoContract.set_offer_registration_fee_lookup(_minimum_fee,
#         _minimum_interval, _fee_multiplier, _fee_multiplier_decimals,
#         {'from': owner})
#     tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
#     assert tx_receipt['status'] == 1
#     # set_currency_support for Lend_token in CurrencyDaoContract
#     tx_hash = CurrencyDaoContract.set_currency_support(Lend_token.address, True,
#         {'from': owner, 'gas': 1570000})
#     tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
#     assert tx_receipt['status'] == 1
#     # set_currency_support for Borrow_token in CurrencyDaoContract
#     tx_hash = CurrencyDaoContract.set_currency_support(Borrow_token.address, True,
#         {'from': owner, 'gas': 1570000})
#     tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
#     assert tx_receipt['status'] == 1
#     # register_pool for Lend_token
#     pool_owner = accounts[1]
#     tx_hash = UnderwriterPoolDaoContract.register_pool(Lend_token.address,
#         'Underwriter Pool A', 'UPA', 50,
#         {'from': pool_owner, 'gas': 850000})
#     tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
#     assert tx_receipt['status'] == 1
#     # get UnderwriterPool contract
#     logs_8 = get_log_args(tx_hash, UnderwriterPoolDaoContract, "PoolRegistered")
#     _pool_hash = UnderwriterPoolDaoContract.pool_hash(Lend_token.address, logs_8[0].args._pool_address)
#     UnderwriterPool = get_contract(
#         'contracts/templates/UnderwriterPoolTemplate1.v.py',
#         interfaces=[
#             'ERC20', 'ERC1155', 'ERC1155TokenReceiver', 'UnderwriterPoolDaoContract'
#         ],
#         address=UnderwriterPoolDaoContract.pools__pool_address(_pool_hash)
#     )
#     # get UnderwriterPoolCurrency
#     UnderwriterPoolCurrency = get_contract(
#         'contracts/templates/ERC20Template1.v.py',
#         address=UnderwriterPool.pool_currency_address()
#     )
#     # pool_owner buys LST from a 3rd party
#     LST_token.transfer(pool_owner, 1000 * 10 ** 18, {'from': owner})
#     # pool_owner authorizes CurrencyDaoContract to spend LST required for offer_registration_fee
#     tx_hash = LST_token.approve(CurrencyDaoContract.address, UnderwriterPoolDaoContract.offer_registration_fee() * (10 ** 18),
#         {'from': pool_owner})
#     tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
#     assert tx_receipt['status'] == 1
#     # pool_owner registers an expiry : Last Thursday of December 2019, i.e., December 26th, 2019, i.e., H20
#     _strike_price = 200 * 10 ** 18
#     tx_hash = UnderwriterPool.register_expiry(H20, Borrow_token.address,
#         _strike_price, {'from': pool_owner, 'gas': 2600000})
#     tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
#     assert tx_receipt['status'] == 1
#     # get L_currency_token
#     L_currency_token = get_contract(
#         'contracts/templates/ERC20Template1.v.py',
#         address=CurrencyDaoContract.currencies__l_currency_address(Lend_token.address)
#     )
#     # get L_underlying_token
#     L_underlying_token = get_contract(
#         'contracts/templates/ERC20Template1.v.py',
#         address=CurrencyDaoContract.currencies__l_currency_address(Borrow_token.address)
#     )
#     # assign one of the accounts as a Lender
#     Lender = accounts[2]
#     # Lender buys 1000 lend token from a 3rd party exchange
#     tx_hash = Lend_token.transfer(Lender, 1000 * 10 ** 18, {'from': owner})
#     tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
#     assert tx_receipt['status'] == 1
#     # Lender authorizes CurrencyDaoContract to spend 800 lend currency
#     tx_hash = Lend_token.approve(CurrencyDaoContract.address, 800 * (10 ** 18),
#         {'from': Lender})
#     tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
#     assert tx_receipt['status'] == 1
#     # Lender deposits 800 Lend_tokens to Currency Pool and gets l_tokens
#     tx_hash = CurrencyDaoContract.currency_to_l_currency(Lend_token.address, 800 * 10 ** 18,
#         {'from': Lender, 'gas': 200000})
#     tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
#     assert tx_receipt['status'] == 1
#     # Lender purchases UnderwriterPoolCurrency for 800 L_tokens
#     # Lender gets 40000 UnderwriterPoolCurrency tokens
#     # 800 L_tokens are deposited into UnderwriterPool account
#     tx_hash = UnderwriterPool.purchase_pool_currency(800 * 10 ** 18, {'from': Lender})
#     tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
#     assert tx_receipt['status'] == 1
#     # vefiry shield_currency_price is not set
#     multi_fungible_addresses = CurrencyDaoContract.multi_fungible_addresses(Lend_token.address)
#     _s_hash = UnderwriterPoolDaoContract.multi_fungible_currency_hash(
#         multi_fungible_addresses[3], Lend_token.address, H20,
#         Borrow_token.address, _strike_price)
#     _i_hash = UnderwriterPoolDaoContract.multi_fungible_currency_hash(
#         multi_fungible_addresses[1], Lend_token.address, H20, ZERO_ADDRESS, 0)
#     # pool_owner initiates offer of 600 I_tokens from the UnderwriterPool
#     # 600 L_tokens burned from UnderwriterPool account
#     # 600 I_tokens, 3 S_tokens, and 3 U_tokens minted to UnderwriterPool account
#     tx_hash = UnderwriterPool.increment_i_currency_supply(
#         H20, Borrow_token.address, _strike_price, 600 * 10 ** 18,
#         {'from': pool_owner, 'gas': 600000})
#     tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
#     assert tx_receipt['status'] == 1
#     # get I_token
#     I_token = get_contract(
#         'contracts/templates/ERC1155Template2.v.py',
#         interfaces=['ERC1155TokenReceiver'],
#         address=CurrencyDaoContract.currencies__i_currency_address(Lend_token.address)
#     )
#     S_token = get_contract(
#         'contracts/templates/ERC1155Template2.v.py',
#         interfaces=['ERC1155TokenReceiver'],
#         address=CurrencyDaoContract.currencies__s_currency_address(Lend_token.address)
#     )
#     U_token = get_contract(
#         'contracts/templates/ERC1155Template2.v.py',
#         interfaces=['ERC1155TokenReceiver'],
#         address=CurrencyDaoContract.currencies__u_currency_address(Lend_token.address)
#     )
#     # assign one of the accounts as a High_Risk_Insurer
#     High_Risk_Insurer = accounts[2]
#     # High_Risk_Insurer purchases 100 i_tokens from UnderwriterPool
#     tx_hash = UnderwriterPool.purchase_i_currency(H20, Borrow_token.address,
#         _strike_price, 100 * 10 ** 18, 0, {'from': High_Risk_Insurer})
#     tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
#     assert tx_receipt['status'] == 1
#     # High_Risk_Insurer purchases 2 s_tokens from UnderwriterPool
#     tx_hash = UnderwriterPool.purchase_s_currency(H20, Borrow_token.address,
#         _strike_price, 2 * 10 ** 18, 0, {'from': High_Risk_Insurer})
#     tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
#     assert tx_receipt['status'] == 1
#     # assign one of the accounts as a Borrower
#     Borrower = accounts[3]
#     # Borrower purchases 10 Borrow_tokens from a 3rd party exchange
#     tx_hash = Borrow_token.transfer(Borrower, 10 * 10 ** 18, {'from': owner})
#     tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
#     assert tx_receipt['status'] == 1
#     assert Borrow_token.balanceOf(Borrower) == 10 * 10 ** 18
#     # Borrower authorizes CurrencyDaoContract to spend 2 Borrow_tokens
#     tx_hash = Borrow_token.approve(CurrencyDaoContract.address, 3 * (10 ** 18),
#         {'from': Borrower})
#     tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
#     assert tx_receipt['status'] == 1
#     # Borrower deposits 2 Borrow_tokens to Currency Pool and gets l_tokens
#     tx_hash = CurrencyDaoContract.currency_to_l_currency(Borrow_token.address, 3 * 10 ** 18,
#         {'from': Borrower, 'gas': 200000})
#     tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
#     assert tx_receipt['status'] == 1
#     # Borrower wishes to avail a loan of 400 Lend_tokens
#     # High_Risk_Insurer authorizes CurrencyDaoContract to spend his S_token
#     tx_hash = S_token.setApprovalForAll(CurrencyDaoContract.address, True,
#         {'from': High_Risk_Insurer})
#     tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
#     assert tx_receipt['status'] == 1
#     # High_Risk_Insurer authorizes CurrencyDaoContract to spend his I_token
#     tx_hash = I_token.setApprovalForAll(CurrencyDaoContract.address, True,
#         {'from': High_Risk_Insurer})
#     tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
#     assert tx_receipt['status'] == 1
#     # High_Risk_Insurer sets an offer of 2 s_tokens for 20 i_tokens
#     assert PositionRegistryContract.last_offer_index() == 0
#     tx_hash = PositionRegistryContract.create_offer(
#         Lend_token.address, H20, Borrow_token.address, _strike_price,
#         2, 20, 5 * 10 ** 15,
#         {'from': High_Risk_Insurer, 'gas': 450000})
#     tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
#     assert tx_receipt['status'] == 1
#     # Borrower purchases this offer for the amount of 0.1 ETH
#     # 20 i_tokens and 2 s_tokens are transferred from High_Risk_Insurer account to MarketDaoContract
#     tx_hash = PositionRegistryContract.avail_loan(0,
#         {'from': Borrower, 'value': 10 ** 17, 'gas': 950000})
#     tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
#     assert tx_receipt['status'] == 1
#     # verify Lend_token balance of Borrower
#     assert Lend_token.balanceOf(Borrower) == 400 * 10 ** 18
#     # get Auction contract
#     _loan_market_hash = CollateralAuctionDao.loan_market_hash(
#         Lend_token.address, H20, Borrow_token.address
#     )
#     Auction = get_contract(
#         'contracts/templates/SimpleCollateralAuctionGraph.v.py',
#         interfaces=['ERC20', 'MarketDaoContract'],
#         address=CollateralAuctionDao.graphs(_loan_market_hash)
#     )
#     time_travel(H20)
#     # update price feed
#     tx_hash = PriceFeed.set_price(240 * 10 ** 18, {'from': owner})
#     tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
#     assert tx_receipt['status'] == 1
#     # assign one of the accounts as a _loan_market_settler
#     _loan_market_settler = accounts[3]
#     assert MarketDaoContract.loan_markets__status(_loan_market_hash) == MarketDaoContract.LOAN_MARKET_STATUS_OPEN()
#     assert MarketDaoContract.loan_markets__currency_value_per_underlying_at_expiry(_loan_market_hash) == 0
#     assert MarketDaoContract.loan_markets__total_outstanding_currency_value_at_expiry(_loan_market_hash) == 400 * 10 ** 18
#     assert MarketDaoContract.loan_markets__total_outstanding_underlying_value_at_expiry(_loan_market_hash) == 2 * 10 ** 18
#     tx_hash = MarketDaoContract.settle_loan_market(_loan_market_hash, {'from': _loan_market_settler, 'gas': 280000})
#     tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
#     assert tx_receipt['status'] == 1
#     assert MarketDaoContract.loan_markets__status(_loan_market_hash) == MarketDaoContract.LOAN_MARKET_STATUS_SETTLING()
#     assert MarketDaoContract.loan_markets__currency_value_per_underlying_at_expiry(_loan_market_hash) == 240 * 10 ** 18
#     assert MarketDaoContract.loan_markets__total_outstanding_currency_value_at_expiry(_loan_market_hash) == 400 * 10 ** 18
#     assert MarketDaoContract.loan_markets__total_outstanding_underlying_value_at_expiry(_loan_market_hash) == 2 * 10 ** 18
#     # assign one of the accounts as an _auctioned_collateral_purchaser
#     _auctioned_collateral_purchaser = accounts[4]
#     # _auctioned_collateral_purchaser buys 1000 lend token from a 3rd party exchange
#     tx_hash = Lend_token.transfer(_auctioned_collateral_purchaser, 1000 * 10 ** 18, {'from': owner})
#     tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
#     assert tx_receipt['status'] == 1
#     # _auctioned_collateral_purchaser authorizes CurrencyDaoContract to spend 800 lend currency
#     tx_hash = Lend_token.approve(CurrencyDaoContract.address, 800 * (10 ** 18),
#         {'from': _auctioned_collateral_purchaser})
#     tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
#     assert tx_receipt['status'] == 1
#     time_travel(H20 + 10 * 60)
#     # _auctioned_collateral_purchaser purchases 1.5 Borrow_tokens for 210.6 Lend_tokens
#     assert Auction.is_active() == True
#     assert Auction.current_price() == 216.32 * 10 ** 18
#     assert Auction.currency_value_remaining() == 400 * 10 ** 18
#     assert MarketDaoContract.loan_markets__total_currency_raised_during_auction(_loan_market_hash) == 0
#     assert MarketDaoContract.loan_markets__total_underlying_sold_during_auction(_loan_market_hash) == 0
#     assert MarketDaoContract.loan_markets__underlying_settlement_price_per_currency(_loan_market_hash) == 0
#     _underlying_value = Auction.currency_value_remaining() / Auction.current_price()
#     tx_hash = Auction.purchase(Web3.toWei(_underlying_value, 'ether'), {'from': _auctioned_collateral_purchaser, 'gas': 220000})
#     tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
#     assert tx_receipt['status'] == 1
#     assert MarketDaoContract.loan_markets__total_currency_raised_during_auction(_loan_market_hash) == 400 * 10 ** 18 - Auction.currency_value_remaining()
#     assert MarketDaoContract.loan_markets__total_underlying_sold_during_auction(_loan_market_hash) == Web3.toWei(_underlying_value, 'ether')
#     assert MarketDaoContract.loan_markets__underlying_settlement_price_per_currency(_loan_market_hash) == 0
#     tx_hash = Auction.purchase_for_remaining_currency({'from': _auctioned_collateral_purchaser, 'gas': 280000})
#     tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
#     assert tx_receipt['status'] == 1
#     assert Auction.is_active() == False
#     assert MarketDaoContract.loan_markets__status(_loan_market_hash) == MarketDaoContract.LOAN_MARKET_STATUS_CLOSED()
#     assert MarketDaoContract.loan_markets__total_currency_raised_during_auction(_loan_market_hash) == 400 * 10 ** 18
#     assert MarketDaoContract.loan_markets__total_underlying_sold_during_auction(_loan_market_hash) == 1849586800695850701
#     assert MarketDaoContract.loan_markets__underlying_settlement_price_per_currency(_loan_market_hash) == 216264519107463452257
#
#
# def test_l_token_balances_until_loan_market_settlement_for_expiry_price_below_original_price(accounts, get_contract, get_log_args, time_travel,
#         LST_token, Lend_token, Borrow_token, Malicious_token,
#         ERC20_library, ERC1155_library,
#         CurrencyPool_library, CurrencyDaoContract,
#         InterestPool_library, InterestPoolDaoContract,
#         UnderwriterPool_library, UnderwriterPoolDaoContract,
#         CollateralAuctionGraph_Library, CollateralAuctionDao,
#         ShieldPayoutDaoContract,
#         PositionRegistryContract,
#         PriceFeed,
#         PriceOracle,
#         MarketDaoContract
#     ):
#     owner = accounts[0]
#     _initialize_all_daos(owner, accounts,
#         LST_token, Lend_token, Borrow_token,
#         ERC20_library, ERC1155_library,
#         CurrencyPool_library, CurrencyDaoContract,
#         InterestPool_library, InterestPoolDaoContract,
#         UnderwriterPool_library, UnderwriterPoolDaoContract,
#         CollateralAuctionGraph_Library, CollateralAuctionDao,
#         ShieldPayoutDaoContract,
#         PositionRegistryContract,
#         PriceOracle,
#         MarketDaoContract
#     )
#     # set_offer_registration_fee_lookup()
#     _minimum_fee = 100
#     _minimum_interval = 10
#     _fee_multiplier = 2000
#     _fee_multiplier_decimals = 1000
#     tx_hash = UnderwriterPoolDaoContract.set_offer_registration_fee_lookup(_minimum_fee,
#         _minimum_interval, _fee_multiplier, _fee_multiplier_decimals,
#         {'from': owner})
#     tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
#     assert tx_receipt['status'] == 1
#     # set_currency_support for Lend_token in CurrencyDaoContract
#     tx_hash = CurrencyDaoContract.set_currency_support(Lend_token.address, True,
#         {'from': owner, 'gas': 1570000})
#     tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
#     assert tx_receipt['status'] == 1
#     # set_currency_support for Borrow_token in CurrencyDaoContract
#     tx_hash = CurrencyDaoContract.set_currency_support(Borrow_token.address, True,
#         {'from': owner, 'gas': 1570000})
#     tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
#     assert tx_receipt['status'] == 1
#     # register_pool for Lend_token
#     pool_owner = accounts[1]
#     tx_hash = UnderwriterPoolDaoContract.register_pool(Lend_token.address,
#         'Underwriter Pool A', 'UPA', 50,
#         {'from': pool_owner, 'gas': 850000})
#     tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
#     assert tx_receipt['status'] == 1
#     # get UnderwriterPool contract
#     logs_8 = get_log_args(tx_hash, UnderwriterPoolDaoContract, "PoolRegistered")
#     _pool_hash = UnderwriterPoolDaoContract.pool_hash(Lend_token.address, logs_8[0].args._pool_address)
#     UnderwriterPool = get_contract(
#         'contracts/templates/UnderwriterPoolTemplate1.v.py',
#         interfaces=[
#             'ERC20', 'ERC1155', 'ERC1155TokenReceiver', 'UnderwriterPoolDaoContract'
#         ],
#         address=UnderwriterPoolDaoContract.pools__pool_address(_pool_hash)
#     )
#     # get UnderwriterPoolCurrency
#     UnderwriterPoolCurrency = get_contract(
#         'contracts/templates/ERC20Template1.v.py',
#         address=UnderwriterPool.pool_currency_address()
#     )
#     # pool_owner buys LST from a 3rd party
#     LST_token.transfer(pool_owner, Web3.toWei(1000, 'ether'), {'from': owner})
#     # pool_owner authorizes CurrencyDaoContract to spend LST required for offer_registration_fee
#     tx_hash = LST_token.approve(CurrencyDaoContract.address, UnderwriterPoolDaoContract.offer_registration_fee() * (10 ** 18),
#         {'from': pool_owner})
#     tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
#     assert tx_receipt['status'] == 1
#     # pool_owner registers an expiry : Last Thursday of December 2019, i.e., December 26th, 2019, i.e., H20
#     _strike_price = Web3.toWei(200, 'ether')
#     tx_hash = UnderwriterPool.register_expiry(H20, Borrow_token.address,
#         _strike_price, {'from': pool_owner, 'gas': 2600000})
#     tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
#     assert tx_receipt['status'] == 1
#     # get L_currency_token
#     L_currency_token = get_contract(
#         'contracts/templates/ERC20Template1.v.py',
#         address=CurrencyDaoContract.currencies__l_currency_address(Lend_token.address)
#     )
#     _currency_pool_hash = CurrencyDaoContract.pool_hash(Lend_token.address)
#     # get L_underlying_token
#     L_underlying_token = get_contract(
#         'contracts/templates/ERC20Template1.v.py',
#         address=CurrencyDaoContract.currencies__l_currency_address(Borrow_token.address)
#     )
#     _underlying_pool_hash = CurrencyDaoContract.pool_hash(Borrow_token.address)
#     # assign one of the accounts as a Lender
#     Lender = accounts[2]
#     # Lender buys 1000 lend token from a 3rd party exchange
#     tx_hash = Lend_token.transfer(Lender, Web3.toWei(1000, 'ether'), {'from': owner})
#     tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
#     assert tx_receipt['status'] == 1
#     # Lender authorizes CurrencyDaoContract to spend 800 lend currency
#     tx_hash = Lend_token.approve(CurrencyDaoContract.address, Web3.toWei(800, 'ether'),
#         {'from': Lender})
#     tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
#     assert tx_receipt['status'] == 1
#     # verify l_lend_currency supply and lend_currency_balance
#     assert L_currency_token.totalSupply() == 0
#     assert Lend_token.balanceOf(CurrencyDaoContract.pools__pool_address(_currency_pool_hash)) == 0
#     # Lender deposits 800 Lend_tokens to Currency Pool and gets l_tokens
#     tx_hash = CurrencyDaoContract.currency_to_l_currency(Lend_token.address, Web3.toWei(800, 'ether'),
#         {'from': Lender, 'gas': 200000})
#     tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
#     assert tx_receipt['status'] == 1
#     # verify l_lend_currency supply, l_lend_currency balance and lend_currency balance
#     assert L_currency_token.totalSupply() == Web3.toWei(800, 'ether')
#     assert L_currency_token.balanceOf(Lender) == Web3.toWei(800, 'ether')
#     assert L_currency_token.balanceOf(UnderwriterPool.address) == 0
#     assert Lend_token.balanceOf(CurrencyDaoContract.pools__pool_address(_currency_pool_hash)) == Web3.toWei(800, 'ether')
#     # Lender purchases UnderwriterPoolCurrency for 800 L_tokens
#     # Lender gets 40000 UnderwriterPoolCurrency tokens
#     # 800 L_tokens are deposited into UnderwriterPool account
#     tx_hash = UnderwriterPool.purchase_pool_currency(Web3.toWei(800, 'ether'), {'from': Lender})
#     tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
#     assert tx_receipt['status'] == 1
#     # verify l_lend_currency supply, l_lend_currency balance and lend_currency balance
#     assert L_currency_token.totalSupply() == Web3.toWei(800, 'ether')
#     assert L_currency_token.balanceOf(Lender) == 0
#     assert L_currency_token.balanceOf(UnderwriterPool.address) == Web3.toWei(800, 'ether')
#     assert Lend_token.balanceOf(CurrencyDaoContract.pools__pool_address(_currency_pool_hash)) == Web3.toWei(800, 'ether')
#     # vefiry shield_currency_price is not set
#     multi_fungible_addresses = CurrencyDaoContract.multi_fungible_addresses(Lend_token.address)
#     _s_hash = UnderwriterPoolDaoContract.multi_fungible_currency_hash(
#         multi_fungible_addresses[3], Lend_token.address, H20,
#         Borrow_token.address, _strike_price)
#     _i_hash = UnderwriterPoolDaoContract.multi_fungible_currency_hash(
#         multi_fungible_addresses[1], Lend_token.address, H20, ZERO_ADDRESS, 0)
#     # pool_owner initiates offer of 600 I_tokens from the UnderwriterPool
#     # 600 L_tokens burned from UnderwriterPool account
#     # 600 I_tokens, 3 S_tokens, and 3 U_tokens minted to UnderwriterPool account
#     tx_hash = UnderwriterPool.increment_i_currency_supply(
#         H20, Borrow_token.address, _strike_price, Web3.toWei(600, 'ether'),
#         {'from': pool_owner, 'gas': 600000})
#     tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
#     assert tx_receipt['status'] == 1
#     # verify l_lend_currency supply, l_lend_currency balance and lend_currency balance
#     assert L_currency_token.totalSupply() == Web3.toWei(200, 'ether')
#     assert L_currency_token.balanceOf(UnderwriterPool.address) == Web3.toWei(200, 'ether')
#     assert Lend_token.balanceOf(CurrencyDaoContract.pools__pool_address(_currency_pool_hash)) == Web3.toWei(800, 'ether')
#     # get I_token
#     I_token = get_contract(
#         'contracts/templates/ERC1155Template2.v.py',
#         interfaces=['ERC1155TokenReceiver'],
#         address=CurrencyDaoContract.currencies__i_currency_address(Lend_token.address)
#     )
#     S_token = get_contract(
#         'contracts/templates/ERC1155Template2.v.py',
#         interfaces=['ERC1155TokenReceiver'],
#         address=CurrencyDaoContract.currencies__s_currency_address(Lend_token.address)
#     )
#     U_token = get_contract(
#         'contracts/templates/ERC1155Template2.v.py',
#         interfaces=['ERC1155TokenReceiver'],
#         address=CurrencyDaoContract.currencies__u_currency_address(Lend_token.address)
#     )
#     # assign one of the accounts as a High_Risk_Insurer
#     High_Risk_Insurer = accounts[2]
#     # High_Risk_Insurer purchases 100 i_tokens from UnderwriterPool
#     tx_hash = UnderwriterPool.purchase_i_currency(H20, Borrow_token.address,
#         _strike_price, Web3.toWei(100, 'ether'), 0, {'from': High_Risk_Insurer})
#     tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
#     assert tx_receipt['status'] == 1
#     # High_Risk_Insurer purchases 2 s_tokens from UnderwriterPool
#     tx_hash = UnderwriterPool.purchase_s_currency(H20, Borrow_token.address,
#         _strike_price, Web3.toWei(2, 'ether'), 0, {'from': High_Risk_Insurer})
#     tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
#     assert tx_receipt['status'] == 1
#     # assign one of the accounts as a Borrower
#     Borrower = accounts[3]
#     # Borrower purchases 10 Borrow_tokens from a 3rd party exchange
#     tx_hash = Borrow_token.transfer(Borrower, Web3.toWei(10, 'ether'), {'from': owner})
#     tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
#     assert tx_receipt['status'] == 1
#     assert Borrow_token.balanceOf(Borrower) == Web3.toWei(10, 'ether')
#     # Borrower authorizes CurrencyDaoContract to spend 2 Borrow_tokens
#     tx_hash = Borrow_token.approve(CurrencyDaoContract.address, Web3.toWei(3, 'ether'),
#         {'from': Borrower})
#     tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
#     assert tx_receipt['status'] == 1
#     # verify l_borrow_currency supply, l_borrow_currency balance and borrow_currency balance
#     assert L_underlying_token.totalSupply() == 0
#     assert L_underlying_token.balanceOf(Borrower) == 0
#     assert L_underlying_token.balanceOf(UnderwriterPool.address) == 0
#     assert Borrow_token.balanceOf(CurrencyDaoContract.pools__pool_address(_underlying_pool_hash)) == 0
#     # Borrower deposits 3 Borrow_tokens to Currency Pool and gets l_tokens
#     tx_hash = CurrencyDaoContract.currency_to_l_currency(Borrow_token.address, Web3.toWei(3, 'ether'),
#         {'from': Borrower, 'gas': 200000})
#     tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
#     assert tx_receipt['status'] == 1
#     # verify l_borrow_currency supply, l_borrow_currency balance and borrow_currency balance
#     assert L_underlying_token.totalSupply() == Web3.toWei(3, 'ether')
#     assert L_underlying_token.balanceOf(Borrower) == Web3.toWei(3, 'ether')
#     assert L_underlying_token.balanceOf(MarketDaoContract.address) == 0
#     assert Borrow_token.balanceOf(CurrencyDaoContract.pools__pool_address(_underlying_pool_hash)) == Web3.toWei(3, 'ether')
#     # Borrower wishes to avail a loan of 400 Lend_tokens
#     # High_Risk_Insurer authorizes CurrencyDaoContract to spend his S_token
#     tx_hash = S_token.setApprovalForAll(CurrencyDaoContract.address, True,
#         {'from': High_Risk_Insurer})
#     tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
#     assert tx_receipt['status'] == 1
#     # High_Risk_Insurer authorizes CurrencyDaoContract to spend his I_token
#     tx_hash = I_token.setApprovalForAll(CurrencyDaoContract.address, True,
#         {'from': High_Risk_Insurer})
#     tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
#     assert tx_receipt['status'] == 1
#     # High_Risk_Insurer sets an offer of 2 s_tokens for 20 i_tokens
#     assert PositionRegistryContract.last_offer_index() == 0
#     tx_hash = PositionRegistryContract.create_offer(
#         Lend_token.address, H20, Borrow_token.address, _strike_price,
#         2, 20, 5 * 10 ** 15,
#         {'from': High_Risk_Insurer, 'gas': 450000})
#     tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
#     assert tx_receipt['status'] == 1
#     # verify l_lend_currency supply, l_lend_currency balance and lend_currency balance
#     assert L_currency_token.totalSupply() == Web3.toWei(200, 'ether')
#     assert L_currency_token.balanceOf(UnderwriterPool.address) == Web3.toWei(200, 'ether')
#     assert Lend_token.balanceOf(CurrencyDaoContract.pools__pool_address(_currency_pool_hash)) == Web3.toWei(800, 'ether')
#     # Borrower purchases this offer for the amount of 0.1 ETH
#     # 20 i_tokens and 2 s_tokens are transferred from High_Risk_Insurer account to MarketDaoContract
#     tx_hash = PositionRegistryContract.avail_loan(0,
#         {'from': Borrower, 'value': 10 ** 17, 'gas': 950000})
#     tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
#     assert tx_receipt['status'] == 1
#     # verify l_lend_currency supply, l_lend_currency balance and lend_currency balance
#     assert L_currency_token.totalSupply() == Web3.toWei(200, 'ether')
#     assert L_currency_token.balanceOf(UnderwriterPool.address) == Web3.toWei(200, 'ether')
#     assert Lend_token.balanceOf(CurrencyDaoContract.pools__pool_address(_currency_pool_hash)) == Web3.toWei(400, 'ether')
#     # verify Lend_token balance of Borrower
#     assert Lend_token.balanceOf(Borrower) == Web3.toWei(400, 'ether')
#     # verify l_borrow_currency supply, l_borrow_currency balance and borrow_currency balance
#     assert L_underlying_token.totalSupply() == Web3.toWei(3, 'ether')
#     assert L_underlying_token.balanceOf(Borrower) == Web3.toWei(1, 'ether')
#     assert L_underlying_token.balanceOf(MarketDaoContract.address) == Web3.toWei(2, 'ether')
#     assert Borrow_token.balanceOf(CurrencyDaoContract.pools__pool_address(_underlying_pool_hash)) == Web3.toWei(3, 'ether')
#     # get Auction contract
#     _loan_market_hash = CollateralAuctionDao.loan_market_hash(
#         Lend_token.address, H20, Borrow_token.address
#     )
#     Auction = get_contract(
#         'contracts/templates/SimpleCollateralAuctionGraph.v.py',
#         interfaces=['ERC20', 'MarketDaoContract'],
#         address=CollateralAuctionDao.graphs(_loan_market_hash)
#     )
#     time_travel(H20)
#     # update price feed
#     tx_hash = PriceFeed.set_price(Web3.toWei(150, 'ether'), {'from': owner})
#     tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
#     assert tx_receipt['status'] == 1
#     # assign one of the accounts as a _loan_market_settler
#     _loan_market_settler = accounts[3]
#     assert MarketDaoContract.loan_markets__status(_loan_market_hash) == MarketDaoContract.LOAN_MARKET_STATUS_OPEN()
#     assert MarketDaoContract.loan_markets__currency_value_per_underlying_at_expiry(_loan_market_hash) == 0
#     assert MarketDaoContract.loan_markets__total_outstanding_currency_value_at_expiry(_loan_market_hash) == Web3.toWei(400, 'ether')
#     assert MarketDaoContract.loan_markets__total_outstanding_underlying_value_at_expiry(_loan_market_hash) == Web3.toWei(2, 'ether')
#     # verify l_lend_currency supply, l_lend_currency balance and lend_currency balance
#     assert L_currency_token.totalSupply() == Web3.toWei(200, 'ether')
#     assert L_currency_token.balanceOf(UnderwriterPool.address) == Web3.toWei(200, 'ether')
#     assert Lend_token.balanceOf(CurrencyDaoContract.pools__pool_address(_currency_pool_hash)) == Web3.toWei(400, 'ether')
#     # verify l_borrow_currency supply, l_borrow_currency balance and borrow_currency balance
#     assert L_underlying_token.totalSupply() == Web3.toWei(3, 'ether')
#     assert L_underlying_token.balanceOf(Borrower) == Web3.toWei(1, 'ether')
#     assert L_underlying_token.balanceOf(MarketDaoContract.address) == Web3.toWei(2, 'ether')
#     assert Borrow_token.balanceOf(Auction.address) == 0
#     assert Borrow_token.balanceOf(CurrencyDaoContract.pools__pool_address(_underlying_pool_hash)) == Web3.toWei(3, 'ether')
#     tx_hash = MarketDaoContract.settle_loan_market(_loan_market_hash, {'from': _loan_market_settler, 'gas': 280000})
#     tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
#     assert tx_receipt['status'] == 1
#     assert MarketDaoContract.loan_markets__status(_loan_market_hash) == MarketDaoContract.LOAN_MARKET_STATUS_SETTLING()
#     assert MarketDaoContract.loan_markets__currency_value_per_underlying_at_expiry(_loan_market_hash) == Web3.toWei(150, 'ether')
#     assert MarketDaoContract.loan_markets__total_outstanding_currency_value_at_expiry(_loan_market_hash) == Web3.toWei(400, 'ether')
#     assert MarketDaoContract.loan_markets__total_outstanding_underlying_value_at_expiry(_loan_market_hash) == Web3.toWei(2, 'ether')
#     # verify l_lend_currency supply, l_lend_currency balance and lend_currency balance
#     assert L_currency_token.totalSupply() == Web3.toWei(200, 'ether')
#     assert L_currency_token.balanceOf(UnderwriterPool.address) == Web3.toWei(200, 'ether')
#     assert Lend_token.balanceOf(CurrencyDaoContract.pools__pool_address(_currency_pool_hash)) == Web3.toWei(400, 'ether')
#     # verify l_borrow_currency supply, l_borrow_currency balance and borrow_currency balance
#     assert L_underlying_token.totalSupply() == Web3.toWei(1, 'ether')
#     assert L_underlying_token.balanceOf(Borrower) == Web3.toWei(1, 'ether')
#     assert L_underlying_token.balanceOf(MarketDaoContract.address) == 0
#     assert Borrow_token.balanceOf(Auction.address) == Web3.toWei(2, 'ether')
#     assert Borrow_token.balanceOf(CurrencyDaoContract.pools__pool_address(_underlying_pool_hash)) == Web3.toWei(1, 'ether')
#     # assign one of the accounts as an _auctioned_collateral_purchaser
#     _auctioned_collateral_purchaser = accounts[4]
#     # _auctioned_collateral_purchaser buys 1000 lend token from a 3rd party exchange
#     tx_hash = Lend_token.transfer(_auctioned_collateral_purchaser, 1000 * 10 ** 18, {'from': owner})
#     tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
#     assert tx_receipt['status'] == 1
#     # _auctioned_collateral_purchaser authorizes CurrencyDaoContract to spend 800 lend currency
#     tx_hash = Lend_token.approve(CurrencyDaoContract.address, 800 * (10 ** 18),
#         {'from': _auctioned_collateral_purchaser})
#     tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
#     assert tx_receipt['status'] == 1
#     time_travel(H20 + 10 * 60)
#     assert Auction.is_active() == True
#     assert Auction.current_price() == Web3.toWei(135.2, 'ether')
#     assert Auction.currency_value_remaining() == Web3.toWei(400, 'ether')
#     assert MarketDaoContract.loan_markets__total_currency_raised_during_auction(_loan_market_hash) == 0
#     assert MarketDaoContract.loan_markets__total_underlying_sold_during_auction(_loan_market_hash) == 0
#     assert MarketDaoContract.loan_markets__underlying_settlement_price_per_currency(_loan_market_hash) == 0
#     # verify l_lend_currency supply, l_lend_currency balance and lend_currency balance
#     assert L_currency_token.totalSupply() == Web3.toWei(200, 'ether')
#     assert L_currency_token.balanceOf(UnderwriterPool.address) == Web3.toWei(200, 'ether')
#     assert Lend_token.balanceOf(CurrencyDaoContract.pools__pool_address(_currency_pool_hash)) == Web3.toWei(400, 'ether')
#     # verify l_borrow_currency supply, l_borrow_currency balance and borrow_currency balance
#     assert L_underlying_token.totalSupply() == Web3.toWei(1, 'ether')
#     assert L_underlying_token.balanceOf(Borrower) == Web3.toWei(1, 'ether')
#     assert Borrow_token.balanceOf(Auction.address) == Web3.toWei(2, 'ether')
#     assert Borrow_token.balanceOf(CurrencyDaoContract.pools__pool_address(_underlying_pool_hash)) == Web3.toWei(1, 'ether')
#     # _auctioned_collateral_purchaser purchases all of the 2 Borrow_tokens for current price of Lend_tokens
#     tx_hash = Auction.purchase_for_remaining_currency({'from': _auctioned_collateral_purchaser, 'gas': 280000})
#     tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
#     assert tx_receipt['status'] == 1
#     assert Auction.is_active() == False
#     assert MarketDaoContract.loan_markets__status(_loan_market_hash) == MarketDaoContract.LOAN_MARKET_STATUS_CLOSED()
#     assert MarketDaoContract.loan_markets__total_currency_raised_during_auction(_loan_market_hash) == 270330666666666666666
#     assert MarketDaoContract.loan_markets__total_underlying_sold_during_auction(_loan_market_hash) == Web3.toWei(2, 'ether')
#     assert MarketDaoContract.loan_markets__underlying_settlement_price_per_currency(_loan_market_hash) == 135165333333333333333
#     # verify l_lend_currency supply, l_lend_currency balance and lend_currency balance
#     assert L_currency_token.totalSupply() == Web3.toWei(200, 'ether')
#     assert L_currency_token.balanceOf(UnderwriterPool.address) == Web3.toWei(200, 'ether')
#     assert Lend_token.balanceOf(CurrencyDaoContract.pools__pool_address(_currency_pool_hash)) == 670330666666666666666
#     # verify l_borrow_currency supply, l_borrow_currency balance and borrow_currency balance
#     assert L_underlying_token.totalSupply() == Web3.toWei(1, 'ether')
#     assert L_underlying_token.balanceOf(Borrower) == Web3.toWei(1, 'ether')
#     assert Borrow_token.balanceOf(Auction.address) == 0
#     assert Borrow_token.balanceOf(CurrencyDaoContract.pools__pool_address(_underlying_pool_hash)) == Web3.toWei(1, 'ether')
#
#
# def test_close_liquidated_loan_for_settlement_price_below_original_price(accounts, get_contract, get_log_args, time_travel,
#         LST_token, Lend_token, Borrow_token, Malicious_token,
#         ERC20_library, ERC1155_library,
#         CurrencyPool_library, CurrencyDaoContract,
#         InterestPool_library, InterestPoolDaoContract,
#         UnderwriterPool_library, UnderwriterPoolDaoContract,
#         CollateralAuctionGraph_Library, CollateralAuctionDao,
#         ShieldPayoutDaoContract,
#         PositionRegistryContract,
#         PriceFeed,
#         PriceOracle,
#         MarketDaoContract
#     ):
#     owner = accounts[0]
#     _initialize_all_daos(owner, accounts,
#         LST_token, Lend_token, Borrow_token,
#         ERC20_library, ERC1155_library,
#         CurrencyPool_library, CurrencyDaoContract,
#         InterestPool_library, InterestPoolDaoContract,
#         UnderwriterPool_library, UnderwriterPoolDaoContract,
#         CollateralAuctionGraph_Library, CollateralAuctionDao,
#         ShieldPayoutDaoContract,
#         PositionRegistryContract,
#         PriceOracle,
#         MarketDaoContract
#     )
#     # set_offer_registration_fee_lookup()
#     _minimum_fee = 100
#     _minimum_interval = 10
#     _fee_multiplier = 2000
#     _fee_multiplier_decimals = 1000
#     tx_hash = UnderwriterPoolDaoContract.set_offer_registration_fee_lookup(_minimum_fee,
#         _minimum_interval, _fee_multiplier, _fee_multiplier_decimals,
#         {'from': owner})
#     tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
#     assert tx_receipt['status'] == 1
#     # set_currency_support for Lend_token in CurrencyDaoContract
#     tx_hash = CurrencyDaoContract.set_currency_support(Lend_token.address, True,
#         {'from': owner, 'gas': 1570000})
#     tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
#     assert tx_receipt['status'] == 1
#     # set_currency_support for Borrow_token in CurrencyDaoContract
#     tx_hash = CurrencyDaoContract.set_currency_support(Borrow_token.address, True,
#         {'from': owner, 'gas': 1570000})
#     tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
#     assert tx_receipt['status'] == 1
#     # register_pool for Lend_token
#     pool_owner = accounts[1]
#     tx_hash = UnderwriterPoolDaoContract.register_pool(Lend_token.address,
#         'Underwriter Pool A', 'UPA', 50,
#         {'from': pool_owner, 'gas': 850000})
#     tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
#     assert tx_receipt['status'] == 1
#     # get UnderwriterPool contract
#     logs_8 = get_log_args(tx_hash, UnderwriterPoolDaoContract, "PoolRegistered")
#     _pool_hash = UnderwriterPoolDaoContract.pool_hash(Lend_token.address, logs_8[0].args._pool_address)
#     UnderwriterPool = get_contract(
#         'contracts/templates/UnderwriterPoolTemplate1.v.py',
#         interfaces=[
#             'ERC20', 'ERC1155', 'ERC1155TokenReceiver', 'UnderwriterPoolDaoContract'
#         ],
#         address=UnderwriterPoolDaoContract.pools__pool_address(_pool_hash)
#     )
#     # get UnderwriterPoolCurrency
#     UnderwriterPoolCurrency = get_contract(
#         'contracts/templates/ERC20Template1.v.py',
#         address=UnderwriterPool.pool_currency_address()
#     )
#     # pool_owner buys LST from a 3rd party
#     LST_token.transfer(pool_owner, Web3.toWei(1000, 'ether'), {'from': owner})
#     # pool_owner authorizes CurrencyDaoContract to spend LST required for offer_registration_fee
#     tx_hash = LST_token.approve(CurrencyDaoContract.address, Web3.toWei(UnderwriterPoolDaoContract.offer_registration_fee(), 'ether'),
#         {'from': pool_owner})
#     tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
#     assert tx_receipt['status'] == 1
#     # pool_owner registers an expiry : Last Thursday of December 2019, i.e., December 26th, 2019, i.e., H20
#     _strike_price = Web3.toWei(200, 'ether')
#     tx_hash = UnderwriterPool.register_expiry(H20, Borrow_token.address,
#         _strike_price, {'from': pool_owner, 'gas': 2600000})
#     tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
#     assert tx_receipt['status'] == 1
#     # get L_currency_token
#     L_currency_token = get_contract(
#         'contracts/templates/ERC20Template1.v.py',
#         address=CurrencyDaoContract.currencies__l_currency_address(Lend_token.address)
#     )
#     _currency_pool_hash = CurrencyDaoContract.pool_hash(Lend_token.address)
#     # get L_underlying_token
#     L_underlying_token = get_contract(
#         'contracts/templates/ERC20Template1.v.py',
#         address=CurrencyDaoContract.currencies__l_currency_address(Borrow_token.address)
#     )
#     _underlying_pool_hash = CurrencyDaoContract.pool_hash(Borrow_token.address)
#     # assign one of the accounts as a Lender
#     Lender = accounts[2]
#     # Lender buys 1000 lend token from a 3rd party exchange
#     tx_hash = Lend_token.transfer(Lender, Web3.toWei(1000, 'ether'), {'from': owner})
#     tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
#     assert tx_receipt['status'] == 1
#     # Lender authorizes CurrencyDaoContract to spend 800 lend currency
#     tx_hash = Lend_token.approve(CurrencyDaoContract.address, Web3.toWei(800, 'ether'),
#         {'from': Lender})
#     tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
#     assert tx_receipt['status'] == 1
#     # Lender deposits 800 Lend_tokens to Currency Pool and gets l_tokens
#     assert L_currency_token.totalSupply() == 0
#     assert Lend_token.balanceOf(CurrencyDaoContract.pools__pool_address(_currency_pool_hash)) == 0
#     tx_hash = CurrencyDaoContract.currency_to_l_currency(Lend_token.address, Web3.toWei(800, 'ether'),
#         {'from': Lender, 'gas': 200000})
#     tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
#     assert tx_receipt['status'] == 1
#     # verify l_lend_currency supply, l_lend_currency balance and lend_currency balance
#     assert L_currency_token.totalSupply() == Web3.toWei(800, 'ether')
#     assert L_currency_token.balanceOf(Lender) == Web3.toWei(800, 'ether')
#     assert L_currency_token.balanceOf(UnderwriterPool.address) == 0
#     # Lender purchases UnderwriterPoolCurrency for 800 L_tokens
#     # Lender gets 40000 UnderwriterPoolCurrency tokens
#     # 800 L_tokens are deposited into UnderwriterPool account
#     tx_hash = UnderwriterPool.purchase_pool_currency(Web3.toWei(800, 'ether'), {'from': Lender})
#     tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
#     assert tx_receipt['status'] == 1
#     # verify l_lend_currency supply, l_lend_currency balance and lend_currency balance
#     assert L_currency_token.totalSupply() == Web3.toWei(800, 'ether')
#     assert L_currency_token.balanceOf(Lender) == 0
#     assert L_currency_token.balanceOf(UnderwriterPool.address) == Web3.toWei(800, 'ether')
#     # vefiry shield_currency_price is not set
#     multi_fungible_addresses = CurrencyDaoContract.multi_fungible_addresses(Lend_token.address)
#     _s_hash = UnderwriterPoolDaoContract.multi_fungible_currency_hash(
#         multi_fungible_addresses[3], Lend_token.address, H20,
#         Borrow_token.address, _strike_price)
#     _i_hash = UnderwriterPoolDaoContract.multi_fungible_currency_hash(
#         multi_fungible_addresses[1], Lend_token.address, H20, ZERO_ADDRESS, 0)
#     # pool_owner initiates offer of 600 I_tokens from the UnderwriterPool
#     # 600 L_tokens burned from UnderwriterPool account
#     # 600 I_tokens, 3 S_tokens, and 3 U_tokens minted to UnderwriterPool account
#     tx_hash = UnderwriterPool.increment_i_currency_supply(
#         H20, Borrow_token.address, _strike_price, 600 * 10 ** 18,
#         {'from': pool_owner, 'gas': 600000})
#     tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
#     assert tx_receipt['status'] == 1
#     # get I_token
#     I_token = get_contract(
#         'contracts/templates/ERC1155Template2.v.py',
#         interfaces=['ERC1155TokenReceiver'],
#         address=CurrencyDaoContract.currencies__i_currency_address(Lend_token.address)
#     )
#     S_token = get_contract(
#         'contracts/templates/ERC1155Template2.v.py',
#         interfaces=['ERC1155TokenReceiver'],
#         address=CurrencyDaoContract.currencies__s_currency_address(Lend_token.address)
#     )
#     U_token = get_contract(
#         'contracts/templates/ERC1155Template2.v.py',
#         interfaces=['ERC1155TokenReceiver'],
#         address=CurrencyDaoContract.currencies__u_currency_address(Lend_token.address)
#     )
#     # verify l_lend_currency supply, l_lend_currency balance and lend_currency balance
#     assert L_currency_token.totalSupply() == Web3.toWei(200, 'ether')
#     assert L_currency_token.balanceOf(UnderwriterPool.address) == Web3.toWei(200, 'ether')
#     # verify i_lend_currency supply and i_lend_currency balance
#     assert I_token.totalBalanceOf(UnderwriterPool.address) == Web3.toWei(600, 'ether')
#     # verify s_lend_currency supply and s_lend_currency balance
#     assert S_token.totalBalanceOf(UnderwriterPool.address) == Web3.toWei(3, 'ether')
#     # verify u_lend_currency supply and u_lend_currency balance
#     assert U_token.totalBalanceOf(UnderwriterPool.address) == Web3.toWei(3, 'ether')
#     # assign one of the accounts as a High_Risk_Insurer
#     High_Risk_Insurer = accounts[2]
#     # High_Risk_Insurer purchases 100 i_tokens from UnderwriterPool
#     tx_hash = UnderwriterPool.purchase_i_currency(H20, Borrow_token.address,
#         _strike_price, Web3.toWei(100, 'ether'), 0, {'from': High_Risk_Insurer})
#     tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
#     assert tx_receipt['status'] == 1
#     # High_Risk_Insurer purchases 2 s_tokens from UnderwriterPool
#     # The corresponding 2 u_tokens remain in the UnderwriterPool
#     tx_hash = UnderwriterPool.purchase_s_currency(H20, Borrow_token.address,
#         _strike_price, Web3.toWei(2, 'ether'), 0, {'from': High_Risk_Insurer})
#     tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
#     assert tx_receipt['status'] == 1
#     # verify i_lend_currency supply and i_lend_currency balance
#     assert I_token.totalBalanceOf(High_Risk_Insurer) == Web3.toWei(100, 'ether')
#     assert I_token.totalBalanceOf(UnderwriterPool.address) == Web3.toWei(500, 'ether')
#     # verify s_lend_currency supply and s_lend_currency balance
#     assert S_token.totalBalanceOf(High_Risk_Insurer) == Web3.toWei(2, 'ether')
#     assert S_token.totalBalanceOf(UnderwriterPool.address) == Web3.toWei(1, 'ether')
#     # verify u_lend_currency supply and u_lend_currency balance
#     assert U_token.totalBalanceOf(High_Risk_Insurer) == 0
#     assert U_token.totalBalanceOf(UnderwriterPool.address) == Web3.toWei(3, 'ether')
#     # assign one of the accounts as a Borrower
#     Borrower = accounts[3]
#     # Borrower purchases 10 Borrow_tokens from a 3rd party exchange
#     tx_hash = Borrow_token.transfer(Borrower, Web3.toWei(10, 'ether'), {'from': owner})
#     tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
#     assert tx_receipt['status'] == 1
#     assert Borrow_token.balanceOf(Borrower) == Web3.toWei(10, 'ether')
#     # Borrower authorizes CurrencyDaoContract to spend 2 Borrow_tokens
#     tx_hash = Borrow_token.approve(CurrencyDaoContract.address, Web3.toWei(3, 'ether'),
#         {'from': Borrower})
#     tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
#     assert tx_receipt['status'] == 1
#     # Borrower deposits 2 Borrow_tokens to Currency Pool and gets l_tokens
#     tx_hash = CurrencyDaoContract.currency_to_l_currency(Borrow_token.address, Web3.toWei(3, 'ether'),
#         {'from': Borrower, 'gas': 200000})
#     tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
#     assert tx_receipt['status'] == 1
#     # Borrower wishes to avail a loan of 400 Lend_tokens
#     # High_Risk_Insurer authorizes CurrencyDaoContract to spend his S_token
#     tx_hash = S_token.setApprovalForAll(CurrencyDaoContract.address, True,
#         {'from': High_Risk_Insurer})
#     tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
#     assert tx_receipt['status'] == 1
#     # High_Risk_Insurer authorizes CurrencyDaoContract to spend his I_token
#     tx_hash = I_token.setApprovalForAll(CurrencyDaoContract.address, True,
#         {'from': High_Risk_Insurer})
#     tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
#     assert tx_receipt['status'] == 1
#     # High_Risk_Insurer sets an offer of 2 s_tokens for 20 i_tokens
#     assert PositionRegistryContract.last_offer_index() == 0
#     tx_hash = PositionRegistryContract.create_offer(
#         Lend_token.address, H20, Borrow_token.address, _strike_price,
#         2, 20, 5 * 10 ** 15,
#         {'from': High_Risk_Insurer, 'gas': 450000})
#     tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
#     assert tx_receipt['status'] == 1
#     # Borrower purchases this offer for the amount of 0.1 ETH
#     # 20 i_tokens are transferred from High_Risk_Insurer account to Borrower
#     # 2 s_tokens are transferred from High_Risk_Insurer account to MarketDaoContract
#     tx_hash = PositionRegistryContract.avail_loan(0,
#         {'from': Borrower, 'value': 10 ** 17, 'gas': 950000})
#     tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
#     assert tx_receipt['status'] == 1
#     # verify i_lend_currency supply and i_lend_currency balance
#     assert I_token.totalBalanceOf(High_Risk_Insurer) == Web3.toWei(80, 'ether')
#     assert I_token.totalBalanceOf(Borrower) == Web3.toWei(20, 'ether')
#     assert I_token.totalBalanceOf(MarketDaoContract.address) == 0
#     assert I_token.totalBalanceOf(UnderwriterPool.address) == Web3.toWei(500, 'ether')
#     # verify s_lend_currency supply and s_lend_currency balance
#     assert S_token.totalBalanceOf(High_Risk_Insurer) == Web3.toWei(0, 'ether')
#     assert S_token.totalBalanceOf(Borrower) == 0
#     assert S_token.totalBalanceOf(MarketDaoContract.address) == Web3.toWei(2, 'ether')
#     assert S_token.totalBalanceOf(UnderwriterPool.address) == Web3.toWei(1, 'ether')
#     # verify u_lend_currency supply and u_lend_currency balance
#     assert U_token.totalBalanceOf(High_Risk_Insurer) == 0
#     assert U_token.totalBalanceOf(Borrower) == 0
#     assert U_token.totalBalanceOf(MarketDaoContract.address) == 0
#     assert U_token.totalBalanceOf(UnderwriterPool.address) == Web3.toWei(3, 'ether')
#     # verify Lend_token balance of Borrower
#     assert Lend_token.balanceOf(Borrower) == Web3.toWei(400, 'ether')
#     # Borrower authorizes CurrencyDaoContract to spend 400 Lend_tokens
#     tx_hash = Lend_token.approve(CurrencyDaoContract.address, Web3.toWei(400, 'ether'),
#         {'from': Borrower})
#     tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
#     assert tx_receipt['status'] == 1
#     # get Auction contract
#     _loan_market_hash = CollateralAuctionDao.loan_market_hash(
#         Lend_token.address, H20, Borrow_token.address
#     )
#     Auction = get_contract(
#         'contracts/templates/SimpleCollateralAuctionGraph.v.py',
#         interfaces=['ERC20', 'MarketDaoContract'],
#         address=CollateralAuctionDao.graphs(_loan_market_hash)
#     )
#     # time passes until loan market expires
#     time_travel(H20)
#     # update price feed
#     tx_hash = PriceFeed.set_price(Web3.toWei(150, 'ether'), {'from': owner})
#     tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
#     assert tx_receipt['status'] == 1
#     # verify l_borrow_currency supply, l_borrow_currency balance and borrow_currency balance
#     assert L_underlying_token.totalSupply() == Web3.toWei(3, 'ether')
#     assert L_underlying_token.balanceOf(Borrower) == Web3.toWei(1, 'ether')
#     assert L_underlying_token.balanceOf(MarketDaoContract.address) == Web3.toWei(2, 'ether')
#     assert Borrow_token.balanceOf(Auction.address) == 0
#     assert Borrow_token.balanceOf(CurrencyDaoContract.pools__pool_address(_underlying_pool_hash)) == Web3.toWei(3, 'ether')
#     # assign one of the accounts as a _loan_market_settler
#     _loan_market_settler = accounts[3]
#     # _loan_market_settler initiates loan market settlement
#     tx_hash = MarketDaoContract.settle_loan_market(_loan_market_hash, {'from': _loan_market_settler, 'gas': 280000})
#     tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
#     assert tx_receipt['status'] == 1
#     # verify l_borrow_currency supply, l_borrow_currency balance and borrow_currency balance
#     assert L_underlying_token.totalSupply() == Web3.toWei(1, 'ether')
#     assert L_underlying_token.balanceOf(Borrower) == Web3.toWei(1, 'ether')
#     assert L_underlying_token.balanceOf(MarketDaoContract.address) == 0
#     assert Borrow_token.balanceOf(Auction.address) == Web3.toWei(2, 'ether')
#     assert Borrow_token.balanceOf(CurrencyDaoContract.pools__pool_address(_underlying_pool_hash)) == Web3.toWei(1, 'ether')
#     assert MarketDaoContract.loan_markets__status(_loan_market_hash) == MarketDaoContract.LOAN_MARKET_STATUS_SETTLING()
#     # assign one of the accounts as an _auctioned_collateral_purchaser
#     _auctioned_collateral_purchaser = accounts[4]
#     # _auctioned_collateral_purchaser buys 1000 lend token from a 3rd party exchange
#     tx_hash = Lend_token.transfer(_auctioned_collateral_purchaser, 1000 * 10 ** 18, {'from': owner})
#     tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
#     assert tx_receipt['status'] == 1
#     # _auctioned_collateral_purchaser authorizes CurrencyDaoContract to spend 800 lend currency
#     tx_hash = Lend_token.approve(CurrencyDaoContract.address, 800 * (10 ** 18),
#         {'from': _auctioned_collateral_purchaser})
#     tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
#     assert tx_receipt['status'] == 1
#     time_travel(H20 + 10 * 60)
#     # _auctioned_collateral_purchaser purchases all of the 2 Borrow_tokens for current price of Lend_tokens
#     tx_hash = Auction.purchase_for_remaining_currency({'from': _auctioned_collateral_purchaser, 'gas': 280000})
#     tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
#     assert tx_receipt['status'] == 1
#     assert MarketDaoContract.loan_markets__underlying_settlement_price_per_currency(_loan_market_hash) == 135165333333333333333
#     # verify l_lend_currency supply, l_lend_currency balance and lend_currency balance
#     assert L_currency_token.totalSupply() == Web3.toWei(200, 'ether')
#     assert L_currency_token.balanceOf(UnderwriterPool.address) == Web3.toWei(200, 'ether')
#     assert L_currency_token.balanceOf(Borrower) == 0
#     # verify l_borrow_currency supply, l_borrow_currency balance and borrow_currency balance
#     assert L_underlying_token.totalSupply() == Web3.toWei(1, 'ether')
#     assert L_underlying_token.balanceOf(Borrower) == Web3.toWei(1, 'ether')
#     assert L_underlying_token.balanceOf(MarketDaoContract.address) == 0
#     assert Borrow_token.balanceOf(Auction.address) == 0
#     assert Borrow_token.balanceOf(CurrencyDaoContract.pools__pool_address(_underlying_pool_hash)) == Web3.toWei(1, 'ether')
#     # verify i_lend_currency supply and i_lend_currency balance
#     assert I_token.totalBalanceOf(High_Risk_Insurer) == Web3.toWei(80, 'ether')
#     assert I_token.totalBalanceOf(Borrower) == Web3.toWei(20, 'ether')
#     assert I_token.totalBalanceOf(MarketDaoContract.address) == 0
#     assert I_token.totalBalanceOf(UnderwriterPool.address) == Web3.toWei(500, 'ether')
#     # verify s_lend_currency supply and s_lend_currency balance
#     assert S_token.totalBalanceOf(High_Risk_Insurer) == Web3.toWei(0, 'ether')
#     assert S_token.totalBalanceOf(Borrower) == 0
#     assert S_token.totalBalanceOf(MarketDaoContract.address) == Web3.toWei(2, 'ether')
#     assert S_token.totalBalanceOf(UnderwriterPool.address) == Web3.toWei(1, 'ether')
#     # verify u_lend_currency supply and u_lend_currency balance
#     assert U_token.totalBalanceOf(High_Risk_Insurer) == 0
#     assert U_token.totalBalanceOf(Borrower) == 0
#     assert U_token.totalBalanceOf(MarketDaoContract.address) == 0
#     assert U_token.totalBalanceOf(UnderwriterPool.address) == Web3.toWei(3, 'ether')
#     # Borrower cannot exercise his 2 s_tokens
#     assert MarketDaoContract.shield_payout(Lend_token.address, H20, Borrow_token.address, _strike_price) == 0
#     # Borrower closes the liquidated loan
#     position_id = PositionRegistryContract.borrow_position(Borrower, PositionRegistryContract.borrow_position_count(Borrower))
#     tx_hash = PositionRegistryContract.close_liquidated_loan(position_id, {'from': Borrower, 'gas': 200000})
#     tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
#     print('\n\n tx_receipt:\n{0}\n\n'.format(tx_receipt))
#     assert tx_receipt['status'] == 1
#     # verify l_lend_currency supply, l_lend_currency balance and lend_currency balance
#     assert L_currency_token.totalSupply() == Web3.toWei(200, 'ether')
#     assert L_currency_token.balanceOf(UnderwriterPool.address) == Web3.toWei(200, 'ether')
#     assert L_currency_token.balanceOf(Borrower) == 0
#     # verify l_borrow_currency supply, l_borrow_currency balance and borrow_currency balance
#     assert L_underlying_token.totalSupply() == Web3.toWei(1, 'ether')
#     assert L_underlying_token.balanceOf(Borrower) == Web3.toWei(1, 'ether')
#     assert L_underlying_token.balanceOf(MarketDaoContract.address) == 0
#     assert Borrow_token.balanceOf(CurrencyDaoContract.pools__pool_address(_underlying_pool_hash)) == Web3.toWei(1, 'ether')
#     # verify i_lend_currency supply and i_lend_currency balance
#     assert I_token.totalBalanceOf(High_Risk_Insurer) == Web3.toWei(80, 'ether')
#     assert I_token.totalBalanceOf(Borrower) == Web3.toWei(20, 'ether')
#     assert I_token.totalBalanceOf(MarketDaoContract.address) == 0
#     assert I_token.totalBalanceOf(UnderwriterPool.address) == Web3.toWei(500, 'ether')
#     # verify s_lend_currency supply and s_lend_currency balance
#     assert S_token.totalBalanceOf(High_Risk_Insurer) == 0
#     assert S_token.totalBalanceOf(Borrower) == 0
#     assert S_token.totalBalanceOf(MarketDaoContract.address) == 0
#     assert S_token.totalBalanceOf(UnderwriterPool.address) == Web3.toWei(1, 'ether')
#     # verify u_lend_currency supply and u_lend_currency balance
#     assert U_token.totalBalanceOf(High_Risk_Insurer) == 0
#     assert U_token.totalBalanceOf(Borrower) == 0
#     assert U_token.totalBalanceOf(MarketDaoContract.address) == 0
#     assert U_token.totalBalanceOf(UnderwriterPool.address) == Web3.toWei(3, 'ether')
