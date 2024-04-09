r"""
This package provides the following functions defined in __all__ for writing
simple procedural style programs with AlgoWorld Robots

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

import sys
import tkinter as tk
import random as r

# from random import randint as rnd
from eduworld import Application, PlotterCanvas as Canvas


# pylint: disable=too-many-arguments
class _AppWithState:
    """Store App and it's state"""

    def __init__(self):
        self.cell_size: int = 35
        self._initial_cell_size: int = 35
        self.app: Application = Application()
        self.root = self.app.root
        self.canvas: Canvas = Canvas(self.root)
        self.initialized: bool = False
        self._colors = self._setup_colors()
        self.app.set_canvas(self.canvas)

    def setup(
        self,
        x: float = 0,
        y: float = 0,
        cell_size: int = 35,
        delay: float = 0.7,
        interactive: bool = False,
    ):
        """Setup the app"""
        if cell_size is not None:
            self.cell_size = cell_size
            self._initial_cell_size = cell_size
            self.canvas.set_cell_size(cell_size, False)
        self.canvas.set_draw_delay(delay)
        self.canvas.pen_set_pos(x, y)
        self._bind_movement_keys()
        if interactive:
            self._bind_paint_keys()
            self.canvas.set_draw_delay(0)

    def shutdown(self, keep_window: bool = False):
        """Kill the App"""
        self.canvas.set_draw_delay(0)
        self.app.shutdown(keep_window)

    def run(self):
        """Run the App"""
        self.app.run()

    def _setup_colors(self):
        return [
            "black",
            "gray",
            "red",
            "green",
            "blue",
            "dodgerblue",
            "cyan",
            "firebrick",
            "magenta",
            "orange",
            "pink",
        ]

    def _rand_color(self):
        i = r.randint(0, len(self._colors) - 1)
        self.canvas.pen_color(self._colors[i])

    def _incr_cell_size(self):
        self.cell_size += 2
        self.canvas.set_cell_size(self.cell_size)

    def _decr_cell_size(self):
        self.cell_size -= 2
        self.canvas.set_cell_size(self.cell_size)

    def _reset_pen(self):
        self.cell_size = self._initial_cell_size
        self.canvas.pen_set_pos(0, 0)
        self.canvas.set_cell_size(self._initial_cell_size)

    def _bind_movement_keys(self):
        self.root.bind("<KP_0>", lambda _: self._reset_pen())
        self.root.bind("<KP_7>", lambda _: self.canvas.pen_move_by(-1, 1))
        self.root.bind("<KP_9>", lambda _: self.canvas.pen_move_by(1, 1))
        self.root.bind("<KP_1>", lambda _: self.canvas.pen_move_by(-1, -1))
        self.root.bind("<KP_3>", lambda _: self.canvas.pen_move_by(1, -1))
        self.root.bind("<KP_2>", lambda _: self.canvas.pen_move_by(0, -1))
        self.root.bind("<KP_8>", lambda _: self.canvas.pen_move_by(0, 1))
        self.root.bind("<KP_4>", lambda _: self.canvas.pen_move_by(-1, 0))
        self.root.bind("<KP_6>", lambda _: self.canvas.pen_move_by(1, 0))
        self.root.bind("<KP_Add>", lambda _: self._incr_cell_size())
        self.root.bind("<KP_Subtract>", lambda _: self._decr_cell_size())

    def _bind_paint_keys(self):
        self.root.bind("<W>", lambda _: self.canvas.pen_width(r.randint(1, 15)))
        self.root.bind("<w>", lambda _: self.canvas.pen_width(r.randint(1, 15)))
        self.root.bind("<E>", lambda _: self._rand_color())
        self.root.bind("<e>", lambda _: self._rand_color())
        self.root.bind("<R>", lambda _: self.canvas.pen_raise())
        self.root.bind("<r>", lambda _: self.canvas.pen_raise())
        self.root.bind("<F>", lambda _: self.canvas.pen_lower())
        self.root.bind("<f>", lambda _: self.canvas.pen_lower())
        self.root.bind("<C>", lambda _: self.canvas.clear())
        self.root.bind("<c>", lambda _: self.canvas.clear())
        self.root.bind("<Z>", lambda _: self.canvas.undo_last_line())
        self.root.bind("<z>", lambda _: self.canvas.undo_last_line())


app: _AppWithState = _AppWithState()


def _hide_tk_err(f):
    def w(*args, **kwargs):
        try:
            f(*args, **kwargs)
        except tk.TclError:
            sys.exit(1)

    return w


def setup(
    x: float = 0,
    y: float = 0,
    cell_size: int = None,
    delay: float = 0.7,
    interactive: bool = False,
) -> None:
    """Setup the plotter"""
    if not app.initialized:
        app.initialized = True
        app.setup(
            x=x,
            y=y,
            cell_size=cell_size,
            delay=delay,
            interactive=interactive,
        )
        app.run()


def shutdown(keep_window: bool = False) -> None:
    """Shut down the app"""
    app.shutdown(keep_window)


@_hide_tk_err
def pen_move_by(dx: float, dy: float) -> None:
    """Move pen by delta"""
    app.canvas.pen_move_by(dx, dy)


@_hide_tk_err
def pen_set_pos(x: float, y: float) -> None:
    """Move pen to apsolute x and y coordinates"""
    app.canvas.pen_set_pos(x, y)


@_hide_tk_err
def pen_up() -> None:
    """Raise pen"""
    app.canvas.pen_raise()


@_hide_tk_err
def pen_down() -> None:
    """Lower pen"""
    app.canvas.pen_lower()


@_hide_tk_err
def pen_color(color: str) -> None:
    """Set pen color"""
    app.canvas.pen_color(color)


@_hide_tk_err
def pen_width(width: int) -> None:
    """Set pen width"""
    app.canvas.pen_width(width)


__all__ = [
    # setup
    "setup",
    "shutdown",
    "pen_up",
    "pen_down",
    "pen_color",
    "pen_width",
    "pen_set_pos",
    "pen_move_by",
]
