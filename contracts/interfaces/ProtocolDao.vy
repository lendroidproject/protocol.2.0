# Events

DAOInitialized: event({_setter: address, _dao_type: int128, _dao_address: address})
RegistryInitialized: event({_setter: address, _template_type: int128, _registry_address: address})
TemplateSettingsUpdated: event({_setter: address, _template_type: int128, _template_address: address})
AuthorizedCallerUpdated: event({_caller_type: int128, _caller: address, _authorized_caller: address})
SystemSettingsUpdated: event({_setter: address})

# Functions

@public
def change_governor(_address: address) -> bool:
    pass

@public
def change_escape_hatch_manager(_address: address) -> bool:
    pass

@public
def change_escape_hatch_token_holder(_address: address) -> bool:
    pass

@public
def initialize_pool_name_registry(_pool_name_registration_minimum_stake: uint256) -> bool:
    pass

@public
def initialize_position_registry() -> bool:
    pass

@public
def initialize_currency_dao() -> bool:
    pass

@public
def initialize_interest_pool_dao() -> bool:
    pass

@public
def initialize_underwriter_pool_dao() -> bool:
    pass

@public
def initialize_market_dao() -> bool:
    pass

@public
def initialize_shield_payout_dao() -> bool:
    pass

@public
def activate_public_contributions() -> bool:
    pass

@public
def activate_non_standard_expiries() -> bool:
    pass

@public
def set_expiry_support(_timestamp: uint256(sec, positional), _label: string[3], _is_active: bool) -> bool:
    pass

@public
def set_registry(_dao_type: int128, _registry_type: uint256, _address: address) -> bool:
    pass

@public
def set_template(_template_type: int128, _address: address) -> bool:
    pass

@public
def set_pool_name_registration_minimum_stake(_value: uint256) -> bool:
    pass

@public
def set_pool_name_registration_stake_lookup(_name_length: int128, _value: uint256) -> bool:
    pass

@public
def set_token_support(_token: address, _is_active: bool) -> bool:
    pass

@public
def set_minimum_mft_fee(_dao_type: int128, _value: uint256) -> bool:
    pass

@public
def set_fee_multiplier_per_mft_count(_dao_type: int128, _mft_count: uint256, _value: uint256) -> bool:
    pass

@public
def set_maximum_mft_support_count(_dao_type: int128, _value: uint256) -> bool:
    pass

@public
def set_price_oracle(_currency: address, _underlying: address, _oracle: address) -> bool:
    pass

@public
def set_maximum_liability_for_currency_market(_currency: address, _expiry: uint256(sec, positional), _value: uint256) -> bool:
    pass

@public
def set_maximum_liability_for_loan_market(_currency: address, _expiry: uint256(sec, positional), _underlying: address, _value: uint256) -> bool:
    pass

@public
def set_auction_slippage_percentage(_value: uint256) -> bool:
    pass

@public
def set_auction_maximum_discount_percentage(_value: uint256) -> bool:
    pass

@public
def set_auction_discount_duration(_value: uint256(sec)) -> bool:
    pass

@public
def toggle_dao_pause(_dao_type: int128, _pause: bool) -> bool:
    pass

@public
def toggle_registry_pause(_registry_type: int128, _pause: bool) -> bool:
    pass

@public
def escape_hatch_dao_erc20(_dao_type: int128, _currency: address, _is_l: bool) -> bool:
    pass

@public
def escape_hatch_registry_erc20(_registry_type: int128, _currency: address) -> bool:
    pass

@public
def escape_hatch_dao_mft(_dao_type: int128, _mft_type: int128, _currency: address, _expiry: uint256(sec, positional), _underlying: address, _strike_price: uint256) -> bool:
    pass

@public
def escape_hatch_auction(_currency: address, _expiry: uint256(sec, positional), _underlying: address) -> bool:
    pass

@constant
@public
def LST() -> address:
    pass

@constant
@public
def authorized_callers(arg0: int128) -> address:
    pass

@constant
@public
def daos(arg0: int128) -> address:
    pass

@constant
@public
def registries(arg0: int128) -> address:
    pass

@constant
@public
def expiries__expiry_timestamp(arg0: uint256(sec, positional)) -> uint256(sec, positional):
    pass

@constant
@public
def expiries__expiry_label(arg0: uint256(sec, positional)) -> string[3]:
    pass

@constant
@public
def expiries__is_active(arg0: uint256(sec, positional)) -> bool:
    pass

@constant
@public
def templates(arg0: int128) -> address:
    pass

@constant
@public
def public_contributions_activated() -> bool:
    pass

@constant
@public
def non_standard_expiries_activated() -> bool:
    pass

@constant
@public
def initialized() -> bool:
    pass
