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

import time

from ..canvas import Canvas


class Pen:
    """Simple data holder for Pen props"""

    def __init__(self):
        self.pos = [0, 0]
        self.color = "black"
        self.width = 6
        self.can_draw = False

    def move_by(self, dx: float, dy: float) -> None:
        """Move pen relatively to its position"""
        self.pos[0] += dx
        self.pos[1] += dy

    def set_pos(self, x: float, y: float) -> None:
        """Set absolute pen position"""
        self.pos[0] = x
        self.pos[1] = y

    def set_width(self, width: int) -> None:
        """Set pen width. Constrained between 4 .. 15"""
        self.width = int(max(4, min(width, 15)))


class Point:
    """Some arbitrary 2d point"""

    def __init__(self):
        self.x: int = 0
        self.y: int = 0


# pylint: disable=too-many-ancestors, too-many-instance-attributes
class PlotterCanvas(Canvas):
    """Class for drawing lines of many colors aka Plotter"""

    def __init__(self, parent):
        super().__init__(parent)
        self._unit_size = 35
        self._arrow_size = 16
        self._width = 0
        self._height = 0
        self._origin = Point()
        self._pen = Pen()
        self._lines = []

    def set_cell_size(self, cell_size: int, redraw: bool = True):
        """Set the unit cell size"""
        if cell_size is not None:
            self._unit_size = cell_size
        if redraw:
            self.redraw()

    def pen_raise(self):
        """Raise the pen. Plotter with pen raised can't draw lines"""
        self._pen.can_draw = False
        self.redraw()

    def pen_lower(self):
        """Lower the pen. Plotter with pen lowered can draw lines"""
        self._pen.can_draw = True
        self.redraw()

    def pen_color(self, color: str) -> None:
        """Set the pen color"""
        self._pen.color = color
        self.redraw()

    def pen_width(self, width: int) -> None:
        """Set the pen width"""
        self._pen.set_width(width)
        self.redraw()

    def pen_move_by(self, dx: float, dy: float) -> None:
        """Move pen by dx and dy"""
        p = self._pen
        last = p.pos.copy()
        p.move_by(dx, dy)
        if p.can_draw:
            coords = last + p.pos.copy()
            self._lines.append((coords, p.width, p.color))
        self.redraw()

    def pen_set_pos(self, x: float, y: float) -> None:
        """Set absolute pen position"""
        p = self._pen
        last = p.pos.copy()
        p.set_pos(x, y)
        if p.can_draw:
            coords = last + p.pos.copy()
            self._lines.append((coords, p.width, p.color))
        self.redraw()

    def undo_last_line(self):
        """Undo draw last line"""
        if len(self._lines) == 0:
            return;
        can_draw = self._pen.can_draw
        coords, width, color = self._lines.pop()
        self.pen_raise()
        self.pen_set_pos(coords[0], coords[1])
        self.pen_color(color)
        self.pen_width(width)
        if can_draw:
            self.pen_lower()
        self.redraw()

    def clear(self):
        """Remove all drawn lines"""
        self._lines.clear()
        self.redraw()

    def redraw(self, immediate=False) -> None:
        """Redraw everything"""
        if not immediate:
            time.sleep(self._draw_delay)
        self._height = self.winfo_height()
        self._width = self.winfo_width()
        self._origin.x = self._width / 2
        self._origin.y = self._height / 2
        self._delete_all()
        self._draw_grid()
        self._draw_lines()
        self._draw_pen()
        self._draw_origin_numbers()
        # self._draw_numbers()
        self.root.update()

    def _delete_all(self):
        self.delete("grid")
        self.delete("lines")
        self.delete("pen")
        self.delete("numbers")

    def _calc_true_origin(self):
        ox = self._origin.x
        oy = self._origin.y
        cx = -self._pen.pos[0] * self._unit_size
        cy = self._pen.pos[1] * self._unit_size
        return (ox + cx, oy + cy)

    def _draw_origin_numbers(self):
        ox, oy = self._calc_true_origin()
        hs = self._unit_size / 2
        s = self._unit_size
        tags = ("numbers",)
        font = "Mono 12 bold"
        fill = "gray"
        self.create_text(ox - hs, oy + hs, text="0", fill=fill, font=font, tags=tags)
        self.create_text(ox + s, oy + hs, text="1", fill=fill, font=font, tags=tags)
        self.create_text(ox - hs, oy - s, text="1", fill=fill, font=font, tags=tags)

    def _draw_pen(self):
        ox, oy = self._calc_true_origin()
        (x, y) = self._pen.pos.copy()
        x = ox + x * self._unit_size
        y = oy - y * self._unit_size
        r = self._pen.width / 2 + 2
        c = [x - r, y - r, x + r, y + r]
        tags = ("pen",)
        fill = self._pen.color if self._pen.can_draw else "gray95"
        outline = "white" if self._pen.can_draw else self._pen.color
        self.create_oval(c, width=2, outline=outline, fill=fill, tags=tags)

    def _draw_lines(self):
        for line in self._lines:
            self._draw_line(line)

    def _draw_line(self, line):
        ox, oy = self._calc_true_origin()
        coords = line[0].copy()
        width = line[1]
        color = line[2]
        coords[0] = ox + coords[0] * self._unit_size  # xs
        coords[1] = oy - coords[1] * self._unit_size  # ys
        coords[2] = ox + coords[2] * self._unit_size  # xs
        coords[3] = oy - coords[3] * self._unit_size  # ys
        self.create_line(coords, fill=color, width=width, tags=("lines",))

    def _draw_grid(self):
        self._draw_verticals()
        self._draw_horizontals()
        self._draw_x_arrow()
        self._draw_y_arrow()

    def _draw_x_arrow(self):
        _, y = self._calc_true_origin()
        x = self._width - 10
        arrowhead_x = x - self._arrow_size
        arrowhead_top = y - self._arrow_size / 2
        arrowhead_bottom = y + self._arrow_size / 2
        coords = [
            # shaft
            10,
            y,
            x,
            y,
            # left side
            arrowhead_x,
            arrowhead_top,
            # central
            x,
            y,
            # right side
            arrowhead_x,
            arrowhead_bottom,
        ]
        self.create_line(coords, fill="gray40", width=2, tags=("grid",))

    def _draw_y_arrow(self):
        x, _ = self._calc_true_origin()
        y = 10
        arrowhead_y = y + self._arrow_size
        arrowhead_left = x - self._arrow_size / 2
        arrowhead_right = x + self._arrow_size / 2
        coords = [
            # shaft
            x,
            self._height - 10,
            x,
            y,
            # left side
            arrowhead_left,
            arrowhead_y,
            # central
            x,
            y,
            # right side
            arrowhead_right,
            arrowhead_y,
        ]
        self.create_line(coords, fill="gray40", width=2, tags=("grid",))

    def _draw_verticals(self):
        line_count = int(self._width / self._unit_size) + 1
        x, _ = self._calc_true_origin()
        delta = x % self._unit_size
        for i in range(line_count):
            x = i * self._unit_size + delta
            coords = [x, 0, x, self._height]
            self.create_line(coords, fill="gray70", width=1, tags=("grid",))

    def _draw_horizontals(self):
        line_count = int(self._height / self._unit_size) + 1
        _, y = self._calc_true_origin()
        delta = y % self._unit_size
        for i in range(line_count):
            y = i * self._unit_size + delta
            coords = [0, y, self._width, y]
            self.create_line(coords, fill="gray70", width=1, tags=("grid",))
