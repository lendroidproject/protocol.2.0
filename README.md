# protocol.2.0
Lendroid Protocol version 2

## Framework
The smart contracts have been written in [Vyper version 0.1.13](https://vyper.readthedocs.io "Vyper ReadTheDocs") and compiled using using the [Truffle Framework](https://truffleframework.com/docs/truffle/overview "Truffle overview"). Unit and functional test cases have been written using the Pytest framework.

Please use Git commits according to this article: https://chris.beams.io/posts/git-commit

## Installation and setup
* Clone this repository

  `git clone <repo>`

* cd into the cloned repo

  `cd protocol.2.0`

* Install dependencies via npm

  `npm install`


* Install Python and Vyper v0.1.0-beta.14

  * Python 3.6+ is a pre-requisite, and can be installed from [here](https://www.python.org/downloads "Python version downloads")

  * Install virtualenv from pip

    `pip install virtualenv` or `pip3 install virtualenv`

  * Create a virtual environment

    `virtualenv -p python3.6 --no-site-packages ~/vyper-venv`

  * Activate Vyper's virtual environment

    `source ~/vyper-venv/bin/activate`

  * Install Vyper v0.1.0-beta.14

    `pip install vyper==0.1.0b14`

  * Install dependencies from requirements.txt via pip

    `pip install -r requirements.txt`

## Test and development

* Activate Vyper's virtual environment

  `source ~/vyper-venv/bin/activate`


* Run the tests using [Pytest Xdist](https://docs.pytest.org/en/3.0.1/xdist.html)

  `pytest -n 8`


_Note_: When the development / testing session ends, deactivate the virtualenv

`(vyper-venv) $ deactivate`
