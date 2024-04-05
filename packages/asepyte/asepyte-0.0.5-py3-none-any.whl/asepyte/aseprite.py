# -*- coding: utf-8 -*-

from io import BytesIO

from asepyte.header import HEADER_SIZE, Header


class Aseprite:
    def __init__(self, header: Header):
        self.header = header

    def encode(self) -> bytes:
        buffer = BytesIO()
        buffer.write(self.header.encode())
        return buffer.getvalue()

    @classmethod
    def decode(cls, data: bytes):
        return cls(Header.decode(data[:HEADER_SIZE]))
