class Table:
    """Represents the tabletop surface with multi-robot support."""

    def __init__(self, width, height, obstacles=None):
        self.width = width
        self.height = height

        # Obstacles: 1 = obstacle, 0 = free
        self.obstacles = [[0 for _ in range(width)] for _ in range(height)]
        if obstacles is not None:
            for obstacle in obstacles:
                self.obstacles[obstacle[0]][obstacle[1]] = 1

        # Multi-robot tracking (design decision 1.2: hybrid storage)
        self.robots_dict = {}  # {robot_uuid: robot_object}
        self.robots_grid = [[None for _ in range(width)] for _ in range(height)]  # {x,y} -> robot_uuid

        # Global command history for global UNDO (design decision 4.1)
        self.command_history = []

    def is_valid_position(self, x, y):
        """Check if a position is valid (boundary, obstacle, collision-free).

        This implements design decision 2.1: collision detection inside is_valid_position()
        """
        # Check boundaries
        if not (0 <= x < self.width and 0 <= y < self.height):
            return False

        # Check obstacles
        if self.obstacles[x][y] == 1:
            return False

        # Check collision with other robots
        if self.robots_grid[x][y] is not None:
            return False

        return True

    def register_robot(self, robot, x, y, facing):
        """Register a robot on the table at initial position.

        Called from robot.place() during initialization.
        """
        # Store robot in dict
        self.robots_dict[robot.robot_id] = robot

        # Mark position in grid
        self.robots_grid[x][y] = robot.robot_id

    def update_robot_position(self, old_pos, new_pos, robot_uuid):
        """Update robot's position in tracking structures.

        This implements design decision 3.2: Robot calls table.update_robot_position()
        """
        old_x, old_y = old_pos
        new_x, new_y = new_pos

        # Clear old position
        self.robots_grid[old_x][old_y] = None

        # Set new position
        self.robots_grid[new_x][new_y] = robot_uuid

    def get_robot(self, robot_uuid):
        """Retrieve a robot by UUID."""
        return self.robots_dict.get(robot_uuid)

    def get_robot_at_position(self, x, y):
        """Get the robot UUID at a specific position, if any."""
        return self.robots_grid[x][y]

    def get_all_robots(self):
        """Return all robots on the table."""
        return list(self.robots_dict.values())

    def record_command(self, robot_uuid, command_type):
        """Record a command for global UNDO history.

        This supports design decision 4.1: global UNDO
        """
        self.command_history.append({
            "robot_uuid": robot_uuid,
            "command_type": command_type,
            "timestamp": len(self.command_history)
        })

    def undo_global(self):
        """Undo the last command globally.

        This supports design decision 4.1: global UNDO
        """
        if not self.command_history:
            return False

        # Pop last command
        last_cmd = self.command_history.pop()
        robot = self.get_robot(last_cmd["robot_uuid"])

        if robot:
            return robot.undo()
        return False
