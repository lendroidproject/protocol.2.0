# Vyper version of the Lendroid protocol v2
# THIS CONTRACT IS NOT AUDITED!


# Interface for the ERC20 contract, used mainly for `transfer` and `transferFrom` functions
contract ERC20:
    def name() -> string[64]: constant
    def symbol() -> string[32]: constant
    def decimals() -> uint256: constant
    def balanceOf(_owner: address) -> uint256: constant
    def totalSupply() -> uint256: constant
    def transfer(_to: address, _amount: uint256) -> bool: modifying
    def transferFrom(_from: address, _to: address, _value: uint256) -> bool: modifying
    def approve(_spender: address, _amount: uint256) -> bool: modifying
    def allowance(_owner: address, _spender: address) -> uint256: constant

# Events of the position
PositionUpdateNotification: event({_wrangler: indexed(address), _position_address: indexed(address), _notification_key: string[64], _notification_value: uint256})
# contract terms
index: public(uint256)
kernel_creator: public(address)
lender: public(address)
borrower: public(address)
relayer: public(address)
wrangler: public(address)
created_at: public(timestamp)
updated_at: public(timestamp)
expires_at: public(timestamp)
borrow_currency_address: public(address)
lend_currency_address: public(address)
borrow_currency_value: public(uint256)
borrow_currency_current_value: public(uint256)
lend_currency_filled_value: public(uint256)
lend_currency_owed_value: public(uint256)
status: public(uint256)
nonce: public(uint256)
relayer_fee: public(uint256)
monitoring_fee: public(uint256)
rollover_fee: public(uint256)
closure_fee: public(uint256)
hash: public(bytes32)
# Variables of the protocol.
protocol_address: public(address)
# constants
SECONDS_PER_DAY: public(uint256)
POSITION_STATUS_OPEN: public(uint256)
POSITION_STATUS_CLOSED: public(uint256)
POSITION_STATUS_LIQUIDATED: public(uint256)
POSITION_STATUS_ROLLED_OVER: public(uint256)
COLLATERAL_TOPPED_UP: public(uint256)
COLLATERAL_WITHDRAWN: public(uint256)


# constant functions
@public
@constant
def ecrecover_from_signature(_hash: bytes32, _sig: bytes[65]) -> address:
    """
    @info Inspired from https://github.com/LayerXcom/verified-vyper-contracts/blob/master/contracts/ecdsa/ECDSA.vy
    @dev Recover signer address from a message by using their signature
    @param _hash bytes32 message, the hash is the signed message. What is recovered is the signer address.
    @param _sig bytes signature, the signature is generated using web3.eth.sign()
    """
    if len(_sig) != 65:
        return ZERO_ADDRESS
    v: int128 = convert(slice(_sig, start=64, len=1), int128)
    if v < 27:
        v += 27
    if v in [27, 28]:
        return ecrecover(_hash, convert(v, uint256), extract32(_sig, 0, type=uint256), extract32(_sig, 32, type=uint256))
    return ZERO_ADDRESS


@public
@constant
def is_signer(_prover: address, _hash: bytes32, _sig: bytes[65]) -> bool:
    if _prover == self.ecrecover_from_signature(_hash, _sig):
        return True
    else:
        sign_prefix: bytes[32] = "\x19Ethereum Signed Message:\n32"
        return _prover == self.ecrecover_from_signature(sha3(concat(sign_prefix, _hash)), _sig)


@public
@constant
def position() -> (uint256, address, address, address, address, address, timestamp, timestamp, timestamp, address, address, uint256, uint256,
    uint256, uint256, uint256, uint256, uint256, uint256, uint256, uint256, bytes32):
    return (self.index, self.kernel_creator, self.lender, self.borrower, self.relayer, self.wrangler, self.created_at, self.updated_at, self.expires_at, self.borrow_currency_address, self.lend_currency_address, self.borrow_currency_value, self.borrow_currency_current_value, self.lend_currency_filled_value, self.lend_currency_owed_value, self.status, self.nonce, self.relayer_fee, self.monitoring_fee, self.rollover_fee, self.closure_fee, self.hash)


@public
@constant
def position_hash(
            _addresses: address[7],
            # _addresses: kernel_creator, lender, borrower, relayer, wrangler, collateralToken, loanToken
            _values: uint256[7],
            # _values: collateralAmount, loanAmountOffered, relayerFeeLST, monitoringFeeLST, rolloverFeeLST, closureFeeLST, loanAmountFilled
            _lend_currency_owed_value: uint256, _nonce: uint256
        ) -> bytes32:
    return sha3(
        concat(
            convert(self.protocol_address, bytes32),
            convert(_addresses[5], bytes32),# collateralToken
            convert(_addresses[6], bytes32),# loanToken
            convert(_values[0], bytes32),# collateralAmount
            convert(_values[6], bytes32),# loanAmountFilled
            convert(_lend_currency_owed_value, bytes32),# loanAmountOwed
            convert(_addresses[0], bytes32),# kernel_creator
            convert(_addresses[1], bytes32),# lender
            convert(_addresses[2], bytes32),# borrower
            convert(_addresses[3], bytes32),# relayer
            convert(_addresses[4], bytes32),# wrangler
            convert(_values[2], bytes32),# relayerFeeLST
            convert(_values[3], bytes32),# monitoringFeeLST
            convert(_values[4], bytes32),# rolloverFeeLST
            convert(_values[5], bytes32),# closureFeeLST
            convert(_nonce, bytes32)# nonce
        )
    )


@public
@constant
def owed_value(
        _filled_value: uint256,
        _kernel_daily_interest_rate: uint256,
        _position_duration_in_seconds: timedelta
    ) -> uint256:
    # calculate owed value
    _position_duration_in_days: uint256 = as_unitless_number(_position_duration_in_seconds) / as_unitless_number(self.SECONDS_PER_DAY)
    _total_interest: uint256 = as_unitless_number(_filled_value) * as_unitless_number(_position_duration_in_days) * as_unitless_number(_kernel_daily_interest_rate) / 10 ** 20
    return as_unitless_number(_filled_value) + as_unitless_number(_total_interest)


# escape hatch functions
@public
def escape_hatch_token(_recipient: address, _token_address: address) -> bool:
    assert msg.sender == self.protocol_address
    # transfer token from this address to owner (message sender)
    token_transfer: bool = ERC20(_token_address).transfer(
        _recipient,
        ERC20(_token_address).balanceOf(self)
    )
    assert token_transfer
    return True


@public
def initialize(
        _index: uint256,
        _kernel_creator: address,
        _addresses: address[6],
        # _addresses: lender, borrower, relayer, wrangler, collateralToken, loanToken
        _values: uint256[7],
        # _values: collateralAmount, loanAmountOffered, relayerFeeLST, monitoringFeeLST, rolloverFeeLST, closureFeeLST, loanAmountFilled (aka, loanAmountBorrowed)
        _nonce: uint256,
        _kernel_daily_interest_rate: uint256,
        _position_duration_in_seconds: timedelta,
        _approval_expires: timestamp,
        _sig_data: bytes[65]
        # v, r, s of wrangler
    ) -> bool:
    assert self.protocol_address == ZERO_ADDRESS, "Contract has already been initialized"
    self.protocol_address = msg.sender
    # set constants
    self.SECONDS_PER_DAY = 86400
    self.POSITION_STATUS_OPEN = 1
    self.POSITION_STATUS_CLOSED = 2
    self.POSITION_STATUS_LIQUIDATED = 3
    self.POSITION_STATUS_ROLLED_OVER = 4
    self.COLLATERAL_TOPPED_UP = 1
    self.COLLATERAL_WITHDRAWN = 2
    # calculate owed value
    _lend_currency_owed_value: uint256 = self.owed_value(_values[6], _kernel_daily_interest_rate, _position_duration_in_seconds)
    # create position from struct
    self.index = _index
    self.kernel_creator = _kernel_creator
    self.lender = _addresses[0]
    self.borrower = _addresses[1]
    self.relayer = _addresses[2]
    self.wrangler = _addresses[3]
    self.created_at = block.timestamp
    self.updated_at = block.timestamp
    self.expires_at = block.timestamp + _position_duration_in_seconds
    self.borrow_currency_address = _addresses[4]
    self.lend_currency_address = _addresses[5]
    self.borrow_currency_value = _values[0]
    self.borrow_currency_current_value = _values[0]
    self.lend_currency_filled_value = _values[6]
    self.lend_currency_owed_value = _lend_currency_owed_value
    self.status = self.POSITION_STATUS_OPEN
    self.nonce = _nonce
    self.relayer_fee = _values[2]
    self.monitoring_fee = _values[3]
    self.rollover_fee = _values[4]
    self.closure_fee = _values[5]
    self.hash = self.position_hash([_kernel_creator, _addresses[0], _addresses[1],
        _addresses[2], _addresses[3], _addresses[4], _addresses[5]],
        _values, _lend_currency_owed_value, _nonce
    )
    # validate wrangler's signature
    assert self.is_signer(self.wrangler, self.hash, _sig_data)
    # notify wrangler that a position has been opened
    log.PositionUpdateNotification(self.wrangler, self, "status", self.POSITION_STATUS_OPEN)

    return True


@public
def topup_collateral(_caller: address, _borrow_currency_increment: uint256) -> bool:
    assert msg.sender == self.protocol_address, "Only protocol can call this function"
    # confirm sender is borrower
    assert _caller == self.borrower
    # confirm position has not expired yet
    assert self.expires_at >= block.timestamp
    # confirm position is still active
    assert self.status == self.POSITION_STATUS_OPEN
    # perform topup
    self.borrow_currency_current_value += _borrow_currency_increment
    # Notify wrangler that a collateral has been topped up
    log.PositionUpdateNotification(self.wrangler, self, "borrow_currency_value", self.COLLATERAL_TOPPED_UP)

    return True


@public
def withdraw_collateral(_caller: address, _borrow_currency_decrement: uint256) -> bool:
    assert msg.sender == self.protocol_address, "Only protocol can call this function"
    # confirm sender is borrower
    assert _caller == self.borrower
    # confirm position has not expired yet
    assert self.expires_at >= block.timestamp
    # confirm position is still active
    assert self.status == self.POSITION_STATUS_OPEN
    # perform topup
    self.borrow_currency_current_value -= _borrow_currency_decrement
    # transfer _borrow_currency_decrement from this address to borrower
    token_transfer: bool = ERC20(self.borrow_currency_address).transfer(
        self.borrower,
        _borrow_currency_decrement
    )
    assert token_transfer
    # Notify wrangler that a collateral has been withdrawn
    log.PositionUpdateNotification(self.wrangler, self, "borrow_currency_value", self.COLLATERAL_WITHDRAWN)

    return True


@public
def liquidate(_caller: address) -> bool:
    assert msg.sender == self.protocol_address, "Only protocol can call this function"
    # confirm position has expired
    assert self.expires_at < block.timestamp
    # confirm sender is lender or wrangler
    assert ((_caller == self.wrangler) or (_caller == self.lender))
    # confirm position is still active
    assert self.status == self.POSITION_STATUS_OPEN
    # perform liquidation
    self.status = self.POSITION_STATUS_LIQUIDATED
    # transfer borrow_currency_current_value from this address to the sender
    token_transfer: bool = ERC20(self.borrow_currency_address).transfer(
        _caller,
        self.borrow_currency_current_value
    )
    assert token_transfer
    # notify wrangler that a position has been liquidated
    log.PositionUpdateNotification(self.wrangler, self, "status", self.POSITION_STATUS_LIQUIDATED)

    return True


@public
def close(_caller: address) -> bool:
    assert msg.sender == self.protocol_address, "Only protocol can call this function"
    # confirm sender is borrower
    assert _caller == self.borrower
    # confirm position has not expired yet
    assert self.expires_at >= block.timestamp
    # confirm position is still active
    assert self.status == self.POSITION_STATUS_OPEN
    # perform closure
    self.status = self.POSITION_STATUS_CLOSED
    # transfer borrow_currency_current_value from this address to borrower
    token_transfer: bool = ERC20(self.borrow_currency_address).transfer(
        self.borrower,
        self.borrow_currency_current_value
    )
    assert token_transfer
    # Notify wrangler that a position has been closed
    log.PositionUpdateNotification(self.wrangler, self, "status", self.POSITION_STATUS_CLOSED)

    return True


@public
def rollover(_caller: address, _new_position_address: address, _protocol_token_address: address) -> bool:
    assert msg.sender == self.protocol_address, "Only protocol can call this function"
    assert _new_position_address.is_contract, "New position should be a contract"
    assert as_unitless_number(self.rollover_fee) > 0, "Cannot perform rollover since is 0"
    # confirm sender is wrangler
    assert _caller == self.wrangler
    # confirm position is still active
    assert self.status == self.POSITION_STATUS_OPEN
    # perform rollover
    self.status = self.POSITION_STATUS_ROLLED_OVER
    # transfer borrow_currency_current_value from this address to _new_position_address
    token_transfer: bool = ERC20(self.borrow_currency_address).transfer(
        _new_position_address,
        self.borrow_currency_current_value
    )
    assert token_transfer
    # transfer rollover_fee from this address to wrangler
    token_transfer = ERC20(_protocol_token_address).transfer(
        self.wrangler,
        self.rollover_fee
    )
    assert token_transfer
    # Notify wrangler that a position has been closed
    log.PositionUpdateNotification(self.wrangler, self, "status", self.POSITION_STATUS_ROLLED_OVER)

    return True
