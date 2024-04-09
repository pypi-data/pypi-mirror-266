"""
Class repesenting a map tile

This file is part of eduworld package.

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

# pylint: disable=too-many-arguments


class Tile:
    """Class representing a map tile (with items, beepers, walls, etc)"""

    FULL_WALL = 15
    TOP_WALL = 8
    RIGHT_WALL = 4
    LEFT_WALL = 2
    BOTTOM_WALL = 1

    def __init__(
        self,
        x: int,
        y: int,
        walls: str = "",
        beepers: int = 0,
        radiation: float = 0,
        temperature: float = 0,
        color: str = "",
        mark: str = "",
    ):
        self.x: int = x
        self.y: int = y
        # using -1 to represent inf count of beepers is not super clear, but ...
        self.beepers: int = beepers
        self.radiation: float = radiation
        self.temperature: float = temperature
        self.color: str = color
        self.mark: str = mark
        self.walls: int = self._parse_walls(walls)

    def _wall_repr(self) -> str:
        s: str = ""
        if self.top_is_wall():
            s += "t"
        if self.bottom_is_wall():
            s += "b"
        if self.left_is_wall():
            s += "l"
        if self.right_is_wall():
            s += "r"
        return s

    def __repr__(self):
        # tile: x y beepers=n,* temp=n radiation=n color=color walls=tblr
        b = "*" if self.beepers == -1 else self.beepers
        return (
            f"tile: x={self.x} y={self.y} "
            f"beepers={b} temp={self.temperature} "
            f"radiation={self.radiation} "
            f"color={self.color} "
            f"walls={self._wall_repr()}"
        )

    def short_repr(self) -> str:
        """Return short one char representation of the tile"""
        if self.has_walls():
            return "#"
        if self.has_beepers():
            b = self.beepers
            if b == -1:
                return "*"
            if b >= 10:
                return "+"
            return str(b)
        return " "

    def has_beepers(self) -> bool:
        """Test if tile has any beepers on it"""
        return self.beepers == -1 or self.beepers > 0

    def add_beeper(self):
        """Increase count of beepers on the tile (if not inf)"""
        if self.beepers != -1:
            self.beepers += 1

    def remove_beeper(self) -> bool:
        """Decrease count of beepers on the tile (if not inf)"""
        if self.beepers == 0:
            return False
        if self.beepers == -1:
            return True
        self.beepers -= 1
        return True

    def has_walls(self) -> bool:
        """Test if tile has any walls"""
        return self.walls > 0

    def top_is_wall(self) -> bool:
        """Return if top is wall"""
        return self.walls & Tile.TOP_WALL != 0

    def bottom_is_wall(self) -> bool:
        """Return if bottom is wall"""
        return self.walls & Tile.BOTTOM_WALL != 0

    def left_is_wall(self) -> bool:
        """Return if left is wall"""
        return self.walls & Tile.LEFT_WALL != 0

    def right_is_wall(self) -> bool:
        """Return if right is wall"""
        return self.walls & Tile.RIGHT_WALL != 0

    def _parse_walls(self, walls: str) -> int:
        w = 0
        for c in walls.lower():
            if c == "e":
                return 0
            elif c == "f":
                return Tile.FULL_WALL
            elif c == "t":
                w |= Tile.TOP_WALL
            elif c == "b":
                w |= Tile.BOTTOM_WALL
            elif c == "l":
                w |= Tile.LEFT_WALL
            elif c == "r":
                w |= Tile.RIGHT_WALL
        return w
