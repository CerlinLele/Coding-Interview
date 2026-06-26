class Table:
    """Represents the tabletop surface."""
    
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
    
    def is_valid_position(self, x, y):
        """
        1. Check if a position is within the table boundaries.
        2. Check if the position is not occupied by an obstacle.
        3. Check if the position is not occupied by another robot.
        """
        success = False
        message = "This is not a valid position."

        # check if the position is within the table boundaries
        if not (0 <= x < self.width and 0 <= y < self.height):
            message = "The position is out of the table boundaries."
        # check if the position is occupied by an obstacle
        elif self.obstacles[x][y] == 1:
            message = "The position is occupied by an obstacle."
        # check if the position is occupied by another robot
        elif self.robots[x][y] is not None:
            message = f"The position is occupied by another robot: {self.robots[x][y].name}."
        # if the position is valid, return success and message
        else:
            success = True
            message = "The position is valid."
        return {
            "success": success,
            "message": message,
        }
        