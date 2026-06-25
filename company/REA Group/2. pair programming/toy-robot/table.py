class Table:
    """Represents the tabletop surface."""
    
    def __init__(self, width, height):
        self.width = width
        self.height = height
    
    def is_valid_position(self, x, y):
        """Check if a position is within the table boundaries."""
        return 0 <= x < self.width and 0 <= y < self.height