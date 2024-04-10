import pytest
from mock import patch
import requests
import electricity_usage.em_data


@pytest.fixture()
def em_with_overhead():
    requests.status_code = 200
    requests.json = {'powerConsumptionTotal': 5, 'powerProductionTotal': 1}
    print('flag')

@pytest.fixture()
def em_no_overhead():
    requests.status_code = 200
    requests.json = {'powerConsumptionTotal': 1, 'powerProductionTotal': 5}

@pytest.fixture()
def em_error():
    requests.status_code = 404
    requests.json = {}


def test_get_power_data(mocker, em_with_overhead):
    fake_resp = mocker.Mock()
    fake_json = mocker.Mock(return_value=em_with_overhead)

    mocker.patch("electricity_usage.em_data.requests.get", return_value=fake_json)
    prod, con = electricity_usage.em_data.get_power_data('DE', 'SOME_API_TOKEN')

    #assert em_data.url = "https://api.electricitymap.org/v3/power-breakdown/latest?zone=DE"
    assert prod == 5
    assert con == 1


