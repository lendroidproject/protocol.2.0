from web3 import Web3
from conftest import (
    ZERO_ADDRESS,
)
# def test_initial_state(w3, get_ERC20_contract):
#     a1, a2, a3 = w3.eth.accounts[1:4]
#     test_token = get_ERC20_contract(
#         'TEST Support Token', 'TST', 18, 12000000000
#     )
#     # Check total supply, name, symbol and decimals are correctly set
#     assert test_token.totalSupply() == Web3.toWei(12000000000, 'ether')
#     assert test_token.name() == 'TEST Support Token'
#     assert test_token.symbol() == 'TST'
#     assert test_token.decimals() == 18
#     # Check several account balances as 0
#     assert test_token.balanceOf(a1) == 0
#     assert test_token.balanceOf(a2) == 0
#     assert test_token.balanceOf(a3) == 0
#     # Check several allowances as 0
#     assert test_token.allowance(a1, a1) == 0
#     assert test_token.allowance(a1, a2) == 0
#     assert test_token.allowance(a1, a3) == 0
#     assert test_token.allowance(a2, a3) == 0


def test_mint_and_burn(w3, assert_tx_failed, get_ERC20_contract):
    minter, a1, a2 = w3.eth.accounts[0:3]
    test_token = get_ERC20_contract(
        'TEST Support Token', 'TST', 18, 12000000000
    )
    # Test scenario were mints 2 to a1, burns twice (check balance consistency)
    assert test_token.balanceOf(a1) == 0
    test_token.mint(a1, 2, transact={'from': minter})
    assert test_token.balanceOf(a1) == 2
    test_token.burn(2, transact={'from': a1})
    assert test_token.balanceOf(a1) == 0
    assert_tx_failed(lambda: test_token.burn(2, transact={'from': a1}))
    assert test_token.balanceOf(a1) == 0
    # Test scenario were mintes 0 to a2, burns (check balance consistency, false burn)
    test_token.mint(a2, 0, transact={'from': minter})
    assert test_token.balanceOf(a2) == 0
    assert_tx_failed(lambda: test_token.burn(2, transact={'from': a2}))
    # Check that a1 cannot burn after depleting their balance
    assert_tx_failed(lambda: test_token.burn(1, transact={'from': a1}))
    # Check that a1, a2 cannot mint
    assert_tx_failed(lambda: test_token.mint(a1, 1, transact={'from': a1}))
    assert_tx_failed(lambda: test_token.mint(a2, 1, transact={'from': a2}))
    # Check that mint to ZERO_ADDRESS failed
    assert_tx_failed(lambda: test_token.mint(ZERO_ADDRESS, 1, transact={'from': a1}))
    assert_tx_failed(lambda: test_token.mint(
        ZERO_ADDRESS, 1, transact={'from': minter}))
#
#
# def test_totalSupply(c, w3, assert_tx_failed):
#     # Test total supply initially, after mint, between two burns, and after failed burn
#     minter, a1 = w3.eth.accounts[0:2]
#     assert c.totalSupply() == 0
#     c.mint(a1, 2, transact={'from': minter})
#     assert c.totalSupply() == 2
#     c.burn(1, transact={'from': a1})
#     assert c.totalSupply() == 1
#     c.burn(1, transact={'from': a1})
#     assert c.totalSupply() == 0
#     assert_tx_failed(lambda: c.burn(1, transact={'from': a1}))
#     assert c.totalSupply() == 0
#     # Test that 0-valued mint can't affect supply
#     c.mint(a1, 0, transact={'from': minter})
#     assert c.totalSupply() == 0
#
#
# def test_transfer(c, w3, assert_tx_failed):
#     minter, a1, a2 = w3.eth.accounts[0:3]
#     assert_tx_failed(lambda: c.burn(1, transact={'from': a2}))
#     c.mint(a1, 2, transact={'from': minter})
#     c.burn(1, transact={'from': a1})
#     c.transfer(a2, 1, transact={'from': a1})
#     assert_tx_failed(lambda: c.burn(1, transact={'from': a1}))
#     c.burn(1, transact={'from': a2})
#     assert_tx_failed(lambda: c.burn(1, transact={'from': a2}))
#     # Ensure transfer fails with insufficient balance
#     assert_tx_failed(lambda: c.transfer(a1, 1, transact={'from': a2}))
#     # Ensure 0-transfer always succeeds
#     c.transfer(a1, 0, transact={'from': a2})
#
#
# def test_maxInts(c, w3, assert_tx_failed):
#     minter, a1, a2 = w3.eth.accounts[0:3]
#     c.mint(a1, MAX_UINT256, transact={'from': minter})
#     assert c.balanceOf(a1) == MAX_UINT256
#     assert_tx_failed(lambda: c.mint(a1, 1, transact={'from': a1}))
#     assert_tx_failed(lambda: c.mint(a1, MAX_UINT256, transact={'from': a1}))
#     # Check that totalSupply cannot overflow, even when mint to other account
#     assert_tx_failed(lambda: c.mint(a2, 1, transact={'from': minter}))
#     # Check that corresponding mint is allowed after burn
#     c.burn(1, transact={'from': a1})
#     c.mint(a2, 1, transact={'from': minter})
#     assert_tx_failed(lambda: c.mint(a2, 1, transact={'from': minter}))
#     c.transfer(a1, 1, transact={'from': a2})
#     # Assert that after obtaining max number of tokens, a1 can transfer those but no more
#     assert c.balanceOf(a1) == MAX_UINT256
#     c.transfer(a2, MAX_UINT256, transact={'from': a1})
#     assert c.balanceOf(a2) == MAX_UINT256
#     assert c.balanceOf(a1) == 0
#     # [ next line should never work in EVM ]
#     with pytest.raises(ValidationError):
#         c.transfer(a1, MAX_UINT256 + 1, transact={'from': a2})
#     # Check approve/allowance w max possible token values
#     assert c.balanceOf(a2) == MAX_UINT256
#     c.approve(a1, MAX_UINT256, transact={'from': a2})
#     c.transferFrom(a2, a1, MAX_UINT256, transact={'from': a1})
#     assert c.balanceOf(a1) == MAX_UINT256
#     assert c.balanceOf(a2) == 0
#     # Check that max amount can be burned
#     c.burn(MAX_UINT256, transact={'from': a1})
#     assert c.balanceOf(a1) == 0
#
#
# def test_transferFrom_and_Allowance(c, w3, assert_tx_failed):
#     minter, a1, a2, a3 = w3.eth.accounts[0:4]
#     assert_tx_failed(lambda: c.burn(1, transact={'from': a2}))
#     c.mint(a1, 1, transact={'from': minter})
#     c.mint(a2, 1, transact={'from': minter})
#     c.burn(1, transact={'from': a1})
#     # This should fail; no allowance or balance (0 always succeeds)
#     assert_tx_failed(lambda: c.transferFrom(a1, a3, 1, transact={'from': a2}))
#     c.transferFrom(a1, a3, 0, transact={'from': a2})
#     # Correct call to approval should update allowance (but not for reverse pair)
#     c.approve(a2, 1, transact={'from': a1})
#     assert c.allowance(a1, a2) == 1
#     assert c.allowance(a2, a1) == 0
#     # transferFrom should succeed when allowed, fail with wrong sender
#     assert_tx_failed(lambda: c.transferFrom(a1, a3, 1, transact={'from': a3}))
#     assert c.balanceOf(a2) == 1
#     c.approve(a1, 1, transact={'from': a2})
#     c.transferFrom(a2, a3, 1, transact={'from': a1})
#     # Allowance should be correctly updated after transferFrom
#     assert c.allowance(a2, a1) == 0
#     # transferFrom with no funds should fail despite approval
#     c.approve(a1, 1, transact={'from': a2})
#     assert c.allowance(a2, a1) == 1
#     assert_tx_failed(lambda: c.transferFrom(a2, a3, 1, transact={'from': a1}))
#     # 0-approve should not change balance or allow transferFrom to change balance
#     c.mint(a2, 1, transact={'from': minter})
#     assert c.allowance(a2, a1) == 1
#     c.approve(a1, 0, transact={'from': a2})
#     assert c.allowance(a2, a1) == 0
#     c.approve(a1, 0, transact={'from': a2})
#     assert c.allowance(a2, a1) == 0
#     assert_tx_failed(lambda: c.transferFrom(a2, a3, 1, transact={'from': a1}))
#     # Test that if non-zero approval exists, 0-approval is NOT required to proceed
#     # a non-conformant implementation is described in countermeasures at
#     # https://docs.google.com/document/d/1YLPtQxZu1UAvO9cZ1O2RPXBbT0mooh4DYKjA_jp-RLM/edit#heading=h.m9fhqynw2xvt
#     # the final spec insists on NOT using this behavior
#     assert c.allowance(a2, a1) == 0
#     c.approve(a1, 1, transact={'from': a2})
#     assert c.allowance(a2, a1) == 1
#     c.approve(a1, 2, transact={'from': a2})
#     assert c.allowance(a2, a1) == 2
#     # Check that approving 0 then amount also works
#     c.approve(a1, 0, transact={'from': a2})
#     assert c.allowance(a2, a1) == 0
#     c.approve(a1, 5, transact={'from': a2})
#     assert c.allowance(a2, a1) == 5
#
#
# def test_burnFrom_and_Allowance(c, w3, assert_tx_failed):
#     minter, a1, a2, a3 = w3.eth.accounts[0:4]
#     assert_tx_failed(lambda: c.burn(1, transact={'from': a2}))
#     c.mint(a1, 1, transact={'from': minter})
#     c.mint(a2, 1, transact={'from': minter})
#     c.burn(1, transact={'from': a1})
#     # This should fail; no allowance or balance (0 always succeeds)
#     assert_tx_failed(lambda: c.burnFrom(a1, 1, transact={'from': a2}))
#     c.burnFrom(a1, 0, transact={'from': a2})
#     # Correct call to approval should update allowance (but not for reverse pair)
#     c.approve(a2, 1, transact={'from': a1})
#     assert c.allowance(a1, a2) == 1
#     assert c.allowance(a2, a1) == 0
#     # transferFrom should succeed when allowed, fail with wrong sender
#     assert_tx_failed(lambda: c.burnFrom(a2, 1, transact={'from': a3}))
#     assert c.balanceOf(a2) == 1
#     c.approve(a1, 1, transact={'from': a2})
#     c.burnFrom(a2, 1, transact={'from': a1})
#     # Allowance should be correctly updated after transferFrom
#     assert c.allowance(a2, a1) == 0
#     # transferFrom with no funds should fail despite approval
#     c.approve(a1, 1, transact={'from': a2})
#     assert c.allowance(a2, a1) == 1
#     assert_tx_failed(lambda: c.burnFrom(a2, 1, transact={'from': a1}))
#     # 0-approve should not change balance or allow transferFrom to change balance
#     c.mint(a2, 1, transact={'from': minter})
#     assert c.allowance(a2, a1) == 1
#     c.approve(a1, 0, transact={'from': a2})
#     assert c.allowance(a2, a1) == 0
#     c.approve(a1, 0, transact={'from': a2})
#     assert c.allowance(a2, a1) == 0
#     assert_tx_failed(lambda: c.burnFrom(a2, 1, transact={'from': a1}))
#     # Test that if non-zero approval exists, 0-approval is NOT required to proceed
#     # a non-conformant implementation is described in countermeasures at
#     # https://docs.google.com/document/d/1YLPtQxZu1UAvO9cZ1O2RPXBbT0mooh4DYKjA_jp-RLM/edit#heading=h.m9fhqynw2xvt
#     # the final spec insists on NOT using this behavior
#     assert c.allowance(a2, a1) == 0
#     c.approve(a1, 1, transact={'from': a2})
#     assert c.allowance(a2, a1) == 1
#     c.approve(a1, 2, transact={'from': a2})
#     assert c.allowance(a2, a1) == 2
#     # Check that approving 0 then amount also works
#     c.approve(a1, 0, transact={'from': a2})
#     assert c.allowance(a2, a1) == 0
#     c.approve(a1, 5, transact={'from': a2})
#     assert c.allowance(a2, a1) == 5
#     # Check that burnFrom to ZERO_ADDRESS failed
#     assert_tx_failed(lambda: c.burnFrom(
#         ZERO_ADDRESS, 0, transact={'from': a1}))
#
#
# def test_raw_logs(c, w3, get_log_args):
#     minter, a1, a2, a3 = w3.eth.accounts[0:4]
#
#     # Check that mint appropriately emits Transfer event
#     args = get_log_args(
#         c.mint(a1, 2, transact={'from': minter}), c, 'Transfer')
#     assert args._from == ZERO_ADDRESS
#     assert args._to == a1
#     assert args._value == 2
#
#     args = get_log_args(
#         c.mint(a1, 0, transact={'from': minter}), c, 'Transfer')
#     assert args._from == ZERO_ADDRESS
#     assert args._to == a1
#     assert args._value == 0
#
#     # Check that burn appropriately emits Transfer event
#     args = get_log_args(c.burn(1, transact={'from': a1}), c, 'Transfer')
#     assert args._from == a1
#     assert args._to == ZERO_ADDRESS
#     assert args._value == 1
#
#     args = get_log_args(c.burn(0, transact={'from': a1}), c, 'Transfer')
#     assert args._from == a1
#     assert args._to == ZERO_ADDRESS
#     assert args._value == 0
#
#     # Check that transfer appropriately emits Transfer event
#     args = get_log_args(c.transfer(
#         a2, 1, transact={'from': a1}), c, 'Transfer')
#     assert args._from == a1
#     assert args._to == a2
#     assert args._value == 1
#
#     args = get_log_args(c.transfer(
#         a2, 0, transact={'from': a1}), c, 'Transfer')
#     assert args._from == a1
#     assert args._to == a2
#     assert args._value == 0
#
#     # Check that approving amount emits events
#     args = get_log_args(c.approve(a1, 1, transact={'from': a2}), c, 'Approval')
#     assert args._owner == a2
#     assert args._spender == a1
#     assert args._value == 1
#
#     args = get_log_args(c.approve(a2, 0, transact={'from': a3}), c, 'Approval')
#     assert args._owner == a3
#     assert args._spender == a2
#     assert args._value == 0
#
#     # Check that transferFrom appropriately emits Transfer event
#     args = get_log_args(c.transferFrom(
#         a2, a3, 1, transact={'from': a1}), c, 'Transfer')
#     assert args._from == a2
#     assert args._to == a3
#     assert args._value == 1
#
#     args = get_log_args(c.transferFrom(
#         a2, a3, 0, transact={'from': a1}), c, 'Transfer')
#     assert args._from == a2
#     assert args._to == a3
#     assert args._value == 0
