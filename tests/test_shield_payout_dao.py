import os

from web3 import Web3

import pytest

from conftest import (
    ZERO_ADDRESS, EMPTY_BYTES32, Z19
)


# """
#     The tests in this file use the following deployed contracts, aka
#     fixtures from conftest:
#     #. LST_token
#     #. Lend_token
#     #. Borrow_token
#     #. Malicious_token
#     #. ERC20_library
#     #. ERC1155_library
#     #. CurrencyPool_library
#     #. CurrencyDao
#     #. InterestPool_library
#     #. InterestPoolDao
#     #. UnderwriterPool_library
#     #. UnderwriterPoolDao
#     #. CollateralAuctionGraph_Library
#     #. CollateralAuctionDao
#     #. ShieldPayoutDao
#     #. PositionRegistry
#     #. MarketDao
# """
#
#
# def test_register_shield_market(w3, get_contract, get_logs,
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
#     tx_5_hash = UnderwriterPoolDao.set_offer_registration_fee_lookup(_minimum_fee,
#         _minimum_interval, _fee_multiplier, _fee_multiplier_decimals,
#         transact={'from': owner})
#     tx_5_receipt = w3.eth.waitForTransactionReceipt(tx_5_hash)
#     assert tx_5_receipt['status'] == 1
#     # set_currency_support for Lend_token in CurrencyDao
#     tx_6_hash = CurrencyDao.set_currency_support(Lend_token.address, True,
#         transact={'from': owner, 'gas': 1570000})
#     tx_6_receipt = w3.eth.waitForTransactionReceipt(tx_6_hash)
#     assert tx_6_receipt['status'] == 1
#     # set_currency_support for Borrow_token in CurrencyDao
#     tx_7_hash = CurrencyDao.set_currency_support(Borrow_token.address, True,
#         transact={'from': owner, 'gas': 1570000})
#     tx_7_receipt = w3.eth.waitForTransactionReceipt(tx_7_hash)
#     assert tx_7_receipt['status'] == 1
#     # register_pool for Lend_token
#     pool_owner = w3.eth.accounts[1]
#     tx_8_hash = UnderwriterPoolDao.register_pool(Lend_token.address,
#         'Underwriter Pool A', 'UPA', 50,
#         transact={'from': pool_owner, 'gas': 850000})
#     tx_8_receipt = w3.eth.waitForTransactionReceipt(tx_8_hash)
#     assert tx_8_receipt['status'] == 1
#     # get UnderwriterPool contract
#     logs_8 = get_logs(tx_8_hash, UnderwriterPoolDao, "PoolRegistered")
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
#     tx_9_hash = LST_token.approve(CurrencyDao.address, Web3.toWei(UnderwriterPoolDao.offer_registration_fee(), 'ether'),
#         transact={'from': pool_owner})
#     tx_9_receipt = w3.eth.waitForTransactionReceipt(tx_9_hash)
#     assert tx_9_receipt['status'] == 1
#     # pool_owner registers an expiry : Last Thursday of December 2019, i.e., December 26th, 2019, i.e., Z19
#     _strike_price = Web3.toWei(200, 'ether')
#     # verify auction graph does not exist
#     _shield_market_hash = ShieldPayoutDao.shield_market_hash(
#         Lend_token.address, Z19, Borrow_token.address, _strike_price
#     )
#     assert ShieldPayoutDao.registered_shield_markets(_shield_market_hash) == False
#     tx_10_hash = UnderwriterPool.register_expiry(Z19, Borrow_token.address,
#         _strike_price, transact={'from': pool_owner, 'gas': 2600000})
#     tx_10_receipt = w3.eth.waitForTransactionReceipt(tx_10_hash)
#     assert tx_10_receipt['status'] == 1
#     assert ShieldPayoutDao.registered_shield_markets(_shield_market_hash) == True
#
#
# def test_exercise_shield_currency_for_market_settlement_without_auction(w3, get_contract, get_logs, time_travel,
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
#     tx_5_hash = UnderwriterPoolDao.set_offer_registration_fee_lookup(_minimum_fee,
#         _minimum_interval, _fee_multiplier, _fee_multiplier_decimals,
#         transact={'from': owner})
#     tx_5_receipt = w3.eth.waitForTransactionReceipt(tx_5_hash)
#     assert tx_5_receipt['status'] == 1
#     # set_currency_support for Lend_token in CurrencyDao
#     tx_6_hash = CurrencyDao.set_currency_support(Lend_token.address, True,
#         transact={'from': owner, 'gas': 1570000})
#     tx_6_receipt = w3.eth.waitForTransactionReceipt(tx_6_hash)
#     assert tx_6_receipt['status'] == 1
#     # set_currency_support for Borrow_token in CurrencyDao
#     tx_7_hash = CurrencyDao.set_currency_support(Borrow_token.address, True,
#         transact={'from': owner, 'gas': 1570000})
#     tx_7_receipt = w3.eth.waitForTransactionReceipt(tx_7_hash)
#     assert tx_7_receipt['status'] == 1
#     # register_pool for Lend_token
#     pool_owner = w3.eth.accounts[1]
#     tx_8_hash = UnderwriterPoolDao.register_pool(Lend_token.address,
#         'Underwriter Pool A', 'UPA', 50,
#         transact={'from': pool_owner, 'gas': 850000})
#     tx_8_receipt = w3.eth.waitForTransactionReceipt(tx_8_hash)
#     assert tx_8_receipt['status'] == 1
#     # get UnderwriterPool contract
#     logs_8 = get_logs(tx_8_hash, UnderwriterPoolDao, "PoolRegistered")
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
#     tx_9_hash = LST_token.approve(CurrencyDao.address, Web3.toWei(UnderwriterPoolDao.offer_registration_fee(), 'ether'),
#         transact={'from': pool_owner})
#     tx_9_receipt = w3.eth.waitForTransactionReceipt(tx_9_hash)
#     assert tx_9_receipt['status'] == 1
#     # pool_owner registers an expiry : Last Thursday of December 2019, i.e., December 26th, 2019, i.e., Z19
#     _strike_price = Web3.toWei(200, 'ether')
#     tx_10_hash = UnderwriterPool.register_expiry(Z19, Borrow_token.address,
#         _strike_price, transact={'from': pool_owner, 'gas': 2600000})
#     tx_10_receipt = w3.eth.waitForTransactionReceipt(tx_10_hash)
#     assert tx_10_receipt['status'] == 1
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
#     tx_11_hash = Lend_token.transfer(Lender, Web3.toWei(1000, 'ether'), transact={'from': owner})
#     tx_11_receipt = w3.eth.waitForTransactionReceipt(tx_11_hash)
#     assert tx_11_receipt['status'] == 1
#     # Lender authorizes CurrencyDao to spend 800 lend currency
#     tx_12_hash = Lend_token.approve(CurrencyDao.address, Web3.toWei(800, 'ether'),
#         transact={'from': Lender})
#     tx_12_receipt = w3.eth.waitForTransactionReceipt(tx_12_hash)
#     assert tx_12_receipt['status'] == 1
#     # Lender deposits 800 Lend_tokens to Currency Pool and gets l_tokens
#     assert L_currency_token.totalSupply() == 0
#     assert Lend_token.balanceOf(CurrencyDao.pools__pool_address(_currency_pool_hash)) == 0
#     tx_13_hash = CurrencyDao.currency_to_l_currency(Lend_token.address, Web3.toWei(800, 'ether'),
#         transact={'from': Lender, 'gas': 200000})
#     tx_13_receipt = w3.eth.waitForTransactionReceipt(tx_13_hash)
#     assert tx_13_receipt['status'] == 1
#     # verify l_lend_currency supply, l_lend_currency balance and lend_currency balance
#     assert L_currency_token.totalSupply() == Web3.toWei(800, 'ether')
#     assert L_currency_token.balanceOf(Lender) == Web3.toWei(800, 'ether')
#     assert L_currency_token.balanceOf(UnderwriterPool.address) == 0
#     # Lender purchases UnderwriterPoolCurrency for 800 L_tokens
#     # Lender gets 40000 UnderwriterPoolCurrency tokens
#     # 800 L_tokens are deposited into UnderwriterPool account
#     tx_14_hash = UnderwriterPool.purchase_pool_currency(Web3.toWei(800, 'ether'), transact={'from': Lender})
#     tx_14_receipt = w3.eth.waitForTransactionReceipt(tx_14_hash)
#     assert tx_14_receipt['status'] == 1
#     # verify l_lend_currency supply, l_lend_currency balance and lend_currency balance
#     assert L_currency_token.totalSupply() == Web3.toWei(800, 'ether')
#     assert L_currency_token.balanceOf(Lender) == 0
#     assert L_currency_token.balanceOf(UnderwriterPool.address) == Web3.toWei(800, 'ether')
#     # vefiry shield_currency_price is not set
#     multi_fungible_addresses = CurrencyDao.multi_fungible_addresses(Lend_token.address)
#     _s_hash = UnderwriterPoolDao.multi_fungible_currency_hash(
#         multi_fungible_addresses[3], Lend_token.address, Z19,
#         Borrow_token.address, _strike_price)
#     _i_hash = UnderwriterPoolDao.multi_fungible_currency_hash(
#         multi_fungible_addresses[1], Lend_token.address, Z19, ZERO_ADDRESS, 0)
#     # pool_owner initiates offer of 600 I_tokens from the UnderwriterPool
#     # 600 L_tokens burned from UnderwriterPool account
#     # 600 I_tokens, 3 S_tokens, and 3 U_tokens minted to UnderwriterPool account
#     tx_16_hash = UnderwriterPool.increment_i_currency_supply(
#         Z19, Borrow_token.address, _strike_price, 600 * 10 ** 18,
#         transact={'from': pool_owner, 'gas': 600000})
#     tx_16_receipt = w3.eth.waitForTransactionReceipt(tx_16_hash)
#     assert tx_16_receipt['status'] == 1
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
#     tx_17_hash = UnderwriterPool.purchase_i_currency(Z19, Borrow_token.address,
#         _strike_price, Web3.toWei(100, 'ether'), 0, transact={'from': High_Risk_Insurer})
#     tx_17_receipt = w3.eth.waitForTransactionReceipt(tx_17_hash)
#     assert tx_17_receipt['status'] == 1
#     # High_Risk_Insurer purchases 2 s_tokens from UnderwriterPool
#     # The corresponding 2 u_tokens remain in the UnderwriterPool
#     tx_18_hash = UnderwriterPool.purchase_s_currency(Z19, Borrow_token.address,
#         _strike_price, Web3.toWei(2, 'ether'), 0, transact={'from': High_Risk_Insurer})
#     tx_18_receipt = w3.eth.waitForTransactionReceipt(tx_18_hash)
#     assert tx_18_receipt['status'] == 1
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
#     tx_19_hash = Borrow_token.transfer(Borrower, Web3.toWei(10, 'ether'), transact={'from': owner})
#     tx_19_receipt = w3.eth.waitForTransactionReceipt(tx_19_hash)
#     assert tx_19_receipt['status'] == 1
#     assert Borrow_token.balanceOf(Borrower) == Web3.toWei(10, 'ether')
#     # Borrower authorizes CurrencyDao to spend 2 Borrow_tokens
#     tx_20_hash = Borrow_token.approve(CurrencyDao.address, Web3.toWei(3, 'ether'),
#         transact={'from': Borrower})
#     tx_20_receipt = w3.eth.waitForTransactionReceipt(tx_20_hash)
#     assert tx_20_receipt['status'] == 1
#     # Borrower deposits 2 Borrow_tokens to Currency Pool and gets l_tokens
#     tx_21_hash = CurrencyDao.currency_to_l_currency(Borrow_token.address, Web3.toWei(3, 'ether'),
#         transact={'from': Borrower, 'gas': 200000})
#     tx_21_receipt = w3.eth.waitForTransactionReceipt(tx_21_hash)
#     assert tx_21_receipt['status'] == 1
#     # Borrower wishes to avail a loan of 400 Lend_tokens
#     # High_Risk_Insurer authorizes CurrencyDao to spend his S_token
#     tx_22_hash = S_token.setApprovalForAll(CurrencyDao.address, True,
#         transact={'from': High_Risk_Insurer})
#     tx_22_receipt = w3.eth.waitForTransactionReceipt(tx_22_hash)
#     assert tx_22_receipt['status'] == 1
#     # High_Risk_Insurer authorizes CurrencyDao to spend his I_token
#     tx_23_hash = I_token.setApprovalForAll(CurrencyDao.address, True,
#         transact={'from': High_Risk_Insurer})
#     tx_23_receipt = w3.eth.waitForTransactionReceipt(tx_23_hash)
#     assert tx_23_receipt['status'] == 1
#     # High_Risk_Insurer sets an offer of 2 s_tokens for 20 i_tokens
#     assert PositionRegistry.last_offer_index() == 0
#     tx_24_hash = PositionRegistry.create_offer(
#         Lend_token.address, Z19, Borrow_token.address, _strike_price,
#         2, 20, 5 * 10 ** 15,
#         transact={'from': High_Risk_Insurer, 'gas': 450000})
#     tx_24_receipt = w3.eth.waitForTransactionReceipt(tx_24_hash)
#     assert tx_24_receipt['status'] == 1
#     # Borrower purchases this offer for the amount of 0.1 ETH
#     # 20 i_tokens are transferred from High_Risk_Insurer account to Borrower
#     # 2 s_tokens are transferred from High_Risk_Insurer account to MarketDao
#     tx_25_hash = PositionRegistry.avail_loan(0,
#         transact={'from': Borrower, 'value': 10 ** 17, 'gas': 950000})
#     tx_25_receipt = w3.eth.waitForTransactionReceipt(tx_25_hash)
#     assert tx_25_receipt['status'] == 1
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
#     tx_26_hash = Lend_token.approve(CurrencyDao.address, Web3.toWei(400, 'ether'),
#         transact={'from': Borrower})
#     tx_26_receipt = w3.eth.waitForTransactionReceipt(tx_26_hash)
#     assert tx_26_receipt['status'] == 1
#     # Borrower repays loan
#     position_id = PositionRegistry.borrow_position(Borrower, PositionRegistry.borrow_position_count(Borrower))
#     tx_27_hash = PositionRegistry.repay_loan(position_id, transact={'from': Borrower})
#     tx_27_receipt = w3.eth.waitForTransactionReceipt(tx_27_hash)
#     assert tx_27_receipt['status'] == 1
#     # verify i_lend_currency supply and i_lend_currency balance
#     assert I_token.totalBalanceOf(High_Risk_Insurer) == Web3.toWei(80, 'ether')
#     assert I_token.totalBalanceOf(Borrower) == Web3.toWei(20, 'ether')
#     assert I_token.totalBalanceOf(MarketDao.address) == 0
#     assert I_token.totalBalanceOf(UnderwriterPool.address) == Web3.toWei(500, 'ether')
#     # verify s_lend_currency supply and s_lend_currency balance
#     assert S_token.totalBalanceOf(High_Risk_Insurer) == Web3.toWei(0, 'ether')
#     assert S_token.totalBalanceOf(Borrower) == Web3.toWei(2, 'ether')
#     assert S_token.totalBalanceOf(MarketDao.address) == 0
#     assert S_token.totalBalanceOf(UnderwriterPool.address) == Web3.toWei(1, 'ether')
#     # verify u_lend_currency supply and u_lend_currency balance
#     assert U_token.totalBalanceOf(High_Risk_Insurer) == 0
#     assert U_token.totalBalanceOf(Borrower) == 0
#     assert U_token.totalBalanceOf(MarketDao.address) == 0
#     assert U_token.totalBalanceOf(UnderwriterPool.address) == Web3.toWei(3, 'ether')
#     # get Auction contract
#     _loan_market_hash = CollateralAuctionDao.loan_market_hash(
#         Lend_token.address, Z19, Borrow_token.address
#     )
#     Auction = get_contract(
#         'contracts/templates/SimpleCollateralAuctionGraph.v.py',
#         interfaces=['ERC20', 'MarketDao'],
#         address=CollateralAuctionDao.graphs(_loan_market_hash)
#     )
#     # time passes until loan market expires
#     time_travel(Z19)
#     # update price feed
#     tx_28_hash = PriceFeed.set_price(Web3.toWei(150, 'ether'), transact={'from': owner})
#     tx_28_receipt = w3.eth.waitForTransactionReceipt(tx_28_hash)
#     assert tx_28_receipt['status'] == 1
#     # assign one of the accounts as a _loan_market_settler
#     _loan_market_settler = w3.eth.accounts[3]
#     # _loan_market_settler initiates loan market settlement
#     tx_29_hash = MarketDao.settle_loan_market(_loan_market_hash, transact={'from': _loan_market_settler, 'gas': 280000})
#     tx_29_receipt = w3.eth.waitForTransactionReceipt(tx_29_hash)
#     assert tx_29_receipt['status'] == 1
#     # since there are no outstanding loans in this use case, the loan market is closed
#     assert MarketDao.loan_markets__status(_loan_market_hash) == MarketDao.LOAN_MARKET_STATUS_CLOSED()
#     # verify l_lend_currency supply, l_lend_currency balance and lend_currency balance
#     assert L_currency_token.totalSupply() == Web3.toWei(200, 'ether')
#     assert L_currency_token.balanceOf(UnderwriterPool.address) == Web3.toWei(200, 'ether')
#     assert L_currency_token.balanceOf(Borrower) == 0
#     # Borrower exercises 2 s_tokens
#     assert MarketDao.shield_payout(Lend_token.address, Z19, Borrow_token.address, _strike_price) == Web3.toWei(50, 'ether')
#     tx_30_hash = ShieldPayoutDao.exercise_shield_currency(Lend_token.address, Z19, Borrow_token.address, _strike_price, 2, transact={'from': Borrower})
#     tx_30_receipt = w3.eth.waitForTransactionReceipt(tx_30_hash)
#     assert tx_30_receipt['status'] == 1
#     # verify l_lend_currency supply, l_lend_currency balance and lend_currency balance
#     assert L_currency_token.totalSupply() == Web3.toWei(300, 'ether')
#     assert L_currency_token.balanceOf(UnderwriterPool.address) == Web3.toWei(200, 'ether')
#     assert L_currency_token.balanceOf(Borrower) == Web3.toWei(100, 'ether')
#     assert L_currency_token.balanceOf(pool_owner) == 0
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
#     # pool_owner exercises 2 u_tokens
#     assert MarketDao.underwriter_payout(Lend_token.address, Z19, Borrow_token.address, _strike_price) == Web3.toWei(150, 'ether')
#     tx_31_hash = UnderwriterPool.exercise_u_currency(Z19, Borrow_token.address, _strike_price, 2, transact={'from': pool_owner})
#     tx_31_receipt = w3.eth.waitForTransactionReceipt(tx_31_hash)
#     assert tx_31_receipt['status'] == 1
#     # verify l_lend_currency supply, l_lend_currency balance and lend_currency balance
#     assert L_currency_token.totalSupply() == Web3.toWei(600, 'ether')
#     assert L_currency_token.balanceOf(UnderwriterPool.address) == Web3.toWei(200, 'ether')
#     assert L_currency_token.balanceOf(Borrower) == Web3.toWei(100, 'ether')
#     assert L_currency_token.balanceOf(pool_owner) == Web3.toWei(300, 'ether')
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
#     assert U_token.totalBalanceOf(UnderwriterPool.address) == Web3.toWei(1, 'ether')
#
#
# def test_exercise_shield_currency_for_market_settlement_with_auction(w3, get_contract, get_logs, time_travel,
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
#     tx_5_hash = UnderwriterPoolDao.set_offer_registration_fee_lookup(_minimum_fee,
#         _minimum_interval, _fee_multiplier, _fee_multiplier_decimals,
#         transact={'from': owner})
#     tx_5_receipt = w3.eth.waitForTransactionReceipt(tx_5_hash)
#     assert tx_5_receipt['status'] == 1
#     # set_currency_support for Lend_token in CurrencyDao
#     tx_6_hash = CurrencyDao.set_currency_support(Lend_token.address, True,
#         transact={'from': owner, 'gas': 1570000})
#     tx_6_receipt = w3.eth.waitForTransactionReceipt(tx_6_hash)
#     assert tx_6_receipt['status'] == 1
#     # set_currency_support for Borrow_token in CurrencyDao
#     tx_7_hash = CurrencyDao.set_currency_support(Borrow_token.address, True,
#         transact={'from': owner, 'gas': 1570000})
#     tx_7_receipt = w3.eth.waitForTransactionReceipt(tx_7_hash)
#     assert tx_7_receipt['status'] == 1
#     # register_pool for Lend_token
#     pool_owner = w3.eth.accounts[1]
#     tx_8_hash = UnderwriterPoolDao.register_pool(Lend_token.address,
#         'Underwriter Pool A', 'UPA', 50,
#         transact={'from': pool_owner, 'gas': 850000})
#     tx_8_receipt = w3.eth.waitForTransactionReceipt(tx_8_hash)
#     assert tx_8_receipt['status'] == 1
#     # get UnderwriterPool contract
#     logs_8 = get_logs(tx_8_hash, UnderwriterPoolDao, "PoolRegistered")
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
#     tx_9_hash = LST_token.approve(CurrencyDao.address, Web3.toWei(UnderwriterPoolDao.offer_registration_fee(), 'ether'),
#         transact={'from': pool_owner})
#     tx_9_receipt = w3.eth.waitForTransactionReceipt(tx_9_hash)
#     assert tx_9_receipt['status'] == 1
#     # pool_owner registers an expiry : Last Thursday of December 2019, i.e., December 26th, 2019, i.e., Z19
#     _strike_price = Web3.toWei(200, 'ether')
#     tx_10_hash = UnderwriterPool.register_expiry(Z19, Borrow_token.address,
#         _strike_price, transact={'from': pool_owner, 'gas': 2600000})
#     tx_10_receipt = w3.eth.waitForTransactionReceipt(tx_10_hash)
#     assert tx_10_receipt['status'] == 1
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
#     tx_11_hash = Lend_token.transfer(Lender, Web3.toWei(1000, 'ether'), transact={'from': owner})
#     tx_11_receipt = w3.eth.waitForTransactionReceipt(tx_11_hash)
#     assert tx_11_receipt['status'] == 1
#     # Lender authorizes CurrencyDao to spend 800 lend currency
#     tx_12_hash = Lend_token.approve(CurrencyDao.address, Web3.toWei(800, 'ether'),
#         transact={'from': Lender})
#     tx_12_receipt = w3.eth.waitForTransactionReceipt(tx_12_hash)
#     assert tx_12_receipt['status'] == 1
#     # Lender deposits 800 Lend_tokens to Currency Pool and gets l_tokens
#     assert L_currency_token.totalSupply() == 0
#     assert Lend_token.balanceOf(CurrencyDao.pools__pool_address(_currency_pool_hash)) == 0
#     tx_13_hash = CurrencyDao.currency_to_l_currency(Lend_token.address, Web3.toWei(800, 'ether'),
#         transact={'from': Lender, 'gas': 200000})
#     tx_13_receipt = w3.eth.waitForTransactionReceipt(tx_13_hash)
#     assert tx_13_receipt['status'] == 1
#     # verify l_lend_currency supply, l_lend_currency balance and lend_currency balance
#     assert L_currency_token.totalSupply() == Web3.toWei(800, 'ether')
#     assert L_currency_token.balanceOf(Lender) == Web3.toWei(800, 'ether')
#     assert L_currency_token.balanceOf(UnderwriterPool.address) == 0
#     # Lender purchases UnderwriterPoolCurrency for 800 L_tokens
#     # Lender gets 40000 UnderwriterPoolCurrency tokens
#     # 800 L_tokens are deposited into UnderwriterPool account
#     tx_14_hash = UnderwriterPool.purchase_pool_currency(Web3.toWei(800, 'ether'), transact={'from': Lender})
#     tx_14_receipt = w3.eth.waitForTransactionReceipt(tx_14_hash)
#     assert tx_14_receipt['status'] == 1
#     # verify l_lend_currency supply, l_lend_currency balance and lend_currency balance
#     assert L_currency_token.totalSupply() == Web3.toWei(800, 'ether')
#     assert L_currency_token.balanceOf(Lender) == 0
#     assert L_currency_token.balanceOf(UnderwriterPool.address) == Web3.toWei(800, 'ether')
#     # vefiry shield_currency_price is not set
#     multi_fungible_addresses = CurrencyDao.multi_fungible_addresses(Lend_token.address)
#     _s_hash = UnderwriterPoolDao.multi_fungible_currency_hash(
#         multi_fungible_addresses[3], Lend_token.address, Z19,
#         Borrow_token.address, _strike_price)
#     _i_hash = UnderwriterPoolDao.multi_fungible_currency_hash(
#         multi_fungible_addresses[1], Lend_token.address, Z19, ZERO_ADDRESS, 0)
#     # pool_owner initiates offer of 600 I_tokens from the UnderwriterPool
#     # 600 L_tokens burned from UnderwriterPool account
#     # 600 I_tokens, 3 S_tokens, and 3 U_tokens minted to UnderwriterPool account
#     tx_16_hash = UnderwriterPool.increment_i_currency_supply(
#         Z19, Borrow_token.address, _strike_price, 600 * 10 ** 18,
#         transact={'from': pool_owner, 'gas': 600000})
#     tx_16_receipt = w3.eth.waitForTransactionReceipt(tx_16_hash)
#     assert tx_16_receipt['status'] == 1
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
#     tx_17_hash = UnderwriterPool.purchase_i_currency(Z19, Borrow_token.address,
#         _strike_price, Web3.toWei(100, 'ether'), 0, transact={'from': High_Risk_Insurer})
#     tx_17_receipt = w3.eth.waitForTransactionReceipt(tx_17_hash)
#     assert tx_17_receipt['status'] == 1
#     # High_Risk_Insurer purchases 2 s_tokens from UnderwriterPool
#     # The corresponding 2 u_tokens remain in the UnderwriterPool
#     tx_18_hash = UnderwriterPool.purchase_s_currency(Z19, Borrow_token.address,
#         _strike_price, Web3.toWei(2, 'ether'), 0, transact={'from': High_Risk_Insurer})
#     tx_18_receipt = w3.eth.waitForTransactionReceipt(tx_18_hash)
#     assert tx_18_receipt['status'] == 1
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
#     tx_19_hash = Borrow_token.transfer(Borrower, Web3.toWei(10, 'ether'), transact={'from': owner})
#     tx_19_receipt = w3.eth.waitForTransactionReceipt(tx_19_hash)
#     assert tx_19_receipt['status'] == 1
#     assert Borrow_token.balanceOf(Borrower) == Web3.toWei(10, 'ether')
#     # Borrower authorizes CurrencyDao to spend 2 Borrow_tokens
#     tx_20_hash = Borrow_token.approve(CurrencyDao.address, Web3.toWei(3, 'ether'),
#         transact={'from': Borrower})
#     tx_20_receipt = w3.eth.waitForTransactionReceipt(tx_20_hash)
#     assert tx_20_receipt['status'] == 1
#     # Borrower deposits 2 Borrow_tokens to Currency Pool and gets l_tokens
#     tx_21_hash = CurrencyDao.currency_to_l_currency(Borrow_token.address, Web3.toWei(3, 'ether'),
#         transact={'from': Borrower, 'gas': 200000})
#     tx_21_receipt = w3.eth.waitForTransactionReceipt(tx_21_hash)
#     assert tx_21_receipt['status'] == 1
#     # Borrower wishes to avail a loan of 400 Lend_tokens
#     # High_Risk_Insurer authorizes CurrencyDao to spend his S_token
#     tx_22_hash = S_token.setApprovalForAll(CurrencyDao.address, True,
#         transact={'from': High_Risk_Insurer})
#     tx_22_receipt = w3.eth.waitForTransactionReceipt(tx_22_hash)
#     assert tx_22_receipt['status'] == 1
#     # High_Risk_Insurer authorizes CurrencyDao to spend his I_token
#     tx_23_hash = I_token.setApprovalForAll(CurrencyDao.address, True,
#         transact={'from': High_Risk_Insurer})
#     tx_23_receipt = w3.eth.waitForTransactionReceipt(tx_23_hash)
#     assert tx_23_receipt['status'] == 1
#     # High_Risk_Insurer sets an offer of 2 s_tokens for 20 i_tokens
#     assert PositionRegistry.last_offer_index() == 0
#     tx_24_hash = PositionRegistry.create_offer(
#         Lend_token.address, Z19, Borrow_token.address, _strike_price,
#         2, 20, 5 * 10 ** 15,
#         transact={'from': High_Risk_Insurer, 'gas': 450000})
#     tx_24_receipt = w3.eth.waitForTransactionReceipt(tx_24_hash)
#     assert tx_24_receipt['status'] == 1
#     # Borrower purchases this offer for the amount of 0.1 ETH
#     # 20 i_tokens are transferred from High_Risk_Insurer account to Borrower
#     # 2 s_tokens are transferred from High_Risk_Insurer account to MarketDao
#     tx_25_hash = PositionRegistry.avail_loan(0,
#         transact={'from': Borrower, 'value': 10 ** 17, 'gas': 950000})
#     tx_25_receipt = w3.eth.waitForTransactionReceipt(tx_25_hash)
#     assert tx_25_receipt['status'] == 1
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
#     tx_26_hash = Lend_token.approve(CurrencyDao.address, Web3.toWei(400, 'ether'),
#         transact={'from': Borrower})
#     tx_26_receipt = w3.eth.waitForTransactionReceipt(tx_26_hash)
#     assert tx_26_receipt['status'] == 1
#     # get Auction contract
#     _loan_market_hash = CollateralAuctionDao.loan_market_hash(
#         Lend_token.address, Z19, Borrow_token.address
#     )
#     Auction = get_contract(
#         'contracts/templates/SimpleCollateralAuctionGraph.v.py',
#         interfaces=['ERC20', 'MarketDao'],
#         address=CollateralAuctionDao.graphs(_loan_market_hash)
#     )
#     # time passes until loan market expires
#     time_travel(Z19)
#     # update price feed
#     tx_27_hash = PriceFeed.set_price(Web3.toWei(150, 'ether'), transact={'from': owner})
#     tx_27_receipt = w3.eth.waitForTransactionReceipt(tx_27_hash)
#     assert tx_27_receipt['status'] == 1
#     # assign one of the accounts as a _loan_market_settler
#     _loan_market_settler = w3.eth.accounts[3]
#     # _loan_market_settler initiates loan market settlement
#     tx_28_hash = MarketDao.settle_loan_market(_loan_market_hash, transact={'from': _loan_market_settler, 'gas': 280000})
#     tx_28_receipt = w3.eth.waitForTransactionReceipt(tx_28_hash)
#     assert tx_28_receipt['status'] == 1
#     assert MarketDao.loan_markets__status(_loan_market_hash) == MarketDao.LOAN_MARKET_STATUS_SETTLING()
#     # assign one of the accounts as an _auctioned_collateral_purchaser
#     _auctioned_collateral_purchaser = w3.eth.accounts[4]
#     # _auctioned_collateral_purchaser buys 1000 lend token from a 3rd party exchange
#     tx_29_hash = Lend_token.transfer(_auctioned_collateral_purchaser, 1000 * 10 ** 18, transact={'from': owner})
#     tx_29_receipt = w3.eth.waitForTransactionReceipt(tx_29_hash)
#     assert tx_29_receipt['status'] == 1
#     # _auctioned_collateral_purchaser authorizes CurrencyDao to spend 800 lend currency
#     tx_30_hash = Lend_token.approve(CurrencyDao.address, 800 * (10 ** 18),
#         transact={'from': _auctioned_collateral_purchaser})
#     tx_30_receipt = w3.eth.waitForTransactionReceipt(tx_30_hash)
#     assert tx_30_receipt['status'] == 1
#     time_travel(Z19 + 10 * 60)
#     # _auctioned_collateral_purchaser purchases all of the 2 Borrow_tokens for current price of Lend_tokens
#     tx_31_hash = Auction.purchase_for_remaining_currency(transact={'from': _auctioned_collateral_purchaser, 'gas': 280000})
#     tx_31_receipt = w3.eth.waitForTransactionReceipt(tx_31_hash)
#     assert tx_31_receipt['status'] == 1
#     assert MarketDao.loan_markets__underlying_settlement_price_per_currency(_loan_market_hash) == 135165333333333333333
#     # verify l_lend_currency supply, l_lend_currency balance and lend_currency balance
#     assert L_currency_token.totalSupply() == Web3.toWei(200, 'ether')
#     assert L_currency_token.balanceOf(UnderwriterPool.address) == Web3.toWei(200, 'ether')
#     assert L_currency_token.balanceOf(Borrower) == 0
#     assert L_currency_token.balanceOf(pool_owner) == 0
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
#     assert MarketDao.shield_payout(Lend_token.address, Z19, Borrow_token.address, _strike_price) == 0
#     # pool_owner exercises 2 u_tokens
#     assert MarketDao.underwriter_payout(Lend_token.address, Z19, Borrow_token.address, _strike_price) == 135165333333333333333
#     tx_31_hash = UnderwriterPool.exercise_u_currency(Z19, Borrow_token.address, _strike_price, 2, transact={'from': pool_owner})
#     tx_31_receipt = w3.eth.waitForTransactionReceipt(tx_31_hash)
#     assert tx_31_receipt['status'] == 1
#     # verify l_lend_currency supply, l_lend_currency balance and lend_currency balance
#     assert L_currency_token.totalSupply() == 470330666666666666666
#     assert L_currency_token.balanceOf(UnderwriterPool.address) == Web3.toWei(200, 'ether')
#     assert L_currency_token.balanceOf(Borrower) == 0
#     assert L_currency_token.balanceOf(pool_owner) == 270330666666666666666
#     # verify i_lend_currency supply and i_lend_currency balance
#     assert I_token.totalBalanceOf(High_Risk_Insurer) == Web3.toWei(80, 'ether')
#     assert I_token.totalBalanceOf(Borrower) == Web3.toWei(20, 'ether')
#     assert I_token.totalBalanceOf(MarketDao.address) == 0
#     assert I_token.totalBalanceOf(UnderwriterPool.address) == Web3.toWei(500, 'ether')
#     # verify s_lend_currency supply and s_lend_currency balance
#     assert S_token.totalBalanceOf(High_Risk_Insurer) == 0
#     assert S_token.totalBalanceOf(Borrower) == 0
#     assert S_token.totalBalanceOf(MarketDao.address) == Web3.toWei(2, 'ether')
#     assert S_token.totalBalanceOf(UnderwriterPool.address) == Web3.toWei(1, 'ether')
#     # verify u_lend_currency supply and u_lend_currency balance
#     assert U_token.totalBalanceOf(High_Risk_Insurer) == 0
#     assert U_token.totalBalanceOf(Borrower) == 0
#     assert U_token.totalBalanceOf(MarketDao.address) == 0
#     assert U_token.totalBalanceOf(UnderwriterPool.address) == Web3.toWei(1, 'ether')
