import os

import pytest

from vyper import (
    compiler,
)

from web3 import Web3

from conftest import VyperContract


ZERO_ADDRESS = Web3.toChecksumAddress('0x0000000000000000000000000000000000000000')
EMPTY_BYTES32 = '0x0000000000000000000000000000000000000000000000000000000000000000'

# EXPIRIES
# Last Thursday of December 2019, i.e., December 26th, 2019, i.e., Z19
Z19 = 1577404799


def _get_contract_from_address(_w3, _address, _source_code_path, **kwargs):
    with open(_source_code_path) as f:
        source_code = f.read()

    out = compiler.compile_code(
        source_code,
        ['abi', 'bytecode'],
        interface_codes=kwargs.pop('interface_codes', None),
    )
    abi = out['abi']
    bytecode = out['bytecode']
    contract = _w3.eth.contract(
        _address,
        abi=abi,
        bytecode=bytecode,
        ContractFactoryClass=VyperContract,
    )
    return contract


@pytest.fixture
def LST_token(w3, get_contract):
    with open('contracts/templates/ERC20Template1.v.py') as f:
        contract_code = f.read()
        # Pass constructor variables directly to the contract
        contract = get_contract(contract_code, 'Lendroid Support Token', 'LST',
            18, 12000000000)
    return contract


@pytest.fixture
def Lend_token(w3, get_contract):
    with open('contracts/templates/ERC20Template1.v.py') as f:
        contract_code = f.read()
        # Pass constructor variables directly to the contract
        contract = get_contract(contract_code, 'Test Lend Token', 'DAI',
            18, 1000000)
    return contract


@pytest.fixture
def Malicious_token(w3, get_contract):
    with open('contracts/templates/ERC20Template1.v.py') as f:
        contract_code = f.read()
        # Pass constructor variables directly to the contract
        contract = get_contract(contract_code, 'Test Malicious Token', 'XXX',
            18, 1000000)
    return contract


@pytest.fixture
def ERC20_library(w3, get_contract):
    with open('contracts/templates/ERC20Template2.v.py') as f:
        contract_code = f.read()
        # Pass constructor variables directly to the contract
        contract = get_contract(contract_code)
    return contract


@pytest.fixture
def ERC1155_library(w3, get_contract):
    interface_codes = {}
    with open(os.path.join(os.path.dirname(os.path.realpath(__file__)),
        os.pardir, 'contracts/interfaces/ERC1155TokenReceiver.vy')) as f:
            interface_codes['ERC1155TokenReceiver'] = {
                'type': 'vyper',
                'code': f.read()
            }
    with open('contracts/templates/ERC1155Template1.v.py') as f:
        contract_code = f.read()
        # Pass constructor variables directly to the contract
        contract = get_contract(contract_code, interface_codes=interface_codes)
    return contract


@pytest.fixture
def CurrencyPool_library(w3, get_contract):
    interface_codes = {}
    with open(os.path.join(os.path.dirname(os.path.realpath(__file__)),
        os.pardir, 'contracts/interfaces/ERC20.vy')) as f:
            interface_codes['ERC20'] = {
                'type': 'vyper',
                'code': f.read()
            }
    with open('contracts/templates/ContinuousCurrencyPoolERC20Template1.v.py') as f:
        contract_code = f.read()
        # Pass constructor variables directly to the contract
        contract = get_contract(contract_code, interface_codes=interface_codes)
    return contract


@pytest.fixture
def CurrencyDao(w3, get_contract):
    interface_codes = {}
    with open(os.path.join(os.path.dirname(os.path.realpath(__file__)),
        os.pardir, 'contracts/interfaces/ERC20.vy')) as f:
            interface_codes['ERC20'] = {
                'type': 'vyper',
                'code': f.read()
            }
    with open(os.path.join(os.path.dirname(os.path.realpath(__file__)),
        os.pardir, 'contracts/interfaces/ERC1155.vy')) as f:
            interface_codes['ERC1155'] = {
                'type': 'vyper',
                'code': f.read()
            }
    with open(os.path.join(os.path.dirname(os.path.realpath(__file__)),
        os.pardir, 'contracts/interfaces/ContinuousCurrencyPoolERC20.vy')) as f:
            interface_codes['ContinuousCurrencyPoolERC20'] = {
                'type': 'vyper',
                'code': f.read()
            }
    with open('contracts/daos/CurrencyDao.v.py') as f:
        contract_code = f.read()
        # Pass constructor variables directly to the contract
        contract = get_contract(contract_code, interface_codes=interface_codes)
    return contract


@pytest.fixture
def InterestPool_library(w3, get_contract):
    interface_codes = {}
    with open(os.path.join(os.path.dirname(os.path.realpath(__file__)),
        os.pardir, 'contracts/interfaces/ERC20.vy')) as f:
            interface_codes['ERC20'] = {
                'type': 'vyper',
                'code': f.read()
            }
    with open(os.path.join(os.path.dirname(os.path.realpath(__file__)),
        os.pardir, 'contracts/interfaces/ERC1155.vy')) as f:
            interface_codes['ERC1155'] = {
                'type': 'vyper',
                'code': f.read()
            }
    with open(os.path.join(os.path.dirname(os.path.realpath(__file__)),
        os.pardir, 'contracts/interfaces/ERC1155TokenReceiver.vy')) as f:
            interface_codes['ERC1155TokenReceiver'] = {
                'type': 'vyper',
                'code': f.read()
            }
    with open(os.path.join(os.path.dirname(os.path.realpath(__file__)),
        os.pardir, 'contracts/interfaces/InterestPoolDao.vy')) as f:
            interface_codes['InterestPoolDao'] = {
                'type': 'vyper',
                'code': f.read()
            }
    with open('contracts/templates/InterestPoolTemplate1.v.py') as f:
        contract_code = f.read()
        # Pass constructor variables directly to the contract
        contract = get_contract(contract_code, interface_codes=interface_codes)
    return contract


@pytest.fixture
def InterestPoolDao(w3, get_contract):
    interface_codes = {}
    with open(os.path.join(os.path.dirname(os.path.realpath(__file__)),
        os.pardir, 'contracts/interfaces/CurrencyDao.vy')) as f:
            interface_codes['CurrencyDao'] = {
                'type': 'vyper',
                'code': f.read()
            }
    with open(os.path.join(os.path.dirname(os.path.realpath(__file__)),
        os.pardir, 'contracts/interfaces/InterestPool.vy')) as f:
            interface_codes['InterestPool'] = {
                'type': 'vyper',
                'code': f.read()
            }
    with open('contracts/daos/InterestPoolDao.v.py') as f:
        contract_code = f.read()
        # Pass constructor variables directly to the contract
        contract = get_contract(contract_code, interface_codes=interface_codes)
    return contract


def test_purchase_i_currency(w3, get_logs,
        LST_token, Lend_token, Malicious_token,
        ERC20_library, ERC1155_library, CurrencyPool_library,
        CurrencyDao, InterestPool_library, InterestPoolDao):
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
    # assign one of the accounts as a High_Risk_Insurer
    High_Risk_Insurer = w3.eth.accounts[2]
    # High_Risk_Insurer buys 1000 lend token from a 3rd party exchange
    tx_8_hash = Lend_token.transfer(High_Risk_Insurer, 1000 * 10 ** 18, transact={'from': owner})
    tx_8_receipt = w3.eth.waitForTransactionReceipt(tx_8_hash)
    assert tx_8_receipt['status'] == 1
    # High_Risk_Insurer authorizes CurrencyDao to spend 100 lend currency
    tx_9_hash = Lend_token.approve(CurrencyDao.address, 100 * (10 ** 18),
        transact={'from': High_Risk_Insurer})
    tx_9_receipt = w3.eth.waitForTransactionReceipt(tx_9_hash)
    assert tx_9_receipt['status'] == 1
    # High_Risk_Insurer deposits Lend_token to Currency Pool and gets l_tokens
    tx_10_hash = CurrencyDao.currency_to_l_currency(Lend_token.address, 100 * 10 ** 18,
        transact={'from': High_Risk_Insurer, 'gas': 200000})
    tx_10_receipt = w3.eth.waitForTransactionReceipt(tx_10_hash)
    assert tx_10_receipt['status'] == 1
    # High_Risk_Insurer purchases InterestPoolCurrency for 100 L_tokens
    # High_Risk_Insurer gets 5000 InterestPoolCurrency tokens
    # 100 L_tokens are deposited into InterestPool account
    tx_11_hash = InterestPool.purchase_pool_currency(100 * 10 ** 18, transact={'from': High_Risk_Insurer})
    tx_11_receipt = w3.eth.waitForTransactionReceipt(tx_11_hash)
    assert tx_11_receipt['status'] == 1
    # pool_owner initiates offer of 20 I_tokens from the InterestPool
    # 20 L_tokens burned from InterestPool account
    # 20 I_tokens and 20 F_tokens deposited to InterestPool account
    tx_12_hash = InterestPool.increment_i_currency_supply(Z19, 20 * 10 ** 18, transact={'from': pool_owner, 'gas': 500000})
    tx_12_receipt = w3.eth.waitForTransactionReceipt(tx_12_hash)
    assert tx_12_receipt['status'] == 1
    # High_Risk_Insurer purchases 10 i_tokens from InterestPool
    tx_13_hash = InterestPool.purchase_i_currency(Z19, 10 * 10 ** 18, 0, transact={'from': High_Risk_Insurer})
    tx_13_receipt = w3.eth.waitForTransactionReceipt(tx_13_hash)
    assert tx_13_receipt['status'] == 1
    # verify InterestPool balances of l, i, f tokens
    assert InterestPool.i_currency_balance(Z19) == 10 * 10 ** 18
    assert InterestPool.f_currency_balance(Z19) == 20 * 10 ** 18
    assert InterestPool.total_f_currency_balance() == 20 * 10 ** 18
    assert InterestPool.l_currency_balance() == 80 * 10 ** 18
    assert InterestPool.total_l_currency_balance() == 100 * 10 ** 18
    # get I_token
    interface_codes = {}
    with open(os.path.join(os.path.dirname(os.path.realpath(__file__)),
        os.pardir, 'contracts/interfaces/ERC1155TokenReceiver.vy')) as f:
            interface_codes['ERC1155TokenReceiver'] = {
                'type': 'vyper',
                'code': f.read()
            }
    I_token = _get_contract_from_address(w3,
        CurrencyDao.currencies__i_currency_address(Lend_token.address),
        'contracts/templates/ERC1155Template1.v.py',
        interface_codes=interface_codes)
    # verify High_Risk_Insurer balance of i tokens
    assert I_token.balanceOf(High_Risk_Insurer, InterestPool.expiries__i_currency_id(Z19)) == 10 * 10 ** 18


def test_redeem_f_currency(w3, get_logs,
        LST_token, Lend_token, Malicious_token,
        ERC20_library, ERC1155_library, CurrencyPool_library,
        CurrencyDao, InterestPool_library, InterestPoolDao):
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
    # assign one of the accounts as a High_Risk_Insurer
    High_Risk_Insurer = w3.eth.accounts[2]
    # High_Risk_Insurer buys 1000 lend token from a 3rd party exchange
    tx_8_hash = Lend_token.transfer(High_Risk_Insurer, 1000 * 10 ** 18, transact={'from': owner})
    tx_8_receipt = w3.eth.waitForTransactionReceipt(tx_8_hash)
    assert tx_8_receipt['status'] == 1
    # High_Risk_Insurer authorizes CurrencyDao to spend 100 lend currency
    tx_9_hash = Lend_token.approve(CurrencyDao.address, 100 * (10 ** 18),
        transact={'from': High_Risk_Insurer})
    tx_9_receipt = w3.eth.waitForTransactionReceipt(tx_9_hash)
    assert tx_9_receipt['status'] == 1
    # High_Risk_Insurer deposits Lend_token to Currency Pool and gets l_tokens
    tx_10_hash = CurrencyDao.currency_to_l_currency(Lend_token.address, 100 * 10 ** 18,
        transact={'from': High_Risk_Insurer, 'gas': 200000})
    tx_10_receipt = w3.eth.waitForTransactionReceipt(tx_10_hash)
    assert tx_10_receipt['status'] == 1
    # High_Risk_Insurer purchases InterestPoolCurrency for 100 L_tokens
    # High_Risk_Insurer gets 5000 InterestPoolCurrency tokens
    # 100 L_tokens are deposited into InterestPool account
    tx_11_hash = InterestPool.purchase_pool_currency(100 * 10 ** 18, transact={'from': High_Risk_Insurer})
    tx_11_receipt = w3.eth.waitForTransactionReceipt(tx_11_hash)
    assert tx_11_receipt['status'] == 1
    # pool_owner initiates offer of 20 I_tokens from the InterestPool
    # 20 L_tokens burned from InterestPool account
    # 20 I_tokens and 20 F_tokens deposited to InterestPool account
    tx_12_hash = InterestPool.increment_i_currency_supply(Z19, 20 * 10 ** 18, transact={'from': pool_owner, 'gas': 500000})
    tx_12_receipt = w3.eth.waitForTransactionReceipt(tx_12_hash)
    assert tx_12_receipt['status'] == 1
    assert InterestPool.i_currency_balance(Z19) == 20 * 10 ** 18
    assert InterestPool.f_currency_balance(Z19) == 20 * 10 ** 18
    assert InterestPool.total_f_currency_balance() == 20 * 10 ** 18
    assert InterestPool.l_currency_balance() == (100 - 20) * 10 ** 18
    assert InterestPool.total_l_currency_balance() == 100 * 10 ** 18
    # High_Risk_Insurer redeems f_tokens worth 5000 InterestPoolCurrency tokens from InterestPool
    assert InterestPool.estimated_pool_tokens(100 * 10 ** 18) == 5000 * 10 ** 18
    tx_13_hash = InterestPool.redeem_f_currency(Z19, 5000 * 10 ** 18, transact={'from': High_Risk_Insurer, 'gas': 500000})
    tx_13_receipt = w3.eth.waitForTransactionReceipt(tx_13_hash)
    assert tx_13_receipt['status'] == 1
    # get F_token
    interface_codes = {}
    with open(os.path.join(os.path.dirname(os.path.realpath(__file__)),
        os.pardir, 'contracts/interfaces/ERC1155TokenReceiver.vy')) as f:
            interface_codes['ERC1155TokenReceiver'] = {
                'type': 'vyper',
                'code': f.read()
            }
    F_token = _get_contract_from_address(w3,
        CurrencyDao.currencies__f_currency_address(Lend_token.address),
        'contracts/templates/ERC1155Template1.v.py',
        interface_codes=interface_codes)
    # verify High_Risk_Insurer balance of l and f tokens
    assert F_token.balanceOf(High_Risk_Insurer, InterestPool.expiries__f_currency_id(Z19)) == 100 * 10 ** 18
    assert L_token.balanceOf(High_Risk_Insurer) == 0 * 10 ** 18
    # verify InterestPool balance of InterestPoolCurrency tokens
    assert InterestPoolCurrency.balanceOf(InterestPool.address) == 0
    # verify multi_fungible_currency balances of InterestPool
    assert InterestPool.i_currency_balance(Z19) == 20 * 10 ** 18
    assert InterestPool.f_currency_balance(Z19) == 0
    assert InterestPool.total_f_currency_balance() == 0
    assert InterestPool.l_currency_balance() == 0
    assert InterestPool.total_l_currency_balance() == 0
