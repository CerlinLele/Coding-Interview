# Multi-Robot System - Design Decisions

## 1. Robot Identification & Storage

### Question 1.1: Robot ID Assignment

**Problem**: How do we uniquely identify each robot?

**Options**:
- (A) Auto-increment ID (Robot_1, Robot_2, ...)
- (B) User-provided ID (PLACE robot_id, x, y, facing)
- (C) UUID/random ID

**Your Answer**: 

---

### Question 1.2: Robot Storage Structure

**Problem**: How do you store robots in the Table for efficient collision detection?

**Scenario**: You have 3 robots on a 5×5 table at (0,0), (2,2), (3,4).

You need to:
1. Check "Is there a robot at (2,3)?" → O(1)
2. Get robot object at (2,2) → O(1)
3. Iterate all robots → need full list
4. Update positions when robot moves

**Options**:
- (A) Only dict: `{robot_uuid: robot_object}` — Con: O(n) collision check
- (B) Only 2D grid: `robots_grid[x][y] = robot_uuid` — Con: can't iterate easily
- (C) Hybrid: Both dict AND 2D grid — Pro: O(1) everything, Con: dual maintenance
- (D) 2D grid stores object directly: `robots_grid[x][y] = robot_object`

**Your Answer**: 

**Follow-up**: What if table is 1,000,000 × 1,000,000 with only 10 robots?

---

## 2. Collision Detection Strategy

### Question 2.1: When to Detect Collision?

**Problem**: At what point in `move()` should we detect collision?

**Options**:
- (A) Before state change (validate new position first)
- (B) After state change (change, then check & rollback)
- (C) In `is_valid_position()` as part of boundary check

**Your Answer**: 

**Rationale**: 

---

### Question 2.2: Collision Response

**Problem**: What should `move()` return when collision occurs?

**Options**:
- (A) Boolean: `True/False`
- (B) Dict: `{"success": False, "collision_with": robot_id, "position": (x,y)}`
- (C) Exception: `raise CollisionException(...)`
- (D) Callback/Event: trigger event listener

**Your Answer**: 

**Rationale**: 

---

## 3. Multi-Robot Initialization & Updates

### Question 3.1: Creating Multiple Robots

**Problem**: How do we create and register multiple robots on the same table?

**Options**:
- (A) Direct: `robot1 = Robot(table, robot_id=uuid.uuid4())`
- (B) Table factory: `robot_id = table.create_robot(x, y, facing)`
- (C) Two-step: `robot = Robot(table)` then `table.register_robot(robot)`
- (D) Separate manager: `RobotManager(table).create_robot(...)`

**Your Answer**: 

**Rationale**: 

---

### Question 3.2: Table Update After Robot Move

**Problem**: Who updates the robots storage when a robot moves?

**Options**:
- (A) `Robot.move()` calls `table.update_robot_position(old_pos, new_pos)`
- (B) `Robot.move()` updates `table.robots_grid` directly
- (C) Table provides callback that Robot calls
- (D) External orchestrator handles updates

**Your Answer**: 

**Rationale**: 

---

## 4. Undo & History with Multiple Robots

### Question 4.1: UNDO Scope

**Problem**: Should UNDO be per-robot or system-wide?

**Options**:
- (A) Per-robot: `robot.undo()` undoes only that robot's last move
- (B) Global: `table.undo()` undoes the last move across all robots
- (C) Both: support both modes

**Your Answer**: 

**Rationale**: 

---

## 5. Backward Compatibility

### Question 5.1: Single Robot Support

**Problem**: Should the new system still work with a single robot (like the original Toy Robot)?

**Options**:
- (A) Yes, fully backward compatible — make multi-robot code work for 1 robot too
- (B) No, separate implementations — keep old single-robot, build new multi-robot
- (C) Migration layer — old API calls new multi-robot internally

**Your Answer**: 

**Rationale**: 

---

## Summary

Once you fill these in, I'll review, add feedback, and we commit everything together.

**Ready to answer?** Just edit this file and fill in your answers. 👍
