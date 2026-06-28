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

    def append_history(self, x=None, y=None, facing=None, move_count=None, affected_robots = None):
        """Append a history entry."""
        if x is None:
            x = self.x
        if y is None:
            y = self.y
        if facing is None:
            facing = self.facing
        if move_count is None:
            move_count = self.move_count
        if affected_robots is None:
            affected_robots = []
        self.history.append((x, y, facing, move_count, affected_robots))

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
        self.table.register_robot(self.id, self)
        self.table.update_robot_position(self.id, (x, y, facing, self.move_count))

        return {
            "success": True, 
            "message": "Robot is placed successfully",
            "position": (self.x, self.y, self.facing, self.move_count)
        }
    
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
            self.append_history()

            self.table.update_robot_grid(None, None, self.x, self.y)
            self.table.update_robot_position(self.id, None)

            self.x = new_x
            self.y = new_y
            self.move_count += 1

            self.table.update_robot_grid(self.id, self.name, new_x, new_y)
            self.table.update_robot_position(self.id, (new_x, new_y, self.facing, self.move_count))

        validation_result["message"] = f"Moved {direction} successfully"
        validation_result["position"] = (self.x, self.y, self.facing, self.move_count)

        return validation_result

    def backward(self):
        """Move the robot one unit backward (opposite to the direction it's facing)."""
        return self.move(direction="backward")

    def jump(self, steps):
        """Jump forward N steps. Stop if blocked by boundary, obstacle, or robot."""
        if not self.is_placed():
            return {"success": False, "message": "Robot is not placed on the table."}

        start_x, start_y, start_move_count = self.x, self.y, self.move_count
        dx, dy = self.DIRECTION_DELTAS[self.facing]

        for i in range(steps):
            new_x = self.x + dx
            new_y = self.y + dy

            # 1. Check each cell one at a time
            validation_result = self.table.is_valid_position(new_x, new_y)

            # 2. Stop when blocked
            if not validation_result.get("success"):

                # 4. Track history
                if i > 0:
                    self.append_history(start_x, start_y, self.facing, start_move_count)

                validation_result["position"] = (self.x, self.y, self.facing, self.move_count)
                return validation_result

            # 3. Update the grid if you actually move
            self.table.update_robot_grid(None, None, self.x, self.y)
            self.table.update_robot_position(self.id, None)

            self.x = new_x
            self.y = new_y

            self.move_count += 1

            self.table.update_robot_grid(self.id, self.name, new_x, new_y)
            self.table.update_robot_position(self.id, (new_x, new_y, self.facing, self.move_count))

        # 5. Return consistent format
        return {
            "success": True,
            "message": f"Jump {steps} steps successfully",
            "position": (self.x, self.y, self.facing, self.move_count)
        }   

    def push(self, steps=1):
        """Push the robot forward N steps. Stop if blocked by boundary, obstacle, or robot."""
        if not self.is_placed():
            return {"success": False, "message": "Robot is not placed on the table."}

        # Currently we only support pushing one step
        if steps != 1:
            return {"success": False, "message": "Currently we only support pushing one step."}

        # Push the robot forward N steps. Stop if blocked by boundary, obstacle, or robot.
        start_x, start_y, start_facing, start_move_count = self.x, self.y, self.facing, self.move_count
        dx, dy = self.DIRECTION_DELTAS[start_facing]

        # Currently we only support pushing one step

        new_x = start_x + dx
        new_y = start_y + dy

        validation_result = self.table.is_valid_position(new_x, new_y)

        if validation_result.get("success"):
            return {
                "success": False,
                "message": "There is nothing to push.",
                "position": (self.x, self.y, self.facing, self.move_count)
            }

        if validation_result.get("reason") == "boundary":
            validation_result["message"] = "Pushed to the boundary."
            validation_result["position"] = (self.x, self.y, self.facing, self.move_count)
            return validation_result

        if validation_result.get("reason") == "obstacle":
            validation_result["message"] = "Pushed to the obstacle."
            validation_result["position"] = (self.x, self.y, self.facing, self.move_count)
            return validation_result

        if validation_result.get("reason") == "collision":
            next_x = new_x + dx
            next_y = new_y + dy
            next_validation_result = self.table.is_valid_position(next_x, next_y)
            next_validation_result["position"] = (next_x, next_y, self.facing, self.move_count)
            if next_validation_result.get("success"):
                blocked_robot_info = self.table.get_robot_by_position(new_x, new_y)

                if blocked_robot_info:
                    uuid = blocked_robot_info[0]
                    blocked_robot = self.table.get_robot_by_id(uuid)
                    blocked_robot.append_history()
                    blocked_robot.table.update_robot_grid(None, None, blocked_robot.x, blocked_robot.y)
                    blocked_robot.table.update_robot_position(blocked_robot.id, None)

                    blocked_robot.x = next_x
                    blocked_robot.y = next_y
                    blocked_robot.move_count += 1

                    blocked_robot.table.update_robot_grid(blocked_robot.id, blocked_robot.name, blocked_robot.x, blocked_robot.y)
                    blocked_robot.table.update_robot_position(blocked_robot.id, (blocked_robot.x, blocked_robot.y, blocked_robot.facing, blocked_robot.move_count))

                affected_robots = [blocked_robot.id]
                self.append_history(affected_robots=affected_robots)

                self.table.update_robot_grid(None, None, self.x, self.y)
                self.table.update_robot_position(self.id, None)

                self.x = new_x
                self.y = new_y
                self.move_count += 1

                self.table.update_robot_grid(self.id, self.name, self.x, self.y)
                self.table.update_robot_position(self.id, (self.x, self.y, self.facing, self.move_count))

                next_validation_result["message"] = "Pushed to the robot successfully."
                next_validation_result["position"] = blocked_robot.report()
                return next_validation_result
            else:
                return next_validation_result
    
    def left(self):
        """Rotate the robot 90 degrees to the left."""
        if not self.is_placed():
            return {"success": False, "message": "Robot is not placed on the table."}

        self.append_history()

        current_index = self.DIRECTIONS.index(self.facing)
        self.facing = self.DIRECTIONS[(current_index - 1) % 4]
        return {
            "success": True, 
            "message": "Rotated 90 degrees to the left.",
            "position": (self.x, self.y, self.facing, self.move_count)
        }
    
    def right(self):
        """Rotate the robot 90 degrees to the right."""
        if not self.is_placed():
            return {"success": False, "message": "Robot is not placed on the table."}

        self.append_history()

        current_index = self.DIRECTIONS.index(self.facing)
        self.facing = self.DIRECTIONS[(current_index + 1) % 4]
        return {
            "success": True, 
            "message": "Rotated to the right.",
            "position": (self.x, self.y, self.facing, self.move_count)
        }

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

        self.table.update_robot_grid(None, None, self.x, self.y)
        self.table.update_robot_position(self.id, None)

        self.x, self.y, self.facing, self.move_count, affected_robots = current_state

        for robot_id in affected_robots:
            robot = self.table.get_robot_by_id(robot_id)

            affected_state = robot.history.pop()
            
            robot.table.update_robot_grid(None, None, robot.x, robot.y)
            robot.table.update_robot_position(robot.id, None)

            robot.x, robot.y, robot.facing, robot.move_count = affected_state[:4]

            robot.table.update_robot_grid(robot.id, robot.name, robot.x, robot.y)
            robot.table.update_robot_position(robot.id, (robot.x, robot.y, robot.facing, robot.move_count))

        self.table.update_robot_grid(self.id, self.name, self.x, self.y)
        self.table.update_robot_position(self.id, (self.x, self.y, self.facing, self.move_count))
        
        return {
            "success": True, 
            "message": "Last command has been undone.",
            "position": (self.x, self.y, self.facing, self.move_count)
        }
    
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

        elif command.startswith('PUSH'):
            parts = command.split()
            if len(parts) != 2:
                return self.push(1)
            try:
                steps = int(parts[1])
                return self.push(steps)
            except (ValueError, IndexError):
                return None

        elif command == 'MOVE':
            return self.move(direction="forward")

        elif command == 'BACKWARD':
            return self.move(direction="backward")

        elif command.startswith('JUMP'):
            parts = command.split()
            if len(parts) != 2:
                return None
            try:
                steps = int(parts[1])
                return self.jump(steps)
            except (ValueError, IndexError):
                return None

        elif command == 'LEFT':
            return self.left()

        elif command == 'RIGHT':
            return self.right()

        elif command == 'REPORT':
            return self.report()

        elif command == 'UNDO':
            return self.undo()

        return None
