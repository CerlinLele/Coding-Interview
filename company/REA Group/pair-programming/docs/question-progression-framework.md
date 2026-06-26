# Toy Robot 出题模式与考察层次

基于 REA pair programming 面试的典型递进模式

---

## 考察层次

### Level 1：基础命令扩展（10-15 分钟）

**典型题目**：
- 添加 `BACKWARD` 命令（向后移动一步）
- 添加 `JUMP X,Y` 命令（直接跳到指定位置，保持朝向）

**考察点**：
- 能否快速理解现有的 `MOVE` 实现
- 能否复用现有的边界检查逻辑
- 命名和代码风格是否与现有代码一致

**应对策略**：
- 先读 `move()` 方法，理解 `DIRECTION_DELTAS` 的作用
- 口头说："BACKWARD 就是朝反方向移动，我可以复用现有逻辑，只是把 delta 取反"
- 快速实现，立即在 main 或测试里验证

**示例实现思路**：

```python
def backward(self):
    """向后移动一步"""
    if not self.is_placed():
        return False
    
    # 获取反方向的 delta
    dx, dy = self.DIRECTION_DELTAS[self.facing]
    new_x = self.x - dx  # 反向
    new_y = self.y - dy
    
    if self.table.is_valid_position(new_x, new_y):
        self.x = new_x
        self.y = new_y
        return True
    
    return False
```

**重构优化（如果面试官追问或有时间）**：

面试官可能会说："你会发现 `move()` 和 `backward()` 代码很相似，能不能优化一下？"

第一步观察：两个方法唯一的区别是方向。

```python
# move()：dx, dy = self.DIRECTION_DELTAS[self.facing]；new_x = self.x + dx
# backward()：dx, dy = self.DIRECTION_DELTAS[self.facing]；new_x = self.x - dx
```

第二步设计：引入 `direction` 参数，在方向差值层面处理。

```python
def move(self, direction="forward"):
    """Move the robot one unit in the specified direction."""
    if not self.is_placed():
        return False
    
    dx, dy = self.DIRECTION_DELTAS[self.facing]
    if direction == "backward":
        dx, dy = -dx, -dy  # 取反方向
    
    new_x = self.x + dx
    new_y = self.y + dy
    
    if self.table.is_valid_position(new_x, new_y):
        self.history.append((self.x, self.y, self.facing))
        self.x = new_x
        self.y = new_y
        self.move_count += 1
        return True
    
    return False
```

第三步更新命令处理：

```python
elif command == 'MOVE':
    self.move(direction="forward")

elif command == 'BACKWARD':
    self.move(direction="backward")
```

**重构要点**：
- ✓ **消除重复**：31 行代码合并，职责单一
- ✓ **易于维护**：修改一处即同步两个方向（边界检查、历史记录、网格更新）
- ✓ **逻辑清晰**：参数明确表达意图（正向 vs 反向）
- ⚠️ **权衡**：参数多了一个，需要文档说明默认值；但好处是避免了方法重复

**面试官的反应**：
- 好的反馈："很不错，这就是 DRY（Don't Repeat Yourself）原则"
- 可能追问："如果以后要加 DIAGONAL（斜向）呢？现在的参数设计还能扩展吗？"
  - 回答思路："目前参数是字符串，如果需要更多方向，可以考虑用枚举（Enum）或四元组坐标，但现在需求还不明确，所以字符串够用"

---

### Level 2：状态管理扩展（15-20 分钟）

**典型题目**：
- 实现命令历史记录
- 添加 `UNDO` 功能（撤销上一步移动或转向）

**考察点**：
- 如何设计状态快照
- 哪些命令需要记录（MOVE/LEFT/RIGHT 要，REPORT 不要）
- 边界情况处理（连续 UNDO、UNDO 到初始状态）

**应对策略**：
- 说出权衡："我可以记录完整状态快照，也可以只记录命令，前者实现简单但内存占用大，后者需要实现反向操作"
- 先做最简单版本："我先用栈存储 (x, y, facing) 快照，UNDO 时弹出"
- 口头说明局限："目前 UNDO 无法恢复到未放置状态，如果需要可以用 Optional"

**示例实现思路**：

```python
class Robot:
    def __init__(self, table):
        self.table = table
        self.x = None
        self.y = None
        self.facing = None
        self.history = []  # 状态栈
    
    def _save_state(self):
        """保存当前状态"""
        if self.is_placed():
            self.history.append((self.x, self.y, self.facing))
    
    def move(self):
        if not self.is_placed():
            return False
        
        self._save_state()  # 移动前保存
        # ... 原有移动逻辑
    
    def undo(self):
        """撤销上一步操作"""
        if not self.history:
            return False
        
        self.x, self.y, self.facing = self.history.pop()
        return True
```

---

### Level 3：多实体或复杂交互（20-30 分钟）

**典型题目**：
- 支持多个机器人在同一桌面
- 添加障碍物，机器人不能进入障碍物格子
- 两个机器人不能占据同一格子

**考察点**：
- 如何重构架构（Table 需要维护占用状态）
- 对象间的职责划分（碰撞检查放在 Robot 还是 Table）
- API 设计（如何初始化多个机器人）

**应对策略**：
- 先画个简单草图："现在 Table 只管边界，我需要让它管理占用状态"
- 说出设计选择："我可以在 Table 里加个 occupied_cells 集合，Robot move 前先问 Table"
- 增量实现："我先让单个机器人能感知障碍物，验证通过后再加第二个机器人"

**示例实现思路**：

```python
class Table:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.obstacles = set()  # 障碍物位置
        self.robots = {}  # {robot_id: (x, y)}
    
    def is_valid_position(self, x, y, robot_id=None):
        """检查位置是否可用"""
        # 检查边界
        if not (0 <= x < self.width and 0 <= y < self.height):
            return False
        
        # 检查障碍物
        if (x, y) in self.obstacles:
            return False
        
        # 检查其他机器人
        for rid, (rx, ry) in self.robots.items():
            if rid != robot_id and (rx, ry) == (x, y):
                return False
        
        return True
    
    def add_obstacle(self, x, y):
        """添加障碍物"""
        if self.is_valid_position(x, y):
            self.obstacles.add((x, y))

class Robot:
    def __init__(self, table, robot_id):
        self.table = table
        self.robot_id = robot_id
        # ...
    
    def move(self):
        # ...
        if self.table.is_valid_position(new_x, new_y, self.robot_id):
            # 更新 table 的机器人位置记录
            self.table.robots[self.robot_id] = (new_x, new_y)
            self.x = new_x
            self.y = new_y
            return True
```

---

### Level 4：架构重构（如果时间充裕）

**典型题目**：
- 从文件读取一系列命令并执行
- 支持可配置的桌面大小
- 命令解析器插件化（方便以后加新命令）

**考察点**：
- 是否会过度设计
- 能否识别"现在不需要但以后可能需要"的扩展点
- 重构时是否保持测试通过

**应对策略**：
- 明确说："如果只是从文件读命令，我就加个简单的文件读取循环"
- 不要主动提策略模式："现在 5 个命令用 if-else 很清晰，如果以后命令数量到 20+，可以考虑命令注册表"
- 边重构边跑测试："我改完一处就跑一次测试，确保没破坏现有功能"

**示例实现思路（文件读取）**：

```python
def execute_from_file(robot, filepath):
    """从文件读取并执行命令"""
    try:
        with open(filepath, 'r') as f:
            for line in f:
                command = line.strip()
                if command:  # 跳过空行
                    result = robot.execute(command)
                    if result:
                        print(result)
    except FileNotFoundError:
        print(f"文件未找到: {filepath}")
    except Exception as e:
        print(f"执行出错: {e}")
```

---

## 面试官常用的递进方式

### 1. 第一个扩展
简单、明确，看你能否快速上手

**示例**：
- "能不能给机器人加个 BACKWARD 命令？"
- 观察你如何读现有代码、如何复用逻辑

### 2. 追问边界情况
看你考虑问题是否全面

**示例**：
- "如果机器人已经在边缘，BACKWARD 会怎样？"
- "如果用户输入 PLACE -1,0,NORTH 呢？"
- "UNDO 多次会发生什么？"

### 3. 第二个扩展
稍复杂，看你的设计思路

**示例**：
- "现在要加 UNDO 功能，你会怎么设计？"
- 观察你是否说出多种方案和权衡

### 4. 开放讨论
不需要实现，只是讨论架构

**示例**：
- "如果让你设计一个支持 100 个机器人的版本，你会怎么做？"
- "如果要支持机器人之间的消息传递，你会如何扩展？"

---

## 你应该展现的

### 务实优先
- ❌ "我先设计一个抽象工厂，用策略模式解耦命令……"
- ✅ "我先加个 backward() 方法，逻辑和 move() 类似，只是方向相反"

### 增量验证
- ❌ 写完 100 行代码再运行
- ✅ 每完成一个小功能就跑一下："我先试试 BACKWARD 能不能动"

### 主动沟通
- ❌ 沉默敲代码 10 分钟
- ✅ "我现在要复用这个 DIRECTION_DELTAS，把 delta 取反就是后退"

### 接受反馈
- ❌ 面试官："这样会有个问题……" 你："不会的，因为……"
- ✅ 面试官："这样会有个问题……" 你："确实，我没考虑到这点，那我改成……"

---

## 时间分配参考

| 阶段 | 时间 | 活动 |
|-----|------|-----|
| 破冰 | 5 分钟 | 自我介绍、了解面试官 |
| 理解需求 | 10 分钟 | 读代码、跑测试、确认任务 |
| Level 1 扩展 | 10-15 分钟 | 基础命令，快速验证 |
| Level 2 扩展 | 15-20 分钟 | 状态管理，处理边界 |
| Level 3 扩展 | 15-20 分钟 | 架构调整（如果时间够） |
| 收尾总结 | 10 分钟 | 演示、说明局限、提问 |

**总计**：约 60-70 分钟实际编码时间

---

## 常见错误模式

### 1. 过度设计

**错误示范**：
```python
# 为了加一个 BACKWARD 就搞出一堆抽象
class Command(ABC):
    @abstractmethod
    def execute(self): pass

class BackwardCommand(Command):
    def __init__(self, robot):
        self.robot = robot
    
    def execute(self):
        # ... 10 行配置代码
```

**正确做法**：
```python
# 直接在 Robot 类里加方法
def backward(self):
    if not self.is_placed():
        return False
    dx, dy = self.DIRECTION_DELTAS[self.facing]
    new_x, new_y = self.x - dx, self.y - dy
    if self.table.is_valid_position(new_x, new_y):
        self.x, self.y = new_x, new_y
        return True
    return False
```

### 2. 沉默写代码

**错误示范**：
- [沉默 5 分钟]
- [写了一堆代码]
- "好了，我写完了"

**正确做法**：
- "我先看一下 move() 是怎么实现的……"
- "好的，它用了 DIRECTION_DELTAS 这个字典……"
- "那我 BACKWARD 就是把 delta 反过来……"
- "我现在加一个 backward() 方法……"
- "写完了，我跑一下试试……"

### 3. 忽略测试

**错误示范**：
- 写完代码直接说："应该能跑"
- 不验证边界情况

**正确做法**：
- 写完立即跑：`python main.py` 或 `pytest`
- 口头提及边界："现在只测了正常情况，边界的话机器人在 (0,0) 时 BACKWARD 会被阻止"

---

## 记住 REA 的核心价值观

1. **Pragmatism** - 用最简单的方式解决问题
2. **Learning Mindset** - 开放接受反馈和建议
3. **Technical Knowledge** - 基本 OOP 和代码组织能力

这不是算法竞赛，是**模拟真实的团队协作**。

---

## 算法在 Pair Programming 中的出现方式

REA 不会考 LeetCode 式算法题，但算法思维会以以下方式渗透：

### 1. 数据结构选择

面试官可能问："你为什么用 list 做 UNDO 栈？"

**标准回答框架**：
- list 的 `append`/`pop` 都是 O(1)，足够用
- 如果需要双端操作可以换 `collections.deque`，但这里不需要
- 不过度设计：需求是栈，list 就是栈

### 2. 复杂度意识

面试官可能追问："如果历史记录很长怎么办？"

**可能的回答**：
- 当前方案：无限增长，内存 O(n)
- 优化方向：限制历史深度（`MAX_HISTORY = 50`），超出后丢弃最老的记录
- 若用 `deque(maxlen=50)` 可自动淘汰

### 3. 路径/搜索问题（Level 3+ 可能出现）

**典型变体**：
- "找出机器人从当前位置到达目标位置的最短路径"
- 本质是 **BFS**（无权图最短路径）

**识别信号**：
- "最短"、"最少步数" → BFS
- "所有可能路径" → DFS
- "是否可达" → BFS 或 DFS 均可

**BFS 模板**（面试时能说出思路即可）：
```python
from collections import deque

def shortest_path(robot, target_x, target_y):
    start = (robot.x, robot.y)
    target = (target_x, target_y)
    queue = deque([(start, 0)])  # (位置, 步数)
    visited = {start}

    while queue:
        (x, y), steps = queue.popleft()
        if (x, y) == target:
            return steps
        for dx, dy in [(0,1),(0,-1),(1,0),(-1,0)]:
            nx, ny = x + dx, y + dy
            if robot.table.is_valid_position(nx, ny) and (nx, ny) not in visited:
                visited.add((nx, ny))
                queue.append(((nx, ny), steps + 1))
    return -1  # 不可达
```

### 4. 常见追问与应对

| 面试官追问 | 你应该说的 |
|-----------|-----------|
| 为什么用栈不用队列？ | UNDO 是后进先出，栈天然匹配 |
| 时间复杂度是多少？ | 每次操作 O(1)，历史长度 O(n) 空间 |
| 如果要支持 REDO 呢？ | 需要第二个栈存储被撤销的操作 |
| 1000x1000 的桌子怎么优化？ | 稀疏表示：只存机器人和障碍物位置，而不是整个网格 |

### 总结

面试考的不是你背了多少算法，而是：
- 能否**识别**当前问题是什么数据结构/算法类型
- 能否**说清楚**选择的理由和权衡
- 能否**快速实现**一个够用的版本，而不是最优版本