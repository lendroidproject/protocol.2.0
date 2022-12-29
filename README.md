# Deleuze package with Lendroid protocol v2.0
The Deleuze package comprises the following tools. Please feel free to use them (in any combination) to deploy your own 4-token-model, ant-fragile lending ecosystem.

## Smart contracts
Lendroid Protocol version 2.0

The smart contracts have been written in [Vyper version 0.1.16](https://vyper.readthedocs.io "Vyper ReadTheDocs") and compiled using using the [Brownie Framework](https://eth-brownie.readthedocs.io "eth-brownie"). Unit and functional test cases have been written using the Pytest framework.

- [Github](https://github.com/lendroidproject/protocol.2.0)
- [Audit report](https://github.com/lendroidproject/protocol.2.0/blob/master/audit-report.pdf)

## Javascript library
Nodejs implementation for user interface to interact with the smart contracts.
- [Github](https://github.com/lendroidproject/lendroid-2-js)
## UI template
A base template of the user interface.
- [Github](https://github.com/lendroidproject/wallet-ui)
## Technical Documentation
Technical Documentation on how to use the Javascript library
- [Github](https://github.com/lendroidproject/lendroid2js-documentation)

## How to use this repo

### Installation and setup
* Clone this repository

  `git clone <repo>`

* cd into the cloned repo

  `cd protocol.2.0`

* Install dependencies via npm

  `npm install ganache-cli@istanbul -g`


* Install Python and Vyper v0.1.0-beta.16

  * Python 3.7 is a pre-requisite, and can be installed from [here](https://www.python.org/downloads "Python version downloads")

  * Install virtualenv from pip

    `pip install virtualenv` or `pip3 install virtualenv`

  * Create a virtual environment

    `virtualenv -p python3.7 --no-site-packages ~/vyper-venv`

  * Activate Vyper's virtual environment

    `source ~/vyper-venv/bin/activate`

  * Install dependencies from requirements.txt via pip

    `pip install -r requirements.txt`

### Test and development

* Activate Vyper's virtual environment

  `source ~/vyper-venv/bin/activate`


* Compile using brownie

  `brownie compile`

* Run the tests with coverage

  `brownie test --coverage`

  <i>Note : Version 1.5.1 of brownie requires the following patch:
  * Within the virtual env, navigate to the brownie package installed in python3 site-packages.
  * edit `brownie/network/transaction.py` and add a `try, catch` around the line `pc = last["pc_map"][trace[i]["pc"]]` like this
  ```
  try:
      pc = last["pc_map"][trace[i]["pc"]]
  except KeyError:
      continue
  ```
  </i>


_Note_: When the development / testing session ends, deactivate the virtualenv

`(vyper-venv) $ deactivate`
