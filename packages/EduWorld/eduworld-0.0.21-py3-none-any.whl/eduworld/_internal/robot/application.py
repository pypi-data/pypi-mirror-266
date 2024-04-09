"""
This file is part of eduworld package.

This is a main application window class with Canvas and board and etc

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

from ..application import Application


class RobotApplication(Application):
    """Defines an Tkinter application with canvas, board and other stuff"""

    def __init__(self, title=""):
        super().__init__(title)
        self.initialized = False
        self._board = None

    def initialize_app(self):
        super().initialize_app()
        if self._canvas.board is None or not self._canvas.board.initialized:
            print("Board is not set or not initialized! Exiting!")
            sys.exit(1)
