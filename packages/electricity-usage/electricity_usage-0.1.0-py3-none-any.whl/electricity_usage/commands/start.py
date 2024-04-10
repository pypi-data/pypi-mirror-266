import click
import os
import platformdirs
import threading
from electricity_usage.commands.area_codes import codes, validate_code
from electricity_usage import data_dirs
from electricity_usage import daemon

# the start command creates a daemon instance and starts its run method as a daemon process

@click.command()
@click.option('--area',type=str, default='DE', callback=validate_code, help="area code corresponding to the local area as shown by 'electricity_usage areas'. The default value for this is 'DE' corresponding to Germany")
@click.option('--em_auth_token', type=str, default=None, help="Optional token for accessing Electricity Maps service. This is not mandatory for locations that provide data about electricity consumption and production for free.")

def start(area, em_auth_token):
    '''starts the tool background process (demon)'''
    # build directory for daemon communication
    if em_auth_token is None:
        print("You're not using an Electricity Maps auth token. While this should suffice for most purposes, please note that certain locations may require an Electricity Maps auth token for full data access.")
    data_dir = data_dirs.create_input_dir_path()
    # create daemon instance
    #daemon_instance = daemon.Daemon(os.getenv("EM_API_KEY"), area, data_dir)
    daemon_instance = daemon.Daemon(em_auth_token, area, data_dir)

    # start daemon.run in seperate thread
    daemon_thread = threading.Thread(target=daemon_instance.run) 

    daemon_thread.start()

