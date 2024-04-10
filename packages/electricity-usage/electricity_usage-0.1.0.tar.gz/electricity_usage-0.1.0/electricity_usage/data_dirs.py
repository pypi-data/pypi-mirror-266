import os
import platformdirs

# Creates an input_dir folder for communication with the Daemon
def create_input_dir_path():
    # Get directory for application data
    data_dir = platformdirs.user_data_dir(appname='electricity_usage')

    # Create electricity_usage directory if it doesn't exist
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)

    # Create input_dirs directory if it doesn't exist
    input_dirs_dir = os.path.join(data_dir, 'input_dirs')
    if not os.path.exists(input_dirs_dir):
        os.makedirs(input_dirs_dir)

    # Create input_dir in the input_dirs directory if it doesn't exist
    input_dir = os.path.join(input_dirs_dir, 'input_dir')
    if not os.path.exists(input_dir):
        os.makedirs(input_dir)
    return input_dir

# Returns the path to the input_dir folder
def get_input_dir_path():
    # Get directory for application data
    data_dir = platformdirs.user_data_dir(appname='electricity_usage')

    # Create input_dirs directory
    input_dirs_dir = os.path.join(data_dir, 'input_dirs')

    # Create input_dir in the input_dirs directory
    input_dir = os.path.join(input_dirs_dir, 'input_dir')

    return input_dir
