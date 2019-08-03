# Vyper version of the Lendroid protocol v2
# THIS CONTRACT IS NOT AUDITED!


# External Contracts
contract Kernel:
    def initialize() -> bool: modifying
    def ecrecover_from_signature(_hash: bytes32, _sig: bytes[65]) -> address: constant
    def is_signer(_prover: address, _hash: bytes32, _sig: bytes[65]) -> bool: constant
    def filled_or_cancelled(_kernel_hash: bytes32) -> uint256: constant
    def kernel_hash(_addresses: address[6], _values: uint256[5], _kernel_expires_at: uint256(sec, positional), _creator_salt: bytes32, _daily_interest_rate: uint256, _position_duration_in_seconds: uint256(sec)) -> bytes32: constant
    def fill(_addresses: address[6], _values: uint256[7], _nonce: uint256, _kernel_daily_interest_rate: uint256, _is_creator_lender: bool, _timestamps: uint256(sec, positional)[2], _position_duration_in_seconds: uint256(sec), _kernel_creator_salt: bytes32, _sig_data_kernel_creator: bytes[65], _sig_data_wrangler: bytes[65]) -> bool: modifying
    def cancel(_caller: address, _addresses: address[6], _values: uint256[5], _kernel_expires: uint256(sec, positional), _kernel_creator_salt: bytes32, _kernel_daily_interest_rate: uint256, _position_duration_in_seconds: uint256(sec), _sig_data: bytes[65], _lend_currency_cancel_value: uint256) -> bool: modifying
    def protocol_address() -> address: constant
    def filled(arg0: bytes32) -> uint256: constant
    def cancelled(arg0: bytes32) -> uint256: constant


# External Contracts
contract Position:
    def ecrecover_from_signature(_hash: bytes32, _sig: bytes[65]) -> address: constant
    def is_signer(_prover: address, _hash: bytes32, _sig: bytes[65]) -> bool: constant
    def position() -> (uint256, address, address, address, address, address, uint256(sec, positional), uint256(sec, positional), uint256(sec, positional), address, address, uint256, uint256, uint256, uint256, uint256, uint256, uint256, uint256, uint256, uint256, bytes32): constant
    def position_hash(_addresses: address[7], _values: uint256[7], _lend_currency_owed_value: uint256, _nonce: uint256) -> bytes32: constant
    def owed_value(_filled_value: uint256, _kernel_daily_interest_rate: uint256, _position_duration_in_seconds: uint256(sec)) -> uint256: constant
    def escape_hatch_token(_recipient: address, _token_address: address) -> bool: modifying
    def initialize(_index: uint256, _kernel_creator: address, _addresses: address[6], _values: uint256[7], _nonce: uint256, _kernel_daily_interest_rate: uint256, _position_duration_in_seconds: uint256(sec), _approval_expires: uint256(sec, positional), _sig_data: bytes[65]) -> bool: modifying
    def topup_collateral(_caller: address, _borrow_currency_increment: uint256) -> bool: modifying
    def withdraw_collateral(_caller: address, _borrow_currency_decrement: uint256) -> bool: modifying
    def liquidate(_caller: address) -> bool: modifying
    def close(_caller: address) -> bool: modifying
    def rollover(_caller: address, _new_position_address: address, _protocol_token_address: address) -> bool: modifying
    def index() -> uint256: constant
    def kernel_creator() -> address: constant
    def lender() -> address: constant
    def borrower() -> address: constant
    def relayer() -> address: constant
    def wrangler() -> address: constant
    def created_at() -> uint256(sec, positional): constant
    def updated_at() -> uint256(sec, positional): constant
    def expires_at() -> uint256(sec, positional): constant
    def borrow_currency_address() -> address: constant
    def lend_currency_address() -> address: constant
    def borrow_currency_value() -> uint256: constant
    def borrow_currency_current_value() -> uint256: constant
    def lend_currency_filled_value() -> uint256: constant
    def lend_currency_owed_value() -> uint256: constant
    def status() -> uint256: constant
    def nonce() -> uint256: constant
    def relayer_fee() -> uint256: constant
    def monitoring_fee() -> uint256: constant
    def rollover_fee() -> uint256: constant
    def closure_fee() -> uint256: constant
    def hash() -> bytes32: constant
    def protocol_address() -> address: constant
    def SECONDS_PER_DAY() -> uint256: constant
    def POSITION_STATUS_OPEN() -> uint256: constant
    def POSITION_STATUS_CLOSED() -> uint256: constant
    def POSITION_STATUS_LIQUIDATED() -> uint256: constant
    def POSITION_TOPPED_UP() -> uint256: constant


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


# Events of the protocol.
ProtocolParameterUpdateNotification: event({_notification_key: string[64], _address: indexed(address), _notification_value: uint256})

# Variables of the protocol.
protocol_token_address: public(address)
kernel_address: public(address)
position_template_address: public(address)
owner: public(address)
# all positions
positions: public(map(address, bool))
# positions: public(map(bytes32, Position))
last_position_index: public(uint256)
position_index: public(map(uint256, address))
borrow_positions: public(map(address, map(uint256, address)))
lend_positions: public(map(address, map(uint256, address)))
borrow_position_index: map(address, map(address, uint256))
lend_position_index: map(address, map(address, uint256))
borrow_positions_count: public(map(address, uint256))
lend_positions_count: public(map(address, uint256))

# wrangler
wranglers: public(map(address, bool))
wrangler_nonces: public(map(address, map(address, uint256)))

# tokens
supported_tokens: public(map(address, bool))

# nonreentrant locks for positions, inspired from https://github.com/ethereum/vyper/issues/1204
nonreentrant_locks: map(address, bool)

# constants
SECONDS_PER_DAY: public(uint256)


@public
def __init__(
        _protocol_token_address: address,
        _kernel_template_address: address,
        _position_template_address: address
        ):
    self.owner = msg.sender
    self.protocol_token_address = _protocol_token_address
    self.SECONDS_PER_DAY = 86400

    self.kernel_address = create_forwarder_to(_kernel_template_address)
    kernel_initialization: bool = Kernel(self.kernel_address).initialize()
    assert kernel_initialization

    self.position_template_address = _position_template_address


# constant functions
@public
@constant
def position(_position_address: address) -> (uint256, address, address, address, address, address, timestamp, timestamp, timestamp, address, address, uint256, uint256,
    uint256, uint256, uint256, uint256, uint256, uint256, uint256, uint256, bytes32):
    return Position(_position_address).position()


@public
@constant
def position_counts(_address: address) -> (uint256, uint256):
    return (self.borrow_positions_count[_address], self.lend_positions_count[_address])


@public
@constant
def kernels_filled(_kernel_hash: bytes32) -> uint256:
    return Kernel(self.kernel_address).filled(_kernel_hash)


@public
@constant
def kernels_cancelled(_kernel_hash: bytes32) -> uint256:
    return Kernel(self.kernel_address).cancelled(_kernel_hash)


@public
@constant
def kernel_hash(
        _addresses: address[6], _values: uint256[5],
        _kernel_expires_at: timestamp, _creator_salt: bytes32,
        _daily_interest_rate: uint256, _position_duration_in_seconds: timedelta
        ) -> bytes32:
    return Kernel(self.kernel_address).kernel_hash(
        _addresses, _values, _kernel_expires_at, _creator_salt,
        _daily_interest_rate, _position_duration_in_seconds
    )


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
            convert(self, bytes32),
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
def escape_hatch_token(_token_address: address) -> bool:
    assert msg.sender == self.owner
    # transfer token from this address to owner (message sender)
    token_transfer: bool = ERC20(_token_address).transfer(
        msg.sender,
        ERC20(_token_address).balanceOf(self)
    )
    assert token_transfer
    return True


@public
def escape_hatch_token_from_position(_position_address: address, _token_address: address) -> bool:
    assert msg.sender == self.owner
    # transfer token from this address to owner (message sender)
    token_transfer: bool = Position(_position_address).escape_hatch_token(
        msg.sender,
        _token_address
    )
    assert token_transfer
    return True


# protocol parameter functions
@public
def set_wrangler_status(_address: address, _is_active: bool) -> bool:
    assert msg.sender == self.owner
    self.wranglers[_address] = _is_active
    log.ProtocolParameterUpdateNotification("wrangler_status", _address, convert(_is_active, uint256))
    return True


@public
def set_token_support(_address: address, _is_active: bool) -> bool:
    assert msg.sender == self.owner
    assert _address.is_contract
    self.supported_tokens[_address] = _is_active
    log.ProtocolParameterUpdateNotification("token_support", _address, convert(_is_active, uint256))
    return True


# internal functions
@private
def lock_position(_position_address: address):
    assert self.nonreentrant_locks[_position_address] == False
    self.nonreentrant_locks[_position_address] = True


@private
def unlock_position(_position_address: address):
    assert self.nonreentrant_locks[_position_address] == True
    self.nonreentrant_locks[_position_address] = False


@private
def record_position(_lender: address, _borrower: address, _position_address: address):
    # borrow position
    self.borrow_positions_count[_borrower] += 1
    self.borrow_position_index[_borrower][_position_address] = self.borrow_positions_count[_borrower]
    self.borrow_positions[_borrower][self.borrow_positions_count[_borrower]] = _position_address
    # lend position
    self.lend_positions_count[_lender] += 1
    self.lend_position_index[_lender][_position_address] = self.lend_positions_count[_lender]
    self.lend_positions[_lender][self.lend_positions_count[_lender]] = _position_address


@private
def remove_position(_position_address: address):
    _borrower: address = Position(_position_address).borrower()
    _lender: address = Position(_position_address).lender()
    # update borrow position indices
    _current_position_index: uint256 = self.borrow_position_index[_borrower][_position_address]
    _last_position_index: uint256 = self.borrow_positions_count[_borrower]
    _last_position_address: address = self.borrow_positions[_borrower][_last_position_index]
    self.borrow_positions[_borrower][_current_position_index] = self.borrow_positions[_borrower][_last_position_index]
    clear(self.borrow_positions[_borrower][_last_position_index])
    clear(self.borrow_position_index[_borrower][_position_address])
    self.borrow_position_index[_borrower][_last_position_address] = _current_position_index
    self.borrow_positions_count[_borrower] -= 1
    # update lend position indices
    _current_position_index = self.lend_position_index[_lender][_position_address]
    _last_position_index = self.lend_positions_count[_lender]
    _last_position_address = self.lend_positions[_lender][_last_position_index]
    self.lend_positions[_lender][_current_position_index] = self.lend_positions[_lender][_last_position_index]
    clear(self.lend_positions[_lender][_last_position_index])
    clear(self.lend_position_index[_lender][_position_address])
    self.lend_position_index[_lender][_last_position_address] = _current_position_index
    self.lend_positions_count[_lender] -= 1


@public
def open_position(
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
    assert self.supported_tokens[_addresses[4]]
    # validate _loanToken is a contract address
    assert self.supported_tokens[_addresses[5]]
    # validate wrangler's activation status
    assert self.wranglers[_addresses[3]]
    # validate wrangler's approval expiry
    assert _timestamps[1] > block.timestamp

    _kernel_creator: address = _addresses[1]
    if _is_creator_lender:
        _kernel_creator = _addresses[0]

    # validate wrangler's nonce
    assert _nonce == self.wrangler_nonces[_addresses[3]][_kernel_creator] + 1
    # increment wrangler's nonce for kernel creator
    self.wrangler_nonces[_addresses[3]][_kernel_creator] += 1

    # fill kernel
    kernel_fill: bool = Kernel(self.kernel_address).fill(
        _addresses, _values, _nonce, _kernel_daily_interest_rate, _is_creator_lender,
        _timestamps, _position_duration_in_seconds, _kernel_creator_salt, _sig_data_kernel_creator,
        _sig_data_wrangler
    )
    assert kernel_fill
    # open position
    _position_address: address = create_forwarder_to(self.position_template_address)
    # lock position_non_reentrant before loan creation
    self.lock_position(_position_address)
    _position_updated: bool = Position(_position_address).initialize(
        self.last_position_index,
        _kernel_creator, _addresses, _values,
        _nonce, _kernel_daily_interest_rate,
        _position_duration_in_seconds, _timestamps[1], _sig_data_wrangler
    )
    assert _position_updated
    # update position index
    self.position_index[self.last_position_index] = _position_address
    self.last_position_index += 1
    # record position
    self.record_position(_addresses[0], _addresses[1], _position_address)
    token_transfer: bool = False
    # transfer borrow_currency_current_value from borrower to position contract
    token_transfer = ERC20(_addresses[4]).transferFrom(
        _addresses[1],
        _position_address,
        _values[0]
    )
    assert token_transfer, "Error during borrow_currency_current_value transfer from borrower to position contract"
    # transfer lend_currency_filled_value from lender to borrower
    token_transfer = ERC20(_addresses[5]).transferFrom(
        _addresses[0],
        _addresses[1],
        _values[6]
    )
    assert token_transfer, "Error during lend_currency_filled_value transfer from lender to borrower"
    # transfer monitoring_fee from lender to wrangler
    token_transfer = ERC20(self.protocol_token_address).transferFrom(
        _addresses[0],
        _addresses[3],
        _values[3]
    )
    assert token_transfer, "Error during monitoring_fee transfer from lender to wrangler"
    # transfer relayerFeeLST from kernel creator to relayer
    if (_addresses[2] != ZERO_ADDRESS) and (as_unitless_number(_values[2]) > 0):
        token_transfer = ERC20(self.protocol_token_address).transferFrom(
            _kernel_creator,
            _addresses[2],
            _values[2]
        )
        assert token_transfer, "Error during relayerFeeLST transfer from kernel creator to relayer"
    # transfer rolloverFeeLST from kernel borrower to position contract
    if as_unitless_number(_values[4]) > 0:
        token_transfer = ERC20(self.protocol_token_address).transferFrom(
            _addresses[1],
            _position_address,
            _values[4]
        )
        assert token_transfer, "Error during rolloverFeeLST transfer from borrower to position contract"
    # unlock position_non_reentrant after loan creation
    self.unlock_position(_position_address)

    return True


@public
def rollover_position(
        _old_position_address: address,
        _addresses: address[6],
        # _addresses: lender, borrower, relayer, wrangler, collateralToken, loanToken
        _values: uint256[7],
        # _values: collateralAmount, loanAmountOffered, relayerFeeLST, monitoringFeeLST, rolloverFeeLST, closureFeeLST, loanAmountFilled
        _nonce: uint256,
        _kernel_daily_interest_rate: uint256,
        _is_creator_lender: bool,
        wrangler_approval_expires_at: timestamp,
        # kernel_expires_at, wrangler_approval_expires_at
        _position_duration_in_seconds: timedelta,
        # loanDuration
        _sig_data_wrangler: bytes[65]
        # v, r, s of wrangler
        ) -> bool:
    assert self.supported_tokens[_addresses[4]]
    # validate _loanToken is a contract address
    assert self.supported_tokens[_addresses[5]]
    # validate wrangler's activation status
    assert self.wranglers[_addresses[3]]
    # validate wrangler's approval expiry
    assert _timestamps[1] > block.timestamp

    _kernel_creator: address = _addresses[1]
    if _is_creator_lender:
        _kernel_creator = _addresses[0]

    # validate wrangler's nonce
    assert _nonce == self.wrangler_nonces[_addresses[3]][_kernel_creator] + 1
    # lock position_non_reentrant before rollover
    self.lock_position(_old_position_address)
    self.remove_position(_old_position_address)
    # increment wrangler's nonce for kernel creator
    self.wrangler_nonces[_addresses[3]][_kernel_creator] += 1

    # open position
    _new_position_address: address = create_forwarder_to(self.position_template_address)
    # lock position_non_reentrant before loan creation
    self.lock_position(_new_position_address)
    _position_updated: bool = Position(_new_position_address).initialize(
        self.last_position_index,
        _kernel_creator, _addresses, _values,
        _nonce, _kernel_daily_interest_rate,
        _position_duration_in_seconds, wrangler_approval_expires_at, _sig_data_wrangler
    )
    assert _position_updated
    # update position index
    self.position_index[self.last_position_index] = _new_position_address
    self.last_position_index += 1
    # record position
    self.record_position(_addresses[0], _addresses[1], _new_position_address)
    token_transfer: bool = False
    # update old position contract, transfer borrow_currency_current_value from old to new position contract
    _old_position_updated: bool = Position(_old_position_address).rollover(
        msg.sender, _new_position_address, self.protocol_token_address
    )
    assert _old_position_updated
    # unlock position_non_reentrant after loan creation
    self.unlock_position(_position_address)

    # unlock position_non_reentrant after rollover
    self.unlock_position(_old_position_address)

    return True


@public
def topup_collateral(_position_address: address, _borrow_currency_increment: uint256) -> bool:
    # lock position_non_reentrant before topup
    self.lock_position(_position_address)
    # update position
    _position_updated: bool = Position(_position_address).topup_collateral(
        msg.sender, _borrow_currency_increment
    )
    assert _position_updated
    # transfer borrow_currency_current_value from borrower to this address
    token_transfer: bool = ERC20(Position(_position_address).borrow_currency_address()).transferFrom(
        msg.sender,
        _position_address,
        _borrow_currency_increment
    )
    assert token_transfer
    # unlock position_non_reentrant after topup
    self.unlock_position(_position_address)

    return True


@public
def withdraw_collateral(_position_address: address, _borrow_currency_decrement: uint256) -> bool:
    # lock position_non_reentrant before topup
    self.lock_position(_position_address)
    # update position
    _position_updated: bool = Position(_position_address).withdraw_collateral(
        msg.sender, _borrow_currency_decrement
    )
    assert _position_updated
    # unlock position_non_reentrant after topup
    self.unlock_position(_position_address)

    return True


@public
def liquidate_position(_position_address: address) -> bool:
    # lock position_non_reentrant before topup
    self.lock_position(_position_address)
    self.remove_position(_position_address)
    # update position
    _position_updated: bool = Position(_position_address).liquidate(msg.sender)
    assert _position_updated
    # unlock position_non_reentrant after topup
    self.unlock_position(_position_address)

    return True


@public
def close_position(_position_address: address) -> bool:
    # lock position_non_reentrant before topup
    self.lock_position(_position_address)
    self.remove_position(_position_address)
    # update position
    _position_updated: bool = Position(_position_address).close(msg.sender)
    assert _position_updated
    # transfer lend_currency_owed_value from borrower to lender
    token_transfer: bool = ERC20(Position(_position_address).lend_currency_address()).transferFrom(
        msg.sender,
        Position(_position_address).lender(),
        Position(_position_address).lend_currency_owed_value()
    )
    assert token_transfer
    # unlock position_non_reentrant after topup
    self.unlock_position(_position_address)

    return True


@public
def cancel_kernel(
        _addresses: address[6], _values: uint256[5],
        _kernel_expires: timestamp, _kernel_creator_salt: bytes32,
        _kernel_daily_interest_rate: uint256, _position_duration_in_seconds: timedelta,
        _sig_data: bytes[65],
        _lend_currency_cancel_value: uint256) -> bool:
    kernel_cancel: bool = Kernel(self.kernel_address).cancel(
        msg.sender,
        _addresses, _values, _kernel_expires, _kernel_creator_salt,
        _kernel_daily_interest_rate, _position_duration_in_seconds, _sig_data,
        _lend_currency_cancel_value
    )
    assert kernel_cancel

    return True
