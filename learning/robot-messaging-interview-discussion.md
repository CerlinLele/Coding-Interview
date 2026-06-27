# Robot Messaging — Interview Discussion Points

## Context

In the toy robot pair-programming interview, the interviewer may ask:

> "If you wanted to support message passing between robots, how would you extend the design?"

This is a **Level 4 open discussion** question — no implementation expected, just architectural thinking. It typically comes up in the last 10-15 minutes as a wrap-up prompt.

---

## Concrete Scenarios

**1. Cooperative movement**
A tells B: "I'm heading north, move aside." B receives the message and clears the cell. More sophisticated than simple collision — it's negotiation rather than "bump and stop."

**2. Formation / following**
A sends "FOLLOW ME" to B. B then mirrors A's movements each turn. Leader-follower pattern — B stops accepting external commands and only listens to A.

**3. Relay / item handoff**
A drops a "package" at (2,3) and messages B: "Item at (2,3), come pick it up." Introduces state transfer between robots.

**4. Warning / broadcast**
A detects an obstacle ahead and broadcasts to all robots: "(3,4) is blocked, avoid it." Shared information, distributed perception.

---

## How to Answer in the Interview

Don't try to cover all scenarios. Pick the simplest one and describe a minimal design:

> "For example, robot A wants B to move aside. Simplest implementation: give each Robot an `inbox` list. A executes `SEND B 'move_aside'`, which appends a message to B's inbox. Next time B runs, it can `CHECK_INBOX` and decide whether to respond. It's still serial turn-based — no concurrency needed."

Then stop. Let the interviewer decide whether to go deeper. **Do not voluntarily escalate the complexity.**

---

## Relationship to Concurrency

Message passing itself is a **communication mechanism**; concurrency is an **execution model**. They overlap when:

- Robots operate independently and asynchronously (each on its own thread/event loop)
- A sends a message but doesn't wait for B to respond — both keep moving
- A and B send messages to each other simultaneously — ordering matters

But in this interview, the interviewer most likely just wants to see you design a simple interaction interface, not dive into concurrent architecture.

**Pragmatic framing:**

> "If messages are synchronous — A sends, B's inbox gets it, B processes next turn — then nothing changes about the execution model. It's still one command at a time. If we need true async (robots acting in parallel, reacting to messages in real time), that's a fundamentally different architecture — event loops or actor model — and I'd want to confirm that's the actual requirement before going there."

---

## Key Principles to Demonstrate

- **Pragmatism** — default to the simplest model (synchronous inbox, turn-based processing)
- **Recognise the boundary** — know where "simple extension" ends and "architectural shift" begins
- **Don't over-build** — one sentence acknowledging the complex path is enough; don't design it unless asked
