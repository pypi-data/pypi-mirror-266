r"""
This package provides the following functions defined in __all__ for writing
simple procedural style programs with AlgoWorld Robots

This module is deprecated in favor of eduworld.robot
but retained for compatibility

This file is part of eduworld package

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

import warnings
from eduworld.robot import (
    setup,
    shutdown,
    up,
    down,
    left,
    right,
    up_is_wall,
    down_is_wall,
    left_is_wall,
    right_is_wall,
    tile_color,
    paint,
    put,
    pickup,
    has_beepers,
    next_to_beeper,
    tile_radiation,
    tile_temperature,
)

__all__ = [
    # setup
    "setup",
    "shutdown",
    # movement
    "up",
    "down",
    "left",
    "right",
    # check movement
    "up_is_wall",
    "down_is_wall",
    "left_is_wall",
    "right_is_wall",
    # color paint
    "tile_color",
    "paint",
    # beepers
    "put",
    "pickup",
    "has_beepers",
    "next_to_beeper",
    # other sensors
    "tile_radiation",
    "tile_temperature",
]

warnings.warn(
    "the eduworld.simple module is deprecated, please use eduworld.robot instead",
    DeprecationWarning,
    stacklevel=2,
)
