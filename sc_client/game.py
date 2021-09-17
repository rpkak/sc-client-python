from __future__ import annotations

import logging
import xml.etree.ElementTree as ET
from collections.abc import Callable, Iterator
from enum import Enum
from typing import Optional

from .connection import Connection


class Team(Enum):
    ONE = 1
    TWO = 2


class PieceType(Enum):
    Herzmuschel = [(1, 1), (1, -1)]
    Moewe = [(1, 0), (-1, 0), (0, 1), (0, -1)]
    Seestern = [(1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    Robbe = [(2, 1), (1, 2), (2, -1), (1, -2),
             (-2, 1), (-1, 2), (-2, -1), (-1, -2)]


class Game:
    def __init__(self, room_id: str, setup: Callable[[Game], None], calculate_move: Callable[[Game], None], on_result: Callable[[Game, Result], None], connection: Connection):
        self.room_id = room_id
        self.setup = setup
        self.calculate_move = calculate_move
        self.on_result = on_result
        self.connection = connection
        self.team: Team = None
        self.pieces: list[Piece] = None
        self.start_team: Team = None
        self.turn: int = 0
        self.last_move: Move = None
        self.ambers = {Team.ONE: 0, Team.TWO: 0}

    def update(self, element: ET.Element) -> None:
        if element.get('class') == 'memento':
            self.turn = int(element.find('state').get('turn'))
            self.start_team = Team[element.find('state/startTeam').text]
            self.pieces = [Piece.from_xml(entry, self) for entry in element.findall(
                'state/board/pieces/entry')]

            last_move = element.find('state/lastMove')
            if last_move:
                self.last_move = Move.from_xml(last_move, self)

            for entry in element.findall('state/ambers/entry'):
                self.ambers[Team[entry.find('team').text]] = int(
                    entry.find('int').text)
        elif element.get('class') == 'welcomeMessage':
            self.team = Team[element.get('color')]
            self.setup(self)
        elif element.get('class') == 'moveRequest':
            move = self.calculate_move(self)
            self.connection.send(move.to_xml())
        elif element.get('class') == 'result':
            self.on_result(self, Result.from_xml(element))
            return True
        else:
            logging.warning(
                'Unexpected data xml tag with class \'%s\'.', element.get('class'))

    def get_piece(self, x: int, y: int) -> Optional[Piece]:
        for piece in self.pieces:
            if piece.x == x and piece.y == y:
                return piece

    def get_board(self) -> list[list[Optional[Piece]]]:
        return [[self.get_piece(x, y) for y in range(8)] for x in range(8)]

    def get_possible_moves(self) -> Iterator[Move]:
        for piece in self.pieces:
            if piece.team == self.team:
                yield from piece.get_possible_moves()


class Move:
    @classmethod
    def from_xml(cls, element: ET.Element, game: Game) -> Move:
        from_ = element.find('from')
        to = element.find('to')
        from_x = int(from_.get('x'))
        from_y = int(from_.get('y'))
        to_x = int(to.get('x'))
        to_y = int(to.get('y'))
        piece = game.get_piece(to_x, to_y)
        return cls(
            piece=piece,
            from_x=from_x,
            from_y=from_y,
            to_x=to_x,
            to_y=to_y
        )

    def __init__(self, piece: Piece, from_x: int, from_y: int, to_x: int, to_y: int):
        self.piece = piece
        self.to_x = to_x
        self.to_y = to_y
        self.from_x = from_x
        self.from_y = from_y

    def to_xml(self) -> ET.Element:
        room = ET.Element('room', attrib={'roomId': self.piece.game.room_id})
        move = ET.SubElement(room, 'data', attrib={'class': 'move'})
        ET.SubElement(move, 'from', attrib={
                      'x': str(self.from_x), 'y': str(self.from_y)})
        ET.SubElement(move, 'to', attrib={
                      'x': str(self.to_x), 'y': str(self.to_y)})
        return room


class Piece:
    @classmethod
    def from_xml(cls, element: ET.Element, game: Game) -> Piece:
        coordinates = element.find('coordinates')
        piece = element.find('piece')
        return cls(
            x=int(coordinates.get('x')),
            y=int(coordinates.get('y')),
            team=Team[piece.get('team')],
            type=PieceType[piece.get('type')],
            count=int(piece.get('count')),
            game=game
        )

    def __init__(self, x: int, y: int, team: Team, type: PieceType, count: int, game: Game):
        self.x = x
        self.y = y
        self.team = team
        self.type = type
        self.count = count
        self.game = game

    def get_possible_moves(self) -> Iterator[Move]:
        if self.team == Team.ONE:
            possible_move_positions = [(self.x + x, self.y + y)
                                       for x, y in self.type.value]
        else:
            possible_move_positions = [(self.x - x, self.y + y)
                                       for x, y in self.type.value]

        for x, y in possible_move_positions:
            piece = self.game.get_piece(x, y)
            if 0 <= x < 8 and 0 <= y < 8 and (piece is None or piece.team != self.team):
                yield Move(self, self.x, self.y, x, y)


class Result:
    @classmethod
    def from_xml(cls, element: ET.Element) -> Result:
        definitions = element.findall('definition/fragment')
        score_index = definitions.index(next(
            definition for definition in definitions if definition.get('name') == 'Siegpunkte')) + 1

        scores = {}
        regular = True
        for entry in element.findall('scores/entry'):
            scores[Team[entry.find('player').get('team')]] = int(
                entry.find('score/part[%s]' % score_index).text)

            regular = regular and entry.find('score').get('cause') == 'REGULAR'

        winner = element.find('winner')
        if winner is not None:
            winner = Team[winner.get('team')]

        return cls(
            scores=scores,
            winner=winner,
            regular=regular
        )

    def __init__(self, scores: dict[Team, int], winner: Optional[Team], regular: bool):
        self.scores = scores
        self.winner = winner
        self.regular = regular
