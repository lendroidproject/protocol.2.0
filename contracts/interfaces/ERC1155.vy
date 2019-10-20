# Events

URI: event({_value: string[64], _id: uint256})
TransferSingle: event({_operator: address, _from: address, _to: address, _id: uint256, _value: uint256})
TransferBatch: event({_operator: address, _from: address, _to: address, _ids: uint256[5], _values: uint256[5]})
ApprovalForAll: event({_owner: address, _operator: address, _approved: bool})

# Functions

@public
def initialize() -> bool:
    pass

@constant
@public
def supportsInterface(_interfaceId: bytes[10]) -> bool:
    pass

@public
def setURI(_uri: string[64], _id: uint256):
    pass

@public
def create_token_type(_initialSupply: uint256, _uri: string[64]) -> uint256:
    pass

@public
def mint(_id: uint256, _to: address, _quantity: uint256) -> bool:
    pass

@public
def mintAndAuthorizeCreator(_id: uint256, _to: address, _quantity: uint256) -> bool:
    pass

@public
def burn(_id: uint256, _from: address, _quantity: uint256) -> bool:
    pass

@public
def safeTransferFrom(_from: address, _to: address, _id: uint256, _value: uint256, _data: bytes32) -> bool:
    pass

@public
def authorizedTransferFrom(_from: address, _to: address, _id: uint256, _value: uint256, _data: bytes32) -> bool:
    pass

@public
def safeBatchTransferFrom(_from: address, _to: address, _ids: uint256[5], _values: uint256[5], _data: bytes32):
    pass

@constant
@public
def totalBalanceOf(_owner: address) -> uint256:
    pass

@constant
@public
def balanceOf(_owner: address, _id: uint256) -> uint256:
    pass

@constant
@public
def balanceOfBatch(_owner: address, _ids: uint256[5]) -> uint256[5]:
    pass

@public
def setApprovalForAll(_operator: address, _approved: bool):
    pass

@constant
@public
def isApprovedForAll(_owner: address, _operator: address) -> bool:
    pass

@constant
@public
def creators(arg0: uint256) -> address:
    pass

@constant
@public
def nonce() -> uint256:
    pass
