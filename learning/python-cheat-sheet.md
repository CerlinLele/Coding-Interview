# Python Cheat Sheet - REA Pair Programming 面试

针对 toy robot 类 OOP 练习的快速参考

---

## 类和对象

```python
class Robot:
    # 类变量（所有实例共享）
    DIRECTIONS = ['NORTH', 'EAST', 'SOUTH', 'WEST']
    
    def __init__(self, table):
        # 实例变量（每个实例独有）
        self.table = table
        self.x = None
        self.y = None
        self.facing = None
    
    def method_name(self, param):
        """方法定义"""
        return self.x + param
    
    def is_valid(self):
        """判断类方法（返回布尔值）"""
        return self.x is not None

# 使用
robot = Robot(table)
robot.method_name(5)
```

---

## 集合（Set）（常用于去重、集合运算）

```python
# 定义
positions = {(0, 0), (1, 2), (3, 3)}  # 元组作为元素（元组是不可变的）
directions = {'NORTH', 'EAST', 'SOUTH', 'WEST'}

# 添加元素
positions.add((2, 1))

# 删除元素
positions.discard((0, 0))  # 不存在也不报错
# positions.remove((0, 0))  # 不存在会报 KeyError

# 检查是否存在
if (1, 2) in positions:
    print("存在")

# 集合运算
set_a = {1, 2, 3}
set_b = {2, 3, 4}
union = set_a | set_b        # {1, 2, 3, 4}
intersection = set_a & set_b # {2, 3}
difference = set_a - set_b   # {1}

# 长度和迭代
len(positions)
for pos in positions:
    print(pos)

# 转换为列表
pos_list = list(positions)
```

**面试中的应用**：
- 记录已访问过的位置：`visited = set()`，然后 `visited.add((x, y))`
- 快速去重：`unique_states = set([(x, y, facing, count) for ... ])`
- 避免重复：`if state not in visited: visited.add(state)`

**Toy Robot 中的实际用途**（四元组作为状态）：
```python
# 记录所有访问过的状态（完整状态包括位置、朝向和移动次数）
visited_states = set()

# 执行命令后，记录当前状态
def record_state(self, visited):
    state = (self.x, self.y, self.facing, self.move_count)  # 四元组
    visited.add(state)

# 检查是否到达过这个状态
if (current_x, current_y, current_facing, current_count) not in visited_states:
    visited_states.add((current_x, current_y, current_facing, current_count))

# 快速判断是否重复
self.robot.execute('PLACE 0,0,NORTH')
self.robot.execute('MOVE')
state1 = (self.robot.x, self.robot.y, self.robot.facing, self.robot.move_count)  # (0, 1, 'NORTH', 1)
visited = {state1}

self.robot.execute('UNDO')
state2 = (self.robot.x, self.robot.y, self.robot.facing, self.robot.move_count)  # (0, 0, 'NORTH', 0)
if state2 not in visited:
    visited.add(state2)
```

**为什么用 Set 而不是 List**：
- List 检查元素存在：`O(n)` 时间
- Set 检查元素存在：`O(1)` 时间
- 如果要记录 100+ 个状态，Set 性能远优于 List

---

## 字典（常用于方向映射）

```python
# 定义
deltas = {
    'NORTH': (0, 1),
    'EAST': (1, 0),
    'SOUTH': (0, -1),
    'WEST': (-1, 0)
}

# 访问
dx, dy = deltas['NORTH']  # (0, 1)

# 访问不存在的键会抛出 KeyError
# deltas['SOUTH_EAST']  # KeyError: 'SOUTH_EAST'

# 用 .get() 避免错误（返回 None 或默认值）
delta = deltas.get('NORTH')         # (0, 1)
delta = deltas.get('UNKNOWN')       # None
delta = deltas.get('UNKNOWN', (0, 0))  # (0, 0)

# 检查键是否存在
if 'NORTH' in deltas:
    print("存在")

# 获取所有键/值
deltas.keys()
deltas.values()
deltas.items()  # [('NORTH', (0, 1)), ...]
```

---

## 列表（常用于历史记录、状态栈）

```python
# 定义
history = []
directions = ['NORTH', 'EAST', 'SOUTH', 'WEST']

# 添加元素
history.append((x, y, facing))

# 删除并返回最后一个元素
last = history.pop()

# 访问
first = directions[0]      # 'NORTH'
last = directions[-1]      # 'WEST'

# 切片
subset = directions[1:3]   # ['EAST', 'SOUTH']

# 长度
len(directions)            # 4

# 索引查找
idx = directions.index('EAST')  # 1

# 检查是否存在
if 'NORTH' in directions:
    pass
```

---

## 字符串操作

```python
# 分割
"PLACE 0,0,NORTH".split()           # ['PLACE', '0,0,NORTH']
"0,0,NORTH".split(',')              # ['0', '0', 'NORTH']

# 大小写
"place".upper()                     # 'PLACE'
"NORTH".lower()                     # 'north'

# 去除空格
"  hello  ".strip()                 # 'hello'

# 检查开头
"PLACE 0,0,NORTH".startswith('PLACE')  # True

# 格式化
f"{x},{y},{facing}"                 # "0,1,NORTH"
"{},{},{}".format(x, y, facing)     # 同上
```

---

## 条件语句

```python
# 基本 if-else
if x < 0:
    return False
elif x == 0:
    return True
else:
    return False

# 简写（三元表达式）
result = 'valid' if x >= 0 else 'invalid'

# 检查 None
if self.x is None:
    return False

if self.x is not None:
    pass

# 多条件
if x >= 0 and x < 5:
    pass

if facing in ['NORTH', 'SOUTH']:
    pass
```

---

## 循环

```python
# for 循环（字典）
for key, value in deltas.items():
    print(key, value)

# for 循环（列表）
for direction in directions:
    print(direction)

# for 循环（带索引）
for i, direction in enumerate(directions):
    print(i, direction)  # 0 NORTH, 1 EAST, ...

# range
for i in range(4):      # 0, 1, 2, 3
    pass

# while 循环
while True:
    command = input("> ")
    if command == 'EXIT':
        break
```

---

## 函数

```python
# 基本函数
def calculate(x, y):
    return x + y

# 默认参数
def move(steps=1):
    return self.x + steps

# 无返回值（返回 None）
def print_status():
    print(f"{self.x},{self.y}")

# 多返回值
def get_position():
    return self.x, self.y

x, y = get_position()
```

---

## 异常处理

```python
# 基本 try-except
try:
    x = int("abc")
except ValueError:
    print("转换失败")

# 捕获多种异常
try:
    result = 10 / 0
except (ValueError, ZeroDivisionError):
    pass

# 通用异常（不推荐）
except Exception as e:
    print(f"错误: {e}")
```

---

## 测试（pytest）

```python
import pytest
from robot import Robot

class TestRobot:
    def setup_method(self):
        """每个测试前执行"""
        self.robot = Robot()
    
    def test_place_valid_position(self):
        """测试方法名要以 test_ 开头"""
        assert self.robot.place(0, 0, 'NORTH') == True
        assert self.robot.x == 0
        assert self.robot.y == 0
    
    def test_move_north(self):
        self.robot.place(0, 0, 'NORTH')
        self.robot.move()
        assert self.robot.y == 1

# 运行测试
# pytest                    # 运行所有测试
# pytest -v                # 详细输出
# pytest test_robot.py     # 运行特定文件
```

---

## 常用模式

### 取模运算（用于循环方向）

```python
DIRECTIONS = ['NORTH', 'EAST', 'SOUTH', 'WEST']

# 左转（逆时针）
current_index = DIRECTIONS.index('NORTH')  # 0
new_index = (current_index - 1) % 4        # 3
new_facing = DIRECTIONS[new_index]         # 'WEST'

# 右转（顺时针）
new_index = (current_index + 1) % 4        # 1
new_facing = DIRECTIONS[new_index]         # 'EAST'
```

### 元组解包

```python
# 定义
position = (2, 3)
delta = (0, 1)

# 解包
x, y = position
dx, dy = delta

# 计算新位置
new_x = x + dx
new_y = y + dy
```

### 提前返回（避免深层嵌套）

```python
# 不好
def move(self):
    if self.is_placed():
        if self.table.is_valid(new_x, new_y):
            self.x = new_x
            return True
        else:
            return False
    else:
        return False

# 好
def move(self):
    if not self.is_placed():
        return False
    
    if not self.table.is_valid(new_x, new_y):
        return False
    
    self.x = new_x
    return True
```

---

## 调试技巧

```python
# 打印调试
print(f"x={x}, y={y}, facing={facing}")

# 类型检查
print(type(x))           # <class 'int'>
print(isinstance(x, int))  # True

# 查看对象属性
print(vars(robot))       # {'x': 0, 'y': 1, 'facing': 'NORTH'}
```

---

## 面试时常用口头表达

- "我先定义一个方法来处理这个"
- "这里用字典映射方向比较清晰"
- "我加个边界检查，确保不会越界"
- "先实现最简单的版本，然后再重构"
- "我用 assert 快速验证一下逻辑"