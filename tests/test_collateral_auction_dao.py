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


def test_create_graph(w3, get_contract, get_logs,
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
    # verify auction graph does not exist
    _loan_market_hash = CollateralAuctionDao.loan_market_hash(
        Lend_token.address, Z19, Borrow_token.address
    )
    assert CollateralAuctionDao.graphs(_loan_market_hash) in (EMPTY_BYTES32, None)
    assert MarketDao.loan_markets__collateral_auction_graph_address(_loan_market_hash) in (EMPTY_BYTES32, None)
    tx_10_hash = UnderwriterPool.register_expiry(Z19, Borrow_token.address,
        _strike_price, transact={'from': pool_owner, 'gas': 2600000})
    tx_10_receipt = w3.eth.waitForTransactionReceipt(tx_10_hash)
    assert tx_10_receipt['status'] == 1
    assert not CollateralAuctionDao.graphs(_loan_market_hash) in (EMPTY_BYTES32, None)
    assert not MarketDao.loan_markets__collateral_auction_graph_address(_loan_market_hash) in (EMPTY_BYTES32, None)
    assert CollateralAuctionDao.graphs(_loan_market_hash) == MarketDao.loan_markets__collateral_auction_graph_address(_loan_market_hash)
