from __future__ import annotations

import socket
import xml.etree.ElementTree as ET
from io import BytesIO
from typing import Union


class Connection:
    def __init__(self, host: str, port: int, bufsize: int):
        self.host = host
        self.port = port
        self.bufsize = bufsize
        self.socket: socket.socket = None
        self.elements: list[ET.Element] = []

    def __enter__(self) -> Connection:
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.host, self.port))
        self.elements = []
        return self

    def send(self, content: Union[bytes, ET.Element]) -> None:
        if isinstance(content, ET.Element):
            bio = BytesIO()
            ET.ElementTree(content).write(bio, 'utf-8')
            content = bio.getvalue()

        self.socket.send(content)

    def receive(self) -> ET.Element:
        while not self.elements:
            response = b''

            while not (response.endswith(b'</room>') or response.endswith(b'</protocol>')):
                response += self.socket.recv(self.bufsize)

            if b'</protocol>' in response:
                return None

            if response.startswith(b'<protocol>'):
                response = response[len(b'<protocol>'):]

            response = b'<_>' + response + b'</_>'
            element = ET.fromstring(response)

            self.elements.extend(element)

        return self.elements.pop(0)

    def __exit__(self, type, value, traceback) -> None:
        self.socket.close()
        self.socket = None
