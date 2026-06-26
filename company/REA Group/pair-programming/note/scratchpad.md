# **multiple robots**

## Storage

- Multiple robots can coexist on the table

I will choose 2d array to store the positions of multiple robots.

One trade off may be large sparse tables, in that case, set maybe more suitable.

## collision detection/handling

- They can't occupy the same cell
- They need collision detection/handling

Every time the robots move, they will check whether there is an obstacle or another robot.

robots[x][y] is occupied or not

## Robot

- Consider how robots are created, managed, and identified

### ID

each table needs an id  
uuid: identical, we don’t need to keep an incremental number or something  
name: human-readable

### init

Open-close & DI

```jsx
robot1 = Robot(table, 'Robot 1')
robot2 = Robot(table, 'Robot 2')
```

### manage

```jsx
robot1.execute('PLACE 0,0,NORTH')
robot2.execute('PLACE 1,1,EAST')
```

When the robot is placed or the position is changed:  
the table need to update the robots grid

1. empty the current position
2. occupy the next position

