# Events

URI: event({_value: string[64], _id: uint256})
TransferSingle: event({_operator: address, _from: address, _to: address, _id: uint256, _value: uint256})

# Functions

@public
def initialize(_protocol_dao: address, _authorized_daos: address[5]) -> bool:
    pass

@constant
@public
def supportsInterface(_interfaceId: bytes[10]) -> bool:
    pass

@constant
@public
def id(_currency: address, _expiry: uint256(sec, positional), _underlying: address, _strike_price: uint256) -> uint256:
    pass

@constant
@public
def is_valid_id(_id: uint256) -> bool:
    pass

@public
def setURI(_uri: string[64], _id: uint256):
    pass

@public
def get_or_create_id(_currency: address, _expiry: uint256(sec, positional), _underlying: address, _strike_price: uint256, _uri: string[64]) -> uint256:
    pass

@public
def mint(_id: uint256, _to: address, _quantity: uint256) -> bool:
    pass

@public
def burn(_id: uint256, _from: address, _quantity: uint256) -> bool:
    pass

@public
def safeTransferFrom(_from: address, _to: address, _id: uint256, _value: uint256, _data: bytes32) -> bool:
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

@constant
@public
def protocol_dao() -> address:
    pass

@constant
@public
def authorized_daos(arg0: address) -> bool:
    pass

@constant
@public
def hash_to_id(arg0: bytes32) -> uint256:
    pass

@constant
@public
def id_to_hash(arg0: uint256) -> bytes32:
    pass

@constant
@public
def metadata__address_(arg0: uint256) -> address:
    pass

@constant
@public
def metadata__currency(arg0: uint256) -> address:
    pass

@constant
@public
def metadata__expiry(arg0: uint256) -> uint256(sec, positional):
    pass

@constant
@public
def metadata__underlying(arg0: uint256) -> address:
    pass

@constant
@public
def metadata__strike_price(arg0: uint256) -> uint256:
    pass

@constant
@public
def metadata__uri(arg0: uint256) -> string[64]:
    pass

@constant
@public
def metadata__id(arg0: uint256) -> uint256:
    pass

@constant
@public
def metadata__hash(arg0: uint256) -> bytes32:
    pass

@constant
@public
def creators(arg0: uint256) -> address:
    pass

@constant
@public
def nonce() -> uint256:
    pass

@constant
@public
def initialized() -> bool:
    pass
