import pytest

from web3 import Web3

from conftest import (
    PROTOCOL_CONSTANTS,
    POOL_NAME_REGISTRATION_MIN_STAKE_LST,
    INTEREST_POOL_DAO_MIN_MFT_FEE,
    INTEREST_POOL_DAO_FEE_MULTIPLIER_PER_MFT_COUNT,
    INTEREST_POOL_DAO_MAXIMUM_MFT_SUPPORT_COUNT,
    MAX_LIABILITY_CURENCY_MARKET,
    AUCTION_SLIPPAGE_PERCENTAGE,
    AUCTION_MAXIMUM_DISCOUNT_PERCENTAGE,
    AUCTION_DISCOUNT_DURATION,
    ZERO_ADDRESS,
    H20
)


def test_change_governor(accounts, assert_tx_failed, get_log_args, Governor, ProtocolDaoContract):
    _new_governor = accounts[5]
    assert ProtocolDaoContract.authorized_callers(PROTOCOL_CONSTANTS['CALLER_GOVERNOR']) == Governor
    # Tx fails when called by non-Governor
    for account in accounts:
        if account == Governor:
            continue
        assert_tx_failed(lambda: ProtocolDaoContract.change_governor(account, {'from': account}))
    args = get_log_args(ProtocolDaoContract.change_governor(_new_governor, {'from': Governor}), 'AuthorizedCallerUpdated')
    assert args['_caller_type'] == PROTOCOL_CONSTANTS['CALLER_GOVERNOR']
    assert args['_caller'] == Governor
    assert args['_authorized_caller'] == _new_governor
    assert ProtocolDaoContract.authorized_callers(PROTOCOL_CONSTANTS['CALLER_GOVERNOR']) == _new_governor
    # Tx fails when called by non-_new_governor
    for account in accounts:
        if account == _new_governor:
            continue
        assert_tx_failed(lambda: ProtocolDaoContract.change_governor(account, {'from': account}))


    assert True


def test_change_escape_hatch_manager(accounts, assert_tx_failed, get_log_args, Governor, EscapeHatchManager, ProtocolDaoContract):
    _new_escape_hatch_manager = accounts[5]
    assert ProtocolDaoContract.authorized_callers(PROTOCOL_CONSTANTS['CALLER_ESCAPE_HATCH_MANAGER']) == EscapeHatchManager
    args = get_log_args(ProtocolDaoContract.change_escape_hatch_manager(_new_escape_hatch_manager, {'from': Governor}), 'AuthorizedCallerUpdated')
    assert args['_caller_type'] == PROTOCOL_CONSTANTS['CALLER_ESCAPE_HATCH_MANAGER']
    assert args['_caller'] == Governor
    assert args['_authorized_caller'] == _new_escape_hatch_manager
    assert ProtocolDaoContract.authorized_callers(PROTOCOL_CONSTANTS['CALLER_ESCAPE_HATCH_MANAGER']) == _new_escape_hatch_manager
    # Tx fails when called by non-Governor
    for account in accounts:
        if account == Governor:
            continue
        assert_tx_failed(lambda: ProtocolDaoContract.change_escape_hatch_manager(account, {'from': account}))


def test_change_escape_hatch_token_holder(accounts, assert_tx_failed, get_log_args, Governor, EscapeHatchTokenHolder, ProtocolDaoContract):
    _new_escape_hatch_token_holder = accounts[5]
    assert ProtocolDaoContract.authorized_callers(PROTOCOL_CONSTANTS['CALLER_ESCAPE_HATCH_TOKEN_HOLDER']) == EscapeHatchTokenHolder
    args = get_log_args(ProtocolDaoContract.change_escape_hatch_token_holder(_new_escape_hatch_token_holder, {'from': Governor}), 'AuthorizedCallerUpdated')
    assert args['_caller_type'] == PROTOCOL_CONSTANTS['CALLER_ESCAPE_HATCH_TOKEN_HOLDER']
    assert args['_caller'] == Governor
    assert args['_authorized_caller'] == _new_escape_hatch_token_holder
    assert ProtocolDaoContract.authorized_callers(PROTOCOL_CONSTANTS['CALLER_ESCAPE_HATCH_TOKEN_HOLDER']) == _new_escape_hatch_token_holder
    # Tx fails when called by non-Governor
    for account in accounts:
        if account == Governor:
            continue
        assert_tx_failed(lambda: ProtocolDaoContract.change_escape_hatch_token_holder(account, {'from': account}))


def test_initialize_pool_name_registry(accounts, assert_tx_failed, get_log_args, Deployer, ProtocolDaoContract):
    _stake = Web3.toWei(POOL_NAME_REGISTRATION_MIN_STAKE_LST, 'ether')
    args = get_log_args(ProtocolDaoContract.initialize_pool_name_registry(_stake, {'from': Deployer}), 'RegistryInitialized')
    assert args['_setter'] == Deployer
    assert args['_template_type'] == PROTOCOL_CONSTANTS['REGISTRY_POOL_NAME']
    assert args['_registry_address'] == ProtocolDaoContract.registries(PROTOCOL_CONSTANTS['REGISTRY_POOL_NAME'])
    # Tx fails when called by non-Deployer
    for account in accounts:
        if account == Deployer:
            continue
        assert_tx_failed(lambda: ProtocolDaoContract.initialize_pool_name_registry(Web3.toWei(POOL_NAME_REGISTRATION_MIN_STAKE_LST, 'ether'), {'from': account}))


def test_initialize_position_registry(accounts, assert_tx_failed, get_log_args, Deployer, ProtocolDaoContract):
    args = get_log_args(ProtocolDaoContract.initialize_position_registry({'from': Deployer}), 'RegistryInitialized')
    assert args['_setter'] == Deployer
    assert args['_template_type'] == PROTOCOL_CONSTANTS['REGISTRY_POSITION']
    assert args['_registry_address'] == ProtocolDaoContract.registries(PROTOCOL_CONSTANTS['REGISTRY_POSITION'])
    # Tx fails when called by non-Deployer
    for account in accounts:
        if account == Deployer:
            continue
        assert_tx_failed(lambda: ProtocolDaoContract.initialize_position_registry({'from': account}))


def test_initialize_currency_dao(accounts, assert_tx_failed, get_log_args, Deployer, ProtocolDaoContract):
    args = get_log_args(ProtocolDaoContract.initialize_currency_dao({'from': Deployer}), 'DAOInitialized')
    assert args['_setter'] == Deployer
    assert args['_dao_type'] == PROTOCOL_CONSTANTS['DAO_CURRENCY']
    assert args['_dao_address'] == ProtocolDaoContract.daos(PROTOCOL_CONSTANTS['DAO_CURRENCY'])
    # Tx fails when called by non-Deployer
    for account in accounts:
        if account == Deployer:
            continue
        assert_tx_failed(lambda: ProtocolDaoContract.initialize_currency_dao({'from': account}))


def test_initialize_interest_pool_dao(accounts, assert_tx_failed, get_log_args, Deployer, ProtocolDaoContract):
    args = get_log_args(ProtocolDaoContract.initialize_interest_pool_dao({'from': Deployer}), 'DAOInitialized')
    assert args['_setter'] == Deployer
    assert args['_dao_type'] == PROTOCOL_CONSTANTS['DAO_INTEREST_POOL']
    assert args['_dao_address'] == ProtocolDaoContract.daos(PROTOCOL_CONSTANTS['DAO_INTEREST_POOL'])
    # Tx fails when called by non-Deployer
    for account in accounts:
        if account == Deployer:
            continue
        assert_tx_failed(lambda: ProtocolDaoContract.initialize_interest_pool_dao({'from': account}))


def test_initialize_underwriter_pool_dao(accounts, assert_tx_failed, get_log_args, Deployer, ProtocolDaoContract):
    args = get_log_args(ProtocolDaoContract.initialize_underwriter_pool_dao({'from': Deployer}), 'DAOInitialized')
    assert args['_setter'] == Deployer
    assert args['_dao_type'] == PROTOCOL_CONSTANTS['DAO_UNDERWRITER_POOL']
    assert args['_dao_address'] == ProtocolDaoContract.daos(PROTOCOL_CONSTANTS['DAO_UNDERWRITER_POOL'])
    # Tx fails when called by non-Deployer
    for account in accounts:
        if account == Deployer:
            continue
        assert_tx_failed(lambda: ProtocolDaoContract.initialize_underwriter_pool_dao({'from': account}))


def test_initialize_market_dao(accounts, assert_tx_failed, get_log_args, Deployer, ProtocolDaoContract):
    args = get_log_args(ProtocolDaoContract.initialize_market_dao({'from': Deployer}), 'DAOInitialized')
    assert args['_setter'] == Deployer
    assert args['_dao_type'] == PROTOCOL_CONSTANTS['DAO_MARKET']
    assert args['_dao_address'] == ProtocolDaoContract.daos(PROTOCOL_CONSTANTS['DAO_MARKET'])
    # Tx fails when called by non-Deployer
    for account in accounts:
        if account == Deployer:
            continue
        assert_tx_failed(lambda: ProtocolDaoContract.initialize_market_dao({'from': account}))


def test_initialize_shield_payout_dao(accounts, assert_tx_failed, get_log_args, Deployer, ProtocolDaoContract):
    args = get_log_args(ProtocolDaoContract.initialize_shield_payout_dao({'from': Deployer}), 'DAOInitialized')
    assert args['_setter'] == Deployer
    assert args['_dao_type'] == PROTOCOL_CONSTANTS['DAO_SHIELD_PAYOUT']
    assert args['_dao_address'] == ProtocolDaoContract.daos(PROTOCOL_CONSTANTS['DAO_SHIELD_PAYOUT'])
    # Tx fails when called by non-Deployer
    for account in accounts:
        if account == Deployer:
            continue
        assert_tx_failed(lambda: ProtocolDaoContract.initialize_shield_payout_dao({'from': account}))


def test_activate_public_contributions(accounts, assert_tx_failed, get_log_args, Governor, ProtocolDaoContract):
    anyone = accounts[-1]
    assert not ProtocolDaoContract.public_contributions_activated({'from': anyone})
    # Tx fails when called by non-Governor
    for account in accounts:
        if account == Governor:
            continue
        assert_tx_failed(lambda: ProtocolDaoContract.activate_public_contributions({'from': account}))
    ProtocolDaoContract.activate_public_contributions({'from': Governor})
    assert ProtocolDaoContract.public_contributions_activated({'from': anyone})


def test_activate_non_standard_expiries(accounts, assert_tx_failed, get_log_args, Governor, ProtocolDaoContract):
    anyone = accounts[-1]
    assert not ProtocolDaoContract.non_standard_expiries_activated({'from': anyone})
    # Tx fails when called by non-Governor
    for account in accounts:
        if account == Governor:
            continue
        assert_tx_failed(lambda: ProtocolDaoContract.activate_non_standard_expiries({'from': account}))
    ProtocolDaoContract.activate_non_standard_expiries({'from': Governor})
    assert ProtocolDaoContract.non_standard_expiries_activated({'from': anyone})


def test_set_expiry_support(accounts, assert_tx_failed, get_log_args, Governor, ProtocolDaoContract):
    anyone = accounts[-1]
    assert ProtocolDaoContract.expiries__expiry_timestamp(H20, {'from': anyone}) == 0
    assert ProtocolDaoContract.expiries__expiry_label(H20, {'from': anyone}) == ""
    assert not ProtocolDaoContract.expiries__is_active(H20, {'from': anyone})
    # Tx fails when called by non-Governor, to register support for expiry
    for account in accounts:
        if account == Governor:
            continue
        assert_tx_failed(lambda: ProtocolDaoContract.set_expiry_support(H20, "H20", True, {'from': account}))
    # Governor registers support for expiry
    ProtocolDaoContract.set_expiry_support(H20, "H20", True, {'from': Governor})
    assert ProtocolDaoContract.expiries__expiry_timestamp(H20, {'from': anyone}) == H20
    assert ProtocolDaoContract.expiries__expiry_label(H20, {'from': anyone}) == "H20"
    assert ProtocolDaoContract.expiries__is_active(H20, {'from': anyone})
    # Tx fails when timestamp is 0
    assert_tx_failed(lambda: ProtocolDaoContract.set_expiry_support(0, "000", True, {'from': Governor}))
    # Tx fails when called by non-Governor, to register support for expiry
    for account in accounts:
        if account == Governor:
            continue
        assert_tx_failed(lambda: ProtocolDaoContract.set_expiry_support(H20, "H20", False, {'from': account}))
    # Governor registers support for expiry
    ProtocolDaoContract.set_expiry_support(H20, "H20", False, {'from': Governor})
    assert ProtocolDaoContract.expiries__expiry_timestamp(H20, {'from': anyone}) == H20
    assert ProtocolDaoContract.expiries__expiry_label(H20, {'from': anyone}) == "H20"
    assert not ProtocolDaoContract.expiries__is_active(H20, {'from': anyone})


def test_set_registry(accounts, assert_tx_failed, Deployer, Governor,
    get_MarketDao_contract, get_PositionRegistry_contract, ProtocolDaoContract):
    anyone = accounts[-1]
    MarketDaoContract = get_MarketDao_contract(address=ProtocolDaoContract.daos(PROTOCOL_CONSTANTS['DAO_MARKET']))
    PositionRegistry = get_PositionRegistry_contract(address=ProtocolDaoContract.registries(PROTOCOL_CONSTANTS['REGISTRY_POSITION']))
    NewPositionRegistry = get_PositionRegistry_contract()
    # Tx fails when target DAO is not initialized
    assert_tx_failed(lambda: ProtocolDaoContract.set_registry(
        PROTOCOL_CONSTANTS['DAO_MARKET'], PROTOCOL_CONSTANTS['REGISTRY_POSITION'], NewPositionRegistry.address, {'from': Governor}))
    # Initialize target DAO
    ProtocolDaoContract.initialize_market_dao({'from': Deployer})
    # Tx fails when called by non-Governor
    # Tx also fails for invalid DAO and Registry types, or contract address
    for account in accounts:
        if account == Governor:
            continue
        assert_tx_failed(lambda: ProtocolDaoContract.set_registry(
            PROTOCOL_CONSTANTS['DAO_MARKET'], PROTOCOL_CONSTANTS['REGISTRY_POSITION'], NewPositionRegistry.address, {'from': account}))
        assert_tx_failed(lambda: ProtocolDaoContract.set_registry(
            PROTOCOL_CONSTANTS['DAO_MARKET'], PROTOCOL_CONSTANTS['REGISTRY_POSITION'], account, {'from': Governor}))
    assert_tx_failed(lambda: ProtocolDaoContract.set_registry(
        0, PROTOCOL_CONSTANTS['REGISTRY_POSITION'], NewPositionRegistry.address, {'from': Governor}))
    assert_tx_failed(lambda: ProtocolDaoContract.set_registry(
        PROTOCOL_CONSTANTS['DAO_MARKET'], 0, NewPositionRegistry.address, {'from': Governor}))
    # Tx fails for Invalid contract address
    assert_tx_failed(lambda: ProtocolDaoContract.set_registry(
        PROTOCOL_CONSTANTS['DAO_MARKET'], PROTOCOL_CONSTANTS['REGISTRY_POSITION'], ZERO_ADDRESS, {'from': Governor}))
    # Tx fails for MarketDao and invalid Registry type
    assert_tx_failed(lambda: ProtocolDaoContract.set_registry(
        PROTOCOL_CONSTANTS['DAO_MARKET'], PROTOCOL_CONSTANTS['REGISTRY_POOL_NAME'], NewPositionRegistry.address, {'from': Governor}))
    assert MarketDaoContract.registries(PROTOCOL_CONSTANTS['REGISTRY_POSITION'], {'from': anyone}) == PositionRegistry.address
    # set registry
    ProtocolDaoContract.set_registry(
        PROTOCOL_CONSTANTS['DAO_MARKET'], PROTOCOL_CONSTANTS['REGISTRY_POSITION'], NewPositionRegistry.address, {'from': Governor})
    assert MarketDaoContract.registries(PROTOCOL_CONSTANTS['REGISTRY_POSITION'], {'from': anyone}) == NewPositionRegistry.address


def test_set_pool_name_registration_minimum_stake(accounts, assert_tx_failed, Deployer, Governor,
    get_PoolNameRegistry_contract, ProtocolDaoContract):
    anyone = accounts[-1]
    PoolNameRegistry = get_PoolNameRegistry_contract(address=ProtocolDaoContract.registries(PROTOCOL_CONSTANTS['REGISTRY_POOL_NAME']))
    # Tx fails when target DAO is not initialized
    assert_tx_failed(lambda: ProtocolDaoContract.set_pool_name_registration_minimum_stake(
        Web3.toWei(POOL_NAME_REGISTRATION_MIN_STAKE_LST, 'ether'), {'from': Governor}))
    # Initialize target DAO
    ProtocolDaoContract.initialize_pool_name_registry(Web3.toWei(POOL_NAME_REGISTRATION_MIN_STAKE_LST, 'ether'), {'from': Deployer})
    # Tx fails when called by non-Governor
    for account in accounts:
        if account == Governor:
            continue
        assert_tx_failed(lambda: ProtocolDaoContract.set_pool_name_registration_minimum_stake(
            Web3.toWei(POOL_NAME_REGISTRATION_MIN_STAKE_LST, 'ether'), {'from': account}))
    # Tx fails for 0 value
    assert_tx_failed(lambda: ProtocolDaoContract.set_pool_name_registration_minimum_stake(
        0, {'from': Governor}))
    assert PoolNameRegistry.name_registration_minimum_stake({'from': anyone}) == Web3.toWei(POOL_NAME_REGISTRATION_MIN_STAKE_LST, 'ether')
    # set maximum_market_liability
    ProtocolDaoContract.set_pool_name_registration_minimum_stake(
        Web3.toWei(100000, 'ether'), {'from': Governor})
    assert PoolNameRegistry.name_registration_minimum_stake({'from': anyone}) == Web3.toWei(100000, 'ether')


def test_set_pool_name_registration_stake_lookup(accounts, assert_tx_failed, Deployer, Governor,
    get_PoolNameRegistry_contract, ProtocolDaoContract):
    anyone = accounts[-1]
    PoolNameRegistry = get_PoolNameRegistry_contract(address=ProtocolDaoContract.registries(PROTOCOL_CONSTANTS['REGISTRY_POOL_NAME']))
    # Tx fails when target DAO is not initialized
    assert_tx_failed(lambda: ProtocolDaoContract.set_pool_name_registration_stake_lookup(
        1, Web3.toWei(10000000, 'ether'), {'from': Governor}))
    # Initialize target DAO
    ProtocolDaoContract.initialize_pool_name_registry(Web3.toWei(POOL_NAME_REGISTRATION_MIN_STAKE_LST, 'ether'), {'from': Deployer})
    # Tx fails when called by non-Governor
    for account in accounts:
        if account == Governor:
            continue
        assert_tx_failed(lambda: ProtocolDaoContract.set_pool_name_registration_stake_lookup(
            1, Web3.toWei(10000000, 'ether'), {'from': account}))
    # Tx fails for 0 values
    assert_tx_failed(lambda: ProtocolDaoContract.set_pool_name_registration_stake_lookup(
        0, Web3.toWei(10000000, 'ether'), {'from': Governor}))
    assert_tx_failed(lambda: ProtocolDaoContract.set_pool_name_registration_stake_lookup(
        1, 0, {'from': Governor}))
    assert PoolNameRegistry.name_registration_stake_lookup__stake(1, {'from': anyone}) == 0
    # set maximum_market_liability
    ProtocolDaoContract.set_pool_name_registration_stake_lookup(
        1, Web3.toWei(10000000, 'ether'), {'from': Governor})
    assert PoolNameRegistry.name_registration_stake_lookup__stake(1, {'from': anyone}) == Web3.toWei(10000000, 'ether')


def test_set_token_support(accounts, assert_tx_failed, Deployer,
    get_CurrencyDao_contract,
    Lend_token,
    Governor, ProtocolDaoContract):
    anyone = accounts[-1]
    CurrencyDao = get_CurrencyDao_contract(address=ProtocolDaoContract.daos(PROTOCOL_CONSTANTS['DAO_CURRENCY']))
    # Tx fails when target DAO is not initialized
    assert_tx_failed(lambda: ProtocolDaoContract.set_token_support(Lend_token.address, True, {'from': Governor}))
    ProtocolDaoContract.initialize_currency_dao({'from': Deployer})
    # Tx fails for invalid token
    assert_tx_failed(lambda: ProtocolDaoContract.set_token_support(ZERO_ADDRESS, True, {'from': Governor}))
    for account in accounts:
        if account == Governor:
            continue
        assert_tx_failed(lambda: ProtocolDaoContract.set_token_support(account, True, {'from': account}))
    # Tx fails when called by non-Governor
    for account in accounts:
        if account == Governor:
            continue
        assert_tx_failed(lambda: ProtocolDaoContract.set_token_support(Lend_token.address, True, {'from': account}))
    assert not CurrencyDao.is_token_supported(Lend_token.address, {'from': anyone})
    ProtocolDaoContract.set_token_support(Lend_token.address, True, {'from': Governor})
    assert CurrencyDao.is_token_supported(Lend_token.address, {'from': anyone})


def test_set_minimum_mft_fee(accounts, assert_tx_failed, Deployer,
    get_InterestPoolDao_contract, get_UnderwriterPoolDao_contract,
    Governor, ProtocolDaoContract):
    anyone = accounts[-1]
    InterestPoolDao = get_InterestPoolDao_contract(address=ProtocolDaoContract.daos(PROTOCOL_CONSTANTS['DAO_INTEREST_POOL']))
    UnderwriterPoolDao = get_UnderwriterPoolDao_contract(address=ProtocolDaoContract.daos(PROTOCOL_CONSTANTS['DAO_UNDERWRITER_POOL']))
    # Tx fails when target DAO is not initialized
    assert_tx_failed(lambda: ProtocolDaoContract.set_minimum_mft_fee(
        PROTOCOL_CONSTANTS['DAO_INTEREST_POOL'],
        Web3.toWei(INTEREST_POOL_DAO_MIN_MFT_FEE, 'ether'),
        {'from': Governor}))
    assert_tx_failed(lambda: ProtocolDaoContract.set_minimum_mft_fee(
        PROTOCOL_CONSTANTS['DAO_UNDERWRITER_POOL'],
        Web3.toWei(INTEREST_POOL_DAO_MIN_MFT_FEE, 'ether'),
        {'from': Governor}))
    ProtocolDaoContract.initialize_interest_pool_dao({'from': Deployer})
    ProtocolDaoContract.initialize_underwriter_pool_dao({'from': Deployer})
    # Tx fails for invalid target DAO
    assert_tx_failed(lambda: ProtocolDaoContract.set_minimum_mft_fee(
        PROTOCOL_CONSTANTS['DAO_SHIELD_PAYOUT'],
        Web3.toWei(INTEREST_POOL_DAO_MIN_MFT_FEE, 'ether'),
        {'from': Governor}))
    # Tx fails for 0 value
    assert_tx_failed(lambda: ProtocolDaoContract.set_minimum_mft_fee(
        PROTOCOL_CONSTANTS['DAO_INTEREST_POOL'], Web3.toWei(0, 'ether'),
        {'from': Governor}))
    assert_tx_failed(lambda: ProtocolDaoContract.set_minimum_mft_fee(
        PROTOCOL_CONSTANTS['DAO_UNDERWRITER_POOL'], Web3.toWei(0, 'ether'),
        {'from': Governor}))
    assert InterestPoolDao.minimum_mft_fee({'from': anyone}) == 0
    ProtocolDaoContract.set_minimum_mft_fee(
        PROTOCOL_CONSTANTS['DAO_INTEREST_POOL'],
        Web3.toWei(INTEREST_POOL_DAO_MIN_MFT_FEE, 'ether'),
        {'from': Governor})
    assert InterestPoolDao.minimum_mft_fee({'from': anyone}) == Web3.toWei(INTEREST_POOL_DAO_MIN_MFT_FEE, 'ether')
    assert UnderwriterPoolDao.minimum_mft_fee({'from': anyone}) == 0
    ProtocolDaoContract.set_minimum_mft_fee(
        PROTOCOL_CONSTANTS['DAO_UNDERWRITER_POOL'],
        Web3.toWei(INTEREST_POOL_DAO_MIN_MFT_FEE, 'ether'),
        {'from': Governor})
    assert UnderwriterPoolDao.minimum_mft_fee({'from': anyone}) == Web3.toWei(INTEREST_POOL_DAO_MIN_MFT_FEE, 'ether')
    # Tx fails when called by non-Governor
    for account in accounts:
        if account == Governor:
            continue
        assert_tx_failed(lambda: ProtocolDaoContract.set_minimum_mft_fee(
            PROTOCOL_CONSTANTS['DAO_INTEREST_POOL'],
            Web3.toWei(INTEREST_POOL_DAO_MIN_MFT_FEE, 'ether'),
            {'from': account}))
        assert_tx_failed(lambda: ProtocolDaoContract.set_minimum_mft_fee(
            PROTOCOL_CONSTANTS['DAO_UNDERWRITER_POOL'],
            Web3.toWei(INTEREST_POOL_DAO_MIN_MFT_FEE, 'ether'),
            {'from': account}))


def test_set_fee_multiplier_per_mft_count(accounts, assert_tx_failed, Deployer,
    get_InterestPoolDao_contract, get_UnderwriterPoolDao_contract,
    Governor, ProtocolDaoContract):
    anyone = accounts[-1]
    InterestPoolDao = get_InterestPoolDao_contract(address=ProtocolDaoContract.daos(PROTOCOL_CONSTANTS['DAO_INTEREST_POOL']))
    UnderwriterPoolDao = get_UnderwriterPoolDao_contract(address=ProtocolDaoContract.daos(PROTOCOL_CONSTANTS['DAO_UNDERWRITER_POOL']))
    # Tx fails when target DAO is not initialized
    assert_tx_failed(lambda: ProtocolDaoContract.set_fee_multiplier_per_mft_count(
        PROTOCOL_CONSTANTS['DAO_INTEREST_POOL'], Web3.toWei(0, 'ether'), Web3.toWei(INTEREST_POOL_DAO_FEE_MULTIPLIER_PER_MFT_COUNT, 'ether'),
        {'from': Governor, 'gas': 75000}))
    assert_tx_failed(lambda: ProtocolDaoContract.set_fee_multiplier_per_mft_count(
        PROTOCOL_CONSTANTS['DAO_UNDERWRITER_POOL'], Web3.toWei(0, 'ether'), Web3.toWei(INTEREST_POOL_DAO_FEE_MULTIPLIER_PER_MFT_COUNT, 'ether'),
        {'from': Governor, 'gas': 75000}))
    # Initialize target DAOs
    ProtocolDaoContract.initialize_interest_pool_dao({'from': Deployer})
    ProtocolDaoContract.initialize_underwriter_pool_dao({'from': Deployer})
    # Tx fails for invalid target DAO
    assert_tx_failed(lambda: ProtocolDaoContract.set_fee_multiplier_per_mft_count(
        PROTOCOL_CONSTANTS['DAO_SHIELD_PAYOUT'], Web3.toWei(0, 'ether'), Web3.toWei(INTEREST_POOL_DAO_FEE_MULTIPLIER_PER_MFT_COUNT, 'ether'),
        {'from': Governor, 'gas': 75000}))
    # Tx fails for 0 value
    assert_tx_failed(lambda: ProtocolDaoContract.set_fee_multiplier_per_mft_count(
        PROTOCOL_CONSTANTS['DAO_INTEREST_POOL'], Web3.toWei(0, 'ether'), Web3.toWei(0, 'ether'),
        {'from': Governor, 'gas': 75000}))
    assert_tx_failed(lambda: ProtocolDaoContract.set_fee_multiplier_per_mft_count(
        PROTOCOL_CONSTANTS['DAO_UNDERWRITER_POOL'], Web3.toWei(0, 'ether'), Web3.toWei(0, 'ether'),
        {'from': Governor, 'gas': 75000}))
    assert InterestPoolDao.fee_multiplier_per_mft_count(0, {'from': anyone}) == 0
    ProtocolDaoContract.set_fee_multiplier_per_mft_count(
        PROTOCOL_CONSTANTS['DAO_INTEREST_POOL'], Web3.toWei(0, 'ether'),
        Web3.toWei(INTEREST_POOL_DAO_FEE_MULTIPLIER_PER_MFT_COUNT, 'ether'),
        {'from': Governor, 'gas': 75000})
    assert InterestPoolDao.fee_multiplier_per_mft_count(0, {'from': anyone}) == Web3.toWei(INTEREST_POOL_DAO_FEE_MULTIPLIER_PER_MFT_COUNT, 'ether')
    assert UnderwriterPoolDao.fee_multiplier_per_mft_count(0, {'from': anyone}) == 0
    ProtocolDaoContract.set_fee_multiplier_per_mft_count(
        PROTOCOL_CONSTANTS['DAO_UNDERWRITER_POOL'], Web3.toWei(0, 'ether'),
        Web3.toWei(INTEREST_POOL_DAO_FEE_MULTIPLIER_PER_MFT_COUNT, 'ether'),
        {'from': Governor, 'gas': 75000})
    assert UnderwriterPoolDao.fee_multiplier_per_mft_count(0, {'from': anyone}) == Web3.toWei(INTEREST_POOL_DAO_FEE_MULTIPLIER_PER_MFT_COUNT, 'ether')
    # Tx fails when called by non-Governor
    for account in accounts:
        if account == Governor:
            continue
        assert_tx_failed(lambda: ProtocolDaoContract.set_fee_multiplier_per_mft_count(
            PROTOCOL_CONSTANTS['DAO_INTEREST_POOL'], Web3.toWei(0, 'ether'),
            Web3.toWei(INTEREST_POOL_DAO_FEE_MULTIPLIER_PER_MFT_COUNT, 'ether'),
            {'from': account, 'gas': 75000}))
        assert_tx_failed(lambda: ProtocolDaoContract.set_fee_multiplier_per_mft_count(
            PROTOCOL_CONSTANTS['DAO_UNDERWRITER_POOL'], Web3.toWei(0, 'ether'),
            Web3.toWei(INTEREST_POOL_DAO_FEE_MULTIPLIER_PER_MFT_COUNT, 'ether'),
            {'from': account, 'gas': 75000}))


def test_set_maximum_mft_support_count(accounts, assert_tx_failed, Deployer,
    get_InterestPoolDao_contract, get_UnderwriterPoolDao_contract,
    Governor, ProtocolDaoContract):
    anyone = accounts[-1]
    InterestPoolDao = get_InterestPoolDao_contract(address=ProtocolDaoContract.daos(PROTOCOL_CONSTANTS['DAO_INTEREST_POOL']))
    UnderwriterPoolDao = get_UnderwriterPoolDao_contract(address=ProtocolDaoContract.daos(PROTOCOL_CONSTANTS['DAO_UNDERWRITER_POOL']))
    # Tx fails when target DAO is not initialized
    assert_tx_failed(lambda: ProtocolDaoContract.set_maximum_mft_support_count(
        PROTOCOL_CONSTANTS['DAO_INTEREST_POOL'], Web3.toWei(INTEREST_POOL_DAO_MAXIMUM_MFT_SUPPORT_COUNT, 'ether'),
        {'from': Governor}))
    assert_tx_failed(lambda: ProtocolDaoContract.set_maximum_mft_support_count(
        PROTOCOL_CONSTANTS['DAO_UNDERWRITER_POOL'], Web3.toWei(INTEREST_POOL_DAO_MAXIMUM_MFT_SUPPORT_COUNT, 'ether'),
        {'from': Governor}))
    # Initialize target DAOs
    ProtocolDaoContract.initialize_interest_pool_dao({'from': Deployer})
    ProtocolDaoContract.initialize_underwriter_pool_dao({'from': Deployer})
    # Tx fails for invalid target DAO
    assert_tx_failed(lambda: ProtocolDaoContract.set_maximum_mft_support_count(
        PROTOCOL_CONSTANTS['DAO_SHIELD_PAYOUT'], Web3.toWei(INTEREST_POOL_DAO_MAXIMUM_MFT_SUPPORT_COUNT, 'ether'),
        {'from': Governor}))
    # Tx fails for 0 value
    assert_tx_failed(lambda: ProtocolDaoContract.set_maximum_mft_support_count(
        PROTOCOL_CONSTANTS['DAO_INTEREST_POOL'], Web3.toWei(0, 'ether'),
        {'from': Governor}))
    assert_tx_failed(lambda: ProtocolDaoContract.set_maximum_mft_support_count(
        PROTOCOL_CONSTANTS['DAO_UNDERWRITER_POOL'], Web3.toWei(0, 'ether'),
        {'from': Governor}))
    assert InterestPoolDao.maximum_mft_support_count({'from': anyone}) == 0
    ProtocolDaoContract.set_maximum_mft_support_count(
        PROTOCOL_CONSTANTS['DAO_INTEREST_POOL'],
        Web3.toWei(INTEREST_POOL_DAO_MAXIMUM_MFT_SUPPORT_COUNT, 'ether'),
        {'from': Governor})
    assert InterestPoolDao.maximum_mft_support_count({'from': anyone}) == Web3.toWei(INTEREST_POOL_DAO_MAXIMUM_MFT_SUPPORT_COUNT, 'ether')
    assert UnderwriterPoolDao.maximum_mft_support_count({'from': anyone}) == 0
    ProtocolDaoContract.set_maximum_mft_support_count(
        PROTOCOL_CONSTANTS['DAO_UNDERWRITER_POOL'],
        Web3.toWei(INTEREST_POOL_DAO_MAXIMUM_MFT_SUPPORT_COUNT, 'ether'),
        {'from': Governor})
    assert UnderwriterPoolDao.maximum_mft_support_count({'from': anyone}) == Web3.toWei(INTEREST_POOL_DAO_MAXIMUM_MFT_SUPPORT_COUNT, 'ether')
    # Tx fails when called by non-Governor
    for account in accounts:
        if account == Governor:
            continue
        assert_tx_failed(lambda: ProtocolDaoContract.set_maximum_mft_support_count(
            PROTOCOL_CONSTANTS['DAO_INTEREST_POOL'],
            Web3.toWei(INTEREST_POOL_DAO_MIN_MFT_FEE, 'ether'),
            {'from': account}))
        assert_tx_failed(lambda: ProtocolDaoContract.set_maximum_mft_support_count(
            PROTOCOL_CONSTANTS['DAO_UNDERWRITER_POOL'],
            Web3.toWei(INTEREST_POOL_DAO_MIN_MFT_FEE, 'ether'),
            {'from': account}))


def test_set_price_oracle(accounts, assert_tx_failed, Deployer, Governor,
    get_MarketDao_contract,
    Lend_token, Borrow_token,
    PriceOracle, ProtocolDaoContract):
    anyone = accounts[-1]
    MarketDaoContract = get_MarketDao_contract(address=ProtocolDaoContract.daos(PROTOCOL_CONSTANTS['DAO_MARKET']))
    # Tx fails when target DAO is not initialized
    assert_tx_failed(lambda: ProtocolDaoContract.set_price_oracle(
        Lend_token.address, Borrow_token.address, PriceOracle.address,
        {'from': Governor}))
    # Initialize target DAO
    ProtocolDaoContract.initialize_market_dao({'from': Deployer})
    # Tx fails when called by non-Governor
    # Tx also fails for invalid Lend_token, Borrow_token, or PriceOracle addresses
    for account in accounts:
        if account == Governor:
            continue
        assert_tx_failed(lambda: ProtocolDaoContract.set_price_oracle(
            Lend_token.address, Borrow_token.address, PriceOracle.address,
            {'from': account}))
        assert_tx_failed(lambda: ProtocolDaoContract.set_price_oracle(
            account, Borrow_token.address, PriceOracle.address,
            {'from': Governor}))
        assert_tx_failed(lambda: ProtocolDaoContract.set_price_oracle(
            Lend_token.address, account, PriceOracle.address,
            {'from': Governor}))
        assert_tx_failed(lambda: ProtocolDaoContract.set_price_oracle(
            Lend_token.address, Borrow_token.address, account,
            {'from': Governor}))
    assert_tx_failed(lambda: ProtocolDaoContract.set_price_oracle(
        ZERO_ADDRESS, Borrow_token.address, PriceOracle.address,
        {'from': Governor}))
    assert_tx_failed(lambda: ProtocolDaoContract.set_price_oracle(
        Lend_token.address, ZERO_ADDRESS, PriceOracle.address,
        {'from': Governor}))
    assert_tx_failed(lambda: ProtocolDaoContract.set_price_oracle(
        Lend_token.address, Borrow_token.address, ZERO_ADDRESS,
        {'from': Governor}))
    _currency_underlying_pair_hash = MarketDaoContract.currency_underlying_pair_hash(Lend_token.address, Borrow_token.address, {'from': anyone})
    assert MarketDaoContract.price_oracles(_currency_underlying_pair_hash, {'from': anyone}) == ZERO_ADDRESS
    ProtocolDaoContract.set_price_oracle(
        Lend_token.address, Borrow_token.address, PriceOracle.address,
        {'from': Governor})
    assert MarketDaoContract.price_oracles(_currency_underlying_pair_hash, {'from': anyone}) == PriceOracle.address


def test_set_maximum_liability_for_currency_market(accounts, assert_tx_failed, Deployer, Governor,
    get_MarketDao_contract,
    Lend_token,
    ProtocolDaoContract):
    anyone = accounts[-1]
    MarketDaoContract = get_MarketDao_contract(address=ProtocolDaoContract.daos(PROTOCOL_CONSTANTS['DAO_MARKET']))
    # Tx fails when target DAO is not initialized
    assert_tx_failed(lambda: ProtocolDaoContract.set_maximum_liability_for_currency_market(
        Lend_token.address, H20, Web3.toWei(MAX_LIABILITY_CURENCY_MARKET, 'ether'),
        {'from': Governor}))
    # Initialize target DAO
    ProtocolDaoContract.initialize_market_dao({'from': Deployer})
    # Tx fails when called by non-Governor
    # Tx also fails for invalid Lend_token
    for account in accounts:
        if account == Governor:
            continue
        assert_tx_failed(lambda: ProtocolDaoContract.set_maximum_liability_for_currency_market(
            Lend_token.address, H20, Web3.toWei(MAX_LIABILITY_CURENCY_MARKET, 'ether'),
            {'from': account}))
        assert_tx_failed(lambda: ProtocolDaoContract.set_maximum_liability_for_currency_market(
            account, H20, Web3.toWei(MAX_LIABILITY_CURENCY_MARKET, 'ether'),
            {'from': Governor}))
    assert_tx_failed(lambda: ProtocolDaoContract.set_maximum_liability_for_currency_market(
        ZERO_ADDRESS, H20, Web3.toWei(MAX_LIABILITY_CURENCY_MARKET, 'ether'),
        {'from': Governor}))
    # Tx also fails for 0 values
    assert_tx_failed(lambda: ProtocolDaoContract.set_maximum_liability_for_currency_market(
        Lend_token.address, 0, Web3.toWei(MAX_LIABILITY_CURENCY_MARKET, 'ether'),
        {'from': Governor}))
    assert_tx_failed(lambda: ProtocolDaoContract.set_maximum_liability_for_currency_market(
        Lend_token.address, H20, 0,
        {'from': Governor}))
    assert MarketDaoContract.maximum_liability_for_currency_market(Lend_token.address, H20, {'from': anyone}) == 0
    # set maximum_market_liability
    ProtocolDaoContract.set_maximum_liability_for_currency_market(
        Lend_token.address, H20, Web3.toWei(MAX_LIABILITY_CURENCY_MARKET, 'ether'),
        {'from': Governor})
    assert MarketDaoContract.maximum_liability_for_currency_market(Lend_token.address, H20, {'from': anyone}) == Web3.toWei(MAX_LIABILITY_CURENCY_MARKET, 'ether')


def test_set_maximum_liability_for_loan_market(accounts, assert_tx_failed, Deployer, Governor,
    get_MarketDao_contract,
    Lend_token, Borrow_token,
    ProtocolDaoContract):
    anyone = accounts[-1]
    MarketDaoContract = get_MarketDao_contract(address=ProtocolDaoContract.daos(PROTOCOL_CONSTANTS['DAO_MARKET']))
    # Tx fails when target DAO is not initialized
    assert_tx_failed(lambda: ProtocolDaoContract.set_maximum_liability_for_loan_market(
        Lend_token.address, H20, Borrow_token.address, Web3.toWei(MAX_LIABILITY_CURENCY_MARKET, 'ether'),
        {'from': Governor}))
    # Initialize target DAO
    ProtocolDaoContract.initialize_market_dao({'from': Deployer})
    # Tx fails when called by non-Governor
    # Tx also fails for invalid Lend_token, or Borrow_token
    for account in accounts:
        if account == Governor:
            continue
        assert_tx_failed(lambda: ProtocolDaoContract.set_maximum_liability_for_loan_market(
            Lend_token.address, H20, Borrow_token.address, Web3.toWei(MAX_LIABILITY_CURENCY_MARKET, 'ether'),
            {'from': account}))
        assert_tx_failed(lambda: ProtocolDaoContract.set_maximum_liability_for_loan_market(
            account, H20, Borrow_token.address, Web3.toWei(MAX_LIABILITY_CURENCY_MARKET, 'ether'),
            {'from': Governor}))
        assert_tx_failed(lambda: ProtocolDaoContract.set_maximum_liability_for_loan_market(
            Lend_token.address, H20, account, Web3.toWei(MAX_LIABILITY_CURENCY_MARKET, 'ether'),
            {'from': Governor}))
    assert_tx_failed(lambda: ProtocolDaoContract.set_maximum_liability_for_loan_market(
        ZERO_ADDRESS, H20, Borrow_token.address, Web3.toWei(MAX_LIABILITY_CURENCY_MARKET, 'ether'),
        {'from': Governor}))
    assert_tx_failed(lambda: ProtocolDaoContract.set_maximum_liability_for_loan_market(
        Lend_token.address, H20, ZERO_ADDRESS, Web3.toWei(MAX_LIABILITY_CURENCY_MARKET, 'ether'),
        {'from': Governor}))
    # Tx also fails for 0 values
    assert_tx_failed(lambda: ProtocolDaoContract.set_maximum_liability_for_loan_market(
        Lend_token.address, 0, Borrow_token.address, Web3.toWei(MAX_LIABILITY_CURENCY_MARKET, 'ether'),
        {'from': Governor}))
    assert_tx_failed(lambda: ProtocolDaoContract.set_maximum_liability_for_loan_market(
        Lend_token.address, H20, Borrow_token.address, 0,
        {'from': Governor}))
    assert MarketDaoContract.maximum_liability_for_loan_market(Lend_token.address, H20, Borrow_token.address, {'from': anyone}) == 0
    # set maximum_market_liability
    ProtocolDaoContract.set_maximum_liability_for_loan_market(
        Lend_token.address, H20, Borrow_token.address, Web3.toWei(MAX_LIABILITY_CURENCY_MARKET, 'ether'),
        {'from': Governor})
    assert MarketDaoContract.maximum_liability_for_loan_market(Lend_token.address, H20, Borrow_token.address, {'from': anyone}) == Web3.toWei(MAX_LIABILITY_CURENCY_MARKET, 'ether')


def test_set_auction_slippage_percentage(accounts, assert_tx_failed, Deployer, Governor,
    get_MarketDao_contract, ProtocolDaoContract):
    anyone = accounts[-1]
    MarketDaoContract = get_MarketDao_contract(address=ProtocolDaoContract.daos(PROTOCOL_CONSTANTS['DAO_MARKET']))
    # Tx fails when target DAO is not initialized
    assert_tx_failed(lambda: ProtocolDaoContract.set_auction_slippage_percentage(
        AUCTION_SLIPPAGE_PERCENTAGE, {'from': Governor}))
    # Initialize target DAO
    ProtocolDaoContract.initialize_market_dao({'from': Deployer})
    # Tx fails when called by non-Governor
    for account in accounts:
        if account == Governor:
            continue
        assert_tx_failed(lambda: ProtocolDaoContract.set_auction_slippage_percentage(
            AUCTION_SLIPPAGE_PERCENTAGE, {'from': account}))
    # Tx fails for 0 value
    assert_tx_failed(lambda: ProtocolDaoContract.set_auction_slippage_percentage(
        0, {'from': Governor}))
    assert MarketDaoContract.auction_slippage_percentage({'from': anyone}) == 0
    # set maximum_market_liability
    ProtocolDaoContract.set_auction_slippage_percentage(
        AUCTION_SLIPPAGE_PERCENTAGE, {'from': Governor})
    assert MarketDaoContract.auction_slippage_percentage({'from': anyone}) == AUCTION_SLIPPAGE_PERCENTAGE


def test_set_auction_maximum_discount_percentage(accounts, assert_tx_failed, Deployer, Governor,
    get_MarketDao_contract, ProtocolDaoContract):
    anyone = accounts[-1]
    MarketDaoContract = get_MarketDao_contract(address=ProtocolDaoContract.daos(PROTOCOL_CONSTANTS['DAO_MARKET']))
    # Tx fails when target DAO is not initialized
    assert_tx_failed(lambda: ProtocolDaoContract.set_auction_maximum_discount_percentage(
        AUCTION_MAXIMUM_DISCOUNT_PERCENTAGE, {'from': Governor}))
    # Initialize target DAO
    ProtocolDaoContract.initialize_market_dao({'from': Deployer})
    # Tx fails when called by non-Governor
    for account in accounts:
        if account == Governor:
            continue
        assert_tx_failed(lambda: ProtocolDaoContract.set_auction_maximum_discount_percentage(
            AUCTION_MAXIMUM_DISCOUNT_PERCENTAGE, {'from': account}))
    # Tx fails for 0 value
    assert_tx_failed(lambda: ProtocolDaoContract.set_auction_maximum_discount_percentage(
        0, {'from': Governor}))
    assert MarketDaoContract.auction_maximum_discount_percentage({'from': anyone}) == 0
    # set maximum_market_liability
    ProtocolDaoContract.set_auction_maximum_discount_percentage(
        AUCTION_MAXIMUM_DISCOUNT_PERCENTAGE, {'from': Governor})
    assert MarketDaoContract.auction_maximum_discount_percentage({'from': anyone}) == AUCTION_MAXIMUM_DISCOUNT_PERCENTAGE


def test_set_auction_discount_duration(accounts, assert_tx_failed, Deployer, Governor,
    get_MarketDao_contract, ProtocolDaoContract):
    anyone = accounts[-1]
    MarketDaoContract = get_MarketDao_contract(address=ProtocolDaoContract.daos(PROTOCOL_CONSTANTS['DAO_MARKET']))
    # Tx fails when target DAO is not initialized
    assert_tx_failed(lambda: ProtocolDaoContract.set_auction_discount_duration(
        AUCTION_DISCOUNT_DURATION, {'from': Governor}))
    # Initialize target DAO
    ProtocolDaoContract.initialize_market_dao({'from': Deployer})
    # Tx fails when called by non-Governor
    for account in accounts:
        if account == Governor:
            continue
        assert_tx_failed(lambda: ProtocolDaoContract.set_auction_discount_duration(
            AUCTION_DISCOUNT_DURATION, {'from': account}))
    # Tx fails for 0 value
    assert_tx_failed(lambda: ProtocolDaoContract.set_auction_discount_duration(
        0, {'from': Governor}))
    assert MarketDaoContract.auction_discount_duration({'from': anyone}) == 0
    # set maximum_market_liability
    ProtocolDaoContract.set_auction_discount_duration(
        AUCTION_DISCOUNT_DURATION, {'from': Governor})
    assert MarketDaoContract.auction_discount_duration({'from': anyone}) == AUCTION_DISCOUNT_DURATION
