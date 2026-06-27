# **Multiple robots**

# Jump

```
robot1 = Robot(table, "Robot A")
robot2 = Robot(table, "Robot B")

robot1.execute("PLACE 0,0,NORTH")
robot2.execute("PLACE 1,0,EAST")

robot1.execute("MOVE")  # robot1 tries to move to (0,1)
# Expected: Success

robot1.execute("JUMP 3")  # robot1 tries to jump 3 steps north from (0,1)
# What should happen?
```

**A) Stop at the robot's position and fail (treat the robot like a wall)**\
<span style="color: rgb(74, 158, 232);">I choose this one.</span>

<span style="color: rgb(74, 158, 232);">If JUMP only moves 2 steps out of 3 requested because it hit something, it should be considered as failure.</span>\
B) Stop before the robot and succeed (stop at last valid position)\
<span style="color: rgb(74, 158, 232);">We don't achieve enough steps, so it is cannot be considered as success.</span>\
C) Skip over the robot and keep jumping (allow 'jumping over')

<span style="color: rgb(74, 158, 232);">I don't prefer jump over at this moment, because since we set obstacles and collisions, we really need it to take effects.</span>

Add a new method `jump(n)`

- Check one cell ahead, we want move as far as we can until we are blocked.

When I stop early, I will return

```
{
  "success": False,
  "message": "The position is occupied by another robot: {robot_info}" | "The position is occupied by an obstacle.",
  "position: (x, y, facing, move_count)
}
```

The user may also want to know about where we are at after this execution. So I will also include position in return object.\
Refactored in other executions also.

If we

1. At the beginning, I thought `jump(n)` means `move()` n steps. But then I realized the history track is different. `jump(n)` will be considered as only one record in the history. But every move will have one record.
2. For the calculation of `move_count` , I may choose atomic operation instead of all or nothing. Because previously we decided that we can reach to the fareast as we can. So it actually **moved**. If we choose all-or-nothing, it seems like we stay at the start point.\
   Now we also need to save `move_count` into the history for `undo()` . Because undo may not just decrease move_count by 1 this time.

# Storage

## Multiple robots can coexist on the table

### 2D Array

I will choose 2d array to store the positions of multiple robots.

One trade-off is that large sparse tables waste memory. In that case, using a Set might be more suitable.

- **Table as source of truth** — If the table is tracking robot positions in a grid, but each robot also tracks its own `(x, y)`, how do you keep them in sync? What if they diverge?

### Triple-state problem

1. We should keep **Robot object** as the source of truth

2. **Table.robots grid** is to check whether there is a collision

3. **Table.robot_positions map** may seems unnecessary since Robot object itself already tracked its own position. But since we don't have a robot registry now. We may keep it at the moment. In the future, we can use:

   ```
   robot = RobotRegistry.get(uuid)
   robot.x
   robot.y
   ```

# Collision detection/handling

- They can't occupy the same cell →They need collision detection/handling

  - **PLACE onto occupied cell** — In your `place()` method, you check `is_valid_position()` which now checks for other robots. But what's the expected behavior? Should PLACE fail silently if the cell is occupied, or should it return False and log something? \
    I should keep it consistent for:

    - `place()`
    - `move()`
    - `left()`
    - `right()`
    - `undo()`

    They return their own validation result because it's their responsibility to report blockers to the user, not silently fail without explanation. As for `report()`, we can stay as it is. Because we just need to print something, not a real execution.

- **Robot identity** — You added `id` and `name` to each robot. Currently, we use them for identification since different robots may have the same name. UUIDs are used to track robot positions in the grid. When we want to return a detailed log message about which robot collided, we need the robot's name instead of just the UUID. We may not want to use a registry pattern: Now we can just save `(uuid, name)` in the gird, and use it as the map key also.

  - When the robots move, they will check whether there is an obstacle or another robot occupying the target cell (`robots[x][y]`).

# Robot

- Consider how robots are created, managed, and identified

## ID

Each robot needs:

- **uuid**: unique identifier (no need for incremental numbers)
- **name**: human-readable label

## Init

Open-close & DI

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

I would like to keep my current approach. Robots are independent entities that use the table as a reference; they're not born from the table, and their lifecycle is not tied to it.

## Manage

```python
robot1.execute('PLACE 0,0,NORTH')
robot2.execute('PLACE 1,1,EAST')
```

When the robot is placed or the position is changed, the table needs to update the robots grid:

1. empty the current position
2. occupy the next position

**Undo behavior** — When a robot calls `undo()`, the position is restored from history, but the `table.robots` grid isn't updated. So if robot1 was at (0,0), moved to (0,1), then undo — the grid still thinks robot1 is at (0,1). What happens then?

We also need to consider undo:

1. before: empty the current position
2. after: reset back to previous position