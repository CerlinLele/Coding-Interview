import uuid

class Robot:
    """Represents a toy robot that can move on a table."""
    
    DIRECTIONS = ['NORTH', 'EAST', 'SOUTH', 'WEST']
    DIRECTION_DELTAS = {
        'NORTH': (0, 1),
        'EAST': (1, 0),
        'SOUTH': (0, -1),
        'WEST': (-1, 0)
    }
    
    def __init__(self, table, name="anonymous"):
        self.table = table
        self.id = uuid.uuid4()
        self.name = name
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
        
        self.table.robots[x][y] = self

        return True
    
    def move(self, direction="forward"):
        """Move the robot one unit forward in the direction it's facing."""

        if not self.is_placed():
            return False
        
        dx, dy = self.DIRECTION_DELTAS[self.facing]
        if direction == "backward":
            dx, dy = -dx, -dy
        
        new_x = self.x + dx
        new_y = self.y + dy
        
        if self.table.is_valid_position(new_x, new_y):
            self.history.append((self.x, self.y, self.facing)) 

            self.table.robots[self.x][self.y] = None

            self.x = new_x
            self.y = new_y
            self.move_count += 1

            self.table.robots[new_x][new_y] = self

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
    def undo(self):
        """Undo the last command."""
        if not self.history:
            return False
        
        current_state = self.history.pop()
        if current_state[2] == self.facing:
            self.move_count -= 1

        self.x, self.y, self.facing = current_state
        
        return True
    
    def report(self):
        """Return the current position and facing direction."""
        if not self.is_placed():
            return None
        
        return f"{self.x},{self.y},{self.facing},{self.move_count}"
    
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
            return self.move(direction="forward")

        elif command == 'BACKWARD':
            return self.move(direction="backward")
        
        elif command == 'LEFT':
            return self.left()
        
        elif command == 'RIGHT':
            return self.right()
        
        elif command == 'REPORT':
            return self.report()
        
        elif command == 'UNDO':
            return self.undo()
        
        return None