import os
import sys
from importlib.util import module_from_spec, spec_from_file_location
from time import sleep

from .gameloop import start_gameloop
from .project_init import init_project

from argparse import ArgumentParser, SUPPRESS


def dir_path(string):
    if os.path.isdir(string):
        return string
    else:
        raise NotADirectoryError(string)


def file_path(string):
    if os.path.isfile(string):
        return string
    else:
        raise NotADirectoryError(string)


def scpy():
    parser = ArgumentParser()
    parser.set_defaults(command='usage')
    subparsers = parser.add_subparsers()
    init_parser = subparsers.add_parser('init')
    init_parser.set_defaults(command='init')
    init_parser.add_argument('-d', '--directory', default='.',
                             type=dir_path, help='Directory of the new project.')
    init_parser.add_argument(
        '-f', '--logic', default='logic.py', help='Name of the logic file.')
    init_parser.add_argument('-s', '--setup', default='setup',
                             help='Name of the function which is called after you join a team.')
    init_parser.add_argument('-c', '--calculate-move', default='calculate_move',
                             help='Name of the function which should return a move.')
    init_parser.add_argument('-r', '--on-result', default='on_result',
                             help='Name of the function which is called when the result is ready.')

    run_parser = subparsers.add_parser('run', add_help=False)
    run_parser.add_argument('--help', action='help',
                            help='show this help message and exit', default=SUPPRESS)
    run_parser.set_defaults(command='run')
    run_parser.add_argument(
        '-h', '--host', default='localhost', help='The host of the server.')
    run_parser.add_argument('-p', '--port', default=13050,
                            type=int, help='The port of the server.')
    g = run_parser.add_mutually_exclusive_group()
    g.add_argument('-r', '--reservation',
                   help='Reservation to join a room.')
    g.add_argument('--room', help='The room id to join.')
    run_parser.add_argument('-f', '--file', type=file_path, default='logic.py',
                            help='The path of the file where the logic is implemented.')
    run_parser.add_argument('-s', '--setup', default='setup',
                            help='A function in \'--file\' which is called after you join a team.')
    run_parser.add_argument('-c', '--calculate-move', default='calculate_move',
                            help='A function in \'--file\' which should return a move.')
    run_parser.add_argument('-e', '--on-result', default='on_result',
                            help='A function in \'--file\' which is called when the result is ready.')
    run_parser.add_argument('-l', '--loop', type=int,
                            default=1, help='Number of times to be played.')

    args = parser.parse_args()
    if args.command == 'usage':
        parser.print_usage()
    elif args.command == 'init':
        init_project(args.directory, args.logic, args.setup,
                     args.calculate_move, args.on_result)
    elif args.command == 'run':
        sys.path.insert(0, os.getcwd())

        logic_spec = spec_from_file_location('logic', args.file)
        logic = module_from_spec(logic_spec)
        logic_spec.loader.exec_module(logic)

        for _ in range(args.loop):
            start_gameloop(
                setup=getattr(logic, args.setup),
                calculate_move=getattr(logic, args.calculate_move),
                on_result=getattr(logic, args.on_result),
                host=args.host,
                port=args.port,
                reservation=args.reservation,
                room=args.room
            )
            if args.loop != 1:
                sleep(1)
