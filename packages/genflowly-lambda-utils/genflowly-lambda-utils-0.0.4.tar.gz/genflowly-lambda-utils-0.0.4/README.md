## Project setup
* `git clone https://github.com/GenFlowly/lambda-utils.git`
* `python3 -m venv venv` or windows `py -m venv venv`
* `source venv/bin/activate` or windows `.\venv\Scripts\activate`
* `python -m pip install pip-tools`
* `pip install -r requirements.txt`
* `pip-compile requirements-test.in`
* `pip-compile requirements.in`
* `pip-sync requirements-test.txt`
* `pip-sync requirements.txt`

## Before checking in code 
* `flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics`
* `flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics`

# Deploying
* `sh deployment.sh`

