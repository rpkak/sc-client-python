import logging
import xml.etree.ElementTree as ET
from enum import Enum


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
    def __init__(self, room_id, calculate_move, setup, connection):
        self.room_id = room_id
        self.calculate_move = calculate_move
        self.setup = setup
        self.connection = connection
        self.team = None
        self.pieces = None
        self.start_team = None
        self.turn = 0
        self.last_move = None
        self.ambers = {Team.ONE: 0, Team.TWO: 0}

    def update(self, element):
        if element.get('class') == 'memento':
            self.turn = int(element.find('state').get('turn'))
            self.start_team = element.find('state/startTeam').text
            self.pieces = [Piece.from_xml(entry, self) for entry in element.findall(
                'state/board/pieces/entry')]

            last_move = element.find('state/lastMove')
            if last_move:
                self.last_move = Move.from_xml(last_move, self)

            ambers = element.findall('state/ambers/entry')
            if ambers:
                self.ambers = dict((Team[entry.find('team').text], int(
                    entry.find('int').text)) for entry in ambers)
        elif element.get('class') == 'welcomeMessage':
            self.team = Team[element.get('color')]
            self.setup(self)
        elif element.get('class') == 'moveRequest':
            move = self.calculate_move(self)
            self.connection.send(move.to_xml())
        else:
            logging.warning(
                'Unexpected data xml tag with class \'%s\'.', element.get('class'))

    def get_piece(self, x, y):
        for piece in self.pieces:
            if piece.x == x and piece.y == y:
                return piece

    def get_possible_moves(self):
        for piece in self.pieces:
            if piece.team == self.team:
                yield from piece.get_possible_moves()


class Move:
    @classmethod
    def from_xml(cls, element, game):
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

    def __init__(self, piece, from_x, from_y, to_x, to_y):
        self.piece = piece
        self.to_x = to_x
        self.to_y = to_y
        self.from_x = from_x
        self.from_y = from_y

    def to_xml(self):
        room = ET.Element('room', attrib={'roomId': self.piece.game.room_id})
        move = ET.SubElement(room, 'data', attrib={'class': 'move'})
        ET.SubElement(move, 'from', attrib={
                      'x': str(self.from_x), 'y': str(self.from_y)})
        ET.SubElement(move, 'to', attrib={
                      'x': str(self.to_x), 'y': str(self.to_y)})
        return room


class Piece:
    @classmethod
    def from_xml(cls, element, game):
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

    def __init__(self, x, y, team, type, count, game):
        self.x = x
        self.y = y
        self.team = team
        self.type = type
        self.count = count
        self.game = game

    def get_possible_moves(self):
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
