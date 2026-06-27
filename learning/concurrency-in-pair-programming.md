# Concurrency in the Toy Robot Pair-Programming Interview

## TL;DR — Will they ask about concurrency?

Low probability, but not zero.

REA pair programming assesses **Pragmatism, Learning Mindset, and code organisation** — not algorithms or systems programming. The instructions explicitly say they are *not* assessing language capability, and that "simple is often better." Real multithreading (threads / asyncio / locks) does **not** fit the tone of this interview — it is too systems-heavy and too easy to over-engineer.

But there is one **trigger**: the current design has **multiple robots sharing a single `Table`**. That naturally invites an open-ended discussion question:

> "What if these robots executed commands concurrently? e.g. two robots both want to move into the same cell at the same time?"

This is *not* a request to write threaded code. It tests whether you can **recognise a race condition**.

---

## The real race in the current code

If pushed, point at `move()` in `robot.py` — it is a **check-then-act** pattern:

```python
validation_result = self.table.is_valid_position(new_x, new_y)  # 1. CHECK
if validation_result.get("success"):
    # ... 2. only THEN occupy the cell
    self.table.update_robot_grid(self.id, self.name, new_x, new_y)
```

The check and the occupation are **not atomic** — meaning these two steps are not an indivisible unit; something else can happen in between. Serial execution is fine because no one can interrupt. But under concurrency the gap becomes exploitable:

```
Robot A: check (2,3) → empty ✓
                                    Robot B: check (2,3) → empty ✓  (A hasn't written yet)
Robot A: occupy (2,3)
                                    Robot B: occupy (2,3) ← overwrites A!
```

Both pass the check because the cell *was* empty at the moment each looked. But both then write into it — the later write overwrites the earlier one, corrupting the grid state.

**Atomic** means "either the whole operation completes without interruption, or it doesn't happen at all" — like a database transaction. The fix is to make check + occupy a single locked unit so no other thread can slip in between (see `try_occupy` below).

The same check-then-act gap exists in `place()`.

---

## How to respond (aligned with REA values)

**Step 1 — Pragmatically scope it out:**
> "Right now this design executes commands serially on a single thread, so there is no concurrency problem. I'd only need synchronisation if we actually required concurrent execution."

**Step 2 — If they push, identify the problem instead of rushing to add a lock:**
> "The issue is that `is_valid_position` (the check) and occupying the cell are two separate steps — that's a classic check-then-act race condition."

**Step 3 — Offer a gradient of pragmatic options (shows Learning Mindset):**

| Option | What to say |
|--------|-------------|
| Simplest | "The most pragmatic approach is to avoid real concurrency — put commands on a queue and let a single scheduler process them serially. That sidesteps locking entirely." |
| If real concurrency is required | "If we must run concurrently, I'd collapse 'check + occupy' into a single atomic method on the `Table`, e.g. `try_occupy(x, y)`, with a lock inside it — rather than letting each `Robot` check on its own." |
| Over-engineering warning | "I wouldn't start with a fine-grained lock per cell — that's premature optimisation. First confirm there's a genuine concurrency requirement." |

The key insight: **put the lock on the `Table` (the shared resource), not on the `Robot`** — the `Table` is the contended object.

---

## Why `try_occupy` works

The fix is to make the check and the write happen together, so no other robot can slip in between:

```python
import threading

class Table:
    def __init__(self, width, height, obstacles=None):
        # ... existing init
        self._lock = threading.Lock()

    def try_occupy(self, uuid, name, x, y):
        """Atomically validate and claim a cell. Returns the validation dict."""
        with self._lock:
            result = self.is_valid_position(x, y)
            if result["success"]:
                self.update_robot_grid(uuid, name, x, y)
            return result
```

Now `move()` calls `table.try_occupy(...)` instead of doing the check itself. The lock guarantees only one robot can validate-and-claim at a time.

---

## Talking points for the gradient

- **Queue / single scheduler** — robots submit commands, one consumer thread applies them in order. No shared-state locking needed at all. Most pragmatic for a toy domain.
- **Coarse lock on the Table** — one lock for the whole grid. Simple, correct, fine for small tables. Trade-off: serialises *all* moves even when robots are far apart.
- **Per-cell / per-region locks** — finer granularity, more parallelism, much more complexity and deadlock risk. Only justified at large scale with proven contention.

---

## Why this hits all three assessment dimensions

- **Technical Knowledge** — you named the bug (check-then-act race) and know where the lock belongs.
- **Pragmatism** — you defaulted to "serial / queue" and refused to add locks speculatively.
- **Learning Mindset** — you laid out a gradient of solutions with explicit trade-offs rather than one dogmatic answer.

You don't need to practise writing threaded code. Just internalise the chain:

> **check-then-act race → serialise via a queue, or make it atomic on the Table → only go fine-grained if contention is proven.**
