# Welcome to electricity_usage

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![GitHub Workflow Status](https://img.shields.io/github/actions/workflow/status/weyandtim/electricity_usage/ci.yml?branch=main)](https://github.com/weyandtim/electricity_usage/actions/workflows/ci.yml)
[![Documentation Status](https://readthedocs.org/projects/electricity_usage/badge/)](https://electricity_usage.readthedocs.io/)
[![codecov](https://codecov.io/gh/weyandtim/electricity_usage/branch/main/graph/badge.svg)](https://codecov.io/gh/weyandtim/electricity_usage)

The electricity_usage package provides a scheduler which will kick off processes only when there is a surplus in local energy production.
For more information see the [usage](usage.html) documentation.

## Installation

The Python package `electricity_usage` can be installed by cloning the git repository and installing it using pip install.

```
git clone https://github.com/weyandtim/electricity_usage
pip install electricity_usage
```
To fully utilize this package, you also need a subscription to Electricity Maps, available here `<https://api-portal.electricitymaps.com/>`.  
Upon subscription, you'll receive an authentication token. This token is used to access additional electricity production and consumption data for specific locations from Electricity Maps.  
We incorporate the token using an optional parameter `--em_auth_token`, in our `start` command.  
Please note that the majority of locations do not require an authentication token.  
More information about Electricity Maps can be found in :ref:`api-ref`.

<!-- @Tim kann sein dass das nicht reicht, deine Entscheidung -->


## Development installation

If you want to contribute to the development of `electricity_usage`, we recommend
the following editable installation from this repository:

```
git clone https://github.com/weyandtim/electricity_usage
cd electricity_usage
python -m pip install --editable .[tests]
```

Having done so, the test suite can be run using `pytest`:

```
python -m pytest
```


## Contributing

This project was done as a software practical by Tim Weyand and Nemo Glade, under supervision of Dominic Kempf.

If you wish to contribute to electricity\_usage open an issue in the issue tracker of the [GitHub project](https://github.com/weyandtim/electricity_usage/issues).


## Acknowledgments

This repository was set up using the [SSC Cookiecutter for Python Packages](https://github.com/ssciwr/cookiecutter-python-package).
The project relies on data from [Electricity Maps](https://github.com/electricitymaps/electricitymaps-contrib).
