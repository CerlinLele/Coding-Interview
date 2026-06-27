# Toy Robot Multi-Robot Implementation: Gotchas & Lessons Learned

**Date:** 2026-06-28  
**Interview Stage:** Pair Programming - Multi-Robot Extension  
**Status:** 48 tests passing, production-ready for 5×5 table scenarios

---

## The Three Biggest Gotchas

### Gotcha 1: History Format Changes Break Undo Logic

**The Problem:**
When we refactored history from `(x, y, facing)` to `(x, y, facing, move_count)`, we introduced a subtle invariant that **must be maintained**.

```python
# OLD (single robot, no move_count tracking)
self.history.append((self.x, self.y, self.facing))

# NEW (multi-robot with move_count in JUMP scenarios)
self.history.append((self.x, self.y, self.facing, move_count))
```

**Why it's dangerous:**
If a new command (e.g., `DASH`, `SPIN`, etc.) is added and the developer forgets to save the full 4-tuple, `undo()` will silently fail:

```python
def undo(self):
    current_state = self.history.pop()
    # Expects: (x, y, facing, move_count)
    # But gets: (x, y, facing)  ← Missing move_count!
    self.x, self.y, self.facing, self.move_count = current_state  # ❌ ValueError!
```

**Mitigation:**
- **Document the invariant clearly** in the history tuple structure
- **Add a validation function** in undo() to verify tuple length
- **Test every new command** with undo to catch this immediately
- **Consider a NamedTuple** or dataclass to make the structure explicit:

```python
from collections import namedtuple
RobotState = namedtuple('RobotState', ['x', 'y', 'facing', 'move_count'])
self.history.append(RobotState(self.x, self.y, self.facing, self.move_count))
```

---

### Gotcha 2: Grid Consistency — The Triple (Actually Quadruple) Update

**The Problem:**
Every robot movement requires **four coordinated updates** across two objects:

```python
def move(self, direction="forward"):
    # Calculate new position
    new_x, new_y = ...
    
    # STEP 1: Clear old position in table grid
    self.table.update_robot_grid(None, None, self.x, self.y)
    
    # STEP 2: Clear old position in robot_positions map
    self.table.update_robot_position(self.id, None)
    
    # STEP 3: Update robot's internal state
    self.x, self.y = new_x, new_y
    self.move_count += 1
    
    # STEP 4: Write new position to both table structures
    self.table.update_robot_grid(self.id, self.name, new_x, new_y)
    self.table.update_robot_position(self.id, (new_x, new_y, self.facing, self.move_count))
```

**Why it's dangerous:**
This pattern is repeated in:
- `move()` (forward/backward)
- `jump()` (partial moves + complete moves)
- `undo()` (restore old position + update grid)
- `place()` (initial placement)

**If you miss one step:**

| Step skipped | Result |
|---|---|
| Skip Step 1 | Old position still marked occupied → collision false negatives |
| Skip Step 2 | `table.get_robot_position()` returns stale data |
| Skip Step 3 | Grid says robot is here, but robot object says it's there → chaos |
| Skip Step 4 | New position is untracked → robot can occupy same cell as another |

**Mitigation:**
- **Encapsulate this pattern** in a Table method:

```python
def move_robot(self, robot_id, robot_name, from_x, from_y, to_x, to_y, state_tuple):
    """Atomic robot movement: clear old + update new."""
    self.update_robot_grid(None, None, from_x, from_y)
    self.update_robot_position(robot_id, None)
    self.update_robot_grid(robot_id, robot_name, to_x, to_y)
    self.update_robot_position(robot_id, state_tuple)
```

Then Robot calls this single method, not four separate ones:

```python
self.table.move_robot(self.id, self.name, self.x, self.y, new_x, new_y, new_state)
self.x, self.y = new_x, new_y
self.move_count += 1
```

- **Write invariant tests** that verify grid consistency after every operation:

```python
def test_grid_consistency_after_move(self):
    robot.move()
    # Grid says robot is at (0,1)
    assert table.robots[0][1] == (robot.id, robot.name)
    # robot_positions map says robot is at (0,1)
    assert table.get_robot_position(robot.id) == '0,1,NORTH,1'
    # Robot object says it's at (0,1)
    assert robot.x == 0 and robot.y == 1
    # All three match — consistency holds
```

---

### Gotcha 3: State Ownership Violation — Direct Access vs. API

**The Problem:**
We established that **Robot is the source of truth** for its own state, but **Table tracks positions for collision detection**. This creates a temptation for direct attribute access:

```python
# ❌ WRONG: Direct assignment
robot.x = 5
robot.y = 3
# Table still thinks robot is at old position!

# ✅ RIGHT: Go through API
robot.place(5, 3, robot.facing)  # or robot.move() + validation
```

**Why it's dangerous:**
Python doesn't enforce encapsulation. A junior engineer might do:

```python
# Quick hack during debugging or feature development
if some_condition:
    robot.x = new_x  # Bypasses table.update_robot_grid()
    robot.y = new_y
# Then later...
robot2.move()  # Collision detection fails because grid is stale
```

**Real-world scenario from your code:**
In `jump()`, you correctly do this:

```python
self.table.update_robot_grid(None, None, self.x, self.y)  # Clear old
self.x = new_x  # Update robot state
self.y = new_y
self.table.update_robot_grid(self.id, self.name, new_x, new_y)  # Update grid
```

But what if someone refactors to:

```python
self.x = new_x  # ❌ Oops, updated position
self.y = new_y
self.table.update_robot_grid(None, None, self.x, self.y)  # ← Clearing wrong position!
```

**Mitigation:**
- **Use a property with a setter** to prevent direct assignment:

```python
@property
def x(self):
    return self._x

@x.setter
def x(self, value):
    raise AttributeError("Cannot set robot.x directly. Use move() or place().")
```

- **Add a precondition check** in undo() and move():

```python
def move(self):
    # Verify grid is consistent BEFORE move
    current_cell = self.table.robots[self.x][self.y]
    assert current_cell == (self.id, self.name), "Grid is corrupted!"
    
    # ... perform move ...
```

- **Document the contract explicitly:**

```python
class Robot:
    """
    INVARIANT: Robot state (x, y, facing, move_count) must always 
    match table.robots[x][y] and table.robot_positions[id].
    
    DO NOT modify x, y, facing, move_count directly.
    Always use move(), place(), left(), right(), undo().
    """
```

---

## Summary: What to Tell a Junior Engineer

**"When extending this codebase, watch out for:**

1. **History tuple format** — It's `(x, y, facing, move_count)` now. Any new command that changes state must append this full tuple, or undo breaks.

2. **Grid synchronization** — Every move requires clearing the old position AND updating the new position in both `table.robots` grid AND `table.robot_positions` map. Do it atomically or collisions fail silently.

3. **State ownership** — Robot is the source of truth. Don't modify `robot.x` directly. Use the API methods. If the grid ever diverges from the robot's state, you've got a bug that's hard to find."

---

## Lessons for Future Iterations

### If adding more features:
- **Serialization**: Will you save/load robot state? History format change makes this non-trivial.
- **Concurrency**: What if two robots try to move to the same cell simultaneously?
- **Multi-table**: Can robots transfer between tables? Does Robot know which Table it belongs to?
- **Robot removal**: Currently robots can't "leave" the table. Add a `remove()` method.

### If scaling up:
- **Sparse tables**: Switch from 2D array to Set-based approach if width×height > 100K and robot count < 10% occupancy.
- **Batch operations**: JUMP uses a loop of individual moves. Consider a "compound move" optimization.
- **Command validation**: Currently command parsing is basic. Add a command validator/builder if more complex commands arise.

---

## Test Coverage Status

✅ **48 tests passing:**
- Basic robot functionality (13 tests)
- Movement & rotation (14 tests)
- Undo & move_count (12 tests)
- Multi-robot scenarios (8 tests)
- JUMP with collision (1 test)

**Gaps to consider:**
- [ ] JUMP with obstacles
- [ ] JUMP with multiple robots in path
- [ ] Undo after JUMP that moved N steps (verify move_count restored correctly)
- [ ] Grid consistency invariant tests
- [ ] Stress test: 100+ robots on large table
