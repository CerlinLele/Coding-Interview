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

1. At the beginning, I thought `jump(n)` means `move()` n steps. But then I realized the history track is different. `jump(n)` will be considered as only one record in the history. But every move will have one record.
2. For the calculation of `move_count` , I may choose atomic operation instead of all or nothing. Because previously we decided that we can reach to the fareast as we can. So it actually **moved**. If we choose all-or-nothing, it seems like we stay at the start point.\
   Now we also need to save `move_count` into the history for `undo()` . Because undo may not just decrease move_count by 1 this time.

# Storage

## Multiple robots can coexist on the table

### 2D Array

I will choose 2d array to store the positions of multiple robots.

- **At what point would you switch from 2D array to a Set-based approach?**

  I'll start with **2D array** because:

  - Collision detection is O(1) — just check `grid[x][y]`
  - Most practical cases (8×8, 10×10 boards) are small enough
  - Implementation is straightforward

  Switch to **Set-based** when:

  - Grid size &gt; 100×100 **AND** robot count &lt; 5% of grid size
  - Example: A 1000×1000 map with only 50 robots → O(50) space vs O(1,000,000) for 2D array
  - Memory savings: 1,000,000 cells × 8 bytes = 8MB vs 50 positions × 16 bytes = 0.8KB

  **Decision strategy:** Use a hybrid approach

  ```python
  table = Table(width=1000, height=1000, robot_capacity=50)
  # Automatically picks Set if density < 5%, otherwise 2D array
  ```

  For this toy robot project, stick with **2D array** — the grid is small enough that memory isn't a real concern, and the O(1) collision check is worth the simplicity.

- **Table as source of truth** — If the table is tracking robot positions in a grid, but each robot also tracks its own `(x, y)`, how do you keep them in sync? What if they diverge?

  I use a **"single source of truth"** pattern:

  - **Robot object** holds the authoritative state: `(x, y, facing, move_count)`
  - **Table.robots grid** is a cache for fast O(1) collision detection: `grid[x][y] = robot_id`
  - **Table.robot_positions map** is a registry: `positions[robot_id] = (x, y, facing, move_count)`

  **Sync strategy:**

  ```
  When robot moves:
    1. Update Robot.x, Robot.y (primary source)
    2. Update Table.robots grid (cache)
    3. Update Table.robot_positions map (registry)
  
  When reading state:
    - Always read from Robot object, never from cache
    - Cache/registry are sync'd immediately after every action
  ```

  **If they diverge (bug):** The robot object is always correct. If the grid gets out of sync (e.g., due to a programming error), we can rebuild the grid from the robot objects:

  ```python
  def rebuild_grid(self):
      self.robots = [[None] * self.width for _ in range(self.height)]
      for robot in all_robots:
          self.robots[robot.x][robot.y] = robot.id
  ```

  This keeps the design simple: one source of truth, two caches for performance.

# Collision detection/handling

- They can't occupy the same cell → They need collision detection/handling

  - **PLACE onto occupied cell** — In your `place()` method, you check `is_valid_position()` which now checks for other robots. But what's the expected behavior? Should PLACE fail silently if the cell is occupied, or should it return False and log something?

  **Unified return format for all commands:**

  ```python
  {
    "success": bool,
    "message": str,           # Explains why it failed or what happened
    "position": (x, y, facing, move_count)  # Current state after action
  }
  ```

  - `place(0, 0, 'NORTH')` on occupied cell → `{"success": False, "message": "Cell (0,0) is occupied by Robot B", "position": None}`
  - `move()` blocked by wall → `{"success": False, "message": "Cannot move: boundary at (5,0)", "position": (4, 0, 'NORTH', 5)}`
  - `move()` succeeds → `{"success": True, "message": "Moved forward", "position": (5, 0, 'NORTH', 6)}`

  This keeps the caller informed: they see exactly what blocked them and the current state, so they can decide what to do next.

- **Robot identity** — You added `id` and `name` to each robot. Currently, we use them for identification since different robots may have the same name. UUIDs are used to track robot positions in the grid. When we want to return a detailed log message about which robot collided, we need the robot's name instead of just the UUID.

  **Design:**

  - **id (UUID)**: Internal identifier for the Table to track positions in the grid. Not exposed to users.
  - **name**: Human-readable label for messaging and debugging.

  **Implementation:**

  ```python
  grid[x][y] = robot.id  # Store UUID in grid for fast lookup
  
  # When collision happens, translate to user-friendly message:
  blocked_robot = find_robot_by_id(grid[target_x][target_y])
  return {"success": False, 
          "message": f"Cannot move: blocked by {blocked_robot.name}"}
  ```

  This gives us O(1) collision detection while keeping error messages readable. We don't need a separate registry yet — the Table can look up robot objects by iterating its robot list (for a small number of robots, this is fine; a registry pattern scales better for 100+ robots).

## **Robot Pushing Mechanic**

`PUSH X` : x default to 1, consider only 1 step at this moment

`robot1.push(1)`

- **Check what's one step ahead**
  - Is it empty? → Fail (nothing to push), the robot stay still
  - Is it a wall/obstacle? → Fail
  - Is it another robot: robot2? → Try to push it
    - robot2 will do the same check as robot1
      - Check if the cell *after* that robot is free
      - If yes → both robots move, both succeed
      - If no → push fails entirely, neither moves
        - So we don't need to check the thrid time?

The users need to know more about why they are blocked.

```
# Success case
result = robot1.execute("PUSH 1")
# {"success": True, "message": "Pushed Robot B forward", ...}

# Failure case
result = robot1.execute("PUSH 1")
# {"success": False, "message": "Cannot push: Robot B blocked by wall", ...}
```

# Robot

- Consider how robots are created, managed, and identified

## ID

Each robot needs:

- **uuid**: unique identifier (no need for incremental numbers)
- **name**: human-readable label

## Init

**Should the Table manage robot creation and lifecycle?**

Option A: User creates robots, passes Table as dependency

```python
table = Table(5, 5)
robot1 = Robot(table, 'Robot 1')
robot2 = Robot(table, 'Robot 2')
```

Option B: Table creates and manages robots (factory pattern)

```python
table = Table(5, 5)
robot1 = table.create_robot('Robot 1')
robot2 = table.create_robot('Robot 2')
all_robots = table.get_all_robots()
```

**I choose Option A** because:

- **Separation of concerns**: Robot and Table are independent entities; Table doesn't own robots
- **Flexibility**: Robot doesn't have to be tied to the Table's lifetime. You can create robots before the table or share robots across tables
- **Simplicity**: Fewer dependencies = fewer things to manage
- **Use case fit**: This toy robot is command-driven, not complex enough to need a registry pattern

For a larger system (e.g., multi-table simulation), Option B would make sense.

### Robot Registry

Now we may need a robot registry to manage robot. I don't want to bind the life cycle of the robots with a table.

```
robotRegistry = RobotRegistry()
uuid = robotRegistry.create_robot(name)
robot = robotRegistry.get_by_id(uuid)
```

## Manage

**Grid update on every action:**

When robot moves/rotates/undoes, we must keep Table.robots grid in sync:

```
Old position: grid[old_x][old_y] = None
New position: grid[new_x][new_y] = robot_id
```

**Undo behavior** — When `undo()` is called:

```python
def undo(self):
    if not self.history:
        return {"success": False, "message": "No moves to undo"}
    
    # Get previous state
    prev_x, prev_y, prev_facing, prev_move_count = self.history.pop()
    
    # Clear old position from grid
    self.table.update_robot_grid(None, None, self.x, self.y)
    self.table.update_robot_position(self.id, None)
    
    # Restore to previous state
    self.x, self.y, self.facing, self.move_count = prev_x, prev_y, prev_facing, prev_move_count
    
    # Update grid with new position
    self.table.update_robot_grid(self.id, self.name, self.x, self.y)
    self.table.update_robot_position(self.id, (self.x, self.y, self.facing, self.move_count))
    
    return {"success": True, "message": "Undo successful", "position": (self.x, self.y, self.facing, self.move_count)}
```

**Key insight:** History stores the **complete state** `(x, y, facing, move_count)`, not just position. This way, undo is atomic — one history entry = one reversible action, regardless of whether it was a move (which increments move_count) or a rotation (which doesn't).