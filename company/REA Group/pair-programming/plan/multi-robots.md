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