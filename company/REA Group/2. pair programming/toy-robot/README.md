# Toy Robot Simulator

A simple simulation of a toy robot moving on a 5x5 square tabletop.

## Description

- The robot is free to roam around the surface of the table
- Any movement that would result in the robot falling from the table is prevented
- The first valid command is a `PLACE` command, all other commands are ignored until a valid `PLACE` is executed

## Commands

- `PLACE X,Y,FACING` - Put the robot on the table at position (X,Y) facing NORTH, SOUTH, EAST or WEST
- `MOVE` - Move the robot one unit forward in the direction it is currently facing
- `LEFT` - Rotate the robot 90 degrees left without changing position
- `RIGHT` - Rotate the robot 90 degrees right without changing position
- `REPORT` - Announce the current position and facing direction

## Constraints

- The tabletop is 5x5 units
- Valid positions are (0,0) to (4,4)
- Valid facing directions are NORTH, SOUTH, EAST, WEST
- The origin (0,0) is the SOUTH WEST corner

## Installation

```bash
pip install -r requirements.txt
```

## Running Tests

```bash
pytest
```

## Interactive Mode

```bash
python main.py
```

## Usage

```python
from robot import Robot
from table import Table

table = Table(5, 5)
robot = Robot(table)

robot.execute("PLACE 0,0,NORTH")
robot.execute("MOVE")
robot.execute("REPORT")  # Output: 0,1,NORTH
```

## Example Commands

```
PLACE 0,0,NORTH
MOVE
REPORT
# Output: 0,1,NORTH

PLACE 0,0,NORTH
LEFT
REPORT
# Output: 0,0,WEST

PLACE 1,2,EAST
MOVE
MOVE
LEFT
MOVE
REPORT
# Output: 3,3,NORTH
```