# Functions

@public
def initialize(_owner: address, _protocol_currency_address: address, _dao_address_currency: address, _dao_address_interest_pool: address, _dao_address_underwriter_pool: address, _dao_address_shield_payout: address, _dao_address_collateral_auction: address, _registry_address_position: address) -> bool:
    pass

@constant
@public
def shield_payout(_currency_address: address, _expiry: uint256(sec, positional), _underlying_address: address, _strike_price: uint256) -> uint256:
    pass

@constant
@public
def underwriter_payout(_currency_address: address, _expiry: uint256(sec, positional), _underlying_address: address, _strike_price: uint256) -> uint256:
    pass

@public
def setShouldReject(_value: bool):
    pass

@constant
@public
def supportsInterface(interfaceID: bytes[10]) -> bool:
    pass

@public
def onERC1155Received(_operator: address, _from: address, _id: uint256, _value: uint256, _data: bytes32) -> bytes[10]:
    pass

@public
def onERC1155BatchReceived(_operator: address, _from: address, _ids: uint256[5], _values: uint256[5], _data: bytes32) -> bytes[10]:
    pass

@constant
@public
def loan_market_hash(_currency_address: address, _expiry: uint256(sec, positional), _underlying_address: address) -> bytes32:
    pass

@constant
@public
def currency_underlying_pair_hash(_currency_address: address, _underlying_address: address) -> bytes32:
    pass

@public
def open_shield_market(_currency_address: address, _expiry: uint256(sec, positional), _underlying_address: address, _strike_price: uint256, _s_hash: bytes32, _s_parent_address: address, _s_id: uint256, _u_hash: bytes32, _u_parent_address: address, _u_id: uint256) -> bool:
    pass

@public
def settle_loan_market(_loan_market_hash: bytes32):
    pass

@public
def set_registry(_registry_type: uint256, _address: address) -> bool:
    pass

@public
def set_price_oracle(_currency_address: address, _underlying_address: address, _price_oracle_address: address) -> bool:
    pass

@public
def secure_currency_deposit_and_market_update_from_auction_purchase(_currency_address: address, _expiry: uint256(sec, positional), _underlying_address: address, _purchaser: address, _currency_value: uint256, _underlying_value: uint256, _is_auction_active: bool) -> bool:
    pass

@public
def open_position(_borrower: address, _currency_value: uint256, _currency_address: address, _expiry: uint256(sec, positional), _underlying_address: address, _strike_price: uint256) -> bool:
    pass

@public
def close_position(_borrower: address, _currency_value: uint256, _currency_address: address, _expiry: uint256(sec, positional), _underlying_address: address, _strike_price: uint256) -> bool:
    pass

@public
def close_liquidated_position(_borrower: address, _currency_value: uint256, _currency_address: address, _expiry: uint256(sec, positional), _underlying_address: address, _strike_price: uint256) -> bool:
    pass

@constant
@public
def protocol_currency_address() -> address:
    pass

@constant
@public
def protocol_dao_address() -> address:
    pass

@constant
@public
def owner() -> address:
    pass

@constant
@public
def daos(arg0: uint256) -> address:
    pass

@constant
@public
def registries(arg0: uint256) -> address:
    pass

@constant
@public
def expiry_markets__expiry(arg0: uint256(sec, positional)) -> uint256(sec, positional):
    pass

@constant
@public
def expiry_markets__id(arg0: uint256(sec, positional)) -> uint256:
    pass

@constant
@public
def last_expiry_market_index() -> uint256:
    pass

@constant
@public
def expiry_market_id_to_timestamp(arg0: uint256) -> uint256(sec, positional):
    pass

@constant
@public
def loan_markets__currency_address(arg0: bytes32) -> address:
    pass

@constant
@public
def loan_markets__expiry(arg0: bytes32) -> uint256(sec, positional):
    pass

@constant
@public
def loan_markets__underlying_address(arg0: bytes32) -> address:
    pass

@constant
@public
def loan_markets__currency_value_per_underlying_at_expiry(arg0: bytes32) -> uint256:
    pass

@constant
@public
def loan_markets__status(arg0: bytes32) -> uint256:
    pass

@constant
@public
def loan_markets__total_outstanding_currency_value_at_expiry(arg0: bytes32) -> uint256:
    pass

@constant
@public
def loan_markets__total_outstanding_underlying_value_at_expiry(arg0: bytes32) -> uint256:
    pass

@constant
@public
def loan_markets__collateral_auction_graph_address(arg0: bytes32) -> address:
    pass

@constant
@public
def loan_markets__total_currency_raised_during_auction(arg0: bytes32) -> uint256:
    pass

@constant
@public
def loan_markets__total_underlying_sold_during_auction(arg0: bytes32) -> uint256:
    pass

@constant
@public
def loan_markets__underlying_settlement_price_per_currency(arg0: bytes32) -> uint256:
    pass

@constant
@public
def loan_markets__shield_market_count(arg0: bytes32) -> uint256:
    pass

@constant
@public
def loan_markets__hash(arg0: bytes32) -> bytes32:
    pass

@constant
@public
def loan_markets__id(arg0: bytes32) -> uint256:
    pass

@constant
@public
def last_loan_market_index(arg0: uint256(sec, positional)) -> uint256:
    pass

@constant
@public
def loan_market_id_to_hash(arg0: uint256(sec, positional), arg1: uint256) -> bytes32:
    pass

@constant
@public
def shield_markets__currency_address(arg0: bytes32) -> address:
    pass

@constant
@public
def shield_markets__expiry(arg0: bytes32) -> uint256(sec, positional):
    pass

@constant
@public
def shield_markets__underlying_address(arg0: bytes32) -> address:
    pass

@constant
@public
def shield_markets__strike_price(arg0: bytes32) -> uint256:
    pass

@constant
@public
def shield_markets__s_hash(arg0: bytes32) -> bytes32:
    pass

@constant
@public
def shield_markets__s_parent_address(arg0: bytes32) -> address:
    pass

@constant
@public
def shield_markets__s_token_id(arg0: bytes32) -> uint256:
    pass

@constant
@public
def shield_markets__u_hash(arg0: bytes32) -> bytes32:
    pass

@constant
@public
def shield_markets__u_parent_address(arg0: bytes32) -> address:
    pass

@constant
@public
def shield_markets__u_token_id(arg0: bytes32) -> uint256:
    pass

@constant
@public
def shield_markets__hash(arg0: bytes32) -> bytes32:
    pass

@constant
@public
def shield_markets__id(arg0: bytes32) -> uint256:
    pass

@constant
@public
def last_shield_market_index(arg0: uint256(sec, positional)) -> uint256:
    pass

@constant
@public
def shield_market_id_to_hash(arg0: uint256(sec, positional), arg1: uint256) -> bytes32:
    pass

@constant
@public
def price_oracles(arg0: bytes32) -> address:
    pass

@constant
@public
def REGISTRY_TYPE_POSITION() -> uint256:
    pass

@constant
@public
def DAO_TYPE_CURRENCY() -> uint256:
    pass

@constant
@public
def DAO_TYPE_INTEREST_POOL() -> uint256:
    pass

@constant
@public
def DAO_TYPE_UNDERWRITER_POOL() -> uint256:
    pass

@constant
@public
def DAO_TYPE_SHIELD_PAYOUT() -> uint256:
    pass

@constant
@public
def DAO_TYPE_COLLATERAL_AUCION() -> uint256:
    pass

@constant
@public
def LOAN_MARKET_STATUS_OPEN() -> uint256:
    pass

@constant
@public
def LOAN_MARKET_STATUS_SETTLING() -> uint256:
    pass

@constant
@public
def LOAN_MARKET_STATUS_CLOSED() -> uint256:
    pass

@constant
@public
def shouldReject() -> bool:
    pass

@constant
@public
def lastData() -> bytes32:
    pass

@constant
@public
def lastOperator() -> address:
    pass

@constant
@public
def lastFrom() -> address:
    pass

@constant
@public
def lastId() -> uint256:
    pass

@constant
@public
def lastValue() -> uint256:
    pass

@constant
@public
def initialized() -> bool:
    pass
