r"""
This file is part of eduworld package.

This class defines Board that can read file based world-boards

=== LICENSE INFO ===

Copyright (c) 2024 - Stanislav Grinkov

The eduworld package is free software: you can redistribute it
and/or modify it under the terms of the GNU General Public License
as published by the Free Software Foundation, either version 3
of the License, or (at your option) any later version.

The package is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with the algoworld package.
If not, see `<https://www.gnu.org/licenses/>`_.
"""

import sys
import re
from pathlib import Path

from .tile import Tile
from .board import Board
from .robot import Robot

# pylint: disable=too-few-public-methods


class MapDef:
    """Class encapsulating logic for parsing world file definitions
    World file format defined as follows.
    - It should specify one definition per line in the format
      DEF_NAME: PARAMETERS
    - Empty lines or lines starts with # will be ignored
    - PARAMETERS:
        - Format: name=value. There is no spaces around the equals sign!
        - parameters are separated by space
        - case insensitive
        - can appear in any order
        - unknown parameter names are ignored
    - The accepted DEF_NAME: PARAMETERS
        - map: rows=int cols=int
          both "rows" and "cols" parameters are *required*
        - robot: x=int y=int
          initial position of 'default' robot in this world
        - tile: x=int y=int beepers=N,* temperature=float radiation=float color="" walls=""
            - Required: "x" and "y" parameters
            - Other parameters are optional
            - Parameter "beepers" accepts either special '*' char value
              which means 'inifinite' amount, or int value - amount of beepers
            - radiation and temperature accept any float value
              (use dot to separate the whole and fractional parts)
            - Parameter "color" accepts any color value described in Tk docs
              but without spaces: https://tcl.tk/man/tcl8.6/TkCmd/colors.htm
            - Parameter "walls" describe walls around the cell
              t - top, b - bottom, l - left, r - right, f - full
              It accepts only 't', 'b', 'r', 'l', or 'f' chars
              or any combination of them in any order (e.g. 'tbr' or "tlbr")
              Unknown characters are ignored. e.g. "tool" is the same as "tl"
              Duplicate characters are ignored.
    """

    Invalid = 0
    Size = 1
    Tile = 2
    Robot = 3

    def __init__(self, line: str, line_index: int):
        self.type = 0
        self.data = {}
        self._line = line.strip().lower()
        self._index = line_index
        self._fns = self._init_fns()
        self._parse()

    def _init_fns(self):
        def to_int(v):
            return int(v)

        def to_float(v):
            return float(v)

        def as_is(v):
            return v

        def to_beepers(v):
            """value of * or -1 means that tile will have inifinite beepers"""
            return -1 if v == "*" else int(v)

        return {
            "as_is": as_is,
            "to_int": to_int,
            "to_beepers": to_beepers,
            "to_float": to_float,
        }

    def _parse(
        self,
    ) -> None:
        line = self._line
        if not line or line.startswith("#"):
            return
        if line.startswith("map:"):
            self._parse_def("map", MapDef.Size)
            self._validate_size_def()
            return
        if line.startswith("tile:"):
            self._parse_def("tile", MapDef.Tile)
            self._validate_tile_def()
            return
        if line.startswith("robot:"):
            self._parse_def("robot", MapDef.Robot)
            self._validate_robot_def()

    def _validate_robot_def(self):
        to_int = self._fns["to_int"]
        to_beepers = self._fns["to_beepers"]
        pairs = {
            "x": {"fn": to_int, "req": True},
            "y": {"fn": to_int, "req": True},
            "beepers": {"fn": to_beepers, "req": False},
        }
        self._validate_req_data(pairs)

    def _validate_tile_def(self):
        to_int = self._fns["to_int"]
        to_float = self._fns["to_float"]
        to_beepers = self._fns["to_beepers"]
        as_is = self._fns["as_is"]
        pairs = {
            "x": {"fn": to_int, "req": True},
            "y": {"fn": to_int, "req": True},
            "radiation": {"fn": to_float, "req": False},
            "temperature": {"fn": to_float, "req": False},
            "beepers": {"fn": to_beepers, "req": False},
            "color": {"fn": as_is, "req": False},
            "walls": {"fn": as_is, "req": False},
            "mark": {"fn": as_is, "req": False},
        }
        self._validate_req_data(pairs)

    def _validate_size_def(self):
        to_int = self._fns["to_int"]
        pairs = {
            "rows": {"fn": to_int, "req": True},
            "cols": {"fn": to_int, "req": True},
        }
        self._validate_req_data(pairs)

    def _parse_def(self, def_key: str, def_type: int) -> None:
        self.type = def_type
        start = len(def_key) + 1  # to take into account :
        parts = set(re.split(" ", self._line[start:].lstrip()))
        self._parse_parts(parts)

    def _parse_parts(self, parts) -> None:
        for p in parts:
            p = p.strip()
            if len(p) == 0:
                continue
            k, v = re.split("=", p)
            self.data[k.strip()] = v.strip()

    def _validate_req_data(self, pairs):
        for k, v in pairs.items():
            if v["req"] and k not in self.data:
                raise ValueError(
                    f'Definition "{self._line}" as {self._index} '
                    f"does not contains required '{k}' parameter"
                )
            if k in self.data:
                self.data[k] = v["fn"](self.data[k])

        for k, _ in self.data.items():
            if k not in pairs:
                del self.data[k]


class AlgoWorldBoard(Board):
    """Board loaded from the world file in AlgoWorld World format .aww extension"""

    def __init__(self, world: str):
        super().__init__()
        self.world_path = self._find_world_path(world)
        self._load()

    def _find_world_path(self, world_name):
        if not world_name.endswith(".aww"):
            world_name += ".aww"

        package_path = Path(__file__).absolute().parent / "worlds"
        for worlds_dir in [Path("."), Path("worlds"), package_path]:
            if not worlds_dir.is_dir():
                continue
            world_path = worlds_dir / world_name
            if world_path.is_file():
                return world_path

        raise FileNotFoundError(
            "The specified file was not one of provided worlds.\n"
            "Please store custom worlds in a directory named 'worlds'"
        )

    def _load(self):
        with self.world_path.open(encoding="utf-8") as f:
            for i, line in enumerate(f):
                ld = MapDef(line, i)
                if ld.type == MapDef.Size:
                    self.nrows = ld.data["rows"]
                    self.ncols = ld.data["cols"]
                    self.tiles.set_bounds(self.nrows, self.ncols)
                    self.initialized = True
                if ld.type == MapDef.Tile:
                    x = ld.data["x"]
                    y = ld.data["y"]
                    tile = Tile(**ld.data)
                    self.tiles[x, y] = tile
                if ld.type == MapDef.Robot:
                    x = ld.data.get("x", 1)
                    y = ld.data.get("y", 1)
                    b = ld.data.get("beepers", -1)
                    r = Robot()
                    r.setup(name="default", x=x, y=y, beepers=b)
                    self.add_robot(robot=r)

        if not self.initialized:
            print(
                "ERROR: Map definition does not contain required MAP tag "
                "with the size of the board (rows and cols)"
            )
            sys.exit(1)
