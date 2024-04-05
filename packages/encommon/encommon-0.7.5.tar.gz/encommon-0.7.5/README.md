# Enasis Network Common Library

Common classes and functions used in various public and private projects for
[Enasis Network](https://github.com/enasisnetwork).

[![](https://img.shields.io/github/actions/workflow/status/enasisnetwork/encommon/build.yml?style=flat-square&label=GitHub%20actions)](https://github.com/enasisnetwork/encommon/actions)<br>
[![codecov](https://codecov.io/gh/enasisnetwork/encommon/graph/badge.svg?token=7PGOXKJU0E)](https://codecov.io/gh/enasisnetwork/encommon)<br>
[![](https://img.shields.io/readthedocs/encommon?style=flat-square&label=Read%20the%20Docs)](https://encommon.readthedocs.io/en/stable)<br>
[![](https://img.shields.io/pypi/v/encommon.svg?style=flat-square&label=PyPi%20version)](https://pypi.org/project/encommon)<br>
[![](https://img.shields.io/pypi/dm/encommon?style=flat-square&label=PyPi%20downloads)](https://pypi.org/project/encommon)

## Installing the package
Installing stable from the PyPi repository
```
pip install encommon
```
Installing latest from GitHub repository
```
pip install git+https://github.com/enasisnetwork/encommon
```

## Documentation
Documentation is on [Read the Docs](https://encommon.readthedocs.io).
Should you venture into the sections below you will be able to use the
`sphinx` recipe to build documention in the `docs/html` directory.

## Quick start for local development
Start by cloning the repository to your local machine.
```
git clone https://github.com/enasisnetwork/encommon.git
```
Set up the Python virtual environments expected by the Makefile.
```
make -s venv-create
```

### Execute the linters and tests
The comprehensive approach is to use the `check` recipe. This will stop on
any failure that is encountered.
```
make -s check
```
However you can run the linters in a non-blocking mode.
```
make -s linters-pass
```
And finally run the various tests to validate the code and produce coverage
information found in the `htmlcov` folder in the root of the project.
```
make -s pytest
```

## Build and upload to PyPi
Build the package.
```
make -s pypackage
```
Upload to the test PyPi.
```
make -s pypi-upload-test
```
Upload to the prod PyPi.
```
make -s pypi-upload-prod
```
