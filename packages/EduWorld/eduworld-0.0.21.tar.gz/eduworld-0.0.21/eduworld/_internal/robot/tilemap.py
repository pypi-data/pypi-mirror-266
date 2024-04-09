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

from typing import Tuple, Dict
from .tile import Tile


Coords = Tuple[int, int]
MapType = Dict[Coords, Tile]


class TileMap:
    """Sparse container for a tiles on a grid
    Technically this container is infinite, but
    at the moment is used as a bounded grid
    """

    def __init__(self):
        self.nrows: int = None
        self.ncols: int = None
        self.tiles: MapType = {}

    def __getitem__(self, xy: Coords) -> Tile:
        if not self.in_range(*xy):
            return Tile(*xy, walls="f")
        return self.tiles.get(xy, Tile(*xy))

    def __setitem__(self, xy: Coords, tile: Tile) -> None:
        self.tiles[xy] = tile

    def set_bounds(self, nrows: int, ncols: int) -> None:
        """Set bounds of the world"""
        self.nrows: int = nrows
        self.ncols: int = ncols

    def in_range(self, x: int, y: int) -> bool:
        """Check if coordinates in map[cols,rows] range"""
        return 0 < y <= self.nrows and 0 < x <= self.ncols

    def has_tile_at(self, xy: Coords) -> bool:
        """this is a crazy way to check if sparse map has tile at coords"""
        return not self.tiles.get(xy, None) is None
