import pytest

from web3 import Web3

from conftest import (
    PROTOCOL_CONSTANTS,
    POOL_NAME_REGISTRATION_MIN_STAKE_LST,
    ZERO_ADDRESS
)


def test_change_governor(w3, Governor, get_logs, ProtocolDao):
    _new_governor = w3.eth.accounts[5]
    assert ProtocolDao.authorized_callers(PROTOCOL_CONSTANTS['CALLER_GOVERNOR']) == Governor
    tx_1_hash = ProtocolDao.change_governor(_new_governor, transact={'from': Governor})
    tx_1_receipt = w3.eth.waitForTransactionReceipt(tx_1_hash)
    assert tx_1_receipt['status'] == 1
    logs_1 = get_logs(tx_1_hash, ProtocolDao, "AuthorizedCallerUpdated")
    assert logs_1[0].args._caller_type == PROTOCOL_CONSTANTS['CALLER_GOVERNOR']
    assert logs_1[0].args._caller == Governor
    assert logs_1[0].args._authorized_caller == _new_governor
    assert ProtocolDao.authorized_callers(PROTOCOL_CONSTANTS['CALLER_GOVERNOR']) == _new_governor

    assert True


def test_change_governor_fail_when_called_by_non_governor(w3, Governor, assert_tx_failed, ProtocolDao):
    for account in w3.eth.accounts:
        if account == Governor:
            continue
        assert_tx_failed(lambda: ProtocolDao.change_governor(account))


def test_change_escape_hatch_manager(w3, Governor, EscapeHatchManager, get_logs, ProtocolDao):
    _new_escape_hatch_manager = w3.eth.accounts[5]
    assert ProtocolDao.authorized_callers(PROTOCOL_CONSTANTS['CALLER_ESCAPE_HATCH_MANAGER']) == EscapeHatchManager
    tx_1_hash = ProtocolDao.change_escape_hatch_manager(_new_escape_hatch_manager, transact={'from': Governor})
    tx_1_receipt = w3.eth.waitForTransactionReceipt(tx_1_hash)
    assert tx_1_receipt['status'] == 1
    logs_1 = get_logs(tx_1_hash, ProtocolDao, "AuthorizedCallerUpdated")
    assert logs_1[0].args._caller_type == PROTOCOL_CONSTANTS['CALLER_ESCAPE_HATCH_MANAGER']
    assert logs_1[0].args._caller == Governor
    assert logs_1[0].args._authorized_caller == _new_escape_hatch_manager
    assert ProtocolDao.authorized_callers(PROTOCOL_CONSTANTS['CALLER_ESCAPE_HATCH_MANAGER']) == _new_escape_hatch_manager

    assert True


def test_change_escape_hatch_manager_fail_when_called_by_non_governor(w3, Governor, assert_tx_failed, ProtocolDao):
    for account in w3.eth.accounts:
        if account == Governor:
            continue
        assert_tx_failed(lambda: ProtocolDao.change_escape_hatch_manager(account))


def test_change_escape_hatch_token_holder(w3, Governor, EscapeHatchTokenHolder, get_logs, ProtocolDao):
    _new_escape_hatch_token_holder = w3.eth.accounts[5]
    assert ProtocolDao.authorized_callers(PROTOCOL_CONSTANTS['CALLER_ESCAPE_HATCH_TOKEN_HOLDER']) == EscapeHatchTokenHolder
    tx_1_hash = ProtocolDao.change_escape_hatch_token_holder(_new_escape_hatch_token_holder, transact={'from': Governor})
    tx_1_receipt = w3.eth.waitForTransactionReceipt(tx_1_hash)
    assert tx_1_receipt['status'] == 1
    logs_1 = get_logs(tx_1_hash, ProtocolDao, "AuthorizedCallerUpdated")
    assert logs_1[0].args._caller_type == PROTOCOL_CONSTANTS['CALLER_ESCAPE_HATCH_TOKEN_HOLDER']
    assert logs_1[0].args._caller == Governor
    assert logs_1[0].args._authorized_caller == _new_escape_hatch_token_holder
    assert ProtocolDao.authorized_callers(PROTOCOL_CONSTANTS['CALLER_ESCAPE_HATCH_TOKEN_HOLDER']) == _new_escape_hatch_token_holder

    assert True


def test_change_escape_hatch_token_holder_fail_when_called_by_non_governor(w3, Governor, assert_tx_failed, ProtocolDao):
    for account in w3.eth.accounts:
        if account == Governor:
            continue
    assert_tx_failed(lambda: ProtocolDao.change_escape_hatch_token_holder(account))


def test_initialize_pool_name_registry(w3, Deployer, get_logs, ProtocolDao):
    _stake = Web3.toWei(POOL_NAME_REGISTRATION_MIN_STAKE_LST, 'ether')
    tx_1_hash = ProtocolDao.initialize_pool_name_registry(_stake, transact={'from': Deployer})
    tx_1_receipt = w3.eth.waitForTransactionReceipt(tx_1_hash)
    assert tx_1_receipt['status'] == 1
    logs_1 = get_logs(tx_1_hash, ProtocolDao, "RegistryInitialized")
    assert logs_1[0].args._setter == Deployer
    assert logs_1[0].args._template_type == PROTOCOL_CONSTANTS['REGISTRY_POOL_NAME']
    assert logs_1[0].args._registry_address == ProtocolDao.registries(PROTOCOL_CONSTANTS['REGISTRY_POOL_NAME'])


def test_initialize_pool_name_registry_fail_when_called_by_non_deployer(w3, Deployer, assert_tx_failed, ProtocolDao):
    _stake = Web3.toWei(POOL_NAME_REGISTRATION_MIN_STAKE_LST, 'ether')
    for account in w3.eth.accounts:
        if account == Deployer:
            continue
        assert_tx_failed(lambda: ProtocolDao.initialize_pool_name_registry(_stake, transact={'from': account}))


def test_initialize_position_registry(w3, Deployer, get_logs, ProtocolDao):
    tx_1_hash = ProtocolDao.initialize_position_registry(transact={'from': Deployer})
    tx_1_receipt = w3.eth.waitForTransactionReceipt(tx_1_hash)
    assert tx_1_receipt['status'] == 1
    logs_1 = get_logs(tx_1_hash, ProtocolDao, "RegistryInitialized")
    assert logs_1[0].args._setter == Deployer
    assert logs_1[0].args._template_type == PROTOCOL_CONSTANTS['REGISTRY_POSITION']
    assert logs_1[0].args._registry_address == ProtocolDao.registries(PROTOCOL_CONSTANTS['REGISTRY_POSITION'])


def test_initialize_position_registry_fail_when_called_by_non_deployer(w3, Deployer, assert_tx_failed, ProtocolDao):
    for account in w3.eth.accounts:
        if account == Deployer:
            continue
        assert_tx_failed(lambda: ProtocolDao.initialize_position_registry(transact={'from': account}))


def test_initialize_currency_dao(w3, Deployer, get_logs, ProtocolDao):
    tx_1_hash = ProtocolDao.initialize_currency_dao(transact={'from': Deployer})
    tx_1_receipt = w3.eth.waitForTransactionReceipt(tx_1_hash)
    assert tx_1_receipt['status'] == 1
    logs_1 = get_logs(tx_1_hash, ProtocolDao, "DAOInitialized")
    assert logs_1[0].args._setter == Deployer
    assert logs_1[0].args._dao_type == PROTOCOL_CONSTANTS['DAO_CURRENCY']
    assert logs_1[0].args._dao_address == ProtocolDao.daos(PROTOCOL_CONSTANTS['DAO_CURRENCY'])


def test_initialize_currency_dao_fail_when_called_by_non_deployer(w3, Deployer, assert_tx_failed, ProtocolDao):
    for account in w3.eth.accounts:
        if account == Deployer:
            continue
        assert_tx_failed(lambda: ProtocolDao.initialize_currency_dao(transact={'from': account}))


def test_initialize_interest_pool_dao(w3, Deployer, get_logs, ProtocolDao):
    tx_1_hash = ProtocolDao.initialize_interest_pool_dao(transact={'from': Deployer})
    tx_1_receipt = w3.eth.waitForTransactionReceipt(tx_1_hash)
    assert tx_1_receipt['status'] == 1
    logs_1 = get_logs(tx_1_hash, ProtocolDao, "DAOInitialized")
    assert logs_1[0].args._setter == Deployer
    assert logs_1[0].args._dao_type == PROTOCOL_CONSTANTS['DAO_INTEREST_POOL']
    assert logs_1[0].args._dao_address == ProtocolDao.daos(PROTOCOL_CONSTANTS['DAO_INTEREST_POOL'])


def test_initialize_interest_pool_dao_fail_when_called_by_non_deployer(w3, Deployer, assert_tx_failed, ProtocolDao):
    for account in w3.eth.accounts:
        if account == Deployer:
            continue
        assert_tx_failed(lambda: ProtocolDao.initialize_interest_pool_dao(transact={'from': account}))


def test_initialize_underwriter_pool_dao(w3, Deployer, get_logs, ProtocolDao):
    tx_1_hash = ProtocolDao.initialize_underwriter_pool_dao(transact={'from': Deployer})
    tx_1_receipt = w3.eth.waitForTransactionReceipt(tx_1_hash)
    assert tx_1_receipt['status'] == 1
    logs_1 = get_logs(tx_1_hash, ProtocolDao, "DAOInitialized")
    assert logs_1[0].args._setter == Deployer
    assert logs_1[0].args._dao_type == PROTOCOL_CONSTANTS['DAO_UNDERWRITER_POOL']
    assert logs_1[0].args._dao_address == ProtocolDao.daos(PROTOCOL_CONSTANTS['DAO_UNDERWRITER_POOL'])


def test_initialize_underwriter_pool_dao_fail_when_called_by_non_deployer(w3, Deployer, assert_tx_failed, ProtocolDao):
    for account in w3.eth.accounts:
        if account == Deployer:
            continue
        assert_tx_failed(lambda: ProtocolDao.initialize_underwriter_pool_dao(transact={'from': account}))


def test_initialize_market_dao(w3, Deployer, get_logs, ProtocolDao):
    tx_1_hash = ProtocolDao.initialize_market_dao(transact={'from': Deployer})
    tx_1_receipt = w3.eth.waitForTransactionReceipt(tx_1_hash)
    assert tx_1_receipt['status'] == 1
    logs_1 = get_logs(tx_1_hash, ProtocolDao, "DAOInitialized")
    assert logs_1[0].args._setter == Deployer
    assert logs_1[0].args._dao_type == PROTOCOL_CONSTANTS['DAO_MARKET']
    assert logs_1[0].args._dao_address == ProtocolDao.daos(PROTOCOL_CONSTANTS['DAO_MARKET'])


def test_initialize_market_dao_fail_when_called_by_non_deployer(w3, Deployer, assert_tx_failed, ProtocolDao):
    for account in w3.eth.accounts:
        if account == Deployer:
            continue
        assert_tx_failed(lambda: ProtocolDao.initialize_market_dao(transact={'from': account}))


def test_initialize_shield_payout_dao(w3, Deployer, get_logs, ProtocolDao):
    tx_1_hash = ProtocolDao.initialize_shield_payout_dao(transact={'from': Deployer})
    tx_1_receipt = w3.eth.waitForTransactionReceipt(tx_1_hash)
    assert tx_1_receipt['status'] == 1
    logs_1 = get_logs(tx_1_hash, ProtocolDao, "DAOInitialized")
    assert logs_1[0].args._setter == Deployer
    assert logs_1[0].args._dao_type == PROTOCOL_CONSTANTS['DAO_SHIELD_PAYOUT']
    assert logs_1[0].args._dao_address == ProtocolDao.daos(PROTOCOL_CONSTANTS['DAO_SHIELD_PAYOUT'])


def test_initialize_shield_payout_dao_fail_when_called_by_non_deployer(w3, Deployer, assert_tx_failed, ProtocolDao):
    for account in w3.eth.accounts:
        if account == Deployer:
            continue
        assert_tx_failed(lambda: ProtocolDao.initialize_shield_payout_dao(transact={'from': account}))


def test_set_token_support(w3, Deployer, get_logs,
    get_CurrencyDao_contract,
    Lend_token,
    Governor, ProtocolDao):
    tx_1_hash = ProtocolDao.initialize_currency_dao(transact={'from': Deployer})
    tx_1_receipt = w3.eth.waitForTransactionReceipt(tx_1_hash)
    assert tx_1_receipt['status'] == 1
    CurrencyDao = get_CurrencyDao_contract(address=ProtocolDao.daos(PROTOCOL_CONSTANTS['DAO_CURRENCY']))
    assert not CurrencyDao.is_token_supported(Lend_token.address)
    tx_2_hash = ProtocolDao.set_token_support(Lend_token.address, True, transact={'from': Governor})
    tx_2_receipt = w3.eth.waitForTransactionReceipt(tx_2_hash)
    assert tx_2_receipt['status'] == 1
    assert CurrencyDao.is_token_supported(Lend_token.address)
