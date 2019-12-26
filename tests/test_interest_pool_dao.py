import os

import pytest

from web3 import Web3

from conftest import (
    PROTOCOL_CONSTANTS,
    POOL_NAME_REGISTRATION_MIN_STAKE_LST,
    ZERO_ADDRESS, EMPTY_BYTES32, Z19
)


def test_initialize(w3, Deployer, get_InterestPoolDao_contract, ProtocolDao):
    InterestPoolDao = get_InterestPoolDao_contract(address=ProtocolDao.daos(PROTOCOL_CONSTANTS['DAO_INTEREST_POOL']))
    assert not InterestPoolDao.initialized()
    tx_1_hash = ProtocolDao.initialize_interest_pool_dao(transact={'from': Deployer})
    tx_1_receipt = w3.eth.waitForTransactionReceipt(tx_1_hash)
    assert tx_1_receipt['status'] == 1
    assert InterestPoolDao.initialized()


def test_split(w3,
        Whale, Deployer, Governor,
        Lend_token,
        get_ERC20_contract, get_MFT_contract,
        get_CurrencyDao_contract, get_InterestPoolDao_contract,
        ProtocolDao):
    # get CurrencyDao
    CurrencyDao = get_CurrencyDao_contract(address=ProtocolDao.daos(PROTOCOL_CONSTANTS['DAO_CURRENCY']))
    # get InterestPoolDao
    InterestPoolDao = get_InterestPoolDao_contract(address=ProtocolDao.daos(PROTOCOL_CONSTANTS['DAO_INTEREST_POOL']))
    # assign one of the accounts as _lend_token_holder
    _lend_token_holder = w3.eth.accounts[5]
    # initialize CurrencyDao
    tx_1_hash = ProtocolDao.initialize_currency_dao(transact={'from': Deployer})
    tx_1_receipt = w3.eth.waitForTransactionReceipt(tx_1_hash)
    assert tx_1_receipt['status'] == 1
    # initialize InterestPoolDao
    tx_2_hash = ProtocolDao.initialize_interest_pool_dao(transact={'from': Deployer})
    tx_2_receipt = w3.eth.waitForTransactionReceipt(tx_2_hash)
    assert tx_2_receipt['status'] == 1
    # set support for Lend_token
    tx_3_hash = ProtocolDao.set_token_support(Lend_token.address, True, transact={'from': Governor})
    tx_3_receipt = w3.eth.waitForTransactionReceipt(tx_3_hash)
    assert tx_3_receipt['status'] == 1
    # get L_Lend_token
    L_lend_token = get_ERC20_contract(address=CurrencyDao.token_addresses__l(Lend_token.address))
    # get F_Lend_token
    F_lend_token = get_MFT_contract(address=CurrencyDao.token_addresses__f(Lend_token.address))
    # get I_Lend_token
    I_lend_token = get_MFT_contract(address=CurrencyDao.token_addresses__i(Lend_token.address))
    # _lend_token_holder buys 1000 lend token from a 3rd party exchange
    tx_4_hash = Lend_token.transfer(_lend_token_holder, Web3.toWei(1000, 'ether'), transact={'from': Whale})
    tx_4_receipt = w3.eth.waitForTransactionReceipt(tx_4_hash)
    assert tx_4_receipt['status'] == 1
    assert Lend_token.balanceOf(_lend_token_holder) == Web3.toWei(1000, 'ether')
    # _lend_token_holder authorizes CurrencyDao to spend 800 Lend_token
    tx_5_hash = Lend_token.approve(CurrencyDao.address, Web3.toWei(800, 'ether'), transact={'from': _lend_token_holder})
    tx_5_receipt = w3.eth.waitForTransactionReceipt(tx_5_hash)
    assert tx_5_receipt['status'] == 1
    assert Lend_token.allowance(_lend_token_holder, CurrencyDao.address) == Web3.toWei(800, 'ether')
    # _lend_token_holder wraps 800 Lend_token to L_lend_token
    assert L_lend_token.balanceOf(_lend_token_holder) == 0
    tx_6_hash = CurrencyDao.wrap(Lend_token.address, Web3.toWei(800, 'ether'), transact={'from': _lend_token_holder, 'gas': 145000})
    tx_6_receipt = w3.eth.waitForTransactionReceipt(tx_6_hash)
    assert tx_6_receipt['status'] == 1
    assert L_lend_token.balanceOf(_lend_token_holder) == Web3.toWei(800, 'ether')
    # _lend_token_holder splits 600 L_lend_tokens into 600 F_lend_tokens and 600 I_lend_tokens for Z19
    tx_7_hash = InterestPoolDao.split(Lend_token.address, Z19, Web3.toWei(600, 'ether'), transact={'from': _lend_token_holder, 'gas': 640000})
    tx_7_receipt = w3.eth.waitForTransactionReceipt(tx_7_hash)
    assert tx_7_receipt['status'] == 1
    assert L_lend_token.balanceOf(_lend_token_holder) == Web3.toWei(200, 'ether')
    _f_id = F_lend_token.id(Lend_token.address, Z19, ZERO_ADDRESS, 0)
    _i_id = I_lend_token.id(Lend_token.address, Z19, ZERO_ADDRESS, 0)
    assert F_lend_token.balanceOf(_lend_token_holder, _f_id) == Web3.toWei(600, 'ether')
    assert I_lend_token.balanceOf(_lend_token_holder, _i_id) == Web3.toWei(600, 'ether')


def test_fuse(w3,
        Whale, Deployer, Governor,
        Lend_token,
        get_ERC20_contract, get_MFT_contract,
        get_CurrencyDao_contract, get_InterestPoolDao_contract,
        ProtocolDao):
    # get CurrencyDao
    CurrencyDao = get_CurrencyDao_contract(address=ProtocolDao.daos(PROTOCOL_CONSTANTS['DAO_CURRENCY']))
    # get InterestPoolDao
    InterestPoolDao = get_InterestPoolDao_contract(address=ProtocolDao.daos(PROTOCOL_CONSTANTS['DAO_INTEREST_POOL']))
    # assign one of the accounts as _lend_token_holder
    _lend_token_holder = w3.eth.accounts[5]
    # initialize CurrencyDao
    tx_1_hash = ProtocolDao.initialize_currency_dao(transact={'from': Deployer})
    tx_1_receipt = w3.eth.waitForTransactionReceipt(tx_1_hash)
    assert tx_1_receipt['status'] == 1
    # initialize InterestPoolDao
    tx_2_hash = ProtocolDao.initialize_interest_pool_dao(transact={'from': Deployer})
    tx_2_receipt = w3.eth.waitForTransactionReceipt(tx_2_hash)
    assert tx_2_receipt['status'] == 1
    # set support for Lend_token
    tx_3_hash = ProtocolDao.set_token_support(Lend_token.address, True, transact={'from': Governor})
    tx_3_receipt = w3.eth.waitForTransactionReceipt(tx_3_hash)
    assert tx_3_receipt['status'] == 1
    # get L_Lend_token
    L_lend_token = get_ERC20_contract(address=CurrencyDao.token_addresses__l(Lend_token.address))
    # get F_Lend_token
    F_lend_token = get_MFT_contract(address=CurrencyDao.token_addresses__f(Lend_token.address))
    # get I_Lend_token
    I_lend_token = get_MFT_contract(address=CurrencyDao.token_addresses__i(Lend_token.address))
    # _lend_token_holder buys 1000 lend token from a 3rd party exchange
    tx_4_hash = Lend_token.transfer(_lend_token_holder, Web3.toWei(1000, 'ether'), transact={'from': Whale})
    tx_4_receipt = w3.eth.waitForTransactionReceipt(tx_4_hash)
    assert tx_4_receipt['status'] == 1
    # _lend_token_holder authorizes CurrencyDao to spend 800 Lend_token
    tx_5_hash = Lend_token.approve(CurrencyDao.address, Web3.toWei(800, 'ether'), transact={'from': _lend_token_holder})
    tx_5_receipt = w3.eth.waitForTransactionReceipt(tx_5_hash)
    assert tx_5_receipt['status'] == 1
    # _lend_token_holder wraps 800 Lend_token to L_lend_token
    assert L_lend_token.balanceOf(_lend_token_holder) == 0
    tx_6_hash = CurrencyDao.wrap(Lend_token.address, Web3.toWei(800, 'ether'), transact={'from': _lend_token_holder, 'gas': 145000})
    tx_6_receipt = w3.eth.waitForTransactionReceipt(tx_6_hash)
    assert tx_6_receipt['status'] == 1
    # _lend_token_holder splits 600 L_lend_tokens into 600 F_lend_tokens and 600 I_lend_tokens for Z19
    tx_7_hash = InterestPoolDao.split(Lend_token.address, Z19, Web3.toWei(600, 'ether'), transact={'from': _lend_token_holder, 'gas': 640000})
    tx_7_receipt = w3.eth.waitForTransactionReceipt(tx_7_hash)
    assert tx_7_receipt['status'] == 1
    _f_id = F_lend_token.id(Lend_token.address, Z19, ZERO_ADDRESS, 0)
    _i_id = I_lend_token.id(Lend_token.address, Z19, ZERO_ADDRESS, 0)
    assert L_lend_token.balanceOf(_lend_token_holder) == Web3.toWei(200, 'ether')
    _f_id = F_lend_token.id(Lend_token.address, Z19, ZERO_ADDRESS, 0)
    _i_id = I_lend_token.id(Lend_token.address, Z19, ZERO_ADDRESS, 0)
    assert F_lend_token.balanceOf(_lend_token_holder, _f_id) == Web3.toWei(600, 'ether')
    assert I_lend_token.balanceOf(_lend_token_holder, _i_id) == Web3.toWei(600, 'ether')
    # _lend_token_holder fuses 400 F_lend_tokens and 400 I_lend_tokens for Z19 into 400 L_lend_tokens
    tx_8_hash = InterestPoolDao.fuse(Lend_token.address, Z19, Web3.toWei(400, 'ether'), transact={'from': _lend_token_holder, 'gas': 150000})
    tx_8_receipt = w3.eth.waitForTransactionReceipt(tx_8_hash)
    assert tx_8_receipt['status'] == 1
    assert L_lend_token.balanceOf(_lend_token_holder) == Web3.toWei(600, 'ether')
    assert F_lend_token.balanceOf(_lend_token_holder, _f_id) == Web3.toWei(200, 'ether')
    assert I_lend_token.balanceOf(_lend_token_holder, _i_id) == Web3.toWei(200, 'ether')


# def test_failed_transaction_for_register_pool_call_for_non_supported_token(
#         w3, get_contract, get_logs,
#         LST_token, Lend_token, Malicious_token,
#         ERC20_library, ERC1155_library, CurrencyPool_library,
#         CurrencyDao, InterestPool_library, InterestPoolDao,
#         MarketDao
#     ):
#     owner = w3.eth.accounts[0]
#     # initialize CurrencyDao
#     tx_hash = CurrencyDao.initialize(
#         owner, LST_token.address, CurrencyPool_library.address,
#         ERC20_library.address, ERC1155_library.address,
#         MarketDao.address,
#         transact={'from': owner})
#     tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
#     assert tx_receipt['status'] == 1
#     # initialize InterestPoolDao
#     tx_hash = InterestPoolDao.initialize(
#         owner, LST_token.address, CurrencyDao.address,
#         InterestPool_library.address, ERC20_library.address,
#         transact={'from': owner})
#     tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
#     assert tx_receipt['status'] == 1
#     # set_offer_registration_fee_lookup()
#     tx_hash = InterestPoolDao.set_offer_registration_fee_lookup(100, 10, 2000,
#         1000, transact={'from': owner})
#     tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
#     assert tx_receipt['status'] == 1
#     # set_currency_support for Lend_token in CurrencyDao
#     tx_hash = CurrencyDao.set_currency_support(Lend_token.address, True,
#         transact={'from': owner, 'gas': 1570000})
#     tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
#     assert tx_receipt['status'] == 1
#     # register_pool for Lend_token
#     tx_hash = InterestPoolDao.register_pool(Malicious_token.address,
#         'Interest Pool A', 'IPA', 50, transact={'from': owner, 'gas': 1000000})
#     tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
#     assert tx_receipt['status'] == 0
#
#
# def test_register_pool(w3, get_contract, get_logs,
#         LST_token, Lend_token, Malicious_token,
#         ERC20_library, ERC1155_library, CurrencyPool_library,
#         CurrencyDao, InterestPool_library, InterestPoolDao,
#         MarketDao
#     ):
#     owner = w3.eth.accounts[0]
#     # initialize CurrencyDao
#     tx_1_hash = CurrencyDao.initialize(
#         owner, LST_token.address, CurrencyPool_library.address,
#         ERC20_library.address, ERC1155_library.address,
#         MarketDao.address,
#         transact={'from': owner})
#     tx_1_receipt = w3.eth.waitForTransactionReceipt(tx_1_hash)
#     assert tx_1_receipt['status'] == 1
#     # initialize InterestPoolDao
#     tx_2_hash = InterestPoolDao.initialize(
#         owner, LST_token.address, CurrencyDao.address,
#         InterestPool_library.address, ERC20_library.address,
#         transact={'from': owner})
#     tx_2_receipt = w3.eth.waitForTransactionReceipt(tx_2_hash)
#     assert tx_2_receipt['status'] == 1
#     # set_offer_registration_fee_lookup()
#     _minimum_fee = 100
#     _minimum_interval = 10
#     _fee_multiplier = 2000
#     _fee_multiplier_decimals = 1000
#     tx_3_hash = InterestPoolDao.set_offer_registration_fee_lookup(_minimum_fee,
#         _minimum_interval, _fee_multiplier, _fee_multiplier_decimals,
#         transact={'from': owner})
#     tx_3_receipt = w3.eth.waitForTransactionReceipt(tx_3_hash)
#     assert tx_3_receipt['status'] == 1
#     # set_currency_support for Lend_token in CurrencyDao
#     tx_4_hash = CurrencyDao.set_currency_support(Lend_token.address, True,
#         transact={'from': owner, 'gas': 1570000})
#     tx_4_receipt = w3.eth.waitForTransactionReceipt(tx_4_hash)
#     assert tx_4_receipt['status'] == 1
#     # register_pool for Lend_token
#     pool_owner = w3.eth.accounts[1]
#     tx_5_hash = InterestPoolDao.register_pool(Lend_token.address,
#         'Interest Pool A', 'IPA', 50,
#         transact={'from': pool_owner, 'gas': 800000})
#     tx_5_receipt = w3.eth.waitForTransactionReceipt(tx_5_hash)
#     assert tx_5_receipt['status'] == 1
#     # verify PoolRegistered log from InterestPoolDao
#     logs_5 = get_logs(tx_5_hash, InterestPoolDao, "PoolRegistered")
#     assert len(logs_5) == 1
#     assert logs_5[0].args._operator == pool_owner
#     assert logs_5[0].args._currency_address == Lend_token.address
#     _pool_hash = InterestPoolDao.pool_hash(Lend_token.address, logs_5[0].args._pool_address)
#     assert InterestPoolDao.pools__currency_address(_pool_hash) == Lend_token.address
#     assert InterestPoolDao.pools__pool_name(_pool_hash) == 'Interest Pool A'
#     assert InterestPoolDao.pools__pool_address(_pool_hash) == logs_5[0].args._pool_address
#     assert InterestPoolDao.pools__pool_operator(_pool_hash) == pool_owner
#     assert InterestPoolDao.pools__hash(_pool_hash) == _pool_hash
#     # verify InterestPool initialized
#     InterestPool = get_contract(
#         'contracts/templates/InterestPoolTemplate1.v.py',
#         interfaces=[
#             'ERC20', 'ERC1155', 'ERC1155TokenReceiver', 'InterestPoolDao'
#         ],
#         address=InterestPoolDao.pools__pool_address(_pool_hash)
#     )
#     assert InterestPool.owner() == InterestPoolDao.address
#     assert InterestPool.pool_hash() == _pool_hash
#     assert InterestPool.name() == 'Interest Pool A'
#     assert InterestPool.initial_exchange_rate() == 50
#     assert InterestPool.currency_address() == Lend_token.address
#     assert not InterestPool.pool_currency_address() in (None, ZERO_ADDRESS)
#     assert InterestPool.l_currency_address() == CurrencyDao.currencies__l_currency_address(Lend_token.address)
#     assert InterestPool.f_currency_address() == CurrencyDao.currencies__f_currency_address(Lend_token.address)
#     assert InterestPool.i_currency_address() == CurrencyDao.currencies__i_currency_address(Lend_token.address)
#     # verify Transfer log from InterestPool.pool_currency
#     InterestPoolCurrency = get_contract(
#         'contracts/templates/ERC20Template1.v.py',
#         address=InterestPool.pool_currency_address()
#     )
#     logs_5 = get_logs(tx_5_hash, InterestPoolCurrency, "Transfer")
#     assert len(logs_5) == 1
#     assert logs_5[0].args._from == ZERO_ADDRESS
#     assert logs_5[0].args._to == InterestPool.address
#     assert logs_5[0].args._value == 0
#
#
# def test_register_expiry(w3, get_contract, get_logs,
#         LST_token, Lend_token, Malicious_token,
#         ERC20_library, ERC1155_library, CurrencyPool_library,
#         CurrencyDao, InterestPool_library, InterestPoolDao,
#         MarketDao
#     ):
#     owner = w3.eth.accounts[0]
#     # initialize CurrencyDao
#     tx_1_hash = CurrencyDao.initialize(
#         owner, LST_token.address, CurrencyPool_library.address,
#         ERC20_library.address, ERC1155_library.address,
#         MarketDao.address,
#         transact={'from': owner})
#     tx_1_receipt = w3.eth.waitForTransactionReceipt(tx_1_hash)
#     assert tx_1_receipt['status'] == 1
#     # initialize InterestPoolDao
#     tx_2_hash = InterestPoolDao.initialize(
#         owner, LST_token.address, CurrencyDao.address,
#         InterestPool_library.address, ERC20_library.address,
#         transact={'from': owner})
#     tx_2_receipt = w3.eth.waitForTransactionReceipt(tx_2_hash)
#     assert tx_2_receipt['status'] == 1
#     # set_offer_registration_fee_lookup()
#     _minimum_fee = 100
#     _minimum_interval = 10
#     _fee_multiplier = 2000
#     _fee_multiplier_decimals = 1000
#     tx_3_hash = InterestPoolDao.set_offer_registration_fee_lookup(_minimum_fee,
#         _minimum_interval, _fee_multiplier, _fee_multiplier_decimals,
#         transact={'from': owner})
#     tx_3_receipt = w3.eth.waitForTransactionReceipt(tx_3_hash)
#     assert tx_3_receipt['status'] == 1
#     # set_currency_support for Lend_token in CurrencyDao
#     tx_4_hash = CurrencyDao.set_currency_support(Lend_token.address, True,
#         transact={'from': owner, 'gas': 1570000})
#     tx_4_receipt = w3.eth.waitForTransactionReceipt(tx_4_hash)
#     assert tx_4_receipt['status'] == 1
#     # register_pool for Lend_token
#     pool_owner = w3.eth.accounts[1]
#     tx_5_hash = InterestPoolDao.register_pool(Lend_token.address,
#         'Interest Pool A', 'IPA', 50,
#         transact={'from': pool_owner, 'gas': 800000})
#     tx_5_receipt = w3.eth.waitForTransactionReceipt(tx_5_hash)
#     assert tx_5_receipt['status'] == 1
#     # get InterestPool contract
#     logs_5 = get_logs(tx_5_hash, InterestPoolDao, "PoolRegistered")
#     _pool_hash = InterestPoolDao.pool_hash(Lend_token.address, logs_5[0].args._pool_address)
#     InterestPool = get_contract(
#         'contracts/templates/InterestPoolTemplate1.v.py',
#         interfaces=[
#             'ERC20', 'ERC1155', 'ERC1155TokenReceiver', 'InterestPoolDao'
#         ],
#         address=InterestPoolDao.pools__pool_address(_pool_hash)
#     )
#     # get InterestPoolCurrency
#     InterestPoolCurrency = get_contract(
#         'contracts/templates/ERC20Template1.v.py',
#         address=InterestPool.pool_currency_address()
#     )
#     # pool_owner buys LST from a 3rd party
#     assert LST_token.balanceOf(pool_owner) == 0
#     LST_token.transfer(pool_owner, 1000 * 10 ** 18, transact={'from': owner})
#     assert LST_token.balanceOf(pool_owner) == 1000 * 10 ** 18
#     # pool_owner authorizes CurrencyDao to spend LST required for offer_registration_fee
#     tx_6_hash = LST_token.approve(CurrencyDao.address, InterestPoolDao.offer_registration_fee() * (10 ** 18),
#         transact={'from': pool_owner})
#     tx_6_receipt = w3.eth.waitForTransactionReceipt(tx_6_hash)
#     assert tx_6_receipt['status'] == 1
#     # pool_owner registers an expiry : Last Thursday of December 2019, i.e., December 26th, 2019, i.e., Z19
#     assert InterestPool.expiries__expiry_timestamp(Z19) == 0
#     assert Web3.toHex(InterestPool.expiries__i_currency_hash(Z19)) == EMPTY_BYTES32
#     assert InterestPool.expiries__i_currency_id(Z19) == 0
#     assert Web3.toHex(InterestPool.expiries__f_currency_hash(Z19)) == EMPTY_BYTES32
#     assert InterestPool.expiries__f_currency_id(Z19) == 0
#     assert InterestPool.expiries__is_active(Z19) in (None, False)
#     tx_7_hash = InterestPool.register_expiry(Z19,
#         transact={'from': pool_owner, 'gas': 1100000})
#     tx_7_receipt = w3.eth.waitForTransactionReceipt(tx_7_hash)
#     assert tx_7_receipt['status'] == 1
#     assert InterestPool.expiries__expiry_timestamp(Z19) == 1577404799
#     assert InterestPoolDao.multi_fungible_currencies__token_id(Web3.toHex(InterestPool.expiries__i_currency_hash(Z19))) == InterestPool.expiries__i_currency_id(Z19)
#     assert InterestPoolDao.multi_fungible_currencies__token_id(Web3.toHex(InterestPool.expiries__f_currency_hash(Z19))) == InterestPool.expiries__f_currency_id(Z19)
#     assert InterestPool.expiries__is_active(Z19) == True
#
#
# def test_deposit_l_currency(w3, get_contract, get_logs,
#         LST_token, Lend_token, Malicious_token,
#         ERC20_library, ERC1155_library, CurrencyPool_library,
#         CurrencyDao, InterestPool_library, InterestPoolDao,
#         MarketDao
#     ):
#     owner = w3.eth.accounts[0]
#     # initialize CurrencyDao
#     tx_1_hash = CurrencyDao.initialize(
#         owner, LST_token.address, CurrencyPool_library.address,
#         ERC20_library.address, ERC1155_library.address,
#         MarketDao.address,
#         transact={'from': owner})
#     tx_1_receipt = w3.eth.waitForTransactionReceipt(tx_1_hash)
#     assert tx_1_receipt['status'] == 1
#     # initialize InterestPoolDao
#     tx_2_hash = InterestPoolDao.initialize(
#         owner, LST_token.address, CurrencyDao.address,
#         InterestPool_library.address, ERC20_library.address,
#         transact={'from': owner})
#     tx_2_receipt = w3.eth.waitForTransactionReceipt(tx_2_hash)
#     assert tx_2_receipt['status'] == 1
#     # set_currency_support for Lend_token in CurrencyDao
#     tx_3_hash = CurrencyDao.set_currency_support(Lend_token.address, True,
#         transact={'from': owner, 'gas': 1570000})
#     tx_3_receipt = w3.eth.waitForTransactionReceipt(tx_3_hash)
#     assert tx_3_receipt['status'] == 1
#     # register_pool for Lend_token
#     pool_owner = w3.eth.accounts[1]
#     tx_4_hash = InterestPoolDao.register_pool(Lend_token.address,
#         'Interest Pool A', 'IPA', 50,
#         transact={'from': pool_owner, 'gas': 800000})
#     tx_4_receipt = w3.eth.waitForTransactionReceipt(tx_4_hash)
#     assert tx_4_receipt['status'] == 1
#     # get InterestPool contract
#     logs_4 = get_logs(tx_4_hash, InterestPoolDao, "PoolRegistered")
#     _pool_hash = InterestPoolDao.pool_hash(Lend_token.address, logs_4[0].args._pool_address)
#     InterestPool = get_contract(
#         'contracts/templates/InterestPoolTemplate1.v.py',
#         interfaces=[
#             'ERC20', 'ERC1155', 'ERC1155TokenReceiver', 'InterestPoolDao'
#         ],
#         address=InterestPoolDao.pools__pool_address(_pool_hash)
#     )
#     # get InterestPoolCurrency
#     InterestPoolCurrency = get_contract(
#         'contracts/templates/ERC20Template1.v.py',
#         address=InterestPool.pool_currency_address()
#     )
#     # assign one of the accounts as a lender
#     lender = w3.eth.accounts[2]
#     # lender buys 1000 lend token from a 3rd party exchange
#     assert Lend_token.balanceOf(lender) == 0
#     Lend_token.transfer(lender, 1000 * 10 ** 18, transact={'from': owner})
#     assert Lend_token.balanceOf(lender) == 1000 * 10 ** 18
#     # lender authorizes CurrencyDao to spend 100 lend currency
#     tx_5_hash = Lend_token.approve(CurrencyDao.address, 100 * (10 ** 18),
#         transact={'from': lender})
#     tx_5_receipt = w3.eth.waitForTransactionReceipt(tx_5_hash)
#     assert tx_5_receipt['status'] == 1
#     # lender deposits Lend_token to Currency Pool and gets l_tokens
#     tx_6_hash = CurrencyDao.currency_to_l_currency(Lend_token.address, 100 * 10 ** 18,
#         transact={'from': lender, 'gas': 200000})
#     tx_6_receipt = w3.eth.waitForTransactionReceipt(tx_6_hash)
#     assert tx_6_receipt['status'] == 1
#     # verify lend currency balance of CurrencyDao
#     lend_token_balance = Lend_token.balanceOf(CurrencyDao.pools__pool_address(CurrencyDao.pool_hash(Lend_token.address)))
#     assert lend_token_balance == 100 * 10 ** 18
#     # verify lend currency balance of lender
#     lend_token_balance = Lend_token.balanceOf(lender)
#     assert lend_token_balance == (1000 - 100) * (10 ** 18)
#     # verify L_token balance of lender
#     L_token_address = CurrencyDao.currencies__l_currency_address(Lend_token.address)
#     L_token = get_contract(
#         'contracts/templates/ERC20Template1.v.py',
#         address=L_token_address
#     )
#     l_token_balance = L_token.balanceOf(lender)
#     assert l_token_balance == 100 * 10 ** 18
#     # verify lend currency balance of InterestPool
#     l_token_balance = InterestPool.l_currency_balance()
#     assert l_token_balance == 0
#     l_token_balance = InterestPool.total_l_currency_balance()
#     assert l_token_balance == 0
#     # lender purchases InterestPoolCurrency for 100 L_tokens
#     assert InterestPoolCurrency.totalSupply() == 0
#     estimated_InterestPoolCurrency_tokens = InterestPool.estimated_pool_tokens(100 * 10 ** 18)
#     assert estimated_InterestPoolCurrency_tokens == (50 * 100) * 10 ** 18
#     tx_7_hash = InterestPool.purchase_pool_currency(100 * 10 ** 18, transact={'from': lender})
#     tx_7_receipt = w3.eth.waitForTransactionReceipt(tx_7_hash)
#     assert tx_7_receipt['status'] == 1
#     # verify lend currency balance of InterestPool
#     l_token_balance = InterestPool.l_currency_balance()
#     assert l_token_balance == 100 * 10 ** 18
#     l_token_balance = InterestPool.total_l_currency_balance()
#     assert l_token_balance == 100 * 10 ** 18
#     # verify lend currency balance of lender
#     l_token_balance = L_token.balanceOf(lender)
#     assert l_token_balance == 0
#     # verify InterestPoolCurrency balance of lender
#     InterestPoolCurrency_balance = InterestPoolCurrency.balanceOf(lender)
#     assert InterestPoolCurrency_balance == estimated_InterestPoolCurrency_tokens
#     assert InterestPoolCurrency.totalSupply() == estimated_InterestPoolCurrency_tokens
#
#
