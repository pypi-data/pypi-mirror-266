import click
import json
import os
import random
import string
from datetime import datetime, timedelta
from pytimeparse import parse
from electricity_usage.commands.area_codes import codes
from electricity_usage import data_dirs 

# the run command is used to create new jobs, 
# it saves its parameters to an input directory which is subsequently processed by the daemon

input_data_directory = data_dirs.get_input_dir_path()
default_deadline = datetime.now()+timedelta(1)  

def generate_filename():
    rand = ''.join(random.choice(string.ascii_letters) for _ in range(16))
    time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    return f"{time}_{rand}.json"

def validate_estimate(ctx, param, estimate):
    check = parse(estimate)
    if type(check) == int:
        return estimate
    raise click.BadParameter(f"estimatre must be in a format accepted by pytimeparse. See https://github.com/wroberts/pytimeparse for more information. Your input {estimate} was not accepted.")

@click.command()
@click.option('--estimate', type=str,required=True, callback=validate_estimate,
        help='estimated runtime of the program in any format as accepted by the pytimeparse package. For more information on the formatting, see https://pypi.org/project/pyytimeparse/.'
        )
@click.option('--deadline', default=default_deadline,
        type=click.DateTime(formats=['%Y-%m-%d', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%d %H:%M:%S']), 
        help='latest date when the program should be finished; defaults to in 24h'
        )
@click.option('--commandline', type=str, help='the command line to be executed', required=True)

def run(estimate,deadline,commandline): 
    '''adds a process to the queue. this can only be done after electricity usage has been started'''
    if deadline.time() == datetime.min.time():  # In case the deadline is just a date without a specific time set
        deadline = deadline.replace(hour=0, minute=0, second=0)  # Set time as 00:00:00
    
    deadline_str = deadline.strftime("%Y-%m-%d %H:%M:%S")
    data = {
        "estimate": estimate,
        "deadline": deadline_str,
        "commandline": commandline
    }
    print(data)
    json_document = json.dumps(data)
    json_filename = generate_filename()

    with open(os.path.join(input_data_directory, json_filename), 'w') as f:
        f.write(json_document)
    
    return os.path.join(input_data_directory, json_filename)

