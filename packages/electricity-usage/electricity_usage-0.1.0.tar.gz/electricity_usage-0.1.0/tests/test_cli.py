import pytest
from mock import patch
import platformdirs
import os
import time
from click.testing import CliRunner
from electricity_usage.__main__ import cli

@pytest.fixture
def runner():
    return CliRunner()
@pytest.fixture
def data_dir():
    data_dir = platformdirs.user_data_dir(appname='electricity_usage')
    return data_dir

######  areas  ######
def test_areas_command(runner):
    result = runner.invoke(cli, ['areas'])
    assert result.exit_code == 0


######  queue  ######
def test_queue_command(runner):
    pass


######  start  ######
def test_start_command_default(runner):
    result = runner.invoke(cli, ['start'])
    assert result.exit_code == 0

def test_start_command_with_valid_area(runner):
    result = runner.invoke(cli, ['start', '--area', 'BE'])
    assert result.exit_code == 0

def test_start_command_with_invalid_area(runner):
    result = runner.invoke(cli, ['start', '--area', 'FF'])
    assert result.exit_code == 2


######  run  ######
def test_run_command_valid(runner, data_dir):
    result = runner.invoke(cli, ['run', '--estimate 1 --deadline "2025-02-22" --commandline "command"'])
    #assert result.exit_code == 0
    assert os.path.isdir(os.path.join(data_dir, 'input_dirs/input_data')) == True

######  stop  ######
def test_stop_command_valid(runner, data_dir):
    result = runner.invoke(cli, ['stop'])
    assert result.exit_code == 0
    time.sleep(2)  #wait for stop command to be done deleting directories
    assert os.path.isdir(data_dir)==False
