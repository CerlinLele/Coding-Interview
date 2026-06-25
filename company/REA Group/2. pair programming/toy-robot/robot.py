class Robot:
    """Represents a toy robot that can move on a table."""
    
    DIRECTIONS = ['NORTH', 'EAST', 'SOUTH', 'WEST']
    DIRECTION_DELTAS = {
        'NORTH': (0, 1),
        'EAST': (1, 0),
        'SOUTH': (0, -1),
        'WEST': (-1, 0)
    }
    
    def __init__(self, table):
        self.table = table
        self.x = None
        self.y = None
        self.facing = None
        self.history = [] # (x, y, facing)
        self.move_count = 0
    
    def is_placed(self):
        """Check if the robot has been placed on the table."""
        return self.x is not None and self.y is not None and self.facing is not None
    
    def place(self, x, y, facing):
        """Place the robot at position (x, y) facing a direction."""
        if facing not in self.DIRECTIONS:
            return False
        
        if not self.table.is_valid_position(x, y):
            return False
        
        self.x = x
        self.y = y
        self.facing = facing
        return True
    
    def move(self):
        """Move the robot one unit forward in the direction it's facing."""

        if not self.is_placed():
            return False
        
        dx, dy = self.DIRECTION_DELTAS[self.facing]
        new_x = self.x + dx
        new_y = self.y + dy
        
        if self.table.is_valid_position(new_x, new_y):
            self.history.append((self.x, self.y, self.facing)) 

            self.x = new_x
            self.y = new_y
            self.move_count += 1
            return True
        
        return False
    
    def left(self):
        """Rotate the robot 90 degrees to the left."""
        
        if not self.is_placed():
            return False

        self.history.append((self.x, self.y, self.facing))
        
        current_index = self.DIRECTIONS.index(self.facing)
        self.facing = self.DIRECTIONS[(current_index - 1) % 4]
        return True
    
    def right(self):
        """Rotate the robot 90 degrees to the right."""

        if not self.is_placed():
            return False

        self.history.append((self.x, self.y, self.facing))
        
        current_index = self.DIRECTIONS.index(self.facing)
        self.facing = self.DIRECTIONS[(current_index + 1) % 4]
        return True

    def backward(self):
        """Move the robot one unit backward in the direction it's facing."""

        if not self.is_placed():
            return False
        
        dx, dy = self.DIRECTION_DELTAS[self.facing]
        new_x = self.x - dx
        new_y = self.y - dy
        
        if self.table.is_valid_position(new_x, new_y):
            self.history.append((self.x, self.y, self.facing))
            self.x = new_x
            self.y = new_y
            self.move_count += 1
            return True
        
        return False    
    
    def undo(self):
        """Undo the last command."""
        if not self.history:
            return False
        
        self.x, self.y, self.facing = self.history.pop()
        return True
    
    def report(self):
        """Return the current position and facing direction."""
        if not self.is_placed():
            return None
        
        return f"{self.x},{self.y},{self.facing}"
    
    def execute(self, command):
        """Execute a command string."""

        command = command.strip().upper()
        
        if command.startswith('PLACE'):
            parts = command.split()
            if len(parts) != 2:
                return None
            
            try:
                coords_and_facing = parts[1].split(',')
                if len(coords_and_facing) != 3:
                    return None
                
                x = int(coords_and_facing[0])
                y = int(coords_and_facing[1])
                facing = coords_and_facing[2]
                
                self.place(x, y, facing)
            except (ValueError, IndexError):
                return None
        
        elif command == 'MOVE':
            self.move()
        
        elif command == 'LEFT':
            self.left()
        
        elif command == 'RIGHT':
            self.right()
        
        elif command == 'REPORT':
            return self.report()

        elif command == 'BACKWARD':
            self.backward()
        
        elif command == 'UNDO':
            return self.undo()
        
        return None