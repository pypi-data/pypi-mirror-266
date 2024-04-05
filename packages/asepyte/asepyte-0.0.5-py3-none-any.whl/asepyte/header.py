# -*- coding: utf-8 -*-

from struct import calcsize, pack, unpack
from typing import Final, Sequence

MAGIC_NUMBER: Final[int] = 0xA5E0
COLOR_DEPTHS: Final[Sequence[int]] = 8, 16, 32

# noinspection SpellCheckingInspection
HEADER_FORMAT: Final[bytes] = b"<IHHHHHIHIIB3pHBBhhHH84p"
HEADER_SIZE: Final[int] = calcsize(HEADER_FORMAT)


class Header:
    filesize: int
    """
    File size
    """

    magic_number: int
    """
    Magic number (0xA5E0)
    """

    frames: int
    width_in_pixels: int
    height_in_pixels: int

    color_depth: int
    """
    bits per pixel
      * 32 bpp = RGBA
      * 16 bpp = Grayscale
      * 8 bpp = Indexed
    """

    flags: int
    """
    1 = layer opacity has valid value
    """

    speed: int
    """
    milliseconds between frame, like in FLC files
    .. deprecated::
       You should use the frame duration field from each frame header
    """

    padding1: int  # set be 0
    padding2: int  # set be 0

    palette_entry: int
    """
    Palette entry (index) which represent transparent color
    in all non-background layers (only for Indexed sprites).
    """

    padding3: bytes  # Ignore these bytes

    number_of_colors: int
    """
    0 means 256 for old sprites
    """

    pixel_width: int
    """
    pixel ratio is "pixel width/pixel height".
    If this or pixel height field is zero, pixel ratio is 1:1
    """

    pixel_height: int

    x_position_of_the_grid: int
    y_position_of_the_grid: int

    grid_width: int
    """
    zero if there is no grid, grid size is 16x16 on Aseprite by default
    """

    grid_height: int
    """
    zero if there is no grid
    """

    reserve: bytes

    def __init__(
        self,
        filesize: int,
        magic_number: int,
        frames: int,
        width_in_pixels: int,
        height_in_pixels: int,
        color_depth: int,
        flags: int,
        speed: int,
        padding1: int,
        padding2: int,
        palette_entry: int,
        padding3: bytes,
        number_of_colors: int,
        pixel_width: int,
        pixel_height: int,
        x_position_of_the_grid: int,
        y_position_of_the_grid: int,
        grid_width: int,
        grid_height: int,
        reserve: bytes,
    ):
        if magic_number != MAGIC_NUMBER:
            raise ValueError(f"Invalid magic number: 0x{magic_number:02X}")
        if color_depth not in COLOR_DEPTHS:
            raise ValueError(f"Unexpected color depth: {color_depth}")

        self.filesize = filesize
        self.magic_number = magic_number
        self.frames = frames
        self.width_in_pixels = width_in_pixels
        self.height_in_pixels = height_in_pixels
        self.color_depth = color_depth
        self.flags = flags
        self.speed = speed
        self.padding1 = padding1
        self.padding2 = padding2
        self.palette_entry = palette_entry
        self.padding3 = padding3
        self.number_of_colors = number_of_colors
        self.pixel_width = pixel_width
        self.pixel_height = pixel_height
        self.x_position_of_the_grid = x_position_of_the_grid
        self.y_position_of_the_grid = y_position_of_the_grid
        self.grid_width = grid_width
        self.grid_height = grid_height
        self.reserve = reserve

    def encode(self) -> bytes:
        data = pack(
            HEADER_FORMAT,
            self.filesize,
            self.magic_number,
            self.frames,
            self.width_in_pixels,
            self.height_in_pixels,
            self.color_depth,
            self.flags,
            self.speed,
            self.padding1,
            self.padding2,
            self.palette_entry,
            self.padding3,
            self.number_of_colors,
            self.pixel_width,
            self.pixel_height,
            self.x_position_of_the_grid,
            self.y_position_of_the_grid,
            self.grid_width,
            self.grid_height,
            self.reserve,
        )
        assert len(data) == HEADER_SIZE
        return data

    @classmethod
    def decode(cls, data: bytes):
        if len(data) != HEADER_SIZE:
            raise ValueError(f"Invalid header bytes: {len(data)}")
        return cls(*unpack(HEADER_FORMAT, data[:HEADER_SIZE]))
