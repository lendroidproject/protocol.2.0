import os

import pytest

from conftest import (
    _initialize_all_daos, ZERO_ADDRESS, EMPTY_BYTES32, Z19
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


def test_avail_loan(w3, get_contract, get_logs,
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
    tx_5_hash = UnderwriterPoolDao.set_offer_registration_fee_lookup(_minimum_fee,
        _minimum_interval, _fee_multiplier, _fee_multiplier_decimals,
        transact={'from': owner})
    tx_5_receipt = w3.eth.waitForTransactionReceipt(tx_5_hash)
    assert tx_5_receipt['status'] == 1
    # set_currency_support for Lend_token in CurrencyDao
    tx_6_hash = CurrencyDao.set_currency_support(Lend_token.address, True,
        transact={'from': owner, 'gas': 1570000})
    tx_6_receipt = w3.eth.waitForTransactionReceipt(tx_6_hash)
    assert tx_6_receipt['status'] == 1
    # set_currency_support for Borrow_token in CurrencyDao
    tx_7_hash = CurrencyDao.set_currency_support(Borrow_token.address, True,
        transact={'from': owner, 'gas': 1570000})
    tx_7_receipt = w3.eth.waitForTransactionReceipt(tx_7_hash)
    assert tx_7_receipt['status'] == 1
    # register_pool for Lend_token
    pool_owner = w3.eth.accounts[1]
    tx_8_hash = UnderwriterPoolDao.register_pool(Lend_token.address,
        'Underwriter Pool A', 'UPA', 50,
        transact={'from': pool_owner, 'gas': 850000})
    tx_8_receipt = w3.eth.waitForTransactionReceipt(tx_8_hash)
    assert tx_8_receipt['status'] == 1
    # get UnderwriterPool contract
    logs_8 = get_logs(tx_8_hash, UnderwriterPoolDao, "PoolRegistered")
    _pool_hash = UnderwriterPoolDao.pool_hash(Lend_token.address, logs_8[0].args._pool_address)
    UnderwriterPool = get_contract(
        'contracts/templates/UnderwriterPoolTemplate1.v.py',
        interfaces=[
            'ERC20', 'ERC1155', 'ERC1155TokenReceiver', 'UnderwriterPoolDao'
        ],
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
    tx_9_hash = LST_token.approve(CurrencyDao.address, UnderwriterPoolDao.offer_registration_fee() * (10 ** 18),
        transact={'from': pool_owner})
    tx_9_receipt = w3.eth.waitForTransactionReceipt(tx_9_hash)
    assert tx_9_receipt['status'] == 1
    # pool_owner registers an expiry : Last Thursday of December 2019, i.e., December 26th, 2019, i.e., Z19
    _strike_price = 200 * 10 ** 18
    tx_10_hash = UnderwriterPool.register_expiry(Z19, Borrow_token.address,
        _strike_price, transact={'from': pool_owner, 'gas': 2600000})
    tx_10_receipt = w3.eth.waitForTransactionReceipt(tx_10_hash)
    assert tx_10_receipt['status'] == 1
    # get L_Lend_token
    L_Lend_token_address = CurrencyDao.currencies__l_currency_address(Lend_token.address)
    L_Lend_token = get_contract(
        'contracts/templates/ERC20Template1.v.py',
        address=L_Lend_token_address
    )
    # get L_Borrow_token
    L_Borrow_token_address = CurrencyDao.currencies__l_currency_address(Borrow_token.address)
    L_Borrow_token = get_contract(
        'contracts/templates/ERC20Template1.v.py',
        address=L_Borrow_token_address
    )
    # assign one of the accounts as a Lender
    Lender = w3.eth.accounts[2]
    # Lender buys 1000 lend token from a 3rd party exchange
    tx_11_hash = Lend_token.transfer(Lender, 1000 * 10 ** 18, transact={'from': owner})
    tx_11_receipt = w3.eth.waitForTransactionReceipt(tx_11_hash)
    assert tx_11_receipt['status'] == 1
    # Lender authorizes CurrencyDao to spend 800 lend currency
    tx_12_hash = Lend_token.approve(CurrencyDao.address, 800 * (10 ** 18),
        transact={'from': Lender})
    tx_12_receipt = w3.eth.waitForTransactionReceipt(tx_12_hash)
    assert tx_12_receipt['status'] == 1
    # Lender deposits 800 Lend_tokens to Currency Pool and gets l_tokens
    tx_13_hash = CurrencyDao.currency_to_l_currency(Lend_token.address, 800 * 10 ** 18,
        transact={'from': Lender, 'gas': 200000})
    tx_13_receipt = w3.eth.waitForTransactionReceipt(tx_13_hash)
    assert tx_13_receipt['status'] == 1
    # Lender purchases UnderwriterPoolCurrency for 800 L_tokens
    # Lender gets 40000 UnderwriterPoolCurrency tokens
    # 800 L_tokens are deposited into UnderwriterPool account
    # verify UnderwriterPool balances of l, i, s, u tokens
    assert UnderwriterPool.l_currency_balance() == 0 * 10 ** 18
    assert UnderwriterPool.i_currency_balance(Z19, Borrow_token.address, _strike_price) == 0 * 10 ** 18
    assert UnderwriterPool.s_currency_balance(Z19, Borrow_token.address, _strike_price) == 0 * 10 ** 18
    assert UnderwriterPool.u_currency_balance(Z19, Borrow_token.address, _strike_price) == 0 * 10 ** 18
    tx_14_hash = UnderwriterPool.purchase_pool_currency(800 * 10 ** 18, transact={'from': Lender})
    tx_14_receipt = w3.eth.waitForTransactionReceipt(tx_14_hash)
    assert tx_14_receipt['status'] == 1
    # verify UnderwriterPool balances of l, i, s, u tokens
    assert UnderwriterPool.l_currency_balance() == 800 * 10 ** 18
    assert UnderwriterPool.i_currency_balance(Z19, Borrow_token.address, _strike_price) == 0 * 10 ** 18
    assert UnderwriterPool.s_currency_balance(Z19, Borrow_token.address, _strike_price) == 0 * 10 ** 18
    assert UnderwriterPool.u_currency_balance(Z19, Borrow_token.address, _strike_price) == 0 * 10 ** 18
    # vefiry shield_currency_price is not set
    multi_fungible_addresses = CurrencyDao.multi_fungible_addresses(Lend_token.address)
    _s_hash = UnderwriterPoolDao.multi_fungible_currency_hash(
        multi_fungible_addresses[3], Lend_token.address, Z19,
        Borrow_token.address, _strike_price)
    _i_hash = UnderwriterPoolDao.multi_fungible_currency_hash(
        multi_fungible_addresses[1], Lend_token.address, Z19, ZERO_ADDRESS, 0)
    # pool_owner initiates offer of 600 I_tokens from the UnderwriterPool
    # 600 L_tokens burned from UnderwriterPool account
    # 600 I_tokens, 3 S_tokens, and 3 U_tokens minted to UnderwriterPool account
    tx_16_hash = UnderwriterPool.increment_i_currency_supply(
        Z19, Borrow_token.address, _strike_price, 600 * 10 ** 18,
        transact={'from': pool_owner, 'gas': 600000})
    tx_16_receipt = w3.eth.waitForTransactionReceipt(tx_16_hash)
    assert tx_16_receipt['status'] == 1
    # verify UnderwriterPool balances of l, i, s, u tokens
    assert UnderwriterPool.l_currency_balance() == 200 * 10 ** 18
    assert UnderwriterPool.i_currency_balance(Z19, Borrow_token.address, _strike_price) == 600 * 10 ** 18
    assert UnderwriterPool.s_currency_balance(Z19, Borrow_token.address, _strike_price) == 3 * 10 ** 18
    assert UnderwriterPool.u_currency_balance(Z19, Borrow_token.address, _strike_price) == 3 * 10 ** 18
    # get I_token
    I_token = get_contract(
        'contracts/templates/ERC1155Template1.v.py',
        interfaces=['ERC1155TokenReceiver'],
        address=CurrencyDao.currencies__i_currency_address(Lend_token.address)
    )
    S_token = get_contract(
        'contracts/templates/ERC1155Template1.v.py',
        interfaces=['ERC1155TokenReceiver'],
        address=CurrencyDao.currencies__s_currency_address(Lend_token.address)
    )
    U_token = get_contract(
        'contracts/templates/ERC1155Template1.v.py',
        interfaces=['ERC1155TokenReceiver'],
        address=CurrencyDao.currencies__u_currency_address(Lend_token.address)
    )
    # assign one of the accounts as a High_Risk_Insurer
    High_Risk_Insurer = w3.eth.accounts[2]
    # High_Risk_Insurer purchases 100 i_tokens from UnderwriterPool
    tx_17_hash = UnderwriterPool.purchase_i_currency(Z19, Borrow_token.address,
        _strike_price, 100 * 10 ** 18, 0, transact={'from': High_Risk_Insurer})
    tx_17_receipt = w3.eth.waitForTransactionReceipt(tx_17_hash)
    assert tx_17_receipt['status'] == 1
    # verify UnderwriterPool balances of l, i, s, u tokens
    assert UnderwriterPool.l_currency_balance() == 200 * 10 ** 18
    assert UnderwriterPool.i_currency_balance(Z19, Borrow_token.address, _strike_price) == 500 * 10 ** 18
    assert UnderwriterPool.s_currency_balance(Z19, Borrow_token.address, _strike_price) == 3 * 10 ** 18
    assert UnderwriterPool.u_currency_balance(Z19, Borrow_token.address, _strike_price) == 3 * 10 ** 18
    # High_Risk_Insurer purchases 2 s_tokens from UnderwriterPool
    tx_18_hash = UnderwriterPool.purchase_s_currency(Z19, Borrow_token.address,
        _strike_price, 2 * 10 ** 18, 0, transact={'from': High_Risk_Insurer})
    tx_18_receipt = w3.eth.waitForTransactionReceipt(tx_18_hash)
    assert tx_18_receipt['status'] == 1
    # verify UnderwriterPool balances of l, i, s, u tokens
    assert UnderwriterPool.l_currency_balance() == 200 * 10 ** 18
    assert UnderwriterPool.i_currency_balance(Z19, Borrow_token.address, _strike_price) == 500 * 10 ** 18
    assert UnderwriterPool.s_currency_balance(Z19, Borrow_token.address, _strike_price) == 1 * 10 ** 18
    assert UnderwriterPool.u_currency_balance(Z19, Borrow_token.address, _strike_price) == 1 * 10 ** 18
    # assign one of the accounts as a Borrower
    Borrower = w3.eth.accounts[3]
    # Borrower purchases 10 Borrow_tokens from a 3rd party exchange
    tx_19_hash = Borrow_token.transfer(Borrower, 10 * 10 ** 18, transact={'from': owner})
    tx_19_receipt = w3.eth.waitForTransactionReceipt(tx_19_hash)
    assert tx_19_receipt['status'] == 1
    assert Borrow_token.balanceOf(Borrower) == 10 * 10 ** 18
    # Borrower authorizes CurrencyDao to spend 2 Borrow_tokens
    tx_20_hash = Borrow_token.approve(CurrencyDao.address, 3 * (10 ** 18),
        transact={'from': Borrower})
    tx_20_receipt = w3.eth.waitForTransactionReceipt(tx_20_hash)
    assert tx_20_receipt['status'] == 1
    # Borrower deposits 2 Borrow_tokens to Currency Pool and gets l_tokens
    tx_21_hash = CurrencyDao.currency_to_l_currency(Borrow_token.address, 3 * 10 ** 18,
        transact={'from': Borrower, 'gas': 200000})
    tx_21_receipt = w3.eth.waitForTransactionReceipt(tx_21_hash)
    assert tx_21_receipt['status'] == 1
    # Borrower wishes to avail a loan of 400 Lend_tokens
    # High_Risk_Insurer authorizes CurrencyDao to spend his S_token
    tx_22_hash = S_token.setApprovalForAll(CurrencyDao.address, True,
        transact={'from': High_Risk_Insurer})
    tx_22_receipt = w3.eth.waitForTransactionReceipt(tx_22_hash)
    assert tx_22_receipt['status'] == 1
    # High_Risk_Insurer authorizes CurrencyDao to spend his I_token
    tx_23_hash = I_token.setApprovalForAll(CurrencyDao.address, True,
        transact={'from': High_Risk_Insurer})
    tx_23_receipt = w3.eth.waitForTransactionReceipt(tx_23_hash)
    assert tx_23_receipt['status'] == 1
    # High_Risk_Insurer sets an offer of 2 s_tokens for 20 i_tokens
    assert PositionRegistry.last_offer_index() == 0
    tx_24_hash = PositionRegistry.create_offer(
        Lend_token.address, Z19, Borrow_token.address, _strike_price,
        2, 20, 5 * 10 ** 15,
        transact={'from': High_Risk_Insurer, 'gas': 450000})
    tx_24_receipt = w3.eth.waitForTransactionReceipt(tx_24_hash)
    assert tx_24_receipt['status'] == 1
    assert PositionRegistry.last_offer_index() == 1
    assert PositionRegistry.offers__creator(0) == High_Risk_Insurer
    assert PositionRegistry.offers__s_quantity(0) == 2
    assert PositionRegistry.offers__i_quantity(0) == 20
    assert PositionRegistry.offers__i_unit_price_in_wei(0) == 5 * 10 ** 15
    # verify i_token, s_token and l_token balances of MarketDao
    assert I_token.balanceOf(
        MarketDao.address,
        UnderwriterPoolDao.multi_fungible_currencies__token_id(_i_hash)
    ) == 0
    assert S_token.balanceOf(
        MarketDao.address,
        UnderwriterPoolDao.multi_fungible_currencies__token_id(_s_hash)
    ) == 0
    # verify i_token, s_token and l_token balances of High_Risk_Insurer
    assert I_token.balanceOf(
        High_Risk_Insurer,
        UnderwriterPoolDao.multi_fungible_currencies__token_id(_i_hash)
    ) == 100 * 10 ** 18
    assert S_token.balanceOf(
        High_Risk_Insurer,
        UnderwriterPoolDao.multi_fungible_currencies__token_id(_s_hash)
    ) == 2 * 10 ** 18
    # verify L_Borrow_token balance of MarketDao
    assert L_Borrow_token.balanceOf(MarketDao.address) == 0
    # verify L_Borrow_token balance of Borrower
    assert L_Borrow_token.balanceOf(Borrower) == 3 * 10 ** 18
    # verify Lend_token balance of Borrower
    assert Lend_token.balanceOf(Borrower) == 0
    # Borrower purchases this offer for the amount of 0.1 ETH
    # 20 i_tokens and 2 s_tokens are transferred from High_Risk_Insurer account to MarketDao
    tx_25_hash = PositionRegistry.avail_loan(0,
        transact={'from': Borrower, 'value': 10 ** 17, 'gas': 950000})
    tx_25_receipt = w3.eth.waitForTransactionReceipt(tx_25_hash)
    assert tx_25_receipt['status'] == 1
    # verify i_token, s_token and l_token balances of MarketDao
    assert I_token.balanceOf(
        Borrower,
        UnderwriterPoolDao.multi_fungible_currencies__token_id(_i_hash)
    ) == 20 * 10 ** 18
    assert S_token.balanceOf(
        MarketDao.address,
        UnderwriterPoolDao.multi_fungible_currencies__token_id(_s_hash)
    ) == 2 * 10 ** 18
    # verify i_token, s_token and l_token balances of High_Risk_Insurer
    assert I_token.balanceOf(
        High_Risk_Insurer,
        UnderwriterPoolDao.multi_fungible_currencies__token_id(_i_hash)
    ) == 80 * 10 ** 18
    assert S_token.balanceOf(
        High_Risk_Insurer,
        UnderwriterPoolDao.multi_fungible_currencies__token_id(_s_hash)
    ) == 0
    # verify L_Borrow_token balance of MarketDao
    assert L_Borrow_token.balanceOf(MarketDao.address) == 2 * 10 ** 18
    # verify L_Borrow_token balance of Borrower
    assert L_Borrow_token.balanceOf(Borrower) == 1 * 10 ** 18
    # verify Lend_token balance of Borrower
    assert Lend_token.balanceOf(Borrower) == 400 * 10 ** 18


def test_repay_loan(w3, get_contract, get_logs,
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
    tx_5_hash = UnderwriterPoolDao.set_offer_registration_fee_lookup(_minimum_fee,
        _minimum_interval, _fee_multiplier, _fee_multiplier_decimals,
        transact={'from': owner})
    tx_5_receipt = w3.eth.waitForTransactionReceipt(tx_5_hash)
    assert tx_5_receipt['status'] == 1
    # set_currency_support for Lend_token in CurrencyDao
    tx_6_hash = CurrencyDao.set_currency_support(Lend_token.address, True,
        transact={'from': owner, 'gas': 1570000})
    tx_6_receipt = w3.eth.waitForTransactionReceipt(tx_6_hash)
    assert tx_6_receipt['status'] == 1
    # set_currency_support for Borrow_token in CurrencyDao
    tx_7_hash = CurrencyDao.set_currency_support(Borrow_token.address, True,
        transact={'from': owner, 'gas': 1570000})
    tx_7_receipt = w3.eth.waitForTransactionReceipt(tx_7_hash)
    assert tx_7_receipt['status'] == 1
    # register_pool for Lend_token
    pool_owner = w3.eth.accounts[1]
    tx_8_hash = UnderwriterPoolDao.register_pool(Lend_token.address,
        'Underwriter Pool A', 'UPA', 50,
        transact={'from': pool_owner, 'gas': 850000})
    tx_8_receipt = w3.eth.waitForTransactionReceipt(tx_8_hash)
    assert tx_8_receipt['status'] == 1
    # get UnderwriterPool contract
    logs_8 = get_logs(tx_8_hash, UnderwriterPoolDao, "PoolRegistered")
    _pool_hash = UnderwriterPoolDao.pool_hash(Lend_token.address, logs_8[0].args._pool_address)
    UnderwriterPool = get_contract(
        'contracts/templates/UnderwriterPoolTemplate1.v.py',
        interfaces=[
            'ERC20', 'ERC1155', 'ERC1155TokenReceiver', 'UnderwriterPoolDao'
        ],
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
    tx_9_hash = LST_token.approve(CurrencyDao.address, UnderwriterPoolDao.offer_registration_fee() * (10 ** 18),
        transact={'from': pool_owner})
    tx_9_receipt = w3.eth.waitForTransactionReceipt(tx_9_hash)
    assert tx_9_receipt['status'] == 1
    # pool_owner registers an expiry : Last Thursday of December 2019, i.e., December 26th, 2019, i.e., Z19
    _strike_price = 200 * 10 ** 18
    tx_10_hash = UnderwriterPool.register_expiry(Z19, Borrow_token.address,
        _strike_price, transact={'from': pool_owner, 'gas': 2600000})
    tx_10_receipt = w3.eth.waitForTransactionReceipt(tx_10_hash)
    assert tx_10_receipt['status'] == 1
    # get L_Lend_token
    L_Lend_token_address = CurrencyDao.currencies__l_currency_address(Lend_token.address)
    L_Lend_token = get_contract(
        'contracts/templates/ERC20Template1.v.py',
        address=L_Lend_token_address
    )
    # get L_Borrow_token
    L_Borrow_token_address = CurrencyDao.currencies__l_currency_address(Borrow_token.address)
    L_Borrow_token = get_contract(
        'contracts/templates/ERC20Template1.v.py',
        address=L_Borrow_token_address
    )
    # assign one of the accounts as a Lender
    Lender = w3.eth.accounts[2]
    # Lender buys 1000 lend token from a 3rd party exchange
    tx_11_hash = Lend_token.transfer(Lender, 1000 * 10 ** 18, transact={'from': owner})
    tx_11_receipt = w3.eth.waitForTransactionReceipt(tx_11_hash)
    assert tx_11_receipt['status'] == 1
    # Lender authorizes CurrencyDao to spend 800 lend currency
    tx_12_hash = Lend_token.approve(CurrencyDao.address, 800 * (10 ** 18),
        transact={'from': Lender})
    tx_12_receipt = w3.eth.waitForTransactionReceipt(tx_12_hash)
    assert tx_12_receipt['status'] == 1
    # Lender deposits 800 Lend_tokens to Currency Pool and gets l_tokens
    tx_13_hash = CurrencyDao.currency_to_l_currency(Lend_token.address, 800 * 10 ** 18,
        transact={'from': Lender, 'gas': 200000})
    tx_13_receipt = w3.eth.waitForTransactionReceipt(tx_13_hash)
    assert tx_13_receipt['status'] == 1
    # Lender purchases UnderwriterPoolCurrency for 800 L_tokens
    # Lender gets 40000 UnderwriterPoolCurrency tokens
    # 800 L_tokens are deposited into UnderwriterPool account
    tx_14_hash = UnderwriterPool.purchase_pool_currency(800 * 10 ** 18, transact={'from': Lender})
    tx_14_receipt = w3.eth.waitForTransactionReceipt(tx_14_hash)
    assert tx_14_receipt['status'] == 1
    # vefiry shield_currency_price is not set
    multi_fungible_addresses = CurrencyDao.multi_fungible_addresses(Lend_token.address)
    _s_hash = UnderwriterPoolDao.multi_fungible_currency_hash(
        multi_fungible_addresses[3], Lend_token.address, Z19,
        Borrow_token.address, _strike_price)
    _i_hash = UnderwriterPoolDao.multi_fungible_currency_hash(
        multi_fungible_addresses[1], Lend_token.address, Z19, ZERO_ADDRESS, 0)
    # pool_owner initiates offer of 600 I_tokens from the UnderwriterPool
    # 600 L_tokens burned from UnderwriterPool account
    # 600 I_tokens, 3 S_tokens, and 3 U_tokens minted to UnderwriterPool account
    tx_16_hash = UnderwriterPool.increment_i_currency_supply(
        Z19, Borrow_token.address, _strike_price, 600 * 10 ** 18,
        transact={'from': pool_owner, 'gas': 600000})
    tx_16_receipt = w3.eth.waitForTransactionReceipt(tx_16_hash)
    assert tx_16_receipt['status'] == 1
    # get I_token
    I_token = get_contract(
        'contracts/templates/ERC1155Template1.v.py',
        interfaces=['ERC1155TokenReceiver'],
        address=CurrencyDao.currencies__i_currency_address(Lend_token.address)
    )
    S_token = get_contract(
        'contracts/templates/ERC1155Template1.v.py',
        interfaces=['ERC1155TokenReceiver'],
        address=CurrencyDao.currencies__s_currency_address(Lend_token.address)
    )
    U_token = get_contract(
        'contracts/templates/ERC1155Template1.v.py',
        interfaces=['ERC1155TokenReceiver'],
        address=CurrencyDao.currencies__u_currency_address(Lend_token.address)
    )
    # assign one of the accounts as a High_Risk_Insurer
    High_Risk_Insurer = w3.eth.accounts[2]
    # High_Risk_Insurer purchases 100 i_tokens from UnderwriterPool
    tx_17_hash = UnderwriterPool.purchase_i_currency(Z19, Borrow_token.address,
        _strike_price, 100 * 10 ** 18, 0, transact={'from': High_Risk_Insurer})
    tx_17_receipt = w3.eth.waitForTransactionReceipt(tx_17_hash)
    assert tx_17_receipt['status'] == 1
    # High_Risk_Insurer purchases 2 s_tokens from UnderwriterPool
    tx_18_hash = UnderwriterPool.purchase_s_currency(Z19, Borrow_token.address,
        _strike_price, 2 * 10 ** 18, 0, transact={'from': High_Risk_Insurer})
    tx_18_receipt = w3.eth.waitForTransactionReceipt(tx_18_hash)
    assert tx_18_receipt['status'] == 1
    # assign one of the accounts as a Borrower
    Borrower = w3.eth.accounts[3]
    # Borrower purchases 10 Borrow_tokens from a 3rd party exchange
    tx_19_hash = Borrow_token.transfer(Borrower, 10 * 10 ** 18, transact={'from': owner})
    tx_19_receipt = w3.eth.waitForTransactionReceipt(tx_19_hash)
    assert tx_19_receipt['status'] == 1
    assert Borrow_token.balanceOf(Borrower) == 10 * 10 ** 18
    # Borrower authorizes CurrencyDao to spend 2 Borrow_tokens
    tx_20_hash = Borrow_token.approve(CurrencyDao.address, 3 * (10 ** 18),
        transact={'from': Borrower})
    tx_20_receipt = w3.eth.waitForTransactionReceipt(tx_20_hash)
    assert tx_20_receipt['status'] == 1
    # Borrower deposits 2 Borrow_tokens to Currency Pool and gets l_tokens
    tx_21_hash = CurrencyDao.currency_to_l_currency(Borrow_token.address, 3 * 10 ** 18,
        transact={'from': Borrower, 'gas': 200000})
    tx_21_receipt = w3.eth.waitForTransactionReceipt(tx_21_hash)
    assert tx_21_receipt['status'] == 1
    # Borrower wishes to avail a loan of 400 Lend_tokens
    # High_Risk_Insurer authorizes CurrencyDao to spend his S_token
    tx_22_hash = S_token.setApprovalForAll(CurrencyDao.address, True,
        transact={'from': High_Risk_Insurer})
    tx_22_receipt = w3.eth.waitForTransactionReceipt(tx_22_hash)
    assert tx_22_receipt['status'] == 1
    # High_Risk_Insurer authorizes CurrencyDao to spend his I_token
    tx_23_hash = I_token.setApprovalForAll(CurrencyDao.address, True,
        transact={'from': High_Risk_Insurer})
    tx_23_receipt = w3.eth.waitForTransactionReceipt(tx_23_hash)
    assert tx_23_receipt['status'] == 1
    # High_Risk_Insurer sets an offer of 2 s_tokens for 20 i_tokens
    assert PositionRegistry.last_offer_index() == 0
    tx_24_hash = PositionRegistry.create_offer(
        Lend_token.address, Z19, Borrow_token.address, _strike_price,
        2, 20, 5 * 10 ** 15,
        transact={'from': High_Risk_Insurer, 'gas': 450000})
    tx_24_receipt = w3.eth.waitForTransactionReceipt(tx_24_hash)
    assert tx_24_receipt['status'] == 1
    # Borrower purchases this offer for the amount of 0.1 ETH
    # 20 i_tokens and 2 s_tokens are transferred from High_Risk_Insurer account to MarketDao
    tx_25_hash = PositionRegistry.avail_loan(0,
        transact={'from': Borrower, 'value': 10 ** 17, 'gas': 950000})
    tx_25_receipt = w3.eth.waitForTransactionReceipt(tx_25_hash)
    assert tx_25_receipt['status'] == 1
    # verify Lend_token balance of Borrower
    assert Lend_token.balanceOf(Borrower) == 400 * 10 ** 18
    # Borrower authorizes CurrencyDao to spend 400 Lend_tokens
    tx_26_hash = Lend_token.approve(CurrencyDao.address, 400 * (10 ** 18),
        transact={'from': Borrower})
    tx_26_receipt = w3.eth.waitForTransactionReceipt(tx_26_hash)
    assert tx_26_receipt['status'] == 1
    # Borrower repays loan
    position_id = PositionRegistry.borrow_position(Borrower, PositionRegistry.borrow_position_count(Borrower))
    tx_27_hash = PositionRegistry.repay_loan(position_id, transact={'from': Borrower})
    tx_27_receipt = w3.eth.waitForTransactionReceipt(tx_27_hash)
    assert tx_27_receipt['status'] == 1
    # verify L_Borrow_token balance of Borrower
    assert L_Borrow_token.balanceOf(Borrower) == 3 * 10 ** 18
    # verify Lend_token balance of Borrower
    assert Lend_token.balanceOf(Borrower) == 0
