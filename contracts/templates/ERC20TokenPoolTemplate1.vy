# @version 0.1.0b16
# @notice Implementation of Lendroid v2 - ERC20 Token Pool. This Template will be provided by the Lendroid Team.
# @dev THIS CONTRACT IS CURRENTLY UNDER AUDIT
# @author Vignesh (Vii) Meenakshi Sundaram (@vignesh-msundaram)
# Lendroid Foundation


from ...interfaces import ERC20Interface


owner: public(address)
token: public(address)

initialized: public(bool)


@public
def initialize(_token: address) -> bool:
    # validate inputs
    assert msg.sender.is_contract
    assert _token.is_contract
    assert not self.initialized
    self.initialized = True
    self.owner = msg.sender
    self.token = _token

    return True


@public
@constant
def borrowable_amount() -> uint256:
    return ERC20Interface(self.token).balanceOf(self)


@public
def release(_to: address, _value: uint256) -> bool:
    assert self.initialized
    assert msg.sender == self.owner
    # verify _value is not 0
    assert as_unitless_number(_value) > 0
    assert_modifiable(ERC20Interface(self.token).transfer(_to, _value))

    return True


@public
def destroy() -> bool:
    assert self.initialized
    assert msg.sender == self.owner
    assert_modifiable(ERC20Interface(self.token).transfer(
        self.owner,
        ERC20Interface(self.token).balanceOf(self)
    ))
    selfdestruct(self.owner)
