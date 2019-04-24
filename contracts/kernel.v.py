# THIS CONTRACT IS NOT AUDITED!


# struct representing a kernel
struct Kernel:
    lender: address
    borrower: address
    relayer: address
    wrangler: address
    borrow_currency_address: address
    lend_currency_address: address
    lend_currency_offered_value: uint256
    relayer_fee: uint256
    monitoring_fee: uint256
    rollover_fee: uint256
    closure_fee: uint256
    salt: bytes32
    expires_at: timestamp
    daily_interest_rate: uint256
    position_duration_in_seconds: timedelta

protocol_address: public(address)

filled: public(map(bytes32, uint256))
cancelled: public(map(bytes32, uint256))


@public
def initialize() -> bool:
    assert self.protocol_address == ZERO_ADDRESS, "Contract has already been initialized"
    self.protocol_address = msg.sender
    return True


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
def filled_or_cancelled(_kernel_hash: bytes32) -> uint256:
    return as_unitless_number(self.filled[_kernel_hash]) + as_unitless_number(self.cancelled[_kernel_hash])


@public
@constant
def kernel_hash(
        _addresses: address[6], _values: uint256[5],
        _kernel_expires_at: timestamp, _creator_salt: bytes32,
        _daily_interest_rate: uint256, _position_duration_in_seconds: timedelta
        ) -> bytes32:
    if not msg.sender == self:
        assert msg.sender == self.protocol_address, "Only the protocol can call this function"
    return sha3(
        concat(
            convert(self, bytes32),
            convert(_addresses[0], bytes32),# lender
            convert(_addresses[1], bytes32),# borrower
            convert(_addresses[2], bytes32),# relayer
            convert(_addresses[3], bytes32),# wrangler
            convert(_addresses[4], bytes32),# collateralToken
            convert(_addresses[5], bytes32),# loanToken
            convert(_values[0], bytes32),# loanAmountOffered
            convert(_values[1], bytes32),# relayerFeeLST
            convert(_values[2], bytes32),# monitoringFeeLST
            convert(_values[3], bytes32),# rolloverFeeLST
            convert(_values[4], bytes32),# closureFeeLST
            _creator_salt,# creatorSalt
            convert(_kernel_expires_at, bytes32),# offerExpiryTimestamp
            convert(_daily_interest_rate, bytes32),# loanInterestRatePerDay
            convert(_position_duration_in_seconds, bytes32)# loanDuration
        )
    )


@public
def fill(
        _addresses: address[6],
        # _addresses: lender, borrower, relayer, wrangler, collateralToken, loanToken
        _values: uint256[7],
        # _values: collateralAmount, loanAmountOffered, relayerFeeLST, monitoringFeeLST, rolloverFeeLST, closureFeeLST, loanAmountFilled
        _nonce: uint256,
        _kernel_daily_interest_rate: uint256,
        _is_creator_lender: bool,
        _timestamps: timestamp[2],
        # kernel_expires_at, wrangler_approval_expires_at
        _position_duration_in_seconds: timedelta,
        # loanDuration
        _kernel_creator_salt: bytes32,
        _sig_data_kernel_creator: bytes[65],
        _sig_data_wrangler: bytes[65]
        # v, r, s of kernel_creator and wrangler
        ) -> bool:
    assert msg.sender == self.protocol_address, "Only the protocol can call this function"
    # validate _lender is not empty
    assert _addresses[0] != ZERO_ADDRESS
    # validate _borrower is not empty
    assert _addresses[1] != ZERO_ADDRESS
    _kernel_creator: address = _addresses[1]
    _kernel: Kernel = Kernel({
        lender: ZERO_ADDRESS,
        borrower: _addresses[1],
        relayer: _addresses[2],
        wrangler: _addresses[3],
        borrow_currency_address: _addresses[4],
        lend_currency_address: _addresses[5],
        lend_currency_offered_value: _values[1],
        relayer_fee: _values[2],
        monitoring_fee: _values[3],
        rollover_fee: _values[4],
        closure_fee: _values[5],
        salt: _kernel_creator_salt,
        expires_at: _timestamps[0],
        daily_interest_rate: _kernel_daily_interest_rate,
        position_duration_in_seconds: _position_duration_in_seconds
    })
    if _is_creator_lender:
        _kernel_creator = _addresses[0]
        _kernel.lender = _addresses[0]
        _kernel.borrower = ZERO_ADDRESS
    # It's OK if _relayer is empty
    # validate _wrangler is not empty
    assert _kernel.wrangler != ZERO_ADDRESS
    # validate loan amounts
    assert as_unitless_number(_values[0]) > 0
    assert as_unitless_number(_kernel.lend_currency_offered_value) > 0
    assert as_unitless_number(_values[6]) > 0
    # validate asked and offered expiry timestamps
    assert _kernel.expires_at > block.timestamp
    # validate daily interest rate on Kernel is greater than 0
    assert as_unitless_number(_kernel.daily_interest_rate) > 0
    # compute hash of kernel
    _k_hash: bytes32 = self.kernel_hash(
        [_kernel.lender, _kernel.borrower, _kernel.relayer, _kernel.wrangler,
        _kernel.borrow_currency_address, _kernel.lend_currency_address],
        [_kernel.lend_currency_offered_value,
        _kernel.relayer_fee, _kernel.monitoring_fee, _kernel.rollover_fee, _kernel.closure_fee],
        _kernel.expires_at, _kernel.salt, _kernel.daily_interest_rate, _kernel.position_duration_in_seconds)
    # validate kernel_creator's signature
    assert self.is_signer(_kernel_creator, _k_hash, _sig_data_kernel_creator), "Invalid kernel signer"
    # validate loan amount to be filled
    assert as_unitless_number(_kernel.lend_currency_offered_value) - as_unitless_number(self.filled_or_cancelled(_k_hash)) >= as_unitless_number(_values[6])
    # fill offer with lending currency
    self.filled[_k_hash] += _values[6]

    return True


@public
def cancel(
        _caller: address,
        _addresses: address[6], _values: uint256[5],
        _kernel_expires: timestamp, _kernel_creator_salt: bytes32,
        _kernel_daily_interest_rate: uint256, _position_duration_in_seconds: timedelta,
        _sig_data: bytes[65],
        _lend_currency_cancel_value: uint256) -> bool:
    assert msg.sender == self.protocol_address, "Only the protocol can call this function"
    # compute kernel hash from inputs
    _kernel: Kernel = Kernel({
        lender: _addresses[0],
        borrower: _addresses[1],
        relayer: _addresses[2],
        wrangler: _addresses[3],
        borrow_currency_address: _addresses[4],
        lend_currency_address: _addresses[5],
        lend_currency_offered_value: _values[0],
        relayer_fee: _values[1],
        monitoring_fee: _values[2],
        rollover_fee: _values[3],
        closure_fee: _values[4],
        salt: _kernel_creator_salt,
        expires_at: _kernel_expires,
        daily_interest_rate: _kernel_daily_interest_rate,
        position_duration_in_seconds: _position_duration_in_seconds
    })
    _k_hash: bytes32 = self.kernel_hash(
        [_kernel.lender, _kernel.borrower, _kernel.relayer, _kernel.wrangler,
        _kernel.borrow_currency_address, _kernel.lend_currency_address],
        [_kernel.lend_currency_offered_value,
        _kernel.relayer_fee, _kernel.monitoring_fee, _kernel.rollover_fee, _kernel.closure_fee],
        _kernel.expires_at, _kernel.salt, _kernel.daily_interest_rate, _kernel.position_duration_in_seconds)
    # verify sender is kernel creator
    assert self.is_signer(_caller, _k_hash, _sig_data)
    # verify sanity of offered and cancellation amounts
    assert as_unitless_number(_kernel.lend_currency_offered_value) > 0
    assert as_unitless_number(_lend_currency_cancel_value) > 0
    # verify cancellation amount does not exceed remaining loan amount to be filled
    assert as_unitless_number(_kernel.lend_currency_offered_value) - self.filled_or_cancelled(_k_hash) >= as_unitless_number(_lend_currency_cancel_value)
    self.cancelled[_k_hash] += _lend_currency_cancel_value

    return True
