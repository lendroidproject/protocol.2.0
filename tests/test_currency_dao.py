import pytest

from web3 import Web3

from conftest import (
    PROTOCOL_CONSTANTS,
    POOL_NAME_REGISTRATION_MIN_STAKE_LST,
    ZERO_ADDRESS
)


def test_initialize(accounts, Deployer, get_CurrencyDao_contract, ProtocolDaoContract):
    anyone = accounts[-1]
    CurrencyDaoContract = get_CurrencyDao_contract(address=ProtocolDaoContract.daos(PROTOCOL_CONSTANTS['DAO_CURRENCY']))
    assert not CurrencyDaoContract.initialized({'from': anyone})
    ProtocolDaoContract.initialize_currency_dao({'from': Deployer})
    assert CurrencyDaoContract.initialized({'from': anyone})


def test_pause_and_unpause(accounts, Deployer, EscapeHatchManager, get_CurrencyDao_contract, ProtocolDaoContract):
    anyone = accounts[-1]
    CurrencyDaoContract = get_CurrencyDao_contract(address=ProtocolDaoContract.daos(PROTOCOL_CONSTANTS['DAO_CURRENCY']))
    ProtocolDaoContract.initialize_currency_dao({'from': Deployer})
    assert not CurrencyDaoContract.paused({'from': anyone})
    ProtocolDaoContract.toggle_dao_pause(PROTOCOL_CONSTANTS['DAO_CURRENCY'], True, {'from': EscapeHatchManager})
    assert CurrencyDaoContract.paused({'from': anyone})
    ProtocolDaoContract.toggle_dao_pause(PROTOCOL_CONSTANTS['DAO_CURRENCY'], False, {'from': EscapeHatchManager})
    assert not CurrencyDaoContract.paused({'from': anyone})


def test_pause_failed_when_paused(accounts, assert_tx_failed, Deployer, EscapeHatchManager, get_CurrencyDao_contract, ProtocolDaoContract):
    anyone = accounts[-1]
    CurrencyDaoContract = get_CurrencyDao_contract(address=ProtocolDaoContract.daos(PROTOCOL_CONSTANTS['DAO_CURRENCY']))
    ProtocolDaoContract.initialize_currency_dao({'from': Deployer})
    ProtocolDaoContract.toggle_dao_pause(PROTOCOL_CONSTANTS['DAO_CURRENCY'], True, {'from': EscapeHatchManager})
    assert_tx_failed(lambda: ProtocolDaoContract.toggle_dao_pause(PROTOCOL_CONSTANTS['DAO_CURRENCY'], True, {'from': EscapeHatchManager}))


def test_pause_failed_when_uninitialized(accounts, assert_tx_failed, Deployer, EscapeHatchManager, get_CurrencyDao_contract, ProtocolDaoContract):
    anyone = accounts[-1]
    CurrencyDaoContract = get_CurrencyDao_contract(address=ProtocolDaoContract.daos(PROTOCOL_CONSTANTS['DAO_CURRENCY']))
    assert_tx_failed(lambda: ProtocolDaoContract.toggle_dao_pause(PROTOCOL_CONSTANTS['DAO_CURRENCY'], True, {'from': EscapeHatchManager}))


def test_pause_failed_when_called_by_non_protocol_dao(accounts, assert_tx_failed, Deployer, EscapeHatchManager, get_CurrencyDao_contract, ProtocolDaoContract):
    anyone = accounts[-1]
    CurrencyDaoContract = get_CurrencyDao_contract(address=ProtocolDaoContract.daos(PROTOCOL_CONSTANTS['DAO_CURRENCY']))
    ProtocolDaoContract.initialize_currency_dao({'from': Deployer})
    # Tx failed
    for account in accounts:
        assert_tx_failed(lambda: CurrencyDaoContract.pause({'from': account}))


def test_unpause_failed_when_unpaused(accounts, assert_tx_failed, Deployer, EscapeHatchManager, get_CurrencyDao_contract, ProtocolDaoContract):
    anyone = accounts[-1]
    CurrencyDaoContract = get_CurrencyDao_contract(address=ProtocolDaoContract.daos(PROTOCOL_CONSTANTS['DAO_CURRENCY']))
    ProtocolDaoContract.initialize_currency_dao({'from': Deployer})
    assert_tx_failed(lambda: ProtocolDaoContract.toggle_dao_pause(PROTOCOL_CONSTANTS['DAO_CURRENCY'], False, {'from': EscapeHatchManager}))


def test_unpause_failed_when_uninitialized(accounts, assert_tx_failed, Deployer, EscapeHatchManager, get_CurrencyDao_contract, ProtocolDaoContract):
    anyone = accounts[-1]
    CurrencyDaoContract = get_CurrencyDao_contract(address=ProtocolDaoContract.daos(PROTOCOL_CONSTANTS['DAO_CURRENCY']))
    assert_tx_failed(lambda: ProtocolDaoContract.toggle_dao_pause(PROTOCOL_CONSTANTS['DAO_CURRENCY'], False, {'from': EscapeHatchManager}))


def test_unpause_failed_when_called_by_non_protocol_dao(accounts, assert_tx_failed, Deployer, EscapeHatchManager, get_CurrencyDao_contract, ProtocolDaoContract):
    anyone = accounts[-1]
    CurrencyDaoContract = get_CurrencyDao_contract(address=ProtocolDaoContract.daos(PROTOCOL_CONSTANTS['DAO_CURRENCY']))
    ProtocolDaoContract.initialize_currency_dao({'from': Deployer})
    # Tx failed
    for account in accounts:
        assert_tx_failed(lambda: CurrencyDaoContract.unpause({'from': account}))


def test_wrap(accounts, assert_tx_failed, get_ERC20_contract, get_CurrencyDao_contract,
    Deployer, Governor, EscapeHatchManager,
    Whale, Lend_token,
    ProtocolDaoContract):
    anyone = accounts[-1]
    # get CurrencyDaoContract
    CurrencyDaoContract = get_CurrencyDao_contract(address=ProtocolDaoContract.daos(PROTOCOL_CONSTANTS['DAO_CURRENCY']))
    # assign one of the accounts as _lend_token_holder
    _lend_token_holder = accounts[5]
    # Tx fails when calling wrap() and CurrencyDaoContract is not initialized
    assert_tx_failed(lambda: CurrencyDaoContract.wrap(Lend_token.address, Web3.toWei(800, 'ether'), {'from': _lend_token_holder, 'gas': 145000}))
    # initialize CurrencyDaoContract
    ProtocolDaoContract.initialize_currency_dao({'from': Deployer})
    # Governor registers support for Lend_token
    ProtocolDaoContract.set_token_support(Lend_token.address, True, {'from': Governor, 'gas': 2000000})
    # _lend_token_holder buys 1000 lend token from a 3rd party exchange
    assert Lend_token.balanceOf(_lend_token_holder, {'from': anyone}) == 0
    Lend_token.transfer(_lend_token_holder, Web3.toWei(1000, 'ether'), {'from': Whale})
    assert Lend_token.balanceOf(_lend_token_holder, {'from': anyone}) == Web3.toWei(1000, 'ether')
    # get L_Lend_token
    L_lend_token = get_ERC20_contract(address=CurrencyDaoContract.token_addresses__l(Lend_token.address, {'from': anyone}))
    # _lend_token_holder authorizes CurrencyDaoContract to spend 500 Lend_token
    assert Lend_token.allowance(_lend_token_holder, CurrencyDaoContract.address, {'from': anyone}) == 0
    Lend_token.approve(CurrencyDaoContract.address, Web3.toWei(800, 'ether'), {'from': _lend_token_holder})
    assert Lend_token.allowance(_lend_token_holder, CurrencyDaoContract.address, {'from': anyone}) == Web3.toWei(800, 'ether')
    assert L_lend_token.balanceOf(_lend_token_holder, {'from': anyone}) == 0
    # _lend_token_holder wraps 800 Lend_token to L_lend_token
    CurrencyDaoContract.wrap(Lend_token.address, Web3.toWei(800, 'ether'), {'from': _lend_token_holder, 'gas': 145000})
    # verify allowance, balances of Lend_token and L_lend_token
    assert Lend_token.allowance(_lend_token_holder, CurrencyDaoContract.address, {'from': anyone}) == 0
    assert Lend_token.balanceOf(_lend_token_holder, {'from': anyone}) == Web3.toWei(200, 'ether')
    assert L_lend_token.balanceOf(_lend_token_holder, {'from': anyone}) == Web3.toWei(800, 'ether')
    # EscapeHatchManager pauses CurrencyDaoContract
    ProtocolDaoContract.toggle_dao_pause(PROTOCOL_CONSTANTS['DAO_CURRENCY'], True, {'from': EscapeHatchManager})
    # Tx fails when calling wrap() and CurrencyDaoContract is paused
    assert_tx_failed(lambda: CurrencyDaoContract.wrap(Lend_token.address, Web3.toWei(800, 'ether'), {'from': _lend_token_holder, 'gas': 145000}))
    # EscapeHatchManager unpauses CurrencyDaoContract
    ProtocolDaoContract.toggle_dao_pause(PROTOCOL_CONSTANTS['DAO_CURRENCY'], False, {'from': EscapeHatchManager})
    # Governor withdraws support for Lend_token
    ProtocolDaoContract.set_token_support(Lend_token.address, False, {'from': Governor, 'gas': 2000000})
    # Tx fails when calling wrap() and token is not supported
    assert_tx_failed(lambda: CurrencyDaoContract.wrap(Lend_token.address, Web3.toWei(800, 'ether'), {'from': _lend_token_holder, 'gas': 145000}))


def test_unwrap(accounts, assert_tx_failed, get_ERC20_contract, get_CurrencyDao_contract,
    Deployer, Governor, EscapeHatchManager,
    Whale, Lend_token,
    ProtocolDaoContract):
    anyone = accounts[-1]
    # get CurrencyDaoContract
    CurrencyDaoContract = get_CurrencyDao_contract(address=ProtocolDaoContract.daos(PROTOCOL_CONSTANTS['DAO_CURRENCY']))
    # assign one of the accounts as _lend_token_holder
    _lend_token_holder = accounts[5]
    # Tx fails when calling unwrap() and CurrencyDaoContract is not initialized
    assert_tx_failed(lambda: CurrencyDaoContract.unwrap(Lend_token.address, Web3.toWei(800, 'ether'), {'from': _lend_token_holder, 'gas': 100000}))
    # initialize CurrencyDaoContract
    ProtocolDaoContract.initialize_currency_dao({'from': Deployer})
    ProtocolDaoContract.set_token_support(Lend_token.address, True, {'from': Governor, 'gas': 2000000})
    # _lend_token_holder buys 1000 lend token from a 3rd party exchange
    assert Lend_token.balanceOf(_lend_token_holder, {'from': anyone}) == 0
    Lend_token.transfer(_lend_token_holder, Web3.toWei(1000, 'ether'), {'from': Whale})
    assert Lend_token.balanceOf(_lend_token_holder, {'from': anyone}) == Web3.toWei(1000, 'ether')
    # get L_Lend_token
    L_lend_token = get_ERC20_contract(address=CurrencyDaoContract.token_addresses__l(Lend_token.address, {'from': anyone}))
    # _lend_token_holder authorizes CurrencyDaoContract to spend 500 Lend_token
    Lend_token.approve(CurrencyDaoContract.address, Web3.toWei(800, 'ether'), {'from': _lend_token_holder})
    # _lend_token_holder wraps 800 Lend_token to L_lend_token
    CurrencyDaoContract.wrap(Lend_token.address, Web3.toWei(800, 'ether'), {'from': _lend_token_holder, 'gas': 145000})
    # Tx fails when trying to unwrap 0 tokens
    assert_tx_failed(lambda: CurrencyDaoContract.unwrap(Lend_token.address, 0, {'from': _lend_token_holder, 'gas': 100000}))
    # _lend_token_holder wraps 800 Lend_token to L_lend_token
    CurrencyDaoContract.unwrap(Lend_token.address, Web3.toWei(800, 'ether'), {'from': _lend_token_holder, 'gas': 100000})
    # verify balances of Lend_token and L_lend_token
    assert Lend_token.balanceOf(_lend_token_holder, {'from': anyone}) == Web3.toWei(1000, 'ether')
    assert L_lend_token.balanceOf(_lend_token_holder, {'from': anyone}) == 0
    # EscapeHatchManager pauses CurrencyDaoContract
    ProtocolDaoContract.toggle_dao_pause(PROTOCOL_CONSTANTS['DAO_CURRENCY'], True, {'from': EscapeHatchManager})
    # Tx fails when calling unwrap() and CurrencyDaoContract is paused
    assert_tx_failed(lambda: CurrencyDaoContract.unwrap(Lend_token.address, Web3.toWei(800, 'ether'), {'from': _lend_token_holder, 'gas': 100000}))
    # Governor withdraws support for Lend_token
    ProtocolDaoContract.set_token_support(Lend_token.address, False, {'from': Governor, 'gas': 2000000})
    # Tx fails when calling unwrap() and token is not supported
    assert_tx_failed(lambda: CurrencyDaoContract.unwrap(Lend_token.address, Web3.toWei(800, 'ether'), {'from': _lend_token_holder, 'gas': 100000}))


def test_set_token_support(accounts, assert_tx_failed, get_ERC20_contract, get_CurrencyPool_contract, get_CurrencyDao_contract,
    Deployer, Governor,
    Whale, LST_token, Lend_token,
    ProtocolDaoContract):
    anyone = accounts[-1]
    # get CurrencyDaoContract
    CurrencyDaoContract = get_CurrencyDao_contract(address=ProtocolDaoContract.daos(PROTOCOL_CONSTANTS['DAO_CURRENCY']))
    # assign one of the accounts as _lend_token_holder
    _lend_token_holder = accounts[5]
    # Tx fails when calling set_token_support() and CurrencyDaoContract is not initialized
    assert_tx_failed(lambda: ProtocolDaoContract.set_token_support(Lend_token.address, True, {'from': Governor, 'gas': 2000000}))
    # initialize CurrencyDaoContract
    ProtocolDaoContract.initialize_currency_dao({'from': Deployer})
    # Tx fails when called by non-protocol_dao
    assert_tx_failed(lambda: CurrencyDaoContract.set_token_support(Lend_token.address, True, {'from': Governor, 'gas': 2000000}))
    # Governor sets support for Lend_token
    ProtocolDaoContract.set_token_support(Lend_token.address, True, {'from': Governor, 'gas': 2000000})
    # Tx fails for LST support
    assert_tx_failed(lambda: ProtocolDaoContract.set_token_support(LST_token.address, True, {'from': Governor, 'gas': 2000000}))
    # Tx fails for invalid token support
    assert_tx_failed(lambda: ProtocolDaoContract.set_token_support(ZERO_ADDRESS, True, {'from': Governor, 'gas': 2000000}))
    for account in accounts:
        assert_tx_failed(lambda: ProtocolDaoContract.set_token_support(account, True, {'from': Governor, 'gas': 2000000}))
    _pool_hash = CurrencyDaoContract.pool_hash(Lend_token.address, {'from': anyone})
    # get LendTokenPoolContract
    assert not CurrencyDaoContract.pools__address_(_pool_hash, {'from': anyone}) == ZERO_ADDRESS
    LendTokenPoolContract = get_CurrencyPool_contract(address=CurrencyDaoContract.pools__address_(_pool_hash, {'from': anyone}))
    # verify token pool details stored in CurrencyDaoContract
    assert CurrencyDaoContract.pools__currency(_pool_hash, {'from': anyone}) == Lend_token.address
    assert CurrencyDaoContract.pools__operator(_pool_hash, {'from': anyone}) == CurrencyDaoContract.address
    assert CurrencyDaoContract.pools__hash(_pool_hash, {'from': anyone}) == _pool_hash
    assert CurrencyDaoContract.pools__name(_pool_hash, {'from': anyone}) == Lend_token.name({'from': anyone})
    # _lend_token_holder buys 1000 lend token from a 3rd party exchange
    Lend_token.transfer(_lend_token_holder, Web3.toWei(1000, 'ether'), {'from': Whale})
    # get L_Lend_token
    L_lend_token = get_ERC20_contract(address=CurrencyDaoContract.token_addresses__l(Lend_token.address, {'from': anyone}))
    # _lend_token_holder authorizes CurrencyDaoContract to spend 500 Lend_token
    Lend_token.approve(CurrencyDaoContract.address, Web3.toWei(1000, 'ether'), {'from': _lend_token_holder})
    # _lend_token_holder wraps 800 Lend_token to L_lend_token
    CurrencyDaoContract.wrap(Lend_token.address, Web3.toWei(1000, 'ether'), {'from': _lend_token_holder, 'gas': 145000})
    # verify token pool details from token pool contract
    assert LendTokenPoolContract.initialized({'from': anyone})
    assert LendTokenPoolContract.owner({'from': anyone}) == CurrencyDaoContract.address
    assert LendTokenPoolContract.token({'from': anyone}) == Lend_token.address
    assert LendTokenPoolContract.borrowable_amount({'from': anyone}) == Web3.toWei(1000, 'ether')
    # Governor removes support for Lend_token
    assert Lend_token.balanceOf(CurrencyDaoContract.address) == 0
    ProtocolDaoContract.set_token_support(Lend_token.address, False, {'from': Governor, 'gas': 120000})
    # verify token pool details stored in CurrencyDaoContract
    assert CurrencyDaoContract.pools__address_(_pool_hash, {'from': anyone}) == ZERO_ADDRESS
    assert CurrencyDaoContract.pools__currency(_pool_hash, {'from': anyone}) == Lend_token.address
    assert CurrencyDaoContract.pools__operator(_pool_hash, {'from': anyone}) == CurrencyDaoContract.address
    assert CurrencyDaoContract.pools__hash(_pool_hash, {'from': anyone}) == _pool_hash
    assert CurrencyDaoContract.pools__name(_pool_hash, {'from': anyone}) == ""
    # verify Lend_token has been transferred to CurrencyDaoContract
    assert Lend_token.balanceOf(CurrencyDaoContract.address) == Web3.toWei(1000, 'ether')
    # Governor restores support for Lend_token
    ProtocolDaoContract.set_token_support(Lend_token.address, True, {'from': Governor, 'gas': 2000000})
    # verify token pool details stored in CurrencyDaoContract
    assert CurrencyDaoContract.pools__currency(_pool_hash, {'from': anyone}) == Lend_token.address
    assert CurrencyDaoContract.pools__operator(_pool_hash, {'from': anyone}) == CurrencyDaoContract.address
    assert CurrencyDaoContract.pools__hash(_pool_hash, {'from': anyone}) == _pool_hash
    assert CurrencyDaoContract.pools__name(_pool_hash, {'from': anyone}) == Lend_token.name({'from': anyone})
