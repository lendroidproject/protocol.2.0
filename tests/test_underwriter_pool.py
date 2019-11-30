import os

import pytest

from vyper import (
    compiler,
)

from conftest import (
    _initialize_all_daos, ZERO_ADDRESS, EMPTY_BYTES32, Z19,
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
    #. InterestPool_library
    #. InterestPoolDao
    #. UnderwriterPool_library
    #. UnderwriterPoolDao
    #. CollateralAuctionGraph_Library
    #. CollateralAuctionDao
    #. ShieldPayoutDao
    #. PositionRegistry
    #. MarketDao
"""


def test_purchase_i_currency(w3, get_contract, get_logs,
        LST_token, Lend_token, Borrow_token, Malicious_token,
        ERC20_library, ERC1155_library,
        CurrencyPool_library, CurrencyDao,
        InterestPool_library, InterestPoolDao,
        UnderwriterPool_library, UnderwriterPoolDao,
        CollateralAuctionGraph_Library, CollateralAuctionDao,
        ShieldPayoutDao,
        PositionRegistry,
        PriceFeed,
        PriceOracle,
        MarketDao
    ):
    owner = w3.eth.accounts[0]
    _initialize_all_daos(owner, w3,
        LST_token, Lend_token, Borrow_token,
        ERC20_library, ERC1155_library,
        CurrencyPool_library, CurrencyDao,
        InterestPool_library, InterestPoolDao,
        UnderwriterPool_library, UnderwriterPoolDao,
        CollateralAuctionGraph_Library, CollateralAuctionDao,
        ShieldPayoutDao,
        PositionRegistry,
        PriceOracle,
        MarketDao
    )
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
        _strike_price, transact={'from': pool_owner, 'gas': 2600000})
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
    # lender authorizes CurrencyDao to spend 800 lend currency
    tx_10_hash = Lend_token.approve(CurrencyDao.address, 800 * (10 ** 18),
        transact={'from': lender})
    tx_10_receipt = w3.eth.waitForTransactionReceipt(tx_10_hash)
    assert tx_10_receipt['status'] == 1
    # lender deposits Lend_token to Currency Pool and gets l_tokens
    tx_11_hash = CurrencyDao.currency_to_l_currency(Lend_token.address, 600 * 10 ** 18,
        transact={'from': lender, 'gas': 200000})
    tx_11_receipt = w3.eth.waitForTransactionReceipt(tx_11_hash)
    assert tx_11_receipt['status'] == 1
    # lender purchases UnderwriterPoolCurrency for 600 L_tokens
    # lender gets 30000 UnderwriterPoolCurrency tokens
    # 600 L_tokens are deposited into UnderwriterPool account
    tx_12_hash = UnderwriterPool.purchase_pool_currency(600 * 10 ** 18, transact={'from': lender})
    tx_12_receipt = w3.eth.waitForTransactionReceipt(tx_12_hash)
    assert tx_12_receipt['status'] == 1
    assert UnderwriterPool.l_currency_balance() == 600 * 10 ** 18
    multi_fungible_addresses = CurrencyDao.multi_fungible_addresses(Lend_token.address)
    _s_hash = UnderwriterPoolDao.multi_fungible_currency_hash(
        multi_fungible_addresses[3], Lend_token.address, Z19,
        Borrow_token.address, _strike_price)
    # pool_owner initiates offer of 400 I_tokens from the UnderwriterPool
    # 400 L_tokens burned from UnderwriterPool account
    # 400 I_tokens, 2 S_tokens, and 2 U_tokens minted to UnderwriterPool account
    tx_14_hash = UnderwriterPool.increment_i_currency_supply(
        Z19, Borrow_token.address, _strike_price, 400 * 10 ** 18,
        transact={'from': pool_owner, 'gas': 600000})
    tx_14_receipt = w3.eth.waitForTransactionReceipt(tx_14_hash)
    assert tx_14_receipt['status'] == 1
    # get I_token
    I_token = get_contract(
        'contracts/templates/ERC1155Template2.v.py',
        interfaces=['ERC1155TokenReceiver'],
        address=CurrencyDao.currencies__i_currency_address(Lend_token.address)
    )
    # assign one of the accounts as a High_Risk_Insurer
    High_Risk_Insurer = w3.eth.accounts[2]
    # verify UnderwriterPool balances of l, i, s, u tokens
    assert UnderwriterPool.l_currency_balance() == 200 * 10 ** 18
    assert UnderwriterPool.i_currency_balance(Z19, Borrow_token.address, _strike_price) == 400 * 10 ** 18
    assert UnderwriterPool.s_currency_balance(Z19, Borrow_token.address, _strike_price) == 2 * 10 ** 18
    assert UnderwriterPool.u_currency_balance(Z19, Borrow_token.address, _strike_price) == 2 * 10 ** 18
    # verify High_Risk_Insurer balance of i tokens
    _expiry_hash = UnderwriterPool.expiry_hash(Z19, Borrow_token.address,
        _strike_price)
    assert I_token.balanceOf(High_Risk_Insurer, UnderwriterPool.expiries__i_currency_id(_expiry_hash)) == 0
    # High_Risk_Insurer purchases 50 i_tokens from UnderwriterPool
    tx_15_hash = UnderwriterPool.purchase_i_currency(Z19, Borrow_token.address,
        _strike_price, 50 * 10 ** 18, 0, transact={'from': High_Risk_Insurer})
    tx_15_receipt = w3.eth.waitForTransactionReceipt(tx_15_hash)
    assert tx_15_receipt['status'] == 1
    # verify UnderwriterPool balances of l, i, s, u tokens
    assert UnderwriterPool.l_currency_balance() == 200 * 10 ** 18
    assert UnderwriterPool.i_currency_balance(Z19, Borrow_token.address, _strike_price) == 350 * 10 ** 18
    assert UnderwriterPool.s_currency_balance(Z19, Borrow_token.address, _strike_price) == 2 * 10 ** 18
    assert UnderwriterPool.u_currency_balance(Z19, Borrow_token.address, _strike_price) == 2 * 10 ** 18
    # verify High_Risk_Insurer balance of i tokens
    assert I_token.balanceOf(High_Risk_Insurer, UnderwriterPool.expiries__i_currency_id(_expiry_hash)) == 50 * 10 ** 18


def test_purchase_s_currency(w3, get_contract, get_logs,
        LST_token, Lend_token, Borrow_token, Malicious_token,
        ERC20_library, ERC1155_library,
        CurrencyPool_library, CurrencyDao,
        InterestPool_library, InterestPoolDao,
        UnderwriterPool_library, UnderwriterPoolDao,
        CollateralAuctionGraph_Library, CollateralAuctionDao,
        ShieldPayoutDao,
        PositionRegistry,
        PriceFeed,
        PriceOracle,
        MarketDao
    ):
    owner = w3.eth.accounts[0]
    _initialize_all_daos(owner, w3,
        LST_token, Lend_token, Borrow_token,
        ERC20_library, ERC1155_library,
        CurrencyPool_library, CurrencyDao,
        InterestPool_library, InterestPoolDao,
        UnderwriterPool_library, UnderwriterPoolDao,
        CollateralAuctionGraph_Library, CollateralAuctionDao,
        ShieldPayoutDao,
        PositionRegistry,
        PriceOracle,
        MarketDao
    )
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
        _strike_price, transact={'from': pool_owner, 'gas': 2600000})
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
    # lender authorizes CurrencyDao to spend 800 lend currency
    tx_10_hash = Lend_token.approve(CurrencyDao.address, 1000 * (10 ** 18),
        transact={'from': lender})
    tx_10_receipt = w3.eth.waitForTransactionReceipt(tx_10_hash)
    assert tx_10_receipt['status'] == 1
    # lender deposits Lend_token to Currency Pool and gets l_tokens
    tx_11_hash = CurrencyDao.currency_to_l_currency(Lend_token.address, 800 * 10 ** 18,
        transact={'from': lender, 'gas': 200000})
    tx_11_receipt = w3.eth.waitForTransactionReceipt(tx_11_hash)
    assert tx_11_receipt['status'] == 1
    # lender purchases UnderwriterPoolCurrency for 800 L_tokens
    # lender gets 40000 UnderwriterPoolCurrency tokens
    # 800 L_tokens are deposited into UnderwriterPool account
    tx_12_hash = UnderwriterPool.purchase_pool_currency(800 * 10 ** 18, transact={'from': lender})
    tx_12_receipt = w3.eth.waitForTransactionReceipt(tx_12_hash)
    assert tx_12_receipt['status'] == 1
    assert UnderwriterPool.l_currency_balance() == 800 * 10 ** 18
    # vefiry shield_currency_price is not set
    multi_fungible_addresses = CurrencyDao.multi_fungible_addresses(Lend_token.address)
    _s_hash = UnderwriterPoolDao.multi_fungible_currency_hash(
        multi_fungible_addresses[3], Lend_token.address, Z19,
        Borrow_token.address, _strike_price)
    # pool_owner initiates offer of 600 I_tokens from the UnderwriterPool
    # 600 L_tokens burned from UnderwriterPool account
    # 600 I_tokens, 3 S_tokens, and 3 U_tokens minted to UnderwriterPool account
    tx_14_hash = UnderwriterPool.increment_i_currency_supply(
        Z19, Borrow_token.address, _strike_price, 600 * 10 ** 18,
        transact={'from': pool_owner, 'gas': 600000})
    tx_14_receipt = w3.eth.waitForTransactionReceipt(tx_14_hash)
    assert tx_14_receipt['status'] == 1
    # get S_token and U_token
    S_token = get_contract(
        'contracts/templates/ERC1155Template2.v.py',
        interfaces=['ERC1155TokenReceiver'],
        address=CurrencyDao.currencies__s_currency_address(Lend_token.address)
    )
    U_token = get_contract(
        'contracts/templates/ERC1155Template2.v.py',
        interfaces=['ERC1155TokenReceiver'],
        address=CurrencyDao.currencies__u_currency_address(Lend_token.address)
    )
    # assign one of the accounts as a High_Risk_Insurer
    High_Risk_Insurer = w3.eth.accounts[2]
    # verify UnderwriterPool balances of l, i, s, u tokens
    assert UnderwriterPool.l_currency_balance() == 200 * 10 ** 18
    assert UnderwriterPool.i_currency_balance(Z19, Borrow_token.address, _strike_price) == 600 * 10 ** 18
    assert UnderwriterPool.s_currency_balance(Z19, Borrow_token.address, _strike_price) == 3 * 10 ** 18
    assert UnderwriterPool.u_currency_balance(Z19, Borrow_token.address, _strike_price) == 3 * 10 ** 18
    # verify High_Risk_Insurer balance of s and u tokens
    _expiry_hash = UnderwriterPool.expiry_hash(Z19, Borrow_token.address,
        _strike_price)
    assert S_token.balanceOf(High_Risk_Insurer, UnderwriterPool.expiries__i_currency_id(_expiry_hash)) == 0
    assert U_token.balanceOf(High_Risk_Insurer, UnderwriterPool.expiries__i_currency_id(_expiry_hash)) == 0
    # High_Risk_Insurer purchases 2 s_tokens from UnderwriterPool
    tx_15_hash = UnderwriterPool.purchase_s_currency(Z19, Borrow_token.address,
        _strike_price, 2 * 10 ** 18, 0, transact={'from': High_Risk_Insurer})
    tx_15_receipt = w3.eth.waitForTransactionReceipt(tx_15_hash)
    assert tx_15_receipt['status'] == 1
    # verify UnderwriterPool balances of l, i, s, u tokens
    assert UnderwriterPool.l_currency_balance() == 200 * 10 ** 18
    assert UnderwriterPool.i_currency_balance(Z19, Borrow_token.address, _strike_price) == 600 * 10 ** 18
    assert UnderwriterPool.s_currency_balance(Z19, Borrow_token.address, _strike_price) == 1 * 10 ** 18
    assert UnderwriterPool.u_currency_balance(Z19, Borrow_token.address, _strike_price) == 3 * 10 ** 18
    # verify High_Risk_Insurer balance of s and u tokens
    assert S_token.balanceOf(High_Risk_Insurer, UnderwriterPool.expiries__i_currency_id(_expiry_hash)) == 2 * 10 ** 18
    assert U_token.balanceOf(High_Risk_Insurer, UnderwriterPool.expiries__i_currency_id(_expiry_hash)) == 0
