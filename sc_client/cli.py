from importlib.util import module_from_spec, spec_from_file_location

import click
import sys
import os

from .mainloop import start_mainloop
from .project_init import init_project


@click.group()
def scpy():
    pass


@scpy.command(help='Initializes a new project')
@click.option('--directory', '-d', default='.', type=click.Path(file_okay=False, writable=True, readable=False, resolve_path=True), show_default=True, help='Directory of the new project.')
@click.option('--logic', '-f', default='logic.py', show_default=True, help='Name of the logic file.')
@click.option('--setup', '-s', default='setup', show_default=True, help='Name of the function which is called after you join a team.')
@click.option('--calculate-move', '-c', default='calculate_move', show_default=True, help='Name of the function which should return a move.')
@click.option('--no-git', is_flag=True, help='Do not try to initialize git.')
def init(directory, logic, setup, calculate_move, no_git):
    init_project(directory, logic, setup, calculate_move, no_git)


@scpy.command(help='Starts the client.')
@click.option('--host', '-h', default='localhost', show_default=True, help='The host of the server.')
@click.option('--port', '-p', default=13050, type=click.IntRange(0, 49152, max_open=True), show_default=True, help='The port of the server.')
@click.option('--reservation', '-r', help='Reservation to join a room.')
@click.option('--room', help='The room id to join.')
@click.option('--file', '-f', type=click.Path(exists=True, dir_okay=False), default='logic.py', show_default=True, help='The path of the file where the logic is implemented.')
@click.option('--setup', '-s', default='setup', show_default=True, help='A function in \'--file\' which is called after you join a team.')
@click.option('--calculate-move', '-c', default='calculate_move', show_default=True, help='A function in \'--file\' which should return a move.')
def run(host, port, reservation, room, file, setup, calculate_move):
    if reservation is not None and room is not None:
        raise click.UsageError('Either use \'--reservation\' or \'--room\'.')

    logic_spec = spec_from_file_location('logic', file)
    logic = module_from_spec(logic_spec)
    logic_spec.loader.exec_module(logic)

    start_mainloop(
        setup=getattr(logic, setup),
        calculate_move=getattr(logic, calculate_move),
        host=host,
        port=port,
        reservation=reservation,
        room=room
    )
