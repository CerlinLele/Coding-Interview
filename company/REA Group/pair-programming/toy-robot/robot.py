import uuid

class Robot:
    """Represents a toy robot that can move on a table (multi-robot support)."""

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
        self.robot_id = self.id  # Alias for compatibility
        self.name = name
        self.x = None
        self.y = None
        self.facing = None
        self.history = []  # (x, y, facing)
        self.move_count = 0

    def is_placed(self):
        """Check if the robot has been placed on the table."""
        return self.x is not None and self.y is not None and self.facing is not None

    def place(self, x, y, facing):
        """Place the robot at position (x, y) facing a direction.

        Design decision 3.1: Direct instantiation + place() pattern
        Design decision 3.2: Robot calls table.register_robot()
        """
        if facing not in self.DIRECTIONS:
            return {"success": False, "message": "Invalid facing direction."}

        validation_result = self.table.is_valid_position(x, y)
        if not validation_result.get("success"):
            return validation_result

        self.x = x
        self.y = y
        self.facing = facing

        self.table.update_robot_grid(self.id, self.name, x, y)
        self.table.update_robot_position(self.id, (x, y, facing, self.move_count))

        return {"success": True, "message": "The position is valid."}
    
    def move(self, direction="forward"):
        """Move the robot one unit forward in the direction it's facing."""

        if not self.is_placed():
            return {"success": False, "message": "Robot is not placed on the table."}

        dx, dy = self.DIRECTION_DELTAS[self.facing]
        if direction == "backward":
            dx, dy = -dx, -dy

        new_x = self.x + dx
        new_y = self.y + dy

        validation_result = self.table.is_valid_position(new_x, new_y)

        if validation_result.get("success"):
            self.history.append((self.x, self.y, self.facing))

            self.table.update_robot_grid(None, None, self.x, self.y)
            self.table.update_robot_position(self.id, None)

            self.x = new_x
            self.y = new_y
            self.move_count += 1

            self.table.update_robot_grid(self.id, self.name, new_x, new_y)
            self.table.update_robot_position(self.id, (new_x, new_y, self.facing, self.move_count))

        return validation_result

    def backward(self):
        """Move the robot one unit backward (opposite to the direction it's facing)."""
        return self.move(direction="backward")
    
    def left(self):
        """Rotate the robot 90 degrees to the left."""
        if not self.is_placed():
            return {"success": False, "message": "Robot is not placed on the table."}

        self.history.append((self.x, self.y, self.facing))

        current_index = self.DIRECTIONS.index(self.facing)
        self.facing = self.DIRECTIONS[(current_index - 1) % 4]
        return {"success": True, "message": "Rotated 90 degrees to the left."}
    
    def right(self):
        """Rotate the robot 90 degrees to the right."""
        if not self.is_placed():
            return {"success": False, "message": "Robot is not placed on the table."}

        self.history.append((self.x, self.y, self.facing))

        current_index = self.DIRECTIONS.index(self.facing)
        self.facing = self.DIRECTIONS[(current_index + 1) % 4]
        return {"success": True, "message": "Rotated to the right."}

    def undo(self):
        """Undo the last command (per-robot UNDO).

        Design decision 4.1: Support both per-robot and global UNDO
        """
        if not self.history:
            return {"success": False, "message": "No history to undo."}
        
        current_state = self.history.pop()
        if current_state[2] == self.facing:
            if self.move_count <= 0:
                return {"success": False, "message": "No moves to undo."}
            self.move_count -= 1

        self.table.update_robot_grid(None, None, self.x, self.y)
        self.table.update_robot_position(self.id, None)

        self.x, self.y, self.facing = current_state

        self.table.update_robot_grid(self.id, self.name, self.x, self.y)
        self.table.update_robot_position(self.id, (self.x, self.y, self.facing, self.move_count))
        
        return {"success": True, "message": "Last command has been undone."}
    
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
                
                return self.place(x, y, facing)
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
