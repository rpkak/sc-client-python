import logging
from collections.abc import Callable
from typing import Optional

from .connection import Connection
from .game import Game, Result


def start_gameloop(setup, calculate_move, on_result, host='localhost', port=13050, reservation=None, room=None):
    with Connection(host, port, 4096) as conn:
        prepare_gameloop(conn, reservation, room)

        game = None
        go_on = True
        while go_on:
            game, go_on = gameloop_step(
                conn, game, setup, calculate_move, on_result)


def prepare_gameloop(conn, reservation=None, room=None):
    if reservation is not None:
        conn.send(b'<protocol><joinPrepared reservationCode="%s" />' %
                  reservation.encode('utf-8'))
    elif room is not None:
        conn.send(b'<protocol><joinRoom roomId="%s" />' % room.encode('utf-8'))
    else:
        conn.send(b'<protocol><join />')


def gameloop_step(conn, game, setup, calculate_move, on_result):
    element = conn.receive()
    if element is None:
        return game, False
    if element.tag == 'joined':
        game = Game(element.get('roomId'), setup,
                    calculate_move, on_result, conn)
    elif element.tag == 'room' and element.get('roomId') == game.room_id:
        if game.update(element.find('data')):
            return game, False
    else:
        logging.warning('Unexpected xml tag \'%s\' with attributes %s.',
                        element.tag, ', '.join('\'%s=%s\'' % key for key in element.attrib))
    return game, True
