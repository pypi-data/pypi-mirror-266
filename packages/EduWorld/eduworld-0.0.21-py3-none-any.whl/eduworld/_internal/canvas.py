r"""
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

import tkinter as tk


# pylint: disable=too-many-ancestors
class Canvas(tk.Canvas):
    """Class for drawing the stuff on tk.canvas"""

    def __init__(self, parent):
        super().__init__(parent, width=320, height=240, background="gray95")
        self.root = parent
        self._draw_delay = 0.7
        self.grid(column=0, row=0, sticky="NEWS")
        self.bind("<Configure>", lambda _: self.redraw(True))

    def set_draw_delay(self, delay: float) -> None:
        """Sets the delay (like 0.7 or 0.05 of a second) between redraws"""
        self._draw_delay = min(max(0, delay), 1)

    def redraw(self, immediate=False) -> None:
        """Override this method in a derived class to draw something
        import time
        # then use following code in the override to draw with delay
        # --
        if not immediate:
            time.sleep(self.draw_delay)
        # draw something
        self.root.update()
        # ---
        """
