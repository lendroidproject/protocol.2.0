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
def Borrow_token(w3, get_contract):
    with open('contracts/templates/ERC20Template1.v.py') as f:
        contract_code = f.read()
        # Pass constructor variables directly to the contract
        contract = get_contract(contract_code, 'Test Borrow Token', 'WETH',
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
def ShieldPayoutGraph_library(w3, get_contract):
    with open('contracts/templates/SimpleShieldPayoutGraph.v.py') as f:
        contract_code = f.read()
        # Pass constructor variables directly to the contract
        contract = get_contract(contract_code)
    return contract


@pytest.fixture
def ShieldPayoutDao(w3, get_contract):
    interface_codes = {}
    with open(os.path.join(os.path.dirname(os.path.realpath(__file__)),
        os.pardir, 'contracts/interfaces/CurrencyDao.vy')) as f:
            interface_codes['CurrencyDao'] = {
                'type': 'vyper',
                'code': f.read()
            }
    with open(os.path.join(os.path.dirname(os.path.realpath(__file__)),
        os.pardir, 'contracts/interfaces/ShieldPayoutGraph.vy')) as f:
            interface_codes['ShieldPayoutGraph'] = {
                'type': 'vyper',
                'code': f.read()
            }
    with open('contracts/daos/ShieldPayoutDao.v.py') as f:
        contract_code = f.read()
        # Pass constructor variables directly to the contract
        contract = get_contract(contract_code, interface_codes=interface_codes)
    return contract


@pytest.fixture
def UnderwriterPool_library(w3, get_contract):
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
        os.pardir, 'contracts/interfaces/UnderwriterPoolDao.vy')) as f:
            interface_codes['UnderwriterPoolDao'] = {
                'type': 'vyper',
                'code': f.read()
            }
    with open('contracts/templates/UnderwriterPoolTemplate1.v.py') as f:
        contract_code = f.read()
        # Pass constructor variables directly to the contract
        contract = get_contract(contract_code, interface_codes=interface_codes)
    return contract


@pytest.fixture
def UnderwriterPoolDao(w3, get_contract):
    interface_codes = {}
    with open(os.path.join(os.path.dirname(os.path.realpath(__file__)),
        os.pardir, 'contracts/interfaces/CurrencyDao.vy')) as f:
            interface_codes['CurrencyDao'] = {
                'type': 'vyper',
                'code': f.read()
            }
    with open(os.path.join(os.path.dirname(os.path.realpath(__file__)),
        os.pardir, 'contracts/interfaces/UnderwriterPool.vy')) as f:
            interface_codes['UnderwriterPool'] = {
                'type': 'vyper',
                'code': f.read()
            }
    with open('contracts/daos/UnderwriterPoolDao.v.py') as f:
        contract_code = f.read()
        # Pass constructor variables directly to the contract
        contract = get_contract(contract_code, interface_codes=interface_codes)
    return contract


def test_purchase_i_currency(w3, get_logs,
        LST_token, Lend_token, Borrow_token, Malicious_token,
        ERC20_library, ERC1155_library,
        CurrencyPool_library, CurrencyDao,
        ShieldPayoutGraph_library, ShieldPayoutDao,
        UnderwriterPool_library, UnderwriterPoolDao):
    owner = w3.eth.accounts[0]
    # initialize CurrencyDao
    tx_1_hash = CurrencyDao.initialize(
        owner, LST_token.address, CurrencyPool_library.address,
        ERC20_library.address, ERC1155_library.address,
        transact={'from': owner})
    tx_1_receipt = w3.eth.waitForTransactionReceipt(tx_1_hash)
    assert tx_1_receipt['status'] == 1
    # initialize ShieldPayoutDao
    tx_1_hash = ShieldPayoutDao.initialize(
        owner, LST_token.address, CurrencyDao.address,
        UnderwriterPoolDao.address, ShieldPayoutGraph_library.address,
        transact={'from': owner})
    tx_1_receipt = w3.eth.waitForTransactionReceipt(tx_1_hash)
    assert tx_1_receipt['status'] == 1
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
        os.pardir, 'contracts/interfaces/UnderwriterPoolDao.vy')) as f:
            interface_codes['UnderwriterPoolDao'] = {
                'type': 'vyper',
                'code': f.read()
            }
    UnderwriterPool = _get_contract_from_address(w3,
        UnderwriterPoolDao.pools__pool_address(_pool_hash),
        'contracts/templates/UnderwriterPoolTemplate1.v.py',
        interface_codes=interface_codes)
    # get UnderwriterPoolCurrency
    UnderwriterPoolCurrency = _get_contract_from_address(w3,
        UnderwriterPool.pool_currency_address(),
        'contracts/templates/ERC20Template1.v.py')
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
        _strike_price, transact={'from': pool_owner, 'gas': 1100000})
    tx_8_receipt = w3.eth.waitForTransactionReceipt(tx_8_hash)
    assert tx_8_receipt['status'] == 1
    # get L_token
    L_token_address = CurrencyDao.currencies__l_currency_address(Lend_token.address)
    L_token = _get_contract_from_address(w3, L_token_address, 'contracts/templates/ERC20Template1.v.py')
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
    assert UnderwriterPool.l_currency_balance() == 100 * 10 ** 18
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
    # assign one of the accounts as a High_Risk_Insurer
    High_Risk_Insurer = w3.eth.accounts[2]
    # verify UnderwriterPool balances of l, i, s, u tokens
    assert UnderwriterPool.l_currency_balance() == 20 * 10 ** 18
    assert UnderwriterPool.i_currency_balance(Z19, Borrow_token.address, _strike_price) == 80 * 10 ** 18
    assert UnderwriterPool.s_currency_balance(Z19, Borrow_token.address, _strike_price) == 4 * 10 ** 18
    assert UnderwriterPool.u_currency_balance(Z19, Borrow_token.address, _strike_price) == 4 * 10 ** 18
    # verify High_Risk_Insurer balance of i tokens
    _expiry_hash = UnderwriterPool.expiry_hash(Z19, Borrow_token.address,
        _strike_price)
    assert I_token.balanceOf(High_Risk_Insurer, UnderwriterPool.expiries__i_currency_id(_expiry_hash)) == 0
    # High_Risk_Insurer purchases 10 i_tokens from UnderwriterPool
    tx_15_hash = UnderwriterPool.purchase_i_currency(Z19, Borrow_token.address,
        _strike_price, 10 * 10 ** 18, 0, transact={'from': High_Risk_Insurer})
    tx_15_receipt = w3.eth.waitForTransactionReceipt(tx_15_hash)
    assert tx_15_receipt['status'] == 1
    # verify UnderwriterPool balances of l, i, s, u tokens
    assert UnderwriterPool.l_currency_balance() == 20 * 10 ** 18
    assert UnderwriterPool.i_currency_balance(Z19, Borrow_token.address, _strike_price) == 70 * 10 ** 18
    assert UnderwriterPool.s_currency_balance(Z19, Borrow_token.address, _strike_price) == 4 * 10 ** 18
    assert UnderwriterPool.u_currency_balance(Z19, Borrow_token.address, _strike_price) == 4 * 10 ** 18
    # verify High_Risk_Insurer balance of i tokens
    assert I_token.balanceOf(High_Risk_Insurer, UnderwriterPool.expiries__i_currency_id(_expiry_hash)) == 10 * 10 ** 18


def test_purchase_s_currency(w3, get_logs,
        LST_token, Lend_token, Borrow_token, Malicious_token,
        ERC20_library, ERC1155_library,
        CurrencyPool_library, CurrencyDao,
        ShieldPayoutGraph_library, ShieldPayoutDao,
        UnderwriterPool_library, UnderwriterPoolDao):
    owner = w3.eth.accounts[0]
    # initialize CurrencyDao
    tx_1_hash = CurrencyDao.initialize(
        owner, LST_token.address, CurrencyPool_library.address,
        ERC20_library.address, ERC1155_library.address,
        transact={'from': owner})
    tx_1_receipt = w3.eth.waitForTransactionReceipt(tx_1_hash)
    assert tx_1_receipt['status'] == 1
    # initialize ShieldPayoutDao
    tx_1_hash = ShieldPayoutDao.initialize(
        owner, LST_token.address, CurrencyDao.address,
        UnderwriterPoolDao.address, ShieldPayoutGraph_library.address,
        transact={'from': owner})
    tx_1_receipt = w3.eth.waitForTransactionReceipt(tx_1_hash)
    assert tx_1_receipt['status'] == 1
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
        os.pardir, 'contracts/interfaces/UnderwriterPoolDao.vy')) as f:
            interface_codes['UnderwriterPoolDao'] = {
                'type': 'vyper',
                'code': f.read()
            }
    UnderwriterPool = _get_contract_from_address(w3,
        UnderwriterPoolDao.pools__pool_address(_pool_hash),
        'contracts/templates/UnderwriterPoolTemplate1.v.py',
        interface_codes=interface_codes)
    # get UnderwriterPoolCurrency
    UnderwriterPoolCurrency = _get_contract_from_address(w3,
        UnderwriterPool.pool_currency_address(),
        'contracts/templates/ERC20Template1.v.py')
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
        _strike_price, transact={'from': pool_owner, 'gas': 1100000})
    tx_8_receipt = w3.eth.waitForTransactionReceipt(tx_8_hash)
    assert tx_8_receipt['status'] == 1
    # get L_token
    L_token_address = CurrencyDao.currencies__l_currency_address(Lend_token.address)
    L_token = _get_contract_from_address(w3, L_token_address, 'contracts/templates/ERC20Template1.v.py')
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
    assert UnderwriterPool.l_currency_balance() == 100 * 10 ** 18
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
    # get S_token and U_token
    interface_codes = {}
    with open(os.path.join(os.path.dirname(os.path.realpath(__file__)),
        os.pardir, 'contracts/interfaces/ERC1155TokenReceiver.vy')) as f:
            interface_codes['ERC1155TokenReceiver'] = {
                'type': 'vyper',
                'code': f.read()
            }
    S_token = _get_contract_from_address(w3,
        CurrencyDao.currencies__s_currency_address(Lend_token.address),
        'contracts/templates/ERC1155Template1.v.py',
        interface_codes=interface_codes)
    U_token = _get_contract_from_address(w3,
        CurrencyDao.currencies__u_currency_address(Lend_token.address),
        'contracts/templates/ERC1155Template1.v.py',
        interface_codes=interface_codes)
    # assign one of the accounts as a High_Risk_Insurer
    High_Risk_Insurer = w3.eth.accounts[2]
    # verify UnderwriterPool balances of l, i, s, u tokens
    assert UnderwriterPool.l_currency_balance() == 20 * 10 ** 18
    assert UnderwriterPool.i_currency_balance(Z19, Borrow_token.address, _strike_price) == 80 * 10 ** 18
    assert UnderwriterPool.s_currency_balance(Z19, Borrow_token.address, _strike_price) == 4 * 10 ** 18
    assert UnderwriterPool.u_currency_balance(Z19, Borrow_token.address, _strike_price) == 4 * 10 ** 18
    # verify High_Risk_Insurer balance of s and u tokens
    _expiry_hash = UnderwriterPool.expiry_hash(Z19, Borrow_token.address,
        _strike_price)
    assert S_token.balanceOf(High_Risk_Insurer, UnderwriterPool.expiries__i_currency_id(_expiry_hash)) == 0
    assert U_token.balanceOf(High_Risk_Insurer, UnderwriterPool.expiries__i_currency_id(_expiry_hash)) == 0
    # High_Risk_Insurer purchases 10 i_tokens from UnderwriterPool
    tx_15_hash = UnderwriterPool.purchase_s_currency(Z19, Borrow_token.address,
        _strike_price, 3 * 10 ** 18, 0, transact={'from': High_Risk_Insurer})
    tx_15_receipt = w3.eth.waitForTransactionReceipt(tx_15_hash)
    assert tx_15_receipt['status'] == 1
    # verify UnderwriterPool balances of l, i, s, u tokens
    assert UnderwriterPool.l_currency_balance() == 20 * 10 ** 18
    assert UnderwriterPool.i_currency_balance(Z19, Borrow_token.address, _strike_price) == 80 * 10 ** 18
    assert UnderwriterPool.s_currency_balance(Z19, Borrow_token.address, _strike_price) == 1 * 10 ** 18
    assert UnderwriterPool.u_currency_balance(Z19, Borrow_token.address, _strike_price) == 1 * 10 ** 18
    # verify High_Risk_Insurer balance of s and u tokens
    assert S_token.balanceOf(High_Risk_Insurer, UnderwriterPool.expiries__i_currency_id(_expiry_hash)) == 3 * 10 ** 18
    assert U_token.balanceOf(High_Risk_Insurer, UnderwriterPool.expiries__i_currency_id(_expiry_hash)) == 3 * 10 ** 18
