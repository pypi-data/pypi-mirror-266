# EduWorld

`EduWorld` is an educational `python` package designed for students to learn computational thinking, algorithms, and other basic programming concepts. Through this process they learn how to divide a problem into smaller steps and refine them; to abstract; to recognize patterns; and to design and implement algorithms;

## Robot

Conceptually it is based on Kumir Robot, with bits of Karel the Robot. (but shares no code)
* https://github.com/a-a-maly/kumir2
* https://github.com/TylerYep/stanfordkarel
* https://github.com/xsebek/karel

The Robot can walk in four cardinal directions, sense walls, temperature, radiation, and place/pickup beepers.

See the `eduworld.robot` module for the list of all available procedural commands.

Oop version of the Robot is not yet completed and somewhat clumsy to use.

### Interactive mode

```python
from eduworld.robot import setup, shutdown


setup(world="demo-world", interactive=True, x=1, y=1)
shutdown(keep_window=True)
```

To launch Robot in interactive mode (immediate command execution), run `python test_robot.py`.
In this mode Robot will not execute error shut-off even if you run it into the wall.

Command keys

* W - move up
* S - move down
* A - move left
* D - move right
* E - paint tile
* R - pickup beeper
* F - put beeper
* Q - quit

## Plotter

The Plotter is used to paint lines on endless sheet of paper. It is conceptually based on Kumir Plotter, but with few extras.

See the `eduworld.plotter` module for list of available commands.

### Interactive mode

```python
from eduworld.plotter import setup, shutdown


setup(interactive=True)
shutdown(keep_window=True)
```

To launch Plotter in interactive mode run `python test_plotter.py`.
In this mode you can control plotter's head using following keys

* Keypad 8 - move up 1 unit
* Keypad 2 - move down 1 unit
* Keypad 4 - move left 1 unit
* Keypad 6 - move right 1 unit
* Keypad 9 - move up-right 1 unit
* Keypad 3 - move down-right 1 unit
* Keypad 1 - move down-left 1 unit
* Keypad 7 - move up-left 1 unit
* Keypad 0 - Move pen to origin (0, 0)
* Keypad - - zoom out
* Keypad + - zoom in
* W - randomly pick pen width
* E - randomly pick pen color
* R - raise pen
* F - lower pen
* Z - undo last line
* C - erase drawing

When you `shutdown()` Plotter with `keep_window=True`, you can use Keypad to move around the paper sheet.
