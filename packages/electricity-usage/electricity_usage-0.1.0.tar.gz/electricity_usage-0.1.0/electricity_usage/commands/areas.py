import click
from .area_codes import areas_str

@click.command()
def areas():
    '''shows list of available area codes and the corresponding area codes'''
    print('ElectricityMaps offers data from areas corresponding to the following areas\n')
    for a in areas_str:
        print(a)
