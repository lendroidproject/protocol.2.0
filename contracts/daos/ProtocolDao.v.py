# Vyper version of the Lendroid protocol v2
# THIS CONTRACT HAS NOT BEEN AUDITED!


from contracts.interfaces import CurrencyDao
from contracts.interfaces import InterestPoolDao
from contracts.interfaces import UnderwriterPoolDao
from contracts.interfaces import LoanDao


# Structs

struct Expiry:
    expiry_timestamp: timestamp
    expiry_label: string[3]
    is_active: bool


# Events of the protocol.

# Variables of the protocol.
protocol_currency_address: public(address)
owner: public(address)
# dao_type => dao_address
daos: public(map(uint256, address))
# timestamp => Expiry
expiries: public(map(timestamp, Expiry))
# template_name => template_contract_address
templates: public(map(string[64], address))

DAO_TYPE_CURRENCY: public(uint256)
DAO_TYPE_INTEREST_POOL: public(uint256)
DAO_TYPE_UNDERWRITER_POOL: public(uint256)
DAO_TYPE_LOAN: public(uint256)


@public
def __init__(
        _protocol_currency_address: address,
        _template_address_currency_dao: address,
        _template_address_currency_pool: address,
        _template_address_currency_erc20: address,
        _template_address_currency_erc1155: address,
        _template_address_interest_pool_dao: address,
        _template_address_interest_pool: address,
        _template_address_underwriter_pool_dao: address,
        _template_address_underwriter_pool: address,
        _template_address_loan_dao: address,
    ):
    # Before init, need to deploy the following template contracts:
    #. CurrencyDao
    #. ContinuousCurrencyPoolERC20Template1
    #. InterestPoolDao
    #. InterestPoolTemplate1
    #. UnderwriterPoolDao
    #. UnderwriterPoolTemplate1
    #. ERC20Template1
    #. ERC1155Template2
    #. LoanDao
    self.owner = msg.sender
    self.protocol_currency_address = _protocol_currency_address

    self.DAO_TYPE_CURRENCY = 1
    self.DAO_TYPE_INTEREST_POOL = 2
    self.DAO_TYPE_UNDERWRITER_POOL = 3
    self.DAO_TYPE_LOAN = 4

    # deploy and initialize currency dao
    _dao_address: address = create_forwarder_to(_template_address_currency_dao)
    assert _dao_address.is_contract
    self.daos[self.DAO_TYPE_CURRENCY] = _dao_address
    _external_call_successful: bool = CurrencyDao(_dao_address).initialize(
        self.owner, _protocol_currency_address,
        _template_address_currency_pool, _template_address_currency_erc20,
        _template_address_currency_erc1155
    )
    assert _external_call_successful
    # deploy and initialize interest pool dao
    _dao_address = create_forwarder_to(_template_address_interest_pool_dao)
    assert _dao_address.is_contract
    self.daos[self.DAO_TYPE_INTEREST_POOL] = _dao_address
    _external_call_successful = InterestPoolDao(_dao_address).initialize(
        self.owner, _protocol_currency_address,
        self.daos[self.DAO_TYPE_CURRENCY], _template_address_interest_pool,
        _template_address_currency_erc20
    )
    assert _external_call_successful
    # deploy and initialize underwriter pool dao
    _dao_address = create_forwarder_to(_template_address_underwriter_pool_dao)
    assert _dao_address.is_contract
    self.daos[self.DAO_TYPE_UNDERWRITER_POOL] = _dao_address
    _external_call_successful = UnderwriterPoolDao(_dao_address).initialize(
        self.owner, _protocol_currency_address,
        self.daos[self.DAO_TYPE_CURRENCY], _template_address_underwriter_pool,
        _template_address_currency_erc20
    )
    assert _external_call_successful
    # deploy and initialize loan dao
    _dao_address = create_forwarder_to(_template_address_loan_dao)
    assert _dao_address.is_contract
    self.daos[self.DAO_TYPE_LOAN] = _dao_address
    _external_call_successful = LoanDao(_dao_address).initialize(
        self.owner, _protocol_currency_address,
        self.daos[self.DAO_TYPE_CURRENCY], self.daos[self.DAO_TYPE_UNDERWRITER_POOL]
    )
    assert _external_call_successful


# Admin functions


@public
def set_expiry_support(_timestamp: timestamp, _label: string[3], _is_active: bool) -> bool:
    assert msg.sender == self.owner
    self.expiries[_timestamp] = Expiry({
        expiry_timestamp: _timestamp,
        expiry_label: _label,
        is_active: _is_active
    })
    return True


@public
def set_template(_label: string[64], _address: address) -> bool:
    assert msg.sender == self.owner
    self.templates[_label] = _address
    return True
