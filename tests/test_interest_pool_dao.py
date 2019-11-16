import os

import pytest

from web3 import Web3

from conftest import (ZERO_ADDRESS, EMPTY_BYTES32, Z19,
    _get_contract_from_address
)


"""
    The tests in this file use the following deployed contracts, aka
    fixtures from conftest:
    #. LST_token
    #. Lend_token
    #. Malicious_token
    #. ERC20_library
    #. ERC1155_library
    #. CurrencyPool_library
    #. CurrencyDao
    #. InterestPool_library
    #. InterestPoolDao
"""


def test_initialize(w3, get_logs,
        LST_token,
        ERC20_library, ERC1155_library,
        CurrencyPool_library, CurrencyDao,
        InterestPool_library, InterestPoolDao
    ):
    owner = w3.eth.accounts[0]
    # initialize CurrencyDao
    tx_hash = CurrencyDao.initialize(
        owner, LST_token.address, CurrencyPool_library.address,
        ERC20_library.address, ERC1155_library.address,
        transact={'from': owner})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    # initialize InterestPoolDao
    assert InterestPoolDao.initialized() == False
    assert InterestPoolDao.owner() in (None, ZERO_ADDRESS)
    assert InterestPoolDao.protocol_dao_address() in (None, ZERO_ADDRESS)
    assert InterestPoolDao.protocol_currency_address() in (None, ZERO_ADDRESS)
    assert InterestPoolDao.DAO_TYPE_CURRENCY() == 0
    assert InterestPoolDao.TEMPLATE_TYPE_INTEREST_POOL() == 0
    assert InterestPoolDao.TEMPLATE_TYPE_CURRENCY_ERC20() == 0
    tx_hash = InterestPoolDao.initialize(
        owner, LST_token.address, CurrencyDao.address,
        InterestPool_library.address, ERC20_library.address,
        transact={'from': owner})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    assert InterestPoolDao.initialized() == True
    assert InterestPoolDao.owner() == owner
    assert InterestPoolDao.protocol_dao_address() == owner
    assert InterestPoolDao.protocol_currency_address() == LST_token.address
    assert InterestPoolDao.DAO_TYPE_CURRENCY() == 1
    assert InterestPoolDao.TEMPLATE_TYPE_INTEREST_POOL() == 1
    assert InterestPoolDao.TEMPLATE_TYPE_CURRENCY_ERC20() == 2
    assert InterestPoolDao.templates(1) == InterestPool_library.address
    assert InterestPoolDao.templates(2) == ERC20_library.address


def test_set_offer_registration_fee_lookup(w3, get_logs,
        LST_token,
        ERC20_library, ERC1155_library,
        CurrencyPool_library, CurrencyDao,
        InterestPool_library, InterestPoolDao
    ):
    owner = w3.eth.accounts[0]
    # initialize CurrencyDao
    tx_hash = CurrencyDao.initialize(
        owner, LST_token.address, CurrencyPool_library.address,
        ERC20_library.address, ERC1155_library.address,
        transact={'from': owner})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    # initialize InterestPoolDao
    tx_hash = InterestPoolDao.initialize(
        owner, LST_token.address, CurrencyDao.address,
        InterestPool_library.address, ERC20_library.address,
        transact={'from': owner})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    assert InterestPoolDao.offer_registration_fee_lookup__minimum_fee(InterestPoolDao.address) == 0
    assert InterestPoolDao.offer_registration_fee_lookup__minimum_interval(InterestPoolDao.address) == 0
    assert InterestPoolDao.offer_registration_fee_lookup__fee_multiplier(InterestPoolDao.address) == 0
    assert InterestPoolDao.offer_registration_fee_lookup__fee_multiplier_decimals(InterestPoolDao.address) == 0
    assert InterestPoolDao.offer_registration_fee_lookup__last_registered_at(InterestPoolDao.address) == 0
    assert InterestPoolDao.offer_registration_fee_lookup__last_paid_fee(InterestPoolDao.address) == 0
    # set_offer_registration_fee_lookup()
    _minimum_fee = 100
    _minimum_interval = 10
    _fee_multiplier = 2000
    _fee_multiplier_decimals = 1000
    tx_hash = InterestPoolDao.set_offer_registration_fee_lookup(_minimum_fee,
        _minimum_interval, _fee_multiplier, _fee_multiplier_decimals,
        transact={'from': owner})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    assert InterestPoolDao.offer_registration_fee_lookup__minimum_fee(InterestPoolDao.address) == _minimum_fee
    assert InterestPoolDao.offer_registration_fee_lookup__minimum_interval(InterestPoolDao.address) == _minimum_interval
    assert InterestPoolDao.offer_registration_fee_lookup__fee_multiplier(InterestPoolDao.address) == _fee_multiplier
    assert InterestPoolDao.offer_registration_fee_lookup__fee_multiplier_decimals(InterestPoolDao.address) == _fee_multiplier_decimals
    assert InterestPoolDao.offer_registration_fee_lookup__last_registered_at(InterestPoolDao.address) == 0
    assert InterestPoolDao.offer_registration_fee_lookup__last_paid_fee(InterestPoolDao.address) == 0
    assert InterestPoolDao.offer_registration_fee() == _minimum_fee


def test_failed_transaction_for_register_pool_call_for_non_supported_token(
        w3, get_logs,
        LST_token, Lend_token, Malicious_token,
        ERC20_library, ERC1155_library, CurrencyPool_library,
        CurrencyDao, InterestPool_library, InterestPoolDao
    ):
    owner = w3.eth.accounts[0]
    # initialize CurrencyDao
    tx_hash = CurrencyDao.initialize(
        owner, LST_token.address, CurrencyPool_library.address,
        ERC20_library.address, ERC1155_library.address,
        transact={'from': owner})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    # initialize InterestPoolDao
    tx_hash = InterestPoolDao.initialize(
        owner, LST_token.address, CurrencyDao.address,
        InterestPool_library.address, ERC20_library.address,
        transact={'from': owner})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    # set_offer_registration_fee_lookup()
    tx_hash = InterestPoolDao.set_offer_registration_fee_lookup(100, 10, 2000,
        1000, transact={'from': owner})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    # set_currency_support for Lend_token in CurrencyDao
    tx_hash = CurrencyDao.set_currency_support(Lend_token.address, True,
        transact={'from': owner, 'gas': 1570000})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    # register_pool for Lend_token
    tx_hash = InterestPoolDao.register_pool(Malicious_token.address,
        'Interest Pool A', 'IPA', 50, transact={'from': owner, 'gas': 1000000})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 0


def test_register_pool(w3, get_logs,
        LST_token, Lend_token, Malicious_token,
        ERC20_library, ERC1155_library, CurrencyPool_library,
        CurrencyDao, InterestPool_library, InterestPoolDao
    ):
    owner = w3.eth.accounts[0]
    # initialize CurrencyDao
    tx_1_hash = CurrencyDao.initialize(
        owner, LST_token.address, CurrencyPool_library.address,
        ERC20_library.address, ERC1155_library.address,
        transact={'from': owner})
    tx_1_receipt = w3.eth.waitForTransactionReceipt(tx_1_hash)
    assert tx_1_receipt['status'] == 1
    # initialize InterestPoolDao
    tx_2_hash = InterestPoolDao.initialize(
        owner, LST_token.address, CurrencyDao.address,
        InterestPool_library.address, ERC20_library.address,
        transact={'from': owner})
    tx_2_receipt = w3.eth.waitForTransactionReceipt(tx_2_hash)
    assert tx_2_receipt['status'] == 1
    # set_offer_registration_fee_lookup()
    _minimum_fee = 100
    _minimum_interval = 10
    _fee_multiplier = 2000
    _fee_multiplier_decimals = 1000
    tx_3_hash = InterestPoolDao.set_offer_registration_fee_lookup(_minimum_fee,
        _minimum_interval, _fee_multiplier, _fee_multiplier_decimals,
        transact={'from': owner})
    tx_3_receipt = w3.eth.waitForTransactionReceipt(tx_3_hash)
    assert tx_3_receipt['status'] == 1
    # set_currency_support for Lend_token in CurrencyDao
    tx_4_hash = CurrencyDao.set_currency_support(Lend_token.address, True,
        transact={'from': owner, 'gas': 1570000})
    tx_4_receipt = w3.eth.waitForTransactionReceipt(tx_4_hash)
    assert tx_4_receipt['status'] == 1
    # register_pool for Lend_token
    pool_owner = w3.eth.accounts[1]
    tx_5_hash = InterestPoolDao.register_pool(Lend_token.address,
        'Interest Pool A', 'IPA', 50,
        transact={'from': pool_owner, 'gas': 775000})
    tx_5_receipt = w3.eth.waitForTransactionReceipt(tx_5_hash)
    assert tx_5_receipt['status'] == 1
    # verify PoolRegistered log from InterestPoolDao
    logs_5 = get_logs(tx_5_hash, InterestPoolDao, "PoolRegistered")
    assert len(logs_5) == 1
    assert logs_5[0].args._operator == pool_owner
    assert logs_5[0].args._currency_address == Lend_token.address
    _pool_hash = InterestPoolDao.pool_hash(Lend_token.address, logs_5[0].args._pool_address)
    assert InterestPoolDao.pools__currency_address(_pool_hash) == Lend_token.address
    assert InterestPoolDao.pools__pool_name(_pool_hash) == 'Interest Pool A'
    assert InterestPoolDao.pools__pool_address(_pool_hash) == logs_5[0].args._pool_address
    assert InterestPoolDao.pools__pool_operator(_pool_hash) == pool_owner
    assert InterestPoolDao.pools__hash(_pool_hash) == _pool_hash
    # verify InterestPool initialized
    interest_pool_interface_codes = {}
    with open(os.path.join(os.path.dirname(os.path.realpath(__file__)),
        os.pardir, 'contracts/interfaces/ERC20.vy')) as f:
            interest_pool_interface_codes['ERC20'] = {
                'type': 'vyper',
                'code': f.read()
            }
    with open(os.path.join(os.path.dirname(os.path.realpath(__file__)),
        os.pardir, 'contracts/interfaces/ERC1155.vy')) as f:
            interest_pool_interface_codes['ERC1155'] = {
                'type': 'vyper',
                'code': f.read()
            }
    with open(os.path.join(os.path.dirname(os.path.realpath(__file__)),
        os.pardir, 'contracts/interfaces/ERC1155TokenReceiver.vy')) as f:
            interest_pool_interface_codes['ERC1155TokenReceiver'] = {
                'type': 'vyper',
                'code': f.read()
            }
    with open(os.path.join(os.path.dirname(os.path.realpath(__file__)),
        os.pardir, 'contracts/interfaces/InterestPoolDao.vy')) as f:
            interest_pool_interface_codes['InterestPoolDao'] = {
                'type': 'vyper',
                'code': f.read()
            }
    InterestPool = _get_contract_from_address(w3,
        InterestPoolDao.pools__pool_address(_pool_hash),
        'contracts/templates/InterestPoolTemplate1.v.py',
        interface_codes=interest_pool_interface_codes)
    assert InterestPool.owner() == InterestPoolDao.address
    assert InterestPool.pool_hash() == _pool_hash
    assert InterestPool.name() == 'Interest Pool A'
    assert InterestPool.initial_exchange_rate() == 50
    assert InterestPool.currency_address() == Lend_token.address
    assert not InterestPool.pool_currency_address() in (None, ZERO_ADDRESS)
    assert InterestPool.l_currency_address() == CurrencyDao.currencies__l_currency_address(Lend_token.address)
    assert InterestPool.f_currency_address() == CurrencyDao.currencies__f_currency_address(Lend_token.address)
    assert InterestPool.i_currency_address() == CurrencyDao.currencies__i_currency_address(Lend_token.address)
    # verify Transfer log from InterestPool.pool_currency
    InterestPoolCurrency = _get_contract_from_address(w3,
        InterestPool.pool_currency_address(),
        'contracts/templates/ERC20Template1.v.py')
    logs_5 = get_logs(tx_5_hash, InterestPoolCurrency, "Transfer")
    assert len(logs_5) == 1
    assert logs_5[0].args._from == ZERO_ADDRESS
    assert logs_5[0].args._to == InterestPool.address
    assert logs_5[0].args._value == 0


def test_register_expiry(w3, get_logs,
        LST_token, Lend_token, Malicious_token,
        ERC20_library, ERC1155_library, CurrencyPool_library,
        CurrencyDao, InterestPool_library, InterestPoolDao
    ):
    owner = w3.eth.accounts[0]
    # initialize CurrencyDao
    tx_1_hash = CurrencyDao.initialize(
        owner, LST_token.address, CurrencyPool_library.address,
        ERC20_library.address, ERC1155_library.address,
        transact={'from': owner})
    tx_1_receipt = w3.eth.waitForTransactionReceipt(tx_1_hash)
    assert tx_1_receipt['status'] == 1
    # initialize InterestPoolDao
    tx_2_hash = InterestPoolDao.initialize(
        owner, LST_token.address, CurrencyDao.address,
        InterestPool_library.address, ERC20_library.address,
        transact={'from': owner})
    tx_2_receipt = w3.eth.waitForTransactionReceipt(tx_2_hash)
    assert tx_2_receipt['status'] == 1
    # set_offer_registration_fee_lookup()
    _minimum_fee = 100
    _minimum_interval = 10
    _fee_multiplier = 2000
    _fee_multiplier_decimals = 1000
    tx_3_hash = InterestPoolDao.set_offer_registration_fee_lookup(_minimum_fee,
        _minimum_interval, _fee_multiplier, _fee_multiplier_decimals,
        transact={'from': owner})
    tx_3_receipt = w3.eth.waitForTransactionReceipt(tx_3_hash)
    assert tx_3_receipt['status'] == 1
    # set_currency_support for Lend_token in CurrencyDao
    tx_4_hash = CurrencyDao.set_currency_support(Lend_token.address, True,
        transact={'from': owner, 'gas': 1570000})
    tx_4_receipt = w3.eth.waitForTransactionReceipt(tx_4_hash)
    assert tx_4_receipt['status'] == 1
    # register_pool for Lend_token
    pool_owner = w3.eth.accounts[1]
    tx_5_hash = InterestPoolDao.register_pool(Lend_token.address,
        'Interest Pool A', 'IPA', 50,
        transact={'from': pool_owner, 'gas': 775000})
    tx_5_receipt = w3.eth.waitForTransactionReceipt(tx_5_hash)
    assert tx_5_receipt['status'] == 1
    # get InterestPool contract
    logs_5 = get_logs(tx_5_hash, InterestPoolDao, "PoolRegistered")
    _pool_hash = InterestPoolDao.pool_hash(Lend_token.address, logs_5[0].args._pool_address)
    interest_pool_interface_codes = {}
    with open(os.path.join(os.path.dirname(os.path.realpath(__file__)),
        os.pardir, 'contracts/interfaces/ERC20.vy')) as f:
            interest_pool_interface_codes['ERC20'] = {
                'type': 'vyper',
                'code': f.read()
            }
    with open(os.path.join(os.path.dirname(os.path.realpath(__file__)),
        os.pardir, 'contracts/interfaces/ERC1155.vy')) as f:
            interest_pool_interface_codes['ERC1155'] = {
                'type': 'vyper',
                'code': f.read()
            }
    with open(os.path.join(os.path.dirname(os.path.realpath(__file__)),
        os.pardir, 'contracts/interfaces/ERC1155TokenReceiver.vy')) as f:
            interest_pool_interface_codes['ERC1155TokenReceiver'] = {
                'type': 'vyper',
                'code': f.read()
            }
    with open(os.path.join(os.path.dirname(os.path.realpath(__file__)),
        os.pardir, 'contracts/interfaces/InterestPoolDao.vy')) as f:
            interest_pool_interface_codes['InterestPoolDao'] = {
                'type': 'vyper',
                'code': f.read()
            }
    InterestPool = _get_contract_from_address(w3,
        InterestPoolDao.pools__pool_address(_pool_hash),
        'contracts/templates/InterestPoolTemplate1.v.py',
        interface_codes=interest_pool_interface_codes)
    # get InterestPoolCurrency
    InterestPoolCurrency = _get_contract_from_address(w3,
        InterestPool.pool_currency_address(),
        'contracts/templates/ERC20Template1.v.py')
    # pool_owner buys LST from a 3rd party
    assert LST_token.balanceOf(pool_owner) == 0
    LST_token.transfer(pool_owner, 1000 * 10 ** 18, transact={'from': owner})
    assert LST_token.balanceOf(pool_owner) == 1000 * 10 ** 18
    # pool_owner authorizes CurrencyDao to spend LST required for offer_registration_fee
    tx_6_hash = LST_token.approve(CurrencyDao.address, InterestPoolDao.offer_registration_fee() * (10 ** 18),
        transact={'from': pool_owner})
    tx_6_receipt = w3.eth.waitForTransactionReceipt(tx_6_hash)
    assert tx_6_receipt['status'] == 1
    # pool_owner registers an expiry : Last Thursday of December 2019, i.e., December 26th, 2019, i.e., Z19
    assert InterestPool.expiries__expiry_timestamp(Z19) == 0
    assert Web3.toHex(InterestPool.expiries__i_currency_hash(Z19)) == EMPTY_BYTES32
    assert InterestPool.expiries__i_currency_id(Z19) == 0
    assert Web3.toHex(InterestPool.expiries__f_currency_hash(Z19)) == EMPTY_BYTES32
    assert InterestPool.expiries__f_currency_id(Z19) == 0
    assert InterestPool.expiries__is_active(Z19) in (None, False)
    tx_7_hash = InterestPool.register_expiry(Z19,
        transact={'from': pool_owner, 'gas': 710000})
    tx_7_receipt = w3.eth.waitForTransactionReceipt(tx_7_hash)
    print('\n\n tx_7_receipt : {0}'.format(tx_7_receipt))
    assert tx_7_receipt['status'] == 1
    assert InterestPool.expiries__expiry_timestamp(Z19) == 1577404799
    assert InterestPoolDao.multi_fungible_currencies__token_id(Web3.toHex(InterestPool.expiries__i_currency_hash(Z19))) == InterestPool.expiries__i_currency_id(Z19)
    assert InterestPoolDao.multi_fungible_currencies__token_id(Web3.toHex(InterestPool.expiries__f_currency_hash(Z19))) == InterestPool.expiries__f_currency_id(Z19)
    assert InterestPool.expiries__is_active(Z19) == True


def test_deposit_l_currency(w3, get_logs,
        LST_token, Lend_token, Malicious_token,
        ERC20_library, ERC1155_library, CurrencyPool_library,
        CurrencyDao, InterestPool_library, InterestPoolDao
    ):
    owner = w3.eth.accounts[0]
    # initialize CurrencyDao
    tx_1_hash = CurrencyDao.initialize(
        owner, LST_token.address, CurrencyPool_library.address,
        ERC20_library.address, ERC1155_library.address,
        transact={'from': owner})
    tx_1_receipt = w3.eth.waitForTransactionReceipt(tx_1_hash)
    assert tx_1_receipt['status'] == 1
    # initialize InterestPoolDao
    tx_2_hash = InterestPoolDao.initialize(
        owner, LST_token.address, CurrencyDao.address,
        InterestPool_library.address, ERC20_library.address,
        transact={'from': owner})
    tx_2_receipt = w3.eth.waitForTransactionReceipt(tx_2_hash)
    assert tx_2_receipt['status'] == 1
    # set_currency_support for Lend_token in CurrencyDao
    tx_3_hash = CurrencyDao.set_currency_support(Lend_token.address, True,
        transact={'from': owner, 'gas': 1570000})
    tx_3_receipt = w3.eth.waitForTransactionReceipt(tx_3_hash)
    assert tx_3_receipt['status'] == 1
    # register_pool for Lend_token
    pool_owner = w3.eth.accounts[1]
    tx_4_hash = InterestPoolDao.register_pool(Lend_token.address,
        'Interest Pool A', 'IPA', 50,
        transact={'from': pool_owner, 'gas': 775000})
    tx_4_receipt = w3.eth.waitForTransactionReceipt(tx_4_hash)
    assert tx_4_receipt['status'] == 1
    # get InterestPool contract
    logs_4 = get_logs(tx_4_hash, InterestPoolDao, "PoolRegistered")
    _pool_hash = InterestPoolDao.pool_hash(Lend_token.address, logs_4[0].args._pool_address)
    interest_pool_interface_codes = {}
    with open(os.path.join(os.path.dirname(os.path.realpath(__file__)),
        os.pardir, 'contracts/interfaces/ERC20.vy')) as f:
            interest_pool_interface_codes['ERC20'] = {
                'type': 'vyper',
                'code': f.read()
            }
    with open(os.path.join(os.path.dirname(os.path.realpath(__file__)),
        os.pardir, 'contracts/interfaces/ERC1155.vy')) as f:
            interest_pool_interface_codes['ERC1155'] = {
                'type': 'vyper',
                'code': f.read()
            }
    with open(os.path.join(os.path.dirname(os.path.realpath(__file__)),
        os.pardir, 'contracts/interfaces/ERC1155TokenReceiver.vy')) as f:
            interest_pool_interface_codes['ERC1155TokenReceiver'] = {
                'type': 'vyper',
                'code': f.read()
            }
    with open(os.path.join(os.path.dirname(os.path.realpath(__file__)),
        os.pardir, 'contracts/interfaces/InterestPoolDao.vy')) as f:
            interest_pool_interface_codes['InterestPoolDao'] = {
                'type': 'vyper',
                'code': f.read()
            }
    InterestPool = _get_contract_from_address(w3,
        InterestPoolDao.pools__pool_address(_pool_hash),
        'contracts/templates/InterestPoolTemplate1.v.py',
        interface_codes=interest_pool_interface_codes)
    # get InterestPoolCurrency
    InterestPoolCurrency = _get_contract_from_address(w3,
        InterestPool.pool_currency_address(),
        'contracts/templates/ERC20Template1.v.py')
    # assign one of the accounts as a lender
    lender = w3.eth.accounts[2]
    # lender buys 1000 lend token from a 3rd party exchange
    assert Lend_token.balanceOf(lender) == 0
    Lend_token.transfer(lender, 1000 * 10 ** 18, transact={'from': owner})
    assert Lend_token.balanceOf(lender) == 1000 * 10 ** 18
    # lender authorizes CurrencyDao to spend 100 lend currency
    tx_5_hash = Lend_token.approve(CurrencyDao.address, 100 * (10 ** 18),
        transact={'from': lender})
    tx_5_receipt = w3.eth.waitForTransactionReceipt(tx_5_hash)
    assert tx_5_receipt['status'] == 1
    # lender deposits Lend_token to Currency Pool and gets l_tokens
    tx_6_hash = CurrencyDao.currency_to_l_currency(Lend_token.address, 100 * 10 ** 18,
        transact={'from': lender, 'gas': 200000})
    tx_6_receipt = w3.eth.waitForTransactionReceipt(tx_6_hash)
    assert tx_6_receipt['status'] == 1
    # verify lend currency balance of CurrencyDao
    lend_token_balance = Lend_token.balanceOf(CurrencyDao.pools__pool_address(CurrencyDao.pool_hash(Lend_token.address)))
    assert lend_token_balance == 100 * 10 ** 18
    # verify lend currency balance of lender
    lend_token_balance = Lend_token.balanceOf(lender)
    assert lend_token_balance == (1000 - 100) * (10 ** 18)
    # verify L_token balance of lender
    L_token_address = CurrencyDao.currencies__l_currency_address(Lend_token.address)
    L_token = _get_contract_from_address(w3, L_token_address, 'contracts/templates/ERC20Template1.v.py')
    l_token_balance = L_token.balanceOf(lender)
    assert l_token_balance == 100 * 10 ** 18
    # verify lend currency balance of InterestPool
    l_token_balance = InterestPool.l_currency_balance()
    assert l_token_balance == 0
    l_token_balance = InterestPool.total_l_currency_balance()
    assert l_token_balance == 0
    # lender purchases InterestPoolCurrency for 100 L_tokens
    assert InterestPoolCurrency.totalSupply() == 0
    estimated_InterestPoolCurrency_tokens = InterestPool.estimated_pool_tokens(100 * 10 ** 18)
    assert estimated_InterestPoolCurrency_tokens == (50 * 100) * 10 ** 18
    tx_7_hash = InterestPool.purchase_pool_currency(100 * 10 ** 18, transact={'from': lender})
    tx_7_receipt = w3.eth.waitForTransactionReceipt(tx_7_hash)
    assert tx_7_receipt['status'] == 1
    # verify lend currency balance of InterestPool
    l_token_balance = InterestPool.l_currency_balance()
    assert l_token_balance == 100 * 10 ** 18
    l_token_balance = InterestPool.total_l_currency_balance()
    assert l_token_balance == 100 * 10 ** 18
    # verify lend currency balance of lender
    l_token_balance = L_token.balanceOf(lender)
    assert l_token_balance == 0
    # verify InterestPoolCurrency balance of lender
    InterestPoolCurrency_balance = InterestPoolCurrency.balanceOf(lender)
    assert InterestPoolCurrency_balance == estimated_InterestPoolCurrency_tokens
    assert InterestPoolCurrency.totalSupply() == estimated_InterestPoolCurrency_tokens


def test_l_currency_to_i_and_f_currency(w3, get_logs,
        LST_token, Lend_token, Malicious_token,
        ERC20_library, ERC1155_library, CurrencyPool_library,
        CurrencyDao, InterestPool_library, InterestPoolDao
    ):
    owner = w3.eth.accounts[0]
    # initialize CurrencyDao
    tx_1_hash = CurrencyDao.initialize(
        owner, LST_token.address, CurrencyPool_library.address,
        ERC20_library.address, ERC1155_library.address,
        transact={'from': owner})
    tx_1_receipt = w3.eth.waitForTransactionReceipt(tx_1_hash)
    assert tx_1_receipt['status'] == 1
    # initialize InterestPoolDao
    tx_2_hash = InterestPoolDao.initialize(
        owner, LST_token.address, CurrencyDao.address,
        InterestPool_library.address, ERC20_library.address,
        transact={'from': owner})
    tx_2_receipt = w3.eth.waitForTransactionReceipt(tx_2_hash)
    assert tx_2_receipt['status'] == 1
    # set_offer_registration_fee_lookup()
    _minimum_fee = 100
    _minimum_interval = 10
    _fee_multiplier = 2000
    _fee_multiplier_decimals = 1000
    tx_3_hash = InterestPoolDao.set_offer_registration_fee_lookup(_minimum_fee,
        _minimum_interval, _fee_multiplier, _fee_multiplier_decimals,
        transact={'from': owner})
    tx_3_receipt = w3.eth.waitForTransactionReceipt(tx_3_hash)
    assert tx_3_receipt['status'] == 1
    # set_currency_support for Lend_token in CurrencyDao
    tx_4_hash = CurrencyDao.set_currency_support(Lend_token.address, True,
        transact={'from': owner, 'gas': 1570000})
    tx_4_receipt = w3.eth.waitForTransactionReceipt(tx_4_hash)
    assert tx_4_receipt['status'] == 1
    # register_pool for Lend_token
    pool_owner = w3.eth.accounts[1]
    tx_5_hash = InterestPoolDao.register_pool(Lend_token.address,
        'Interest Pool A', 'IPA', 50,
        transact={'from': pool_owner, 'gas': 775000})
    tx_5_receipt = w3.eth.waitForTransactionReceipt(tx_5_hash)
    assert tx_5_receipt['status'] == 1
    # get InterestPool contract
    logs_5 = get_logs(tx_5_hash, InterestPoolDao, "PoolRegistered")
    _pool_hash = InterestPoolDao.pool_hash(Lend_token.address, logs_5[0].args._pool_address)
    interest_pool_interface_codes = {}
    with open(os.path.join(os.path.dirname(os.path.realpath(__file__)),
        os.pardir, 'contracts/interfaces/ERC20.vy')) as f:
            interest_pool_interface_codes['ERC20'] = {
                'type': 'vyper',
                'code': f.read()
            }
    with open(os.path.join(os.path.dirname(os.path.realpath(__file__)),
        os.pardir, 'contracts/interfaces/ERC1155.vy')) as f:
            interest_pool_interface_codes['ERC1155'] = {
                'type': 'vyper',
                'code': f.read()
            }
    with open(os.path.join(os.path.dirname(os.path.realpath(__file__)),
        os.pardir, 'contracts/interfaces/ERC1155TokenReceiver.vy')) as f:
            interest_pool_interface_codes['ERC1155TokenReceiver'] = {
                'type': 'vyper',
                'code': f.read()
            }
    with open(os.path.join(os.path.dirname(os.path.realpath(__file__)),
        os.pardir, 'contracts/interfaces/InterestPoolDao.vy')) as f:
            interest_pool_interface_codes['InterestPoolDao'] = {
                'type': 'vyper',
                'code': f.read()
            }
    InterestPool = _get_contract_from_address(w3,
        InterestPoolDao.pools__pool_address(_pool_hash),
        'contracts/templates/InterestPoolTemplate1.v.py',
        interface_codes=interest_pool_interface_codes)
    # get InterestPoolCurrency
    InterestPoolCurrency = _get_contract_from_address(w3,
        InterestPool.pool_currency_address(),
        'contracts/templates/ERC20Template1.v.py')
    # pool_owner buys LST from a 3rd party
    LST_token.transfer(pool_owner, 1000 * 10 ** 18, transact={'from': owner})
    # pool_owner authorizes CurrencyDao to spend LST required for offer_registration_fee
    tx_6_hash = LST_token.approve(CurrencyDao.address, InterestPoolDao.offer_registration_fee() * (10 ** 18),
        transact={'from': pool_owner})
    tx_6_receipt = w3.eth.waitForTransactionReceipt(tx_6_hash)
    assert tx_6_receipt['status'] == 1
    # pool_owner registers an expiry : Last Thursday of December 2019, i.e., December 26th, 2019, i.e., Z19
    tx_7_hash = InterestPool.register_expiry(Z19,
        transact={'from': pool_owner, 'gas': 710000})
    tx_7_receipt = w3.eth.waitForTransactionReceipt(tx_7_hash)
    # get L_token
    L_token_address = CurrencyDao.currencies__l_currency_address(Lend_token.address)
    L_token = _get_contract_from_address(w3, L_token_address, 'contracts/templates/ERC20Template1.v.py')
    # assign one of the accounts as a lender
    lender = w3.eth.accounts[2]
    # lender buys 1000 lend token from a 3rd party exchange
    tx_8_hash = Lend_token.transfer(lender, 1000 * 10 ** 18, transact={'from': owner})
    tx_8_receipt = w3.eth.waitForTransactionReceipt(tx_8_hash)
    assert tx_8_receipt['status'] == 1
    # lender authorizes CurrencyDao to spend 100 lend currency
    tx_9_hash = Lend_token.approve(CurrencyDao.address, 100 * (10 ** 18),
        transact={'from': lender})
    tx_9_receipt = w3.eth.waitForTransactionReceipt(tx_9_hash)
    assert tx_9_receipt['status'] == 1
    # lender deposits Lend_token to Currency Pool and gets l_tokens
    tx_10_hash = CurrencyDao.currency_to_l_currency(Lend_token.address, 100 * 10 ** 18,
        transact={'from': lender, 'gas': 200000})
    tx_10_receipt = w3.eth.waitForTransactionReceipt(tx_10_hash)
    assert tx_10_receipt['status'] == 1
    # lender purchases InterestPoolCurrency for 100 L_tokens
    # lender gets 5000 InterestPoolCurrency tokens
    # 100 L_tokens are deposited into InterestPool account
    tx_11_hash = InterestPool.purchase_pool_currency(100 * 10 ** 18, transact={'from': lender})
    tx_11_receipt = w3.eth.waitForTransactionReceipt(tx_11_hash)
    assert tx_11_receipt['status'] == 1
    # pool_owner initiates offer of 20 I_tokens from the InterestPool
    # 20 L_tokens burned from InterestPool account
    # 20 I_tokens and 20 F_tokens deposited to InterestPool account
    tx_12_hash = InterestPool.increment_i_currency_supply(Z19, 20 * 10 ** 18, transact={'from': pool_owner, 'gas': 500000})
    tx_12_receipt = w3.eth.waitForTransactionReceipt(tx_12_hash)
    print('\n\n tx_12_receipt : {0}'.format(tx_12_receipt))
    assert tx_12_receipt['status'] == 1
    # verify multi_fungible_currencies balances of InterestPool
    assert InterestPool.i_currency_balance(Z19) == 20 * 10 ** 18
    assert InterestPool.f_currency_balance(Z19) == 20 * 10 ** 18
    assert InterestPool.total_f_currency_balance() == 20 * 10 ** 18
    assert InterestPool.l_currency_balance() == (100 - 20) * 10 ** 18
    assert InterestPool.total_l_currency_balance() == 100 * 10 ** 18


def test_l_currency_from_i_and_f_currency(w3, get_logs,
        LST_token, Lend_token, Malicious_token,
        ERC20_library, ERC1155_library, CurrencyPool_library,
        CurrencyDao, InterestPool_library, InterestPoolDao
    ):
    owner = w3.eth.accounts[0]
    # initialize CurrencyDao
    tx_1_hash = CurrencyDao.initialize(
        owner, LST_token.address, CurrencyPool_library.address,
        ERC20_library.address, ERC1155_library.address,
        transact={'from': owner})
    tx_1_receipt = w3.eth.waitForTransactionReceipt(tx_1_hash)
    assert tx_1_receipt['status'] == 1
    # initialize InterestPoolDao
    tx_2_hash = InterestPoolDao.initialize(
        owner, LST_token.address, CurrencyDao.address,
        InterestPool_library.address, ERC20_library.address,
        transact={'from': owner})
    tx_2_receipt = w3.eth.waitForTransactionReceipt(tx_2_hash)
    assert tx_2_receipt['status'] == 1
    # set_offer_registration_fee_lookup()
    _minimum_fee = 100
    _minimum_interval = 10
    _fee_multiplier = 2000
    _fee_multiplier_decimals = 1000
    tx_3_hash = InterestPoolDao.set_offer_registration_fee_lookup(_minimum_fee,
        _minimum_interval, _fee_multiplier, _fee_multiplier_decimals,
        transact={'from': owner})
    tx_3_receipt = w3.eth.waitForTransactionReceipt(tx_3_hash)
    assert tx_3_receipt['status'] == 1
    # set_currency_support for Lend_token in CurrencyDao
    tx_4_hash = CurrencyDao.set_currency_support(Lend_token.address, True,
        transact={'from': owner, 'gas': 1570000})
    tx_4_receipt = w3.eth.waitForTransactionReceipt(tx_4_hash)
    assert tx_4_receipt['status'] == 1
    # register_pool for Lend_token
    pool_owner = w3.eth.accounts[1]
    tx_5_hash = InterestPoolDao.register_pool(Lend_token.address,
        'Interest Pool A', 'IPA', 50,
        transact={'from': pool_owner, 'gas': 775000})
    tx_5_receipt = w3.eth.waitForTransactionReceipt(tx_5_hash)
    assert tx_5_receipt['status'] == 1
    # get InterestPool contract
    logs_5 = get_logs(tx_5_hash, InterestPoolDao, "PoolRegistered")
    _pool_hash = InterestPoolDao.pool_hash(Lend_token.address, logs_5[0].args._pool_address)
    interest_pool_interface_codes = {}
    with open(os.path.join(os.path.dirname(os.path.realpath(__file__)),
        os.pardir, 'contracts/interfaces/ERC20.vy')) as f:
            interest_pool_interface_codes['ERC20'] = {
                'type': 'vyper',
                'code': f.read()
            }
    with open(os.path.join(os.path.dirname(os.path.realpath(__file__)),
        os.pardir, 'contracts/interfaces/ERC1155.vy')) as f:
            interest_pool_interface_codes['ERC1155'] = {
                'type': 'vyper',
                'code': f.read()
            }
    with open(os.path.join(os.path.dirname(os.path.realpath(__file__)),
        os.pardir, 'contracts/interfaces/ERC1155TokenReceiver.vy')) as f:
            interest_pool_interface_codes['ERC1155TokenReceiver'] = {
                'type': 'vyper',
                'code': f.read()
            }
    with open(os.path.join(os.path.dirname(os.path.realpath(__file__)),
        os.pardir, 'contracts/interfaces/InterestPoolDao.vy')) as f:
            interest_pool_interface_codes['InterestPoolDao'] = {
                'type': 'vyper',
                'code': f.read()
            }
    InterestPool = _get_contract_from_address(w3,
        InterestPoolDao.pools__pool_address(_pool_hash),
        'contracts/templates/InterestPoolTemplate1.v.py',
        interface_codes=interest_pool_interface_codes)
    # get InterestPoolCurrency
    InterestPoolCurrency = _get_contract_from_address(w3,
        InterestPool.pool_currency_address(),
        'contracts/templates/ERC20Template1.v.py')
    # pool_owner buys LST from a 3rd party
    LST_token.transfer(pool_owner, 1000 * 10 ** 18, transact={'from': owner})
    # pool_owner authorizes CurrencyDao to spend LST required for offer_registration_fee
    tx_6_hash = LST_token.approve(CurrencyDao.address, InterestPoolDao.offer_registration_fee() * (10 ** 18),
        transact={'from': pool_owner})
    tx_6_receipt = w3.eth.waitForTransactionReceipt(tx_6_hash)
    assert tx_6_receipt['status'] == 1
    # pool_owner registers an expiry : Last Thursday of December 2019, i.e., December 26th, 2019, i.e., Z19
    tx_7_hash = InterestPool.register_expiry(Z19,
        transact={'from': pool_owner, 'gas': 710000})
    tx_7_receipt = w3.eth.waitForTransactionReceipt(tx_7_hash)
    # get L_token
    L_token_address = CurrencyDao.currencies__l_currency_address(Lend_token.address)
    L_token = _get_contract_from_address(w3, L_token_address, 'contracts/templates/ERC20Template1.v.py')
    # assign one of the accounts as a lender
    lender = w3.eth.accounts[2]
    # lender buys 1000 lend token from a 3rd party exchange
    tx_8_hash = Lend_token.transfer(lender, 1000 * 10 ** 18, transact={'from': owner})
    tx_8_receipt = w3.eth.waitForTransactionReceipt(tx_8_hash)
    assert tx_8_receipt['status'] == 1
    # lender authorizes CurrencyDao to spend 100 lend currency
    tx_9_hash = Lend_token.approve(CurrencyDao.address, 100 * (10 ** 18),
        transact={'from': lender})
    tx_9_receipt = w3.eth.waitForTransactionReceipt(tx_9_hash)
    assert tx_9_receipt['status'] == 1
    # lender deposits Lend_token to Currency Pool and gets l_tokens
    tx_10_hash = CurrencyDao.currency_to_l_currency(Lend_token.address, 100 * 10 ** 18,
        transact={'from': lender, 'gas': 200000})
    tx_10_receipt = w3.eth.waitForTransactionReceipt(tx_10_hash)
    assert tx_10_receipt['status'] == 1
    # lender purchases InterestPoolCurrency for 100 L_tokens
    # lender gets 5000 InterestPoolCurrency tokens
    # 100 L_tokens are deposited into InterestPool account
    tx_11_hash = InterestPool.purchase_pool_currency(100 * 10 ** 18, transact={'from': lender})
    tx_11_receipt = w3.eth.waitForTransactionReceipt(tx_11_hash)
    assert tx_11_receipt['status'] == 1
    # pool_owner initiates offer of 20 I_tokens from the InterestPool
    # 20 L_tokens burned from InterestPool account
    # 20 I_tokens and 20 F_tokens deposited to InterestPool account
    tx_12_hash = InterestPool.increment_i_currency_supply(Z19, 20 * 10 ** 18, transact={'from': pool_owner, 'gas': 500000})
    tx_12_receipt = w3.eth.waitForTransactionReceipt(tx_12_hash)
    assert tx_12_receipt['status'] == 1
    # pool_owner reduces offer of 10 I_tokens from the InterestPool
    # 10 L_tokens minted from InterestPool account
    # 10 I_tokens and 10 F_tokens burned from InterestPool account
    tx_13_hash = InterestPool.decrement_i_currency_supply(Z19, 10 * 10 ** 18, transact={'from': pool_owner, 'gas': 450000})
    tx_13_receipt = w3.eth.waitForTransactionReceipt(tx_13_hash)
    assert tx_13_receipt['status'] == 1
    # verify multi_fungible_currencies balances of InterestPool
    assert InterestPool.i_currency_balance(Z19) == 10 * 10 ** 18
    assert InterestPool.f_currency_balance(Z19) == 10 * 10 ** 18
    assert InterestPool.total_f_currency_balance() == 10 * 10 ** 18
    assert InterestPool.l_currency_balance() == 90 * 10 ** 18
    assert InterestPool.total_l_currency_balance() == 100 * 10 ** 18
