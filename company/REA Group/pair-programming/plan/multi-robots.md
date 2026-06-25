# Multi-Robot System - Design Decisions

## Question 1.1: Robot ID Assignment

**Problem**: How do we uniquely identify each robot?

**Options**:

- (A) Auto-increment ID (Robot_1, Robot_2, ...)
- (B) User-provided ID (PLACE robot_id, x, y, facing)
- (C) UUID/random ID

**Your Answer**: C ✅

**Rationale**: 

- A: we need to keep a counter
- B: user may provide duplicate IDs
- C: It is just an ID; if we want something human-readable, we can assign it a name

**Interviewer Feedback**:
Strong reasoning! You correctly identified the pain points of (A) and (B). I like your point about decoupling ID from display name — UUID for internal uniqueness, a separate `name` attribute for readability. This is actually a good design pattern (unique identifier ≠ human label).

One thing to consider: UUIDs can be generated on-the-fly (`uuid.uuid4()`) but you'll need to import the `uuid` module. When should this ID be generated — when Robot is created or when it's registered on the table?

When robot is created. Because I want my uuid to mark the life of a robot.

**Decision confirmed**: UUID approach. Moving forward with this.

---

---

## Question 1.2: Robot Storage Structure

**Problem**: How do you store robots in the Table for efficient collision detection and operations?

**Scenario**: You have 3 robots on a 5×5 table:

- Robot A (uuid_1) at (0, 0)
- Robot B (uuid_2) at (2, 2)
- Robot C (uuid_3) at (3, 4)

**Operations you need to support**:

1. **Collision check**: "Is there a robot at (2, 3)?" → must be O(1)
2. **Retrieve robot**: "Get the robot object at (2, 2)" → must be O(1)
3. **Iterate all robots**: "Move all robots north"
4. **Update positions**: When a robot moves from (0,0) to (1,0), update tracking

**Options**:

**(A) Dict only**: `robots_dict = {uuid: robot_object}`

- ✅ Pro: Single source of truth, clean
- ❌ Con: Collision check needs O(n) iteration through all robots

**(B) 2D Grid only**: `robots_grid[x][y] = robot_uuid`

- ✅ Pro: O(1) collision detection
- ❌ Con: Can't iterate easily, need separate mapping uuid→robot, space waste on 1M×1M table

**(C) Hybrid (Dict + Grid)**: 

- `robots_dict = {uuid: robot_object}`
- `robots_grid[x][y] = uuid`
- ✅ Pro: O(1) collision check + O(1) retrieval + easy iteration
- ❌ Con: Dual maintenance (when robot moves, update both structures)

**(D) Grid stores object directly**: `robots_grid[x][y] = robot_object`

- ✅ Pro: All info in one place, no mapping needed
- ❌ Con: Massive memory waste on huge sparse tables (1M×1M with 10 robots = 1 trillion cells!)

**Your Answer**: C ✅

**Rationale**: O(1) for both robot -> position and position -> robot

**Follow-up**: How would your choice scale if the table is 1,000,000 × 1,000,000 but only 10 robots exist?
- Your answer: In that case, maybe we don't need 2D grid.

**Interviewer Feedback**:
Excellent! You nailed it. Hybrid is the right choice for most cases. And your follow-up observation is spot-on — this is exactly where many engineers miss the scaling problem.

**Key insight you discovered**: For a 1M×1M table with only 10 robots, a 2D array wastes **1 trillion cells** of memory. In this case, you'd want to use a **dict-based position map**: `{(x, y): robot_uuid}` instead of the 2D grid.

**Design decision for scaling**:
- Small table (5×5 to maybe 1000×1000): Use hybrid (dict + 2D grid) — fast and simple
- Large table (1M+) with few robots: Use dict only for position tracking — memory efficient
- For now, let's assume we're building for small tables (5×5 to 100×100), so **Hybrid (C) is our choice**

**Decision confirmed**: Hybrid storage (dict + 2D grid) for small-to-medium tables.

Also noted: You wisely added UUID generation on robot creation earlier — good thinking!

---

## Question 2.1: When to Detect Collision?

**Problem**: At what point in `robot.move()` should we detect collision with another robot?

**Scenario**: Robot A is at (1, 1) facing NORTH. Robot B is at (1, 2). Robot A executes MOVE.

```python
def move(self):
    new_x, new_y = calculate_new_position()
    # ❓ At which step do we check for collision?
    # Option A: Check BEFORE changing state
    # Option B: Check AFTER changing state
    # Option C: Check inside is_valid_position()
```

**Options**:

**(A) Check BEFORE state change**:
```python
def move(self):
    new_x, new_y = calculate_new_position()
    # Step 1: Validate new position (including collision check)
    if not self.table.is_valid_position(new_x, new_y):
        return False  # Collision detected, don't move
    # Step 2: If valid, update state
    self.x, self.y = new_x, new_y
    return True
```
- ✅ Pro: Atomic operation, no rollback needed, state always consistent
- ❌ Con: None really

**(B) Check AFTER state change**:
```python
def move(self):
    old_x, old_y = self.x, self.y
    # Step 1: Change state first
    self.x, self.y = calculate_new_position()
    # Step 2: Then check if valid
    if not self.table.is_valid_position(self.x, self.y):
        # Step 3: Rollback if collision
        self.x, self.y = old_x, old_y
        return False
    return True
```
- ✅ Pro: ??? (hard to find a pro)
- ❌ Con: Need rollback logic, risk of inconsistent state if rollback fails, more complex

**(C) Check inside is_valid_position()**:
```python
def move(self):
    new_x, new_y = calculate_new_position()
    if self.table.is_valid_position(new_x, new_y):  # Contains collision check
        self.x, self.y = new_x, new_y
        return True
    return False
```
- ✅ Pro: Single Responsibility — is_valid_position() handles ALL validity checks
- ❌ Con: Same as (A), but with better encapsulation

**Your Answer**: C ✅

**Rationale**: Single responsibility fall on Table side.

**Interviewer Feedback**:
Perfect! You nailed it. Option C is exactly right. By putting the collision check inside `is_valid_position()`, you keep the Table responsible for determining what's "valid" on the table — that's its job. The Robot just calls `is_valid_position()` and trusts the answer.

This also aligns with your earlier decision on hybrid storage — the Table has access to the 2D grid, so it can efficiently check collisions in O(1).

**Additional note**: This also makes the code testable. You can test Robot.move() independently by mocking Table.is_valid_position(), and test Table.is_valid_position() independently.

**Decision confirmed**: Check collision inside Table.is_valid_position(). Robot.move() delegates to Table.

---

## Question 2.2: Collision Response Format

**Problem**: When collision is detected in `robot.move()`, what should we return to the caller?

**Context**: The caller might want to know:
- Did the move succeed or fail?
- If it failed, was it because of collision or boundary?
- If collision, which robot did we hit?
- What position were we trying to move to?

**Options**:

**(A) Boolean only**: `move()` returns `True` or `False`
- Caller: `if robot.move(): print("moved") else: print("blocked")`

**(B) Dict with details**: `move()` returns `{"success": bool, "reason": str, "collision_with": uuid or None, "position": (x, y)}`
- Caller: `result = robot.move(); if not result["success"] and result["reason"] == "collision": handle_collision(result["collision_with"])`

**(C) Exception**: `move()` raises `CollisionException(robot_id, position)` on failure
- Caller: `try: robot.move() except CollisionException as e: handle_collision(e.robot_id)`

**(D) Callback/Event**: `move()` returns boolean, but triggers `on_collision(robot_a, robot_b)` event
- Caller: `robot.on_collision += my_handler; robot.move()`

**Your Answer**: B ✅

**Rationale**: I want to give user better feedback but don't want to over design at the moment. In production, we may need to handle exception or callback.

**Interviewer Feedback**:
Excellent pragmatism! This is exactly the right balance. Option B gives you:
- ✅ Rich feedback for debugging and testing
- ✅ Easy to extend later (add more fields to the dict)
- ✅ No early over-engineering (exception handling can come later if needed)
- ✅ Simple to use: just check `result["success"]`

Your note about production needs is spot-on. If you later want to add event listeners or exception handling, you can wrap the dict response — so B is a solid foundation.

**Design note**: The dict structure will be:
```python
{
    "success": bool,
    "reason": str,  # "boundary" or "collision" or "obstacle"
    "collision_with": uuid or None,
    "position": (x, y)  # where we tried to move
}
```

**Decision confirmed**: Return dict with details from move(). Simple, informative, extensible.