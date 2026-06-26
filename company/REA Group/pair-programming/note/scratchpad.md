# **multiple robots**

## Storage

- Multiple robots can coexist on the table

I will choose 2d array to store the positions of multiple robots.

One trade off may be large sparse tables, in that case, set maybe more suitable.

## collision detection/handling

- They can't occupy the same cell
- They need collision detection/handling
- **PLACE onto occupied cell** — In your `place()` method, you check `is_valid_position()` which now checks for other robots. But what's the expected behavior? Should PLACE fail silently if the cell is occupied, or should it return False and log something?
    1. **Robot identity unused** — You added `id` and `name` to each robot, but they're never actually used anywhere. Why did you add them? How are you planning to use them later?
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

```jsx
robot1 = Robot(table, 'Robot 1')
robot2 = Robot(table, 'Robot 2')
```

### manage

```jsx
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
