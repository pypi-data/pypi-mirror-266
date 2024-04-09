r"""
This package provides the following functions (__all__) for writing oop
programs with EduWorld Robots

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

from .application import Application
from .robot import RobotApplication, Board, AlgoWorldBoard, RobotCanvas, Robot
from .plotter import PlotterCanvas

__all__ = [
    "Application",
    "RobotApplication",
    "Board",
    "RobotCanvas",
    "AlgoWorldBoard",
    "Robot",
    "PlotterCanvas",
]
