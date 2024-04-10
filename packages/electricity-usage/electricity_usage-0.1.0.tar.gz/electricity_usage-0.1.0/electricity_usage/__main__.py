#!usr/bin/env python3
# Module containing the data transformation
from datetime import date, datetime
import json
import click
from electricity_usage.commands import areas, status, run, start, stop

@click.group(help='This is a tool to schedule one or multiple processes to start when there is a local energy production surplus.\n')
def cli():
   pass
cli.add_command(areas.areas)
cli.add_command(status.status)
cli.add_command(run.run)
cli.add_command(start.start)
cli.add_command(stop.stop)

   
if __name__ == '__main__':
    cli()
