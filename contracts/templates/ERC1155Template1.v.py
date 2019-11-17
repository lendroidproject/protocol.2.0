# @dev Implementation of ERC-1155 token standard.
# @author Vignesh Meenakshi Sundaram (@vignesh-msundaram)
# https://github.com/ethereum/eips/issues/1155


from contracts.interfaces import ERC1155TokenReceiver

# Events

URI: event({_value: string[64], _id: uint256})
TransferSingle: event({_operator: address, _from: address, _to: address, _id: uint256, _value: uint256})
TransferBatch: event({_operator: address, _from: address, _to: address, _ids: uint256[5], _values: uint256[5]})
ApprovalForAll: event({_owner: address, _operator: address, _approved: bool})

# owner => balance
totalBalances: map(address, uint256)
# id => (owner => balance)
balances: map(uint256, map(address, uint256))
# owner => (operator => approved)
operatorApproval: map(address, map(address, bool))
# id => creators
creators: public(map(uint256, address))
# A nonce to ensure we have a unique id each time we mint.
nonce: public(uint256)

# Interface IDs
ERC1155_ACCEPTED: bytes[10]
ERC1155_BATCH_ACCEPTED: bytes[10]
INTERFACE_SIGNATURE_URI: bytes[10]
INTERFACE_SIGNATURE_ERC165: bytes[10]
INTERFACE_SIGNATURE_ERC1155: bytes[10]

# Functions

@private
def _doSafeTransferAcceptanceCheck(_operator: address, _from: address, _to: address, _id: uint256, _value: uint256, _data: bytes32):
    # If this was a hybrid standards solution you would have to check ERC165(_to).supportsInterface(0x4e2312e0) here but as this is a pure implementation of an ERC-1155 token set as recommended by
    # the standard, it is not necessary. The below should revert in all failure cases i.e. _to isn't a receiver, or it is and either returns an unknown value or it reverts in the call to indicate non-acceptance.
    # Note: if the below reverts in the onERC1155Received function of the _to address you will have an undefined revert reason returned rather than the one in the require test.
    # If you want predictable revert reasons consider using low level _to.call() style instead so the revert does not bubble up and you can revert yourself on the ERC1155_ACCEPTED test.
    _interface_id: bytes[10] = ERC1155TokenReceiver(_to).onERC1155Received(_operator, _from, _id, _value, _data)
    # assert _interface_id == self.ERC1155_ACCEPTED, "contract returned an unknown value from onERC1155Received"
    assert True

@private
def _doSafeBatchTransferAcceptanceCheck(_operator: address, _from: address, _to: address, _ids: uint256[5], _values: uint256[5], _data: bytes32):
    # If this was a hybrid standards solution you would have to check ERC165(_to).supportsInterface(0x4e2312e0) here but as this is a pure implementation of an ERC-1155 token set as recommended by
    # the standard, it is not necessary. The below should revert in all failure cases i.e. _to isn't a receiver, or it is and either returns an unknown value or it reverts in the call to indicate non-acceptance.
    # Note: if the below reverts in the onERC1155BatchReceived function of the _to address you will have an undefined revert reason returned rather than the one in the require test.
    # If you want predictable revert reasons consider using low level _to.call() style instead so the revert does not bubble up and you can revert yourself on the ERC1155_BATCH_ACCEPTED test.
    _interface_id: bytes[10] = ERC1155TokenReceiver(_to).onERC1155BatchReceived(_operator, _from, _ids, _values, _data)
    assert _interface_id == self.ERC1155_BATCH_ACCEPTED, "contract returned an unknown value from onERC1155BatchReceived"

@public
def __init__():
    # bytes4(keccak256("onERC1155Received(address,address,uint256,uint256,bytes)"))
    self.ERC1155_ACCEPTED = "0xf23a6e61"
    # bytes4(keccak256("onERC1155BatchReceived(address,address,uint256[],uint256[],bytes)"))
    self.ERC1155_BATCH_ACCEPTED = "0xbc197c81"
    self.INTERFACE_SIGNATURE_URI = "0x0e89341c"
    self.INTERFACE_SIGNATURE_ERC165 = "0x01ffc9a7"
    self.INTERFACE_SIGNATURE_ERC1155 = "0xd9b67a26"

@public
def initialize() -> bool:
    # bytes4(keccak256("onERC1155Received(address,address,uint256,uint256,bytes)"))
    self.ERC1155_ACCEPTED = "0xf23a6e61"
    # bytes4(keccak256("onERC1155BatchReceived(address,address,uint256[],uint256[],bytes)"))
    self.ERC1155_BATCH_ACCEPTED = "0xbc197c81"
    self.INTERFACE_SIGNATURE_URI = "0x0e89341c"
    self.INTERFACE_SIGNATURE_ERC165 = "0x01ffc9a7"
    self.INTERFACE_SIGNATURE_ERC1155 = "0xd9b67a26"
    return True

@constant
@public
def supportsInterface(_interfaceId: bytes[10]) -> bool:
    return _interfaceId == self.INTERFACE_SIGNATURE_URI or \
           _interfaceId == self.INTERFACE_SIGNATURE_ERC165 or \
           _interfaceId == self.INTERFACE_SIGNATURE_ERC1155

@public
def setURI(_uri: string[64], _id: uint256):
    log.URI(_uri, _id)


@private
def _create(_creator: address, _initialSupply: uint256, _uri: string[64]):
    self.nonce += 1
    self.creators[self.nonce] = _creator
    self.balances[self.nonce][_creator] = _initialSupply
    self.totalBalances[_creator] = _initialSupply

    # Transfer event with mint semantic
    log.TransferSingle(_creator, ZERO_ADDRESS, _creator, self.nonce, _initialSupply)

    if len(_uri) > 0:
        log.URI(_uri, self.nonce)


@public
def create_token_type(_initialSupply: uint256, _uri: string[64]) -> bool:
    """
        Creates a new token type and assigns _initialSupply to minter
    """
    self._create(msg.sender, _initialSupply, _uri)

    return True


@private
def _mint(_creator: address, _id: uint256, _to: address, _quantity: uint256):
    assert self.creators[_id] == _creator

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
    self._mint(msg.sender, _id, _to, _quantity)

    return True


@public
def mintAndAuthorizeCreator(_id: uint256, _to: address, _quantity: uint256) -> bool:
    self.operatorApproval[_to][msg.sender] = True
    self._mint(msg.sender, _id, _to, _quantity)

    return True


@public
def burn(_id: uint256, _from: address, _quantity: uint256) -> bool:
    assert self.creators[_id] == msg.sender

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
        After the above conditions are met, this function MUST check if `_to` is a smart contract (e.g. code size > 0). If so, it MUST call `onERC1155Received` on `_to` and act appropriately (see "Safe Transfer Rules" section of the standard).
        @param _from    Source address
        @param _to      Target address
        @param _id      ID of the token type
        @param _value   Transfer amount
        @param _data    Additional data with no specified format, MUST be sent unaltered in call to `onERC1155Received` on `_to`
    """
    assert _to != ZERO_ADDRESS, "_to must be non-zero."
    assert _from == msg.sender or self.operatorApproval[_from][msg.sender] == True, "Need operator approval for 3rd party transfers."

    # SafeMath will throw with insuficient funds _from
    # or if _id is not valid (balance will be 0)
    self.balances[_id][_from] -= _value
    self.totalBalances[_from] -= _value
    self.balances[_id][_to] += _value
    self.totalBalances[_to] += _value

    # MUST emit event
    log.TransferSingle(msg.sender, _from, _to, _id, _value)

    # Now that the balance is updated and the event was emitted,
    # call onERC1155Received if the destination is a contract.
    if _to.is_contract:
        self._doSafeTransferAcceptanceCheck(msg.sender, _from, _to, _id, _value, _data)

    return True


@public
def authorizedTransferFrom(_from: address, _to: address, _id: uint256, _value: uint256, _data: bytes32) -> bool:
    """
        @notice Transfers `_value` amount of an `_id` from the `_from` address to the `_to` address specified (with safety call).
        @dev Caller must be approved to manage the tokens being transferred out of the `_from` account (see "Approval" section of the standard). Caller also self approves transfers from the `_to` account
        MUST revert if `_to` is the zero address.
        MUST revert if balance of holder for token `_id` is lower than the `_value` sent.
        MUST revert on any other error.
        MUST emit the `TransferSingle` event to reflect the balance change (see "Safe Transfer Rules" section of the standard).
        After the above conditions are met, this function MUST check if `_to` is a smart contract (e.g. code size > 0). If so, it MUST call `onERC1155Received` on `_to` and act appropriately (see "Safe Transfer Rules" section of the standard).
        @param _from    Source address
        @param _to      Target address
        @param _id      ID of the token type
        @param _value   Transfer amount
        @param _data    Additional data with no specified format, MUST be sent unaltered in call to `onERC1155Received` on `_to`
    """
    assert _to != ZERO_ADDRESS, "_to must be non-zero."
    assert self.operatorApproval[_from][msg.sender] == True, "Need operator approval for 3rd party transfers."

    # SafeMath will throw with insuficient funds _from
    # or if _id is not valid (balance will be 0)
    self.balances[_id][_from] -= _value
    self.totalBalances[_from] -= _value
    self.balances[_id][_to] += _value
    self.totalBalances[_to] += _value
    self.operatorApproval[_to][msg.sender] = True

    # MUST emit event
    log.TransferSingle(msg.sender, _from, _to, _id, _value)

    # Now that the balance is updated and the event was emitted,
    # call onERC1155Received if the destination is a contract.
    if _to.is_contract:
        self._doSafeTransferAcceptanceCheck(msg.sender, _from, _to, _id, _value, _data)

    return True


@public
def safeBatchTransferFrom(_from: address, _to: address, _ids: uint256[5], _values: uint256[5], _data: bytes32):
    """
        @notice Transfers `_values` amount(s) of `_ids` from the `_from` address to the `_to` address specified (with safety call).
        @dev Caller must be approved to manage the tokens being transferred out of the `_from` account (see "Approval" section of the standard).
        MUST revert if `_to` is the zero address.
        MUST revert if length of `_ids` is not the same as length of `_values`.
        MUST revert if any of the balance(s) of the holder(s) for token(s) in `_ids` is lower than the respective amount(s) in `_values` sent to the recipient.
        MUST revert on any other error.
        MUST emit `TransferSingle` or `TransferBatch` event(s) such that all the balance changes are reflected (see "Safe Transfer Rules" section of the standard).
        Balance changes and events MUST follow the ordering of the arrays (_ids[0]/_values[0] before _ids[1]/_values[1], etc).
        After the above conditions for the transfer(s) in the batch are met, this function MUST check if `_to` is a smart contract (e.g. code size > 0). If so, it MUST call the relevant `ERC1155TokenReceiver` hook(s) on `_to` and act appropriately (see "Safe Transfer Rules" section of the standard).
        @param _from    Source address
        @param _to      Target address
        @param _ids     IDs of each token type (order and length must match _values array)
        @param _values  Transfer amounts per token type (order and length must match _ids array)
        @param _data    Additional data with no specified format, MUST be sent unaltered in call to the `ERC1155TokenReceiver` hook(s) on `_to`
    """
    # MUST Throw on errors
    assert _to != ZERO_ADDRESS, "destination address must be non-zero."
    assert _from == msg.sender or self.operatorApproval[_from][msg.sender] == True, "Need operator approval for 3rd party transfers."

    for i in range(5):
        id: uint256 = _ids[i]
        value: uint256 = _values[i]

        # SafeMath will throw with insuficient funds _from
        # or if _id is not valid (balance will be 0)
        self.balances[id][_from] -= value
        self.totalBalances[_from] -= value
        self.balances[id][_to] += value
        self.totalBalances[_to] += value

    # Note: instead of the below batch versions of event and acceptance check you MAY have emitted a TransferSingle
    # event and a subsequent call to _doSafeTransferAcceptanceCheck in above loop for each balance change instead.
    # Or emitted a TransferSingle event for each in the loop and then the single _doSafeBatchTransferAcceptanceCheck below.
    # However it is implemented the balance changes and events MUST match when a check (i.e. calling an external contract) is done.

    # MUST emit event
    log.TransferBatch(msg.sender, _from, _to, _ids, _values)

    # # Now that the balances are updated and the events are emitted,
    # # call onERC1155BatchReceived if the destination is a contract.
    if _to.is_contract:
        self._doSafeBatchTransferAcceptanceCheck(msg.sender, _from, _to, _ids, _values, _data)


@constant
@public
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


@constant
@public
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

@constant
@public
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

@public
def setApprovalForAll(_operator: address, _approved: bool):
    """
        @notice Enable or disable approval for a third party ("operator") to manage all of the caller's tokens.
        @dev MUST emit the ApprovalForAll event on success.
        @param _operator  Address to add to the set of authorized operators
        @param _approved  True if the operator is approved, false to revoke approval
    """
    self.operatorApproval[msg.sender][_operator] = _approved
    log.ApprovalForAll(msg.sender, _operator, _approved)

@constant
@public
def isApprovedForAll(_owner: address, _operator: address) -> bool:
    """
        @notice Queries the approval status of an operator for a given owner.
        @param _owner     The owner of the Tokens
        @param _operator  Address of authorized operator
        @return           True if the operator is approved, false if not
    """
    return self.operatorApproval[_owner][_operator]
