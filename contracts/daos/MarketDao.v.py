# Vyper version of the Lendroid protocol v2
# THIS CONTRACT HAS NOT BEEN AUDITED!


from contracts.interfaces import ERC20
from contracts.interfaces import ERC1155
from contracts.interfaces import ERC1155TokenReceiver
from contracts.interfaces import CurrencyDao
from contracts.interfaces import ShieldPayoutDao
from contracts.interfaces import CollateralAuctionDao
from contracts.interfaces import CollateralAuctionGraph
from contracts.interfaces import SimplePriceOracle


implements: ERC1155TokenReceiver


# Structs
struct ExpiryMarket:
    expiry: timestamp
    id: uint256


struct LoanMarket:
    currency_address: address
    expiry: timestamp
    underlying_address: address
    currency_value_per_underlying_at_expiry: uint256
    status: uint256
    total_outstanding_currency_value_at_expiry: uint256
    total_outstanding_underlying_value_at_expiry: uint256
    collateral_auction_graph_address: address
    total_currency_raised_during_auction: uint256
    total_underlying_sold_during_auction: uint256
    underlying_settlement_price_per_currency: uint256
    shield_market_count: uint256
    hash: bytes32
    id: uint256


struct ShieldMarket:
    currency_address: address
    expiry: timestamp
    underlying_address: address
    strike_price: uint256
    s_hash: bytes32
    s_parent_address: address
    s_token_id: uint256
    u_hash: bytes32
    u_parent_address: address
    u_token_id: uint256
    # Minmum collateral value, aka, minimum currency value per underlying
    minimum_collateral_value: uint256
    hash: bytes32
    id: uint256


protocol_currency_address: public(address)
protocol_dao_address: public(address)
owner: public(address)
# dao_type => dao_address
daos: public(map(uint256, address))
# registry_type => registry_address
registries: public(map(uint256, address))

# expiry_market_timestammp => ExpiryMarket
expiry_markets: public(map(timestamp, ExpiryMarket))
# index per ExpiryMarket
last_expiry_market_index: public(uint256)
# expiry_market_id => expiry_market_timestammp
expiry_market_id_to_timestamp: public(map(uint256, timestamp))
# loan_market_hash => LoanMarket
loan_markets: public(map(bytes32, LoanMarket))
# expiry_timestamp => index per LoanMarket
last_loan_market_index: public(map(timestamp, uint256))
# expiry_timestamp => (loan_market_id => loan_market_hash)
loan_market_id_to_hash: public(map(timestamp, map(uint256, bytes32)))
# shield_market_hash => ShieldMarket
shield_markets: public(map(bytes32, ShieldMarket))
# expiry_timestamp => index per ShieldMarket
last_shield_market_index: public(map(timestamp, uint256))
# expiry_timestamp => (market_id => shield_market_hash)
shield_market_id_to_hash: public(map(timestamp, map(uint256, bytes32)))
# currency_underlying_pair_hash => price_oracle_address
price_oracles: public(map(bytes32, address))

REGISTRY_TYPE_POSITION: public(uint256)

DAO_TYPE_CURRENCY: public(uint256)
DAO_TYPE_INTEREST_POOL: public(uint256)
DAO_TYPE_UNDERWRITER_POOL: public(uint256)
DAO_TYPE_SHIELD_PAYOUT: public(uint256)
DAO_TYPE_COLLATERAL_AUCION: public(uint256)

LOAN_MARKET_STATUS_OPEN: public(uint256)
LOAN_MARKET_STATUS_SETTLING: public(uint256)
LOAN_MARKET_STATUS_CLOSED: public(uint256)

# ERC1155TokenReceiver interface variables
shouldReject: public(bool)
lastData: public(bytes32)
lastOperator: public(address)
lastFrom: public(address)
lastId: public(uint256)
lastValue: public(uint256)
ERC1155_ACCEPTED: bytes[10]
ERC1155_BATCH_ACCEPTED: bytes[10]

initialized: public(bool)


@private
@constant
def _is_initialized() -> bool:
    return self.initialized == True


@public
def initialize(
        _owner: address,
        _protocol_currency_address: address,
        _dao_address_currency: address,
        _dao_address_interest_pool: address,
        _dao_address_underwriter_pool: address,
        _dao_address_shield_payout: address,
        _dao_address_collateral_auction: address,
        _registry_address_position: address) -> bool:
    assert not self._is_initialized()
    self.initialized = True
    self.owner = _owner
    self.protocol_dao_address = msg.sender
    self.protocol_currency_address = _protocol_currency_address

    self.REGISTRY_TYPE_POSITION = 1
    self.registries[self.REGISTRY_TYPE_POSITION] = _registry_address_position

    self.DAO_TYPE_CURRENCY = 1
    self.daos[self.DAO_TYPE_CURRENCY] = _dao_address_currency
    self.DAO_TYPE_INTEREST_POOL = 2
    self.daos[self.DAO_TYPE_INTEREST_POOL] = _dao_address_interest_pool
    self.DAO_TYPE_UNDERWRITER_POOL = 3
    self.daos[self.DAO_TYPE_UNDERWRITER_POOL] = _dao_address_underwriter_pool
    self.DAO_TYPE_SHIELD_PAYOUT = 4
    self.daos[self.DAO_TYPE_SHIELD_PAYOUT] = _dao_address_shield_payout
    self.DAO_TYPE_COLLATERAL_AUCION = 5
    self.daos[self.DAO_TYPE_COLLATERAL_AUCION] = _dao_address_collateral_auction

    self.LOAN_MARKET_STATUS_OPEN = 1
    self.LOAN_MARKET_STATUS_SETTLING = 2
    self.LOAN_MARKET_STATUS_CLOSED = 3

    # bytes4(keccak256("onERC1155Received(address,address,uint256,uint256,bytes)"))
    self.ERC1155_ACCEPTED = "0xf23a6e61"
    # bytes4(keccak256("onERC1155BatchReceived(address,address,uint256[],uint256[],bytes)"))
    self.ERC1155_BATCH_ACCEPTED = "0xbc197c81"
    self.shouldReject = False

    return True


@private
@constant
def _multi_fungible_currency_hash(parent_currency_address: address, _currency_address: address, _expiry: timestamp, _underlying_address: address, _strike_price: uint256) -> bytes32:
    return keccak256(
        concat(
            convert(self.protocol_dao_address, bytes32),
            convert(parent_currency_address, bytes32),
            convert(_currency_address, bytes32),
            convert(_expiry, bytes32),
            convert(_underlying_address, bytes32),
            convert(_strike_price, bytes32)
        )
    )


@private
@constant
def _currency_underlying_pair_hash(_currency_address: address, _underlying_address: address) -> bytes32:
    return keccak256(
        concat(
            convert(self.protocol_dao_address, bytes32),
            convert(_currency_address, bytes32),
            convert(_underlying_address, bytes32)
        )
    )


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
@constant
def _shield_market_hash(_currency_address: address, _expiry: timestamp, _underlying_address: address, _strike_price: uint256) -> bytes32:
    return keccak256(
        concat(
            convert(self.protocol_dao_address, bytes32),
            convert(_currency_address, bytes32),
            convert(_expiry, bytes32),
            convert(_underlying_address, bytes32),
            convert(_strike_price, bytes32)
        )
    )


@private
@constant
def _is_currency_valid(_currency_address: address) -> bool:
    return CurrencyDao(self.daos[self.DAO_TYPE_CURRENCY]).is_currency_valid(_currency_address)


@private
@constant
def _multi_fungible_addresses(_currency_address: address) -> (address, address, address, address, address):
    return CurrencyDao(self.daos[self.DAO_TYPE_CURRENCY]).multi_fungible_addresses(_currency_address)


@private
@constant
def _shield_payout(
        _currency_address: address, _expiry: timestamp,
        _underlying_address: address, _strike_price: uint256,
        _underlying_settlement_price_per_currency: uint256
        ) -> uint256:
    _shield_market_hash: bytes32 = self._shield_market_hash(_currency_address, _expiry, _underlying_address, _strike_price)
    if _underlying_settlement_price_per_currency <= self.shield_markets[_shield_market_hash].strike_price:
        return 0
    return (as_unitless_number(_underlying_settlement_price_per_currency) - as_unitless_number(self.shield_markets[_shield_market_hash].strike_price)) / as_unitless_number(_underlying_settlement_price_per_currency)


@private
@constant
def _underwriter_payout(
    _currency_address: address, _expiry: timestamp,
    _underlying_address: address, _strike_price: uint256,
    _underlying_settlement_price_per_currency: uint256
    ) -> uint256:
    _shield_market_hash: bytes32 = self._shield_market_hash(_currency_address, _expiry, _underlying_address, _strike_price)
    if _underlying_settlement_price_per_currency <= self.shield_markets[_shield_market_hash].strike_price:
        return 0
    return as_unitless_number(self.shield_markets[_shield_market_hash].strike_price) / as_unitless_number(_underlying_settlement_price_per_currency)


@public
@constant
def shield_payout(_currency_address: address, _expiry: timestamp, _underlying_address: address, _strike_price: uint256) -> uint256:
    _loan_market_hash: bytes32 = self._loan_market_hash(_currency_address, _expiry, _underlying_address)
    if not self.loan_markets[_loan_market_hash].status == self.LOAN_MARKET_STATUS_CLOSED:
        return 0
    return self._shield_payout(
        _currency_address, _expiry, _underlying_address, _strike_price,
        self.loan_markets[_loan_market_hash].underlying_settlement_price_per_currency
    )


@public
@constant
def underwriter_payout(_currency_address: address, _expiry: timestamp, _underlying_address: address, _strike_price: uint256) -> uint256:
    _loan_market_hash: bytes32 = self._loan_market_hash(_currency_address, _expiry, _underlying_address)
    if not self.loan_markets[_loan_market_hash].status == self.LOAN_MARKET_STATUS_CLOSED:
        return 0
    return self._underwriter_payout(_currency_address, _expiry, _underlying_address, _strike_price,
        self.loan_markets[_loan_market_hash].underlying_settlement_price_per_currency
    )


@private
def _deposit_multi_fungible_l_currency(_currency_address: address, _from: address, _to: address, _value: uint256):
    assert_modifiable(CurrencyDao(self.daos[self.DAO_TYPE_CURRENCY]).deposit_multi_fungible_l_currency(
        _currency_address, _from, _to, _value))


@private
def _release_currency_from_pool(_currency_address: address, _to: address, _value: uint256):
    assert_modifiable(CurrencyDao(self.daos[self.DAO_TYPE_CURRENCY]).release_currency_from_pool(
        _currency_address, _to, _value))


@private
def _deposit_currency_to_pool(_currency_address: address, _from: address, _value: uint256):
    assert_modifiable(CurrencyDao(self.daos[self.DAO_TYPE_CURRENCY]).deposit_currency_to_pool(
        _currency_address, _from, _value))


@private
def _transfer_erc20(_currency_address: address, _to: address, _value: uint256):
    assert_modifiable(ERC20(_currency_address).transfer(_to, _value))


@private
def _mint_and_self_authorize_erc20(_currency_address: address, _to: address, _value: uint256):
    assert_modifiable(CurrencyDao(self.daos[self.DAO_TYPE_CURRENCY]).mint_and_self_authorize_erc20(_currency_address, _to, _value))


@private
def _burn_erc1155(_currency_address: address, _id: uint256, _from: address, _value: uint256):
    assert_modifiable(CurrencyDao(self.daos[self.DAO_TYPE_CURRENCY]).burn_erc1155(_currency_address, _id, _from, _value))


@private
def _transfer_as_self_authorized_erc1155_and_authorize(_from: address, _to: address, _currency_address: address, _id: uint256, _value: uint256):
    assert_modifiable(CurrencyDao(self.daos[self.DAO_TYPE_CURRENCY]).transfer_as_self_authorized_erc1155_and_authorize(_from, _to, _currency_address, _id, _value))


# START of ERC1155TokenReceiver interface functions
@public
def setShouldReject(_value: bool):
    assert msg.sender == self.owner
    self.shouldReject = _value


@public
@constant
def supportsInterface(interfaceID: bytes[10]) -> bool:
    # ERC165 or ERC1155_ACCEPTED ^ ERC1155_BATCH_ACCEPTED
    return interfaceID == "0x01ffc9a7" or interfaceID == "0x4e2312e0"


@public
def onERC1155Received(_operator: address, _from: address, _id: uint256, _value: uint256, _data: bytes32) -> bytes[10]:
    self.lastOperator = _operator
    self.lastFrom = _from
    self.lastId = _id
    self.lastValue = _value
    self.lastData = _data
    if self.shouldReject:
        raise("onERC1155Received: transfer not accepted")
    else:
        return self.ERC1155_ACCEPTED


@public
def onERC1155BatchReceived(_operator: address, _from: address, _ids: uint256[5], _values: uint256[5], _data: bytes32) -> bytes[10]:
    self.lastOperator = _operator
    self.lastFrom = _from
    self.lastId = _ids[0]
    self.lastValue = _values[0]
    self.lastData = _data
    if self.shouldReject:
        raise("onERC1155BatchReceived: transfer not accepted")
    else:
        return self.ERC1155_BATCH_ACCEPTED


# END of ERC1155TokenReceiver interface functions


@private
def _open_expiry_market(_expiry: timestamp):
    assert _expiry > block.timestamp
    self.expiry_market_id_to_timestamp[self.last_expiry_market_index] = _expiry
    self.expiry_markets[_expiry] = ExpiryMarket({
        expiry: _expiry,
        id: self.last_expiry_market_index
    })
    self.last_expiry_market_index += 1


@private
def _open_loan_market(_currency_address: address, _expiry: timestamp, _underlying_address: address):
    assert _expiry > block.timestamp
    assert self.expiry_markets[_expiry].expiry == _expiry
    _loan_market_hash: bytes32 = self._loan_market_hash(_currency_address, _expiry, _underlying_address)
    self.loan_market_id_to_hash[_expiry][self.last_loan_market_index[_expiry]] = _loan_market_hash
    # deploy and initialize collateral auction graph
    _auction_address: address = CollateralAuctionDao(self.daos[self.DAO_TYPE_COLLATERAL_AUCION]).create_graph(
        _currency_address, _expiry, _underlying_address)
    assert _auction_address.is_contract
    self.loan_markets[_loan_market_hash] = LoanMarket({
        currency_address: _currency_address,
        expiry: _expiry,
        underlying_address: _underlying_address,
        currency_value_per_underlying_at_expiry: 0,
        status: self.LOAN_MARKET_STATUS_OPEN,
        total_outstanding_currency_value_at_expiry: 0,
        total_outstanding_underlying_value_at_expiry: 0,
        collateral_auction_graph_address: _auction_address,
        total_currency_raised_during_auction: 0,
        total_underlying_sold_during_auction: 0,
        underlying_settlement_price_per_currency: 0,
        shield_market_count: 0,
        hash: _loan_market_hash,
        id: self.last_loan_market_index[_expiry]
    })
    self.last_loan_market_index[_expiry] += 1


@private
def _settle_loan_market(_loan_market_hash: bytes32):
    # TODO : Set _underlying_price_per_currency_at_expiry from an external price-feed oracle
    _currency_underlying_pair_hash: bytes32 = self._currency_underlying_pair_hash(
        self.loan_markets[_loan_market_hash].currency_address,
        self.loan_markets[_loan_market_hash].underlying_address
    )
    # assert self.price_oracles[_currency_underlying_pair_hash].is_contract
    # self.loan_markets[_loan_market_hash].currency_value_per_underlying_at_expiry = SimplePriceOracle(self.price_oracles[_currency_underlying_pair_hash]).get_price()
    self.loan_markets[_loan_market_hash].currency_value_per_underlying_at_expiry = 150 * 10 ** 18
    if as_unitless_number(self.loan_markets[_loan_market_hash].shield_market_count) > 0:
        self.loan_markets[_loan_market_hash].status = self.LOAN_MARKET_STATUS_SETTLING
        # start collateral auction
        assert_modifiable(CollateralAuctionGraph(self.loan_markets[_loan_market_hash].collateral_auction_graph_address).start(
            self.loan_markets[_loan_market_hash].currency_value_per_underlying_at_expiry,
            self.loan_markets[_loan_market_hash].total_outstanding_currency_value_at_expiry,
            self.loan_markets[_loan_market_hash].total_outstanding_underlying_value_at_expiry
        ))
        # send oustanding_value of underlying_currency to collateral auction contract
        assert_modifiable(CurrencyDao(self.daos[self.DAO_TYPE_CURRENCY]).secure_l_currency_to_currency(
            self.loan_markets[_loan_market_hash].underlying_address,
            self.loan_markets[_loan_market_hash].collateral_auction_graph_address,
            self.loan_markets[_loan_market_hash].total_outstanding_underlying_value_at_expiry
        ))
    else:
        self.loan_markets[_loan_market_hash].status = self.LOAN_MARKET_STATUS_CLOSED


@private
def _open_shield_market(_currency_address: address, _expiry: timestamp, _underlying_address: address, _strike_price: uint256,
    _s_hash: bytes32, _s_parent_address: address, _s_id: uint256,
    _u_hash: bytes32, _u_parent_address: address, _u_id: uint256):
    assert block.timestamp < _expiry
    _shield_market_hash: bytes32 = self._shield_market_hash(_currency_address, _expiry, _underlying_address, _strike_price)
    self.shield_market_id_to_hash[_expiry][self.last_shield_market_index[_expiry]] = _shield_market_hash
    # register shield_market
    assert_modifiable(ShieldPayoutDao(self.daos[self.DAO_TYPE_SHIELD_PAYOUT]).register_shield_market(
        _currency_address, _expiry, _underlying_address, _strike_price
    ))

    # save shield market
    self.shield_markets[_shield_market_hash] = ShieldMarket({
        currency_address: _currency_address,
        expiry: _expiry,
        underlying_address: _underlying_address,
        strike_price: _strike_price,
        s_hash: _s_hash,
        s_parent_address: _s_parent_address,
        s_token_id: _s_id,
        u_hash: _u_hash,
        u_parent_address: _u_parent_address,
        u_token_id: _u_id,
        minimum_collateral_value: _strike_price,
        hash: _shield_market_hash,
        id: self.last_shield_market_index[_expiry]
    })
    self.last_shield_market_index[_expiry] += 1
    # update loan market
    _loan_market_hash: bytes32 = self._loan_market_hash(_currency_address, _expiry, _underlying_address)
    self.loan_markets[_loan_market_hash].shield_market_count += 1


@public
def open_shield_market(_currency_address: address, _expiry: timestamp, _underlying_address: address, _strike_price: uint256,
    _s_hash: bytes32, _s_parent_address: address, _s_id: uint256,
    _u_hash: bytes32, _u_parent_address: address, _u_id: uint256) -> bool:
    assert self._is_initialized()
    assert msg.sender == self.daos[self.DAO_TYPE_UNDERWRITER_POOL]
    # create expiry market if it does not exist
    if not self.expiry_markets[_expiry].expiry == _expiry:
        self._open_expiry_market(_expiry)
    # create loan market if it does not exist
    if self.loan_markets[self._loan_market_hash(_currency_address, _expiry, _underlying_address)].hash == EMPTY_BYTES32:
        self._open_loan_market(_currency_address, _expiry, _underlying_address)
    # create shield market if it does not exist
    if self.shield_markets[self._shield_market_hash(_currency_address, _expiry, _underlying_address, _strike_price)].hash == EMPTY_BYTES32:
        self._open_shield_market(_currency_address, _expiry, _underlying_address, _strike_price,
            _s_hash, _s_parent_address, _s_id, _u_hash, _u_parent_address, _u_id)

    return True


@public
def settle_loan_market(_loan_market_hash: bytes32):
    assert block.timestamp >= self.loan_markets[_loan_market_hash].expiry
    assert self.loan_markets[_loan_market_hash].status == self.LOAN_MARKET_STATUS_OPEN
    self._settle_loan_market(_loan_market_hash)
    # TODO : reward msg.sender with LST for initiating loan market settlement


@public
def set_registry(_registry_type: uint256, _address: address) -> bool:
    assert self._is_initialized()
    assert msg.sender == self.owner
    assert _registry_type == self.REGISTRY_TYPE_POSITION
    self.registries[_registry_type] = _address
    return True


@public
def set_shield_market_minimum_collateral_value(_currency_address: address, _expiry: timestamp, _underlying_address: address, _strike_price: uint256, _price: uint256) -> bool:
    assert self._is_initialized()
    assert msg.sender == self.owner
    assert block.timestamp < _expiry
    _shield_market_hash: bytes32 = self._shield_market_hash(_currency_address, _expiry, _underlying_address, _strike_price)
    assert self.shield_markets[_shield_market_hash].hash == _shield_market_hash
    self.shield_markets[_shield_market_hash].minimum_collateral_value = _price

    return True


@public
def set_price_oracle(_currency_address: address, _underlying_address: address, _price_oracle_address: address) -> bool:
    assert self._is_initialized()
    assert msg.sender == self.owner
    assert _currency_address.is_contract
    assert _underlying_address.is_contract
    assert _price_oracle_address.is_contract
    _currency_underlying_pair_hash: bytes32 = self._currency_underlying_pair_hash(_currency_address, _underlying_address)
    self.price_oracles[_currency_underlying_pair_hash] = _price_oracle_address

    return True


@public
@constant
def shield_currency_minimum_collateral_values(_currency_address: address, _expiry: timestamp, _underlying_address: address, _strike_price: uint256) -> uint256:
    return self.shield_markets[self._shield_market_hash(_currency_address, _expiry, _underlying_address, _strike_price)].minimum_collateral_value


@public
def i_currency_for_offer_creation(
    _creator: address, _s_quantity: uint256,
    _currency_address: address, _expiry: timestamp, _underlying_address: address, _strike_price: uint256) -> (address, uint256):
    assert msg.sender == self.registries[self.REGISTRY_TYPE_POSITION]
    assert block.timestamp < _expiry
    _shield_market_hash: bytes32 = self._shield_market_hash(_currency_address, _expiry, _underlying_address, _strike_price)
    assert as_unitless_number(self.shield_markets[_shield_market_hash].minimum_collateral_value) > 0
    _l_currency_address: address = ZERO_ADDRESS
    _i_currency_address: address = ZERO_ADDRESS
    _f_currency_address: address = ZERO_ADDRESS
    _s_currency_address: address = ZERO_ADDRESS
    _u_currency_address: address = ZERO_ADDRESS
    _l_currency_address, _i_currency_address, _f_currency_address, _s_currency_address, _u_currency_address = self._multi_fungible_addresses(_currency_address)
    _i_hash: bytes32 = self._multi_fungible_currency_hash(_i_currency_address, _currency_address, _expiry, ZERO_ADDRESS, 0)
    _i_parent_address: address = CurrencyDao(self.daos[self.DAO_TYPE_CURRENCY]).multi_fungible_currencies__parent_currency_address(_i_hash)
    _i_token_id: uint256 = CurrencyDao(self.daos[self.DAO_TYPE_CURRENCY]).multi_fungible_currencies__token_id(_i_hash)
    _s_hash: bytes32 = self._multi_fungible_currency_hash(_s_currency_address, _currency_address, _expiry, _underlying_address, _strike_price)
    _s_parent_address: address = CurrencyDao(self.daos[self.DAO_TYPE_CURRENCY]).multi_fungible_currencies__parent_currency_address(_s_hash)
    _s_token_id: uint256 = CurrencyDao(self.daos[self.DAO_TYPE_CURRENCY]).multi_fungible_currencies__token_id(_s_hash)
    assert not _i_parent_address == ZERO_ADDRESS
    assert as_unitless_number(_i_token_id) > 0
    # verify creator has sufficient s_currency
    assert as_unitless_number(ERC1155(_s_parent_address).balanceOf(_creator, _s_token_id)) >= as_unitless_number(_s_quantity)
    # verify creator has sufficient i_currency
    assert as_unitless_number(ERC1155(_i_parent_address).balanceOf(_creator, _i_token_id)) >= as_unitless_number(_s_quantity)

    return _i_parent_address, _i_token_id


@public
def secure_currency_deposit_and_market_update_from_auction_purchase(
    _currency_address: address, _expiry: timestamp, _underlying_address: address,
    _purchaser: address, _currency_value: uint256, _underlying_value: uint256,
    _is_auction_active: bool
    ) -> bool:
    _loan_market_hash: bytes32 = self._loan_market_hash(_currency_address, _expiry, _underlying_address)
    assert msg.sender == self.loan_markets[_loan_market_hash].collateral_auction_graph_address
    assert_modifiable(CurrencyDao(self.daos[self.DAO_TYPE_CURRENCY]).secure_deposit_currency_to_pool(
        _currency_address, _purchaser, _currency_value
    ))
    self.loan_markets[_loan_market_hash].total_currency_raised_during_auction += _currency_value
    self.loan_markets[_loan_market_hash].total_underlying_sold_during_auction += _underlying_value
    if not _is_auction_active:
        self.loan_markets[_loan_market_hash].status = self.LOAN_MARKET_STATUS_CLOSED
        self.loan_markets[_loan_market_hash].underlying_settlement_price_per_currency = as_unitless_number(self.loan_markets[_loan_market_hash].total_currency_raised_during_auction) / as_unitless_number(self.loan_markets[_loan_market_hash].total_underlying_sold_during_auction)

    return True


@public
def open_position(
    _shield_market_hash: bytes32,
    _offer_creator: address,
    _i_parent_address: address, _i_token_id: uint256, _i_quantity: uint256,
    _s_quantity: uint256,
    _lend_currency_value: uint256, _borrow_currency_value: uint256,
    _borrower: address
    ) -> bool:
    # validate caller
    assert msg.sender == self.registries[self.REGISTRY_TYPE_POSITION]
    # validate currencies
    assert self._is_currency_valid(self.shield_markets[_shield_market_hash].currency_address)
    assert self._is_currency_valid(self.shield_markets[_shield_market_hash].underlying_address)
    _loan_market_hash: bytes32 = self._loan_market_hash(
        self.shield_markets[_shield_market_hash].currency_address,
        self.shield_markets[_shield_market_hash].expiry,
        self.shield_markets[_shield_market_hash].underlying_address
    )
    assert self.loan_markets[_loan_market_hash].status == self.LOAN_MARKET_STATUS_OPEN
    self.loan_markets[_loan_market_hash].total_outstanding_currency_value_at_expiry += _lend_currency_value
    self.loan_markets[_loan_market_hash].total_outstanding_underlying_value_at_expiry += _borrow_currency_value
    # self._burn_erc1155(_multi_fungible_currency_i_parent_address,
    #     _multi_fungible_currency_i_token_id,
    #     self.offers[_offer_id].creator,
    #     self.offers[_offer_id].multi_fungible_currency_i_quantity
    # )
    # transfer i_lend_currency from offer_creator to _borrower
    self._transfer_as_self_authorized_erc1155_and_authorize(
        _offer_creator,
        _borrower,
        _i_parent_address,
        _i_token_id,
        as_unitless_number(_i_quantity) * (10 ** 18)
    )
    # transfer s_lend_currency from offer_creator to self
    self._transfer_as_self_authorized_erc1155_and_authorize(
        _offer_creator,
        self,
        self.shield_markets[_shield_market_hash].s_parent_address,
        self.shield_markets[_shield_market_hash].s_token_id,
        as_unitless_number(_s_quantity) * (10 ** 18)
    )
    # transfer l_borrow_currency from borrower to self
    self._deposit_multi_fungible_l_currency(
        self.shield_markets[_shield_market_hash].underlying_address,
        _borrower, self, _borrow_currency_value)
    # transfer lend_currency to _borrower
    self._release_currency_from_pool(
        self.shield_markets[_shield_market_hash].currency_address,
        _borrower, _lend_currency_value)

    return True


@public
def close_position(
    _shield_market_hash: bytes32,
    _i_parent_address: address, _i_token_id: uint256, _i_quantity: uint256,
    _s_quantity: uint256,
    _lend_currency_value: uint256, _borrow_currency_value: uint256,
    _borrower: address
    ) -> bool:
    # validate caller
    assert msg.sender == self.registries[self.REGISTRY_TYPE_POSITION]
    # validate currencies
    assert self._is_currency_valid(self.shield_markets[_shield_market_hash].currency_address)
    assert self._is_currency_valid(self.shield_markets[_shield_market_hash].underlying_address)
    _loan_market_hash: bytes32 = self._loan_market_hash(
        self.shield_markets[_shield_market_hash].currency_address,
        self.shield_markets[_shield_market_hash].expiry,
        self.shield_markets[_shield_market_hash].underlying_address
    )
    assert self.loan_markets[_loan_market_hash].status == self.LOAN_MARKET_STATUS_OPEN
    self.loan_markets[_loan_market_hash].total_outstanding_currency_value_at_expiry -= _lend_currency_value
    self.loan_markets[_loan_market_hash].total_outstanding_underlying_value_at_expiry -= _borrow_currency_value
    # transfer s_lend_currency from self to _borrower
    self._transfer_as_self_authorized_erc1155_and_authorize(
        self,
        _borrower,
        self.shield_markets[_shield_market_hash].s_parent_address,
        self.shield_markets[_shield_market_hash].s_token_id,
        as_unitless_number(_s_quantity) * (10 ** 18)
    )
    # transfer l_borrow_currency to msg.sender
    self._transfer_erc20(
        CurrencyDao(self.daos[self.DAO_TYPE_CURRENCY]).currencies__l_currency_address(
        self.shield_markets[_shield_market_hash].underlying_address),
        _borrower,
        _borrow_currency_value)
    # transfer lend_currency from _borrower to currency_pool
    self._deposit_currency_to_pool(
        self.shield_markets[_shield_market_hash].currency_address,
        _borrower,
        _lend_currency_value)

    return True


@public
def close_liquidated_position(
    _shield_market_hash: bytes32, _s_quantity: uint256,
    _lend_currency_value: uint256, _borrow_currency_value: uint256,
    _borrower: address
    ) -> bool:
    # validate caller
    assert msg.sender == self.registries[self.REGISTRY_TYPE_POSITION]
    # validate currencies
    assert self._is_currency_valid(self.shield_markets[_shield_market_hash].currency_address)
    assert self._is_currency_valid(self.shield_markets[_shield_market_hash].underlying_address)
    _loan_market_hash: bytes32 = self._loan_market_hash(
        self.shield_markets[_shield_market_hash].currency_address,
        self.shield_markets[_shield_market_hash].expiry,
        self.shield_markets[_shield_market_hash].underlying_address
    )
    assert self.loan_markets[_loan_market_hash].status == self.LOAN_MARKET_STATUS_CLOSED
    # burn s_lend_currency from self
    self._burn_erc1155(
        self.shield_markets[_shield_market_hash].s_parent_address,
        self.shield_markets[_shield_market_hash].s_token_id,
        self,
        as_unitless_number(_s_quantity) * (10 ** 18)
    )
    # transfer l_borrow_currency to _borrower
    if as_unitless_number(self.loan_markets[_loan_market_hash].underlying_settlement_price_per_currency) > self.shield_markets[_shield_market_hash].strike_price:
        _currency_remaining_ratio: uint256 = (as_unitless_number(self.loan_markets[_loan_market_hash].underlying_settlement_price_per_currency) - self.shield_markets[_shield_market_hash].strike_price) / as_unitless_number(self.loan_markets[_loan_market_hash].underlying_settlement_price_per_currency)
        _underlying_value_to_transfer: uint256 = as_unitless_number(_currency_remaining_ratio) * as_unitless_number(_borrow_currency_value)
        self._transfer_erc20(
            CurrencyDao(self.daos[self.DAO_TYPE_CURRENCY]).currencies__l_currency_address(
            self.shield_markets[_shield_market_hash].underlying_address),
            _borrower,
            _underlying_value_to_transfer)

    return True
