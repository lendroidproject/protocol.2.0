import os

import pytest

from vyper import (
    compiler,
)

from web3 import Web3

from conftest import VyperContract


ZERO_ADDRESS = Web3.toChecksumAddress('0x0000000000000000000000000000000000000000')

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


def test_initialize(w3, get_logs, LST_token, ERC20_library, ERC1155_library,
    CurrencyPool_library, CurrencyDao):
    owner = w3.eth.accounts[0]
    assert CurrencyDao.initialized() == False
    assert CurrencyDao.owner() in (None, ZERO_ADDRESS)
    assert CurrencyDao.protocol_dao_address() in (None, ZERO_ADDRESS)
    assert CurrencyDao.protocol_currency_address() in (None, ZERO_ADDRESS)
    assert CurrencyDao.TEMPLATE_TYPE_CURRENCY_POOL() == 0
    assert CurrencyDao.TEMPLATE_TYPE_CURRENCY_ERC20() == 0
    assert CurrencyDao.TEMPLATE_TYPE_CURRENCY_ERC1155() == 0
    tx_hash = CurrencyDao.initialize(
        owner, LST_token.address, CurrencyPool_library.address,
        ERC20_library.address, ERC1155_library.address,
        transact={'from': owner})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    assert CurrencyDao.initialized() == True
    assert CurrencyDao.owner() == owner
    assert CurrencyDao.protocol_dao_address() == owner
    assert CurrencyDao.protocol_currency_address() == LST_token.address
    assert CurrencyDao.TEMPLATE_TYPE_CURRENCY_POOL() == 1
    assert CurrencyDao.TEMPLATE_TYPE_CURRENCY_ERC20() == 2
    assert CurrencyDao.TEMPLATE_TYPE_CURRENCY_ERC1155() == 3
    assert CurrencyDao.templates(1) == CurrencyPool_library.address
    assert CurrencyDao.templates(2) == ERC20_library.address
    assert CurrencyDao.templates(3) == ERC1155_library.address


def test_failed_transaction_for_set_currency_support_call_by_non_owner(w3, get_logs, LST_token, Malicious_token,
    ERC20_library, ERC1155_library, CurrencyPool_library, CurrencyDao):
    owner = w3.eth.accounts[0]
    tx_hash = CurrencyDao.initialize(
        owner, LST_token.address, CurrencyPool_library.address,
        ERC20_library.address, ERC1155_library.address,
        transact={'from': owner})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    tx_hash = CurrencyDao.set_currency_support(Malicious_token.address, True,
        transact={'from': w3.eth.accounts[1], 'gas': 1570000})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 0


def test_set_currency_support(w3, get_logs, LST_token, Lend_token,
    ERC20_library, ERC1155_library, CurrencyPool_library, CurrencyDao):
    owner = w3.eth.accounts[0]
    tx_hash = CurrencyDao.initialize(
        owner, LST_token.address, CurrencyPool_library.address,
        ERC20_library.address, ERC1155_library.address,
        transact={'from': owner})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    tx_hash = CurrencyDao.set_currency_support(Lend_token.address, True,
        transact={'from': owner, 'gas': 1570000})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1


def test_currency_dao_currency_to_l_currency(w3, get_logs, LST_token, Lend_token,
    ERC20_library, ERC1155_library, CurrencyPool_library, CurrencyDao):

    owner = w3.eth.accounts[0]
    # verify lend currency balance of owner
    currency_balance = Lend_token.balanceOf(owner)
    assert currency_balance == 1000000 * (10 ** 18)
    # authorize CurrencyDao to spend lend currency
    tx_hash = Lend_token.approve(CurrencyDao.address, 100 * (10 ** 18),
        transact={'from': owner})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    # initialize CurrencyDao
    tx_hash = CurrencyDao.initialize(
        owner, LST_token.address, CurrencyPool_library.address,
        ERC20_library.address, ERC1155_library.address,
        transact={'from': owner})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    # set support for lend currency
    tx_hash = CurrencyDao.set_currency_support(Lend_token.address, True,
        transact={'from': owner, 'gas': 1570000})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    # deposit currency to Currency Pool
    tx_hash = CurrencyDao.currency_to_l_currency(Lend_token.address, 100 * (10 ** 18),
        transact={'from': owner})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    # verify lend currency balance of owner
    currency_balance = Lend_token.balanceOf(owner)
    assert currency_balance == (1000000 - 100) * (10 ** 18)
    # verify l token balance of owner
    L_token_address = CurrencyDao.currencies__l_currency_address(Lend_token.address)
    L_token = _get_contract_from_address(w3, L_token_address, 'contracts/templates/ERC20Template1.v.py')
    l_currency_balance = L_token.balanceOf(owner)
    assert l_currency_balance == 100 * (10 ** 18)
