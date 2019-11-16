import os

import pytest

from conftest import _get_contract_from_address


"""
    The tests in this file use the following deployed contracts, aka
    fixtures from conftest:
    #. LST_token
    #. Lend_token
    #. ERC20_library
    #. ERC1155_library
    #. CurrencyPool_library
    #. CurrencyDao
    #. ShieldPayoutGraph_library
    #. ShieldPayoutDao
    #. InterestPool_library
    #. InterestPoolDao
    #. UnderwriterPool_library
    #. UnderwriterPoolDao
    #. LoanDao
"""


@pytest.fixture
def ProtocolDao(w3, get_contract,
        LST_token,
        ERC20_library, ERC1155_library,
        CurrencyPool_library, CurrencyDao,
        InterestPool_library, InterestPoolDao,
        UnderwriterPool_library, UnderwriterPoolDao,
        LoanDao
    ):
    interface_codes = {}
    with open(os.path.join(os.path.dirname(os.path.realpath(__file__)),
        os.pardir, 'contracts/interfaces/CurrencyDao.vy')) as f:
            interface_codes['CurrencyDao'] = {
                'type': 'vyper',
                'code': f.read()
            }
    with open(os.path.join(os.path.dirname(os.path.realpath(__file__)),
        os.pardir, 'contracts/interfaces/InterestPoolDao.vy')) as f:
            interface_codes['InterestPoolDao'] = {
                'type': 'vyper',
                'code': f.read()
            }
    with open(os.path.join(os.path.dirname(os.path.realpath(__file__)),
        os.pardir, 'contracts/interfaces/UnderwriterPoolDao.vy')) as f:
            interface_codes['UnderwriterPoolDao'] = {
                'type': 'vyper',
                'code': f.read()
            }
    with open(os.path.join(os.path.dirname(os.path.realpath(__file__)),
        os.pardir, 'contracts/interfaces/LoanDao.vy')) as f:
            interface_codes['LoanDao'] = {
                'type': 'vyper',
                'code': f.read()
            }
    with open('contracts/daos/ProtocolDao.v.py') as f:
        contract_code = f.read()
        # Pass constructor variables directly to the contract
        contract = get_contract(contract_code,
            LST_token.address,
            CurrencyDao.address, CurrencyPool_library.address,
            ERC20_library.address, ERC1155_library.address,
            InterestPoolDao.address, InterestPool_library.address,
            UnderwriterPoolDao.address, UnderwriterPool_library.address,
            LoanDao.address,
            interface_codes=interface_codes)
    return contract
