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

**Decision confirmed**: UUID approach. Moving forward with this.

---

## Next: Question 1.2 (coming next)

