import os

from eth_tester import (
    EthereumTester,
    PyEVMBackend
)
from eth_tester.exceptions import (
    TransactionFailed,
)
from eth_utils.toolz import (
    compose,
)
import pytest
from web3 import Web3
from web3.contract import (
    Contract,
    mk_collision_prop,
)
from web3.logs import DISCARD
from web3.providers.eth_tester import (
    EthereumTesterProvider,
)
from web3.testing import Testing

from vyper import (
    compiler,
)

# Constants

ZERO_ADDRESS = Web3.toChecksumAddress('0x0000000000000000000000000000000000000000')
EMPTY_BYTES32 = b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
POOL_NAME_REGISTRATION_MIN_STAKE_LST = 250000
POOL_NAME_REGISTRATION_LST_STAKE_PER_NAME_LENGTH = {
    '4': 500000,
    '3': 1000000,
    '2': 5000000,
    '1': 10000000
}
INTEREST_POOL_DAO_MIN_MFT_FEE = 250000
INTEREST_POOL_DAO_FEE_MULTIPLIER_PER_MFT_COUNT = 250

# POOL_NAMES
POOL_NAME_A = "A"
POOL_NAME_AB = "AB"
POOL_NAME_ABC = "ABC"
POOL_NAME_ABCD = "ABCD"
POOL_NAME_LIONFURY = "Lion Fury"

# Liability limits
MAX_LIABILITY_CURENCY_MARKET = 1000000

# STRIKE_PRICES
STRIKE_125 = 125
STRIKE_150 = 150
STRIKE_200 = 200

# EXPIRIES
# Last Thursday of December 2019, i.e., December 26th, 2019, i.e., Z19
Z19 = 1577404799
# Last Thursday of March 2020, i.e., March 26th, 2020, i.e., H20
H20 = 1585267199

PROTOCOL_CONSTANTS = {
    'DAO_CURRENCY': 1,
    'DAO_INTEREST_POOL': 2,
    'DAO_UNDERWRITER_POOL': 3,
    'DAO_MARKET': 4,
    'DAO_SHIELD_PAYOUT': 5,
    'REGISTRY_POOL_NAME': 1,
    'REGISTRY_POSITION': 2,
    'TEMPLATE_TOKEN_POOL': 1,
    'TEMPLATE_INTEREST_POOL': 2,
    'TEMPLATE_UNDERWRITER_POOL': 3,
    'TEMPLATE_PRICE_ORACLE': 4,
    'TEMPLATE_COLLATERAL_AUCTION': 5,
    'TEMPLATE_ERC20': 6,
    'TEMPLATE_MFT': 7,
    'CALLER_GOVERNOR': 1,
    'CALLER_ESCAPE_HATCH_MANAGER': 2,
    'CALLER_ESCAPE_HATCH_TOKEN_HOLDER': 3,
    'CALLER_DEPLOYER': 7,
    'MFT_TYPE_F': 1,
    'MFT_TYPE_I': 2,
    'MFT_TYPE_S': 3,
    'MFT_TYPE_U': 4
}

class VyperMethod:
    ALLOWED_MODIFIERS = {'call', 'estimateGas', 'transact', 'buildTransaction'}

    def __init__(self, function, normalizers=None):
        self._function = function
        self._function._return_data_normalizers = normalizers

    def __call__(self, *args, **kwargs):
        return self.__prepared_function(*args, **kwargs)

    def __prepared_function(self, *args, **kwargs):
        if not kwargs:
            modifier, modifier_dict = 'call', {}
            fn_abi = [
                x
                for x
                in self._function.contract_abi
                if x.get('name') == self._function.function_identifier
            ].pop()
            # To make tests faster just supply some high gas value.
            modifier_dict.update({'gas': fn_abi.get('gas', 0) + 50000})
        elif len(kwargs) == 1:
            modifier, modifier_dict = kwargs.popitem()
            if modifier not in self.ALLOWED_MODIFIERS:
                raise TypeError(
                    f"The only allowed keyword arguments are: {self.ALLOWED_MODIFIERS}")
        else:
            raise TypeError(f"Use up to one keyword argument, one of: {self.ALLOWED_MODIFIERS}")
        return getattr(self._function(*args), modifier)(modifier_dict)


class VyperContract:
    """
    An alternative Contract Factory which invokes all methods as `call()`,
    unless you add a keyword argument. The keyword argument assigns the prep method.
    This call
    > contract.withdraw(amount, transact={'from': eth.accounts[1], 'gas': 100000, ...})
    is equivalent to this call in the classic contract:
    > contract.functions.withdraw(amount).transact({'from': eth.accounts[1], 'gas': 100000, ...})
    """

    def __init__(self, classic_contract, method_class=VyperMethod):
        classic_contract._return_data_normalizers += CONCISE_NORMALIZERS
        self._classic_contract = classic_contract
        self.address = self._classic_contract.address
        protected_fn_names = [fn for fn in dir(self) if not fn.endswith('__')]
        for fn_name in self._classic_contract.functions:
            # Override namespace collisions
            if fn_name in protected_fn_names:
                _concise_method = mk_collision_prop(fn_name)
            else:
                _classic_method = getattr(
                    self._classic_contract.functions,
                    fn_name)
                _concise_method = method_class(
                    _classic_method,
                    self._classic_contract._return_data_normalizers
                )
            setattr(self, fn_name, _concise_method)

    @classmethod
    def factory(cls, *args, **kwargs):
        return compose(cls, Contract.factory(*args, **kwargs))


def _none_addr(datatype, data):
    if datatype == 'address' and int(data, base=16) == 0:
        return (datatype, None)
    else:
        return (datatype, data)


CONCISE_NORMALIZERS = (_none_addr,)


@pytest.fixture
def tester():
    genesis_overrides = {"gas_limit": 4700000}
    custom_genesis_params = PyEVMBackend._generate_genesis_params(
        overrides=genesis_overrides
    )
    pyevm_backend = PyEVMBackend(genesis_parameters=custom_genesis_params)
    t = EthereumTester(backend=pyevm_backend)
    # t = EthereumTester()
    return t


def zero_gas_price_strategy(web3, transaction_params=None):
    return 0  # zero gas price makes testing simpler.


@pytest.fixture
def w3(tester):
    w3 = Web3(EthereumTesterProvider(tester))
    w3.eth.setGasPriceStrategy(zero_gas_price_strategy)
    return w3


def _get_contract(w3, Deployer, source_code_path, *args, **kwargs):
    interfaces = kwargs.pop('interfaces', None)
    if interfaces:
        interface_codes = {}
        for interface in interfaces:
            with open(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                os.pardir, 'contracts/interfaces/{0}.vy'.format(interface))) as f:
                    interface_codes[interface] = {
                        'type': 'vyper',
                        'code': f.read()
                    }
        kwargs.update({'interface_codes': interface_codes})
    with open(source_code_path) as f:
        source_code = f.read()
    out = compiler.compile_code(
        source_code,
        ['abi', 'bytecode'],
        interface_codes=kwargs.pop('interface_codes', None),
    )
    abi = out['abi']
    bytecode = out['bytecode']
    address = kwargs.pop('address', None)
    if address is None:
        value = kwargs.pop('value_in_eth', 0) * 10 ** 18  # Handle deploying with an eth value.
        c = w3.eth.contract(abi=abi, bytecode=bytecode)
        deploy_transaction = c.constructor(*args)
        tx_info = {
            'from': Deployer,
            'value': value,
            'gasPrice': 0,
        }
        tx_info.update(kwargs)
        tx_hash = deploy_transaction.transact(tx_info)
        address = w3.eth.getTransactionReceipt(tx_hash)['contractAddress']
    contract = w3.eth.contract(
        address,
        abi=abi,
        bytecode=bytecode,
        ContractFactoryClass=VyperContract,
    )
    return contract


@pytest.fixture
def get_contract(w3, Deployer):
    def get_contract(source_code_path, *args, **kwargs):
        return _get_contract(w3, Deployer, source_code_path, *args, **kwargs)

    return get_contract


@pytest.fixture
def get_logs(w3):
    def get_logs(tx_hash, c, event_name):
        tx_receipt = w3.eth.getTransactionReceipt(tx_hash)
        logs = c._classic_contract.events[event_name]().processReceipt(tx_receipt, errors=DISCARD)
        return logs

    return get_logs


@pytest.fixture
def assert_tx_failed(tester):
    def assert_tx_failed(function_to_test, exception=TransactionFailed, exc_text=None):
        snapshot_id = tester.take_snapshot()
        with pytest.raises(exception) as excinfo:
            function_to_test()
        tester.revert_to_snapshot(snapshot_id)
        if exc_text:
            assert exc_text in str(excinfo.value)

    return assert_tx_failed


@pytest.fixture
def time_travel(w3):
    def time_travel(timestamp):
        current_timestamp = w3.eth.getBlock('latest')['timestamp']
        testing = Testing(w3)
        testing.timeTravel(timestamp)
        testing.mine()
        assert w3.eth.getBlock('latest')['timestamp'] > current_timestamp

    return time_travel


# Library contracts and DAOS


@pytest.fixture
def Whale(w3):
    return w3.eth.accounts[0]


@pytest.fixture
def Deployer(w3):
    return w3.eth.accounts[1]


@pytest.fixture
def Governor(w3):
    return w3.eth.accounts[2]


@pytest.fixture
def EscapeHatchManager(w3):
    return w3.eth.accounts[3]


@pytest.fixture
def EscapeHatchTokenHolder(w3):
    return w3.eth.accounts[4]


@pytest.fixture
def get_ERC20_contract(w3, Whale):
    def get_ERC20_contract(*args, **kwargs):
        source_code_path = 'contracts/templates/ERC20Template1.v.py'
        return _get_contract(w3, Whale, source_code_path, *args, **kwargs)

    return get_ERC20_contract


@pytest.fixture
def LST_token(get_ERC20_contract):
    contract = get_ERC20_contract(
        'Lendroid Support Token', 'LST', 18, 12000000000
    )
    return contract


@pytest.fixture
def Lend_token(get_ERC20_contract):
    contract = get_ERC20_contract(
        'Test Lend Token', 'DAI', 18, 1000000
    )
    return contract


@pytest.fixture
def Borrow_token(get_ERC20_contract):
    contract = get_ERC20_contract(
        'Test Borrow Token', 'WETH', 18, 1000000
    )
    return contract


@pytest.fixture
def Malicious_token(get_ERC20_contract):
    contract = get_ERC20_contract(
        'Test Malicious Token', 'XXX', 18, 1000000
    )
    return contract


@pytest.fixture
def ERC20_library(get_ERC20_contract):
    contract = get_ERC20_contract('', '', 0, 0)
    return contract


@pytest.fixture
def get_LERC20_contract(w3, Whale):
    def get_LERC20_contract(*args, **kwargs):
        source_code_path = 'contracts/templates/LERC20Template1.v.py'
        return _get_contract(w3, Whale, source_code_path, *args, **kwargs)

    return get_LERC20_contract


@pytest.fixture
def LERC20_library(get_LERC20_contract):
    contract = get_LERC20_contract()
    return contract


@pytest.fixture
def get_ERC20_Pool_Token_contract(w3, Whale):
    def get_ERC20_Pool_Token_contract(*args, **kwargs):
        source_code_path = 'contracts/templates/ERC20PoolTokenTemplate1.v.py'
        return _get_contract(w3, Whale, source_code_path, *args, **kwargs)

    return get_ERC20_Pool_Token_contract


@pytest.fixture
def ERC20_Pool_Token_library(get_ERC20_Pool_Token_contract):
    contract = get_ERC20_Pool_Token_contract()
    return contract


@pytest.fixture
def get_MFT_contract(w3, Deployer):
    def get_MFT_contract(*args, **kwargs):
        source_code_path = 'contracts/templates/MultiFungibleTokenTemplate1.v.py'
        return _get_contract(w3, Deployer, source_code_path, *args, **kwargs)

    return get_MFT_contract


@pytest.fixture
def MultiFungibleToken_library(get_MFT_contract):
    contract = get_MFT_contract()
    return contract


@pytest.fixture
def get_PoolNameRegistry_contract(w3, Deployer):
    def get_PoolNameRegistry_contract(*args, **kwargs):
        source_code_path = 'contracts/templates/PoolNameRegistryTemplate1.v.py'
        interfaces=['ERC20', 'CurrencyDao', 'ProtocolDao']
        kwargs.update({'interfaces': interfaces})
        return _get_contract(w3, Deployer, source_code_path, *args, **kwargs)

    return get_PoolNameRegistry_contract


@pytest.fixture
def PoolNameRegistry_library(get_PoolNameRegistry_contract):
    contract = get_PoolNameRegistry_contract()
    return contract


@pytest.fixture
def get_CurrencyPool_contract(w3, Deployer):
    def get_CurrencyPool_contract(*args, **kwargs):
        source_code_path = 'contracts/templates/ERC20TokenPoolTemplate1.v.py'
        interfaces=['ERC20']
        kwargs.update({'interfaces': interfaces})
        return _get_contract(w3, Deployer, source_code_path, *args, **kwargs)

    return get_CurrencyPool_contract


@pytest.fixture
def CurrencyPool_library(get_CurrencyPool_contract):
    contract = get_CurrencyPool_contract()
    return contract


@pytest.fixture
def get_CurrencyDao_contract(w3, Deployer):
    def get_CurrencyDao_contract(*args, **kwargs):
        source_code_path = 'contracts/daos/CurrencyDao.v.py'
        interfaces=['ERC20', 'LERC20', 'MultiFungibleToken', 'ERC20TokenPool', 'ProtocolDao']
        kwargs.update({'interfaces': interfaces})
        return _get_contract(w3, Deployer, source_code_path, *args, **kwargs)

    return get_CurrencyDao_contract


@pytest.fixture
def CurrencyDao_library(get_CurrencyDao_contract):
    contract = get_CurrencyDao_contract()
    return contract


@pytest.fixture
def get_InterestPool_contract(w3, Deployer):
    def get_InterestPool_contract(*args, **kwargs):
        source_code_path = 'contracts/templates/InterestPoolTemplate1.v.py'
        interfaces=[
            'ERC20', 'ERC20PoolToken', 'MultiFungibleToken', 'InterestPoolDao'
        ]
        kwargs.update({'interfaces': interfaces})
        return _get_contract(w3, Deployer, source_code_path, *args, **kwargs)

    return get_InterestPool_contract


@pytest.fixture
def InterestPool_library(get_InterestPool_contract):
    contract = get_InterestPool_contract()
    return contract


@pytest.fixture
def get_InterestPoolDao_contract(w3, Deployer):
    def get_InterestPoolDao_contract(*args, **kwargs):
        source_code_path = 'contracts/daos/InterestPoolDao.v.py'
        interfaces=['ERC20', 'MultiFungibleToken', 'CurrencyDao', 'InterestPool', 'PoolNameRegistry', 'ProtocolDao']
        kwargs.update({'interfaces': interfaces})
        return _get_contract(w3, Deployer, source_code_path, *args, **kwargs)

    return get_InterestPoolDao_contract


@pytest.fixture
def InterestPoolDao_library(get_InterestPoolDao_contract):
    contract = get_InterestPoolDao_contract()
    return contract


@pytest.fixture
def get_UnderwriterPool_contract(w3, Deployer):
    def get_UnderwriterPool_contract(*args, **kwargs):
        source_code_path = 'contracts/templates/UnderwriterPoolTemplate1.v.py'
        interfaces=[
            'ERC20', 'ERC20PoolToken', 'MultiFungibleToken',
            'UnderwriterPoolDao', 'ShieldPayoutDao'
        ]
        kwargs.update({'interfaces': interfaces})
        return _get_contract(w3, Deployer, source_code_path, *args, **kwargs)

    return get_UnderwriterPool_contract


@pytest.fixture
def UnderwriterPool_library(get_UnderwriterPool_contract):
    contract = get_UnderwriterPool_contract()
    return contract


@pytest.fixture
def get_UnderwriterPoolDao_contract(w3, Deployer):
    def get_UnderwriterPoolDao_contract(*args, **kwargs):
        source_code_path = 'contracts/daos/UnderwriterPoolDao.v.py'
        interfaces=['ERC20', 'MultiFungibleToken', 'CurrencyDao',
            'UnderwriterPool', 'MarketDao', 'PoolNameRegistry', 'ProtocolDao']
        kwargs.update({'interfaces': interfaces})
        return _get_contract(w3, Deployer, source_code_path, *args, **kwargs)

    return get_UnderwriterPoolDao_contract


@pytest.fixture
def UnderwriterPoolDao_library(get_UnderwriterPoolDao_contract):
    contract = get_UnderwriterPoolDao_contract()
    return contract


@pytest.fixture
def get_CollateralAuctionCurve_contract(w3, Deployer):
    def get_CollateralAuctionCurve_contract(*args, **kwargs):
        source_code_path = 'contracts/templates/SimpleCollateralAuctionCurveTemplate1.v.py'
        interfaces=['MultiFungibleToken', 'MarketDao', 'ProtocolDao']
        kwargs.update({'interfaces': interfaces})
        return _get_contract(w3, Deployer, source_code_path, *args, **kwargs)

    return get_CollateralAuctionCurve_contract


@pytest.fixture
def CollateralAuctionCurve_Library(get_CollateralAuctionCurve_contract):
    contract = get_CollateralAuctionCurve_contract()
    return contract


@pytest.fixture
def get_ShieldPayoutDao_contract(w3, Deployer):
    def get_ShieldPayoutDao_contract(*args, **kwargs):
        source_code_path = 'contracts/daos/ShieldPayoutDao.v.py'
        interfaces=['ERC20', 'MultiFungibleToken', 'CurrencyDao', 'MarketDao', 'ProtocolDao']
        kwargs.update({'interfaces': interfaces})
        return _get_contract(w3, Deployer, source_code_path, *args, **kwargs)

    return get_ShieldPayoutDao_contract


@pytest.fixture
def ShieldPayoutDao_library(get_ShieldPayoutDao_contract):
    contract = get_ShieldPayoutDao_contract()
    return contract


@pytest.fixture
def get_PositionRegistry_contract(w3, Deployer):
    def get_PositionRegistry_contract(*args, **kwargs):
        source_code_path = 'contracts/templates/PositionRegistryTemplate1.v.py'
        interfaces=['MarketDao']
        kwargs.update({'interfaces': interfaces})
        return _get_contract(w3, Deployer, source_code_path, *args, **kwargs)

    return get_PositionRegistry_contract


@pytest.fixture
def PositionRegistry_library(get_PositionRegistry_contract):
    contract = get_PositionRegistry_contract()
    return contract


@pytest.fixture
def PriceFeed(w3, get_contract):
    contract = get_contract('tests/TestPriceFeed.v.py')
    return contract


@pytest.fixture
def PriceOracle(w3, get_contract, Lend_token, Borrow_token, PriceFeed):
    contract = get_contract(
        'contracts/templates/SimplePriceOracleTemplate1.v.py',
        Lend_token.address, Borrow_token.address, PriceFeed.address,
        interfaces=['SimplePriceOracle']
    )
    return contract


@pytest.fixture
def get_MarketDao_contract(w3, Deployer):
    def get_MarketDao_contract(*args, **kwargs):
        source_code_path = 'contracts/daos/MarketDao.v.py'
        interfaces=[
            'ERC20', 'MultiFungibleToken',
            'CurrencyDao', 'ShieldPayoutDao', 'CollateralAuctionCurve',
            'SimplePriceOracle', 'ProtocolDao'
        ]
        kwargs.update({'interfaces': interfaces})
        return _get_contract(w3, Deployer, source_code_path, *args, **kwargs)

    return get_MarketDao_contract


@pytest.fixture
def MarketDao_library(get_MarketDao_contract):
    contract = get_MarketDao_contract()
    return contract


@pytest.fixture
def ProtocolDao(get_contract,
        LST_token,
        Governor, EscapeHatchManager, EscapeHatchTokenHolder,
        CurrencyDao_library, InterestPoolDao_library, UnderwriterPoolDao_library,
        MarketDao_library, ShieldPayoutDao_library,
        PoolNameRegistry_library, PositionRegistry_library,
        CurrencyPool_library, InterestPool_library, UnderwriterPool_library,
        PriceOracle, CollateralAuctionCurve_Library,
        ERC20_library, LERC20_library, ERC20_Pool_Token_library,
        MultiFungibleToken_library
    ):
    contract = get_contract(
        'contracts/daos/ProtocolDao.v.py',
        LST_token.address,
        Governor, EscapeHatchManager, EscapeHatchTokenHolder,
        CurrencyDao_library.address, InterestPoolDao_library.address, UnderwriterPoolDao_library.address,
        MarketDao_library.address, ShieldPayoutDao_library.address,
        PoolNameRegistry_library.address, PositionRegistry_library.address,
        CurrencyPool_library.address, InterestPool_library.address, UnderwriterPool_library.address,
        PriceOracle.address, CollateralAuctionCurve_Library.address,
        ERC20_library.address, MultiFungibleToken_library.address,
        LERC20_library.address, ERC20_Pool_Token_library.address,
        interfaces=[
            'CurrencyDao', 'InterestPoolDao', 'UnderwriterPoolDao',
            'MarketDao', 'ShieldPayoutDao',
            'PoolNameRegistry', 'PositionRegistry'
        ]
    )
    return contract
