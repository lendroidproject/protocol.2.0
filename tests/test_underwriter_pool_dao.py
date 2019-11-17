import os

import pytest

from web3 import Web3

from conftest import (
    ZERO_ADDRESS, EMPTY_BYTES32, Z19,
)


"""
    The tests in this file use the following deployed contracts, aka
    fixtures from conftest:
    #. LST_token
    #. Lend_token
    #. Borrow_token
    #. Malicious_token
    #. ERC20_library
    #. ERC1155_library
    #. CurrencyPool_library
    #. CurrencyDao
    #. ShieldPayoutGraph_library
    #. ShieldPayoutDao
    #. InterestPool_library
    #. InterestPoolDao
    #. UnderwriterPool_library
    #. UnderwriterPoolDao
"""


def test_initialize(w3, get_contract, get_logs,
        LST_token,
        ERC20_library, ERC1155_library,
        CurrencyPool_library, CurrencyDao,
        ShieldPayoutGraph_library, ShieldPayoutDao,
        UnderwriterPool_library, UnderwriterPoolDao
    ):
    owner = w3.eth.accounts[0]
    # initialize CurrencyDao
    tx_hash = CurrencyDao.initialize(
        owner, LST_token.address, CurrencyPool_library.address,
        ERC20_library.address, ERC1155_library.address,
        transact={'from': owner})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    # initialize ShieldPayoutDao
    tx_hash = ShieldPayoutDao.initialize(
        owner, LST_token.address, CurrencyDao.address,
        UnderwriterPoolDao.address, ShieldPayoutGraph_library.address,
        transact={'from': owner})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    # initialize UnderwriterPoolDao
    assert UnderwriterPoolDao.initialized() == False
    assert UnderwriterPoolDao.owner() in (None, ZERO_ADDRESS)
    assert UnderwriterPoolDao.protocol_dao_address() in (None, ZERO_ADDRESS)
    assert UnderwriterPoolDao.protocol_currency_address() in (None, ZERO_ADDRESS)
    assert UnderwriterPoolDao.DAO_TYPE_CURRENCY() == 0
    assert UnderwriterPoolDao.TEMPLATE_TYPE_UNDERWRITER_POOL() == 0
    assert UnderwriterPoolDao.TEMPLATE_TYPE_CURRENCY_ERC20() == 0
    tx_hash = UnderwriterPoolDao.initialize(
        owner, LST_token.address, CurrencyDao.address, ShieldPayoutDao.address,
        UnderwriterPool_library.address, ERC20_library.address,
        transact={'from': owner})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    assert UnderwriterPoolDao.initialized() == True
    assert UnderwriterPoolDao.owner() == owner
    assert UnderwriterPoolDao.protocol_dao_address() == owner
    assert UnderwriterPoolDao.protocol_currency_address() == LST_token.address
    assert UnderwriterPoolDao.DAO_TYPE_CURRENCY() == 1
    assert UnderwriterPoolDao.TEMPLATE_TYPE_UNDERWRITER_POOL() == 1
    assert UnderwriterPoolDao.TEMPLATE_TYPE_CURRENCY_ERC20() == 2
    assert UnderwriterPoolDao.templates(1) == UnderwriterPool_library.address
    assert UnderwriterPoolDao.templates(2) == ERC20_library.address


def test_set_offer_registration_fee_lookup(w3, get_contract, get_logs,
        LST_token,
        ERC20_library, ERC1155_library,
        CurrencyPool_library, CurrencyDao,
        ShieldPayoutGraph_library, ShieldPayoutDao,
        UnderwriterPool_library, UnderwriterPoolDao
    ):
    owner = w3.eth.accounts[0]
    # initialize CurrencyDao
    tx_hash = CurrencyDao.initialize(
        owner, LST_token.address, CurrencyPool_library.address,
        ERC20_library.address, ERC1155_library.address,
        transact={'from': owner})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    # initialize ShieldPayoutDao
    tx_hash = ShieldPayoutDao.initialize(
        owner, LST_token.address, CurrencyDao.address,
        UnderwriterPoolDao.address, ShieldPayoutGraph_library.address,
        transact={'from': owner})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    # initialize UnderwriterPoolDao
    tx_hash = UnderwriterPoolDao.initialize(
        owner, LST_token.address, CurrencyDao.address, ShieldPayoutDao.address,
        UnderwriterPool_library.address, ERC20_library.address,
        transact={'from': owner})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    assert UnderwriterPoolDao.offer_registration_fee_lookup__minimum_fee(UnderwriterPoolDao.address) == 0
    assert UnderwriterPoolDao.offer_registration_fee_lookup__minimum_interval(UnderwriterPoolDao.address) == 0
    assert UnderwriterPoolDao.offer_registration_fee_lookup__fee_multiplier(UnderwriterPoolDao.address) == 0
    assert UnderwriterPoolDao.offer_registration_fee_lookup__fee_multiplier_decimals(UnderwriterPoolDao.address) == 0
    assert UnderwriterPoolDao.offer_registration_fee_lookup__last_registered_at(UnderwriterPoolDao.address) == 0
    assert UnderwriterPoolDao.offer_registration_fee_lookup__last_paid_fee(UnderwriterPoolDao.address) == 0
    # set_offer_registration_fee_lookup()
    _minimum_fee = 100
    _minimum_interval = 10
    _fee_multiplier = 2000
    _fee_multiplier_decimals = 1000
    tx_hash = UnderwriterPoolDao.set_offer_registration_fee_lookup(_minimum_fee,
        _minimum_interval, _fee_multiplier, _fee_multiplier_decimals,
        transact={'from': owner})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    assert UnderwriterPoolDao.offer_registration_fee_lookup__minimum_fee(UnderwriterPoolDao.address) == _minimum_fee
    assert UnderwriterPoolDao.offer_registration_fee_lookup__minimum_interval(UnderwriterPoolDao.address) == _minimum_interval
    assert UnderwriterPoolDao.offer_registration_fee_lookup__fee_multiplier(UnderwriterPoolDao.address) == _fee_multiplier
    assert UnderwriterPoolDao.offer_registration_fee_lookup__fee_multiplier_decimals(UnderwriterPoolDao.address) == _fee_multiplier_decimals
    assert UnderwriterPoolDao.offer_registration_fee_lookup__last_registered_at(UnderwriterPoolDao.address) == 0
    assert UnderwriterPoolDao.offer_registration_fee_lookup__last_paid_fee(UnderwriterPoolDao.address) == 0
    assert UnderwriterPoolDao.offer_registration_fee() == _minimum_fee


def test_set_shield_currency_minimum_collateral_value(w3, get_contract, get_logs,
        LST_token, Lend_token, Borrow_token,
        ERC20_library, ERC1155_library,
        CurrencyPool_library, CurrencyDao,
        ShieldPayoutGraph_library, ShieldPayoutDao,
        UnderwriterPool_library, UnderwriterPoolDao
    ):
    owner = w3.eth.accounts[0]
    # initialize CurrencyDao
    tx_1_hash = CurrencyDao.initialize(
        owner, LST_token.address, CurrencyPool_library.address,
        ERC20_library.address, ERC1155_library.address,
        transact={'from': owner})
    tx_1_receipt = w3.eth.waitForTransactionReceipt(tx_1_hash)
    assert tx_1_receipt['status'] == 1
    tx_2_hash = CurrencyDao.set_currency_support(Lend_token.address, True,
        transact={'from': owner, 'gas': 1570000})
    tx_2_receipt = w3.eth.waitForTransactionReceipt(tx_2_hash)
    assert tx_2_receipt['status'] == 1
    # initialize ShieldPayoutDao
    tx_hash = ShieldPayoutDao.initialize(
        owner, LST_token.address, CurrencyDao.address,
        UnderwriterPoolDao.address, ShieldPayoutGraph_library.address,
        transact={'from': owner})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    # initialize UnderwriterPoolDao
    tx_3_hash = UnderwriterPoolDao.initialize(
        owner, LST_token.address, CurrencyDao.address, ShieldPayoutDao.address,
        UnderwriterPool_library.address, ERC20_library.address,
        transact={'from': owner})
    tx_3_receipt = w3.eth.waitForTransactionReceipt(tx_3_hash)
    assert tx_3_receipt['status'] == 1
    # vefiry shield_currency_price is not set
    _strike_price = 200 * 10 ** 18
    multi_fungible_addresses = CurrencyDao.multi_fungible_addresses(Lend_token.address)
    _s_hash = UnderwriterPoolDao.multi_fungible_currency_hash(
        multi_fungible_addresses[3], Lend_token.address, Z19,
        Borrow_token.address, _strike_price)
    assert UnderwriterPoolDao.shield_currency_minimum_collateral_values(_s_hash) == 0
    # set shield_currency_price
    shield_currency_minimum_collateral_value = 20 * 10 ** 18
    tx_4_hash = UnderwriterPoolDao.set_shield_currency_minimum_collateral_value(
        Lend_token.address, Z19, Borrow_token.address, _strike_price,
        shield_currency_minimum_collateral_value, transact={'from': owner})
    tx_4_receipt = w3.eth.waitForTransactionReceipt(tx_4_hash)
    assert tx_4_receipt['status'] == 1
    assert UnderwriterPoolDao.shield_currency_minimum_collateral_values(_s_hash) == shield_currency_minimum_collateral_value


def test_failed_transaction_for_register_pool_call_for_non_supported_token(
        w3, get_contract, get_logs,
        LST_token, Lend_token, Malicious_token,
        ERC20_library, ERC1155_library,
        CurrencyPool_library, CurrencyDao,
        ShieldPayoutGraph_library, ShieldPayoutDao,
        UnderwriterPool_library, UnderwriterPoolDao
    ):
    owner = w3.eth.accounts[0]
    # initialize CurrencyDao
    tx_hash = CurrencyDao.initialize(
        owner, LST_token.address, CurrencyPool_library.address,
        ERC20_library.address, ERC1155_library.address,
        transact={'from': owner})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    # initialize ShieldPayoutDao
    tx_hash = ShieldPayoutDao.initialize(
        owner, LST_token.address, CurrencyDao.address,
        UnderwriterPoolDao.address, ShieldPayoutGraph_library.address,
        transact={'from': owner})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    # initialize UnderwriterPoolDao
    tx_hash = UnderwriterPoolDao.initialize(
        owner, LST_token.address, CurrencyDao.address, ShieldPayoutDao.address,
        UnderwriterPool_library.address, ERC20_library.address,
        transact={'from': owner})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    # set_offer_registration_fee_lookup()
    tx_hash = UnderwriterPoolDao.set_offer_registration_fee_lookup(100, 10, 2000,
        1000, transact={'from': owner})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    # set_currency_support for Lend_token in CurrencyDao
    tx_hash = CurrencyDao.set_currency_support(Lend_token.address, True,
        transact={'from': owner, 'gas': 1570000})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    # register_pool for Lend_token
    tx_hash = UnderwriterPoolDao.register_pool(Malicious_token.address,
        'Underwriter Pool A', 'UPA', 50, transact={'from': owner, 'gas': 1000000})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 0


def test_register_pool(w3, get_contract, get_logs,
        LST_token, Lend_token, Malicious_token,
        ERC20_library, ERC1155_library,
        CurrencyPool_library, CurrencyDao,
        ShieldPayoutGraph_library, ShieldPayoutDao,
        UnderwriterPool_library, UnderwriterPoolDao
    ):
    owner = w3.eth.accounts[0]
    # initialize CurrencyDao
    tx_1_hash = CurrencyDao.initialize(
        owner, LST_token.address, CurrencyPool_library.address,
        ERC20_library.address, ERC1155_library.address,
        transact={'from': owner})
    tx_1_receipt = w3.eth.waitForTransactionReceipt(tx_1_hash)
    assert tx_1_receipt['status'] == 1
    # initialize ShieldPayoutDao
    tx_hash = ShieldPayoutDao.initialize(
        owner, LST_token.address, CurrencyDao.address,
        UnderwriterPoolDao.address, ShieldPayoutGraph_library.address,
        transact={'from': owner})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    # initialize UnderwriterPoolDao
    tx_2_hash = UnderwriterPoolDao.initialize(
        owner, LST_token.address, CurrencyDao.address, ShieldPayoutDao.address,
        UnderwriterPool_library.address, ERC20_library.address,
        transact={'from': owner})
    tx_2_receipt = w3.eth.waitForTransactionReceipt(tx_2_hash)
    assert tx_2_receipt['status'] == 1
    # set_offer_registration_fee_lookup()
    _minimum_fee = 100
    _minimum_interval = 10
    _fee_multiplier = 2000
    _fee_multiplier_decimals = 1000
    tx_3_hash = UnderwriterPoolDao.set_offer_registration_fee_lookup(_minimum_fee,
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
    tx_5_hash = UnderwriterPoolDao.register_pool(Lend_token.address,
        'Underwriter Pool A', 'UPA', 50,
        transact={'from': pool_owner, 'gas': 850000})
    tx_5_receipt = w3.eth.waitForTransactionReceipt(tx_5_hash)
    assert tx_5_receipt['status'] == 1
    # verify PoolRegistered log from UnderwriterPoolDao
    logs_5 = get_logs(tx_5_hash, UnderwriterPoolDao, "PoolRegistered")
    assert len(logs_5) == 1
    assert logs_5[0].args._operator == pool_owner
    assert logs_5[0].args._currency_address == Lend_token.address
    _pool_hash = UnderwriterPoolDao.pool_hash(Lend_token.address, logs_5[0].args._pool_address)
    assert UnderwriterPoolDao.pools__currency_address(_pool_hash) == Lend_token.address
    assert UnderwriterPoolDao.pools__pool_name(_pool_hash) == 'Underwriter Pool A'
    assert UnderwriterPoolDao.pools__pool_address(_pool_hash) == logs_5[0].args._pool_address
    assert UnderwriterPoolDao.pools__pool_operator(_pool_hash) == pool_owner
    assert UnderwriterPoolDao.pools__hash(_pool_hash) == _pool_hash
    # verify UnderwriterPool initialized
    UnderwriterPool = get_contract(
        'contracts/templates/UnderwriterPoolTemplate1.v.py',
        interfaces=['ERC20', 'ERC1155', 'ERC1155TokenReceiver', 'UnderwriterPoolDao'],
        address=UnderwriterPoolDao.pools__pool_address(_pool_hash)
    )
    assert UnderwriterPool.owner() == UnderwriterPoolDao.address
    assert UnderwriterPool.pool_hash() == _pool_hash
    assert UnderwriterPool.name() == 'Underwriter Pool A'
    assert UnderwriterPool.initial_exchange_rate() == 50
    assert UnderwriterPool.currency_address() == Lend_token.address
    assert not UnderwriterPool.pool_currency_address() in (None, ZERO_ADDRESS)
    assert UnderwriterPool.l_currency_address() == CurrencyDao.currencies__l_currency_address(Lend_token.address)
    assert UnderwriterPool.i_currency_address() == CurrencyDao.currencies__i_currency_address(Lend_token.address)
    assert UnderwriterPool.s_currency_address() == CurrencyDao.currencies__s_currency_address(Lend_token.address)
    assert UnderwriterPool.u_currency_address() == CurrencyDao.currencies__u_currency_address(Lend_token.address)
    # verify Transfer log from UnderwriterPool.pool_currency
    UnderwriterPoolCurrency = get_contract(
        'contracts/templates/ERC20Template1.v.py',
        address=UnderwriterPool.pool_currency_address()
    )
    logs_5 = get_logs(tx_5_hash, UnderwriterPoolCurrency, "Transfer")
    assert len(logs_5) == 1
    assert logs_5[0].args._from == ZERO_ADDRESS
    assert logs_5[0].args._to == UnderwriterPool.address
    assert logs_5[0].args._value == 0


def test_register_expiry(w3, get_contract, get_logs,
        LST_token, Lend_token, Borrow_token, Malicious_token,
        ERC20_library, ERC1155_library,
        CurrencyPool_library, CurrencyDao,
        ShieldPayoutGraph_library, ShieldPayoutDao,
        UnderwriterPool_library, UnderwriterPoolDao
    ):
    owner = w3.eth.accounts[0]
    # initialize CurrencyDao
    tx_1_hash = CurrencyDao.initialize(
        owner, LST_token.address, CurrencyPool_library.address,
        ERC20_library.address, ERC1155_library.address,
        transact={'from': owner})
    tx_1_receipt = w3.eth.waitForTransactionReceipt(tx_1_hash)
    assert tx_1_receipt['status'] == 1
    # initialize ShieldPayoutDao
    tx_hash = ShieldPayoutDao.initialize(
        owner, LST_token.address, CurrencyDao.address,
        UnderwriterPoolDao.address, ShieldPayoutGraph_library.address,
        transact={'from': owner})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    # initialize UnderwriterPoolDao
    tx_2_hash = UnderwriterPoolDao.initialize(
        owner, LST_token.address, CurrencyDao.address, ShieldPayoutDao.address,
        UnderwriterPool_library.address, ERC20_library.address,
        transact={'from': owner})
    tx_2_receipt = w3.eth.waitForTransactionReceipt(tx_2_hash)
    assert tx_2_receipt['status'] == 1
    # set_offer_registration_fee_lookup()
    _minimum_fee = 100
    _minimum_interval = 10
    _fee_multiplier = 2000
    _fee_multiplier_decimals = 1000
    tx_3_hash = UnderwriterPoolDao.set_offer_registration_fee_lookup(_minimum_fee,
        _minimum_interval, _fee_multiplier, _fee_multiplier_decimals,
        transact={'from': owner})
    tx_3_receipt = w3.eth.waitForTransactionReceipt(tx_3_hash)
    assert tx_3_receipt['status'] == 1
    # set_currency_support for Lend_token in CurrencyDao
    tx_4_hash = CurrencyDao.set_currency_support(Lend_token.address, True,
        transact={'from': owner, 'gas': 1570000})
    tx_4_receipt = w3.eth.waitForTransactionReceipt(tx_4_hash)
    assert tx_4_receipt['status'] == 1
    # set_currency_support for Borrow_token in CurrencyDao
    tx_5_hash = CurrencyDao.set_currency_support(Borrow_token.address, True,
        transact={'from': owner, 'gas': 1570000})
    tx_5_receipt = w3.eth.waitForTransactionReceipt(tx_5_hash)
    assert tx_5_receipt['status'] == 1
    # register_pool for Lend_token
    pool_owner = w3.eth.accounts[1]
    tx_6_hash = UnderwriterPoolDao.register_pool(Lend_token.address,
        'Underwriter Pool A', 'UPA', 50,
        transact={'from': pool_owner, 'gas': 850000})
    tx_6_receipt = w3.eth.waitForTransactionReceipt(tx_6_hash)
    assert tx_6_receipt['status'] == 1
    # get UnderwriterPool contract
    logs_6 = get_logs(tx_6_hash, UnderwriterPoolDao, "PoolRegistered")
    _pool_hash = UnderwriterPoolDao.pool_hash(Lend_token.address, logs_6[0].args._pool_address)
    UnderwriterPool = get_contract(
        'contracts/templates/UnderwriterPoolTemplate1.v.py',
        interfaces=['ERC20', 'ERC1155', 'ERC1155TokenReceiver', 'UnderwriterPoolDao'],
        address=UnderwriterPoolDao.pools__pool_address(_pool_hash)
    )
    # get UnderwriterPoolCurrency
    UnderwriterPoolCurrency = get_contract(
        'contracts/templates/ERC20Template1.v.py',
        address=UnderwriterPool.pool_currency_address()
    )
    # pool_owner buys LST from a 3rd party
    assert LST_token.balanceOf(pool_owner) == 0
    LST_token.transfer(pool_owner, 1000 * 10 ** 18, transact={'from': owner})
    assert LST_token.balanceOf(pool_owner) == 1000 * 10 ** 18
    # pool_owner authorizes CurrencyDao to spend LST required for offer_registration_fee
    tx_7_hash = LST_token.approve(CurrencyDao.address, UnderwriterPoolDao.offer_registration_fee() * (10 ** 18),
        transact={'from': pool_owner})
    tx_7_receipt = w3.eth.waitForTransactionReceipt(tx_7_hash)
    assert tx_7_receipt['status'] == 1
    # pool_owner registers an expiry : Last Thursday of December 2019, i.e., December 26th, 2019, i.e., Z19
    _strike_price = 200 * 10 ** 18
    _expiry_hash = UnderwriterPool.expiry_hash(Z19, Borrow_token.address,
        _strike_price)
    assert UnderwriterPool.expiries__expiry_timestamp(_expiry_hash) == 0
    assert Web3.toHex(UnderwriterPool.expiries__i_currency_hash(_expiry_hash)) == EMPTY_BYTES32
    assert UnderwriterPool.expiries__i_currency_id(_expiry_hash) == 0
    assert Web3.toHex(UnderwriterPool.expiries__s_currency_hash(_expiry_hash)) == EMPTY_BYTES32
    assert UnderwriterPool.expiries__s_currency_id(_expiry_hash) == 0
    assert Web3.toHex(UnderwriterPool.expiries__u_currency_hash(_expiry_hash)) == EMPTY_BYTES32
    assert UnderwriterPool.expiries__u_currency_id(_expiry_hash) == 0
    assert UnderwriterPool.expiries__is_active(_expiry_hash) in (None, False)
    tx_8_hash = UnderwriterPool.register_expiry(Z19, Borrow_token.address,
        _strike_price, transact={'from': pool_owner, 'gas': 1700000})
    tx_8_receipt = w3.eth.waitForTransactionReceipt(tx_8_hash)
    print('\n\n tx_8_receipt : {0}'.format(tx_8_receipt))
    assert tx_8_receipt['status'] == 1
    assert UnderwriterPool.expiries__expiry_timestamp(_expiry_hash) == Z19
    assert UnderwriterPoolDao.multi_fungible_currencies__token_id(Web3.toHex(UnderwriterPool.expiries__i_currency_hash(_expiry_hash))) == UnderwriterPool.expiries__i_currency_id(_expiry_hash)
    assert UnderwriterPoolDao.multi_fungible_currencies__token_id(Web3.toHex(UnderwriterPool.expiries__s_currency_hash(_expiry_hash))) == UnderwriterPool.expiries__s_currency_id(_expiry_hash)
    assert UnderwriterPoolDao.multi_fungible_currencies__token_id(Web3.toHex(UnderwriterPool.expiries__u_currency_hash(_expiry_hash))) == UnderwriterPool.expiries__u_currency_id(_expiry_hash)
    assert UnderwriterPool.expiries__is_active(_expiry_hash) == True


def test_deposit_l_currency(w3, get_contract, get_logs,
        LST_token, Lend_token, Malicious_token,
        ERC20_library, ERC1155_library,
        CurrencyPool_library, CurrencyDao,
        ShieldPayoutGraph_library, ShieldPayoutDao,
        UnderwriterPool_library, UnderwriterPoolDao
    ):
    owner = w3.eth.accounts[0]
    # initialize CurrencyDao
    tx_1_hash = CurrencyDao.initialize(
        owner, LST_token.address, CurrencyPool_library.address,
        ERC20_library.address, ERC1155_library.address,
        transact={'from': owner})
    tx_1_receipt = w3.eth.waitForTransactionReceipt(tx_1_hash)
    assert tx_1_receipt['status'] == 1
    # initialize ShieldPayoutDao
    tx_hash = ShieldPayoutDao.initialize(
        owner, LST_token.address, CurrencyDao.address,
        UnderwriterPoolDao.address, ShieldPayoutGraph_library.address,
        transact={'from': owner})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    # initialize UnderwriterPoolDao
    tx_2_hash = UnderwriterPoolDao.initialize(
        owner, LST_token.address, CurrencyDao.address, ShieldPayoutDao.address,
        UnderwriterPool_library.address, ERC20_library.address,
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
    tx_4_hash = UnderwriterPoolDao.register_pool(Lend_token.address,
        'Underwriter Pool A', 'UPA', 50,
        transact={'from': pool_owner, 'gas': 850000})
    tx_4_receipt = w3.eth.waitForTransactionReceipt(tx_4_hash)
    assert tx_4_receipt['status'] == 1
    # get UnderwriterPool contract
    logs_4 = get_logs(tx_4_hash, UnderwriterPoolDao, "PoolRegistered")
    _pool_hash = UnderwriterPoolDao.pool_hash(Lend_token.address, logs_4[0].args._pool_address)
    UnderwriterPool = get_contract(
        'contracts/templates/UnderwriterPoolTemplate1.v.py',
        interfaces=['ERC20', 'ERC1155', 'ERC1155TokenReceiver', 'UnderwriterPoolDao'],
        address=UnderwriterPoolDao.pools__pool_address(_pool_hash)
    )
    # get UnderwriterPoolCurrency
    UnderwriterPoolCurrency = get_contract(
        'contracts/templates/ERC20Template1.v.py',
        address=UnderwriterPool.pool_currency_address()
    )
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
    L_token = get_contract(
        'contracts/templates/ERC20Template1.v.py',
        address=L_token_address
    )
    l_token_balance = L_token.balanceOf(lender)
    assert l_token_balance == 100 * 10 ** 18
    # verify lend currency balance of UnderwriterPool
    l_token_balance = UnderwriterPool.l_currency_balance()
    assert l_token_balance == 0
    # lender purchases UnderwriterPoolCurrency for 100 L_tokens
    assert UnderwriterPoolCurrency.totalSupply() == 0
    estimated_UnderwriterPoolCurrency_tokens = UnderwriterPool.estimated_pool_tokens(100 * 10 ** 18)
    assert estimated_UnderwriterPoolCurrency_tokens == (50 * 100) * 10 ** 18
    tx_7_hash = UnderwriterPool.purchase_pool_currency(100 * 10 ** 18, transact={'from': lender})
    tx_7_receipt = w3.eth.waitForTransactionReceipt(tx_7_hash)
    assert tx_7_receipt['status'] == 1
    # verify lend currency balance of UnderwriterPool
    l_token_balance = UnderwriterPool.l_currency_balance()
    assert l_token_balance == 100 * 10 ** 18
    # verify lend currency balance of lender
    l_token_balance = L_token.balanceOf(lender)
    assert l_token_balance == 0
    # verify UnderwriterPoolCurrency balance of lender
    UnderwriterPoolCurrency_balance = UnderwriterPoolCurrency.balanceOf(lender)
    assert UnderwriterPoolCurrency_balance == estimated_UnderwriterPoolCurrency_tokens
    assert UnderwriterPoolCurrency.totalSupply() == estimated_UnderwriterPoolCurrency_tokens


def test_l_currency_to_i_and_s_and_u_currency(w3, get_contract, get_logs,
        LST_token, Lend_token, Borrow_token, Malicious_token,
        ERC20_library, ERC1155_library,
        CurrencyPool_library, CurrencyDao,
        ShieldPayoutGraph_library, ShieldPayoutDao,
        UnderwriterPool_library, UnderwriterPoolDao
    ):
    owner = w3.eth.accounts[0]
    # initialize CurrencyDao
    tx_1_hash = CurrencyDao.initialize(
        owner, LST_token.address, CurrencyPool_library.address,
        ERC20_library.address, ERC1155_library.address,
        transact={'from': owner})
    tx_1_receipt = w3.eth.waitForTransactionReceipt(tx_1_hash)
    assert tx_1_receipt['status'] == 1
    # initialize ShieldPayoutDao
    tx_hash = ShieldPayoutDao.initialize(
        owner, LST_token.address, CurrencyDao.address,
        UnderwriterPoolDao.address, ShieldPayoutGraph_library.address,
        transact={'from': owner})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    # initialize UnderwriterPoolDao
    tx_2_hash = UnderwriterPoolDao.initialize(
        owner, LST_token.address, CurrencyDao.address, ShieldPayoutDao.address,
        UnderwriterPool_library.address, ERC20_library.address,
        transact={'from': owner})
    tx_2_receipt = w3.eth.waitForTransactionReceipt(tx_2_hash)
    assert tx_2_receipt['status'] == 1
    # set_offer_registration_fee_lookup()
    _minimum_fee = 100
    _minimum_interval = 10
    _fee_multiplier = 2000
    _fee_multiplier_decimals = 1000
    tx_3_hash = UnderwriterPoolDao.set_offer_registration_fee_lookup(_minimum_fee,
        _minimum_interval, _fee_multiplier, _fee_multiplier_decimals,
        transact={'from': owner})
    tx_3_receipt = w3.eth.waitForTransactionReceipt(tx_3_hash)
    assert tx_3_receipt['status'] == 1
    # set_currency_support for Lend_token in CurrencyDao
    tx_4_hash = CurrencyDao.set_currency_support(Lend_token.address, True,
        transact={'from': owner, 'gas': 1570000})
    tx_4_receipt = w3.eth.waitForTransactionReceipt(tx_4_hash)
    assert tx_4_receipt['status'] == 1
    # set_currency_support for Borrow_token in CurrencyDao
    tx_5_hash = CurrencyDao.set_currency_support(Borrow_token.address, True,
        transact={'from': owner, 'gas': 1570000})
    tx_5_receipt = w3.eth.waitForTransactionReceipt(tx_5_hash)
    assert tx_5_receipt['status'] == 1
    # register_pool for Lend_token
    pool_owner = w3.eth.accounts[1]
    tx_6_hash = UnderwriterPoolDao.register_pool(Lend_token.address,
        'Underwriter Pool A', 'UPA', 50,
        transact={'from': pool_owner, 'gas': 850000})
    tx_6_receipt = w3.eth.waitForTransactionReceipt(tx_6_hash)
    assert tx_6_receipt['status'] == 1
    # get UnderwriterPool contract
    logs_6 = get_logs(tx_6_hash, UnderwriterPoolDao, "PoolRegistered")
    _pool_hash = UnderwriterPoolDao.pool_hash(Lend_token.address, logs_6[0].args._pool_address)
    UnderwriterPool = get_contract(
        'contracts/templates/UnderwriterPoolTemplate1.v.py',
        interfaces=['ERC20', 'ERC1155', 'ERC1155TokenReceiver', 'UnderwriterPoolDao'],
        address=UnderwriterPoolDao.pools__pool_address(_pool_hash)
    )
    # get UnderwriterPoolCurrency
    UnderwriterPoolCurrency = get_contract(
        'contracts/templates/ERC20Template1.v.py',
        address=UnderwriterPool.pool_currency_address()
    )
    # pool_owner buys LST from a 3rd party
    LST_token.transfer(pool_owner, 1000 * 10 ** 18, transact={'from': owner})
    # pool_owner authorizes CurrencyDao to spend LST required for offer_registration_fee
    tx_7_hash = LST_token.approve(CurrencyDao.address, UnderwriterPoolDao.offer_registration_fee() * (10 ** 18),
        transact={'from': pool_owner})
    tx_7_receipt = w3.eth.waitForTransactionReceipt(tx_7_hash)
    assert tx_7_receipt['status'] == 1
    # pool_owner registers an expiry : Last Thursday of December 2019, i.e., December 26th, 2019, i.e., Z19
    _strike_price = 200 * 10 ** 18
    tx_8_hash = UnderwriterPool.register_expiry(Z19, Borrow_token.address,
        _strike_price, transact={'from': pool_owner, 'gas': 1700000})
    tx_8_receipt = w3.eth.waitForTransactionReceipt(tx_8_hash)
    assert tx_8_receipt['status'] == 1
    # get L_token
    L_token_address = CurrencyDao.currencies__l_currency_address(Lend_token.address)
    L_token = get_contract(
        'contracts/templates/ERC20Template1.v.py',
        address=L_token_address
    )
    # assign one of the accounts as a lender
    lender = w3.eth.accounts[2]
    # lender buys 1000 lend token from a 3rd party exchange
    tx_9_hash = Lend_token.transfer(lender, 1000 * 10 ** 18, transact={'from': owner})
    tx_9_receipt = w3.eth.waitForTransactionReceipt(tx_9_hash)
    assert tx_9_receipt['status'] == 1
    # lender authorizes CurrencyDao to spend 100 lend currency
    tx_10_hash = Lend_token.approve(CurrencyDao.address, 100 * (10 ** 18),
        transact={'from': lender})
    tx_10_receipt = w3.eth.waitForTransactionReceipt(tx_10_hash)
    assert tx_10_receipt['status'] == 1
    # lender deposits Lend_token to Currency Pool and gets l_tokens
    tx_11_hash = CurrencyDao.currency_to_l_currency(Lend_token.address, 100 * 10 ** 18,
        transact={'from': lender, 'gas': 200000})
    tx_11_receipt = w3.eth.waitForTransactionReceipt(tx_11_hash)
    assert tx_11_receipt['status'] == 1
    # lender purchases UnderwriterPoolCurrency for 100 L_tokens
    # lender gets 5000 UnderwriterPoolCurrency tokens
    # 100 L_tokens are deposited into UnderwriterPool account
    tx_12_hash = UnderwriterPool.purchase_pool_currency(100 * 10 ** 18, transact={'from': lender})
    tx_12_receipt = w3.eth.waitForTransactionReceipt(tx_12_hash)
    assert tx_12_receipt['status'] == 1
    # vefiry shield_currency_price is not set
    multi_fungible_addresses = CurrencyDao.multi_fungible_addresses(Lend_token.address)
    _s_hash = UnderwriterPoolDao.multi_fungible_currency_hash(
        multi_fungible_addresses[3], Lend_token.address, Z19,
        Borrow_token.address, _strike_price)
    # set shield_currency_price
    shield_currency_minimum_collateral_value = 20 * 10 ** 18
    tx_13_hash = UnderwriterPoolDao.set_shield_currency_minimum_collateral_value(
        Lend_token.address, Z19, Borrow_token.address, _strike_price,
        shield_currency_minimum_collateral_value, transact={'from': owner})
    tx_13_receipt = w3.eth.waitForTransactionReceipt(tx_13_hash)
    assert tx_13_receipt['status'] == 1
    # pool_owner initiates offer of 20 I_tokens from the UnderwriterPool
    # 20 L_tokens burned from UnderwriterPool account
    # 20 I_tokens minted to UnderwriterPool account
    # 1 S_token minted to UnderwriterPool account
    # 1 U_token minted to UnderwriterPool account
    tx_14_hash = UnderwriterPool.increment_i_currency_supply(
        Z19, Borrow_token.address, _strike_price, 20 * 10 ** 18,
        transact={'from': pool_owner, 'gas': 600000})
    tx_14_receipt = w3.eth.waitForTransactionReceipt(tx_14_hash)
    print(tx_14_receipt)
    assert tx_14_receipt['status'] == 1
    # verify multi_fungible_currencies balances of UnderwriterPool
    assert UnderwriterPool.l_currency_balance() == (100 - 20) * 10 ** 18
    assert UnderwriterPool.i_currency_balance(Z19, Borrow_token.address, _strike_price) == 20 * 10 ** 18
    assert UnderwriterPool.s_currency_balance(Z19, Borrow_token.address, _strike_price) == 1 * 10 ** 18
    assert UnderwriterPool.u_currency_balance(Z19, Borrow_token.address, _strike_price) == 1 * 10 ** 18


def test_l_currency_from_i_and_s_and_u_currency(w3, get_contract, get_logs,
        LST_token, Lend_token, Borrow_token, Malicious_token,
        ERC20_library, ERC1155_library,
        CurrencyPool_library, CurrencyDao,
        ShieldPayoutGraph_library, ShieldPayoutDao,
        UnderwriterPool_library, UnderwriterPoolDao
    ):
    owner = w3.eth.accounts[0]
    # initialize CurrencyDao
    tx_1_hash = CurrencyDao.initialize(
        owner, LST_token.address, CurrencyPool_library.address,
        ERC20_library.address, ERC1155_library.address,
        transact={'from': owner})
    tx_1_receipt = w3.eth.waitForTransactionReceipt(tx_1_hash)
    assert tx_1_receipt['status'] == 1
    # initialize ShieldPayoutDao
    tx_hash = ShieldPayoutDao.initialize(
        owner, LST_token.address, CurrencyDao.address,
        UnderwriterPoolDao.address, ShieldPayoutGraph_library.address,
        transact={'from': owner})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    # initialize UnderwriterPoolDao
    tx_2_hash = UnderwriterPoolDao.initialize(
        owner, LST_token.address, CurrencyDao.address, ShieldPayoutDao.address,
        UnderwriterPool_library.address, ERC20_library.address,
        transact={'from': owner})
    tx_2_receipt = w3.eth.waitForTransactionReceipt(tx_2_hash)
    assert tx_2_receipt['status'] == 1
    # set_offer_registration_fee_lookup()
    _minimum_fee = 100
    _minimum_interval = 10
    _fee_multiplier = 2000
    _fee_multiplier_decimals = 1000
    tx_3_hash = UnderwriterPoolDao.set_offer_registration_fee_lookup(_minimum_fee,
        _minimum_interval, _fee_multiplier, _fee_multiplier_decimals,
        transact={'from': owner})
    tx_3_receipt = w3.eth.waitForTransactionReceipt(tx_3_hash)
    assert tx_3_receipt['status'] == 1
    # set_currency_support for Lend_token in CurrencyDao
    tx_4_hash = CurrencyDao.set_currency_support(Lend_token.address, True,
        transact={'from': owner, 'gas': 1570000})
    tx_4_receipt = w3.eth.waitForTransactionReceipt(tx_4_hash)
    assert tx_4_receipt['status'] == 1
    # set_currency_support for Borrow_token in CurrencyDao
    tx_5_hash = CurrencyDao.set_currency_support(Borrow_token.address, True,
        transact={'from': owner, 'gas': 1570000})
    tx_5_receipt = w3.eth.waitForTransactionReceipt(tx_5_hash)
    assert tx_5_receipt['status'] == 1
    # register_pool for Lend_token
    pool_owner = w3.eth.accounts[1]
    tx_6_hash = UnderwriterPoolDao.register_pool(Lend_token.address,
        'Underwriter Pool A', 'UPA', 50,
        transact={'from': pool_owner, 'gas': 850000})
    tx_6_receipt = w3.eth.waitForTransactionReceipt(tx_6_hash)
    assert tx_6_receipt['status'] == 1
    # get UnderwriterPool contract
    logs_6 = get_logs(tx_6_hash, UnderwriterPoolDao, "PoolRegistered")
    _pool_hash = UnderwriterPoolDao.pool_hash(Lend_token.address, logs_6[0].args._pool_address)
    UnderwriterPool = get_contract(
        'contracts/templates/UnderwriterPoolTemplate1.v.py',
        interfaces=['ERC20', 'ERC1155', 'ERC1155TokenReceiver', 'UnderwriterPoolDao'],
        address=UnderwriterPoolDao.pools__pool_address(_pool_hash)
    )
    # get UnderwriterPoolCurrency
    UnderwriterPoolCurrency = get_contract(
        'contracts/templates/ERC20Template1.v.py',
        address=UnderwriterPool.pool_currency_address()
    )
    # pool_owner buys LST from a 3rd party
    LST_token.transfer(pool_owner, 1000 * 10 ** 18, transact={'from': owner})
    # pool_owner authorizes CurrencyDao to spend LST required for offer_registration_fee
    tx_7_hash = LST_token.approve(CurrencyDao.address, UnderwriterPoolDao.offer_registration_fee() * (10 ** 18),
        transact={'from': pool_owner})
    tx_7_receipt = w3.eth.waitForTransactionReceipt(tx_7_hash)
    assert tx_7_receipt['status'] == 1
    # pool_owner registers an expiry : Last Thursday of December 2019, i.e., December 26th, 2019, i.e., Z19
    _strike_price = 200 * 10 ** 18
    tx_8_hash = UnderwriterPool.register_expiry(Z19, Borrow_token.address,
        _strike_price, transact={'from': pool_owner, 'gas': 1700000})
    tx_8_receipt = w3.eth.waitForTransactionReceipt(tx_8_hash)
    assert tx_8_receipt['status'] == 1
    # get L_token
    L_token_address = CurrencyDao.currencies__l_currency_address(Lend_token.address)
    L_token = get_contract(
        'contracts/templates/ERC20Template1.v.py',
        address=L_token_address
    )
    # assign one of the accounts as a lender
    lender = w3.eth.accounts[2]
    # lender buys 1000 lend token from a 3rd party exchange
    tx_9_hash = Lend_token.transfer(lender, 1000 * 10 ** 18, transact={'from': owner})
    tx_9_receipt = w3.eth.waitForTransactionReceipt(tx_9_hash)
    assert tx_9_receipt['status'] == 1
    # lender authorizes CurrencyDao to spend 100 lend currency
    tx_10_hash = Lend_token.approve(CurrencyDao.address, 100 * (10 ** 18),
        transact={'from': lender})
    tx_10_receipt = w3.eth.waitForTransactionReceipt(tx_10_hash)
    assert tx_10_receipt['status'] == 1
    # lender deposits Lend_token to Currency Pool and gets l_tokens
    tx_11_hash = CurrencyDao.currency_to_l_currency(Lend_token.address, 100 * 10 ** 18,
        transact={'from': lender, 'gas': 200000})
    tx_11_receipt = w3.eth.waitForTransactionReceipt(tx_11_hash)
    assert tx_11_receipt['status'] == 1
    # lender purchases UnderwriterPoolCurrency for 100 L_tokens
    # lender gets 5000 UnderwriterPoolCurrency tokens
    # 100 L_tokens are deposited into UnderwriterPool account
    tx_12_hash = UnderwriterPool.purchase_pool_currency(100 * 10 ** 18, transact={'from': lender})
    tx_12_receipt = w3.eth.waitForTransactionReceipt(tx_12_hash)
    assert tx_12_receipt['status'] == 1
    # vefiry shield_currency_price is not set
    multi_fungible_addresses = CurrencyDao.multi_fungible_addresses(Lend_token.address)
    _s_hash = UnderwriterPoolDao.multi_fungible_currency_hash(
        multi_fungible_addresses[3], Lend_token.address, Z19,
        Borrow_token.address, _strike_price)
    # set shield_currency_price
    shield_currency_minimum_collateral_value = 20 * 10 ** 18
    tx_13_hash = UnderwriterPoolDao.set_shield_currency_minimum_collateral_value(
        Lend_token.address, Z19, Borrow_token.address, _strike_price,
        shield_currency_minimum_collateral_value, transact={'from': owner})
    tx_13_receipt = w3.eth.waitForTransactionReceipt(tx_13_hash)
    assert tx_13_receipt['status'] == 1
    # pool_owner initiates offer of 80 I_tokens from the UnderwriterPool
    # 80 L_tokens burned from UnderwriterPool account
    # 80 I_tokens, 4 S_tokens, and 4 U_tokens minted to UnderwriterPool account
    tx_14_hash = UnderwriterPool.increment_i_currency_supply(
        Z19, Borrow_token.address, _strike_price, 80 * 10 ** 18,
        transact={'from': pool_owner, 'gas': 600000})
    tx_14_receipt = w3.eth.waitForTransactionReceipt(tx_14_hash)
    assert tx_14_receipt['status'] == 1
    # verify multi_fungible_currencies balances of UnderwriterPool
    assert UnderwriterPool.l_currency_balance() == 20 * 10 ** 18
    assert UnderwriterPool.i_currency_balance(Z19, Borrow_token.address, _strike_price) == 80 * 10 ** 18
    assert UnderwriterPool.s_currency_balance(Z19, Borrow_token.address, _strike_price) == 4 * 10 ** 18
    assert UnderwriterPool.u_currency_balance(Z19, Borrow_token.address, _strike_price) == 4 * 10 ** 18
    # pool_owner reduces offer of 60 I_tokens from the UnderwriterPool
    # 60 L_tokens minted to UnderwriterPool account
    # 60 I_tokens, 3 S_tokens, and 3 U_tokens burned from UnderwriterPool account
    tx_14_hash = UnderwriterPool.decrement_i_currency_supply(
        Z19, Borrow_token.address, _strike_price, 60 * 10 ** 18,
        transact={'from': pool_owner, 'gas': 550000})
    tx_14_receipt = w3.eth.waitForTransactionReceipt(tx_14_hash)
    assert tx_14_receipt['status'] == 1
    # verify multi_fungible_currencies balances of UnderwriterPool
    assert UnderwriterPool.l_currency_balance() == 80 * 10 ** 18
    assert UnderwriterPool.i_currency_balance(Z19, Borrow_token.address, _strike_price) == 20 * 10 ** 18
    assert UnderwriterPool.s_currency_balance(Z19, Borrow_token.address, _strike_price) == 1 * 10 ** 18
    assert UnderwriterPool.u_currency_balance(Z19, Borrow_token.address, _strike_price) == 1 * 10 ** 18
