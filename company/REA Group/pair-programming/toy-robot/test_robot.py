import pytest
from robot import Robot
from table import Table


class TestTable:
    def test_valid_position(self):
        table = Table(5, 5)
        assert table.is_valid_position(0, 0).get("success") == True
        assert table.is_valid_position(4, 4).get("success") == True
        assert table.is_valid_position(2, 3).get("success") == True
    
    def test_invalid_position(self):
        obstacles = [(1, 3), (2, 3), (3, 3)]
        table = Table(5, 5, obstacles)
        assert table.is_valid_position(-1, 0).get("success")== False
        assert table.is_valid_position(0, -1).get("success") == False
        assert table.is_valid_position(5, 0).get("success") == False
        assert table.is_valid_position(0, 5).get("success") == False
        assert table.is_valid_position(1, 3).get("success") == False
        assert table.is_valid_position(2, 3).get("success") == False
        assert table.is_valid_position(3, 3).get("success") == False   


class TestRobot:
    def setup_method(self):
        self.table = Table(5, 5)
        self.robot = Robot(self.table)

    def test_robot_not_placed_initially(self):
        assert self.robot.is_placed() == False

    def test_place_robot_valid_position(self):
        assert self.robot.place(0, 0, 'NORTH').get("success") == True
        assert self.robot.is_placed() == True
        assert self.robot.x == 0
        assert self.robot.y == 0
        assert self.robot.facing == 'NORTH'

    def test_place_robot_invalid_position(self):
        assert self.robot.place(-1, 0, 'NORTH').get("success") == False
        assert self.robot.place(5, 5, 'NORTH').get("success") == False
        assert self.robot.is_placed() == False

    def test_place_robot_invalid_direction(self):
        assert self.robot.place(0, 0, 'INVALID').get("success") == False
        assert self.robot.is_placed() == False

    def test_move_north(self):
        self.robot.place(0, 0, 'NORTH')
        result = self.robot.move()
        assert result["success"] == True
        assert self.robot.x == 0
        assert self.robot.y == 1

    def test_move_east(self):
        self.robot.place(0, 0, 'EAST')
        result = self.robot.move()
        assert result["success"] == True
        assert self.robot.x == 1
        assert self.robot.y == 0

    def test_move_prevents_falling(self):
        self.robot.place(0, 0, 'SOUTH')
        result = self.robot.move()
        assert result["success"] == False
        assert result["reason"] == "boundary"
        assert self.robot.x == 0
        assert self.robot.y == 0

    def test_move_without_placement(self):
        assert self.robot.move().get("success") == False
    
    def test_left_rotation(self):
        self.robot.place(0, 0, 'NORTH')
        self.robot.left()
        assert self.robot.facing == 'WEST'
        self.robot.left()
        assert self.robot.facing == 'SOUTH'
        self.robot.left()
        assert self.robot.facing == 'EAST'
        self.robot.left()
        assert self.robot.facing == 'NORTH'

    def test_right_rotation(self):
        self.robot.place(0, 0, 'NORTH')
        self.robot.right()
        assert self.robot.facing == 'EAST'
        self.robot.right()
        assert self.robot.facing == 'SOUTH'
        self.robot.right()
        assert self.robot.facing == 'WEST'
        self.robot.right()
        assert self.robot.facing == 'NORTH'

    def test_report(self):
        self.robot.place(1, 2, 'EAST')
        assert self.robot.report() == '1,2,EAST,0'

    def test_report_without_placement(self):
        assert self.robot.report() is None

    def test_execute_place_command(self):
        self.robot.execute('PLACE 0,0,NORTH')
        assert self.robot.is_placed() == True
        assert self.robot.x == 0
        assert self.robot.y == 0
        assert self.robot.facing == 'NORTH'

    def test_execute_sequence(self):
        self.robot.execute('PLACE 0,0,NORTH')
        self.robot.execute('MOVE')
        result = self.robot.execute('REPORT')
        assert result == '0,1,NORTH,1'

    def test_example_a(self):
        self.robot.execute('PLACE 0,0,NORTH')
        self.robot.execute('MOVE')
        result = self.robot.execute('REPORT')
        assert result == '0,1,NORTH,1'

    def test_example_b(self):
        self.robot.execute('PLACE 0,0,NORTH')
        self.robot.execute('LEFT')
        result = self.robot.execute('REPORT')
        assert result == '0,0,WEST,0'

    def test_example_c(self):
        self.robot.execute('PLACE 1,2,EAST')
        self.robot.execute('MOVE')
        self.robot.execute('MOVE')
        self.robot.execute('LEFT')
        self.robot.execute('MOVE')
        result = self.robot.execute('REPORT')
        assert result == '3,3,NORTH,3'

    def test_commands_before_placement_ignored(self):
        self.robot.execute('MOVE')
        self.robot.execute('LEFT')
        self.robot.execute('RIGHT')
        assert self.robot.is_placed() == False

    def test_backward(self):
        self.robot.execute('PLACE 0,0,NORTH')
        self.robot.execute('BACKWARD')
        result = self.robot.execute('REPORT')
        assert result == '0,0,NORTH,0'

    def test_backward_without_placement(self):
        assert self.robot.execute('BACKWARD').get("success") == False

    def test_backward_invalid_direction(self):
        self.robot.execute('PLACE 1,3,NORTH')
        self.robot.execute('BACKWARD')
        result = self.robot.execute('REPORT')
        assert result == '1,2,NORTH,1'

    def test_undo(self):
        self.robot.execute('PLACE 0,0,NORTH')
        self.robot.execute('MOVE')
        self.robot.execute('UNDO')
        result = self.robot.execute('REPORT')
        assert result == '0,0,NORTH,0'

    def test_undo_without_placement(self):
        assert self.robot.undo().get("success") == False

    def test_undo_multiple_times(self):
        self.robot.execute('PLACE 0,0,NORTH')
        self.robot.execute('MOVE')
        self.robot.execute('MOVE')
        self.robot.execute('UNDO')
        self.robot.execute('UNDO')
        result = self.robot.execute('REPORT')
        assert result == '0,0,NORTH,0'

    def test_undo_past_history_limit(self):
        self.robot.execute('PLACE 0,0,NORTH')
        self.robot.execute('MOVE')
        self.robot.execute('UNDO')
        second_undo = self.robot.execute('UNDO')
        assert second_undo.get("success") == False
        result = self.robot.execute('REPORT')
        assert result == '0,0,NORTH,0'

    def test_undo_after_failed_move(self):
        self.robot.execute('PLACE 0,0,SOUTH')
        self.robot.execute('MOVE')  # fails — at boundary
        second_undo = self.robot.execute('UNDO')
        assert second_undo.get("success") == False
        result = self.robot.execute('REPORT')
        assert result == '0,0,SOUTH,0'

    def test_report_includes_move_count(self):
        self.robot.execute('PLACE 0,0,NORTH')
        result = self.robot.execute('REPORT')
        assert result == '0,0,NORTH,0'

    def test_move_increments_count(self):
        self.robot.execute('PLACE 0,0,NORTH')
        self.robot.execute('MOVE')
        self.robot.execute('MOVE')
        result = self.robot.execute('REPORT')
        assert result == '0,2,NORTH,2'

    def test_backward_increments_count(self):
        self.robot.execute('PLACE 0,2,NORTH')
        self.robot.execute('BACKWARD')
        result = self.robot.execute('REPORT')
        assert result == '0,1,NORTH,1'

    def test_rotation_does_not_increment_count(self):
        self.robot.execute('PLACE 0,0,NORTH')
        self.robot.execute('LEFT')
        self.robot.execute('RIGHT')
        result = self.robot.execute('REPORT')
        assert result == '0,0,NORTH,0'

    def test_undo_move_decrements_count(self):
        self.robot.execute('PLACE 0,0,NORTH')
        self.robot.execute('MOVE')
        self.robot.execute('UNDO')
        result = self.robot.execute('REPORT')
        assert result == '0,0,NORTH,0'

    def test_undo_rotation_does_not_decrement_count(self):
        self.robot.execute('PLACE 0,0,NORTH')
        self.robot.execute('MOVE')
        self.robot.execute('LEFT')
        self.robot.execute('UNDO')  # undoes LEFT, count should stay 1
        result = self.robot.execute('REPORT')
        assert result == '0,1,NORTH,1'

    def test_failed_move_does_not_increment_count(self):
        self.robot.execute('PLACE 0,0,SOUTH')
        self.robot.execute('MOVE')  # fails — at boundary
        result = self.robot.execute('REPORT')
        assert result == '0,0,SOUTH,0'

    def test_move_blocked_by_obstacle(self):
        obstacles = [(0, 1)]
        table = Table(5, 5, obstacles)
        robot = Robot(table)
        robot.execute('PLACE 0,0,NORTH')
        result = robot.move()  # blocked by obstacle at (0,1)
        assert result["success"] == False
        assert result["reason"] == "obstacle"
        report_result = robot.execute('REPORT')
        assert report_result == '0,0,NORTH,0'

    def test_backward_blocked_by_obstacle(self):
        obstacles = [(1, 2)]
        table = Table(5, 5, obstacles)
        robot = Robot(table)
        robot.execute('PLACE 1,3,NORTH')
        result = robot.backward()  # blocked by obstacle at (1,2)
        assert result["success"] == False
        assert result["reason"] == "obstacle"
        report_result = robot.execute('REPORT')
        assert report_result == '1,3,NORTH,0'


class TestMultiRobot:
    """Test multi-robot scenarios (design decision 5.1: backward compatible)."""

    def test_two_robots_on_same_table(self):
        table = Table(5, 5)
        robot_a = Robot(table)
        robot_b = Robot(table)

        # Place both robots
        assert robot_a.place(0, 0, 'NORTH').get("success") == True
        assert robot_b.place(2, 2, 'EAST').get("success") == True

        # Verify both are placed
        assert robot_a.is_placed() == True
        assert robot_b.is_placed() == True
        assert robot_a.report() == '0,0,NORTH,0'
        assert robot_b.report() == '2,2,EAST,0'

    def test_collision_detection(self):
        table = Table(5, 5)
        robot_a = Robot(table)
        robot_b = Robot(table)

        # Place robots
        robot_a.place(0, 0, 'EAST')
        robot_b.place(1, 0, 'WEST')

        # Try to move A into B
        result = robot_a.move()
        assert result["success"] == False
        assert result["reason"] == "collision"
        assert result["collision_with"] == str(robot_b.robot_id)

    def test_robots_move_independently(self):
        table = Table(5, 5)
        robot_a = Robot(table)
        robot_b = Robot(table)

        # Place robots at different positions
        robot_a.place(0, 0, 'NORTH')
        robot_b.place(2, 2, 'EAST')

        # Move A
        result_a = robot_a.move()
        assert result_a["success"] == True
        assert robot_a.report() == '0,1,NORTH,1'

        # Move B independently
        result_b = robot_b.move()
        assert result_b["success"] == True
        assert robot_b.report() == '3,2,EAST,1'

    def test_three_robots_collision_chain(self):
        table = Table(5, 5)
        robot_a = Robot(table)
        robot_b = Robot(table)
        robot_c = Robot(table)

        # Place in a line: A at (0,0), B at (1,0), C at (2,0)
        robot_a.place(0, 0, 'EAST')
        robot_b.place(1, 0, 'EAST')
        robot_c.place(2, 0, 'EAST')

        # A tries to move into B
        result_a = robot_a.move()
        assert result_a["success"] == False
        assert result_a["reason"] == "collision"

        # B tries to move into C
        result_b = robot_b.move()
        assert result_b["success"] == False
        assert result_b["reason"] == "collision"

        # C can move freely
        result_c = robot_c.move()
        assert result_c["success"] == True
        assert robot_c.report() == '3,0,EAST,1'

    def test_per_robot_undo(self):
        table = Table(5, 5)
        robot_a = Robot(table)
        robot_b = Robot(table)

        # Place both
        robot_a.place(0, 0, 'NORTH')
        robot_b.place(2, 2, 'EAST')

        # Move both
        robot_a.move()
        robot_b.move()

        # Undo only A
        robot_a.undo()
        assert robot_a.report() == '0,0,NORTH,0'
        assert robot_b.report() == '3,2,EAST,1'  # B unchanged

    def test_backward_compatible_single_robot(self):
        """Verify single-robot still works (design decision 5.1)."""
        table = Table(5, 5)
        robot = Robot(table)

        # Original single-robot code should work
        robot.execute('PLACE 0,0,NORTH')
        robot.execute('MOVE')
        robot.execute('MOVE')
        result = robot.execute('REPORT')
        assert result == '0,2,NORTH,2'

    def test_multiple_robots_coexist(self):
        table = Table(5, 5)
        robot1 = Robot(table, 'Robot 1')
        robot2 = Robot(table, 'Robot 2')
        robot1.execute('PLACE 0,0,NORTH')
        robot2.execute('PLACE 1,1,EAST')
        result1 = robot1.execute('REPORT')
        result2 = robot2.execute('REPORT')
        assert result1 == '0,0,NORTH,0'
        assert result2 == '1,1,EAST,0'

    def test_multiple_robots_placement_collision(self):
        table = Table(5, 5)
        robot1 = Robot(table, 'Robot 1')
        robot2 = Robot(table, 'Robot 2')
        robot1.execute('PLACE 0,0,NORTH')
        robot2.execute('PLACE 0,0,EAST')
        result1 = robot1.execute('REPORT')
        result2 = robot2.execute('REPORT')
        assert result1 == '0,0,NORTH,0'
        assert result2 == None
    
    def test_multiple_robots_collision(self):
        table = Table(5, 5)
        robot1 = Robot(table, 'Robot 1')
        robot2 = Robot(table, 'Robot 2')
        robot1.execute('PLACE 0,0,NORTH')
        robot2.execute('PLACE 1,0,WEST')
        robot2.execute('MOVE')
        result1 = robot1.execute('REPORT')
        result2 = robot2.execute('REPORT')
        assert result1 == '0,0,NORTH,0'
        assert result2 == '1,0,WEST,0'

    def test_table_tracking_robot_position(self):
        table = Table(5, 5)
        robot = Robot(table, 'Robot 1')
        robot.execute('PLACE 0,0,NORTH')
        robot.execute('MOVE')
        result = table.get_robot_position(robot.id)
        assert result == '0,1,NORTH,1'

    def test_jump_blocked_by_another_robot(self):
        # Setup
        table = Table(5, 5)
        robot1 = Robot(table, "Robot A")
        robot2 = Robot(table, "Robot B")

        # Initial state
        robot1.execute("PLACE 0,0,NORTH")  # Robot A at (0,0), facing NORTH
        robot2.execute("PLACE 0,3,NORTH")  # Robot B at (0,3), facing NORTH

        # Attempt JUMP 5 from (0,0) going NORTH
        # Path: (0,1) → (0,2) → (0,3)[BLOCKED by robot2] → STOP
        result = robot1.execute("JUMP 5")
        assert result.get("success") == False
        assert result.get("position") == (0, 2, 'NORTH', 2)

        # Now test UNDO
        robot1.execute("UNDO")
        result = robot1.report()
        assert result == '0,0,NORTH,0'

    def test_robot_pushing(self):
        table = Table(5, 5)
        robot1 = Robot(table, "Robot A")
        robot2 = Robot(table, "Robot B")
        robot1.execute("PLACE 0,0,NORTH")
        robot2.execute("PLACE 0,1,NORTH")
        robot1.execute("PUSH 1")
        result = robot1.execute("REPORT")
        assert result == '0,1,NORTH,1'
        result = robot2.execute("REPORT")
        assert result == '0,2,NORTH,1'

    def test_robot_pushing_blocked_by_obstacle(self):
        """Push fails when the target robot is blocked by an obstacle."""
        obstacles = [(0, 2)]
        table = Table(5, 5, obstacles)
        robot1 = Robot(table, "Robot A")
        robot2 = Robot(table, "Robot B")
        robot1.execute("PLACE 0,0,NORTH")
        robot2.execute("PLACE 0,1,NORTH")
        # Robot A tries to push Robot B, but B is blocked by obstacle at (0,2)
        result = robot1.execute("PUSH 1")
        assert result.get("success") == False
        # Both robots should stay in place
        result = robot1.execute("REPORT")
        assert result == '0,0,NORTH,0'
        result = robot2.execute("REPORT")
        assert result == '0,1,NORTH,0'

    # def test_robot_pushing_and_undo(self):
    #     """UNDO after PUSH should restore both robots to their original positions."""
    #     table = Table(5, 5)
    #     robot1 = Robot(table, "Robot A")
    #     robot2 = Robot(table, "Robot B")
    #     robot1.execute("PLACE 0,0,NORTH")
    #     robot2.execute("PLACE 0,1,NORTH")
    #     # Push
    #     robot1.execute("PUSH 1")
    #     assert robot1.execute("REPORT") == '0,1,NORTH,1'
    #     assert robot2.execute("REPORT") == '0,2,NORTH,1'
    #     # Undo robot1's push
    #     robot1.execute("UNDO")
    #     assert robot1.execute("REPORT") == '0,0,NORTH,0'
    #     # Robot2 should also be restored
    #     assert robot2.execute("REPORT") == '0,1,NORTH,0'

    def test_undo_collision(self):
        table = Table(5, 5)
        robot1 = Robot(table, "Robot A")
        robot2 = Robot(table, "Robot B")
        robot1.execute("PLACE 0,0,NORTH")
        robot2.execute("PLACE 0,1,NORTH")
        robot2.execute("MOVE")
        robot1.execute("MOVE")
        robot2.execute("UNDO")
        assert robot2.execute("REPORT") == '0,2,NORTH,1'

