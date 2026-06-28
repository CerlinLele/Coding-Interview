from robot import Robot
from table import Table


def main():
    """Simple interactive demo of the toy robot."""
    
    table = Table(5, 5)
    robot = Robot(table)
    
    print("Toy Robot Simulator")
    print("Commands: PLACE X,Y,FACING | MOVE | BACKWARD | JUMP | PUSH | LEFT | RIGHT | REPORT | UNDO | EXIT")
    print()
    
    while True:
        command = input("> ").strip()
        
        if command.upper() == 'EXIT':
            break
        
        result = robot.execute(command)
        if result:
            print(result)


if __name__ == '__main__':
    main()