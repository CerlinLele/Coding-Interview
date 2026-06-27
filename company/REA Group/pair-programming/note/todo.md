# Option 1: Fix the immediate design debt (Quick, tactical)

Address the issues we've identified:

Error messages showing UUID instead of robot name — How do you want to solve this? 

Triple-state problem — Is robot_positions actually necessary, or can you query the grid more efficiently? This would take 30 min, get you to production-ready code, and demonstrates attention to detail.

# Option 2: Scalability & performance (Medium, strategic)

Pick one and design the solution:

Sparse tables: At what dimensions would you switch from 2D array to a Set/hash-based approach? Why? 

Concurrent robots: If multiple robots moved in parallel, what race conditions would emerge? How would you prevent them? This shows systems thinking and forces you to consider real-world constraints.

# Option 3: Architecture review & refactoring (Deep, comprehensive)

Step back and critique your own design:

Does Table have too many responsibilities? (grid + position tracking + validation + error messages) Should there be a separate RobotRegistry or RobotManager class? 

Is your current approach scalable to 100 robots? 1000? What would need to change if robots could move between multiple tables? This is the "senior engineer" level — thinking about maintainability, testability, and future evolution.

## **Robot removal**

What happens when a robot "dies" or leaves the table? Currently, robots can only be placed or moved. There’s no way to remove a robot from the table. Should there be? If so, how would that affect your UUID design?