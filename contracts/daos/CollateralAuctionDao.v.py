# Vyper version of the Lendroid protocol v2
# THIS CONTRACT HAS NOT BEEN AUDITED!


from contracts.interfaces import CollateralAuctionGraph


protocol_currency_address: public(address)
protocol_dao_address: public(address)
owner: public(address)
# dao_type => dao_address
daos: public(map(uint256, address))
# template_name => template_contract_address
templates: public(map(uint256, address))
# loan_market_hash => graph_address
graphs: public(map(bytes32, address))

DAO_TYPE_MARKET: public(uint256)

TEMPLATE_TYPE_COLLATERAL_AUCTION_ERC20: public(uint256)

initialized: public(bool)


@private
@constant
def _is_initialized() -> bool:
    return self.initialized == True


@public
def initialize(
        _owner: address,
        _protocol_currency_address: address,
        _dao_address_market: address,
        _template_address_collateral_auction_erc20: address
        ) -> bool:
    assert not self._is_initialized()
    self.initialized = True
    self.owner = _owner
    self.protocol_dao_address = msg.sender
    self.protocol_currency_address = _protocol_currency_address

    self.DAO_TYPE_MARKET = 2
    self.daos[self.DAO_TYPE_MARKET] = _dao_address_market

    self.TEMPLATE_TYPE_COLLATERAL_AUCTION_ERC20 = 1
    self.templates[self.TEMPLATE_TYPE_COLLATERAL_AUCTION_ERC20] = _template_address_collateral_auction_erc20

    return True


@private
@constant
def _loan_market_hash(_currency_address: address, _expiry: timestamp, _underlying_address: address) -> bytes32:
    return keccak256(
        concat(
            convert(self.protocol_dao_address, bytes32),
            convert(_currency_address, bytes32),
            convert(_expiry, bytes32),
            convert(_underlying_address, bytes32)
        )
    )


@private
def _validate_graph(_loan_market_hash: bytes32, _graph_address: address):
    assert self.graphs[_loan_market_hash] == _graph_address


# admin functions
@public
def set_template(_template_type: uint256, _address: address) -> bool:
    assert self._is_initialized()
    assert msg.sender == self.owner
    assert _template_type == self.TEMPLATE_TYPE_COLLATERAL_AUCTION_ERC20
    self.templates[_template_type] = _address
    return True


@public
def create_graph(_currency_address: address, _expiry: timestamp, _underlying_address: address) -> address:
    assert msg.sender == self.daos[self.DAO_TYPE_MARKET]
    _loan_market_hash: bytes32 = self._loan_market_hash(_currency_address, _expiry, _underlying_address)
    # deploy and initialize collateral auction graph
    _auction_address: address = create_forwarder_to(self.templates[self.TEMPLATE_TYPE_COLLATERAL_AUCTION_ERC20])
    self.graphs[_loan_market_hash] = _auction_address
    assert_modifiable(CollateralAuctionGraph(_auction_address).initialize(
        _currency_address, _underlying_address, _expiry,
        self.daos[self.DAO_TYPE_MARKET]))

    return _auction_address
