class Table:
    """Represents the tabletop surface with multi-robot support."""

    def __init__(self, width, height, obstacles=None):
        self.width = width
        self.height = height

        # initialize obstacles grid
        self.obstacles = [[0 for _ in range(width)] for _ in range(height)]
        # if obstacles are provided, mark them
        if obstacles is not None:
            for obstacle in obstacles:
                self.obstacles[obstacle[0]][obstacle[1]] = 1

        # initialize robots grid
        self.robots = [[None for _ in range(width)] for _ in range(height)]

        # initialize robot registry {uuid:  Robot object}
        self.robot_registry = {}

    def register_robot(self, uuid, robot):
        """Register a robot by uuid."""
        self.robot_registry[uuid] = robot

    def get_robot_by_id(self, uuid):
        """Get a robot by uuid."""
        return self.robot_registry.get(uuid)

    def update_robot_grid(self, uuid, name, x, y):
        """Update the robot grid by uuid."""
        if uuid is None and name is None:
            self.robots[x][y] = None
        else:
            self.robots[x][y] = (uuid, name)

    def get_robot_by_position(self, x, y):
        """Get the robot grid by x and y."""
        return self.robots[x][y]

    def get_robot_position(self, uuid):
        """Get the position of a robot tracked on this table by uuid."""
        robot = self.robot_registry.get(uuid)
        if robot is None:
            return None
        
        return f"{robot.x},{robot.y},{robot.facing},{robot.move_count}"

    def is_valid_position(self, x, y):
        """
        1. Check if a position is within the table boundaries.
        2. Check if the position is not occupied by an obstacle.
        3. Check if the position is not occupied by another robot.
        """
        success = False
        message = "This is not a valid position."
        reason = None
        collision_with = None

        # check if the position is within the table boundaries
        if not (0 <= x < self.width and 0 <= y < self.height):
            message = "The position is out of the table boundaries."
            reason = "boundary"
        # check if the position is occupied by an obstacle
        elif self.obstacles[x][y] == 1:
            message = "The position is occupied by an obstacle."
            reason = "obstacle"
        # check if the position is occupied by another robot
        elif self.get_robot_by_position(x, y) is not None:
            robot_info = self.get_robot_by_position(x, y)
            collision_with = str(robot_info[0])  # robot UUID
            message = f"The position is occupied by another robot: {robot_info}."
            reason = "collision"
        # if the position is valid, return success and message
        else:
            success = True
            message = "The position is valid."

        result = {
            "success": success,
            "message": message,
        }
        if reason:
            result["reason"] = reason
        if collision_with:
            result["collision_with"] = collision_with
        return result
        
