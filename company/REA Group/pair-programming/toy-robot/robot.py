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

    def __init__(self, table):
        self.table = table
        self.robot_id = uuid.uuid4()  # Design decision 1.1: UUID for robot identification
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
            return False

        if not self.table.is_valid_position(x, y):
            return False

        # Register with table (design decision 3.2)
        self.table.register_robot(self, x, y, facing)

        self.x = x
        self.y = y
        self.facing = facing
        return True

    def _move_to(self, new_x, new_y):
        """Helper: Move to new position and update table tracking.

        This implements design decision 3.2: Robot calls table.update_robot_position()
        """
        old_pos = (self.x, self.y)
        new_pos = (new_x, new_y)

        # Update table tracking
        self.table.update_robot_position(old_pos, new_pos, self.robot_id)

        # Save history
        self.history.append((self.x, self.y, self.facing))

        # Update own state
        self.x = new_x
        self.y = new_y
        self.move_count += 1

    def move(self):
        """Move the robot one unit forward in the direction it's facing.

        Design decision 2.1: Collision detection inside Table.is_valid_position()
        Design decision 2.2: Return dict with details
        """
        if not self.is_placed():
            return {"success": False, "reason": "not_placed", "collision_with": None, "position": None}

        dx, dy = self.DIRECTION_DELTAS[self.facing]
        new_x = self.x + dx
        new_y = self.y + dy

        if self.table.is_valid_position(new_x, new_y):
            self._move_to(new_x, new_y)
            self.table.record_command(self.robot_id, "MOVE")
            return {
                "success": True,
                "reason": "moved",
                "collision_with": None,
                "position": (self.x, self.y)
            }

        # Move failed - determine reason
        if not (0 <= new_x < self.table.width and 0 <= new_y < self.table.height):
            return {
                "success": False,
                "reason": "boundary",
                "collision_with": None,
                "position": (new_x, new_y)
            }

        if self.table.obstacles[new_x][new_y] == 1:
            return {
                "success": False,
                "reason": "obstacle",
                "collision_with": None,
                "position": (new_x, new_y)
            }

        # Must be a collision with another robot
        collision_robot_uuid = self.table.get_robot_at_position(new_x, new_y)
        return {
            "success": False,
            "reason": "collision",
            "collision_with": str(collision_robot_uuid),
            "position": (new_x, new_y)
        }

    def left(self):
        """Rotate the robot 90 degrees to the left."""
        if not self.is_placed():
            return False

        self.history.append((self.x, self.y, self.facing))

        current_index = self.DIRECTIONS.index(self.facing)
        self.facing = self.DIRECTIONS[(current_index - 1) % 4]
        self.table.record_command(self.robot_id, "LEFT")
        return True

    def right(self):
        """Rotate the robot 90 degrees to the right."""
        if not self.is_placed():
            return False

        self.history.append((self.x, self.y, self.facing))

        current_index = self.DIRECTIONS.index(self.facing)
        self.facing = self.DIRECTIONS[(current_index + 1) % 4]
        self.table.record_command(self.robot_id, "RIGHT")
        return True

    def backward(self):
        """Move the robot one unit backward in the direction it's facing."""
        if not self.is_placed():
            return {
                "success": False,
                "reason": "not_placed",
                "collision_with": None,
                "position": None
            }

        dx, dy = self.DIRECTION_DELTAS[self.facing]
        new_x = self.x - dx
        new_y = self.y - dy

        if self.table.is_valid_position(new_x, new_y):
            self._move_to(new_x, new_y)
            self.table.record_command(self.robot_id, "BACKWARD")
            return {
                "success": True,
                "reason": "moved",
                "collision_with": None,
                "position": (self.x, self.y)
            }

        # Backward failed - determine reason
        if not (0 <= new_x < self.table.width and 0 <= new_y < self.table.height):
            return {
                "success": False,
                "reason": "boundary",
                "collision_with": None,
                "position": (new_x, new_y)
            }

        if self.table.obstacles[new_x][new_y] == 1:
            return {
                "success": False,
                "reason": "obstacle",
                "collision_with": None,
                "position": (new_x, new_y)
            }

        # Must be a collision
        collision_robot_uuid = self.table.get_robot_at_position(new_x, new_y)
        return {
            "success": False,
            "reason": "collision",
            "collision_with": str(collision_robot_uuid),
            "position": (new_x, new_y)
        }

    def undo(self):
        """Undo the last command (per-robot UNDO).

        Design decision 4.1: Support both per-robot and global UNDO
        """
        if not self.history:
            return False

        current_state = self.history.pop()
        old_x, old_y, old_facing = current_state

        # If facing changed, we need to update table position too
        if old_facing != self.facing:
            # Rotation only, update table
            pass
        else:
            # Position change, update table
            self.table.update_robot_position((self.x, self.y), (old_x, old_y), self.robot_id)

        # If this was a move, decrement move count
        if old_facing == self.facing:
            self.move_count -= 1

        self.x, self.y, self.facing = old_x, old_y, old_facing
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
            return self.move()

        elif command == 'LEFT':
            self.left()

        elif command == 'RIGHT':
            self.right()

        elif command == 'REPORT':
            return self.report()

        elif command == 'BACKWARD':
            return self.backward()

        elif command == 'UNDO':
            return self.undo()

        return None
