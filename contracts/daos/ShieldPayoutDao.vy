# @version 0.1.0b16
# @notice Implementation of Lendroid v2 - Shield Payout DAO
# @dev THIS CONTRACT IS CURRENTLY UNDER AUDIT
# @author Vignesh (Vii) Meenakshi Sundaram (@vignesh-msundaram)
# Lendroid Foundation


from ...interfaces import ERC20Interface
from ...interfaces import MultiFungibleTokenInterface
from ...interfaces import CurrencyDaoInterface
from ...interfaces import MarketDaoInterface

from ...interfaces import ProtocolDaoInterface


LST: public(address)
protocol_dao: public(address)
# dao_type => dao_address
daos: public(map(int128, address))
# shield_market_hash => graph_address
registered_shield_markets: public(map(bytes32, bool))

DAO_CURRENCY: constant(int128) = 1
DAO_MARKET: constant(int128) = 4

CALLER_ESCAPE_HATCH_TOKEN_HOLDER: constant(int128) = 3

MFT_TYPE_F: constant(int128) = 1
MFT_TYPE_I: constant(int128) = 2
MFT_TYPE_S: constant(int128) = 3
MFT_TYPE_U: constant(int128) = 4

initialized: public(bool)
paused: public(bool)


@public
def initialize(
        _LST: address,
        _dao_currency: address,
        _dao_market: address
        ) -> bool:
    # validate inputs
    assert _LST.is_contract
    assert _dao_currency.is_contract
    assert _dao_market.is_contract
    assert not self.initialized
    self.initialized = True
    self.protocol_dao = msg.sender
    self.LST = _LST

    self.daos[DAO_CURRENCY] = _dao_currency
    self.daos[DAO_MARKET] = _dao_market

    return True


@private
@constant
def _mft_hash(_address: address, _currency: address, _expiry: timestamp, _underlying: address, _strike_price: uint256) -> bytes32:
    """
        @dev Function to get the hash of a MFT, given its address and indicators.
        @param _address The address of the MFT.
        @param _currency The address of the currency token in the MFT.
        @param _expiry The timestamp when the MFT expires.
        @param _underlying The address of the underlying token in the MFT.
        @param _strike_price The price of the underlying per currency at _expiry.
        @return A unique bytes32 representing the MFT at the given address and indicators.
    """
    return keccak256(
        concat(
            convert(self.protocol_dao, bytes32),
            convert(_address, bytes32),
            convert(_currency, bytes32),
            convert(_expiry, bytes32),
            convert(_underlying, bytes32),
            convert(_strike_price, bytes32)
        )
    )


@private
@constant
def _shield_market_hash(_currency: address, _expiry: timestamp, _underlying: address, _strike_price: uint256) -> bytes32:
    return keccak256(
        concat(
            convert(self.protocol_dao, bytes32),
            convert(_currency, bytes32),
            convert(_expiry, bytes32),
            convert(_underlying, bytes32),
            convert(_strike_price, bytes32)
        )
    )


@private
@constant
def _loan_market_hash(_currency: address, _expiry: timestamp, _underlying: address) -> bytes32:
    return self._shield_market_hash(_currency, _expiry, _underlying, 0)


@private
@constant
def _s_payoff(_currency: address, _expiry: timestamp, _underlying: address, _strike_price: uint256) -> uint256:
    return MarketDaoInterface(self.daos[DAO_MARKET]).s_payoff(_currency, _expiry, _underlying, _strike_price)


@private
@constant
def _u_payoff(_currency: address, _expiry: timestamp, _underlying: address, _strike_price: uint256) -> uint256:
    return MarketDaoInterface(self.daos[DAO_MARKET]).u_payoff(_currency, _expiry, _underlying, _strike_price)


@private
def _settle_s(
    _currency: address, _expiry: timestamp, _underlying: address, _strike_price: uint256,
    _currency_quantity: uint256, _from: address, _to: address):
    # validate currency
    assert CurrencyDaoInterface(self.daos[DAO_CURRENCY]).is_token_supported(_currency)
    # validate underlying
    assert CurrencyDaoInterface(self.daos[DAO_CURRENCY]).is_token_supported(_underlying)
    _loan_market_hash: bytes32 = self._loan_market_hash(_currency, _expiry, _underlying)
    assert MarketDaoInterface(self.daos[DAO_MARKET]).loan_markets__status(_loan_market_hash) == MarketDaoInterface(self.daos[DAO_MARKET]).LOAN_MARKET_STATUS_CLOSED()
    _shield_market_hash: bytes32 = self._shield_market_hash(_currency, _expiry, _underlying, _strike_price)
    assert self.registered_shield_markets[_shield_market_hash]
    _l_address: address = ZERO_ADDRESS
    _i_address: address = ZERO_ADDRESS
    _f_address: address = ZERO_ADDRESS
    _s_address: address = ZERO_ADDRESS
    _u_address: address = ZERO_ADDRESS
    _l_address, _i_address, _f_address, _s_address, _u_address = CurrencyDaoInterface(self.daos[DAO_CURRENCY]).mft_addresses(_currency)
    # mint _payout in l_currency
    _payout: uint256 = self._s_payoff(_currency, _expiry, _underlying, _strike_price)
    assert as_unitless_number(_payout) > 0
    # burn s_token from _from account
    assert_modifiable(MultiFungibleTokenInterface(MarketDaoInterface(self.daos[DAO_MARKET]).shield_markets__s_address(_shield_market_hash)).burn(
        MarketDaoInterface(self.daos[DAO_MARKET]).shield_markets__s_id(_shield_market_hash),
        _from,
        as_unitless_number(_currency_quantity) * (10 ** 18)
    ))
    # mint l_token to _to account
    assert_modifiable(CurrencyDaoInterface(self.daos[DAO_CURRENCY]).mint_and_self_authorize_erc20(
        _l_address, _to,
        as_unitless_number(_payout) * as_unitless_number(_currency_quantity)
    ))


@private
def _settle_u(_currency: address, _expiry: timestamp, _underlying: address, _strike_price: uint256,
    _currency_quantity: uint256, _from: address, _to: address):
    # validate currency
    assert CurrencyDaoInterface(self.daos[DAO_CURRENCY]).is_token_supported(_currency)
    # validate underlying
    assert CurrencyDaoInterface(self.daos[DAO_CURRENCY]).is_token_supported(_underlying)
    _loan_market_hash: bytes32 = self._loan_market_hash(_currency, _expiry, _underlying)
    assert MarketDaoInterface(self.daos[DAO_MARKET]).loan_markets__status(_loan_market_hash) == MarketDaoInterface(self.daos[DAO_MARKET]).LOAN_MARKET_STATUS_CLOSED()
    _shield_market_hash: bytes32 = self._shield_market_hash(_currency, _expiry, _underlying, _strike_price)
    assert self.registered_shield_markets[_shield_market_hash]
    _l_address: address = ZERO_ADDRESS
    _i_address: address = ZERO_ADDRESS
    _f_address: address = ZERO_ADDRESS
    _s_address: address = ZERO_ADDRESS
    _u_address: address = ZERO_ADDRESS
    _l_address, _i_address, _f_address, _s_address, _u_address = CurrencyDaoInterface(self.daos[DAO_CURRENCY]).mft_addresses(_currency)
    # mint _payout in l_currency
    _payout: uint256 = self._u_payoff(_currency, _expiry, _underlying, _strike_price)
    assert as_unitless_number(_payout) > 0
    # burn u_token from _from account
    assert_modifiable(MultiFungibleTokenInterface(MarketDaoInterface(self.daos[DAO_MARKET]).shield_markets__u_address(_shield_market_hash)).burn(
        MarketDaoInterface(self.daos[DAO_MARKET]).shield_markets__u_id(_shield_market_hash),
        _from,
        as_unitless_number(_currency_quantity) * (10 ** 18)
    ))
    # mint l_token to _to account
    assert_modifiable(CurrencyDaoInterface(self.daos[DAO_CURRENCY]).mint_and_self_authorize_erc20(
        _l_address, _to,
        as_unitless_number(_payout) * as_unitless_number(_currency_quantity)
    ))


@public
@constant
def shield_market_hash(_currency: address, _expiry: timestamp, _underlying: address, _strike_price: uint256) -> bytes32:
    return self._shield_market_hash(_currency, _expiry, _underlying, _strike_price)


@public
@constant
def s_payoff(_currency: address, _expiry: timestamp, _underlying: address, _strike_price: uint256) -> uint256:
    return self._s_payoff(_currency, _expiry, _underlying, _strike_price)


@public
@constant
def u_payoff(_currency: address, _expiry: timestamp, _underlying: address, _strike_price: uint256) -> uint256:
    return self._u_payoff(_currency, _expiry, _underlying, _strike_price)



# Admin functions
@public
def register_shield_market(_currency: address, _expiry: timestamp, _underlying: address, _strike_price: uint256) -> bool:
    # validate inputs
    assert _currency.is_contract
    assert as_unitless_number(_expiry) > 0
    assert _underlying.is_contract
    assert as_unitless_number(_strike_price) > 0
    assert msg.sender == self.daos[DAO_MARKET]
    _shield_market_hash: bytes32 = self._shield_market_hash(_currency, _expiry, _underlying, _strike_price)
    self.registered_shield_markets[_shield_market_hash] = True

    return True


# Escape-hatches

@private
def _pause():
    """
        @dev Internal function to pause this contract.
    """
    assert not self.paused
    self.paused = True


@private
def _unpause():
    """
        @dev Internal function to unpause this contract.
    """
    assert self.paused
    self.paused = False

@public
def pause() -> bool:
    """
        @dev Escape hatch function to pause this contract. Only the Protocol DAO
             can call this function.
        @return A bool with a value of "True" indicating this contract has been
             paused.
    """
    assert self.initialized
    assert msg.sender == self.protocol_dao
    self._pause()
    return True


@public
def unpause() -> bool:
    """
        @dev Escape hatch function to unpause this contract. Only the Protocol
             DAO can call this function.
        @return A bool with a value of "True" indicating this contract has been
             unpaused.
    """
    assert self.initialized
    assert msg.sender == self.protocol_dao
    self._unpause()
    return True


@private
def _transfer_balance_erc20(_token: address):
    """
        @dev Internal function to transfer this contract's balance of the given
             ERC20 token to the Escape Hatch Token Holder.
        @param _token The address of the ERC20 token.
    """
    assert_modifiable(ERC20Interface(_token).transfer(
        ProtocolDaoInterface(self.protocol_dao).authorized_callers(CALLER_ESCAPE_HATCH_TOKEN_HOLDER),
        ERC20Interface(_token).balanceOf(self)
    ))


@private
def _transfer_balance_mft(_token: address,
    _currency: address, _expiry: timestamp, _underlying: address, _strike_price: uint256):
    """
        @dev Internal function to transfer this contract's balance of MFT based
             on the given indicators to the Escape Hatch Token Holder.
        @param _token The address of the MFT.
        @param _currency The address of the currency token in the MFT.
        @param _expiry The timestamp when the MFT expires.
        @param _underlying The address of the underlying token in the MFT.
        @param _strike_price The price of the underlying per currency at _expiry.
    """
    _mft_hash: bytes32 = self._mft_hash(_token, _currency, _expiry, _underlying, _strike_price)
    _id: uint256 = MultiFungibleTokenInterface(_token).hash_to_id(_mft_hash)
    _balance: uint256 = MultiFungibleTokenInterface(_token).balanceOf(self, _id)
    assert_modifiable(MultiFungibleTokenInterface(_token).safeTransferFrom(
        self,
        ProtocolDaoInterface(self.protocol_dao).authorized_callers(CALLER_ESCAPE_HATCH_TOKEN_HOLDER),
        _id, _balance, EMPTY_BYTES32
    ))


@public
def escape_hatch_erc20(_currency: address, _is_l: bool) -> bool:
    """
        @dev Escape hatch function to transfer all tokens of an ERC20 address
             from this contract to the Escape Hatch Token Holder. Only the
             Protocol DAO can call this function.
        @param _currency The address of the ERC20 token
        @param _is_l A bool indicating if the ERC20 token is an L Token
        @return A bool with a value of "True" indicating the ERC20 transfer has
             been made to the Escape Hatch Token Holder.
    """
    assert self.initialized
    assert msg.sender == self.protocol_dao
    _token: address = _currency
    if _is_l:
        CurrencyDaoInterface(self.daos[DAO_CURRENCY]).token_addresses__l(_currency)
    self._transfer_balance_erc20(_currency)
    return True


@public
def escape_hatch_mft(_mft_type: int128, _currency: address, _expiry: timestamp, _underlying: address, _strike_price: uint256) -> bool:
    """
        @dev Escape hatch function to transfer all tokens of a MFT with given
             parameters from this contract to the Escape Hatch Token Holder.
             Only the Protocol DAO can call this function.
        @param _mft_type The MFT type (L, I, S, or U) from which the MFT address
             could be deduced.
        @param _currency The address of the currency token in the MFT.
        @param _expiry The timestamp when the MFT expires.
        @param _underlying The address of the underlying token in the MFT.
        @param _strike_price The price of the underlying per currency at _expiry.
        @return A bool with a value of "True" indicating the MFT transfer has
             been made to the Escape Hatch Token Holder.
    """
    assert self.initialized
    assert msg.sender == self.protocol_dao
    _token: address = ZERO_ADDRESS
    if _mft_type == MFT_TYPE_F:
        _token = CurrencyDaoInterface(self.daos[DAO_CURRENCY]).token_addresses__f(_currency)
    if _mft_type == MFT_TYPE_I:
        _token = CurrencyDaoInterface(self.daos[DAO_CURRENCY]).token_addresses__i(_currency)
    if _mft_type == MFT_TYPE_S:
        _token = CurrencyDaoInterface(self.daos[DAO_CURRENCY]).token_addresses__s(_currency)
    if _mft_type == MFT_TYPE_U:
        _token = CurrencyDaoInterface(self.daos[DAO_CURRENCY]).token_addresses__u(_currency)
    assert not _token == ZERO_ADDRESS
    self._transfer_balance_mft(_token, _currency, _expiry, _underlying, _strike_price)
    return True


# non-admin functions
@public
def exercise_s(_currency: address, _expiry: timestamp, _underlying: address, _strike_price: uint256,
    _quantity: uint256) -> bool:
    assert self.initialized
    assert not self.paused
    assert block.timestamp > _expiry
    _shield_market_hash: bytes32 = self._shield_market_hash(_currency, _expiry, _underlying, _strike_price)
    assert self.registered_shield_markets[_shield_market_hash]
    self._settle_s(_currency, _expiry, _underlying, _strike_price, _quantity, msg.sender, msg.sender)

    return True


@public
def exercise_u(_currency: address, _expiry: timestamp, _underlying: address, _strike_price: uint256,
    _quantity: uint256) -> bool:
    assert self.initialized
    assert not self.paused
    assert block.timestamp > _expiry
    _shield_market_hash: bytes32 = self._shield_market_hash(_currency, _expiry, _underlying, _strike_price)
    assert self.registered_shield_markets[_shield_market_hash]
    self._settle_u(_currency, _expiry, _underlying, _strike_price, _quantity, msg.sender, msg.sender)

    return True
