# @version 0.1.0b14
# @notice Implementation of Multi Fungible Token
# @dev THIS CONTRACT HAS NOT BEEN AUDITED
# @author Vignesh (Vii) Meenakshi Sundaram (@vignesh-msundaram)
# Lendroid Foundation


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
INTERFACE_SIGNATURE_ERC165: bytes[10]
INTERFACE_SIGNATURE_MFT: bytes[10]

initialized: public(bool)

# Functions


@public
def initialize(_protocol_dao: address, _authorized_daos: address[5]) -> bool:
    # validate inputs
    assert _protocol_dao.is_contract
    assert not self.initialized
    self.initialized = True
    self.protocol_dao = _protocol_dao
    # bytes4(keccak256("supportsInterface(bytes[10])"))
    self.INTERFACE_SIGNATURE_ERC165 = "0xa69f31f6"
    # bytes4(keccak256("initialize(address,address[5])")) ^
    # bytes4(keccak256("_hash(address,timestamp,address,uint256)")) ^
    # bytes4(keccak256("get_or_create_id(address,timestamp,address,uint256,string[64])")) ^
    # bytes4(keccak256("supportsInterface(bytes[10])")) ^
    # bytes4(keccak256("id(address,timestamp,address,uint256)")) ^
    # bytes4(keccak256("is_valid_id(uint256)")) ^
    # bytes4(keccak256("setURI(string[64],uint256)")) ^
    # bytes4(keccak256("mint(uint256,address,uint256)")) ^
    # bytes4(keccak256("burn(uint256,address,uint256)")) ^
    # bytes4(keccak256("safeTransferFrom(address,address,uint256,uint256,bytes32)")) ^
    # bytes4(keccak256("balanceOf(address,uint256)")) ^
    # bytes4(keccak256("burn(uint256,address,uint256)")) ^
    # bytes4(keccak256("balanceOfBatch(address,uint256[5])"));
    self.INTERFACE_SIGNATURE_MFT = "0xd9b67a26"
    self.authorized_daos[_protocol_dao] = True
    for _dao in _authorized_daos:
        assert _dao.is_contract
        self.authorized_daos[_dao] = True

    return True


@private
@constant
def _hash(_currency: address, _expiry: timestamp, _underlying: address, _strike_price: uint256) -> bytes32:
    """
        @dev Function to get the _hash of a MFT, given its indicators.
             This is an internal function and is used only within the context of
             this contract.
        @param _currency The address of the currency token in the MFT.
        @param _expiry The timestamp when the MFT expires.
        @param _underlying The address of the underlying token in the MFT.
        @param _strike_price The price of the underlying per currency at _expiry.
        @return A unique bytes32 representing the MFT with the given indicators.
    """
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


@public
@constant
def supportsInterface(_interfaceId: bytes[10]) -> bool:
    """
        @dev Function to check if the given interface ID is supported.
        @param _interfaceId The interface ID.
        @return Bool indicating the support.
    """
    return _interfaceId == self.INTERFACE_SIGNATURE_ERC165 or \
           _interfaceId == self.INTERFACE_SIGNATURE_MFT


@public
@constant
def id(_currency: address, _expiry: timestamp, _underlying: address, _strike_price: uint256) -> uint256:
    """
        @dev Function to get the id of a MFT, given its indicators.
        @param _currency The address of the currency token in the MFT.
        @param _expiry The timestamp when the MFT expires.
        @param _underlying The address of the underlying token in the MFT.
        @param _strike_price The price of the underlying per currency at _expiry.
        @return Non-zero Id of the MFT _hash if the MFT has been created. Zero otherwise.
    """
    return self.hash_to_id[self._hash(_currency, _expiry, _underlying, _strike_price)]


@public
@constant
def is_valid_id(_id: uint256) -> bool:
    """
        @dev Function to check if a given MFT _hash is valid.
        @param _id The MFT id.
        @return Bool indicating if the id is registered to a _hash.
    """
    return self.hash_to_id[self.id_to_hash[_id]] == _id


@public
def setURI(_uri: string[64], _id: uint256) -> bool:
    """
        @dev Function to add a URI to a MFT metadata
        @param _id The MFT id.
        @return Bool indicating if the id is registered to a _hash.
    """
    assert self.authorized_daos[msg.sender]
    self.metadata[_id].uri = _uri
    log.URI(_uri, _id)

    return True


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
    """
      The _creator here might look redundant, however, since it can represent any of the authorized DAOs,
      it is useful to understand which DAO minted the MFT.
    """
    # Grant the items to the caller
    self.balances[_id][_to] += _quantity
    self.totalBalances[_to] += _quantity

    # Emit the Transfer/Mint event.
    # the 0x0 source address implies a mint
    # It will also provide the circulating supply info.
    log.TransferSingle(_creator, ZERO_ADDRESS, _to, _id, _quantity)


@public
def mint(_id: uint256, _to: address, _quantity: uint256) -> bool:
    assert self.initialized
    assert self.authorized_daos[msg.sender]
    assert self.hash_to_id[self.id_to_hash[_id]] == _id
    self._mint(msg.sender, _id, _to, _quantity)

    return True


@public
def burn(_id: uint256, _from: address, _quantity: uint256) -> bool:
    assert self.initialized
    assert (_from == msg.sender) or self.authorized_daos[msg.sender], "Need dao approval for 3rd party burns."

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
        @param _from    Source address
        @param _to      Target address
        @param _id      ID of the token type
        @param _value   Transfer amount
        @param _data    Additional data with no specified format, MUST be sent unaltered in call to `onMFTReceived` on `_to`
    """
    assert self.initialized
    assert _to != ZERO_ADDRESS, "_to must be non-zero."
    assert (_from == msg.sender) or self.authorized_daos[msg.sender], "Need dao approval for 3rd party transfers."

    # Vyper will revert automatically for negative balance
    # if _id is not valid (balance will be 0)
    self.balances[_id][_from] -= _value
    self.totalBalances[_from] -= _value
    self.balances[_id][_to] += _value
    self.totalBalances[_to] += _value

    # MUST emit event
    log.TransferSingle(msg.sender, _from, _to, _id, _value)

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
        @return        The _owner's balance of the Token id requested
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
