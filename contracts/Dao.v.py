# Vyper version of the Lendroid protocol v2
# THIS CONTRACT HAS NOT BEEN AUDITED!


from contracts.interfaces import ERC20
from contracts.interfaces import ERC1155
from contracts.interfaces import ContinuousCurrencyPoolERC20
from contracts.interfaces import InterestPool
from contracts.interfaces import UnderwriterPool


# Structs
struct CurrencyStat:
    pool_address: address
    l_currency_address: address
    i_currency_address: address
    f_currency_address: address
    is_supported: bool


struct CurrencyPairStat:
    lend_currency_address: address
    collateral_currency_address: address
    s_currency_address: address
    u_currency_address: address
    is_supported: bool


struct SUFITokenOfferedExpiryStat:
    has_id: bool
    erc1155_id: uint256


struct PoolExpiryStat:
    is_active: bool
    has_id: bool
    erc1155_id: uint256


struct InterestPoolStat:
    name: string[64]
    is_active: bool
    expiries_offered: map(string[3], PoolExpiryStat)


struct UnderwriterPoolStat:
    name: string[64]
    is_active: bool
    expiries_offered: map(bytes32, PoolExpiryStat)


struct LoanMarketStat:
    lend_currency_address: address
    expiry: timestamp
    market_address: address


struct PoolOfferRegistrationStat:
    minimum_fee: uint256
    minimum_interval: timestamp
    fee_multiplier: uint256
    fee_multiplier_decimals: uint256
    last_registered_at: timestamp
    last_paid_fee: uint256


# Events of the protocol.
CurrencySupportNotification: event({_address: indexed(address), _notification_value: uint256})
CurrencyPairSupportNotification: event({_lend_currency_address: indexed(address), _collateral_currency_address: indexed(address), _notification_value: uint256})
ProtocolParameterExpiryUpdateNotification: event({_notification_key: indexed(string[64]), _timestamp: indexed(timestamp), _notification_value: uint256})

# Variables of the protocol.
protocol_currency_address: public(address)
owner: public(address)

supported_expiry: public(map(timestamp, bool))
expiry_to_label: public(map(timestamp, string[3]))
label_to_expiry: public(map(string[3], timestamp))
supported_currencies: public(map(address, bool))
currency_pools: public(map(address, address))
templates: public(map(string[64], address))
interest_pools: public(map(address, InterestPoolStat))
currencies: public(map(address, CurrencyStat))
fi_offered_expiries: public(map(address, map(string[3], SUFITokenOfferedExpiryStat)))
underwriter_pools: public(map(address, UnderwriterPoolStat))
currency_pairs: public(map(bytes32, CurrencyPairStat))
su_offered_expiries: public(map(address, map(bytes32, SUFITokenOfferedExpiryStat)))
su_currency_price_per_lend_currency: public(map(bytes32, uint256))

# pool_type => PoolOfferRegistrationStat
offer_registrations: public(map(uint256, PoolOfferRegistrationStat))

POOL_TYPE_INTEREST_POOL: public(uint256)
POOL_TYPE_UNDERWRITER_POOL: public(uint256)


@public
def __init__(_protocol_currency_address: address):
    self.owner = msg.sender
    self.protocol_currency_address = _protocol_currency_address
    self.POOL_TYPE_INTEREST_POOL = 1
    self.POOL_TYPE_UNDERWRITER_POOL = 2
    # after init, need to set the following template addresses:
    #. currency_pool_template
    #. ERC20_template
    #. ERC1155_template
    #. InterestPool_template
    #. UnderwriterPool_template


@private
@constant



@private
@constant
def validate_erc20_currency(_currency_address: address,
        _name: string[64], _symbol: string[32], _decimals: uint256) -> bool:
    assert ERC20(_currency_address).name() == _name
    assert ERC20(_currency_address).symbol() == _symbol
    assert ERC20(_currency_address).decimals() == _decimals
    return True


@private
@constant
def _currency_pair_hash(_lend_currency_address: address, _collateral_currency_address: address) -> bytes32:
    return keccak256(
        concat(
            convert(self, bytes32),
            convert(_lend_currency_address, bytes32),
            convert(_collateral_currency_address, bytes32)
        )
    )


@private
@constant
def _shield_hash(_lend_currency_address: address, _underlying_currency_address: address, _strike_price: uint256, _expiry_label: string[3]) -> bytes32:
    return keccak256(
        concat(
            convert(self, bytes32),
            convert(_lend_currency_address, bytes32),
            convert(_underlying_currency_address, bytes32),
            convert(_strike_price, bytes32),
            keccak256(_expiry_label)
        )
    )


@private
@constant
def _l_currency_balance(_currency_address: address) -> uint256:
    return ERC20(self.currencies[_currency_address].l_currency_address).balanceOf(self)


@private
def _deposit_erc20(_currency_address: address, _from: address, _to: address, _value: uint256):
    _external_call_successful: bool = ERC20(_currency_address).transferFrom(
        _from, _to, _value)
    assert _external_call_successful


@private
def _mint_and_self_authorize_erc20(_currency_address: address, _to: address, _value: uint256):
    _external_call_successful: bool = ERC20(_currency_address).mintAndAuthorizeMinter(_to, _value)
    assert _external_call_successful


@private
def _burn_as_self_authorized_erc20(_currency_address: address, _to: address, _value: uint256):
    _external_call_successful: bool = ERC20(_currency_address).burnFrom(_to, _value)
    assert _external_call_successful


@private
def _create_erc1155_type(_currency_address: address, _expiry_label: string[3]) -> uint256:
    _expiry_id: uint256 = ERC1155(_currency_address).create_token_type(0, _expiry_label)
    assert as_unitless_number(_expiry_id) == as_unitless_number(ERC1155(_currency_address).nonce()) + 1
    return _expiry_id


@private
def _mint_erc1155(_currency_address: address, _id: uint256, _to: address, _value: uint256):
    _external_call_successful: bool = ERC1155(_currency_address).mint(_id, _to, _value)
    assert _external_call_successful


@private
def _burn_erc1155(_currency_address: address, _id: uint256, _to: address, _value: uint256):
    _external_call_successful: bool = ERC1155(_currency_address).burn(_id, _to, _value)
    assert _external_call_successful


@private
def _validate_pool_type(_pool_type: uint256):
    assert _pool_type == self.POOL_TYPE_INTEREST_POOL or _pool_type == self.POOL_TYPE_UNDERWRITER_POOL, "invalid pool type"


@private
def _validate_interest_pool(_pool_address: address):
    # validate pool address
    assert _pool_address.is_contract
    assert self.interest_pools[_pool_address].is_active == True


@private
def _validate_underwriter_pool(_pool_address: address):
    # validate pool address
    assert _pool_address.is_contract
    assert self.underwriter_pools[_pool_address].is_active == True


@private
def _set_expiry_offer_status_from_interest_pool(_pool_address: address, _label: string[3], _is_active: bool):
    self._validate_interest_pool(_pool_address)
    # validate expiry
    assert self.supported_expiry[self.label_to_expiry[_label]] == True
    # set expiry status
    self.interest_pools[_pool_address].expiries_offered[_label].is_active = _is_active


@private
def _set_expiry_offer_status_from_underwriter_pool(_pool_address: address, _lend_currency_address: address, _collateral_currency_address: address, _expiry_label: string[3], _strike_price: uint256, _is_active: bool):
    self._validate_underwriter_pool(_pool_address)
    # validate expiry
    assert self.supported_expiry[self.label_to_expiry[_expiry_label]] == True
    # set expiry status
    _shield_hash: bytes32 = self._shield_hash(_lend_currency_address, _collateral_currency_address, _strike_price, _expiry_label)
    self.underwriter_pools[_pool_address].expiries_offered[_shield_hash].is_active = _is_active


@public
@constant
def shield_hash(_lend_currency_address: address, _underlying_currency_address: address, _strike_price: uint256, _expiry_label: string[3]) -> bytes32:
    return self._shield_hash(_lend_currency_address, _underlying_currency_address, _strike_price, _expiry_label)


@public
@constant
def sufi_currency_id_by_expiry(_sufi_currency_address: address, _expiry_label: string[3]) -> uint256:
    if not self.fi_offered_expiries[_sufi_currency_address][_expiry_label].has_id:
        raise("expiry id does not exist")

    return self.fi_offered_expiries[_sufi_currency_address][_expiry_label].erc1155_id


@public
@constant
def l_currency_balance(_currency_address: address) -> uint256:
    return self._l_currency_balance(_currency_address)


@public
def set_template(_label: string[64], _address: address) -> bool:
    assert msg.sender == self.owner
    self.templates[_label] = _address
    return True


@public
def set_pool_offer_registration_stat(_pool_type: uint256, _fee_multiplier: uint256,
    _minimum_fee: uint256, _fee_multiplier_decimals: uint256,
    _minimum_interval: timestamp, _last_registered_at: timestamp, _last_paid_fee: uint256
    ) -> bool:
    self._validate_pool_type(_pool_type)
    self.offer_registrations[_pool_type] = PoolOfferRegistrationStat({
        minimum_fee: _minimum_fee,
        minimum_interval: _minimum_interval,
        fee_multiplier: _fee_multiplier,
        fee_multiplier_decimals: _fee_multiplier_decimals,
        last_registered_at: _last_registered_at,
        last_paid_fee: _last_paid_fee
    })
    return True


@public
def set_currency_support(
        _currency_address: address, _is_active: bool,
        _currency_name: string[64], _currency_symbol: string[32], _currency_decimals: uint256, _supply: uint256
        ) -> bool:
    assert not _currency_address == self.protocol_currency_address
    assert msg.sender == self.owner
    assert _currency_address.is_contract
    assert self.validate_erc20_currency(_currency_address, _currency_name, _currency_symbol, _currency_decimals)
    if _is_active:
        assert self.currencies[_currency_address].pool_address == ZERO_ADDRESS, "Currency Pool already exists"
        _currency_pool_address: address = create_forwarder_to(self.templates["currency_pool"])
        _external_call_successful: bool = ContinuousCurrencyPoolERC20(_currency_pool_address).initialize(_currency_address)
        assert _external_call_successful
        # l token
        _l_currency_address: address = create_forwarder_to(self.templates["erc20"])
        _external_call_successful = ERC20(_l_currency_address).initialize(
            concat("L", slice(_currency_name, start=0, len=63)), _currency_symbol, _currency_decimals, 0)
        assert _external_call_successful
        # i token
        _i_currency_address: address = create_forwarder_to(self.templates["erc1155"])
        _external_call_successful = ERC1155(_i_currency_address).initialize()
        assert _external_call_successful
        # f token
        _f_currency_address: address = create_forwarder_to(self.templates["erc1155"])
        _external_call_successful = ERC1155(_f_currency_address).initialize()
        assert _external_call_successful

        self.currencies[_currency_address] = CurrencyStat({
            pool_address: _currency_pool_address,
            l_currency_address: _l_currency_address,
            i_currency_address: _i_currency_address,
            f_currency_address: _f_currency_address,
            is_supported: True
        })
    else:
        assert self.currencies[_currency_address].is_supported == True
        _external_call_successful: bool = ContinuousCurrencyPoolERC20(self.currencies[_currency_address].pool_address).destroy()
        assert _external_call_successful
        self.currencies[_currency_address].is_supported = False
        clear(self.currencies[_currency_address].pool_address)

    log.CurrencySupportNotification(_currency_address, convert(_is_active, uint256))
    return True


@public
def set_currency_pair_support(
        _lend_currency_address: address, _collateral_currency_address: address, _is_active: bool,
        ) -> bool:
    assert self.currencies[_lend_currency_address].is_supported, "Lend currency is not supported"
    assert self.currencies[_collateral_currency_address].is_supported, "Collateral currency is not supported"
    assert not _lend_currency_address == self.protocol_currency_address
    assert not _collateral_currency_address == self.protocol_currency_address
    assert msg.sender == self.owner
    assert _lend_currency_address.is_contract
    assert _collateral_currency_address.is_contract
    _currency_pair_hash: bytes32 = self._currency_pair_hash(_lend_currency_address, _collateral_currency_address)
    if _is_active:
        assert not self.currency_pairs[_currency_pair_hash].is_supported, "Currency Pair is already supported"
        # s token
        _s_currency_address: address = create_forwarder_to(self.templates["erc1155"])
        _external_call_successful: bool = ERC1155(_s_currency_address).initialize()
        assert _external_call_successful
        # u token
        _u_currency_address: address = create_forwarder_to(self.templates["erc1155"])
        _external_call_successful = ERC1155(_u_currency_address).initialize()
        assert _external_call_successful
        self.currency_pairs[_currency_pair_hash] = CurrencyPairStat({
            lend_currency_address: _lend_currency_address,
            collateral_currency_address: _collateral_currency_address,
            s_currency_address: _s_currency_address,
            u_currency_address: _u_currency_address,
            is_supported: True
        })
    else:
        assert self.currency_pairs[_currency_pair_hash].is_supported == True
        self.currency_pairs[_currency_pair_hash].is_supported = False

    log.CurrencyPairSupportNotification(_lend_currency_address, _collateral_currency_address, convert(_is_active, uint256))
    return True


@public
def set_su_currency_price_per_lend_currency(_lend_currency_address: address, _collateral_currency_address: address, _label: string[3], _strike_price: uint256, _price: uint256) -> bool:
    assert msg.sender == self.owner
    _shield_hash: bytes32 = self._shield_hash(_lend_currency_address, _collateral_currency_address, _strike_price, _label)
    self.su_currency_price_per_lend_currency[_shield_hash] = _price

    return True


@public
def set_expiry_support(_expiry_timestamp: timestamp, _expiry_label: string[3], _is_active: bool) -> bool:
    assert msg.sender == self.owner
    self.supported_expiry[_expiry_timestamp] = _is_active
    if not _is_active:
        assert self.expiry_to_label[_expiry_timestamp] == _expiry_label
        clear(self.expiry_to_label[_expiry_timestamp])
        clear(self.label_to_expiry[_expiry_label])
    else:
        self.expiry_to_label[_expiry_timestamp] = _expiry_label
        self.label_to_expiry[_expiry_label] = _expiry_timestamp
    log.ProtocolParameterExpiryUpdateNotification("expiry_support", _expiry_timestamp, convert(_is_active, uint256))
    return True


@public
def l_currency_from_original_currency(_currency_address: address, _value: uint256) -> bool:
    # validate currency address
    assert self.currencies[_currency_address].is_supported == True, "Currency is not supported"
    # transfer currency to currency pool
    self._deposit_erc20(_currency_address, msg.sender, self.currencies[_currency_address].pool_address, _value)
    # update supply in currency pool
    _external_call_successful: bool = ContinuousCurrencyPoolERC20(self.currencies[_currency_address].pool_address).update_total_supplied(_value)
    assert _external_call_successful
    # mint currency l_token to msg.sender
    self._mint_and_self_authorize_erc20(self.currencies[_currency_address].l_currency_address, msg.sender, _value)

    return True


# Functions that interact with Interest Pools

@public
def register_interest_pool(_currency_address: address, _name: string[62], _symbol: string[32], _initial_exchange_rate: uint256) -> bool:
    assert self.currencies[_currency_address].is_supported == True, "Currency is not supported"
    _interest_pool_address: address = create_forwarder_to(self.templates["interest_pool"])
    assert _interest_pool_address.is_contract
    _external_call_successful: bool = InterestPool(_interest_pool_address).initialize(
        msg.sender, _name, _symbol, _initial_exchange_rate, _currency_address,
        self.currencies[_currency_address].l_currency_address,
        self.currencies[_currency_address].i_currency_address,
        self.currencies[_currency_address].f_currency_address,
        self.templates["erc20"])
    assert _external_call_successful
    self.interest_pools[_interest_pool_address].name = _name
    self.interest_pools[_interest_pool_address].is_active = True

    return True


@private
@constant
def _duration_since_last_registration(_pool_type: uint256) -> uint256:
    return as_unitless_number(block.timestamp - self.offer_registrations[_pool_type].last_registered_at)


@private
@constant
def _offer_creation_fee(_pool_type: uint256) -> uint256:
    if self._duration_since_last_registration(_pool_type) >= self.offer_registrations[_pool_type].minimum_interval:
        return self.offer_registrations[_pool_type].minimum_fee
    else:
        return as_unitless_number(self.offer_registrations[_pool_type].last_paid_fee) * as_unitless_number(self.offer_registrations[_pool_type].fee_multiplier) / self.offer_registrations[_pool_type].fee_multiplier_decimals


@private
def _accept_fee_for_offer_creation(_pool_type: uint256, _from: address):
    self._validate_pool_type(_pool_type)
    _fee_amount: uint256 = self._offer_creation_fee(_pool_type)
    if as_unitless_number(_fee_amount) > 0:
        self._deposit_erc20(self.protocol_currency_address, _from, self, _fee_amount)


@public
def register_expiry_offer_from_interest_pool(_pool_operator: address, _currency_address: address, _label: string[3]) -> (bool, uint256, uint256):
    self._set_expiry_offer_status_from_interest_pool(msg.sender, _label, True)
    _f_currency_expiry_id: uint256 = self.fi_offered_expiries[self.currencies[_currency_address].f_currency_address][_label].erc1155_id
    _i_currency_expiry_id: uint256 = self.fi_offered_expiries[self.currencies[_currency_address].i_currency_address][_label].erc1155_id
    # pay lst as fee to create fi currency if it has not been created
    if not self.fi_offered_expiries[self.currencies[_currency_address].f_currency_address][_label].has_id or \
       not self.fi_offered_expiries[self.currencies[_currency_address].i_currency_address][_label].has_id:
       self._accept_fee_for_offer_creation(self.POOL_TYPE_INTEREST_POOL, _pool_operator)

    if not self.fi_offered_expiries[self.currencies[_currency_address].f_currency_address][_label].has_id:
        _f_currency_expiry_id = self._create_erc1155_type(self.currencies[_currency_address].f_currency_address, _label)
        self.fi_offered_expiries[self.currencies[_currency_address].f_currency_address][_label] = SUFITokenOfferedExpiryStat({
            has_id: True,
            erc1155_id: _f_currency_expiry_id
        })
    if not self.fi_offered_expiries[self.currencies[_currency_address].i_currency_address][_label].has_id:
        _i_currency_expiry_id = self._create_erc1155_type(self.currencies[_currency_address].i_currency_address, _label)
        self.fi_offered_expiries[self.currencies[_currency_address].i_currency_address][_label] = SUFITokenOfferedExpiryStat({
            has_id: True,
            erc1155_id: _i_currency_expiry_id
        })

    return True, _f_currency_expiry_id, _i_currency_expiry_id


@public
def remove_expiry_offer_from_interest_pool(_label: string[3]) -> bool:
    self._set_expiry_offer_status_from_interest_pool(msg.sender, _label, False)

    return True


@public
def deposit_l_tokens_to_interest_pool(_currency_address: address, _from: address, _value: uint256) -> bool:
    self._validate_interest_pool(msg.sender)
    assert self.currencies[_currency_address].is_supported == True
    self._deposit_erc20(self.currencies[_currency_address].l_currency_address, _from, msg.sender, _value)

    return True


@public
def l_currency_to_i_and_f_currency(_currency_address: address, _expiry_label: string[3], _value: uint256) -> bool:
    # validate i token type exists for expiry
    assert self.fi_offered_expiries[self.currencies[_currency_address].i_currency_address][_expiry_label].has_id
    # validate interest_pool
    self._validate_interest_pool(msg.sender)
    # validate _currency_address
    assert self.currencies[_currency_address].is_supported == True
    # burn l_token from interest_pool account
    self._burn_as_self_authorized_erc20(self.currencies[_currency_address].l_currency_address, msg.sender, _value)
    # mint i_token into interest_pool account
    self._mint_erc1155(
        self.currencies[_currency_address].i_currency_address,
        self.fi_offered_expiries[self.currencies[_currency_address].i_currency_address][_expiry_label].erc1155_id,
        msg.sender,
        _value
    )
    self._mint_erc1155(
        self.currencies[_currency_address].f_currency_address,
        self.fi_offered_expiries[self.currencies[_currency_address].f_currency_address][_expiry_label].erc1155_id,
        msg.sender,
        _value
    )
    return True


@public
def l_currency_from_i_and_f_currency(_currency_address: address, _expiry_label: string[3], _value: uint256) -> bool:
    # validate i token type exists for expiry
    assert self.fi_offered_expiries[self.currencies[_currency_address].f_currency_address][_expiry_label].has_id
    assert self.fi_offered_expiries[self.currencies[_currency_address].i_currency_address][_expiry_label].has_id
    # validate interest_pool
    self._validate_interest_pool(msg.sender)
    # validate _currency_address
    assert self.currencies[_currency_address].is_supported == True
    # burn l_token from interest_pool account
    self._mint_and_self_authorize_erc20(self.currencies[_currency_address].l_currency_address, msg.sender, _value)
    # mint i_token into interest_pool account
    self._burn_erc1155(
        self.currencies[_currency_address].i_currency_address,
        self.fi_offered_expiries[self.currencies[_currency_address].i_currency_address][_expiry_label].erc1155_id,
        msg.sender,
        _value
    )
    self._burn_erc1155(
        self.currencies[_currency_address].f_currency_address,
        self.fi_offered_expiries[self.currencies[_currency_address].f_currency_address][_expiry_label].erc1155_id,
        msg.sender,
        _value
    )
    return True


# Functions that interact with Underwriter Pools

@public
def register_underwriter_pool(_lend_currency_address: address, _collateral_currency_address: address, _name: string[62], _symbol: string[32], _initial_exchange_rate: uint256) -> bool:
    assert self.currencies[_lend_currency_address].is_supported == True, "Lend currency is not supported"
    assert self.currencies[_collateral_currency_address].is_supported == True, "Collateral currency is not supported"
    # deploy underwriter pool contract
    _underwriter_pool_address: address = create_forwarder_to(self.templates["underwriter_pool"])
    assert _underwriter_pool_address.is_contract
    _currency_pair_hash: bytes32 = self._currency_pair_hash(_lend_currency_address, _collateral_currency_address)
    # create currency pair if does not exist
    assert self.currency_pairs[_currency_pair_hash].is_supported, "Currency pair is not supported"
    _external_call_successful: bool = UnderwriterPool(_underwriter_pool_address).initialize(
        msg.sender, _name, _symbol, _initial_exchange_rate,
        _lend_currency_address, _collateral_currency_address,
        self.currencies[_lend_currency_address].l_currency_address,
        self.currencies[_lend_currency_address].i_currency_address,
        self.currency_pairs[_currency_pair_hash].s_currency_address,
        self.currency_pairs[_currency_pair_hash].u_currency_address,
        self.templates["erc20"])
    assert _external_call_successful
    self.underwriter_pools[_underwriter_pool_address].name = _name
    self.underwriter_pools[_underwriter_pool_address].is_active = True

    return True


@public
def register_expiry_offer_from_underwriter_pool(_lend_currency_address: address, _collateral_currency_address: address, _label: string[3], _strike_price: uint256) -> (bool, uint256, uint256, uint256):
    self._set_expiry_offer_status_from_underwriter_pool(msg.sender, _lend_currency_address, _collateral_currency_address, _label, _strike_price, True)
    # assert i token of lend currency exists
    _currency_pair_hash: bytes32 = self._currency_pair_hash(_lend_currency_address, _collateral_currency_address)
    _shield_hash: bytes32 = self._shield_hash(_lend_currency_address, _collateral_currency_address, _strike_price, _label)
    _s_currency_expiry_id: uint256 = self.su_offered_expiries[self.currency_pairs[_currency_pair_hash].s_currency_address][_shield_hash].erc1155_id
    _u_currency_expiry_id: uint256 = self.su_offered_expiries[self.currency_pairs[_currency_pair_hash].u_currency_address][_shield_hash].erc1155_id
    _i_currency_expiry_id: uint256 = self.fi_offered_expiries[self.currencies[_lend_currency_address].i_currency_address][_label].erc1155_id
    if not self.su_offered_expiries[self.currency_pairs[_currency_pair_hash].s_currency_address][_shield_hash].has_id:
        _s_currency_expiry_id = self._create_erc1155_type(self.currency_pairs[_currency_pair_hash].s_currency_address, _label)
        self.su_offered_expiries[self.currency_pairs[_currency_pair_hash].s_currency_address][_shield_hash] = SUFITokenOfferedExpiryStat({
            has_id: True,
            erc1155_id: _s_currency_expiry_id
        })
    if not self.su_offered_expiries[self.currency_pairs[_currency_pair_hash].u_currency_address][_shield_hash].has_id:
        _u_currency_expiry_id = self._create_erc1155_type(self.currency_pairs[_currency_pair_hash].u_currency_address, _label)
        self.su_offered_expiries[self.currency_pairs[_currency_pair_hash].u_currency_address][_shield_hash] = SUFITokenOfferedExpiryStat({
            has_id: True,
            erc1155_id: _u_currency_expiry_id
        })
    if not self.fi_offered_expiries[self.currencies[_lend_currency_address].i_currency_address][_label].has_id:
        _i_currency_expiry_id = self._create_erc1155_type(self.currencies[_lend_currency_address].i_currency_address, _label)
        self.fi_offered_expiries[self.currencies[_lend_currency_address].i_currency_address][_label] = SUFITokenOfferedExpiryStat({
            has_id: True,
            erc1155_id: _i_currency_expiry_id
        })

    return True, _s_currency_expiry_id, _u_currency_expiry_id, _i_currency_expiry_id


@public
def remove_expiry_offer_from_underwriter_pool(_lend_currency_address: address, _collateral_currency_address: address, _expiry_label: string[3], _strike_price: uint256) -> bool:
    self._set_expiry_offer_status_from_underwriter_pool(msg.sender, _lend_currency_address, _collateral_currency_address, _expiry_label, _strike_price, False)

    return True


@public
def deposit_l_tokens_to_underwriter_pool(_currency_address: address, _from: address, _value: uint256) -> bool:
    self._validate_underwriter_pool(msg.sender)
    assert self.currencies[_currency_address].is_supported == True
    self._deposit_erc20(self.currencies[_currency_address].l_currency_address, _from, msg.sender, _value)

    return True


@public
def l_currency_to_i_and_s_and_u_currency(_lend_currency_address: address, _collateral_currency_address: address, _expiry_label: string[3], _strike_price: uint256, _value: uint256) -> bool:
    # validate i token type exists for expiry
    assert self.fi_offered_expiries[self.currencies[_lend_currency_address].i_currency_address][_expiry_label].has_id
    # validate s and u token types exist for currency pair
    _currency_pair_hash: bytes32 = self._currency_pair_hash(_lend_currency_address, _collateral_currency_address)
    _shield_hash: bytes32 = self._shield_hash(_lend_currency_address, _collateral_currency_address, _strike_price, _expiry_label)
    assert self.su_offered_expiries[self.currency_pairs[_currency_pair_hash].s_currency_address][_shield_hash].has_id
    assert self.su_offered_expiries[self.currency_pairs[_currency_pair_hash].u_currency_address][_shield_hash].has_id
    # validate interest_pool
    self._validate_underwriter_pool(msg.sender)
    # validate _lend_currency_address
    assert self.currencies[_lend_currency_address].is_supported == True
    # validate _collateral_currency_address
    assert self.currencies[_collateral_currency_address].is_supported == True
    # burn l_token from interest_pool account
    self._burn_as_self_authorized_erc20(self.currencies[_lend_currency_address].l_currency_address, msg.sender, _value)
    # calculate su currency quantitites to be minted
    assert not as_unitless_number(self.su_currency_price_per_lend_currency[_shield_hash]) == 0, "SU currency price per lend currency has not been set"
    _su_currencies_to_mint: uint256 = as_unitless_number(_value) / as_unitless_number(self.su_currency_price_per_lend_currency[_shield_hash])
    # mint i_token into interest_pool account
    self._mint_erc1155(
        self.currencies[_lend_currency_address].i_currency_address,
        self.fi_offered_expiries[self.currencies[_lend_currency_address].i_currency_address][_expiry_label].erc1155_id,
        msg.sender,
        _value
    )
    self._mint_erc1155(
        self.currency_pairs[_currency_pair_hash].s_currency_address,
        self.su_offered_expiries[self.currency_pairs[_currency_pair_hash].s_currency_address][_shield_hash].erc1155_id,
        msg.sender,
        _su_currencies_to_mint
    )
    self._mint_erc1155(
        self.currency_pairs[_currency_pair_hash].u_currency_address,
        self.su_offered_expiries[self.currency_pairs[_currency_pair_hash].u_currency_address][_shield_hash].erc1155_id,
        msg.sender,
        _su_currencies_to_mint
    )
    return True


@public
def l_currency_from_i_and_s_and_u_currency(_lend_currency_address: address, _collateral_currency_address: address, _expiry_label: string[3], _strike_price: uint256, _value: uint256) -> bool:
    # validate i token type exists for expiry
    assert self.fi_offered_expiries[self.currencies[_lend_currency_address].i_currency_address][_expiry_label].has_id
    # validate s and u token types exist for currency pair
    _currency_pair_hash: bytes32 = self._currency_pair_hash(_lend_currency_address, _collateral_currency_address)
    _shield_hash: bytes32 = self._shield_hash(_lend_currency_address, _collateral_currency_address, _strike_price, _expiry_label)
    assert self.su_offered_expiries[self.currency_pairs[_currency_pair_hash].s_currency_address][_shield_hash].has_id
    assert self.su_offered_expiries[self.currency_pairs[_currency_pair_hash].u_currency_address][_shield_hash].has_id
    # validate underwriter_pool
    self._validate_underwriter_pool(msg.sender)
    # validate _lend_currency_address
    assert self.currencies[_lend_currency_address].is_supported == True
    # validate _collateral_currency_address
    assert self.currencies[_collateral_currency_address].is_supported == True
    # burn l_token from interest_pool account
    self._mint_and_self_authorize_erc20(self.currencies[_lend_currency_address].l_currency_address, msg.sender, _value)
    # calculate su currency quantitites to be minted
    assert not as_unitless_number(self.su_currency_price_per_lend_currency[_shield_hash]) == 0, "SU currency price per lend currency has not been set"
    _su_currencies_to_burn: uint256 = as_unitless_number(_value) / as_unitless_number(self.su_currency_price_per_lend_currency[_shield_hash])
    # mint i_token into interest_pool account
    self._burn_erc1155(
        self.currencies[_lend_currency_address].i_currency_address,
        self.fi_offered_expiries[self.currencies[_lend_currency_address].i_currency_address][_expiry_label].erc1155_id,
        msg.sender,
        _value
    )
    self._burn_erc1155(
        self.currency_pairs[_currency_pair_hash].s_currency_address,
        self.su_offered_expiries[self.currency_pairs[_currency_pair_hash].s_currency_address][_shield_hash].erc1155_id,
        msg.sender,
        _su_currencies_to_burn
    )
    self._burn_erc1155(
        self.currency_pairs[_currency_pair_hash].u_currency_address,
        self.su_offered_expiries[self.currency_pairs[_currency_pair_hash].u_currency_address][_shield_hash].erc1155_id,
        msg.sender,
        _su_currencies_to_burn
    )

    return True
