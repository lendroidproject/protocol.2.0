# Vyper version of the Lendroid protocol v2
# THIS CONTRACT HAS NOT BEEN AUDITED!


from contracts.interfaces import ERC20
from contracts.interfaces import ERC1155
from contracts.interfaces import ContinuousCurrencyPoolERC20
from contracts.interfaces import InterestPool


# Structs
struct CurrencyStat:
    pool_address: address
    l_token_address: address
    i_token_address: address
    f_token_address: address
    s_token_address: address
    u_token_address: address
    is_supported: bool


struct SUFITokenOfferedExpiryStat:
    has_id: bool
    erc1155_id: uint256


struct InterestPoolExpiryStat:
    is_active: bool
    has_id: bool
    erc1155_id: uint256


struct InterestPoolStat:
    name: string[64]
    is_active: bool
    expiries_offered: map(string[3], InterestPoolExpiryStat)


struct LoanMarketStat:
    lend_currency_address: address
    expiry: timestamp
    market_address: address

# Events of the protocol.
ProtocolParameterAddressUpdateNotification: event({_notification_key: indexed(string[64]), _address: indexed(address), _notification_value: uint256})
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
loan_markets: public(map(bytes32, LoanMarketStat))
currencies: public(map(address, CurrencyStat))
interest_pools: public(map(address, InterestPoolStat))
sufi_token_offered_expiries: public(map(address, map(string[3], SUFITokenOfferedExpiryStat)))


@public
def __init__(_protocol_currency_address: address):
    self.owner = msg.sender
    self.protocol_currency_address = _protocol_currency_address
    # after init, need to set the following template addresses:
    #. currency_pool_template
    #. ERC20_template
    #. ERC1155_template
    #. InterestPool_template


@private
@constant
def validate_erc20_currency(_currency_address: address,
        _name: string[64], _symbol: string[32], _decimals: uint256) -> bool:
    assert ERC20(_currency_address).name() == _name
    assert ERC20(_currency_address).symbol() == _symbol
    assert ERC20(_currency_address).decimals() == _decimals
    return True


@private
def _l_token_balance(_currency_address: address) -> uint256:
    return ERC20(self.currencies[_currency_address].l_token_address).balanceOf(self)


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
def _validate_interest_pool(_interest_pool_address: address):
    # validate interest pool address
    assert _interest_pool_address.is_contract
    assert self.interest_pools[_interest_pool_address].is_active == True


@private
def _set_expiry_offer_status_from_interest_pool(_interest_pool_address: address, _label: string[3], _is_active: bool):
    self._validate_interest_pool(_interest_pool_address)
    # validate expiry
    assert self.supported_expiry[self.label_to_expiry[_label]] == True
    # set expiry status
    self.interest_pools[_interest_pool_address].expiries_offered[_label].is_active = _is_active


@public
@constant
def sufi_currency_id_by_expiry(_sufi_currency_address: address, _expiry_label: string[3]) -> uint256:
    if not self.sufi_token_offered_expiries[_sufi_currency_address][_expiry_label].has_id:
        raise("expiry id does not exist")

    return self.sufi_token_offered_expiries[_sufi_currency_address][_expiry_label].erc1155_id


@public
def set_template(_label: string[64], _address: address) -> bool:
    assert msg.sender == self.owner
    self.templates[_label] = _address
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
        _l_token_address: address = create_forwarder_to(self.templates["erc20"])
        _external_call_successful = ERC20(_l_token_address).initialize(
            concat("L", slice(_currency_name, start=0, len=63)), _currency_symbol, _currency_decimals, 0)
        assert _external_call_successful
        # i token
        _i_token_address: address = create_forwarder_to(self.templates["erc1155"])
        _external_call_successful = ERC1155(_i_token_address).initialize()
        assert _external_call_successful
        # f token
        _f_token_address: address = create_forwarder_to(self.templates["erc1155"])
        _external_call_successful = ERC1155(_f_token_address).initialize()
        assert _external_call_successful
        # s token
        _s_token_address: address = create_forwarder_to(self.templates["erc1155"])
        _external_call_successful = ERC1155(_s_token_address).initialize()
        assert _external_call_successful
        # u token
        _u_token_address: address = create_forwarder_to(self.templates["erc1155"])
        _external_call_successful = ERC1155(_u_token_address).initialize()
        assert _external_call_successful
        self.currencies[_currency_address] = CurrencyStat({
            pool_address: _currency_pool_address,
            l_token_address: _l_token_address,
            i_token_address: _i_token_address,
            f_token_address: _f_token_address,
            s_token_address: _s_token_address,
            u_token_address: _u_token_address,
            is_supported: True
        })
    else:
        assert self.currencies[_currency_address].is_supported == True
        _external_call_successful: bool = ContinuousCurrencyPoolERC20(self.currencies[_currency_address].pool_address).destroy()
        assert _external_call_successful
        self.currencies[_currency_address].is_supported = False
        clear(self.currencies[_currency_address].pool_address)

    log.ProtocolParameterAddressUpdateNotification("currency_support", _currency_address, convert(_is_active, uint256))
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
    self._mint_and_self_authorize_erc20(self.currencies[_currency_address].l_token_address, msg.sender, _value)

    return True


@public
def register_interest_pool(_currency_address: address, _name: string[62], _symbol: string[32], _initial_exchange_rate: uint256) -> bool:
    assert self.currencies[_currency_address].is_supported == True, "Currency is not supported"
    _interest_pool_address: address = create_forwarder_to(self.templates["interest_pool"])
    assert _interest_pool_address.is_contract
    _external_call_successful: bool = InterestPool(_interest_pool_address).initialize(
        msg.sender, _name, _symbol, _initial_exchange_rate, _currency_address,
        self.currencies[_currency_address].l_token_address,
        self.currencies[_currency_address].i_token_address,
        self.currencies[_currency_address].f_token_address,
        self.templates["erc20"])
    assert _external_call_successful
    self.interest_pools[_interest_pool_address].name = _name
    self.interest_pools[_interest_pool_address].is_active = True

    return True


@public
def register_expiry_offer_from_interest_pool(_currency_address: address, _label: string[3]) -> (bool, uint256, uint256):
    self._set_expiry_offer_status_from_interest_pool(msg.sender, _label, True)
    # _s_token_expiry_id: uint256 = self.sufi_token_offered_expiries[self.currencies[_currency_address].s_token_address][_label].erc1155_id
    # _u_token_expiry_id: uint256 = self.sufi_token_offered_expiries[self.currencies[_currency_address].u_token_address][_label].erc1155_id
    _f_token_expiry_id: uint256 = self.sufi_token_offered_expiries[self.currencies[_currency_address].f_token_address][_label].erc1155_id
    _i_token_expiry_id: uint256 = self.sufi_token_offered_expiries[self.currencies[_currency_address].i_token_address][_label].erc1155_id
    # if not self.sufi_token_offered_expiries[self.currencies[_currency_address].s_token_address][_label].has_id:
    #     _s_token_expiry_id = self._create_erc1155_type(self.currencies[_currency_address].s_token_address, _label)
    # if not self.sufi_token_offered_expiries[self.currencies[_currency_address].u_token_address][_label].has_id:
    #     _u_token_expiry_id = self._create_erc1155_type(self.currencies[_currency_address].u_token_address, _label)
    if not self.sufi_token_offered_expiries[self.currencies[_currency_address].f_token_address][_label].has_id:
        _f_token_expiry_id = self._create_erc1155_type(self.currencies[_currency_address].f_token_address, _label)
    if not self.sufi_token_offered_expiries[self.currencies[_currency_address].i_token_address][_label].has_id:
        _i_token_expiry_id = self._create_erc1155_type(self.currencies[_currency_address].i_token_address, _label)

    # self.sufi_token_offered_expiries[self.currencies[_currency_address].s_token_address][_label] = SUFITokenOfferedExpiryStat({
    #     has_id: True,
    #     erc1155_id: _s_token_expiry_id
    # })
    # self.sufi_token_offered_expiries[self.currencies[_currency_address].u_token_address][_label] = SUFITokenOfferedExpiryStat({
    #     has_id: True,
    #     erc1155_id: _u_token_expiry_id
    # })
    self.sufi_token_offered_expiries[self.currencies[_currency_address].f_token_address][_label] = SUFITokenOfferedExpiryStat({
        has_id: True,
        erc1155_id: _f_token_expiry_id
    })
    self.sufi_token_offered_expiries[self.currencies[_currency_address].i_token_address][_label] = SUFITokenOfferedExpiryStat({
        has_id: True,
        erc1155_id: _i_token_expiry_id
    })

    return True, _f_token_expiry_id, _i_token_expiry_id


@public
def remove_expiry_offer_from_interest_pool(_currency_address: address, _label: string[3]) -> bool:
    self._set_expiry_offer_status_from_interest_pool(msg.sender, _label, False)

    return True


@public
def l_token_balance(_currency_address: address) -> uint256:
    return self._l_token_balance(_currency_address)


@public
def deposit_l_tokens_to_interest_pool(_currency_address: address, _from: address, _value: uint256) -> bool:
    self._validate_interest_pool(msg.sender)
    assert self.currencies[_currency_address].is_supported == True
    self._deposit_erc20(self.currencies[_currency_address].l_token_address, _from, msg.sender, _value)

    return True


@public
def l_currency_to_i_and_f_currency(_currency_address: address, _expiry_label: string[3], _value: uint256) -> bool:
    # validate i token type exists for expiry
    assert self.sufi_token_offered_expiries[self.currencies[_currency_address].i_token_address][_expiry_label].has_id
    # validate interest_pool
    self._validate_interest_pool(msg.sender)
    # validate _currency_address
    assert self.currencies[_currency_address].is_supported == True
    # burn l_token from interest_pool account
    self._burn_as_self_authorized_erc20(self.currencies[_currency_address].l_token_address, msg.sender, _value)
    # mint i_token into interest_pool account
    self._mint_erc1155(
        self.currencies[_currency_address].i_token_address,
        self.sufi_token_offered_expiries[self.currencies[_currency_address].i_token_address][_expiry_label].erc1155_id,
        msg.sender,
        _value
    )
    self._mint_erc1155(
        self.currencies[_currency_address].f_token_address,
        self.sufi_token_offered_expiries[self.currencies[_currency_address].f_token_address][_expiry_label].erc1155_id,
        msg.sender,
        _value
    )
    return True


@public
def l_currency_from_i_and_f_currency(_currency_address: address, _expiry_label: string[3], _value: uint256) -> bool:
    # validate i token type exists for expiry
    assert self.sufi_token_offered_expiries[self.currencies[_currency_address].i_token_address][_expiry_label].has_id
    # validate interest_pool
    self._validate_interest_pool(msg.sender)
    # validate _currency_address
    assert self.currencies[_currency_address].is_supported == True
    # burn l_token from interest_pool account
    self._mint_and_self_authorize_erc20(self.currencies[_currency_address].l_token_address, msg.sender, _value)
    # mint i_token into interest_pool account
    self._burn_erc1155(
        self.currencies[_currency_address].i_token_address,
        self.sufi_token_offered_expiries[self.currencies[_currency_address].i_token_address][_expiry_label].erc1155_id,
        msg.sender,
        _value
    )
    self._burn_erc1155(
        self.currencies[_currency_address].f_token_address,
        self.sufi_token_offered_expiries[self.currencies[_currency_address].f_token_address][_expiry_label].erc1155_id,
        msg.sender,
        _value
    )
    return True
