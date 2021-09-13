import os
from contextlib import redirect_stderr, redirect_stdout

logic_template = '''import logging

from sc_client import Game, Move, Result


def SETUP(game: Game) -> None:
    logging.info('Joined team \\'%s\\' in room \\'%s\\'', game.team, game.room_id)


def CALCULATE_MOVE(game: Game) -> Move:
    move = next(game.get_possible_moves())
    logging.info('Moving %s from %s, %s to %s, %s.', move.piece.type.name,
                 move.from_x, move.from_y, move.to_x, move.to_y)
    return move

def ON_RESULT(game: Game, result: Result) -> None:
    if game.team == result.winner:
        logging.info('I won!')
    else:
        logging.info('I lost!')
'''


def init_project(directory, logic, setup, calculate_move, on_result):
    logic_file_content = logic_template \
        .replace('SETUP', setup) \
        .replace('CALCULATE_MOVE', calculate_move) \
        .replace('ON_RESULT', on_result)

    logic = '%s%s%s' % (directory, os.sep, logic)

    logic_dir = os.path.dirname(logic)
    if not os.path.exists(logic_dir):
        os.makedirs(logic_dir)

    with open(logic, 'w') as f:
        f.write(logic_file_content)
