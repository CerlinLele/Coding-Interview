import pytest
from robot import Robot
from table import Table


class TestTable:
    def test_valid_position(self):
        table = Table(5, 5)
        assert table.is_valid_position(0, 0) == True
        assert table.is_valid_position(4, 4) == True
        assert table.is_valid_position(2, 3) == True
    
    def test_invalid_position(self):
        obstacles = [(1, 3), (2, 3), (3, 3)]
        table = Table(5, 5, obstacles)
        assert table.is_valid_position(-1, 0) == False
        assert table.is_valid_position(0, -1) == False
        assert table.is_valid_position(5, 0) == False
        assert table.is_valid_position(0, 5) == False
        assert table.is_valid_position(1, 3) == False
        assert table.is_valid_position(2, 3) == False
        assert table.is_valid_position(3, 3) == False   


class TestRobot:
    def setup_method(self):
        self.table = Table(5, 5)
        self.robot = Robot(self.table)
    
    def test_robot_not_placed_initially(self):
        assert self.robot.is_placed() == False
    
    def test_place_robot_valid_position(self):
        assert self.robot.place(0, 0, 'NORTH') == True
        assert self.robot.is_placed() == True
        assert self.robot.x == 0
        assert self.robot.y == 0
        assert self.robot.facing == 'NORTH'
    
    def test_place_robot_invalid_position(self):
        assert self.robot.place(-1, 0, 'NORTH') == False
        assert self.robot.place(5, 5, 'NORTH') == False
        assert self.robot.is_placed() == False
    
    def test_place_robot_invalid_direction(self):
        assert self.robot.place(0, 0, 'INVALID') == False
        assert self.robot.is_placed() == False
    
    def test_move_north(self):
        self.robot.place(0, 0, 'NORTH')
        self.robot.move()
        assert self.robot.x == 0
        assert self.robot.y == 1
    
    def test_move_east(self):
        self.robot.place(0, 0, 'EAST')
        self.robot.move()
        assert self.robot.x == 1
        assert self.robot.y == 0
    
    def test_move_prevents_falling(self):
        self.robot.place(0, 0, 'SOUTH')
        self.robot.move()
        assert self.robot.x == 0
        assert self.robot.y == 0
    
    def test_move_without_placement(self):
        assert self.robot.move() == False
    
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
        assert self.robot.backward() == False

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
        assert self.robot.undo() == False

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
        assert second_undo == False
        result = self.robot.execute('REPORT')
        assert result == '0,0,NORTH,0'

    def test_undo_after_failed_move(self):
        self.robot.execute('PLACE 0,0,SOUTH')
        self.robot.execute('MOVE')  # fails — at boundary
        second_undo = self.robot.execute('UNDO')
        assert second_undo == False
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
    