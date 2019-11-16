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


@pytest.fixture
def LoanDao(w3, get_contract):
    interface_codes = {}
    with open(os.path.join(os.path.dirname(os.path.realpath(__file__)),
        os.pardir, 'contracts/interfaces/ERC20.vy')) as f:
            interface_codes['ERC20'] = {
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
        os.pardir, 'contracts/interfaces/CurrencyDao.vy')) as f:
            interface_codes['CurrencyDao'] = {
                'type': 'vyper',
                'code': f.read()
            }
    with open(os.path.join(os.path.dirname(os.path.realpath(__file__)),
        os.pardir, 'contracts/interfaces/InterestPoolDao.vy')) as f:
            interface_codes['InterestPoolDao'] = {
                'type': 'vyper',
                'code': f.read()
            }
    with open(os.path.join(os.path.dirname(os.path.realpath(__file__)),
        os.pardir, 'contracts/interfaces/UnderwriterPoolDao.vy')) as f:
            interface_codes['UnderwriterPoolDao'] = {
                'type': 'vyper',
                'code': f.read()
            }
    with open('contracts/daos/LoanDao.v.py') as f:
        contract_code = f.read()
        # Pass constructor variables directly to the contract
        contract = get_contract(contract_code, interface_codes=interface_codes)
    return contract


def test_avail_loan(w3, get_logs,
        LST_token, Lend_token, Borrow_token, Malicious_token,
        ERC20_library, ERC1155_library,
        CurrencyPool_library, CurrencyDao,
        ShieldPayoutGraph_library, ShieldPayoutDao,
        InterestPool_library, InterestPoolDao,
        UnderwriterPool_library, UnderwriterPoolDao, LoanDao):
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
    # initialize InterestPoolDao
    tx_2_hash = InterestPoolDao.initialize(
        owner, LST_token.address, CurrencyDao.address,
        InterestPool_library.address, ERC20_library.address,
        transact={'from': owner})
    tx_2_receipt = w3.eth.waitForTransactionReceipt(tx_2_hash)
    assert tx_2_receipt['status'] == 1
    # initialize UnderwriterPoolDao
    tx_3_hash = UnderwriterPoolDao.initialize(
        owner, LST_token.address, CurrencyDao.address, ShieldPayoutDao.address,
        UnderwriterPool_library.address, ERC20_library.address,
        transact={'from': owner})
    tx_3_receipt = w3.eth.waitForTransactionReceipt(tx_3_hash)
    assert tx_3_receipt['status'] == 1
    # initialize LoanDao
    tx_4_hash = LoanDao.initialize(
        owner, LST_token.address,
        CurrencyDao.address, InterestPoolDao.address, UnderwriterPoolDao.address,
        transact={'from': owner})
    tx_4_receipt = w3.eth.waitForTransactionReceipt(tx_4_hash)
    assert tx_4_receipt['status'] == 1
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
    tx_9_hash = LST_token.approve(CurrencyDao.address, UnderwriterPoolDao.offer_registration_fee() * (10 ** 18),
        transact={'from': pool_owner})
    tx_9_receipt = w3.eth.waitForTransactionReceipt(tx_9_hash)
    assert tx_9_receipt['status'] == 1
    # pool_owner registers an expiry : Last Thursday of December 2019, i.e., December 26th, 2019, i.e., Z19
    _strike_price = 200 * 10 ** 18
    tx_10_hash = UnderwriterPool.register_expiry(Z19, Borrow_token.address,
        _strike_price, transact={'from': pool_owner, 'gas': 1100000})
    tx_10_receipt = w3.eth.waitForTransactionReceipt(tx_10_hash)
    assert tx_10_receipt['status'] == 1
    # get L_Lend_token
    L_Lend_token_address = CurrencyDao.currencies__l_currency_address(Lend_token.address)
    L_Lend_token = _get_contract_from_address(w3, L_Lend_token_address, 'contracts/templates/ERC20Template1.v.py')
    # get L_Borrow_token
    L_Borrow_token_address = CurrencyDao.currencies__l_currency_address(Borrow_token.address)
    L_Borrow_token = _get_contract_from_address(w3, L_Borrow_token_address, 'contracts/templates/ERC20Template1.v.py')
    # assign one of the accounts as a Lender
    Lender = w3.eth.accounts[2]
    # Lender buys 1000 lend token from a 3rd party exchange
    tx_11_hash = Lend_token.transfer(Lender, 1000 * 10 ** 18, transact={'from': owner})
    tx_11_receipt = w3.eth.waitForTransactionReceipt(tx_11_hash)
    assert tx_11_receipt['status'] == 1
    # Lender authorizes CurrencyDao to spend 500 lend currency
    tx_12_hash = Lend_token.approve(CurrencyDao.address, 500 * (10 ** 18),
        transact={'from': Lender})
    tx_12_receipt = w3.eth.waitForTransactionReceipt(tx_12_hash)
    assert tx_12_receipt['status'] == 1
    # Lender deposits 500 Lend_tokens to Currency Pool and gets l_tokens
    tx_13_hash = CurrencyDao.currency_to_l_currency(Lend_token.address, 500 * 10 ** 18,
        transact={'from': Lender, 'gas': 200000})
    tx_13_receipt = w3.eth.waitForTransactionReceipt(tx_13_hash)
    assert tx_13_receipt['status'] == 1
    # Lender purchases UnderwriterPoolCurrency for 400 L_tokens
    # Lender gets 25000 UnderwriterPoolCurrency tokens
    # 400 L_tokens are deposited into UnderwriterPool account
    # verify UnderwriterPool balances of l, i, s, u tokens
    assert UnderwriterPool.l_currency_balance() == 0 * 10 ** 18
    assert UnderwriterPool.i_currency_balance(Z19, Borrow_token.address, _strike_price) == 0 * 10 ** 18
    assert UnderwriterPool.s_currency_balance(Z19, Borrow_token.address, _strike_price) == 0 * 10 ** 18
    assert UnderwriterPool.u_currency_balance(Z19, Borrow_token.address, _strike_price) == 0 * 10 ** 18
    tx_14_hash = UnderwriterPool.purchase_pool_currency(500 * 10 ** 18, transact={'from': Lender})
    tx_14_receipt = w3.eth.waitForTransactionReceipt(tx_14_hash)
    assert tx_14_receipt['status'] == 1
    # verify UnderwriterPool balances of l, i, s, u tokens
    assert UnderwriterPool.l_currency_balance() == 500 * 10 ** 18
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
    # set shield_currency_price
    shield_currency_minimum_collateral_value = 100 * 10 ** 18
    tx_15_hash = UnderwriterPoolDao.set_shield_currency_minimum_collateral_value(
        Lend_token.address, Z19, Borrow_token.address, _strike_price,
        shield_currency_minimum_collateral_value, transact={'from': owner})
    tx_15_receipt = w3.eth.waitForTransactionReceipt(tx_15_hash)
    assert tx_15_receipt['status'] == 1
    # pool_owner initiates offer of 400 I_tokens from the UnderwriterPool
    # 400 L_tokens burned from UnderwriterPool account
    # 400 I_tokens, 4 S_tokens, and 4 U_tokens minted to UnderwriterPool account
    tx_16_hash = UnderwriterPool.increment_i_currency_supply(
        Z19, Borrow_token.address, _strike_price, 400 * 10 ** 18,
        transact={'from': pool_owner, 'gas': 600000})
    tx_16_receipt = w3.eth.waitForTransactionReceipt(tx_16_hash)
    assert tx_16_receipt['status'] == 1
    # verify UnderwriterPool balances of l, i, s, u tokens
    assert UnderwriterPool.l_currency_balance() == 100 * 10 ** 18
    assert UnderwriterPool.i_currency_balance(Z19, Borrow_token.address, _strike_price) == 400 * 10 ** 18
    assert UnderwriterPool.s_currency_balance(Z19, Borrow_token.address, _strike_price) == 4 * 10 ** 18
    assert UnderwriterPool.u_currency_balance(Z19, Borrow_token.address, _strike_price) == 4 * 10 ** 18
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
    # High_Risk_Insurer purchases 100 i_tokens from UnderwriterPool
    tx_17_hash = UnderwriterPool.purchase_i_currency(Z19, Borrow_token.address,
        _strike_price, 100 * 10 ** 18, 0, transact={'from': High_Risk_Insurer})
    tx_17_receipt = w3.eth.waitForTransactionReceipt(tx_17_hash)
    assert tx_17_receipt['status'] == 1
    # verify UnderwriterPool balances of l, i, s, u tokens
    assert UnderwriterPool.l_currency_balance() == 100 * 10 ** 18
    assert UnderwriterPool.i_currency_balance(Z19, Borrow_token.address, _strike_price) == 300 * 10 ** 18
    assert UnderwriterPool.s_currency_balance(Z19, Borrow_token.address, _strike_price) == 4 * 10 ** 18
    assert UnderwriterPool.u_currency_balance(Z19, Borrow_token.address, _strike_price) == 4 * 10 ** 18
    # High_Risk_Insurer purchases 2 s_tokens from UnderwriterPool
    tx_18_hash = UnderwriterPool.purchase_s_currency(Z19, Borrow_token.address,
        _strike_price, 2 * 10 ** 18, 0, transact={'from': High_Risk_Insurer})
    tx_18_receipt = w3.eth.waitForTransactionReceipt(tx_18_hash)
    assert tx_18_receipt['status'] == 1
    # verify UnderwriterPool balances of l, i, s, u tokens
    assert UnderwriterPool.l_currency_balance() == 100 * 10 ** 18
    assert UnderwriterPool.i_currency_balance(Z19, Borrow_token.address, _strike_price) == 300 * 10 ** 18
    assert UnderwriterPool.s_currency_balance(Z19, Borrow_token.address, _strike_price) == 2 * 10 ** 18
    assert UnderwriterPool.u_currency_balance(Z19, Borrow_token.address, _strike_price) == 2 * 10 ** 18
    # assign one of the accounts as a Borrower
    Borrower = w3.eth.accounts[3]
    # Borrower purchases 10 Borrow_tokens from a 3rd party exchange
    tx_19_hash = Borrow_token.transfer(Borrower, 10 * 10 ** 18, transact={'from': owner})
    tx_19_receipt = w3.eth.waitForTransactionReceipt(tx_19_hash)
    assert tx_19_receipt['status'] == 1
    assert Borrow_token.balanceOf(Borrower) == 10 * 10 ** 18
    # Borrower authorizes CurrencyDao to spend 2 Borrow_tokens
    tx_20_hash = Borrow_token.approve(CurrencyDao.address, 2 * (10 ** 18),
        transact={'from': Borrower})
    tx_20_receipt = w3.eth.waitForTransactionReceipt(tx_20_hash)
    assert tx_20_receipt['status'] == 1
    # Borrower deposits 2 Borrow_tokens to Currency Pool and gets l_tokens
    tx_21_hash = CurrencyDao.currency_to_l_currency(Borrow_token.address, 2 * 10 ** 18,
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
    assert LoanDao.last_offer_index() == 0
    tx_24_hash = LoanDao.create_offer(_s_hash, _i_hash, 2, 20, 5 * 10 ** 15,
        transact={'from': High_Risk_Insurer, 'gas': 450000})
    tx_24_receipt = w3.eth.waitForTransactionReceipt(tx_24_hash)
    assert tx_24_receipt['status'] == 1
    assert LoanDao.last_offer_index() == 1
    assert LoanDao.offers__creator(1) == High_Risk_Insurer
    assert LoanDao.offers__s_hash(1) == _s_hash
    assert LoanDao.offers__s_quantity(1) == 2
    assert LoanDao.offers__i_quantity(1) == 20
    assert LoanDao.offers__i_unit_price_in_wei(1) == 5 * 10 ** 15
    # verify i_token, s_token and l_token balances of LoanDao
    assert I_token.balanceOf(
        LoanDao.address,
        UnderwriterPoolDao.multi_fungible_currencies__token_id(_i_hash)
    ) == 0
    assert S_token.balanceOf(
        LoanDao.address,
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
    # verify L_Borrow_token balance of LoanDao
    assert L_Borrow_token.balanceOf(LoanDao.address) == 0
    # verify L_Borrow_token balance of Borrower
    assert L_Borrow_token.balanceOf(Borrower) == 2 * 10 ** 18
    # verify Lend_token balance of Borrower
    assert Lend_token.balanceOf(Borrower) == 0
    # Borrower purchases this offer for the amount of 0.1 ETH
    # 20 i_tokens and 2 s_tokens are transferred from High_Risk_Insurer account to LoanDao
    tx_25_hash = LoanDao.avail_loan(1,
        transact={'from': Borrower, 'value': 10 ** 17})
    tx_25_receipt = w3.eth.waitForTransactionReceipt(tx_25_hash)
    assert tx_25_receipt['status'] == 1
    # verify i_token, s_token and l_token balances of LoanDao
    assert I_token.balanceOf(
        LoanDao.address,
        UnderwriterPoolDao.multi_fungible_currencies__token_id(_i_hash)
    ) == 20 * 10 ** 18
    assert S_token.balanceOf(
        LoanDao.address,
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
    # verify L_Borrow_token balance of LoanDao
    assert L_Borrow_token.balanceOf(LoanDao.address) == 1 * 10 ** 18
    # verify L_Borrow_token balance of Borrower
    assert L_Borrow_token.balanceOf(Borrower) == 1 * 10 ** 18
    # verify Lend_token balance of Borrower
    assert Lend_token.balanceOf(Borrower) == 400 * 10 ** 18


def test_repay_loan(w3, get_logs,
        LST_token, Lend_token, Borrow_token, Malicious_token,
        ERC20_library, ERC1155_library,
        CurrencyPool_library, CurrencyDao,
        ShieldPayoutGraph_library, ShieldPayoutDao,
        InterestPool_library, InterestPoolDao,
        UnderwriterPool_library, UnderwriterPoolDao, LoanDao):
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
    # initialize InterestPoolDao
    tx_2_hash = InterestPoolDao.initialize(
        owner, LST_token.address, CurrencyDao.address,
        InterestPool_library.address, ERC20_library.address,
        transact={'from': owner})
    tx_2_receipt = w3.eth.waitForTransactionReceipt(tx_2_hash)
    assert tx_2_receipt['status'] == 1
    # initialize UnderwriterPoolDao
    tx_3_hash = UnderwriterPoolDao.initialize(
        owner, LST_token.address, CurrencyDao.address, ShieldPayoutDao.address,
        UnderwriterPool_library.address, ERC20_library.address,
        transact={'from': owner})
    tx_3_receipt = w3.eth.waitForTransactionReceipt(tx_3_hash)
    assert tx_3_receipt['status'] == 1
    # initialize LoanDao
    tx_4_hash = LoanDao.initialize(
        owner, LST_token.address,
        CurrencyDao.address, InterestPoolDao.address, UnderwriterPoolDao.address,
        transact={'from': owner})
    tx_4_receipt = w3.eth.waitForTransactionReceipt(tx_4_hash)
    assert tx_4_receipt['status'] == 1
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
    tx_9_hash = LST_token.approve(CurrencyDao.address, UnderwriterPoolDao.offer_registration_fee() * (10 ** 18),
        transact={'from': pool_owner})
    tx_9_receipt = w3.eth.waitForTransactionReceipt(tx_9_hash)
    assert tx_9_receipt['status'] == 1
    # pool_owner registers an expiry : Last Thursday of December 2019, i.e., December 26th, 2019, i.e., Z19
    _strike_price = 200 * 10 ** 18
    tx_10_hash = UnderwriterPool.register_expiry(Z19, Borrow_token.address,
        _strike_price, transact={'from': pool_owner, 'gas': 1100000})
    tx_10_receipt = w3.eth.waitForTransactionReceipt(tx_10_hash)
    assert tx_10_receipt['status'] == 1
    # get L_Lend_token
    L_Lend_token_address = CurrencyDao.currencies__l_currency_address(Lend_token.address)
    L_Lend_token = _get_contract_from_address(w3, L_Lend_token_address, 'contracts/templates/ERC20Template1.v.py')
    # get L_Borrow_token
    L_Borrow_token_address = CurrencyDao.currencies__l_currency_address(Borrow_token.address)
    L_Borrow_token = _get_contract_from_address(w3, L_Borrow_token_address, 'contracts/templates/ERC20Template1.v.py')
    # assign one of the accounts as a Lender
    Lender = w3.eth.accounts[2]
    # Lender buys 1000 lend token from a 3rd party exchange
    tx_11_hash = Lend_token.transfer(Lender, 1000 * 10 ** 18, transact={'from': owner})
    tx_11_receipt = w3.eth.waitForTransactionReceipt(tx_11_hash)
    assert tx_11_receipt['status'] == 1
    # Lender authorizes CurrencyDao to spend 500 lend currency
    tx_12_hash = Lend_token.approve(CurrencyDao.address, 500 * (10 ** 18),
        transact={'from': Lender})
    tx_12_receipt = w3.eth.waitForTransactionReceipt(tx_12_hash)
    assert tx_12_receipt['status'] == 1
    # Lender deposits 500 Lend_tokens to Currency Pool and gets l_tokens
    tx_13_hash = CurrencyDao.currency_to_l_currency(Lend_token.address, 500 * 10 ** 18,
        transact={'from': Lender, 'gas': 200000})
    tx_13_receipt = w3.eth.waitForTransactionReceipt(tx_13_hash)
    assert tx_13_receipt['status'] == 1
    # Lender purchases UnderwriterPoolCurrency for 400 L_tokens
    # Lender gets 25000 UnderwriterPoolCurrency tokens
    # 400 L_tokens are deposited into UnderwriterPool account
    tx_14_hash = UnderwriterPool.purchase_pool_currency(500 * 10 ** 18, transact={'from': Lender})
    tx_14_receipt = w3.eth.waitForTransactionReceipt(tx_14_hash)
    assert tx_14_receipt['status'] == 1
    # vefiry shield_currency_price is not set
    multi_fungible_addresses = CurrencyDao.multi_fungible_addresses(Lend_token.address)
    _s_hash = UnderwriterPoolDao.multi_fungible_currency_hash(
        multi_fungible_addresses[3], Lend_token.address, Z19,
        Borrow_token.address, _strike_price)
    _i_hash = UnderwriterPoolDao.multi_fungible_currency_hash(
        multi_fungible_addresses[1], Lend_token.address, Z19, ZERO_ADDRESS, 0)
    # set shield_currency_price
    shield_currency_minimum_collateral_value = 100 * 10 ** 18
    tx_15_hash = UnderwriterPoolDao.set_shield_currency_minimum_collateral_value(
        Lend_token.address, Z19, Borrow_token.address, _strike_price,
        shield_currency_minimum_collateral_value, transact={'from': owner})
    tx_15_receipt = w3.eth.waitForTransactionReceipt(tx_15_hash)
    assert tx_15_receipt['status'] == 1
    # pool_owner initiates offer of 400 I_tokens from the UnderwriterPool
    # 400 L_tokens burned from UnderwriterPool account
    # 400 I_tokens, 4 S_tokens, and 4 U_tokens minted to UnderwriterPool account
    tx_16_hash = UnderwriterPool.increment_i_currency_supply(
        Z19, Borrow_token.address, _strike_price, 400 * 10 ** 18,
        transact={'from': pool_owner, 'gas': 600000})
    tx_16_receipt = w3.eth.waitForTransactionReceipt(tx_16_hash)
    assert tx_16_receipt['status'] == 1
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
    # Borrower purchases 3 Borrow_tokens from a 3rd party exchange
    tx_19_hash = Borrow_token.transfer(Borrower, 10 * 10 ** 18, transact={'from': owner})
    tx_19_receipt = w3.eth.waitForTransactionReceipt(tx_19_hash)
    assert tx_19_receipt['status'] == 1
    # Borrower authorizes CurrencyDao to spend 2 Borrow_tokens
    tx_20_hash = Borrow_token.approve(CurrencyDao.address, 2 * (10 ** 18),
        transact={'from': Borrower})
    tx_20_receipt = w3.eth.waitForTransactionReceipt(tx_20_hash)
    assert tx_20_receipt['status'] == 1
    # Borrower deposits 2 Borrow_tokens to Currency Pool and gets l_tokens
    tx_21_hash = CurrencyDao.currency_to_l_currency(Borrow_token.address, 2 * 10 ** 18,
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
    assert LoanDao.last_offer_index() == 0
    tx_24_hash = LoanDao.create_offer(_s_hash, _i_hash, 2, 20, 5 * 10 ** 15,
        transact={'from': High_Risk_Insurer, 'gas': 450000})
    tx_24_receipt = w3.eth.waitForTransactionReceipt(tx_24_hash)
    assert tx_24_receipt['status'] == 1
    # Borrower purchases this offer for the amount of 0.1 ETH
    # 20 i_tokens and 2 s_tokens are transferred from High_Risk_Insurer account to LoanDao
    tx_25_hash = LoanDao.avail_loan(1,
        transact={'from': Borrower, 'value': 10 ** 17})
    tx_25_receipt = w3.eth.waitForTransactionReceipt(tx_25_hash)
    assert tx_25_receipt['status'] == 1
    # Borrower authorizes CurrencyDao to spend 400 Lend_tokens
    tx_26_hash = Lend_token.approve(CurrencyDao.address, 400 * (10 ** 18),
        transact={'from': Borrower})
    tx_26_receipt = w3.eth.waitForTransactionReceipt(tx_26_hash)
    assert tx_26_receipt['status'] == 1
    # Borrower repays loan
    position_id = LoanDao.borrow_position(Borrower, LoanDao.borrow_position_count(Borrower))
    tx_27_hash = LoanDao.repay_loan(position_id, transact={'from': Borrower})
    tx_27_receipt = w3.eth.waitForTransactionReceipt(tx_27_hash)
    assert tx_27_receipt['status'] == 1
    # verify L_Borrow_token balance of Borrower
    assert L_Borrow_token.balanceOf(Borrower) == 2 * 10 ** 18
    # verify Lend_token balance of Borrower
    assert Lend_token.balanceOf(Borrower) == 0
