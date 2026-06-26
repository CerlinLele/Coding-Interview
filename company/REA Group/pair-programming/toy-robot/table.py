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
        return 0 <= x < self.width and 0 <= y < self.height and self.obstacles[x][y] == 0 and self.robots[x][y] is None