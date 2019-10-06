# Vyper version of the Lendroid protocol v2
# THIS CONTRACT HAS NOT BEEN AUDITED!


from contracts.interfaces import ERC20


owner: public(address)
total_supplied: public(uint256)
total_borrowed: public(uint256)
CURRENCY_ADDRESS: public(address)


@private
@constant
def _currency_balance() -> uint256:
    return ERC20(self.CURRENCY_ADDRESS).balanceOf(self)


@public
@constant
def borrowable_amount() -> uint256:
    return self._currency_balance()


@public
def initialize(_currency_address: address) -> bool:
    self.owner = msg.sender
    self.total_supplied = 0
    self.total_borrowed = 0
    self.CURRENCY_ADDRESS = _currency_address

    return True


@public
@constant
def liquidity() -> uint256:
    return as_unitless_number(self.total_supplied) - as_unitless_number(self.total_borrowed)


@public
def destroy() -> bool:
    assert msg.sender == self.owner
    _currency_transfer: bool = ERC20(self.CURRENCY_ADDRESS).transfer(self.owner, self._currency_balance())
    assert _currency_transfer
    selfdestruct(self.owner)


@public
def update_total_supplied(_amount: uint256) -> bool:
    assert msg.sender == self.owner
    self.total_supplied += as_unitless_number(_amount)

    return True


@public
def release_currency(_to: address, _amount: uint256) -> bool:
    assert msg.sender == self.owner
    _currency_transfer: bool = ERC20(self.CURRENCY_ADDRESS).transfer(_to, _amount)
    assert _currency_transfer

    return True
