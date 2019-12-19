# @dev Implementation of Multi Fungible Token.
# @author Vignesh Meenakshi Sundaram (@vignesh-msundaram)


from contracts.interfaces import MultiFungibleTokenReceiver

# Structs
struct Metadata:
    address_: address
    currency: address
    expiry: timestamp
    underlying: address
    strike_price: uint256
    uri: string[64]
    id: uint256
    hash: bytes32

# Events

URI: event({_value: string[64], _id: uint256})
TransferSingle: event({_operator: address, _from: address, _to: address, _id: uint256, _value: uint256})
protocol_dao: public(address)
# dao_address => bool
authorized_daos: public(map(address, bool))
# _hash => id
hash_to_id: public(map(bytes32, uint256))
# id => _hash
id_to_hash: public(map(uint256, bytes32))
# id => Metadata
metadata: public(map(uint256, Metadata))
# owner => balance
totalBalances: map(address, uint256)
# id => (owner => balance)
balances: map(uint256, map(address, uint256))
# id => creators
creators: public(map(uint256, address))
# A nonce to ensure we have a unique id each time we mint.
nonce: public(uint256)

# Interface IDs
MFT_ACCEPTED: bytes[10]
MFT_BATCH_ACCEPTED: bytes[10]
INTERFACE_SIGNATURE_URI: bytes[10]
INTERFACE_SIGNATURE_ERC165: bytes[10]
INTERFACE_SIGNATURE_MFT: bytes[10]

initialized: public(bool)

# Functions


@public
def initialize(_protocol_dao: address, _authorized_daos: address[5]) -> bool:
    assert not self.initialized
    self.initialized = True
    self.protocol_dao = _protocol_dao
    # bytes4(keccak256("onMFTReceived(address,address,uint256,uint256,bytes)"))
    self.MFT_ACCEPTED = "0xf23a6e61"
    # bytes4(keccak256("onMFTBatchReceived(address,address,uint256[],uint256[],bytes)"))
    self.MFT_BATCH_ACCEPTED = "0xbc197c81"
    self.INTERFACE_SIGNATURE_URI = "0x0e89341c"
    self.INTERFACE_SIGNATURE_ERC165 = "0x01ffc9a7"
    self.INTERFACE_SIGNATURE_MFT = "0xd9b67a26"
    for _dao in _authorized_daos:
        self.authorized_daos[_dao] = True

    return True


@private
@constant
def _hash(_currency: address, _expiry: timestamp, _underlying: address, _strike_price: uint256) -> bytes32:
    return keccak256(
        concat(
            convert(self.protocol_dao, bytes32),
            convert(self, bytes32),
            convert(_currency, bytes32),
            convert(_expiry, bytes32),
            convert(_underlying, bytes32),
            convert(_strike_price, bytes32)
        )
    )


@private
def _doSafeTransferAcceptanceCheck(_operator: address, _from: address, _to: address, _id: uint256, _value: uint256, _data: bytes32):
    # If this was a hybrid standards solution you would have to check ERC165(_to).supportsInterface(0x4e2312e0) here but as this is a pure implementation of an ERC-1155 token set as recommended by
    # the standard, it is not necessary. The below should revert in all failure cases i.e. _to isn't a receiver, or it is and either returns an unknown value or it reverts in the call to indicate non-acceptance.
    # Note: if the below reverts in the onMFTReceived function of the _to address you will have an undefined revert reason returned rather than the one in the require test.
    # If you want predictable revert reasons consider using low level _to.call() style instead so the revert does not bubble up and you can revert yourself on the MFT_ACCEPTED test.
    _interface_id: bytes[10] = MultiFungibleTokenReceiver(_to).onMFTReceived(_operator, _from, _id, _value, _data)
    # assert _interface_id == self.MFT_ACCEPTED, "contract returned an unknown value from onMFTReceived"
    assert True


@private
@constant
def hash(_currency: address, _expiry: timestamp, _underlying: address, _strike_price: uint256) -> bytes32:
    return self._hash(_currency, _expiry, _underlying, _strike_price)


@public
@constant
def supportsInterface(_interfaceId: bytes[10]) -> bool:
    return _interfaceId == self.INTERFACE_SIGNATURE_URI or \
           _interfaceId == self.INTERFACE_SIGNATURE_ERC165 or \
           _interfaceId == self.INTERFACE_SIGNATURE_MFT


@public
@constant
def id(_currency: address, _expiry: timestamp, _underlying: address, _strike_price: uint256) -> uint256:
    return self.hash_to_id[self._hash(_currency, _expiry, _underlying, _strike_price)]


@public
@constant
def is_valid_id(_id: uint256) -> bool:
    return self.hash_to_id[self.id_to_hash[_id]] == _id


@public
def setURI(_uri: string[64], _id: uint256):
    log.URI(_uri, _id)


@private
def _create(
    _creator: address, _currency: address, _expiry: timestamp,
    _underlying: address, _strike_price: uint256, _uri: string[64]
    ):
    self.nonce += 1
    self.creators[self.nonce] = _creator
    self.balances[self.nonce][_creator] = 0
    self.totalBalances[_creator] = 0
    _hash: bytes32 = self._hash(_currency, _expiry, _underlying, _strike_price)
    self.hash_to_id[_hash] = self.nonce
    self.id_to_hash[self.nonce] = _hash
    self.metadata[self.nonce] = Metadata({
        address_: self,
        currency: _currency,
        expiry: _expiry,
        underlying: _underlying,
        strike_price: _strike_price,
        uri: _uri,
        id: self.nonce,
        hash: _hash
    })

    # Transfer event with mint semantic
    log.TransferSingle(_creator, ZERO_ADDRESS, _creator, self.nonce, 0)

    if len(_uri) > 0:
        log.URI(_uri, self.nonce)


@public
def get_or_create_id(_currency: address, _expiry: timestamp,
    _underlying: address, _strike_price: uint256, _uri: string[64]
    ) -> uint256:
    """
        Creates a new token type and assigns _initialSupply to minter
    """
    assert self.initialized
    assert self.authorized_daos[msg.sender]
    _hash: bytes32 = self._hash(_currency, _expiry, _underlying, _strike_price)
    if self.hash_to_id[_hash] == 0:
        self._create(msg.sender, _currency, _expiry, _underlying, _strike_price,
         _uri)

    return self.hash_to_id[_hash]


@private
def _mint(_creator: address, _id: uint256, _to: address, _quantity: uint256):
    # Grant the items to the caller
    self.balances[_id][_to] += _quantity
    self.totalBalances[_to] += _quantity

    # Emit the Transfer/Mint event.
    # the 0x0 source address implies a mint
    # It will also provide the circulating supply info.
    log.TransferSingle(_creator, ZERO_ADDRESS, _to, _id, _quantity)

    if _to.is_contract:
        self._doSafeTransferAcceptanceCheck(_creator, _creator, _to, _id, _quantity, EMPTY_BYTES32)


@public
def mint(_id: uint256, _to: address, _quantity: uint256) -> bool:
    assert self.initialized
    assert self.authorized_daos[msg.sender]
    self._mint(msg.sender, _id, _to, _quantity)

    return True


@public
def burn(_id: uint256, _from: address, _quantity: uint256) -> bool:
    assert self.initialized
    assert self.authorized_daos[msg.sender]

    # Remove the items to the caller
    self.balances[_id][_from] -= _quantity
    self.totalBalances[_from] -= _quantity

    # Emit the Transfer/Mint event.
    # the 0x0 source address implies a mint
    # It will also provide the circulating supply info.
    log.TransferSingle(msg.sender, _from, ZERO_ADDRESS, _id, _quantity)

    return True

@public
def safeTransferFrom(_from: address, _to: address, _id: uint256, _value: uint256, _data: bytes32) -> bool:
    """
        @notice Transfers `_value` amount of an `_id` from the `_from` address to the `_to` address specified (with safety call).
        @dev Caller must be approved to manage the tokens being transferred out of the `_from` account (see "Approval" section of the standard).
        MUST revert if `_to` is the zero address.
        MUST revert if balance of holder for token `_id` is lower than the `_value` sent.
        MUST revert on any other error.
        MUST emit the `TransferSingle` event to reflect the balance change (see "Safe Transfer Rules" section of the standard).
        After the above conditions are met, this function MUST check if `_to` is a smart contract (e.g. code size > 0). If so, it MUST call `onMFTReceived` on `_to` and act appropriately (see "Safe Transfer Rules" section of the standard).
        @param _from    Source address
        @param _to      Target address
        @param _id      ID of the token type
        @param _value   Transfer amount
        @param _data    Additional data with no specified format, MUST be sent unaltered in call to `onMFTReceived` on `_to`
    """
    assert self.initialized
    assert _to != ZERO_ADDRESS, "_to must be non-zero."
    assert (_from == msg.sender) or self.authorized_daos[msg.sender], "Need operator approval for 3rd party transfers."

    # SafeMath will throw with insuficient funds _from
    # or if _id is not valid (balance will be 0)
    self.balances[_id][_from] -= _value
    self.totalBalances[_from] -= _value
    self.balances[_id][_to] += _value
    self.totalBalances[_to] += _value

    # MUST emit event
    log.TransferSingle(msg.sender, _from, _to, _id, _value)

    # Now that the balance is updated and the event was emitted,
    # call onMFTReceived if the destination is a contract.
    if _to.is_contract:
        self._doSafeTransferAcceptanceCheck(msg.sender, _from, _to, _id, _value, _data)

    return True


@public
@constant
def totalBalanceOf(_owner: address) -> uint256:
    """
        @notice Get the total balance of an account's Tokens.
        @param _owner  The address of the token holder
        @return        The _owner's total balance of all Token types
    """
    # The balance of any account can be calculated from the Transfer events history.
    # However, since we need to keep the balances to validate transfer request,
    # there is no extra cost to also privide a querry function.
    return self.totalBalances[_owner]


@public
@constant
def balanceOf(_owner: address, _id: uint256) -> uint256:
    """
        @notice Get the balance of an account's Tokens.
        @param _owner  The address of the token holder
        @param _id     ID of the Token
        @return        The _owner's balance of the Token type requested
    """
    # The balance of any account can be calculated from the Transfer events history.
    # However, since we need to keep the balances to validate transfer request,
    # there is no extra cost to also privide a querry function.
    return self.balances[_id][_owner]


@public
@constant
def balanceOfBatch(_owner: address, _ids: uint256[5]) -> uint256[5]:
    """
        @notice Get the balance of multiple account/token pairs
        @param _owners The addresses of the token holders
        @param _ids    ID of the Tokens
        @return        The _owner's balance of the Token types requested (i.e. balance for each (owner, id) pair)
    """

    return [
        self.balances[_ids[0]][_owner],
        self.balances[_ids[1]][_owner],
        self.balances[_ids[2]][_owner],
        self.balances[_ids[3]][_owner],
        self.balances[_ids[4]][_owner]
    ]
