# Vyper version of the Lendroid protocol v2
# THIS CONTRACT HAS NOT BEEN AUDITED!


from contracts.interfaces import ERC20


owner: public(address)
token: public(address)


@private
@constant
def _balance() -> uint256:
    return ERC20(self.token).balanceOf(self)


@public
@constant
def borrowable_amount() -> uint256:
    return self._balance()


@public
def initialize(_token: address) -> bool:
    self.owner = msg.sender
    self.token = _token

    return True


@public
def release(_to: address, _value: uint256) -> bool:
    assert msg.sender == self.owner
    assert_modifiable(ERC20(self.token).transfer(_to, _value))

    return True


@public
def destroy() -> bool:
    assert msg.sender == self.owner
    assert_modifiable(ERC20(self.token).transfer(self.owner, self._balance()))
    selfdestruct(self.owner)
