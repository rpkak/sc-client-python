import logging
from collections.abc import Callable

from .connection import Connection
from .game import Game, Result


def start_gameloop(setup: Callable[[Game], None], calculate_move: Callable[[Game], None], on_result: Callable[[Game, Result], None], host: str='localhost', port=13050, reservation=None, room=None):
    with Connection(host, port, 4096) as conn:
        if reservation is not None:
            conn.send('<joinPrepared reservationCode="%s" />' % reservation)
        elif room is not None:
            conn.send('<joinRoom roomId="%s" />' % room)
        else:
            conn.send(b'<protocol><join />')

        game = None
        while True:
            element = conn.receive()
            if element is None:
                break

            if element.tag == 'joined':
                game = Game(element.get('roomId'), setup,
                            calculate_move, on_result, conn)
            elif element.tag == 'room' and element.get('roomId') == game.room_id:
                if game.update(element.find('data')):
                    break
            else:
                logging.warning('Unexpected xml tag \'%s\' with attributes %s.',
                                element.tag, ', '.join('\'%s=%s\'' % key for key in element.attrib))
