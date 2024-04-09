r"""
This file is part of eduworld package.

This file contains Generic Robot that can move in four cardinal directions
pickup things, and sense dangerous areas (e.g. walls)

Coordinate system for the robot is defined as follows

   1 2 3 4 5
  +- - - - -> x
1 |
  |
  |
  |
5 |
y v

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

import time

from .board import Board


class RobotError(RuntimeError):
    """Raised on wrong execution of a command - e.g. hitting a wall."""


# pylint: disable=too-many-public-methods


class Robot:
    """Generic Robot that can move in four cardinal directions,
    pickup and place things, and sense walls, paint, and other things"""

    def __init__(self):
        self.name = f"robot-{time.monotonic()}"
        self.board: Board = None
        self.color = "green"
        self.x: int = 1
        self.y: int = 1
        self.beepers: int = -1
        self.update_fns = []

    def setup(
        self, x: int, y: int, beepers: int = -1, color: str = "green", name: str = None
    ):
        """Set up robot color, position, and beepers"""
        self.color = color
        self.x: int = x
        self.y: int = y
        self.beepers: int = beepers
        if name is not None:
            self.name = name

    def __repr__(self) -> str:
        b = "*" if self.beepers == -1 else self.beepers
        return f"name: {self.name}; x: {self.x}; y: {self.y}; beepers: {b}"

    def on_update(self, fn):
        """Register robot state update callback function
        can be used for counting steps, canvas redraw, etc"""
        self.update_fns.append(fn)

    def _update(self):
        for fn in self.update_fns:
            fn()

    def put(self) -> None:
        """Robot puts the beeper"""
        if not self.has_beepers():
            raise RobotError("Out of beepers!")
        if self.beepers != -1:
            self.beepers -= 1
        self.board.place_beeper(self.x, self.y)
        self._update()

    def pickup(self) -> None:
        """Robot picks up the beeper (if tile has any)"""
        if not self.board.pickup_beeper(self.x, self.y):
            raise RobotError("Tile has no beepers!")
        if self.beepers != -1:
            self.beepers += 1
        self._update()

    def has_beepers(self) -> bool:
        """True if robot has some or unlimited beepers"""
        return self.beepers != 0

    def next_to_beeper(self) -> bool:
        """Return whether or not tile has beepers"""
        return self.board.has_beepers(self.x, self.y)

    def paint(self, color: str) -> None:
        """Paint the tile ora... I mean in any available color"""
        self.board.paint_tile(self.x, self.y, color)
        self._update()

    def tile_color(self) -> str:
        """Return color of the tile"""
        return self.board.read_tile_color(self.x, self.y)

    def tile_radiation(self) -> float:
        """Return tile radiation"""
        return self.board.read_tile_radiation(self.x, self.y)

    def tile_temperature(self) -> float:
        """Return tile temperature"""
        return self.board.read_tile_temperature(self.x, self.y)

    def left(self) -> None:
        """Robot moves left"""
        if self.left_is_wall():
            raise RobotError("Can't move left. Something is on the way.")
        self.x = self.x - 1
        self._update()

    def right(self) -> None:
        """Robot moves right"""
        if self.right_is_wall():
            raise RobotError("Can't move right. Something is on the way.")
        self.x = self.x + 1
        self._update()

    def up(self) -> None:
        """Robot moves up"""
        if self.up_is_wall():
            raise RobotError("Can't move up. Something is on the way.")
        self.y = self.y - 1
        self._update()

    def down(self) -> None:
        """Robot moves down"""
        if self.down_is_wall():
            raise RobotError("Can't move down. Something is on the way.")
        self.y = self.y + 1
        self._update()

    def up_is_wall(self):
        """Test if tile above the robot is blocked by wall"""
        return self.board.move_up_blocked(self.x, self.y)

    def down_is_wall(self):
        """Test if tile below the robot is blocked by wall"""
        return self.board.move_down_blocked(self.x, self.y)

    def left_is_wall(self):
        """Test if tile left to the robot is blocked by wall"""
        return self.board.move_left_blocked(self.x, self.y)

    def right_is_wall(self):
        """Test if tile right to the robot is blocked by wall"""
        return self.board.move_right_blocked(self.x, self.y)


#    def up_is_free(self):
#        """Test if tile above the robot is free to move"""
#        return not self.up_is_wall()
#
#    def down_is_free(self):
#        """Test if tile below the robot is free to move"""
#        return not self.down_is_wall()
#
#    def left_is_free(self):
#        """Test if tile left to the robot is free to move"""
#        return not self.left_is_wall()
#
#    def right_is_free(self):
#        """Test if tile right to the robot is free to move"""
#        return not self.right_is_wall()
