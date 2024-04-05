# -*- coding: utf-8 -*-

from os import PathLike
from typing import Protocol

from asepyte.aseprite import Aseprite

__version__ = "0.0.5"


class _BinaryReadableFile(Protocol):
    def read(self, n: int = -1) -> bytes: ...


class _BinaryWritableFile(Protocol):
    def write(self, b: bytes) -> int: ...


def encode(data: Aseprite) -> bytes:
    return data.encode()


def decode(data: bytes) -> Aseprite:
    return Aseprite.decode(data)


def dumps(data: Aseprite) -> bytes:
    return encode(data)


def loads(data: bytes) -> Aseprite:
    return decode(data)


def dump(data: Aseprite, fp: _BinaryWritableFile) -> None:
    fp.write(dumps(data))


def load(fp: _BinaryReadableFile) -> Aseprite:
    return loads(fp.read())


def dump_file(data: Aseprite, file: PathLike) -> None:
    with open(file, "wb") as f:
        dump(data, f)


def load_file(file: PathLike) -> Aseprite:
    with open(file, "rb") as f:
        return load(f)
