# Architecture review & refactoring (Deep, comprehensive)

Step back and critique your own design:

Does Table have too many responsibilities? (grid + position tracking + validation + error messages) Should there be a separate RobotRegistry or RobotManager class?

Is your current approach scalable to 100 robots? 1000? What would need to change if robots could move between multiple tables? This is the "senior engineer" level — thinking about maintainability, testability, and future evolution.

## **Robot removal**

What happens when a robot "dies" or leaves the table? Currently, robots can only be placed or moved. There’s no way to remove a robot from the table. Should there be? If so, how would that affect your UUID design?