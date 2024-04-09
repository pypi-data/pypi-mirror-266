r"""
This file is part of eduworld package.

This class defines sparse board with tiles

Board coordinate system is defined as follows
   1 2 3 4 5
  +- - - - -> x
1 |
2 |
3 |
4 |
5 |
  v
  y

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

from enum import Enum, unique

from .tile import Tile
from .tilemap import TileMap


@unique
class Direction(Enum):
    """Class representing robot move direction"""

    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)


class Board:
    """Base class for storing a robot's world with items, walls, and other stuff
    and functions for interacting with it"""

    def __init__(self):
        self.nrows: int = 0
        self.ncols: int = 0
        self.tiles: TileMap = TileMap()
        self.initialized: bool = False
        self.robots = []

    def add_robot(self, robot):
        """Add robot to robots collection for drawing"""
        if robot not in self.robots:
            self.robots.append(robot)
            robot.board = self

    def get_default_robot(self):
        """Return default robot"""
        return self.get_robot("default")

    def get_robot(self, name: str):
        """Return robot by its name, None if not found"""
        for r in self.robots:
            if r.name == name:
                return r
        return None

    def __repr__(self):
        s = ""
        for y in range(1, self.nrows + 1):
            s += "|"
            for x in range(1, self.ncols + 1):
                s += self.tiles[x, y].short_repr()
            s += "|\n"
        return s

    def has_tile_at(self, x: int, y: int):
        """Test if we have tile at coordinates"""
        return self.tiles.has_tile_at((x, y))

    def read_tile_temperature(self, x, y) -> float:
        """Measure tile temperature"""
        return self.tiles[x, y].temperature

    def read_tile_radiation(self, x, y) -> float:
        """Measure tile radiation"""
        return self.tiles[x, y].radiation

    def read_tile_color(self, x, y) -> str:
        """Return color of the tile"""
        return self.tiles[x, y].color

    def paint_tile(self, x, y, color):
        """Paint tile with color"""
        if not self.has_tile_at(x, y):
            self.tiles[x, y] = Tile(x, y)
        self.tiles[x, y].color = color

    def place_beeper(self, x, y):
        """Place one beeper on the tile"""
        if not self.has_tile_at(x, y):
            self.tiles[x, y] = Tile(x, y)
        self.tiles[x, y].add_beeper()

    def has_beepers(self, x, y) -> bool:
        """True if tile has any amount of beepers"""
        return self.tiles[x, y].has_beepers()

    def pickup_beeper(self, x, y) -> bool:
        """Pick up one beeper from the tile. return False if not possible"""
        tile = self.tiles[x, y]
        if not tile.has_beepers():
            return False
        return tile.remove_beeper()

    def move_up_blocked(self, sx, sy, /) -> bool:
        """Test if we can move up from tile[sx, sy]"""
        return self._move_is_blocked(sx, sy, Direction.UP)

    def move_down_blocked(self, sx, sy, /) -> bool:
        """Test if we can move down from tile[sx, sy]"""
        return self._move_is_blocked(sx, sy, Direction.DOWN)

    def move_left_blocked(self, sx, sy, /) -> bool:
        """Test if we can move up from tile[sx, sy]"""
        return self._move_is_blocked(sx, sy, Direction.LEFT)

    def move_right_blocked(self, sx, sy, /) -> bool:
        """Test if we can move up from tile[sx, sy]"""
        return self._move_is_blocked(sx, sy, Direction.RIGHT)

    def _move_is_blocked(self, sx, sy, delta: Direction) -> bool:
        """Use it to test if robot can move from source tile (sx, sy)
        to dest tile. Dest tile is defined using delta by x and y
        """
        dx = sx + delta.value[0]
        dy = sy + delta.value[1]
        t_curr = self.tiles[sx, sy]
        t_next = self.tiles[dx, dy]
        # now let's check the direction
        if delta == Direction.UP:
            return t_curr.top_is_wall() or t_next.bottom_is_wall()
        if delta == Direction.DOWN:
            return t_curr.bottom_is_wall() or t_next.top_is_wall()
        if delta == Direction.LEFT:
            return t_curr.left_is_wall() or t_next.right_is_wall()
        if delta == Direction.RIGHT:
            return t_curr.right_is_wall() or t_next.left_is_wall()
        return True
