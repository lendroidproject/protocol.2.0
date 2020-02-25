import pytest
from web3 import Web3
from conftest import (
    MAX_UINT256,
    ZERO_ADDRESS
)


def test_initial_state(accounts, get_ERC20_contract):
    a1, a2, a3 = accounts[1:4]
    test_token = get_ERC20_contract('TEST Support Token', 'TST', 18, 12000000000)
    # Check total supply, name, symbol and decimals are correctly set
    assert test_token.totalSupply() == Web3.toWei(12000000000, 'ether')
    assert test_token.name() == 'TEST Support Token'
    assert test_token.symbol() == 'TST'
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


def test_mint_and_burn(accounts, assert_tx_failed, get_ERC20_contract):
    minter, a1, a2 = accounts[0:3]
    test_token = get_ERC20_contract('TEST Support Token', 'TST', 18, 12000000000)
    # Test scenario were mints 2 to a1, burns twice (check balance consistency)
    assert test_token.balanceOf(a1) == 0
    test_token.mint(a1, 2, {'from': minter})
    assert test_token.balanceOf(a1) == 2
    test_token.burn(2, {'from': a1})
    assert test_token.balanceOf(a1) == 0
    assert_tx_failed(lambda: test_token.burn(2, {'from': a1}))
    assert test_token.balanceOf(a1) == 0
    # Test scenario were mintes 0 to a2, burns (check balance consistency, false burn)
    test_token.mint(a2, 0, {'from': minter})
    assert test_token.balanceOf(a2) == 0
    assert_tx_failed(lambda: test_token.burn(2, {'from': a2}))
    # Check that a1 cannot burn after depleting their balance
    assert_tx_failed(lambda: test_token.burn(1, {'from': a1}))
    # Check that a1, a2 cannot mint
    assert_tx_failed(lambda: test_token.mint(a1, 1, {'from': a1}))
    assert_tx_failed(lambda: test_token.mint(a2, 1, {'from': a2}))
    # Check that mint to ZERO_ADDRESS failed
    assert_tx_failed(lambda: test_token.mint(ZERO_ADDRESS, 1, {'from': a1}))
    assert_tx_failed(lambda: test_token.mint(
        ZERO_ADDRESS, 1, {'from': minter}))


def test_totalSupply(accounts, assert_tx_failed, get_ERC20_contract):
    # Test total supply initially, after mint, between two burns, and after failed burn
    minter, a1 = accounts[0:2]
    test_token = get_ERC20_contract('TEST Support Token', 'TST', 18, 0)
    assert test_token.totalSupply() == 0
    test_token.mint(a1, 2, {'from': minter})
    assert test_token.totalSupply() == 2
    test_token.burn(1, {'from': a1})
    assert test_token.totalSupply() == 1
    test_token.burn(1, {'from': a1})
    assert test_token.totalSupply() == 0
    assert_tx_failed(lambda: test_token.burn(1, {'from': a1}))
    assert test_token.totalSupply() == 0
    # Test that 0-valued mint can't affect supply
    test_token.mint(a1, 0, {'from': minter})
    assert test_token.totalSupply() == 0


def test_transfer(accounts, assert_tx_failed, get_ERC20_contract):
    minter, a1, a2 = accounts[0:3]
    test_token = get_ERC20_contract('TEST Support Token', 'TST', 18, 0)
    assert_tx_failed(lambda: test_token.burn(1, {'from': a2}))
    test_token.mint(a1, 2, {'from': minter})
    test_token.burn(1, {'from': a1})
    test_token.transfer(a2, 1, {'from': a1})
    assert_tx_failed(lambda: test_token.burn(1, {'from': a1}))
    test_token.burn(1, {'from': a2})
    assert_tx_failed(lambda: test_token.burn(1, {'from': a2}))
    # Ensure transfer fails with insufficient balance
    assert_tx_failed(lambda: test_token.transfer(a1, 1, {'from': a2}))
    # Ensure 0-transfer always succeeds
    test_token.transfer(a1, 0, {'from': a2})
    # Ensure transfer fails when recipient is ZERO_ADDRESS
    assert_tx_failed(lambda: test_token.transfer(ZERO_ADDRESS, 0, {'from': a2}))


def test_maxInts(accounts, assert_tx_failed, get_ERC20_contract):
    minter, a1, a2 = accounts[0:3]
    test_token = get_ERC20_contract('TEST Support Token', 'TST', 18, 0)
    test_token.mint(a1, MAX_UINT256, {'from': minter})
    assert test_token.balanceOf(a1) == MAX_UINT256
    assert_tx_failed(lambda: test_token.mint(a1, 1, {'from': a1}))
    assert_tx_failed(lambda: test_token.mint(a1, MAX_UINT256, {'from': a1}))
    # Check that totalSupply cannot overflow, even when mint to other account
    assert_tx_failed(lambda: test_token.mint(a2, 1, {'from': minter}))
    # Check that corresponding mint is allowed after burn
    test_token.burn(1, {'from': a1})
    test_token.mint(a2, 1, {'from': minter})
    assert_tx_failed(lambda: test_token.mint(a2, 1, {'from': minter}))
    test_token.transfer(a1, 1, {'from': a2})
    # Assert that after obtaining max number of tokens, a1 can transfer those but no more
    assert test_token.balanceOf(a1) == MAX_UINT256
    test_token.transfer(a2, MAX_UINT256, {'from': a1})
    assert test_token.balanceOf(a2) == MAX_UINT256
    assert test_token.balanceOf(a1) == 0
    # [ next line should never work in EVM ]
    with pytest.raises(OverflowError):
        test_token.transfer(a1, MAX_UINT256 + 1, {'from': a2})
    # Check approve/allowance w max possible token values
    assert test_token.balanceOf(a2) == MAX_UINT256
    test_token.approve(a1, MAX_UINT256, {'from': a2})
    test_token.transferFrom(a2, a1, MAX_UINT256, {'from': a1})
    assert test_token.balanceOf(a1) == MAX_UINT256
    assert test_token.balanceOf(a2) == 0
    # Check that max amount can be burned
    test_token.burn(MAX_UINT256, {'from': a1})
    assert test_token.balanceOf(a1) == 0


def test_transferFrom_and_Allowance(accounts, assert_tx_failed, get_ERC20_contract):
    minter, a1, a2, a3 = accounts[0:4]
    test_token = get_ERC20_contract('TEST Support Token', 'TST', 18, 0)
    assert_tx_failed(lambda: test_token.burn(1, {'from': a2}))
    test_token.mint(a1, 1, {'from': minter})
    test_token.mint(a2, 1, {'from': minter})
    test_token.burn(1, {'from': a1})
    # This should fail; no allowance or balance (0 always succeeds)
    assert_tx_failed(lambda: test_token.transferFrom(a1, a3, 1, {'from': a2}))
    test_token.transferFrom(a1, a3, 0, {'from': a2})
    # Correct call to approval should update allowance (but not for reverse pair)
    test_token.approve(a2, 1, {'from': a1})
    assert test_token.allowance(a1, a2) == 1
    assert test_token.allowance(a2, a1) == 0
    # transferFrom should succeed when allowed, fail with wrong sender
    assert_tx_failed(lambda: test_token.transferFrom(a1, a3, 1, {'from': a3}))
    assert test_token.balanceOf(a2) == 1
    test_token.approve(a1, 1, {'from': a2})
    # Ensure transferFrom fails when recipient is ZERO_ADDRESS
    assert_tx_failed(lambda: test_token.transferFrom(a2, ZERO_ADDRESS, 1, {'from': a1}))
    test_token.transferFrom(a2, a3, 1, {'from': a1})
    # Allowance should be correctly updated after transferFrom
    assert test_token.allowance(a2, a1) == 0
    # transferFrom with no funds should fail despite approval
    test_token.approve(a1, 1, {'from': a2})
    assert test_token.allowance(a2, a1) == 1
    assert_tx_failed(lambda: test_token.transferFrom(a2, a3, 1, {'from': a1}))
    # 0-approve should not change balance or allow transferFrom to change balance
    test_token.mint(a2, 1, {'from': minter})
    assert test_token.allowance(a2, a1) == 1
    test_token.approve(a1, 0, {'from': a2})
    assert test_token.allowance(a2, a1) == 0
    test_token.approve(a1, 0, {'from': a2})
    assert test_token.allowance(a2, a1) == 0
    assert_tx_failed(lambda: test_token.transferFrom(a2, a3, 1, {'from': a1}))
    # Test that if non-zero approval exists, 0-approval is NOT required to proceed
    # a non-conformant implementation is described in countermeasures at
    # https://docs.google.com/document/d/1YLPtQxZu1UAvO9cZ1O2RPXBbT0mooh4DYKjA_jp-RLM/edit#heading=h.m9fhqynw2xvt
    # the final spec insists on NOT using this behavior
    assert test_token.allowance(a2, a1) == 0
    test_token.approve(a1, 1, {'from': a2})
    assert test_token.allowance(a2, a1) == 1
    test_token.approve(a1, 2, {'from': a2})
    assert test_token.allowance(a2, a1) == 2
    # Check that approving 0 then amount also works
    test_token.approve(a1, 0, {'from': a2})
    assert test_token.allowance(a2, a1) == 0
    test_token.approve(a1, 5, {'from': a2})
    assert test_token.allowance(a2, a1) == 5


def test_burnFrom_and_Allowance(accounts, assert_tx_failed, get_ERC20_contract):
    minter, a1, a2, a3 = accounts[0:4]
    test_token = get_ERC20_contract('TEST Support Token', 'TST', 18, 0)
    assert_tx_failed(lambda: test_token.burn(1, {'from': a2}))
    test_token.mint(a1, 1, {'from': minter})
    test_token.mint(a2, 1, {'from': minter})
    test_token.burn(1, {'from': a1})
    # This should fail; no allowance or balance (0 always succeeds)
    assert_tx_failed(lambda: test_token.burnFrom(a1, 1, {'from': a2}))
    test_token.burnFrom(a1, 0, {'from': a2})
    # Correct call to approval should update allowance (but not for reverse pair)
    test_token.approve(a2, 1, {'from': a1})
    assert test_token.allowance(a1, a2) == 1
    assert test_token.allowance(a2, a1) == 0
    # transferFrom should succeed when allowed, fail with wrong sender
    assert_tx_failed(lambda: test_token.burnFrom(a2, 1, {'from': a3}))
    assert test_token.balanceOf(a2) == 1
    test_token.approve(a1, 1, {'from': a2})
    test_token.burnFrom(a2, 1, {'from': a1})
    # Allowance should be correctly updated after transferFrom
    assert test_token.allowance(a2, a1) == 0
    # transferFrom with no funds should fail despite approval
    test_token.approve(a1, 1, {'from': a2})
    assert test_token.allowance(a2, a1) == 1
    assert_tx_failed(lambda: test_token.burnFrom(a2, 1, {'from': a1}))
    # 0-approve should not change balance or allow transferFrom to change balance
    test_token.mint(a2, 1, {'from': minter})
    assert test_token.allowance(a2, a1) == 1
    test_token.approve(a1, 0, {'from': a2})
    assert test_token.allowance(a2, a1) == 0
    test_token.approve(a1, 0, {'from': a2})
    assert test_token.allowance(a2, a1) == 0
    assert_tx_failed(lambda: test_token.burnFrom(a2, 1, {'from': a1}))
    # Test that if non-zero approval exists, 0-approval is NOT required to proceed
    # a non-conformant implementation is described in countermeasures at
    # https://docs.google.com/document/d/1YLPtQxZu1UAvO9cZ1O2RPXBbT0mooh4DYKjA_jp-RLM/edit#heading=h.m9fhqynw2xvt
    # the final spec insists on NOT using this behavior
    assert test_token.allowance(a2, a1) == 0
    test_token.approve(a1, 1, {'from': a2})
    assert test_token.allowance(a2, a1) == 1
    test_token.approve(a1, 2, {'from': a2})
    assert test_token.allowance(a2, a1) == 2
    # Check that approving 0 then amount also works
    test_token.approve(a1, 0, {'from': a2})
    assert test_token.allowance(a2, a1) == 0
    test_token.approve(a1, 5, {'from': a2})
    assert test_token.allowance(a2, a1) == 5
    # Check that burnFrom to ZERO_ADDRESS failed
    assert_tx_failed(lambda: test_token.burnFrom(
        ZERO_ADDRESS, 0, {'from': a1}))


def test_raw_logs(accounts, get_log_args, get_ERC20_contract):
    minter, a1, a2, a3 = accounts[0:4]
    test_token = get_ERC20_contract('TEST Support Token', 'TST', 18, 0)

    # Check that mint appropriately emits Transfer event
    args = get_log_args(
        test_token.mint(a1, 2, {'from': minter}), 'Transfer')
    assert args['_from'] == ZERO_ADDRESS
    assert args['_to'] == a1
    assert args['_value'] == 2

    args = get_log_args(
        test_token.mint(a1, 0, {'from': minter}), 'Transfer')
    assert args['_from'] == ZERO_ADDRESS
    assert args['_to'] == a1
    assert args['_value'] == 0

    # Check that burn appropriately emits Transfer event
    args = get_log_args(test_token.burn(1, {'from': a1}), 'Transfer')
    assert args['_from'] == a1
    assert args['_to'] == ZERO_ADDRESS
    assert args['_value'] == 1

    args = get_log_args(test_token.burn(0, {'from': a1}), 'Transfer')
    assert args['_from'] == a1
    assert args['_to'] == ZERO_ADDRESS
    assert args['_value'] == 0

    # Check that transfer appropriately emits Transfer event
    args = get_log_args(test_token.transfer(a2, 1, {'from': a1}), 'Transfer')
    assert args['_from'] == a1
    assert args['_to'] == a2
    assert args['_value'] == 1

    args = get_log_args(test_token.transfer(a2, 0, {'from': a1}), 'Transfer')
    assert args['_from'] == a1
    assert args['_to'] == a2
    assert args['_value'] == 0

    # Check that approving amount emits events
    args = get_log_args(test_token.approve(a1, 1, {'from': a2}), 'Approval')
    assert args['_owner'] == a2
    assert args['_spender'] == a1
    assert args['_value'] == 1

    args = get_log_args(test_token.approve(a2, 0, {'from': a3}), 'Approval')
    assert args['_owner'] == a3
    assert args['_spender'] == a2
    assert args['_value'] == 0

    # Check that transferFrom appropriately emits Transfer event
    args = get_log_args(test_token.transferFrom(a2, a3, 1, {'from': a1}), 'Transfer')
    assert args['_from'] == a2
    assert args['_to'] == a3
    assert args['_value'] == 1

    args = get_log_args(test_token.transferFrom(a2, a3, 0, {'from': a1}), 'Transfer')
    assert args['_from'] == a2
    assert args['_to'] == a3
    assert args['_value'] == 0
