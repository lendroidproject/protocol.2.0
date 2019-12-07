# Vyper version of the Lendroid protocol v2
# THIS CONTRACT HAS NOT BEEN AUDITED!


shouldReject: public(bool)
lastData: public(bytes32)
lastOperator: public(address)
lastFrom: public(address)
lastId: public(uint256)
lastValue: public(uint256)

MFT_ACCEPTED: bytes[10]


@public
def __init__():
    self.MFT_ACCEPTED = "0xf23a6e61"# bytes4(keccak256("onMFTReceived(address,address,uint256,uint256,bytes)"))


@public
def setShouldReject(_value: bool):
    self.shouldReject = _value


# ERC165 interface support
@public
@constant
def supportsInterface(interfaceID: bytes[10]) -> bool:
    # ERC165 or MFT_ACCEPTED
    return interfaceID == "0x01ffc9a7" or interfaceID == "0xf23a6e61"


@public
def onMFTReceived(_operator: address, _from: address, _id: uint256, _value: uint256, _data: bytes32) -> bytes[10]:
    self.lastOperator = _operator
    self.lastFrom = _from
    self.lastId = _id
    self.lastValue = _value
    self.lastData = _data
    if self.shouldReject:
        raise("onMFTReceived: transfer not accepted")
    else:
        return self.MFT_ACCEPTED
