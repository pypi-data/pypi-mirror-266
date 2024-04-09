r"""This is a simple interactive demo program

WSAD to move robot
E to paint tile with random color
F to put the beeper
R to pick up the beeper
Q to quit"""

from eduworld.robot import setup, shutdown
from eduworld.plotter import setup as init_plotter, shutdown as shut_plotter


setup(world="demo-world", interactive=True, x=1, y=1)
init_plotter(interactive=True)

shutdown(keep_window=True)
shut_plotter(keep_window=True)
