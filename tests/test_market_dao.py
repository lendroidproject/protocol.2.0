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


def test_initialize(w3, Deployer, get_MarketDao_contract, ProtocolDao):
    MarketDao = get_MarketDao_contract(address=ProtocolDao.daos(PROTOCOL_CONSTANTS['DAO_MARKET']))
    assert not MarketDao.initialized()
    tx_hash = ProtocolDao.initialize_market_dao(transact={'from': Deployer})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    assert MarketDao.initialized()


def test_pause_and_unpause(w3, Deployer, EscapeHatchManager, get_MarketDao_contract, ProtocolDao):
    MarketDao = get_MarketDao_contract(address=ProtocolDao.daos(PROTOCOL_CONSTANTS['DAO_MARKET']))
    tx_hash = ProtocolDao.initialize_market_dao(transact={'from': Deployer})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    assert not MarketDao.paused()
    tx_hash = ProtocolDao.toggle_dao_pause(PROTOCOL_CONSTANTS['DAO_MARKET'], True, transact={'from': EscapeHatchManager})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    assert MarketDao.paused()
    tx_hash = ProtocolDao.toggle_dao_pause(PROTOCOL_CONSTANTS['DAO_MARKET'], False, transact={'from': EscapeHatchManager})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    assert not MarketDao.paused()


def test_open_position_sans_poolshare_model(w3, get_logs,
    Whale, Deployer, Governor,
    Lend_token, Borrow_token, LST_token,
    get_ERC20_contract, get_MFT_contract,
    get_PoolNameRegistry_contract, get_PositionRegistry_contract,
    get_CurrencyDao_contract, get_InterestPoolDao_contract,
    get_UnderwriterPoolDao_contract, get_MarketDao_contract,
    get_UnderwriterPool_contract,
    ProtocolDao):
    # get CurrencyDao
    CurrencyDao = get_CurrencyDao_contract(address=ProtocolDao.daos(PROTOCOL_CONSTANTS['DAO_CURRENCY']))
    # get InterestPoolDao
    InterestPoolDao = get_InterestPoolDao_contract(address=ProtocolDao.daos(PROTOCOL_CONSTANTS['DAO_INTEREST_POOL']))
    # get UnderwriterPoolDao
    UnderwriterPoolDao = get_UnderwriterPoolDao_contract(address=ProtocolDao.daos(PROTOCOL_CONSTANTS['DAO_UNDERWRITER_POOL']))
    # get MarketDao
    MarketDao = get_MarketDao_contract(address=ProtocolDao.daos(PROTOCOL_CONSTANTS['DAO_MARKET']))
    # get PoolNameRegistry
    PoolNameRegistry = get_PoolNameRegistry_contract(address=ProtocolDao.registries(PROTOCOL_CONSTANTS['REGISTRY_POOL_NAME']))
    # get PositionRegistry
    PositionRegistry = get_PositionRegistry_contract(address=ProtocolDao.registries(PROTOCOL_CONSTANTS['REGISTRY_POSITION']))
    # assign one of the accounts as _lend_and_borrow_token_holder
    _lend_and_borrow_token_holder = w3.eth.accounts[5]
    # assign one of the accounts as _pool_owner
    _pool_owner = w3.eth.accounts[6]
    # initialize PoolNameRegistry
    tx_hash = ProtocolDao.initialize_pool_name_registry(Web3.toWei(POOL_NAME_REGISTRATION_MIN_STAKE_LST, 'ether'), transact={'from': Deployer})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    # initialize PositionRegistry
    tx_hash = ProtocolDao.initialize_position_registry(transact={'from': Deployer})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    # initialize CurrencyDao
    tx_hash = ProtocolDao.initialize_currency_dao(transact={'from': Deployer})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    # initialize InterestPoolDao
    tx_hash = ProtocolDao.initialize_interest_pool_dao(transact={'from': Deployer})
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
    tx_hash = ProtocolDao.set_token_support(Lend_token.address, True, transact={'from': Governor})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    # set support for Borrow_token
    tx_hash = ProtocolDao.set_token_support(Borrow_token.address, True, transact={'from': Governor})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    # get L_lend_token
    L_lend_token = get_ERC20_contract(address=CurrencyDao.token_addresses__l(Lend_token.address))
    # get I_lend_token
    I_lend_token = get_MFT_contract(address=CurrencyDao.token_addresses__i(Lend_token.address))
    # get S_lend_token
    S_lend_token = get_MFT_contract(address=CurrencyDao.token_addresses__s(Lend_token.address))
    # get U_lend_token
    U_lend_token = get_MFT_contract(address=CurrencyDao.token_addresses__u(Lend_token.address))
    # get L_borrow_token
    L_borrow_token = get_ERC20_contract(address=CurrencyDao.token_addresses__l(Borrow_token.address))
    # get F_borrow_token
    F_borrow_token = get_MFT_contract(address=CurrencyDao.token_addresses__f(Borrow_token.address))
    # get I_borrow_token
    I_borrow_token = get_MFT_contract(address=CurrencyDao.token_addresses__i(Borrow_token.address))
    # get _loan_market_hash
    _loan_market_hash = MarketDao.loan_market_hash(Lend_token.address, H20, Borrow_token.address)
    # get _shield_market_hash
    _shield_market_hash = MarketDao.shield_market_hash(Lend_token.address, H20, Borrow_token.address, STRIKE_125)
    # set maximum_market_liability
    tx_hash = ProtocolDao.set_maximum_liability_for_loan_market(Lend_token.address, H20, Borrow_token.address, Web3.toWei(MAX_LIABILITY_CURENCY_MARKET, 'ether'), transact={'from': Governor})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    assert MarketDao.maximum_market_liabilities(_loan_market_hash) == Web3.toWei(MAX_LIABILITY_CURENCY_MARKET, 'ether')
    # _pool_owner buys POOL_NAME_REGISTRATION_MIN_STAKE_LST LST_token from a 3rd party exchange
    tx_hash = LST_token.transfer(_pool_owner, Web3.toWei(POOL_NAME_REGISTRATION_MIN_STAKE_LST, 'ether'), transact={'from': Whale})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    # _pool_owner authorizes CurrencyDao to spend POOL_NAME_REGISTRATION_MIN_STAKE_LST LST_token
    tx_hash = LST_token.approve(CurrencyDao.address, Web3.toWei(POOL_NAME_REGISTRATION_MIN_STAKE_LST, 'ether'), transact={'from': _pool_owner})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
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
    # _pool_owner authorizes CurrencyDao to spend INTEREST_POOL_DAO_MIN_MFT_FEE LST_token
    tx_hash = LST_token.approve(CurrencyDao.address, Web3.toWei(INTEREST_POOL_DAO_MIN_MFT_FEE, 'ether'), transact={'from': _pool_owner})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    # set support for MFT H20
    tx_hash = UnderwriterPool.support_mft(H20, Borrow_token.address, STRIKE_125,
        Web3.toWei(0.025, 'ether'), Web3.toWei(0.05, 'ether'), transact={'from': _pool_owner, 'gas': 2500000})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    # _lend_and_borrow_token_holder buys 1000 Lend_token from a 3rd party exchange
    tx_hash = Lend_token.transfer(_lend_and_borrow_token_holder, Web3.toWei(1000, 'ether'), transact={'from': Whale})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    assert Lend_token.balanceOf(_lend_and_borrow_token_holder) == Web3.toWei(1000, 'ether')
    # _lend_and_borrow_token_holder buys 5 Borrow_token from a 3rd party exchange
    tx_hash = Borrow_token.transfer(_lend_and_borrow_token_holder, Web3.toWei(5, 'ether'), transact={'from': Whale})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    assert Borrow_token.balanceOf(_lend_and_borrow_token_holder) == Web3.toWei(5, 'ether')
    # _lend_and_borrow_token_holder authorizes CurrencyDao to spend 800 Lend_token
    tx_hash = Lend_token.approve(CurrencyDao.address, Web3.toWei(800, 'ether'), transact={'from': _lend_and_borrow_token_holder})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    assert Lend_token.allowance(_lend_and_borrow_token_holder, CurrencyDao.address) == Web3.toWei(800, 'ether')
    # _lend_and_borrow_token_holder authorizes CurrencyDao to spend 4 Borrow_token
    tx_hash = Borrow_token.approve(CurrencyDao.address, Web3.toWei(4, 'ether'), transact={'from': _lend_and_borrow_token_holder})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    assert Borrow_token.allowance(_lend_and_borrow_token_holder, CurrencyDao.address) == Web3.toWei(4, 'ether')
    # _lend_and_borrow_token_holder wraps 800 Lend_token to L_lend_token
    tx_hash = CurrencyDao.wrap(Lend_token.address, Web3.toWei(800, 'ether'), transact={'from': _lend_and_borrow_token_holder, 'gas': 145000})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    assert Lend_token.balanceOf(_lend_and_borrow_token_holder) == Web3.toWei(200, 'ether')
    assert L_lend_token.balanceOf(_lend_and_borrow_token_holder) == Web3.toWei(800, 'ether')
    # _lend_and_borrow_token_holder wraps 4 Borrow_tokens to 4 L_borrow_tokens
    tx_hash = CurrencyDao.wrap(Borrow_token.address, Web3.toWei(4, 'ether'), transact={'from': _lend_and_borrow_token_holder, 'gas': 145000})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    assert Borrow_token.balanceOf(_lend_and_borrow_token_holder) == Web3.toWei(1, 'ether')
    assert L_borrow_token.balanceOf(_lend_and_borrow_token_holder) == Web3.toWei(4, 'ether')
    # _lend_and_borrow_token_holder splits 500 L_lend_tokens into 500 I_lend_tokens and 500 S_lend_tokens and 500 U_lend_tokens for H20, Borrow_token, and STRIKE_200
    tx_hash = UnderwriterPoolDao.split(Lend_token.address, H20, Borrow_token.address, STRIKE_125, Web3.toWei(500, 'ether'), transact={'from': _lend_and_borrow_token_holder, 'gas': 1100000})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    assert L_lend_token.balanceOf(_lend_and_borrow_token_holder) == Web3.toWei(300, 'ether')
    _i_lend_id = I_lend_token.id(Lend_token.address, H20, ZERO_ADDRESS, 0)
    _s_lend_id = S_lend_token.id(Lend_token.address, H20, Borrow_token.address, STRIKE_125)
    _u_lend_id = U_lend_token.id(Lend_token.address, H20, Borrow_token.address, STRIKE_125)
    assert I_lend_token.balanceOf(_lend_and_borrow_token_holder, _i_lend_id) == Web3.toWei(500, 'ether')
    assert S_lend_token.balanceOf(_lend_and_borrow_token_holder, _s_lend_id) == Web3.toWei(500, 'ether')
    assert U_lend_token.balanceOf(_lend_and_borrow_token_holder, _u_lend_id) == Web3.toWei(500, 'ether')
    # _lend_and_borrow_token_holder splits 4 L_borrow_tokens into 4 F_borrow_tokens and 4 I_borrow_tokens for H20
    tx_hash = InterestPoolDao.split(Borrow_token.address, H20, Web3.toWei(4, 'ether'), transact={'from': _lend_and_borrow_token_holder, 'gas': 640000})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    assert L_borrow_token.balanceOf(_lend_and_borrow_token_holder) == 0
    _f_borrow_id = F_borrow_token.id(Borrow_token.address, H20, ZERO_ADDRESS, 0)
    _i_borrow_id = I_borrow_token.id(Borrow_token.address, H20, ZERO_ADDRESS, 0)
    assert F_borrow_token.balanceOf(_lend_and_borrow_token_holder, _f_borrow_id) == Web3.toWei(4, 'ether')
    assert I_borrow_token.balanceOf(_lend_and_borrow_token_holder, _i_borrow_id) == Web3.toWei(4, 'ether')
    # _lend_and_borrow_token_holder avails a loan for 500 Lend_tokens
    # For this, she places 4 F_borrow_tokens, 500 I_lend_tokens and 500 S_lend_tokens as collateral
    assert PositionRegistry.last_position_id() == 0
    assert PositionRegistry.borrow_position_count(_lend_and_borrow_token_holder) == 0
    tx_hash = PositionRegistry.avail_loan(Lend_token.address, H20, Borrow_token.address, STRIKE_125, Web3.toWei(500, 'ether'), transact={'from': _lend_and_borrow_token_holder, 'gas': 1000000})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    print('\n\n tx_receipt:\n{0}\n\n'.format(tx_receipt))
    assert tx_receipt['status'] == 1
    assert Lend_token.balanceOf(_lend_and_borrow_token_holder) == Web3.toWei(700, 'ether')
    assert F_borrow_token.balanceOf(_lend_and_borrow_token_holder, _f_borrow_id) == 0
    assert F_borrow_token.balanceOf(MarketDao.address, _f_borrow_id) == Web3.toWei(4, 'ether')
    assert PositionRegistry.last_position_id() == 1
    assert PositionRegistry.borrow_position_count(_lend_and_borrow_token_holder) == 1
    _position_id = PositionRegistry.borrow_position(_lend_and_borrow_token_holder, 1)
    assert PositionRegistry.positions__id(_position_id) == _position_id
    assert PositionRegistry.positions__borrower(_position_id) == _lend_and_borrow_token_holder
    assert PositionRegistry.positions__currency(_position_id) == Lend_token.address
    assert PositionRegistry.positions__underlying(_position_id) == Borrow_token.address
    assert PositionRegistry.positions__strike_price(_position_id) == STRIKE_125
    assert PositionRegistry.positions__currency_value(_position_id) == Web3.toWei(500, 'ether')
    assert PositionRegistry.positions__underlying_value(_position_id) == Web3.toWei(4, 'ether')
    assert PositionRegistry.positions__status(_position_id) == 1


def test_partial_close_position_sans_poolshare_model(w3, get_logs,
    Whale, Deployer, Governor,
    Lend_token, Borrow_token, LST_token,
    get_ERC20_contract, get_MFT_contract,
    get_PoolNameRegistry_contract, get_PositionRegistry_contract,
    get_CurrencyDao_contract, get_InterestPoolDao_contract,
    get_UnderwriterPoolDao_contract, get_MarketDao_contract,
    get_UnderwriterPool_contract,
    ProtocolDao):
    # get CurrencyDao
    CurrencyDao = get_CurrencyDao_contract(address=ProtocolDao.daos(PROTOCOL_CONSTANTS['DAO_CURRENCY']))
    # get InterestPoolDao
    InterestPoolDao = get_InterestPoolDao_contract(address=ProtocolDao.daos(PROTOCOL_CONSTANTS['DAO_INTEREST_POOL']))
    # get UnderwriterPoolDao
    UnderwriterPoolDao = get_UnderwriterPoolDao_contract(address=ProtocolDao.daos(PROTOCOL_CONSTANTS['DAO_UNDERWRITER_POOL']))
    # get MarketDao
    MarketDao = get_MarketDao_contract(address=ProtocolDao.daos(PROTOCOL_CONSTANTS['DAO_MARKET']))
    # get PoolNameRegistry
    PoolNameRegistry = get_PoolNameRegistry_contract(address=ProtocolDao.registries(PROTOCOL_CONSTANTS['REGISTRY_POOL_NAME']))
    # get PositionRegistry
    PositionRegistry = get_PositionRegistry_contract(address=ProtocolDao.registries(PROTOCOL_CONSTANTS['REGISTRY_POSITION']))
    # assign one of the accounts as _lend_and_borrow_token_holder
    _lend_and_borrow_token_holder = w3.eth.accounts[5]
    # assign one of the accounts as _pool_owner
    _pool_owner = w3.eth.accounts[6]
    # initialize PoolNameRegistry
    tx_hash = ProtocolDao.initialize_pool_name_registry(Web3.toWei(POOL_NAME_REGISTRATION_MIN_STAKE_LST, 'ether'), transact={'from': Deployer})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    # initialize PositionRegistry
    tx_hash = ProtocolDao.initialize_position_registry(transact={'from': Deployer})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    # initialize CurrencyDao
    tx_hash = ProtocolDao.initialize_currency_dao(transact={'from': Deployer})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    # initialize InterestPoolDao
    tx_hash = ProtocolDao.initialize_interest_pool_dao(transact={'from': Deployer})
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
    tx_hash = ProtocolDao.set_token_support(Lend_token.address, True, transact={'from': Governor})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    # set support for Borrow_token
    tx_hash = ProtocolDao.set_token_support(Borrow_token.address, True, transact={'from': Governor})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    # get L_lend_token
    L_lend_token = get_ERC20_contract(address=CurrencyDao.token_addresses__l(Lend_token.address))
    # get I_lend_token
    I_lend_token = get_MFT_contract(address=CurrencyDao.token_addresses__i(Lend_token.address))
    # get S_lend_token
    S_lend_token = get_MFT_contract(address=CurrencyDao.token_addresses__s(Lend_token.address))
    # get U_lend_token
    U_lend_token = get_MFT_contract(address=CurrencyDao.token_addresses__u(Lend_token.address))
    # get L_borrow_token
    L_borrow_token = get_ERC20_contract(address=CurrencyDao.token_addresses__l(Borrow_token.address))
    # get F_borrow_token
    F_borrow_token = get_MFT_contract(address=CurrencyDao.token_addresses__f(Borrow_token.address))
    # get I_borrow_token
    I_borrow_token = get_MFT_contract(address=CurrencyDao.token_addresses__i(Borrow_token.address))
    # get _loan_market_hash
    _loan_market_hash = MarketDao.loan_market_hash(Lend_token.address, H20, Borrow_token.address)
    # get _shield_market_hash
    _shield_market_hash = MarketDao.shield_market_hash(Lend_token.address, H20, Borrow_token.address, STRIKE_125)
    # set maximum_market_liability
    tx_hash = ProtocolDao.set_maximum_liability_for_loan_market(Lend_token.address, H20, Borrow_token.address, Web3.toWei(MAX_LIABILITY_CURENCY_MARKET, 'ether'), transact={'from': Governor})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    # _pool_owner buys POOL_NAME_REGISTRATION_MIN_STAKE_LST LST_token from a 3rd party exchange
    tx_hash = LST_token.transfer(_pool_owner, Web3.toWei(POOL_NAME_REGISTRATION_MIN_STAKE_LST, 'ether'), transact={'from': Whale})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    # _pool_owner authorizes CurrencyDao to spend POOL_NAME_REGISTRATION_MIN_STAKE_LST LST_token
    tx_hash = LST_token.approve(CurrencyDao.address, Web3.toWei(POOL_NAME_REGISTRATION_MIN_STAKE_LST, 'ether'), transact={'from': _pool_owner})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    # _pool_owner registers _pool_name POOL_NAME_LIONFURY
    _pool_name = POOL_NAME_LIONFURY
    tx_hash = UnderwriterPoolDao.register_pool(
        False, Lend_token.address, _pool_name, Web3.toWei(50, 'ether'), 1, 1, 90, transact={'from': _pool_owner, 'gas': 1200000})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
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
    # _pool_owner authorizes CurrencyDao to spend INTEREST_POOL_DAO_MIN_MFT_FEE LST_token
    tx_hash = LST_token.approve(CurrencyDao.address, Web3.toWei(INTEREST_POOL_DAO_MIN_MFT_FEE, 'ether'), transact={'from': _pool_owner})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    # set support for MFT H20
    tx_hash = UnderwriterPool.support_mft(H20, Borrow_token.address, STRIKE_125,
        Web3.toWei(0.025, 'ether'), Web3.toWei(0.05, 'ether'), transact={'from': _pool_owner, 'gas': 2500000})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    # _lend_and_borrow_token_holder buys 1000 Lend_token from a 3rd party exchange
    tx_hash = Lend_token.transfer(_lend_and_borrow_token_holder, Web3.toWei(1000, 'ether'), transact={'from': Whale})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    # _lend_and_borrow_token_holder buys 5 Borrow_token from a 3rd party exchange
    tx_hash = Borrow_token.transfer(_lend_and_borrow_token_holder, Web3.toWei(5, 'ether'), transact={'from': Whale})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    # _lend_and_borrow_token_holder authorizes CurrencyDao to spend 800 Lend_token
    tx_hash = Lend_token.approve(CurrencyDao.address, Web3.toWei(800, 'ether'), transact={'from': _lend_and_borrow_token_holder})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    # _lend_and_borrow_token_holder authorizes CurrencyDao to spend 4 Borrow_token
    tx_hash = Borrow_token.approve(CurrencyDao.address, Web3.toWei(4, 'ether'), transact={'from': _lend_and_borrow_token_holder})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    # _lend_and_borrow_token_holder wraps 800 Lend_token to L_lend_token
    tx_hash = CurrencyDao.wrap(Lend_token.address, Web3.toWei(800, 'ether'), transact={'from': _lend_and_borrow_token_holder, 'gas': 145000})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    # _lend_and_borrow_token_holder wraps 4 Borrow_tokens to 4 L_borrow_tokens
    tx_hash = CurrencyDao.wrap(Borrow_token.address, Web3.toWei(4, 'ether'), transact={'from': _lend_and_borrow_token_holder, 'gas': 145000})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    # _lend_and_borrow_token_holder splits 500 L_lend_tokens into 500 I_lend_tokens and 500 S_lend_tokens and 500 U_lend_tokens for H20, Borrow_token, and STRIKE_200
    tx_hash = UnderwriterPoolDao.split(Lend_token.address, H20, Borrow_token.address, STRIKE_125, Web3.toWei(500, 'ether'), transact={'from': _lend_and_borrow_token_holder, 'gas': 1100000})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    _i_lend_id = I_lend_token.id(Lend_token.address, H20, ZERO_ADDRESS, 0)
    _s_lend_id = S_lend_token.id(Lend_token.address, H20, Borrow_token.address, STRIKE_125)
    _u_lend_id = U_lend_token.id(Lend_token.address, H20, Borrow_token.address, STRIKE_125)
    # _lend_and_borrow_token_holder splits 4 L_borrow_tokens into 4 F_borrow_tokens and 4 I_borrow_tokens for H20
    tx_hash = InterestPoolDao.split(Borrow_token.address, H20, Web3.toWei(4, 'ether'), transact={'from': _lend_and_borrow_token_holder, 'gas': 640000})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    _f_borrow_id = F_borrow_token.id(Borrow_token.address, H20, ZERO_ADDRESS, 0)
    _i_borrow_id = I_borrow_token.id(Borrow_token.address, H20, ZERO_ADDRESS, 0)
    # _lend_and_borrow_token_holder avails a loan for 500 Lend_tokens
    # For this, she places 4 F_borrow_tokens, 500 I_lend_tokens and 500 S_lend_tokens as collateral
    tx_hash = PositionRegistry.avail_loan(Lend_token.address, H20, Borrow_token.address, STRIKE_125, Web3.toWei(500, 'ether'), transact={'from': _lend_and_borrow_token_holder, 'gas': 900000})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    _position_id = PositionRegistry.borrow_position(_lend_and_borrow_token_holder, 1)
    assert PositionRegistry.positions__status(_position_id) == PositionRegistry.LOAN_STATUS_ACTIVE()
    assert PositionRegistry.positions__repaid_value(_position_id) == 0
    # _lend_and_borrow_token_holder authorizes CurrencyDao to spend 300 Lend_token
    tx_hash = Lend_token.approve(CurrencyDao.address, Web3.toWei(300, 'ether'), transact={'from': _lend_and_borrow_token_holder})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    assert Lend_token.allowance(_lend_and_borrow_token_holder, CurrencyDao.address) == Web3.toWei(300, 'ether')
    # _lend_and_borrow_token_holder closes the loan
    tx_hash = PositionRegistry.repay_loan(_position_id, Web3.toWei(300, 'ether'), transact={'from': _lend_and_borrow_token_holder, 'gas': 400000})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    assert PositionRegistry.positions__status(_position_id) == PositionRegistry.LOAN_STATUS_ACTIVE()
    assert PositionRegistry.positions__repaid_value(_position_id) == Web3.toWei(300, 'ether')


def test_full_close_position_sans_poolshare_model(w3, get_logs,
    Whale, Deployer, Governor,
    Lend_token, Borrow_token, LST_token,
    get_ERC20_contract, get_MFT_contract,
    get_PoolNameRegistry_contract, get_PositionRegistry_contract,
    get_CurrencyDao_contract, get_InterestPoolDao_contract,
    get_UnderwriterPoolDao_contract, get_MarketDao_contract,
    get_UnderwriterPool_contract,
    ProtocolDao):
    # get CurrencyDao
    CurrencyDao = get_CurrencyDao_contract(address=ProtocolDao.daos(PROTOCOL_CONSTANTS['DAO_CURRENCY']))
    # get InterestPoolDao
    InterestPoolDao = get_InterestPoolDao_contract(address=ProtocolDao.daos(PROTOCOL_CONSTANTS['DAO_INTEREST_POOL']))
    # get UnderwriterPoolDao
    UnderwriterPoolDao = get_UnderwriterPoolDao_contract(address=ProtocolDao.daos(PROTOCOL_CONSTANTS['DAO_UNDERWRITER_POOL']))
    # get MarketDao
    MarketDao = get_MarketDao_contract(address=ProtocolDao.daos(PROTOCOL_CONSTANTS['DAO_MARKET']))
    # get PoolNameRegistry
    PoolNameRegistry = get_PoolNameRegistry_contract(address=ProtocolDao.registries(PROTOCOL_CONSTANTS['REGISTRY_POOL_NAME']))
    # get PositionRegistry
    PositionRegistry = get_PositionRegistry_contract(address=ProtocolDao.registries(PROTOCOL_CONSTANTS['REGISTRY_POSITION']))
    # assign one of the accounts as _lend_and_borrow_token_holder
    _lend_and_borrow_token_holder = w3.eth.accounts[5]
    # assign one of the accounts as _pool_owner
    _pool_owner = w3.eth.accounts[6]
    # initialize PoolNameRegistry
    tx_hash = ProtocolDao.initialize_pool_name_registry(Web3.toWei(POOL_NAME_REGISTRATION_MIN_STAKE_LST, 'ether'), transact={'from': Deployer})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    # initialize PositionRegistry
    tx_hash = ProtocolDao.initialize_position_registry(transact={'from': Deployer})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    # initialize CurrencyDao
    tx_hash = ProtocolDao.initialize_currency_dao(transact={'from': Deployer})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    # initialize InterestPoolDao
    tx_hash = ProtocolDao.initialize_interest_pool_dao(transact={'from': Deployer})
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
    tx_hash = ProtocolDao.set_token_support(Lend_token.address, True, transact={'from': Governor})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    # set support for Borrow_token
    tx_hash = ProtocolDao.set_token_support(Borrow_token.address, True, transact={'from': Governor})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    # get L_lend_token
    L_lend_token = get_ERC20_contract(address=CurrencyDao.token_addresses__l(Lend_token.address))
    # get I_lend_token
    I_lend_token = get_MFT_contract(address=CurrencyDao.token_addresses__i(Lend_token.address))
    # get S_lend_token
    S_lend_token = get_MFT_contract(address=CurrencyDao.token_addresses__s(Lend_token.address))
    # get U_lend_token
    U_lend_token = get_MFT_contract(address=CurrencyDao.token_addresses__u(Lend_token.address))
    # get L_borrow_token
    L_borrow_token = get_ERC20_contract(address=CurrencyDao.token_addresses__l(Borrow_token.address))
    # get F_borrow_token
    F_borrow_token = get_MFT_contract(address=CurrencyDao.token_addresses__f(Borrow_token.address))
    # get I_borrow_token
    I_borrow_token = get_MFT_contract(address=CurrencyDao.token_addresses__i(Borrow_token.address))
    # get _loan_market_hash
    _loan_market_hash = MarketDao.loan_market_hash(Lend_token.address, H20, Borrow_token.address)
    # get _shield_market_hash
    _shield_market_hash = MarketDao.shield_market_hash(Lend_token.address, H20, Borrow_token.address, STRIKE_125)
    # set maximum_market_liability
    tx_hash = ProtocolDao.set_maximum_liability_for_loan_market(Lend_token.address, H20, Borrow_token.address, Web3.toWei(MAX_LIABILITY_CURENCY_MARKET, 'ether'), transact={'from': Governor})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    # _pool_owner buys POOL_NAME_REGISTRATION_MIN_STAKE_LST LST_token from a 3rd party exchange
    tx_hash = LST_token.transfer(_pool_owner, Web3.toWei(POOL_NAME_REGISTRATION_MIN_STAKE_LST, 'ether'), transact={'from': Whale})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    # _pool_owner authorizes CurrencyDao to spend POOL_NAME_REGISTRATION_MIN_STAKE_LST LST_token
    tx_hash = LST_token.approve(CurrencyDao.address, Web3.toWei(POOL_NAME_REGISTRATION_MIN_STAKE_LST, 'ether'), transact={'from': _pool_owner})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    # _pool_owner registers _pool_name POOL_NAME_LIONFURY
    _pool_name = POOL_NAME_LIONFURY
    tx_hash = UnderwriterPoolDao.register_pool(
        False, Lend_token.address, _pool_name, Web3.toWei(50, 'ether'), 1, 1, 90, transact={'from': _pool_owner, 'gas': 1200000})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
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
    # _pool_owner authorizes CurrencyDao to spend INTEREST_POOL_DAO_MIN_MFT_FEE LST_token
    tx_hash = LST_token.approve(CurrencyDao.address, Web3.toWei(INTEREST_POOL_DAO_MIN_MFT_FEE, 'ether'), transact={'from': _pool_owner})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    # set support for MFT H20
    tx_hash = UnderwriterPool.support_mft(H20, Borrow_token.address, STRIKE_125,
        Web3.toWei(0.025, 'ether'), Web3.toWei(0.05, 'ether'), transact={'from': _pool_owner, 'gas': 2500000})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    # _lend_and_borrow_token_holder buys 1000 Lend_token from a 3rd party exchange
    tx_hash = Lend_token.transfer(_lend_and_borrow_token_holder, Web3.toWei(1000, 'ether'), transact={'from': Whale})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    # _lend_and_borrow_token_holder buys 5 Borrow_token from a 3rd party exchange
    tx_hash = Borrow_token.transfer(_lend_and_borrow_token_holder, Web3.toWei(5, 'ether'), transact={'from': Whale})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    # _lend_and_borrow_token_holder authorizes CurrencyDao to spend 800 Lend_token
    tx_hash = Lend_token.approve(CurrencyDao.address, Web3.toWei(800, 'ether'), transact={'from': _lend_and_borrow_token_holder})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    # _lend_and_borrow_token_holder authorizes CurrencyDao to spend 4 Borrow_token
    tx_hash = Borrow_token.approve(CurrencyDao.address, Web3.toWei(4, 'ether'), transact={'from': _lend_and_borrow_token_holder})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    # _lend_and_borrow_token_holder wraps 800 Lend_token to L_lend_token
    tx_hash = CurrencyDao.wrap(Lend_token.address, Web3.toWei(800, 'ether'), transact={'from': _lend_and_borrow_token_holder, 'gas': 145000})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    # _lend_and_borrow_token_holder wraps 4 Borrow_tokens to 4 L_borrow_tokens
    tx_hash = CurrencyDao.wrap(Borrow_token.address, Web3.toWei(4, 'ether'), transact={'from': _lend_and_borrow_token_holder, 'gas': 145000})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    # _lend_and_borrow_token_holder splits 500 L_lend_tokens into 500 I_lend_tokens and 500 S_lend_tokens and 500 U_lend_tokens for H20, Borrow_token, and STRIKE_200
    tx_hash = UnderwriterPoolDao.split(Lend_token.address, H20, Borrow_token.address, STRIKE_125, Web3.toWei(500, 'ether'), transact={'from': _lend_and_borrow_token_holder, 'gas': 1100000})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    _i_lend_id = I_lend_token.id(Lend_token.address, H20, ZERO_ADDRESS, 0)
    _s_lend_id = S_lend_token.id(Lend_token.address, H20, Borrow_token.address, STRIKE_125)
    _u_lend_id = U_lend_token.id(Lend_token.address, H20, Borrow_token.address, STRIKE_125)
    # _lend_and_borrow_token_holder splits 4 L_borrow_tokens into 4 F_borrow_tokens and 4 I_borrow_tokens for H20
    tx_hash = InterestPoolDao.split(Borrow_token.address, H20, Web3.toWei(4, 'ether'), transact={'from': _lend_and_borrow_token_holder, 'gas': 640000})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    _f_borrow_id = F_borrow_token.id(Borrow_token.address, H20, ZERO_ADDRESS, 0)
    _i_borrow_id = I_borrow_token.id(Borrow_token.address, H20, ZERO_ADDRESS, 0)
    # _lend_and_borrow_token_holder avails a loan for 500 Lend_tokens
    # For this, she places 4 F_borrow_tokens, 500 I_lend_tokens and 500 S_lend_tokens as collateral
    tx_hash = PositionRegistry.avail_loan(Lend_token.address, H20, Borrow_token.address, STRIKE_125, Web3.toWei(500, 'ether'), transact={'from': _lend_and_borrow_token_holder, 'gas': 900000})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    _position_id = PositionRegistry.borrow_position(_lend_and_borrow_token_holder, 1)
    assert PositionRegistry.positions__status(_position_id) == PositionRegistry.LOAN_STATUS_ACTIVE()
    assert PositionRegistry.positions__repaid_value(_position_id) == 0
    # _lend_and_borrow_token_holder authorizes CurrencyDao to spend 300 Lend_token
    tx_hash = Lend_token.approve(CurrencyDao.address, Web3.toWei(500, 'ether'), transact={'from': _lend_and_borrow_token_holder})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    assert Lend_token.allowance(_lend_and_borrow_token_holder, CurrencyDao.address) == Web3.toWei(500, 'ether')
    # _lend_and_borrow_token_holder closes the loan
    tx_hash = PositionRegistry.repay_loan(_position_id, Web3.toWei(500, 'ether'), transact={'from': _lend_and_borrow_token_holder, 'gas': 500000})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    print('\n\n tx_receipt:\n{0}\n\n'.format(tx_receipt))
    assert tx_receipt['status'] == 1
    assert PositionRegistry.positions__repaid_value(_position_id) == Web3.toWei(500, 'ether')
    assert PositionRegistry.positions__status(_position_id) == PositionRegistry.LOAN_STATUS_CLOSED()


# def test_situation_after_loan_market_settlement_for_expiry_price_above_original_price(w3, get_contract, get_logs, time_travel,
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
#     tx_hash = UnderwriterPoolDao.set_offer_registration_fee_lookup(_minimum_fee,
#         _minimum_interval, _fee_multiplier, _fee_multiplier_decimals,
#         transact={'from': owner})
#     tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
#     assert tx_receipt['status'] == 1
#     # set_currency_support for Lend_token in CurrencyDao
#     tx_hash = CurrencyDao.set_currency_support(Lend_token.address, True,
#         transact={'from': owner, 'gas': 1570000})
#     tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
#     assert tx_receipt['status'] == 1
#     # set_currency_support for Borrow_token in CurrencyDao
#     tx_hash = CurrencyDao.set_currency_support(Borrow_token.address, True,
#         transact={'from': owner, 'gas': 1570000})
#     tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
#     assert tx_receipt['status'] == 1
#     # register_pool for Lend_token
#     pool_owner = w3.eth.accounts[1]
#     tx_hash = UnderwriterPoolDao.register_pool(Lend_token.address,
#         'Underwriter Pool A', 'UPA', 50,
#         transact={'from': pool_owner, 'gas': 850000})
#     tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
#     assert tx_receipt['status'] == 1
#     # get UnderwriterPool contract
#     logs_8 = get_logs(tx_hash, UnderwriterPoolDao, "PoolRegistered")
#     _pool_hash = UnderwriterPoolDao.pool_hash(Lend_token.address, logs_8[0].args._pool_address)
#     UnderwriterPool = get_contract(
#         'contracts/templates/UnderwriterPoolTemplate1.v.py',
#         interfaces=[
#             'ERC20', 'ERC1155', 'ERC1155TokenReceiver', 'UnderwriterPoolDao'
#         ],
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
#     tx_hash = LST_token.approve(CurrencyDao.address, UnderwriterPoolDao.offer_registration_fee() * (10 ** 18),
#         transact={'from': pool_owner})
#     tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
#     assert tx_receipt['status'] == 1
#     # pool_owner registers an expiry : Last Thursday of December 2019, i.e., December 26th, 2019, i.e., H20
#     _strike_price = 200 * 10 ** 18
#     tx_hash = UnderwriterPool.register_expiry(H20, Borrow_token.address,
#         _strike_price, transact={'from': pool_owner, 'gas': 2600000})
#     tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
#     assert tx_receipt['status'] == 1
#     # get L_currency_token
#     L_currency_token = get_contract(
#         'contracts/templates/ERC20Template1.v.py',
#         address=CurrencyDao.currencies__l_currency_address(Lend_token.address)
#     )
#     # get L_underlying_token
#     L_underlying_token = get_contract(
#         'contracts/templates/ERC20Template1.v.py',
#         address=CurrencyDao.currencies__l_currency_address(Borrow_token.address)
#     )
#     # assign one of the accounts as a Lender
#     Lender = w3.eth.accounts[2]
#     # Lender buys 1000 lend token from a 3rd party exchange
#     tx_hash = Lend_token.transfer(Lender, 1000 * 10 ** 18, transact={'from': owner})
#     tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
#     assert tx_receipt['status'] == 1
#     # Lender authorizes CurrencyDao to spend 800 lend currency
#     tx_hash = Lend_token.approve(CurrencyDao.address, 800 * (10 ** 18),
#         transact={'from': Lender})
#     tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
#     assert tx_receipt['status'] == 1
#     # Lender deposits 800 Lend_tokens to Currency Pool and gets l_tokens
#     tx_hash = CurrencyDao.currency_to_l_currency(Lend_token.address, 800 * 10 ** 18,
#         transact={'from': Lender, 'gas': 200000})
#     tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
#     assert tx_receipt['status'] == 1
#     # Lender purchases UnderwriterPoolCurrency for 800 L_tokens
#     # Lender gets 40000 UnderwriterPoolCurrency tokens
#     # 800 L_tokens are deposited into UnderwriterPool account
#     tx_hash = UnderwriterPool.purchase_pool_currency(800 * 10 ** 18, transact={'from': Lender})
#     tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
#     assert tx_receipt['status'] == 1
#     # vefiry shield_currency_price is not set
#     multi_fungible_addresses = CurrencyDao.multi_fungible_addresses(Lend_token.address)
#     _s_hash = UnderwriterPoolDao.multi_fungible_currency_hash(
#         multi_fungible_addresses[3], Lend_token.address, H20,
#         Borrow_token.address, _strike_price)
#     _i_hash = UnderwriterPoolDao.multi_fungible_currency_hash(
#         multi_fungible_addresses[1], Lend_token.address, H20, ZERO_ADDRESS, 0)
#     # pool_owner initiates offer of 600 I_tokens from the UnderwriterPool
#     # 600 L_tokens burned from UnderwriterPool account
#     # 600 I_tokens, 3 S_tokens, and 3 U_tokens minted to UnderwriterPool account
#     tx_hash = UnderwriterPool.increment_i_currency_supply(
#         H20, Borrow_token.address, _strike_price, 600 * 10 ** 18,
#         transact={'from': pool_owner, 'gas': 600000})
#     tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
#     assert tx_receipt['status'] == 1
#     # get I_token
#     I_token = get_contract(
#         'contracts/templates/ERC1155Template2.v.py',
#         interfaces=['ERC1155TokenReceiver'],
#         address=CurrencyDao.currencies__i_currency_address(Lend_token.address)
#     )
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
#     # High_Risk_Insurer purchases 100 i_tokens from UnderwriterPool
#     tx_hash = UnderwriterPool.purchase_i_currency(H20, Borrow_token.address,
#         _strike_price, 100 * 10 ** 18, 0, transact={'from': High_Risk_Insurer})
#     tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
#     assert tx_receipt['status'] == 1
#     # High_Risk_Insurer purchases 2 s_tokens from UnderwriterPool
#     tx_hash = UnderwriterPool.purchase_s_currency(H20, Borrow_token.address,
#         _strike_price, 2 * 10 ** 18, 0, transact={'from': High_Risk_Insurer})
#     tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
#     assert tx_receipt['status'] == 1
#     # assign one of the accounts as a Borrower
#     Borrower = w3.eth.accounts[3]
#     # Borrower purchases 10 Borrow_tokens from a 3rd party exchange
#     tx_hash = Borrow_token.transfer(Borrower, 10 * 10 ** 18, transact={'from': owner})
#     tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
#     assert tx_receipt['status'] == 1
#     assert Borrow_token.balanceOf(Borrower) == 10 * 10 ** 18
#     # Borrower authorizes CurrencyDao to spend 2 Borrow_tokens
#     tx_hash = Borrow_token.approve(CurrencyDao.address, 3 * (10 ** 18),
#         transact={'from': Borrower})
#     tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
#     assert tx_receipt['status'] == 1
#     # Borrower deposits 2 Borrow_tokens to Currency Pool and gets l_tokens
#     tx_hash = CurrencyDao.currency_to_l_currency(Borrow_token.address, 3 * 10 ** 18,
#         transact={'from': Borrower, 'gas': 200000})
#     tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
#     assert tx_receipt['status'] == 1
#     # Borrower wishes to avail a loan of 400 Lend_tokens
#     # High_Risk_Insurer authorizes CurrencyDao to spend his S_token
#     tx_hash = S_token.setApprovalForAll(CurrencyDao.address, True,
#         transact={'from': High_Risk_Insurer})
#     tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
#     assert tx_receipt['status'] == 1
#     # High_Risk_Insurer authorizes CurrencyDao to spend his I_token
#     tx_hash = I_token.setApprovalForAll(CurrencyDao.address, True,
#         transact={'from': High_Risk_Insurer})
#     tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
#     assert tx_receipt['status'] == 1
#     # High_Risk_Insurer sets an offer of 2 s_tokens for 20 i_tokens
#     assert PositionRegistry.last_offer_index() == 0
#     tx_hash = PositionRegistry.create_offer(
#         Lend_token.address, H20, Borrow_token.address, _strike_price,
#         2, 20, 5 * 10 ** 15,
#         transact={'from': High_Risk_Insurer, 'gas': 450000})
#     tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
#     assert tx_receipt['status'] == 1
#     # Borrower purchases this offer for the amount of 0.1 ETH
#     # 20 i_tokens and 2 s_tokens are transferred from High_Risk_Insurer account to MarketDao
#     tx_hash = PositionRegistry.avail_loan(0,
#         transact={'from': Borrower, 'value': 10 ** 17, 'gas': 950000})
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
#         interfaces=['ERC20', 'MarketDao'],
#         address=CollateralAuctionDao.graphs(_loan_market_hash)
#     )
#     time_travel(H20)
#     # update price feed
#     tx_hash = PriceFeed.set_price(240 * 10 ** 18, transact={'from': owner})
#     tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
#     assert tx_receipt['status'] == 1
#     # assign one of the accounts as a _loan_market_settler
#     _loan_market_settler = w3.eth.accounts[3]
#     assert MarketDao.loan_markets__status(_loan_market_hash) == MarketDao.LOAN_MARKET_STATUS_OPEN()
#     assert MarketDao.loan_markets__currency_value_per_underlying_at_expiry(_loan_market_hash) == 0
#     assert MarketDao.loan_markets__total_outstanding_currency_value_at_expiry(_loan_market_hash) == 400 * 10 ** 18
#     assert MarketDao.loan_markets__total_outstanding_underlying_value_at_expiry(_loan_market_hash) == 2 * 10 ** 18
#     tx_hash = MarketDao.settle_loan_market(_loan_market_hash, transact={'from': _loan_market_settler, 'gas': 280000})
#     tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
#     assert tx_receipt['status'] == 1
#     assert MarketDao.loan_markets__status(_loan_market_hash) == MarketDao.LOAN_MARKET_STATUS_SETTLING()
#     assert MarketDao.loan_markets__currency_value_per_underlying_at_expiry(_loan_market_hash) == 240 * 10 ** 18
#     assert MarketDao.loan_markets__total_outstanding_currency_value_at_expiry(_loan_market_hash) == 400 * 10 ** 18
#     assert MarketDao.loan_markets__total_outstanding_underlying_value_at_expiry(_loan_market_hash) == 2 * 10 ** 18
#     # assign one of the accounts as an _auctioned_collateral_purchaser
#     _auctioned_collateral_purchaser = w3.eth.accounts[4]
#     # _auctioned_collateral_purchaser buys 1000 lend token from a 3rd party exchange
#     tx_hash = Lend_token.transfer(_auctioned_collateral_purchaser, 1000 * 10 ** 18, transact={'from': owner})
#     tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
#     assert tx_receipt['status'] == 1
#     # _auctioned_collateral_purchaser authorizes CurrencyDao to spend 800 lend currency
#     tx_hash = Lend_token.approve(CurrencyDao.address, 800 * (10 ** 18),
#         transact={'from': _auctioned_collateral_purchaser})
#     tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
#     assert tx_receipt['status'] == 1
#     time_travel(H20 + 10 * 60)
#     # _auctioned_collateral_purchaser purchases 1.5 Borrow_tokens for 210.6 Lend_tokens
#     assert Auction.is_active() == True
#     assert Auction.current_price() == 216.32 * 10 ** 18
#     assert Auction.currency_value_remaining() == 400 * 10 ** 18
#     assert MarketDao.loan_markets__total_currency_raised_during_auction(_loan_market_hash) == 0
#     assert MarketDao.loan_markets__total_underlying_sold_during_auction(_loan_market_hash) == 0
#     assert MarketDao.loan_markets__underlying_settlement_price_per_currency(_loan_market_hash) == 0
#     _underlying_value = Auction.currency_value_remaining() / Auction.current_price()
#     tx_hash = Auction.purchase(Web3.toWei(_underlying_value, 'ether'), transact={'from': _auctioned_collateral_purchaser, 'gas': 220000})
#     tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
#     assert tx_receipt['status'] == 1
#     assert MarketDao.loan_markets__total_currency_raised_during_auction(_loan_market_hash) == 400 * 10 ** 18 - Auction.currency_value_remaining()
#     assert MarketDao.loan_markets__total_underlying_sold_during_auction(_loan_market_hash) == Web3.toWei(_underlying_value, 'ether')
#     assert MarketDao.loan_markets__underlying_settlement_price_per_currency(_loan_market_hash) == 0
#     tx_hash = Auction.purchase_for_remaining_currency(transact={'from': _auctioned_collateral_purchaser, 'gas': 280000})
#     tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
#     assert tx_receipt['status'] == 1
#     assert Auction.is_active() == False
#     assert MarketDao.loan_markets__status(_loan_market_hash) == MarketDao.LOAN_MARKET_STATUS_CLOSED()
#     assert MarketDao.loan_markets__total_currency_raised_during_auction(_loan_market_hash) == 400 * 10 ** 18
#     assert MarketDao.loan_markets__total_underlying_sold_during_auction(_loan_market_hash) == 1849586800695850701
#     assert MarketDao.loan_markets__underlying_settlement_price_per_currency(_loan_market_hash) == 216264519107463452257


# def test_l_token_balances_until_loan_market_settlement_for_expiry_price_below_original_price(w3, get_contract, get_logs, time_travel,
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
#     tx_hash = UnderwriterPoolDao.set_offer_registration_fee_lookup(_minimum_fee,
#         _minimum_interval, _fee_multiplier, _fee_multiplier_decimals,
#         transact={'from': owner})
#     tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
#     assert tx_receipt['status'] == 1
#     # set_currency_support for Lend_token in CurrencyDao
#     tx_hash = CurrencyDao.set_currency_support(Lend_token.address, True,
#         transact={'from': owner, 'gas': 1570000})
#     tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
#     assert tx_receipt['status'] == 1
#     # set_currency_support for Borrow_token in CurrencyDao
#     tx_hash = CurrencyDao.set_currency_support(Borrow_token.address, True,
#         transact={'from': owner, 'gas': 1570000})
#     tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
#     assert tx_receipt['status'] == 1
#     # register_pool for Lend_token
#     pool_owner = w3.eth.accounts[1]
#     tx_hash = UnderwriterPoolDao.register_pool(Lend_token.address,
#         'Underwriter Pool A', 'UPA', 50,
#         transact={'from': pool_owner, 'gas': 850000})
#     tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
#     assert tx_receipt['status'] == 1
#     # get UnderwriterPool contract
#     logs_8 = get_logs(tx_hash, UnderwriterPoolDao, "PoolRegistered")
#     _pool_hash = UnderwriterPoolDao.pool_hash(Lend_token.address, logs_8[0].args._pool_address)
#     UnderwriterPool = get_contract(
#         'contracts/templates/UnderwriterPoolTemplate1.v.py',
#         interfaces=[
#             'ERC20', 'ERC1155', 'ERC1155TokenReceiver', 'UnderwriterPoolDao'
#         ],
#         address=UnderwriterPoolDao.pools__pool_address(_pool_hash)
#     )
#     # get UnderwriterPoolCurrency
#     UnderwriterPoolCurrency = get_contract(
#         'contracts/templates/ERC20Template1.v.py',
#         address=UnderwriterPool.pool_currency_address()
#     )
#     # pool_owner buys LST from a 3rd party
#     LST_token.transfer(pool_owner, Web3.toWei(1000, 'ether'), transact={'from': owner})
#     # pool_owner authorizes CurrencyDao to spend LST required for offer_registration_fee
#     tx_hash = LST_token.approve(CurrencyDao.address, UnderwriterPoolDao.offer_registration_fee() * (10 ** 18),
#         transact={'from': pool_owner})
#     tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
#     assert tx_receipt['status'] == 1
#     # pool_owner registers an expiry : Last Thursday of December 2019, i.e., December 26th, 2019, i.e., H20
#     _strike_price = Web3.toWei(200, 'ether')
#     tx_hash = UnderwriterPool.register_expiry(H20, Borrow_token.address,
#         _strike_price, transact={'from': pool_owner, 'gas': 2600000})
#     tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
#     assert tx_receipt['status'] == 1
#     # get L_currency_token
#     L_currency_token = get_contract(
#         'contracts/templates/ERC20Template1.v.py',
#         address=CurrencyDao.currencies__l_currency_address(Lend_token.address)
#     )
#     _currency_pool_hash = CurrencyDao.pool_hash(Lend_token.address)
#     # get L_underlying_token
#     L_underlying_token = get_contract(
#         'contracts/templates/ERC20Template1.v.py',
#         address=CurrencyDao.currencies__l_currency_address(Borrow_token.address)
#     )
#     _underlying_pool_hash = CurrencyDao.pool_hash(Borrow_token.address)
#     # assign one of the accounts as a Lender
#     Lender = w3.eth.accounts[2]
#     # Lender buys 1000 lend token from a 3rd party exchange
#     tx_hash = Lend_token.transfer(Lender, Web3.toWei(1000, 'ether'), transact={'from': owner})
#     tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
#     assert tx_receipt['status'] == 1
#     # Lender authorizes CurrencyDao to spend 800 lend currency
#     tx_hash = Lend_token.approve(CurrencyDao.address, Web3.toWei(800, 'ether'),
#         transact={'from': Lender})
#     tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
#     assert tx_receipt['status'] == 1
#     # verify l_lend_currency supply and lend_currency_balance
#     assert L_currency_token.totalSupply() == 0
#     assert Lend_token.balanceOf(CurrencyDao.pools__pool_address(_currency_pool_hash)) == 0
#     # Lender deposits 800 Lend_tokens to Currency Pool and gets l_tokens
#     tx_hash = CurrencyDao.currency_to_l_currency(Lend_token.address, Web3.toWei(800, 'ether'),
#         transact={'from': Lender, 'gas': 200000})
#     tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
#     assert tx_receipt['status'] == 1
#     # verify l_lend_currency supply, l_lend_currency balance and lend_currency balance
#     assert L_currency_token.totalSupply() == Web3.toWei(800, 'ether')
#     assert L_currency_token.balanceOf(Lender) == Web3.toWei(800, 'ether')
#     assert L_currency_token.balanceOf(UnderwriterPool.address) == 0
#     assert Lend_token.balanceOf(CurrencyDao.pools__pool_address(_currency_pool_hash)) == Web3.toWei(800, 'ether')
#     # Lender purchases UnderwriterPoolCurrency for 800 L_tokens
#     # Lender gets 40000 UnderwriterPoolCurrency tokens
#     # 800 L_tokens are deposited into UnderwriterPool account
#     tx_hash = UnderwriterPool.purchase_pool_currency(Web3.toWei(800, 'ether'), transact={'from': Lender})
#     tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
#     assert tx_receipt['status'] == 1
#     # verify l_lend_currency supply, l_lend_currency balance and lend_currency balance
#     assert L_currency_token.totalSupply() == Web3.toWei(800, 'ether')
#     assert L_currency_token.balanceOf(Lender) == 0
#     assert L_currency_token.balanceOf(UnderwriterPool.address) == Web3.toWei(800, 'ether')
#     assert Lend_token.balanceOf(CurrencyDao.pools__pool_address(_currency_pool_hash)) == Web3.toWei(800, 'ether')
#     # vefiry shield_currency_price is not set
#     multi_fungible_addresses = CurrencyDao.multi_fungible_addresses(Lend_token.address)
#     _s_hash = UnderwriterPoolDao.multi_fungible_currency_hash(
#         multi_fungible_addresses[3], Lend_token.address, H20,
#         Borrow_token.address, _strike_price)
#     _i_hash = UnderwriterPoolDao.multi_fungible_currency_hash(
#         multi_fungible_addresses[1], Lend_token.address, H20, ZERO_ADDRESS, 0)
#     # pool_owner initiates offer of 600 I_tokens from the UnderwriterPool
#     # 600 L_tokens burned from UnderwriterPool account
#     # 600 I_tokens, 3 S_tokens, and 3 U_tokens minted to UnderwriterPool account
#     tx_hash = UnderwriterPool.increment_i_currency_supply(
#         H20, Borrow_token.address, _strike_price, Web3.toWei(600, 'ether'),
#         transact={'from': pool_owner, 'gas': 600000})
#     tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
#     assert tx_receipt['status'] == 1
#     # verify l_lend_currency supply, l_lend_currency balance and lend_currency balance
#     assert L_currency_token.totalSupply() == Web3.toWei(200, 'ether')
#     assert L_currency_token.balanceOf(UnderwriterPool.address) == Web3.toWei(200, 'ether')
#     assert Lend_token.balanceOf(CurrencyDao.pools__pool_address(_currency_pool_hash)) == Web3.toWei(800, 'ether')
#     # get I_token
#     I_token = get_contract(
#         'contracts/templates/ERC1155Template2.v.py',
#         interfaces=['ERC1155TokenReceiver'],
#         address=CurrencyDao.currencies__i_currency_address(Lend_token.address)
#     )
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
#     # High_Risk_Insurer purchases 100 i_tokens from UnderwriterPool
#     tx_hash = UnderwriterPool.purchase_i_currency(H20, Borrow_token.address,
#         _strike_price, Web3.toWei(100, 'ether'), 0, transact={'from': High_Risk_Insurer})
#     tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
#     assert tx_receipt['status'] == 1
#     # High_Risk_Insurer purchases 2 s_tokens from UnderwriterPool
#     tx_hash = UnderwriterPool.purchase_s_currency(H20, Borrow_token.address,
#         _strike_price, Web3.toWei(2, 'ether'), 0, transact={'from': High_Risk_Insurer})
#     tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
#     assert tx_receipt['status'] == 1
#     # assign one of the accounts as a Borrower
#     Borrower = w3.eth.accounts[3]
#     # Borrower purchases 10 Borrow_tokens from a 3rd party exchange
#     tx_hash = Borrow_token.transfer(Borrower, Web3.toWei(10, 'ether'), transact={'from': owner})
#     tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
#     assert tx_receipt['status'] == 1
#     assert Borrow_token.balanceOf(Borrower) == Web3.toWei(10, 'ether')
#     # Borrower authorizes CurrencyDao to spend 2 Borrow_tokens
#     tx_hash = Borrow_token.approve(CurrencyDao.address, Web3.toWei(3, 'ether'),
#         transact={'from': Borrower})
#     tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
#     assert tx_receipt['status'] == 1
#     # verify l_borrow_currency supply, l_borrow_currency balance and borrow_currency balance
#     assert L_underlying_token.totalSupply() == 0
#     assert L_underlying_token.balanceOf(Borrower) == 0
#     assert L_underlying_token.balanceOf(UnderwriterPool.address) == 0
#     assert Borrow_token.balanceOf(CurrencyDao.pools__pool_address(_underlying_pool_hash)) == 0
#     # Borrower deposits 3 Borrow_tokens to Currency Pool and gets l_tokens
#     tx_hash = CurrencyDao.currency_to_l_currency(Borrow_token.address, Web3.toWei(3, 'ether'),
#         transact={'from': Borrower, 'gas': 200000})
#     tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
#     assert tx_receipt['status'] == 1
#     # verify l_borrow_currency supply, l_borrow_currency balance and borrow_currency balance
#     assert L_underlying_token.totalSupply() == Web3.toWei(3, 'ether')
#     assert L_underlying_token.balanceOf(Borrower) == Web3.toWei(3, 'ether')
#     assert L_underlying_token.balanceOf(MarketDao.address) == 0
#     assert Borrow_token.balanceOf(CurrencyDao.pools__pool_address(_underlying_pool_hash)) == Web3.toWei(3, 'ether')
#     # Borrower wishes to avail a loan of 400 Lend_tokens
#     # High_Risk_Insurer authorizes CurrencyDao to spend his S_token
#     tx_hash = S_token.setApprovalForAll(CurrencyDao.address, True,
#         transact={'from': High_Risk_Insurer})
#     tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
#     assert tx_receipt['status'] == 1
#     # High_Risk_Insurer authorizes CurrencyDao to spend his I_token
#     tx_hash = I_token.setApprovalForAll(CurrencyDao.address, True,
#         transact={'from': High_Risk_Insurer})
#     tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
#     assert tx_receipt['status'] == 1
#     # High_Risk_Insurer sets an offer of 2 s_tokens for 20 i_tokens
#     assert PositionRegistry.last_offer_index() == 0
#     tx_hash = PositionRegistry.create_offer(
#         Lend_token.address, H20, Borrow_token.address, _strike_price,
#         2, 20, 5 * 10 ** 15,
#         transact={'from': High_Risk_Insurer, 'gas': 450000})
#     tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
#     assert tx_receipt['status'] == 1
#     # verify l_lend_currency supply, l_lend_currency balance and lend_currency balance
#     assert L_currency_token.totalSupply() == Web3.toWei(200, 'ether')
#     assert L_currency_token.balanceOf(UnderwriterPool.address) == Web3.toWei(200, 'ether')
#     assert Lend_token.balanceOf(CurrencyDao.pools__pool_address(_currency_pool_hash)) == Web3.toWei(800, 'ether')
#     # Borrower purchases this offer for the amount of 0.1 ETH
#     # 20 i_tokens and 2 s_tokens are transferred from High_Risk_Insurer account to MarketDao
#     tx_hash = PositionRegistry.avail_loan(0,
#         transact={'from': Borrower, 'value': 10 ** 17, 'gas': 950000})
#     tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
#     assert tx_receipt['status'] == 1
#     # verify l_lend_currency supply, l_lend_currency balance and lend_currency balance
#     assert L_currency_token.totalSupply() == Web3.toWei(200, 'ether')
#     assert L_currency_token.balanceOf(UnderwriterPool.address) == Web3.toWei(200, 'ether')
#     assert Lend_token.balanceOf(CurrencyDao.pools__pool_address(_currency_pool_hash)) == Web3.toWei(400, 'ether')
#     # verify Lend_token balance of Borrower
#     assert Lend_token.balanceOf(Borrower) == Web3.toWei(400, 'ether')
#     # verify l_borrow_currency supply, l_borrow_currency balance and borrow_currency balance
#     assert L_underlying_token.totalSupply() == Web3.toWei(3, 'ether')
#     assert L_underlying_token.balanceOf(Borrower) == Web3.toWei(1, 'ether')
#     assert L_underlying_token.balanceOf(MarketDao.address) == Web3.toWei(2, 'ether')
#     assert Borrow_token.balanceOf(CurrencyDao.pools__pool_address(_underlying_pool_hash)) == Web3.toWei(3, 'ether')
#     # get Auction contract
#     _loan_market_hash = CollateralAuctionDao.loan_market_hash(
#         Lend_token.address, H20, Borrow_token.address
#     )
#     Auction = get_contract(
#         'contracts/templates/SimpleCollateralAuctionGraph.v.py',
#         interfaces=['ERC20', 'MarketDao'],
#         address=CollateralAuctionDao.graphs(_loan_market_hash)
#     )
#     time_travel(H20)
#     # update price feed
#     tx_hash = PriceFeed.set_price(Web3.toWei(150, 'ether'), transact={'from': owner})
#     tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
#     assert tx_receipt['status'] == 1
#     # assign one of the accounts as a _loan_market_settler
#     _loan_market_settler = w3.eth.accounts[3]
#     assert MarketDao.loan_markets__status(_loan_market_hash) == MarketDao.LOAN_MARKET_STATUS_OPEN()
#     assert MarketDao.loan_markets__currency_value_per_underlying_at_expiry(_loan_market_hash) == 0
#     assert MarketDao.loan_markets__total_outstanding_currency_value_at_expiry(_loan_market_hash) == Web3.toWei(400, 'ether')
#     assert MarketDao.loan_markets__total_outstanding_underlying_value_at_expiry(_loan_market_hash) == Web3.toWei(2, 'ether')
#     # verify l_lend_currency supply, l_lend_currency balance and lend_currency balance
#     assert L_currency_token.totalSupply() == Web3.toWei(200, 'ether')
#     assert L_currency_token.balanceOf(UnderwriterPool.address) == Web3.toWei(200, 'ether')
#     assert Lend_token.balanceOf(CurrencyDao.pools__pool_address(_currency_pool_hash)) == Web3.toWei(400, 'ether')
#     # verify l_borrow_currency supply, l_borrow_currency balance and borrow_currency balance
#     assert L_underlying_token.totalSupply() == Web3.toWei(3, 'ether')
#     assert L_underlying_token.balanceOf(Borrower) == Web3.toWei(1, 'ether')
#     assert L_underlying_token.balanceOf(MarketDao.address) == Web3.toWei(2, 'ether')
#     assert Borrow_token.balanceOf(Auction.address) == 0
#     assert Borrow_token.balanceOf(CurrencyDao.pools__pool_address(_underlying_pool_hash)) == Web3.toWei(3, 'ether')
#     tx_hash = MarketDao.settle_loan_market(_loan_market_hash, transact={'from': _loan_market_settler, 'gas': 280000})
#     tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
#     assert tx_receipt['status'] == 1
#     assert MarketDao.loan_markets__status(_loan_market_hash) == MarketDao.LOAN_MARKET_STATUS_SETTLING()
#     assert MarketDao.loan_markets__currency_value_per_underlying_at_expiry(_loan_market_hash) == Web3.toWei(150, 'ether')
#     assert MarketDao.loan_markets__total_outstanding_currency_value_at_expiry(_loan_market_hash) == Web3.toWei(400, 'ether')
#     assert MarketDao.loan_markets__total_outstanding_underlying_value_at_expiry(_loan_market_hash) == Web3.toWei(2, 'ether')
#     # verify l_lend_currency supply, l_lend_currency balance and lend_currency balance
#     assert L_currency_token.totalSupply() == Web3.toWei(200, 'ether')
#     assert L_currency_token.balanceOf(UnderwriterPool.address) == Web3.toWei(200, 'ether')
#     assert Lend_token.balanceOf(CurrencyDao.pools__pool_address(_currency_pool_hash)) == Web3.toWei(400, 'ether')
#     # verify l_borrow_currency supply, l_borrow_currency balance and borrow_currency balance
#     assert L_underlying_token.totalSupply() == Web3.toWei(1, 'ether')
#     assert L_underlying_token.balanceOf(Borrower) == Web3.toWei(1, 'ether')
#     assert L_underlying_token.balanceOf(MarketDao.address) == 0
#     assert Borrow_token.balanceOf(Auction.address) == Web3.toWei(2, 'ether')
#     assert Borrow_token.balanceOf(CurrencyDao.pools__pool_address(_underlying_pool_hash)) == Web3.toWei(1, 'ether')
#     # assign one of the accounts as an _auctioned_collateral_purchaser
#     _auctioned_collateral_purchaser = w3.eth.accounts[4]
#     # _auctioned_collateral_purchaser buys 1000 lend token from a 3rd party exchange
#     tx_hash = Lend_token.transfer(_auctioned_collateral_purchaser, 1000 * 10 ** 18, transact={'from': owner})
#     tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
#     assert tx_receipt['status'] == 1
#     # _auctioned_collateral_purchaser authorizes CurrencyDao to spend 800 lend currency
#     tx_hash = Lend_token.approve(CurrencyDao.address, 800 * (10 ** 18),
#         transact={'from': _auctioned_collateral_purchaser})
#     tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
#     assert tx_receipt['status'] == 1
#     time_travel(H20 + 10 * 60)
#     assert Auction.is_active() == True
#     assert Auction.current_price() == Web3.toWei(135.2, 'ether')
#     assert Auction.currency_value_remaining() == Web3.toWei(400, 'ether')
#     assert MarketDao.loan_markets__total_currency_raised_during_auction(_loan_market_hash) == 0
#     assert MarketDao.loan_markets__total_underlying_sold_during_auction(_loan_market_hash) == 0
#     assert MarketDao.loan_markets__underlying_settlement_price_per_currency(_loan_market_hash) == 0
#     # verify l_lend_currency supply, l_lend_currency balance and lend_currency balance
#     assert L_currency_token.totalSupply() == Web3.toWei(200, 'ether')
#     assert L_currency_token.balanceOf(UnderwriterPool.address) == Web3.toWei(200, 'ether')
#     assert Lend_token.balanceOf(CurrencyDao.pools__pool_address(_currency_pool_hash)) == Web3.toWei(400, 'ether')
#     # verify l_borrow_currency supply, l_borrow_currency balance and borrow_currency balance
#     assert L_underlying_token.totalSupply() == Web3.toWei(1, 'ether')
#     assert L_underlying_token.balanceOf(Borrower) == Web3.toWei(1, 'ether')
#     assert Borrow_token.balanceOf(Auction.address) == Web3.toWei(2, 'ether')
#     assert Borrow_token.balanceOf(CurrencyDao.pools__pool_address(_underlying_pool_hash)) == Web3.toWei(1, 'ether')
#     # _auctioned_collateral_purchaser purchases all of the 2 Borrow_tokens for current price of Lend_tokens
#     tx_hash = Auction.purchase_for_remaining_currency(transact={'from': _auctioned_collateral_purchaser, 'gas': 280000})
#     tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
#     assert tx_receipt['status'] == 1
#     assert Auction.is_active() == False
#     assert MarketDao.loan_markets__status(_loan_market_hash) == MarketDao.LOAN_MARKET_STATUS_CLOSED()
#     assert MarketDao.loan_markets__total_currency_raised_during_auction(_loan_market_hash) == 270330666666666666666
#     assert MarketDao.loan_markets__total_underlying_sold_during_auction(_loan_market_hash) == Web3.toWei(2, 'ether')
#     assert MarketDao.loan_markets__underlying_settlement_price_per_currency(_loan_market_hash) == 135165333333333333333
#     # verify l_lend_currency supply, l_lend_currency balance and lend_currency balance
#     assert L_currency_token.totalSupply() == Web3.toWei(200, 'ether')
#     assert L_currency_token.balanceOf(UnderwriterPool.address) == Web3.toWei(200, 'ether')
#     assert Lend_token.balanceOf(CurrencyDao.pools__pool_address(_currency_pool_hash)) == 670330666666666666666
#     # verify l_borrow_currency supply, l_borrow_currency balance and borrow_currency balance
#     assert L_underlying_token.totalSupply() == Web3.toWei(1, 'ether')
#     assert L_underlying_token.balanceOf(Borrower) == Web3.toWei(1, 'ether')
#     assert Borrow_token.balanceOf(Auction.address) == 0
#     assert Borrow_token.balanceOf(CurrencyDao.pools__pool_address(_underlying_pool_hash)) == Web3.toWei(1, 'ether')


# def test_close_liquidated_loan_for_settlement_price_below_original_price(w3, get_contract, get_logs, time_travel,
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
#     tx_hash = UnderwriterPoolDao.set_offer_registration_fee_lookup(_minimum_fee,
#         _minimum_interval, _fee_multiplier, _fee_multiplier_decimals,
#         transact={'from': owner})
#     tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
#     assert tx_receipt['status'] == 1
#     # set_currency_support for Lend_token in CurrencyDao
#     tx_hash = CurrencyDao.set_currency_support(Lend_token.address, True,
#         transact={'from': owner, 'gas': 1570000})
#     tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
#     assert tx_receipt['status'] == 1
#     # set_currency_support for Borrow_token in CurrencyDao
#     tx_hash = CurrencyDao.set_currency_support(Borrow_token.address, True,
#         transact={'from': owner, 'gas': 1570000})
#     tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
#     assert tx_receipt['status'] == 1
#     # register_pool for Lend_token
#     pool_owner = w3.eth.accounts[1]
#     tx_hash = UnderwriterPoolDao.register_pool(Lend_token.address,
#         'Underwriter Pool A', 'UPA', 50,
#         transact={'from': pool_owner, 'gas': 850000})
#     tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
#     assert tx_receipt['status'] == 1
#     # get UnderwriterPool contract
#     logs_8 = get_logs(tx_hash, UnderwriterPoolDao, "PoolRegistered")
#     _pool_hash = UnderwriterPoolDao.pool_hash(Lend_token.address, logs_8[0].args._pool_address)
#     UnderwriterPool = get_contract(
#         'contracts/templates/UnderwriterPoolTemplate1.v.py',
#         interfaces=[
#             'ERC20', 'ERC1155', 'ERC1155TokenReceiver', 'UnderwriterPoolDao'
#         ],
#         address=UnderwriterPoolDao.pools__pool_address(_pool_hash)
#     )
#     # get UnderwriterPoolCurrency
#     UnderwriterPoolCurrency = get_contract(
#         'contracts/templates/ERC20Template1.v.py',
#         address=UnderwriterPool.pool_currency_address()
#     )
#     # pool_owner buys LST from a 3rd party
#     LST_token.transfer(pool_owner, Web3.toWei(1000, 'ether'), transact={'from': owner})
#     # pool_owner authorizes CurrencyDao to spend LST required for offer_registration_fee
#     tx_hash = LST_token.approve(CurrencyDao.address, Web3.toWei(UnderwriterPoolDao.offer_registration_fee(), 'ether'),
#         transact={'from': pool_owner})
#     tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
#     assert tx_receipt['status'] == 1
#     # pool_owner registers an expiry : Last Thursday of December 2019, i.e., December 26th, 2019, i.e., H20
#     _strike_price = Web3.toWei(200, 'ether')
#     tx_hash = UnderwriterPool.register_expiry(H20, Borrow_token.address,
#         _strike_price, transact={'from': pool_owner, 'gas': 2600000})
#     tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
#     assert tx_receipt['status'] == 1
#     # get L_currency_token
#     L_currency_token = get_contract(
#         'contracts/templates/ERC20Template1.v.py',
#         address=CurrencyDao.currencies__l_currency_address(Lend_token.address)
#     )
#     _currency_pool_hash = CurrencyDao.pool_hash(Lend_token.address)
#     # get L_underlying_token
#     L_underlying_token = get_contract(
#         'contracts/templates/ERC20Template1.v.py',
#         address=CurrencyDao.currencies__l_currency_address(Borrow_token.address)
#     )
#     _underlying_pool_hash = CurrencyDao.pool_hash(Borrow_token.address)
#     # assign one of the accounts as a Lender
#     Lender = w3.eth.accounts[2]
#     # Lender buys 1000 lend token from a 3rd party exchange
#     tx_hash = Lend_token.transfer(Lender, Web3.toWei(1000, 'ether'), transact={'from': owner})
#     tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
#     assert tx_receipt['status'] == 1
#     # Lender authorizes CurrencyDao to spend 800 lend currency
#     tx_hash = Lend_token.approve(CurrencyDao.address, Web3.toWei(800, 'ether'),
#         transact={'from': Lender})
#     tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
#     assert tx_receipt['status'] == 1
#     # Lender deposits 800 Lend_tokens to Currency Pool and gets l_tokens
#     assert L_currency_token.totalSupply() == 0
#     assert Lend_token.balanceOf(CurrencyDao.pools__pool_address(_currency_pool_hash)) == 0
#     tx_hash = CurrencyDao.currency_to_l_currency(Lend_token.address, Web3.toWei(800, 'ether'),
#         transact={'from': Lender, 'gas': 200000})
#     tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
#     assert tx_receipt['status'] == 1
#     # verify l_lend_currency supply, l_lend_currency balance and lend_currency balance
#     assert L_currency_token.totalSupply() == Web3.toWei(800, 'ether')
#     assert L_currency_token.balanceOf(Lender) == Web3.toWei(800, 'ether')
#     assert L_currency_token.balanceOf(UnderwriterPool.address) == 0
#     # Lender purchases UnderwriterPoolCurrency for 800 L_tokens
#     # Lender gets 40000 UnderwriterPoolCurrency tokens
#     # 800 L_tokens are deposited into UnderwriterPool account
#     tx_hash = UnderwriterPool.purchase_pool_currency(Web3.toWei(800, 'ether'), transact={'from': Lender})
#     tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
#     assert tx_receipt['status'] == 1
#     # verify l_lend_currency supply, l_lend_currency balance and lend_currency balance
#     assert L_currency_token.totalSupply() == Web3.toWei(800, 'ether')
#     assert L_currency_token.balanceOf(Lender) == 0
#     assert L_currency_token.balanceOf(UnderwriterPool.address) == Web3.toWei(800, 'ether')
#     # vefiry shield_currency_price is not set
#     multi_fungible_addresses = CurrencyDao.multi_fungible_addresses(Lend_token.address)
#     _s_hash = UnderwriterPoolDao.multi_fungible_currency_hash(
#         multi_fungible_addresses[3], Lend_token.address, H20,
#         Borrow_token.address, _strike_price)
#     _i_hash = UnderwriterPoolDao.multi_fungible_currency_hash(
#         multi_fungible_addresses[1], Lend_token.address, H20, ZERO_ADDRESS, 0)
#     # pool_owner initiates offer of 600 I_tokens from the UnderwriterPool
#     # 600 L_tokens burned from UnderwriterPool account
#     # 600 I_tokens, 3 S_tokens, and 3 U_tokens minted to UnderwriterPool account
#     tx_hash = UnderwriterPool.increment_i_currency_supply(
#         H20, Borrow_token.address, _strike_price, 600 * 10 ** 18,
#         transact={'from': pool_owner, 'gas': 600000})
#     tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
#     assert tx_receipt['status'] == 1
#     # get I_token
#     I_token = get_contract(
#         'contracts/templates/ERC1155Template2.v.py',
#         interfaces=['ERC1155TokenReceiver'],
#         address=CurrencyDao.currencies__i_currency_address(Lend_token.address)
#     )
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
#     High_Risk_Insurer = w3.eth.accounts[2]
#     # High_Risk_Insurer purchases 100 i_tokens from UnderwriterPool
#     tx_hash = UnderwriterPool.purchase_i_currency(H20, Borrow_token.address,
#         _strike_price, Web3.toWei(100, 'ether'), 0, transact={'from': High_Risk_Insurer})
#     tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
#     assert tx_receipt['status'] == 1
#     # High_Risk_Insurer purchases 2 s_tokens from UnderwriterPool
#     # The corresponding 2 u_tokens remain in the UnderwriterPool
#     tx_hash = UnderwriterPool.purchase_s_currency(H20, Borrow_token.address,
#         _strike_price, Web3.toWei(2, 'ether'), 0, transact={'from': High_Risk_Insurer})
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
#     Borrower = w3.eth.accounts[3]
#     # Borrower purchases 10 Borrow_tokens from a 3rd party exchange
#     tx_hash = Borrow_token.transfer(Borrower, Web3.toWei(10, 'ether'), transact={'from': owner})
#     tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
#     assert tx_receipt['status'] == 1
#     assert Borrow_token.balanceOf(Borrower) == Web3.toWei(10, 'ether')
#     # Borrower authorizes CurrencyDao to spend 2 Borrow_tokens
#     tx_hash = Borrow_token.approve(CurrencyDao.address, Web3.toWei(3, 'ether'),
#         transact={'from': Borrower})
#     tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
#     assert tx_receipt['status'] == 1
#     # Borrower deposits 2 Borrow_tokens to Currency Pool and gets l_tokens
#     tx_hash = CurrencyDao.currency_to_l_currency(Borrow_token.address, Web3.toWei(3, 'ether'),
#         transact={'from': Borrower, 'gas': 200000})
#     tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
#     assert tx_receipt['status'] == 1
#     # Borrower wishes to avail a loan of 400 Lend_tokens
#     # High_Risk_Insurer authorizes CurrencyDao to spend his S_token
#     tx_hash = S_token.setApprovalForAll(CurrencyDao.address, True,
#         transact={'from': High_Risk_Insurer})
#     tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
#     assert tx_receipt['status'] == 1
#     # High_Risk_Insurer authorizes CurrencyDao to spend his I_token
#     tx_hash = I_token.setApprovalForAll(CurrencyDao.address, True,
#         transact={'from': High_Risk_Insurer})
#     tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
#     assert tx_receipt['status'] == 1
#     # High_Risk_Insurer sets an offer of 2 s_tokens for 20 i_tokens
#     assert PositionRegistry.last_offer_index() == 0
#     tx_hash = PositionRegistry.create_offer(
#         Lend_token.address, H20, Borrow_token.address, _strike_price,
#         2, 20, 5 * 10 ** 15,
#         transact={'from': High_Risk_Insurer, 'gas': 450000})
#     tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
#     assert tx_receipt['status'] == 1
#     # Borrower purchases this offer for the amount of 0.1 ETH
#     # 20 i_tokens are transferred from High_Risk_Insurer account to Borrower
#     # 2 s_tokens are transferred from High_Risk_Insurer account to MarketDao
#     tx_hash = PositionRegistry.avail_loan(0,
#         transact={'from': Borrower, 'value': 10 ** 17, 'gas': 950000})
#     tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
#     assert tx_receipt['status'] == 1
#     # verify i_lend_currency supply and i_lend_currency balance
#     assert I_token.totalBalanceOf(High_Risk_Insurer) == Web3.toWei(80, 'ether')
#     assert I_token.totalBalanceOf(Borrower) == Web3.toWei(20, 'ether')
#     assert I_token.totalBalanceOf(MarketDao.address) == 0
#     assert I_token.totalBalanceOf(UnderwriterPool.address) == Web3.toWei(500, 'ether')
#     # verify s_lend_currency supply and s_lend_currency balance
#     assert S_token.totalBalanceOf(High_Risk_Insurer) == Web3.toWei(0, 'ether')
#     assert S_token.totalBalanceOf(Borrower) == 0
#     assert S_token.totalBalanceOf(MarketDao.address) == Web3.toWei(2, 'ether')
#     assert S_token.totalBalanceOf(UnderwriterPool.address) == Web3.toWei(1, 'ether')
#     # verify u_lend_currency supply and u_lend_currency balance
#     assert U_token.totalBalanceOf(High_Risk_Insurer) == 0
#     assert U_token.totalBalanceOf(Borrower) == 0
#     assert U_token.totalBalanceOf(MarketDao.address) == 0
#     assert U_token.totalBalanceOf(UnderwriterPool.address) == Web3.toWei(3, 'ether')
#     # verify Lend_token balance of Borrower
#     assert Lend_token.balanceOf(Borrower) == Web3.toWei(400, 'ether')
#     # Borrower authorizes CurrencyDao to spend 400 Lend_tokens
#     tx_hash = Lend_token.approve(CurrencyDao.address, Web3.toWei(400, 'ether'),
#         transact={'from': Borrower})
#     tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
#     assert tx_receipt['status'] == 1
#     # get Auction contract
#     _loan_market_hash = CollateralAuctionDao.loan_market_hash(
#         Lend_token.address, H20, Borrow_token.address
#     )
#     Auction = get_contract(
#         'contracts/templates/SimpleCollateralAuctionGraph.v.py',
#         interfaces=['ERC20', 'MarketDao'],
#         address=CollateralAuctionDao.graphs(_loan_market_hash)
#     )
#     # time passes until loan market expires
#     time_travel(H20)
#     # update price feed
#     tx_hash = PriceFeed.set_price(Web3.toWei(150, 'ether'), transact={'from': owner})
#     tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
#     assert tx_receipt['status'] == 1
#     # verify l_borrow_currency supply, l_borrow_currency balance and borrow_currency balance
#     assert L_underlying_token.totalSupply() == Web3.toWei(3, 'ether')
#     assert L_underlying_token.balanceOf(Borrower) == Web3.toWei(1, 'ether')
#     assert L_underlying_token.balanceOf(MarketDao.address) == Web3.toWei(2, 'ether')
#     assert Borrow_token.balanceOf(Auction.address) == 0
#     assert Borrow_token.balanceOf(CurrencyDao.pools__pool_address(_underlying_pool_hash)) == Web3.toWei(3, 'ether')
#     # assign one of the accounts as a _loan_market_settler
#     _loan_market_settler = w3.eth.accounts[3]
#     # _loan_market_settler initiates loan market settlement
#     tx_hash = MarketDao.settle_loan_market(_loan_market_hash, transact={'from': _loan_market_settler, 'gas': 280000})
#     tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
#     assert tx_receipt['status'] == 1
#     # verify l_borrow_currency supply, l_borrow_currency balance and borrow_currency balance
#     assert L_underlying_token.totalSupply() == Web3.toWei(1, 'ether')
#     assert L_underlying_token.balanceOf(Borrower) == Web3.toWei(1, 'ether')
#     assert L_underlying_token.balanceOf(MarketDao.address) == 0
#     assert Borrow_token.balanceOf(Auction.address) == Web3.toWei(2, 'ether')
#     assert Borrow_token.balanceOf(CurrencyDao.pools__pool_address(_underlying_pool_hash)) == Web3.toWei(1, 'ether')
#     assert MarketDao.loan_markets__status(_loan_market_hash) == MarketDao.LOAN_MARKET_STATUS_SETTLING()
#     # assign one of the accounts as an _auctioned_collateral_purchaser
#     _auctioned_collateral_purchaser = w3.eth.accounts[4]
#     # _auctioned_collateral_purchaser buys 1000 lend token from a 3rd party exchange
#     tx_hash = Lend_token.transfer(_auctioned_collateral_purchaser, 1000 * 10 ** 18, transact={'from': owner})
#     tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
#     assert tx_receipt['status'] == 1
#     # _auctioned_collateral_purchaser authorizes CurrencyDao to spend 800 lend currency
#     tx_hash = Lend_token.approve(CurrencyDao.address, 800 * (10 ** 18),
#         transact={'from': _auctioned_collateral_purchaser})
#     tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
#     assert tx_receipt['status'] == 1
#     time_travel(H20 + 10 * 60)
#     # _auctioned_collateral_purchaser purchases all of the 2 Borrow_tokens for current price of Lend_tokens
#     tx_hash = Auction.purchase_for_remaining_currency(transact={'from': _auctioned_collateral_purchaser, 'gas': 280000})
#     tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
#     assert tx_receipt['status'] == 1
#     assert MarketDao.loan_markets__underlying_settlement_price_per_currency(_loan_market_hash) == 135165333333333333333
#     # verify l_lend_currency supply, l_lend_currency balance and lend_currency balance
#     assert L_currency_token.totalSupply() == Web3.toWei(200, 'ether')
#     assert L_currency_token.balanceOf(UnderwriterPool.address) == Web3.toWei(200, 'ether')
#     assert L_currency_token.balanceOf(Borrower) == 0
#     # verify l_borrow_currency supply, l_borrow_currency balance and borrow_currency balance
#     assert L_underlying_token.totalSupply() == Web3.toWei(1, 'ether')
#     assert L_underlying_token.balanceOf(Borrower) == Web3.toWei(1, 'ether')
#     assert L_underlying_token.balanceOf(MarketDao.address) == 0
#     assert Borrow_token.balanceOf(Auction.address) == 0
#     assert Borrow_token.balanceOf(CurrencyDao.pools__pool_address(_underlying_pool_hash)) == Web3.toWei(1, 'ether')
#     # verify i_lend_currency supply and i_lend_currency balance
#     assert I_token.totalBalanceOf(High_Risk_Insurer) == Web3.toWei(80, 'ether')
#     assert I_token.totalBalanceOf(Borrower) == Web3.toWei(20, 'ether')
#     assert I_token.totalBalanceOf(MarketDao.address) == 0
#     assert I_token.totalBalanceOf(UnderwriterPool.address) == Web3.toWei(500, 'ether')
#     # verify s_lend_currency supply and s_lend_currency balance
#     assert S_token.totalBalanceOf(High_Risk_Insurer) == Web3.toWei(0, 'ether')
#     assert S_token.totalBalanceOf(Borrower) == 0
#     assert S_token.totalBalanceOf(MarketDao.address) == Web3.toWei(2, 'ether')
#     assert S_token.totalBalanceOf(UnderwriterPool.address) == Web3.toWei(1, 'ether')
#     # verify u_lend_currency supply and u_lend_currency balance
#     assert U_token.totalBalanceOf(High_Risk_Insurer) == 0
#     assert U_token.totalBalanceOf(Borrower) == 0
#     assert U_token.totalBalanceOf(MarketDao.address) == 0
#     assert U_token.totalBalanceOf(UnderwriterPool.address) == Web3.toWei(3, 'ether')
#     # Borrower cannot exercise his 2 s_tokens
#     assert MarketDao.shield_payout(Lend_token.address, H20, Borrow_token.address, _strike_price) == 0
#     # Borrower closes the liquidated loan
#     position_id = PositionRegistry.borrow_position(Borrower, PositionRegistry.borrow_position_count(Borrower))
#     tx_hash = PositionRegistry.close_liquidated_loan(position_id, transact={'from': Borrower, 'gas': 200000})
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
#     assert L_underlying_token.balanceOf(MarketDao.address) == 0
#     assert Borrow_token.balanceOf(CurrencyDao.pools__pool_address(_underlying_pool_hash)) == Web3.toWei(1, 'ether')
#     # verify i_lend_currency supply and i_lend_currency balance
#     assert I_token.totalBalanceOf(High_Risk_Insurer) == Web3.toWei(80, 'ether')
#     assert I_token.totalBalanceOf(Borrower) == Web3.toWei(20, 'ether')
#     assert I_token.totalBalanceOf(MarketDao.address) == 0
#     assert I_token.totalBalanceOf(UnderwriterPool.address) == Web3.toWei(500, 'ether')
#     # verify s_lend_currency supply and s_lend_currency balance
#     assert S_token.totalBalanceOf(High_Risk_Insurer) == 0
#     assert S_token.totalBalanceOf(Borrower) == 0
#     assert S_token.totalBalanceOf(MarketDao.address) == 0
#     assert S_token.totalBalanceOf(UnderwriterPool.address) == Web3.toWei(1, 'ether')
#     # verify u_lend_currency supply and u_lend_currency balance
#     assert U_token.totalBalanceOf(High_Risk_Insurer) == 0
#     assert U_token.totalBalanceOf(Borrower) == 0
#     assert U_token.totalBalanceOf(MarketDao.address) == 0
#     assert U_token.totalBalanceOf(UnderwriterPool.address) == Web3.toWei(3, 'ether')
