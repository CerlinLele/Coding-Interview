# Multi-Robot System Design

## Interview Scope
- **Core**: Multi-robot system + collision detection
- **Bonus**: Event listener system (skip for now, focus on implementation)

## Architecture Decisions

### 1. Robot Tracking in Table
**Decision**: Add robot tracking to `Table` class
- `Table` maintains a collection of robots
- `Table` tracks robot positions for collision detection

### 2. Collision Detection: O(1) Lookup
**Decision**: Use 2D grid for position tracking
- `Table.robots_grid[x][y]` stores robot ID or object
- Efficient collision detection when robot tries to move
- Tradeoff: works for small tables (5×5), may need optimization for huge sparse tables

### 3. Robot Identity
**Decision**: Store robot object directly in grid
- `Table.robots_grid[x][y] = robot_object`
- Allows direct access to robot info when collision detected
- Alternative considered: separate `robot_map[(x,y)] = robot_id` (more memory efficient)

### 4. Collision Detection Logic
**Responsibility**: `Robot.move()` detects collision
- `Robot.move()` calls `Table.is_valid_position(new_x, new_y)`
- `Table.is_valid_position()` checks:
  - Boundaries
  - Obstacles
  - Other robots
- Returns: `{"success": True/False, "collision_with": robot_id (if collision)}`

### 5. Grid Update
**Responsibility**: `Table` or `Robot`?
- After move succeeds: update grid
  - Set old position to None/0
  - Set new position to robot object

## Open Questions (To Answer During Coding)
- How to initialize multiple robots on same table?
- How to handle robot ID assignment?
- Command queueing for bonus scope?

## Implementation Steps (Next Phase)
1. Refactor `Table` to support robot tracking
2. Refactor `Robot` to work with multiple robots
3. Update collision detection in `is_valid_position()`
4. Write tests for multi-robot scenarios
5. Bonus: Add event system if time permits
