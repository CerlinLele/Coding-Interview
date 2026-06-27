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

**常见错误：Dict 没有 .set() 方法**

```python
# ❌ 错误：Python dict 没有 .set() 方法（那是Java/JavaScript的）
result = {}
result.set("position", (0, 1))  # AttributeError: 'dict' object has no attribute 'set'

# ✅ 正确：使用 dict[key] = value 赋值
result = {}
result["position"] = (0, 1)
result["success"] = True
result["message"] = "Operation successful"

# ✅ 或使用 .update() 方法
result.update({"position": (0, 1), "success": True})

# ✅ 或使用 .setdefault()（仅当键不存在时设置）
result.setdefault("position", (0, 1))
```

**为什么？**

- Python dict 只有 `[]` 赋值语法，没有 `.set()` 方法
- `.set()` 是 Java 和 JavaScript 的 Map/Object 方法
- Python 中 `.set` 指的是 set 数据类型（集合），不是方法

**重要：Dict 键的限制**

```python
# ✅ 可以用作 dict key（不可变）
dict_key_int = {1: 'one', 2: 'two'}
dict_key_tuple = {(0, 0): 'origin', (1, 2): 'position'}
dict_key_str = {'NORTH': (0, 1), 'EAST': (1, 0)}

# ❌ 不能用作 dict key（可变）
# set 是可变的，不能作为 key
# invalid_dict = {{1, 2}: 'value'}  # TypeError: unhashable type: 'set'

# ❌ list 也是可变的
# invalid_dict = {[1, 2]: 'value'}  # TypeError: unhashable type: 'list'

# ✅ 如果要用集合作为键，用 frozenset（不可变集合）
valid_dict = {frozenset([1, 2]): 'value'}  # 可以！
print(valid_dict[frozenset([1, 2])])  # 'value'
```

**为什么？**

- Dict 键需要是 **hashable**（可哈希）的
- Set 和 List 是 **可变的**（mutable），不能被哈希
- Tuple、frozenset、int、str 是 **不可变的**（immutable），可被哈希
- 如果键的值改变，dict 就无法找到这个键

---

## 队列（Queue）和 栈（Stack）

### Stack（栈）- LIFO（后进先出）

```python
# 使用 List 实现 stack
stack = []

# 入栈（push）
stack.append(1)
stack.append(2)
stack.append(3)

# 出栈（pop）- 返回最后一个元素
top = stack.pop()  # 3
print(stack)  # [1, 2]

# 查看栈顶（不弹出）
if stack:
    top = stack[-1]  # 2

# 检查是否为空
if not stack:
    print("Stack is empty")
```

**Toy Robot 应用：UNDO 历史记录**
```python
class Robot:
    def __init__(self):
        self.history = []  # Stack
    
    def execute_command(self, command):
        # 执行命令...
        self.history.append((self.x, self.y, self.facing))  # 记录状态
    
    def undo(self):
        """撤销最后一条命令"""
        if self.history:
            self.x, self.y, self.facing = self.history.pop()
        else:
            print("No history to undo")
```

### Queue（队列）- FIFO（先进先出）

```python
from collections import deque

# 使用 deque 实现 queue（比 list 更高效）
queue = deque()

# 入队（enqueue）- 从右端添加
queue.append(1)
queue.append(2)
queue.append(3)

# 出队（dequeue）- 从左端移除
first = queue.popleft()  # 1
print(queue)  # deque([2, 3])

# 查看队首（不弹出）
if queue:
    front = queue[0]  # 2

# 检查是否为空
if not queue:
    print("Queue is empty")
```

**Deque 双端操作 - 左右都可以增删**

```python
from collections import deque

d = deque([2, 3, 4])

# ========== 右端操作 ==========
d.append(5)           # 从右端添加 → [2, 3, 4, 5]
d.pop()               # 从右端移除 → [2, 3, 4]

# ========== 左端操作 ==========
d.appendleft(1)       # 从左端添加 → [1, 2, 3, 4]
d.popleft()           # 从左端移除 → [2, 3, 4]

# ========== 快速查看两端 ==========
d = deque([1, 2, 3])
print(d[0])           # 2 (左端 / 队首)
print(d[-1])          # 3 (右端 / 队尾)

# ========== 旋转 ==========
d = deque([1, 2, 3, 4, 5])
d.rotate(2)           # 向右旋转 2 位 → [4, 5, 1, 2, 3]
d.rotate(-1)          # 向左旋转 1 位 → [5, 1, 2, 3, 4]
```

**使用场景对比**

```python
from collections import deque

# ========== 标准 Queue（FIFO）==========
# append() 右端进，popleft() 左端出
queue = deque()
queue.append(1)       # 进
queue.append(2)
queue.append(3)
print(queue.popleft())  # 1 出（先进先出）

# ========== 标准 Stack（LIFO）==========
# append() 右端进，pop() 右端出
stack = deque()
stack.append(1)       # 进
stack.append(2)
stack.append(3)
print(stack.pop())     # 3 出（后进先出）

# ========== 双端队列（可从两端进出）==========
deq = deque()
deq.append(2)         # 右端进 → [2]
deq.appendleft(1)     # 左端进 → [1, 2]
deq.append(3)         # 右端进 → [1, 2, 3]
print(deq.popleft())  # 1 左端出
print(deq.pop())      # 3 右端出
```

**Deque 完整 API**

| 方法 | 说明 | 时间复杂度 |
|------|------|---------|
| `append(x)` | 右端添加 | O(1) |
| `pop()` | 右端移除 | O(1) |
| `appendleft(x)` | 左端添加 | O(1) |
| `popleft()` | 左端移除 | O(1) |
| `rotate(n)` | 旋转 n 位 | O(k) |
| `extend(iterable)` | 右端批量添加 | O(k) |
| `extendleft(iterable)` | 左端批量添加 | O(k) |
| `clear()` | 清空 | O(1) |
| `copy()` | 浅拷贝 | O(n) |


**为什么用 deque 而不是 list？**

```python
import time

# List 的 pop(0) 很慢 - O(n)
my_list = list(range(100000))
start = time.time()
for _ in range(1000):
    my_list.pop(0)
print(f"List time: {time.time() - start:.4f}s")  # 比较慢

# deque 的 popleft() 很快 - O(1)
my_deque = deque(range(100000))
start = time.time()
for _ in range(1000):
    my_deque.popleft()
print(f"Deque time: {time.time() - start:.4f}s")  # 快很多
```

**Queue 应用示例：命令队列**
```python
from collections import deque

class CommandProcessor:
    def __init__(self):
        self.command_queue = deque()
    
    def enqueue_command(self, command):
        """添加命令到队列"""
        self.command_queue.append(command)
    
    def process_commands(self):
        """按顺序处理命令"""
        while self.command_queue:
            command = self.command_queue.popleft()
            self.execute(command)
    
    def execute(self, command):
        print(f"Executing: {command}")
```

**Stack vs Queue 对比**

| 特性 | Stack | Queue |
|------|-------|-------|
| 顺序 | LIFO (后进先出) | FIFO (先进先出) |
| 入操作 | append() | append() |
| 出操作 | pop() | popleft() (用deque) |
| 用途 | UNDO、函数调用栈、表达式解析 | 任务队列、广度优先搜索 |
| Python 实现 | list | collections.deque |

---


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
from table import Table

class TestRobot:
    def setup_method(self):
        """每个测试前执行"""
        self.table = Table(5, 5)
        self.robot = Robot(self.table)
    
    def test_place_valid_position(self):
        """测试方法名要以 test_ 开头"""
        assert self.robot.place(0, 0, 'NORTH').get("success") == True
        assert self.robot.x == 0
        assert self.robot.y == 0
    
    def test_move_north(self):
        self.robot.place(0, 0, 'NORTH')
        self.robot.move()
        assert self.robot.y == 1
    
    def test_move_prevents_falling(self):
        """测试边界检查 - 返回字典包含 success 和 reason"""
        self.robot.place(0, 0, 'SOUTH')
        result = self.robot.move()  # 尝试向南走，但边界在 y=-1
        
        # 检查返回值结构
        assert result["success"] == False
        assert result["reason"] == "boundary"
        
        # 检查机器人没有移动
        assert self.robot.x == 0
        assert self.robot.y == 0

# 运行测试
# pytest                    # 运行所有测试
# pytest -v                # 详细输出
# pytest test_robot.py     # 运行特定文件
# pytest test_robot.py::TestRobot::test_move_prevents_falling  # 运行单个测试
```

### pytest 显示 print() 输出

pytest 默认捕获 print() 输出。要显示它们，使用以下选项：

```python
def test_debug_movement(self):
    """在测试中使用 print 调试"""
    self.robot.place(0, 0, 'NORTH')
    result = self.robot.move()
    
    print(f"Robot position: ({self.robot.x}, {self.robot.y})")
    print(f"Move result: {result}")
    
    assert self.robot.y == 1
```

**运行命令：**

```bash
# -s: 显示 print() 输出（最常用）
pytest -s test_robot.py

# -v: 详细模式 + -s: 显示 print
pytest -vs test_robot.py

# 运行单个测试并显示输出
pytest -s test_robot.py::TestRobot::test_debug_movement

# --capture=no 的效果同 -s
pytest --capture=no test_robot.py
```

**持久配置（创建 pytest.ini）：**

在项目根目录创建 `pytest.ini`：
```ini
[pytest]
addopts = -s -v
```

然后直接运行 `pytest test_robot.py` 就会自动使用这些选项。

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