# **multiple robots**

## Storage

- Multiple robots can coexist on the table

I will choose 2d array to store the positions of multiple robots.

One trade off may be large sparse tables, in that case, set maybe more suitable.

1. **Table as source of truth** — If the table is tracking robot positions in a grid, but each robot also tracks its own `(x, y)`, how do you keep them in sync? What if they diverge?

I will use a map robot_positions to track the position of a robot by uuid.
Every time a robot is placed on the table or the position has changed. We should update both robot grid and robot_positions map together to keep in sync.

## collision detection/handling

- They can't occupy the same cell
- They need collision detection/handling
- **PLACE onto occupied cell** — In your `place()` method, you check `is_valid_position()` which now checks for other robots. But what's the expected behavior? Should PLACE fail silently if the cell is occupied, or should it return False and log something?
    
    ```python
    {"success": bool, "message": str}
    ```
    
    I should keep it consistent for 
    
    - place
    - move
    - left
    - right
    - undo
    
    and they return their own validation result.
    
    Because it is their responsibility for them to report their blockers as a student. Not first just report failure to their teacher(`execute()`) without any reason but the teacher need to guess.

    As for report(), we can stay as it is. Because we just need to print something, not a real execution.
    
    1. **Robot identity unused** — You added `id` and `name` to each robot, but they're never actually used anywhere. Why did you add them? How are you planning to use them later?

    Maybe currently we just want to make identification. Because different robots may have the same name. It is for the future. In real world coding, we both need id and name. Or if we want to persist the robots, we need unique ids.
    uuid can be used to track the position of a robot. We can only keep uuids in robots grid.

    - now we want to return a more detailed log message to inform the users why our command failed. Here is how our name is used: to tell the user which robot it collided with.

Every time the robots move, they will check whether there is an obstacle or another robot.

robots[x][y] is occupied or not

## Robot

- Consider how robots are created, managed, and identified

### ID

each table needs an id  
uuid: identical, we don’t need to keep an incremental number or something  
name: human-readable

### init

Open-close & DI

```python
robot1 = Robot(table, 'Robot 1')
robot2 = Robot(table, 'Robot 2')
```

### manage

```python
robot1.execute('PLACE 0,0,NORTH')
robot2.execute('PLACE 1,1,EAST')
```

When the robot is placed or the position is changed:  
the table need to update the robots grid

1. empty the current position
2. occupy the next position

- **Undo behavior** — When a robot calls `undo()`, the position is restored from history, but the `table.robots` grid isn't updated. So if robot1 was at (0,0), moved to (0,1), then undo — the grid still thinks robot1 is at (0,1). What happens then?
    
    We also need to consider undo, 
    
    1. before: empty the current position
    2. after: reset back to previous position

**2. Robot management — who owns the robots?**

Right now robots are created externally:

```python
robot1 = Robot(table, 'Robot 1')
robot2 = Robot(table, 'Robot 2')
```

Should the Table instead manage robot creation and registration? Like:

```python
table = Table(5, 5)
robot1 = table.create_robot('Robot 1')
robot2 = table.create_robot('Robot 2')
```

And then you could do things like:

```python
all_robots = table.get_all_robots()
robot = table.get_robot('Robot 1')
```

I would like to keep my current option. Because robot is not born from table, live with the table. They are independent, their lifecycle don't end with table. They just use tables as reference.