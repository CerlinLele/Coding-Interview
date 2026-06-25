class Table:
    """Represents the tabletop surface."""
    
    def __init__(self, width, height, obstacles=None):
        self.width = width
        self.height = height
        if obstacles is None:
            obstacles = []
        else:
            self.obstacles = [[0 for _ in range(width)] for _ in range(height)]
            for obstacle in obstacles:
                self.obstacles[obstacle[0]][obstacle[1]] = 1
    
    def is_valid_position(self, x, y):
        """Check if a position is within the table boundaries."""
        return 0 <= x < self.width and 0 <= y < self.height and self.obstacles[x][y] == 0