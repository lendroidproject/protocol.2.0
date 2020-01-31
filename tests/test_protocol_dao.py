import pytest

from web3 import Web3

from conftest import (
    PROTOCOL_CONSTANTS,
    POOL_NAME_REGISTRATION_MIN_STAKE_LST,
    INTEREST_POOL_DAO_MIN_MFT_FEE,
    INTEREST_POOL_DAO_FEE_MULTIPLIER_PER_MFT_COUNT,
    ZERO_ADDRESS
)


def test_change_governor(accounts, get_log_args, Governor, ProtocolDaoContract):
    _new_governor = accounts[5]
    assert ProtocolDaoContract.authorized_callers(PROTOCOL_CONSTANTS['CALLER_GOVERNOR']) == Governor
    tx = ProtocolDaoContract.change_governor(_new_governor, {'from': Governor})
    args = get_log_args(tx, 'AuthorizedCallerUpdated')
    assert args['_caller_type'] == PROTOCOL_CONSTANTS['CALLER_GOVERNOR']
    assert args['_caller'] == Governor
    assert args['_authorized_caller'] == _new_governor
    assert ProtocolDaoContract.authorized_callers(PROTOCOL_CONSTANTS['CALLER_GOVERNOR']) == _new_governor

    assert True


def test_change_governor_fail_when_called_by_non_governor(accounts, Governor, assert_tx_failed, ProtocolDaoContract):
    for account in accounts:
        if account == Governor:
            continue
        assert_tx_failed(lambda: ProtocolDaoContract.change_governor(account, {'from': account}))


def test_change_escape_hatch_manager(accounts, get_log_args, Governor, EscapeHatchManager, ProtocolDaoContract):
    _new_escape_hatch_manager = accounts[5]
    assert ProtocolDaoContract.authorized_callers(PROTOCOL_CONSTANTS['CALLER_ESCAPE_HATCH_MANAGER']) == EscapeHatchManager
    tx = ProtocolDaoContract.change_escape_hatch_manager(_new_escape_hatch_manager, {'from': Governor})
    args = get_log_args(tx, 'AuthorizedCallerUpdated')
    assert args['_caller_type'] == PROTOCOL_CONSTANTS['CALLER_ESCAPE_HATCH_MANAGER']
    assert args['_caller'] == Governor
    assert args['_authorized_caller'] == _new_escape_hatch_manager
    assert ProtocolDaoContract.authorized_callers(PROTOCOL_CONSTANTS['CALLER_ESCAPE_HATCH_MANAGER']) == _new_escape_hatch_manager


def test_change_escape_hatch_manager_fail_when_called_by_non_governor(accounts, Governor, assert_tx_failed, ProtocolDaoContract):
    for account in accounts:
        if account == Governor:
            continue
        assert_tx_failed(lambda: ProtocolDaoContract.change_escape_hatch_manager(account, {'from': account}))


def test_change_escape_hatch_token_holder(accounts, get_log_args, Governor, EscapeHatchTokenHolder, ProtocolDaoContract):
    _new_escape_hatch_token_holder = accounts[5]
    assert ProtocolDaoContract.authorized_callers(PROTOCOL_CONSTANTS['CALLER_ESCAPE_HATCH_TOKEN_HOLDER']) == EscapeHatchTokenHolder
    tx = ProtocolDaoContract.change_escape_hatch_token_holder(_new_escape_hatch_token_holder, {'from': Governor})
    args = get_log_args(tx, 'AuthorizedCallerUpdated')
    assert args['_caller_type'] == PROTOCOL_CONSTANTS['CALLER_ESCAPE_HATCH_TOKEN_HOLDER']
    assert args['_caller'] == Governor
    assert args['_authorized_caller'] == _new_escape_hatch_token_holder
    assert ProtocolDaoContract.authorized_callers(PROTOCOL_CONSTANTS['CALLER_ESCAPE_HATCH_TOKEN_HOLDER']) == _new_escape_hatch_token_holder


def test_change_escape_hatch_token_holder_fail_when_called_by_non_governor(accounts, Governor, assert_tx_failed, ProtocolDaoContract):
    for account in accounts:
        if account == Governor:
            continue
    assert_tx_failed(lambda: ProtocolDaoContract.change_escape_hatch_token_holder(account, {'from': account}))


def test_initialize_pool_name_registry(accounts, get_log_args, Deployer, ProtocolDaoContract):
    _stake = Web3.toWei(POOL_NAME_REGISTRATION_MIN_STAKE_LST, 'ether')
    tx = ProtocolDaoContract.initialize_pool_name_registry(_stake, {'from': Deployer})
    args = get_log_args(tx, 'RegistryInitialized')
    assert args['_setter'] == Deployer
    assert args['_template_type'] == PROTOCOL_CONSTANTS['REGISTRY_POOL_NAME']
    assert args['_registry_address'] == ProtocolDaoContract.registries(PROTOCOL_CONSTANTS['REGISTRY_POOL_NAME'])


def test_initialize_pool_name_registry_fail_when_called_by_non_deployer(accounts, Deployer, assert_tx_failed, ProtocolDaoContract):
    _stake = Web3.toWei(POOL_NAME_REGISTRATION_MIN_STAKE_LST, 'ether')
    for account in accounts:
        if account == Deployer:
            continue
        assert_tx_failed(lambda: ProtocolDaoContract.initialize_pool_name_registry(_stake, {'from': account}))


def test_initialize_position_registry(accounts, get_log_args, Deployer, ProtocolDaoContract):
    tx = ProtocolDaoContract.initialize_position_registry({'from': Deployer})
    args = get_log_args(tx, 'RegistryInitialized')
    assert args['_setter'] == Deployer
    assert args['_template_type'] == PROTOCOL_CONSTANTS['REGISTRY_POSITION']
    assert args['_registry_address'] == ProtocolDaoContract.registries(PROTOCOL_CONSTANTS['REGISTRY_POSITION'])


def test_initialize_position_registry_fail_when_called_by_non_deployer(accounts, Deployer, assert_tx_failed, ProtocolDaoContract):
    for account in accounts:
        if account == Deployer:
            continue
        assert_tx_failed(lambda: ProtocolDaoContract.initialize_position_registry({'from': account}))


def test_initialize_currency_dao(accounts, get_log_args, Deployer, ProtocolDaoContract):
    tx = ProtocolDaoContract.initialize_currency_dao({'from': Deployer})
    args = get_log_args(tx, 'DAOInitialized')
    assert args['_setter'] == Deployer
    assert args['_dao_type'] == PROTOCOL_CONSTANTS['DAO_CURRENCY']
    assert args['_dao_address'] == ProtocolDaoContract.daos(PROTOCOL_CONSTANTS['DAO_CURRENCY'])


def test_initialize_currency_dao_fail_when_called_by_non_deployer(accounts, Deployer, assert_tx_failed, ProtocolDaoContract):
    for account in accounts:
        if account == Deployer:
            continue
        assert_tx_failed(lambda: ProtocolDaoContract.initialize_currency_dao({'from': account}))


def test_initialize_interest_pool_dao(accounts, get_log_args, Deployer, ProtocolDaoContract):
    tx = ProtocolDaoContract.initialize_interest_pool_dao({'from': Deployer})
    args = get_log_args(tx, 'DAOInitialized')
    assert args['_setter'] == Deployer
    assert args['_dao_type'] == PROTOCOL_CONSTANTS['DAO_INTEREST_POOL']
    assert args['_dao_address'] == ProtocolDaoContract.daos(PROTOCOL_CONSTANTS['DAO_INTEREST_POOL'])


def test_initialize_interest_pool_dao_fail_when_called_by_non_deployer(accounts, Deployer, assert_tx_failed, ProtocolDaoContract):
    for account in accounts:
        if account == Deployer:
            continue
        assert_tx_failed(lambda: ProtocolDaoContract.initialize_interest_pool_dao({'from': account}))


def test_initialize_underwriter_pool_dao(accounts, get_log_args, Deployer, ProtocolDaoContract):
    tx = ProtocolDaoContract.initialize_underwriter_pool_dao({'from': Deployer})
    args = get_log_args(tx, 'DAOInitialized')
    assert args['_setter'] == Deployer
    assert args['_dao_type'] == PROTOCOL_CONSTANTS['DAO_UNDERWRITER_POOL']
    assert args['_dao_address'] == ProtocolDaoContract.daos(PROTOCOL_CONSTANTS['DAO_UNDERWRITER_POOL'])


def test_initialize_underwriter_pool_dao_fail_when_called_by_non_deployer(accounts, Deployer, assert_tx_failed, ProtocolDaoContract):
    for account in accounts:
        if account == Deployer:
            continue
        assert_tx_failed(lambda: ProtocolDaoContract.initialize_underwriter_pool_dao({'from': account}))


def test_initialize_market_dao(accounts, get_log_args, Deployer, ProtocolDaoContract):
    tx = ProtocolDaoContract.initialize_market_dao({'from': Deployer})
    args = get_log_args(tx, 'DAOInitialized')
    assert args['_setter'] == Deployer
    assert args['_dao_type'] == PROTOCOL_CONSTANTS['DAO_MARKET']
    assert args['_dao_address'] == ProtocolDaoContract.daos(PROTOCOL_CONSTANTS['DAO_MARKET'])


def test_initialize_market_dao_fail_when_called_by_non_deployer(accounts, Deployer, assert_tx_failed, ProtocolDaoContract):
    for account in accounts:
        if account == Deployer:
            continue
        assert_tx_failed(lambda: ProtocolDaoContract.initialize_market_dao({'from': account}))


def test_initialize_shield_payout_dao(accounts, get_log_args, Deployer, ProtocolDaoContract):
    tx = ProtocolDaoContract.initialize_shield_payout_dao({'from': Deployer})
    args = get_log_args(tx, 'DAOInitialized')
    assert args['_setter'] == Deployer
    assert args['_dao_type'] == PROTOCOL_CONSTANTS['DAO_SHIELD_PAYOUT']
    assert args['_dao_address'] == ProtocolDaoContract.daos(PROTOCOL_CONSTANTS['DAO_SHIELD_PAYOUT'])


def test_initialize_shield_payout_dao_fail_when_called_by_non_deployer(accounts, Deployer, assert_tx_failed, ProtocolDaoContract):
    for account in accounts:
        if account == Deployer:
            continue
        assert_tx_failed(lambda: ProtocolDaoContract.initialize_shield_payout_dao({'from': account}))


def test_set_token_support(accounts, Deployer,
    get_CurrencyDao_contract,
    Lend_token,
    Governor, ProtocolDaoContract):
    anyone = accounts[-1]
    ProtocolDaoContract.initialize_currency_dao({'from': Deployer})
    CurrencyDao = get_CurrencyDao_contract(address=ProtocolDaoContract.daos(PROTOCOL_CONSTANTS['DAO_CURRENCY']))
    assert not CurrencyDao.is_token_supported(Lend_token.address, {'from': anyone})
    ProtocolDaoContract.set_token_support(Lend_token.address, True, {'from': Governor})
    assert CurrencyDao.is_token_supported(Lend_token.address, {'from': anyone})


def test_set_minimum_mft_fee_interest_pool_dao(accounts, Deployer,
    get_InterestPoolDao_contract,
    Governor, ProtocolDaoContract):
    anyone = accounts[-1]
    ProtocolDaoContract.initialize_interest_pool_dao({'from': Deployer})
    InterestPoolDao = get_InterestPoolDao_contract(address=ProtocolDaoContract.daos(PROTOCOL_CONSTANTS['DAO_INTEREST_POOL']))
    assert InterestPoolDao.minimum_mft_fee({'from': anyone}) == 0
    tx_2_hash = ProtocolDaoContract.set_minimum_mft_fee(
        PROTOCOL_CONSTANTS['DAO_INTEREST_POOL'],
        Web3.toWei(INTEREST_POOL_DAO_MIN_MFT_FEE, 'ether'),
        {'from': Governor})
    assert InterestPoolDao.minimum_mft_fee({'from': anyone}) == Web3.toWei(INTEREST_POOL_DAO_MIN_MFT_FEE, 'ether')


def test_set_minimum_mft_fee_interest_pool_dao_fail_when_called_by_non_governor(accounts, Deployer, Governor, assert_tx_failed, ProtocolDaoContract):
    ProtocolDaoContract.initialize_interest_pool_dao({'from': Deployer})
    for account in accounts:
        if account == Governor:
            continue
        assert_tx_failed(lambda: ProtocolDaoContract.set_minimum_mft_fee(
            PROTOCOL_CONSTANTS['DAO_INTEREST_POOL'],
            Web3.toWei(INTEREST_POOL_DAO_MIN_MFT_FEE, 'ether'),
            {'from': account}))


def test_set_fee_multiplier_per_mft_count_interest_pool_dao(accounts, Deployer,
    get_InterestPoolDao_contract,
    Governor, ProtocolDaoContract):
    anyone = accounts[-1]
    ProtocolDaoContract.initialize_interest_pool_dao({'from': Deployer})
    InterestPoolDao = get_InterestPoolDao_contract(address=ProtocolDaoContract.daos(PROTOCOL_CONSTANTS['DAO_INTEREST_POOL']))
    assert InterestPoolDao.fee_multiplier_per_mft_count(0, {'from': anyone}) == 0
    tx_hash = ProtocolDaoContract.set_fee_multiplier_per_mft_count(
        PROTOCOL_CONSTANTS['DAO_INTEREST_POOL'], Web3.toWei(0, 'ether'),
        Web3.toWei(INTEREST_POOL_DAO_FEE_MULTIPLIER_PER_MFT_COUNT, 'ether'),
        {'from': Governor, 'gas': 75000})
    assert InterestPoolDao.fee_multiplier_per_mft_count(0, {'from': anyone}) == Web3.toWei(INTEREST_POOL_DAO_FEE_MULTIPLIER_PER_MFT_COUNT, 'ether')


def test_set_fee_multiplier_per_mft_count_interest_pool_dao_fail_when_called_by_non_governor(accounts, Deployer, Governor, assert_tx_failed, ProtocolDaoContract):
    ProtocolDaoContract.initialize_interest_pool_dao({'from': Deployer})
    for account in accounts:
        if account == Governor:
            continue
        assert_tx_failed(lambda: ProtocolDaoContract.set_minimum_mft_fee(
            PROTOCOL_CONSTANTS['DAO_INTEREST_POOL'],
            Web3.toWei(INTEREST_POOL_DAO_MIN_MFT_FEE, 'ether'),
            {'from': account}))
