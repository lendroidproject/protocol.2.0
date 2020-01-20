import pytest
from web3 import Web3
from web3.exceptions import (
    ValidationError,
)
from conftest import (
    PROTOCOL_CONSTANTS,
    MAX_UINT256,
    ZERO_ADDRESS
)


def test_initial_state(w3, get_ERC20_contract, get_CurrencyDao_contract,
    Deployer, Governor,
    Whale, Lend_token,
    ProtocolDao):
    a1, a2, a3 = w3.eth.accounts[1:4]
    # get CurrencyDao
    CurrencyDao = get_CurrencyDao_contract(address=ProtocolDao.daos(PROTOCOL_CONSTANTS['DAO_CURRENCY']))
    # assign one of the accounts as _lend_token_holder
    _lend_token_holder = w3.eth.accounts[5]
    # initialize CurrencyDao
    tx_hash = ProtocolDao.initialize_currency_dao(transact={'from': Deployer})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    tx_hash = ProtocolDao.set_token_support(Lend_token.address, True, transact={'from': Governor, 'gas': 2000000})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    # _lend_token_holder buys 1000 lend token from a 3rd party exchange
    assert Lend_token.balanceOf(_lend_token_holder) == 0
    tx_hash = Lend_token.transfer(_lend_token_holder, Web3.toWei(1000, 'ether'), transact={'from': Whale})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    assert Lend_token.balanceOf(_lend_token_holder) == Web3.toWei(1000, 'ether')
    # get L_Lend_token
    test_token = get_ERC20_contract(address=CurrencyDao.token_addresses__l(Lend_token.address))
    # Check total supply, name, symbol and decimals are correctly set
    assert test_token.totalSupply() == 0
    assert test_token.name() == 'Wrapped Test Lend Token'
    assert test_token.symbol() == 'LDAI'
    assert test_token.decimals() == 18
    # Check several account balances as 0
    assert test_token.balanceOf(a1) == 0
    assert test_token.balanceOf(a2) == 0
    assert test_token.balanceOf(a3) == 0
    # Check several allowances as 0
    assert test_token.allowance(a1, a1) == 0
    assert test_token.allowance(a1, a2) == 0
    assert test_token.allowance(a1, a3) == 0
    assert test_token.allowance(a2, a3) == 0


def test_mint_and_burn(w3, assert_tx_failed, get_ERC20_contract, get_CurrencyDao_contract,
    Deployer, Governor,
    Whale, Lend_token,
    ProtocolDao):
    # get CurrencyDao
    CurrencyDao = get_CurrencyDao_contract(address=ProtocolDao.daos(PROTOCOL_CONSTANTS['DAO_CURRENCY']))
    # assign one of the accounts as _lend_token_holder
    _lend_token_holder = w3.eth.accounts[5]
    # initialize CurrencyDao
    tx_hash = ProtocolDao.initialize_currency_dao(transact={'from': Deployer})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    tx_hash = ProtocolDao.set_token_support(Lend_token.address, True, transact={'from': Governor, 'gas': 2000000})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    # _lend_token_holder buys 1000 lend token from a 3rd party exchange
    tx_hash = Lend_token.transfer(_lend_token_holder, Web3.toWei(1000, 'ether'), transact={'from': Whale})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    # _lend_token_holder authorizes CurrencyDao to spend 500 Lend_token
    tx_hash = Lend_token.approve(CurrencyDao.address, Web3.toWei(800, 'ether'), transact={'from': _lend_token_holder})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    # get L_Lend_token
    test_token = get_ERC20_contract(address=CurrencyDao.token_addresses__l(Lend_token.address))
    # Test scenario were mints 2 to _lend_token_holder, burns twice (check balance consistency)
    # _lend_token_holder wraps 2 Lend_token to L_lend_token
    tx_hash = CurrencyDao.wrap(Lend_token.address, Web3.toWei(2, 'ether'), transact={'from': _lend_token_holder, 'gas': 145000})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    assert test_token.balanceOf(_lend_token_holder) == Web3.toWei(2, 'ether')
    test_token.burn(Web3.toWei(2, 'ether'), transact={'from': _lend_token_holder})
    assert test_token.balanceOf(_lend_token_holder) == 0
    assert_tx_failed(lambda: test_token.burn(Web3.toWei(2, 'ether'), transact={'from': _lend_token_holder}))
    assert test_token.balanceOf(_lend_token_holder) == 0
    # Test scenario were mintes 0 to _lend_token_holder, burns (check balance consistency, false burn)
    tx_hash = CurrencyDao.wrap(Lend_token.address, 0, transact={'from': _lend_token_holder, 'gas': 145000})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    assert test_token.balanceOf(_lend_token_holder) == 0
    assert_tx_failed(lambda: test_token.burn(Web3.toWei(2, 'ether'), transact={'from': _lend_token_holder}))
    # Check that _lend_token_holder cannot mint
    assert_tx_failed(lambda: test_token.mint(_lend_token_holder, Web3.toWei(2, 'ether'), transact={'from': _lend_token_holder}))


def test_totalSupply(w3, assert_tx_failed, get_ERC20_contract, get_CurrencyDao_contract,
    Deployer, Governor,
    Whale, Lend_token,
    ProtocolDao):
    # Test total supply initially, after mint, between two burns, and after failed burn
    # get CurrencyDao
    CurrencyDao = get_CurrencyDao_contract(address=ProtocolDao.daos(PROTOCOL_CONSTANTS['DAO_CURRENCY']))
    # assign one of the accounts as _lend_token_holder
    _lend_token_holder = w3.eth.accounts[5]
    # initialize CurrencyDao
    tx_hash = ProtocolDao.initialize_currency_dao(transact={'from': Deployer})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    tx_hash = ProtocolDao.set_token_support(Lend_token.address, True, transact={'from': Governor, 'gas': 2000000})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    # _lend_token_holder buys 1000 lend token from a 3rd party exchange
    tx_hash = Lend_token.transfer(_lend_token_holder, Web3.toWei(1000, 'ether'), transact={'from': Whale})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    # _lend_token_holder authorizes CurrencyDao to spend 800 Lend_token
    tx_hash = Lend_token.approve(CurrencyDao.address, Web3.toWei(800, 'ether'), transact={'from': _lend_token_holder})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    # get L_Lend_token
    test_token = get_ERC20_contract(address=CurrencyDao.token_addresses__l(Lend_token.address))
    assert test_token.totalSupply() == 0
    # _lend_token_holder wraps 2 Lend_token to L_lend_token
    tx_hash = CurrencyDao.wrap(Lend_token.address, Web3.toWei(2, 'ether'), transact={'from': _lend_token_holder, 'gas': 145000})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    assert test_token.totalSupply() == Web3.toWei(2, 'ether')
    test_token.burn(Web3.toWei(1, 'ether'), transact={'from': _lend_token_holder})
    assert test_token.totalSupply() == Web3.toWei(1, 'ether')
    test_token.burn(Web3.toWei(1, 'ether'), transact={'from': _lend_token_holder})
    assert test_token.totalSupply() == 0
    assert_tx_failed(lambda: test_token.burn(Web3.toWei(1, 'ether'), transact={'from': _lend_token_holder}))
    assert test_token.totalSupply() == 0
    # Test that 0-valued mint can't affect supply
    tx_hash = CurrencyDao.wrap(Lend_token.address, 0, transact={'from': _lend_token_holder, 'gas': 145000})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    assert test_token.totalSupply() == 0


def test_transfer(w3, assert_tx_failed, get_ERC20_contract, get_CurrencyDao_contract,
    Deployer, Governor,
    Whale, Lend_token,
    ProtocolDao):
    minter, a1, a2 = w3.eth.accounts[0:3]
    # get CurrencyDao
    CurrencyDao = get_CurrencyDao_contract(address=ProtocolDao.daos(PROTOCOL_CONSTANTS['DAO_CURRENCY']))
    # assign one of the accounts as _lend_token_holder
    _lend_token_holder = w3.eth.accounts[5]
    # initialize CurrencyDao
    tx_hash = ProtocolDao.initialize_currency_dao(transact={'from': Deployer})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    tx_hash = ProtocolDao.set_token_support(Lend_token.address, True, transact={'from': Governor, 'gas': 2000000})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    # _lend_token_holder buys 1000 lend token from a 3rd party exchange
    tx_hash = Lend_token.transfer(_lend_token_holder, Web3.toWei(1000, 'ether'), transact={'from': Whale})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    # _lend_token_holder authorizes CurrencyDao to spend 800 Lend_token
    tx_hash = Lend_token.approve(CurrencyDao.address, Web3.toWei(800, 'ether'), transact={'from': _lend_token_holder})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    # get L_Lend_token
    test_token = get_ERC20_contract(address=CurrencyDao.token_addresses__l(Lend_token.address))
    assert_tx_failed(lambda: test_token.burn(Web3.toWei(1, 'ether'), transact={'from': a2}))
    # _lend_token_holder wraps 2 Lend_token to L_lend_token
    tx_hash = CurrencyDao.wrap(Lend_token.address, Web3.toWei(2, 'ether'), transact={'from': _lend_token_holder, 'gas': 145000})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    test_token.burn(Web3.toWei(1, 'ether'), transact={'from': _lend_token_holder})
    test_token.transfer(a2, Web3.toWei(1, 'ether'), transact={'from': _lend_token_holder})
    assert_tx_failed(lambda: test_token.burn(Web3.toWei(1, 'ether'), transact={'from': _lend_token_holder}))
    test_token.burn(Web3.toWei(1, 'ether'), transact={'from': a2})
    assert_tx_failed(lambda: test_token.burn(Web3.toWei(1, 'ether'), transact={'from': a2}))
    # Ensure transfer fails with insufficient balance
    assert_tx_failed(lambda: test_token.transfer(_lend_token_holder, Web3.toWei(1, 'ether'), transact={'from': a2}))
    # Ensure 0-transfer always succeeds
    test_token.transfer(_lend_token_holder, 0, transact={'from': a2})


def test_maxInts(w3, assert_tx_failed, get_ERC20_contract, get_CurrencyDao_contract, Deployer, Governor,
    Whale, Lend_token_With_Max_Supply,
    ProtocolDao):
    Lend_token = Lend_token_With_Max_Supply
    minter, a1, a2 = w3.eth.accounts[0:3]
    # get CurrencyDao
    CurrencyDao = get_CurrencyDao_contract(address=ProtocolDao.daos(PROTOCOL_CONSTANTS['DAO_CURRENCY']))
    # assign one of the accounts as _lend_token_holder
    _lend_token_holder = w3.eth.accounts[5]
    # initialize CurrencyDao
    tx_hash = ProtocolDao.initialize_currency_dao(transact={'from': Deployer})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    tx_hash = ProtocolDao.set_token_support(Lend_token.address, True, transact={'from': Governor, 'gas': 2100000})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    # Whale mints MAX_UINT256 Lend_tokens
    tx_hash = Lend_token.mint(Whale, MAX_UINT256, transact={'from': Whale})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    # _lend_token_holder buys 1000 lend token from a 3rd party exchange
    tx_hash = Lend_token.transfer(_lend_token_holder, MAX_UINT256, transact={'from': Whale})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    # _lend_token_holder authorizes CurrencyDao to spend MAX_UINT256 Lend_token
    tx_hash = Lend_token.approve(CurrencyDao.address, MAX_UINT256, transact={'from': _lend_token_holder})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    # get L_Lend_token
    test_token = get_ERC20_contract(address=CurrencyDao.token_addresses__l(Lend_token.address))
    tx_hash = CurrencyDao.wrap(Lend_token.address, MAX_UINT256, transact={'from': _lend_token_holder, 'gas': 145000})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    # Assert that after obtaining max number of tokens, a1 can transfer those but no more
    assert test_token.balanceOf(_lend_token_holder) == MAX_UINT256
    test_token.transfer(a2, MAX_UINT256, transact={'from': _lend_token_holder})
    assert test_token.balanceOf(a2) == MAX_UINT256
    assert test_token.balanceOf(_lend_token_holder) == 0
    # [ next line should never work in EVM ]
    with pytest.raises(ValidationError):
        test_token.transfer(_lend_token_holder, MAX_UINT256 + 1, transact={'from': a2})
    # Check approve/allowance w max possible token values
    assert test_token.balanceOf(a2) == MAX_UINT256
    test_token.approve(_lend_token_holder, MAX_UINT256, transact={'from': a2})
    test_token.transferFrom(a2, _lend_token_holder, MAX_UINT256, transact={'from': _lend_token_holder})
    assert test_token.balanceOf(_lend_token_holder) == MAX_UINT256
    assert test_token.balanceOf(a2) == 0
    # Check that max amount can be burned
    test_token.burn(MAX_UINT256, transact={'from': _lend_token_holder})
    assert test_token.balanceOf(_lend_token_holder) == 0


def test_transferFrom_and_Allowance(w3, assert_tx_failed, get_ERC20_contract, get_CurrencyDao_contract,
    Deployer, Governor,
    Whale, Lend_token,
    ProtocolDao):
    minter, a1, a2, a3 = w3.eth.accounts[0:4]
    # get CurrencyDao
    CurrencyDao = get_CurrencyDao_contract(address=ProtocolDao.daos(PROTOCOL_CONSTANTS['DAO_CURRENCY']))
    # assign one of the accounts as _lend_token_holder
    _lend_token_holder = w3.eth.accounts[5]
    # initialize CurrencyDao
    tx_hash = ProtocolDao.initialize_currency_dao(transact={'from': Deployer})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    tx_hash = ProtocolDao.set_token_support(Lend_token.address, True, transact={'from': Governor, 'gas': 2000000})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    # _lend_token_holder buys 1000 lend token from a 3rd party exchange
    tx_hash = Lend_token.transfer(_lend_token_holder, Web3.toWei(1000, 'ether'), transact={'from': Whale})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    # _lend_token_holder authorizes CurrencyDao to spend 800 Lend_token
    tx_hash = Lend_token.approve(CurrencyDao.address, Web3.toWei(800, 'ether'), transact={'from': _lend_token_holder})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    # get L_Lend_token
    test_token = get_ERC20_contract(address=CurrencyDao.token_addresses__l(Lend_token.address))
    # _lend_token_holder wraps 800 Lend_token to L_lend_token
    tx_hash = CurrencyDao.wrap(Lend_token.address, Web3.toWei(800, 'ether'), transact={'from': _lend_token_holder, 'gas': 145000})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    assert_tx_failed(lambda: test_token.burn(1, transact={'from': a2}))
    test_token.transfer(a2, 1, transact={'from': _lend_token_holder})
    test_token.burn(1, transact={'from': _lend_token_holder})
    # This should fail; no allowance or balance (0 always succeeds)
    assert_tx_failed(lambda: test_token.transferFrom(_lend_token_holder, a3, 1, transact={'from': a2}))
    test_token.transferFrom(_lend_token_holder, a3, 0, transact={'from': a2})
    # Correct call to approval should update allowance (but not for reverse pair)
    test_token.approve(a2, 1, transact={'from': _lend_token_holder})
    assert test_token.allowance(_lend_token_holder, a2) == 1
    assert test_token.allowance(a2, _lend_token_holder) == 0
    # transferFrom should succeed when allowed, fail with wrong sender
    assert_tx_failed(lambda: test_token.transferFrom(_lend_token_holder, a3, 1, transact={'from': a3}))
    assert test_token.balanceOf(a2) == 1
    test_token.approve(_lend_token_holder, 1, transact={'from': a2})
    test_token.transferFrom(a2, a3, 1, transact={'from': _lend_token_holder})
    # Allowance should be correctly updated after transferFrom
    assert test_token.allowance(a2, _lend_token_holder) == 0
    # transferFrom with no funds should fail despite approval
    test_token.approve(_lend_token_holder, 1, transact={'from': a2})
    assert test_token.allowance(a2, _lend_token_holder) == 1
    assert_tx_failed(lambda: test_token.transferFrom(a2, a3, 1, transact={'from': _lend_token_holder}))
    # 0-approve should not change balance or allow transferFrom to change balance
    test_token.transfer(a2, 1, transact={'from': _lend_token_holder})
    assert test_token.allowance(a2, _lend_token_holder) == 1
    test_token.approve(_lend_token_holder, 0, transact={'from': a2})
    assert test_token.allowance(a2, _lend_token_holder) == 0
    test_token.approve(_lend_token_holder, 0, transact={'from': a2})
    assert test_token.allowance(a2, _lend_token_holder) == 0
    assert_tx_failed(lambda: test_token.transferFrom(a2, a3, 1, transact={'from': _lend_token_holder}))
    # Test that if non-zero approval exists, 0-approval is NOT required to proceed
    # a non-conformant implementation is described in countermeasures at
    # https://docs.google.com/document/d/1YLPtQxZu1UAvO9cZ1O2RPXBbT0mooh4DYKjA_jp-RLM/edit#heading=h.m9fhqynw2xvt
    # the final spec insists on NOT using this behavior
    assert test_token.allowance(a2, _lend_token_holder) == 0
    test_token.approve(_lend_token_holder, 1, transact={'from': a2})
    assert test_token.allowance(a2, _lend_token_holder) == 1
    test_token.approve(_lend_token_holder, 2, transact={'from': a2})
    assert test_token.allowance(a2, _lend_token_holder) == 2
    # Check that approving 0 then amount also works
    test_token.approve(_lend_token_holder, 0, transact={'from': a2})
    assert test_token.allowance(a2, _lend_token_holder) == 0
    test_token.approve(_lend_token_holder, 5, transact={'from': a2})
    assert test_token.allowance(a2, _lend_token_holder) == 5


def test_burnFrom_and_Allowance(w3, assert_tx_failed, get_ERC20_contract, get_CurrencyDao_contract,
    Deployer, Governor,
    Whale, Lend_token,
    ProtocolDao):
    minter, a1, a2, a3 = w3.eth.accounts[0:4]
    # get CurrencyDao
    CurrencyDao = get_CurrencyDao_contract(address=ProtocolDao.daos(PROTOCOL_CONSTANTS['DAO_CURRENCY']))
    # assign one of the accounts as _lend_token_holder
    _lend_token_holder = w3.eth.accounts[5]
    # initialize CurrencyDao
    tx_hash = ProtocolDao.initialize_currency_dao(transact={'from': Deployer})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    tx_hash = ProtocolDao.set_token_support(Lend_token.address, True, transact={'from': Governor, 'gas': 2000000})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    # _lend_token_holder buys 1000 lend token from a 3rd party exchange
    tx_hash = Lend_token.transfer(_lend_token_holder, Web3.toWei(1000, 'ether'), transact={'from': Whale})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    # _lend_token_holder authorizes CurrencyDao to spend 800 Lend_token
    tx_hash = Lend_token.approve(CurrencyDao.address, Web3.toWei(800, 'ether'), transact={'from': _lend_token_holder})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    # get L_Lend_token
    test_token = get_ERC20_contract(address=CurrencyDao.token_addresses__l(Lend_token.address))
    # _lend_token_holder wraps 800 Lend_token to L_lend_token
    tx_hash = CurrencyDao.wrap(Lend_token.address, Web3.toWei(800, 'ether'), transact={'from': _lend_token_holder, 'gas': 145000})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    assert_tx_failed(lambda: test_token.burn(1, transact={'from': a2}))
    test_token.transfer(a2, 1, transact={'from': _lend_token_holder})
    test_token.burn(1, transact={'from': _lend_token_holder})
    # This should fail; no allowance or balance (0 always succeeds)
    assert_tx_failed(lambda: test_token.burnFrom(_lend_token_holder, 1, transact={'from': a2}))
    test_token.burnFrom(_lend_token_holder, 0, transact={'from': a2})
    # Correct call to approval should update allowance (but not for reverse pair)
    test_token.approve(a2, 1, transact={'from': _lend_token_holder})
    assert test_token.allowance(_lend_token_holder, a2) == 1
    assert test_token.allowance(a2, _lend_token_holder) == 0
    # transferFrom should succeed when allowed, fail with wrong sender
    assert_tx_failed(lambda: test_token.burnFrom(a2, 1, transact={'from': a3}))
    assert test_token.balanceOf(a2) == 1
    test_token.approve(_lend_token_holder, 1, transact={'from': a2})
    test_token.burnFrom(a2, 1, transact={'from': _lend_token_holder})
    # Allowance should be correctly updated after transferFrom
    assert test_token.allowance(a2, _lend_token_holder) == 0
    # transferFrom with no funds should fail despite approval
    test_token.approve(_lend_token_holder, 1, transact={'from': a2})
    assert test_token.allowance(a2, _lend_token_holder) == 1
    assert_tx_failed(lambda: test_token.burnFrom(a2, 1, transact={'from': _lend_token_holder}))
    # 0-approve should not change balance or allow transferFrom to change balance
    test_token.transfer(a2, 1, transact={'from': _lend_token_holder})
    assert test_token.allowance(a2, _lend_token_holder) == 1
    test_token.approve(_lend_token_holder, 0, transact={'from': a2})
    assert test_token.allowance(a2, _lend_token_holder) == 0
    test_token.approve(_lend_token_holder, 0, transact={'from': a2})
    assert test_token.allowance(a2, _lend_token_holder) == 0
    assert_tx_failed(lambda: test_token.burnFrom(a2, 1, transact={'from': _lend_token_holder}))
    # Test that if non-zero approval exists, 0-approval is NOT required to proceed
    # a non-conformant implementation is described in countermeasures at
    # https://docs.google.com/document/d/1YLPtQxZu1UAvO9cZ1O2RPXBbT0mooh4DYKjA_jp-RLM/edit#heading=h.m9fhqynw2xvt
    # the final spec insists on NOT using this behavior
    assert test_token.allowance(a2, _lend_token_holder) == 0
    test_token.approve(_lend_token_holder, 1, transact={'from': a2})
    assert test_token.allowance(a2, _lend_token_holder) == 1
    test_token.approve(_lend_token_holder, 2, transact={'from': a2})
    assert test_token.allowance(a2, _lend_token_holder) == 2
    # Check that approving 0 then amount also works
    test_token.approve(_lend_token_holder, 0, transact={'from': a2})
    assert test_token.allowance(a2, _lend_token_holder) == 0
    test_token.approve(_lend_token_holder, 5, transact={'from': a2})
    assert test_token.allowance(a2, _lend_token_holder) == 5
    # Check that burnFrom to ZERO_ADDRESS failed
    assert_tx_failed(lambda: test_token.burnFrom(
        ZERO_ADDRESS, 0, transact={'from': _lend_token_holder}))


def test_raw_logs(w3, get_log_args, get_ERC20_contract, get_CurrencyDao_contract, Deployer, Governor,
    Whale, Lend_token,
    ProtocolDao):
    minter, a1, a2, a3 = w3.eth.accounts[0:4]
    # get CurrencyDao
    CurrencyDao = get_CurrencyDao_contract(address=ProtocolDao.daos(PROTOCOL_CONSTANTS['DAO_CURRENCY']))
    # assign one of the accounts as _lend_token_holder
    _lend_token_holder = w3.eth.accounts[5]
    # initialize CurrencyDao
    tx_hash = ProtocolDao.initialize_currency_dao(transact={'from': Deployer})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    tx_hash = ProtocolDao.set_token_support(Lend_token.address, True, transact={'from': Governor, 'gas': 2000000})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    # _lend_token_holder buys 1000 lend token from a 3rd party exchange
    tx_hash = Lend_token.transfer(_lend_token_holder, Web3.toWei(1000, 'ether'), transact={'from': Whale})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    # _lend_token_holder authorizes CurrencyDao to spend 800 Lend_token
    tx_hash = Lend_token.approve(CurrencyDao.address,  Web3.toWei(800, 'ether'), transact={'from': _lend_token_holder})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    # get L_Lend_token
    test_token = get_ERC20_contract(address=CurrencyDao.token_addresses__l(Lend_token.address))
    # _lend_token_holder wraps 800 Lend_token to L_lend_token
    tx_hash = CurrencyDao.wrap(Lend_token.address, Web3.toWei(800, 'ether'), transact={'from': _lend_token_holder, 'gas': 145000})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    # Check that mint appropriately emits Transfer event
    # args = get_log_args(tx_hash, test_token, 'Transfer')
    # assert args._from == ZERO_ADDRESS
    # assert args._to == _lend_token_holder
    # assert args._value == 2

    # Check that burn appropriately emits Transfer event
    args = get_log_args(test_token.burn(1, transact={'from': _lend_token_holder}), test_token, 'Transfer')
    assert args._from == _lend_token_holder
    assert args._to == ZERO_ADDRESS
    assert args._value == 1

    args = get_log_args(test_token.burn(0, transact={'from': _lend_token_holder}), test_token, 'Transfer')
    assert args._from == _lend_token_holder
    assert args._to == ZERO_ADDRESS
    assert args._value == 0

    # Check that transfer appropriately emits Transfer event
    args = get_log_args(test_token.transfer(
        a2, 1, transact={'from': _lend_token_holder}), test_token, 'Transfer')
    assert args._from == _lend_token_holder
    assert args._to == a2
    assert args._value == 1

    args = get_log_args(test_token.transfer(
        a2, 0, transact={'from': _lend_token_holder}), test_token, 'Transfer')
    assert args._from == _lend_token_holder
    assert args._to == a2
    assert args._value == 0

    # Check that approving amount emits events
    args = get_log_args(test_token.approve(_lend_token_holder, 1, transact={'from': a2}), test_token, 'Approval')
    assert args._owner == a2
    assert args._spender == _lend_token_holder
    assert args._value == 1

    args = get_log_args(test_token.approve(a2, 0, transact={'from': a3}), test_token, 'Approval')
    assert args._owner == a3
    assert args._spender == a2
    assert args._value == 0

    # Check that transferFrom appropriately emits Transfer event
    args = get_log_args(test_token.transferFrom(
        a2, a3, 1, transact={'from': _lend_token_holder}), test_token, 'Transfer')
    assert args._from == a2
    assert args._to == a3
    assert args._value == 1

    args = get_log_args(test_token.transferFrom(
        a2, a3, 0, transact={'from': _lend_token_holder}), test_token, 'Transfer')
    assert args._from == a2
    assert args._to == a3
    assert args._value == 0
