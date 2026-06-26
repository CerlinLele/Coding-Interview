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

---

## 更多扩展方向（面试练习题库）

下面是一组**当前文档尚未覆盖**的扩展方向，专门用于正式面试前的练习。
每一条都基于你现有的代码约定：

- 方法返回 `{"success": bool, "message": str}`（`report()` 例外，返回字符串或 `None`）
- `history` 是 `(x, y, facing)` 元组栈，`move_count` 记录有效移动数
- `DIRECTION_DELTAS` / `DIRECTIONS` 驱动方向逻辑
- `execute()` 用 if-elif 分发命令
- `table.robots` 是二维网格，存 `Robot` 或 `None`

练习方法：盖住"实现思路"，只看"典型题目"，自己先口述方案 → 写实现 → 跑测试 → 再对照。

---

### 扩展 A：REDO（重做）— 难度 ★★

文档里已经在追问表格提到"REDO 需要第二个栈"，这里做成完整练习。

**典型题目**：
- 实现 `REDO`，重做刚刚被 `UNDO` 撤销的操作
- 连续 `UNDO` 后能连续 `REDO` 回到最新状态

**考察点**：
- 双栈设计（undo 栈 + redo 栈）
- 关键边界：**执行新命令后 redo 栈必须清空**（这是最容易漏的点，面试官常追问）
- `move_count` 在 redo 时如何同步

**应对策略**：
- 先说清不变量："任何新的 MOVE/LEFT/RIGHT 都会让 redo 历史失效，这点和编辑器的撤销/重做一致"
- 指出现有 `undo()` 已经在 pop history，我只要在 pop 时把状态推到 redo 栈

**示例实现思路**：

```python
def __init__(self, table, name="anonymous"):
    # ... 现有字段
    self.redo_stack = []  # 新增

def _record_for_redo(self, state):
    self.redo_stack.append(state)

def undo(self):
    if not self.history:
        return {"success": False, "message": "No history to undo."}
    # 撤销前，把"当前状态"存进 redo 栈，方便 REDO 回来
    self.redo_stack.append((self.x, self.y, self.facing))
    # ... 现有 undo 逻辑

def redo(self):
    if not self.redo_stack:
        return {"success": False, "message": "Nothing to redo."}
    self.history.append((self.x, self.y, self.facing))
    self.table.robots[self.x][self.y] = None
    self.x, self.y, self.facing = self.redo_stack.pop()
    self.table.robots[self.x][self.y] = self
    return {"success": True, "message": "Redone."}

# 在任何"产生新历史"的命令里（move/left/right）清空 redo 栈：
def move(self, direction="forward"):
    # ... 移动成功后：
    self.redo_stack.clear()
```

**面试官常用追问**：
- "如果 UNDO 后又执行了 MOVE，再 REDO 会怎样？" → redo 栈已清空，REDO 失败，这是正确行为
- "move_count 怎么对齐？" → redo 一个移动要 +1，redo 一个转向不变，逻辑和 undo 镜像

---

### 扩展 B：MOVE n（一次移动多步）— 难度 ★★

**典型题目**：
- 支持 `MOVE 3`，向前移动 3 步
- 路上遇到边界/障碍/其他机器人就**停在最后一个合法格子**，而不是整体失败

**考察点**：
- "尽力而为"语义 vs "全有全无"语义 —— 你能不能主动问面试官想要哪种
- 复用单步 `move()` 而不是复制逻辑
- `move_count` 累加几次

**应对策略**：
- 先确认语义："MOVE 3 如果第二步就撞墙，你是希望停在第一步，还是整个命令失败回退？我倾向停在能到的最远处，更符合直觉"
- 复用现有单步 move：循环调用，遇到失败就 break

**示例实现思路**：

```python
def move_steps(self, steps, direction="forward"):
    if not self.is_placed():
        return {"success": False, "message": "Robot is not placed on the table."}

    moved = 0
    for _ in range(steps):
        result = self.move(direction)  # 复用单步逻辑，含历史/计数/网格更新
        if not result.get("success"):
            break
        moved += 1

    return {
        "success": moved > 0,
        "message": f"Moved {moved} of {steps} step(s).",
    }
```

**`execute()` 解析**：

```python
elif command.startswith('MOVE'):
    parts = command.split()
    steps = int(parts[1]) if len(parts) == 2 and parts[1].isdigit() else 1
    return self.move_steps(steps, direction="forward")
```

**面试官常用追问**：
- "MOVE 3 撞墙停在第 2 格，UNDO 一次会退几格？" → 因为每步都进 history，UNDO 一次只退一格（要主动说明这个设计选择）
- "MOVE 0 或 MOVE -1 呢？" → 边界校验，负数应拒绝或视为 0

---

### 扩展 C：环绕桌面 / TELEPORT 边界（toroidal）— 难度 ★★

**典型题目**：
- 改为环绕地图：从右边缘 MOVE 出去会出现在左边缘（吃豆人式）
- 或者增加一个可切换的"环绕模式"

**考察点**：
- 把"是否越界"的策略与移动逻辑解耦
- 取模运算 `% width` / `% height`
- 这是个很好的"开放讨论"题：要不要做成可配置策略

**应对策略**：
- 务实开场："最简单的方式是在算 new_x 后对宽高取模，但这样会绕过现有的边界检查，所以我想把它做成 Table 的一个模式"
- 强调不破坏障碍物/碰撞逻辑：环绕只影响边界，落点仍要过 `is_valid_position`

**示例实现思路**（落点计算放在 Robot，合法性仍交给 Table）：

```python
def _next_cell(self, dx, dy):
    nx, ny = self.x + dx, self.y + dy
    if self.table.wrap:                 # Table 新增 wrap 标志
        nx %= self.table.width
        ny %= self.table.height
    return nx, ny
```

**面试官常用追问**：
- "环绕模式下还会有'掉下桌子'吗？" → 不会，但障碍物和机器人碰撞仍然挡路
- "如果桌子是 1×1 呢？" → 环绕后原地不动，注意别死循环

---

### 扩展 D：FACE X,Y（转向目标）/ SCAN（传感）— 难度 ★★★

**典型题目**：
- `FACE X,Y`：原地旋转到最接近目标点的四个正方向之一
- `SCAN`：返回当前朝向上第一个障碍物/机器人/边界的距离

**考察点**：
- 把"目标方向"映射到离散的四方向（涉及 dx/dy 的符号判断）
- SCAN 是一个小的"射线步进"循环，体现你对网格遍历的掌握
- 复用 `DIRECTION_DELTAS`

**应对策略**：
- FACE 先讲简化："只支持四个正方向，所以我看 dx、dy 谁的绝对值大，就朝那个轴；这是一种合理的近似"
- SCAN 讲清返回什么："我返回到第一个障碍的步数，没有障碍就返回到边界的距离"

**示例实现思路**：

```python
def scan(self):
    """沿当前朝向探测，返回到第一个阻挡的距离。"""
    if not self.is_placed():
        return {"success": False, "message": "Robot is not placed on the table."}

    dx, dy = self.DIRECTION_DELTAS[self.facing]
    distance = 0
    x, y = self.x, self.y
    while True:
        x, y = x + dx, y + dy
        if not self.table.is_valid_position(x, y).get("success"):
            break
        distance += 1
    return {"success": True, "message": f"Clear for {distance} cell(s) ahead."}
```

**面试官常用追问**：
- "FACE 对角线方向（dx == dy）怎么办？" → 需要定一个 tie-break 规则，主动说出来
- "SCAN 能区分撞墙还是撞机器人吗？" → 可以让 `is_valid_position` 的 message 透传出来，体现你之前 return dict 的设计有了回报

---

### 扩展 E：从文件批量执行 + 错误报告 — 难度 ★★

注意：文档 Level 4 已有"文件读取"骨架，这里的练习重点是**当前 `execute()` 对非法命令静默返回 `None`**，面试官常会借此考你错误处理。

**典型题目**：
- 从文件读命令并执行（Level 4 已有）
- **升级**：非法命令不再静默忽略，而是收集行号和原因，最后汇总报告

**考察点**：
- 你是否注意到现有 `execute()` 把所有错误都吞成了 `None`
- 区分"未知命令"和"命令合法但执行失败"（如越界）
- 不破坏现有交互式 main 的行为

**应对策略**：
- 先点出现状："现在 `execute()` 对 `PLACE x` 这种格式错误直接返回 None，用户不知道为什么没反应"
- 提出小改进："我让 execute 对未知命令也返回一个 success=False 的 dict，这样文件执行器就能统计错误"

**示例实现思路**：

```python
def run_file(robot, filepath):
    errors = []
    with open(filepath) as f:
        for lineno, line in enumerate(f, start=1):
            cmd = line.strip()
            if not cmd:
                continue
            result = robot.execute(cmd)
            if result is None:
                errors.append((lineno, cmd, "unknown or malformed command"))
            elif isinstance(result, dict) and not result.get("success"):
                errors.append((lineno, cmd, result.get("message")))
    return errors
```

**面试官常用追问**：
- "为什么 REPORT 返回字符串而别的返回 dict，不别扭吗？" → 诚实回答这是历史遗留的不一致，可以统一成 dict 但会动到现有测试，属于权衡
- "文件里有一行 EXIT 怎么办？" → 在批量模式里 EXIT 应该停止后续执行

---

### 扩展 F：重构 —— 用分发表替换 if-elif 链 — 难度 ★★★

**典型题目**：
- 面试官："现在 `execute()` 里 7 个 if-elif，如果命令涨到 20 个会很长，能优化吗？"

**考察点**：
- 这是经典的"何时该抽象"判断题 —— 千万别一上来就上策略模式
- 能否用最轻量的"字典分发"而不是一堆类
- 重构时保持所有测试通过

**应对策略**：
- 先守住务实底线："7 个命令用 if-elif 其实很清晰，重构是为了可读和加新命令方便，不是为了炫技"
- 选最轻方案："我用一个 `{命令: 处理函数}` 字典，比抽象基类 + 命令类轻得多"
- 强调 PLACE/MOVE n 这类**带参数**的命令是分发表的难点，要单独说

**示例实现思路**：

```python
def __init__(self, ...):
    # 无参命令的分发表
    self._commands = {
        'MOVE':     lambda: self.move("forward"),
        'BACKWARD': lambda: self.move("backward"),
        'LEFT':     self.left,
        'RIGHT':    self.right,
        'REPORT':   self.report,
        'UNDO':     self.undo,
    }

def execute(self, command):
    command = command.strip().upper()
    if command.startswith('PLACE'):
        return self._handle_place(command)   # 带参数的单独处理
    handler = self._commands.get(command)
    return handler() if handler else None
```

**面试官常用追问**：
- "PLACE 带参数，放不进这个表，怎么办？" → 老实说带参命令需要单独解析，分发表只优雅地处理无参命令；强行统一反而更复杂
- "什么时候才值得上命令模式（Command 类）？" → 当你需要把命令**对象化**（排队、序列化、网络传输、统一 undo 接口）时才值得，现在不需要

---

### 扩展 G：保存 / 加载状态（序列化）— 难度 ★★

**典型题目**：
- `SAVE` 把当前所有机器人和障碍物状态写盘
- `LOAD` 恢复，使会话可中断续玩

**考察点**：
- 选什么格式（JSON 最务实）
- 哪些字段需要持久化（`uuid` 要不要存？`history` 要不要存？）
- 反序列化时如何重建 `table.robots` 二维网格

**应对策略**：
- 务实选型："JSON 够了，人类可读、标准库支持，不需要 pickle 的复杂和安全风险"
- 主动划范围："我先存位置、朝向、障碍物这些核心状态，history 是否要存取决于是否要求保留 undo 能力"

**示例实现思路**：

```python
import json

def to_dict(self):
    return {"x": self.x, "y": self.y, "facing": self.facing,
            "name": self.name, "move_count": self.move_count}

def save_table(table, filepath):
    state = {
        "width": table.width,
        "height": table.height,
        "robots": [c.to_dict() for row in table.robots for c in row if c],
    }
    with open(filepath, "w") as f:
        json.dump(state, f)
```

**面试官常用追问**：
- "uuid 用 json 能直接序列化吗？" → 不能，要 `str(self.id)`，这是个好的细节考点
- "加载时位置冲突怎么办？" → 走现有 `is_valid_position` 校验，体现复用

---

### 扩展 H：机器人推挤（MOVE 时推动前方机器人）— 难度 ★★★★

**典型题目**：
- 当机器人 MOVE 撞到另一个机器人时，不再被挡住，而是**把对方推一格**（如果对方后面是空的）
- 推不动（对方后面是墙/障碍/第三个机器人）则整体失败

**考察点**：
- 多对象联动状态更新（两个机器人 + table 网格同时变）
- 递归/链式推动（A 推 B，B 又顶着 C）—— 很好的开放讨论点
- 失败回退：推到一半发现推不动怎么保持一致性

**应对策略**：
- 先做单层推动，明确不处理连环推："我先实现推一个，连环推动我会在确认这个能跑之后再说"
- 强调原子性："我先检查整条推动链是否可行，全部可行才真正移动，避免推一半的脏状态"

**示例实现思路**（单层推动）：

```python
def move(self, direction="forward"):
    # ... 算出 new_x, new_y
    validation = self.table.is_valid_position(new_x, new_y)
    if not validation.get("success"):
        occupant = self.table.robots[new_x][new_y]
        if occupant is not None:           # 撞到的是机器人 → 尝试推
            push_result = occupant.move(direction)  # 让对方朝同方向走
            if not push_result.get("success"):
                return validation          # 推不动，整体失败
            validation = self.table.is_valid_position(new_x, new_y)  # 对方让开后重新校验
        else:
            return validation              # 撞墙/障碍，正常失败
    # ... 正常移动
```

**面试官常用追问**：
- "A 推 B，B 后面是 C，能连环推吗？" → 上面的递归写法天然支持，但要小心两个机器人面对面互推的死循环
- "推动算谁的 move_count？" → 设计选择题，主动表态（我倾向各算各的）

---

### 扩展 I：回放 / REPLAY — 难度 ★★

**典型题目**：
- 记录完整命令序列，`REPLAY` 从初始状态重新逐步执行并打印每一步
- 用于演示或调试

**考察点**：
- 区分"状态历史"（你现在的 `history` 栈）和"命令历史"（要新增）
- 重放需要先重置到初始状态
- 与 UNDO 的 history 不冲突

**应对策略**：
- 指出现有 history 存的是状态快照，不能直接拿来重放；重放需要单独记原始命令字符串
- 简单实现：在 `execute()` 成功时把命令追加到 `command_log`

**示例实现思路**：

```python
def execute(self, command):
    result = self._dispatch(command)   # 原有逻辑抽到 _dispatch
    if result and (not isinstance(result, dict) or result.get("success")):
        self.command_log.append(command.strip().upper())
    return result

def replay(self):
    log = list(self.command_log)
    self.__init__(self.table, self.name)   # 重置
    for cmd in log:
        print(f"{cmd} -> {self.execute(cmd)}")
```

**面试官常用追问**：
- "REPLAY 时 table 上别的机器人还在原位吗？" → 暴露了重置范围问题，主动讨论是重置单个机器人还是整张桌子
- "命令日志会无限增长吗？" → 同 UNDO 的内存讨论，可设上限

---

### 练习用难度索引

| 扩展 | 难度 | 主要考点 | 适合的面试阶段 |
|------|------|---------|--------------|
| A. REDO | ★★ | 双栈、不变量 | Level 2 状态管理 |
| B. MOVE n | ★★ | 复用、语义澄清 | Level 1-2 |
| C. 环绕边界 | ★★ | 策略解耦、取模 | Level 1 + 开放讨论 |
| D. FACE/SCAN | ★★★ | 方向映射、射线步进 | Level 2-3 |
| E. 文件+错误报告 | ★★ | 错误处理、API 一致性 | Level 4 |
| F. 分发表重构 | ★★★ | 何时抽象、克制 | Level 4 重构 |
| G. 保存/加载 | ★★ | 序列化、字段取舍 | Level 3-4 |
| H. 机器人推挤 | ★★★★ | 多对象联动、原子性 | Level 3 复杂交互 |
| I. REPLAY | ★★ | 命令 vs 状态历史 | Level 2-3 |

---

### 练习时给自己的检查清单

每做完一道扩展，自检是否做到了：

- [ ] **开口确认语义**：在写代码前问清楚"你想要哪种行为？"（尤其 B、C、H）
- [ ] **复用而非复制**：有没有调用现有的 `move()` / `is_valid_position()`，而不是抄一遍逻辑
- [ ] **主动说权衡**：至少说出一个"我选 X 而不是 Y，因为……"
- [ ] **立即验证**：写完先跑一个最小例子，再补边界测试
- [ ] **诚实暴露局限**：主动说"现在没处理 ____，如果需要我可以……"
- [ ] **克制抽象**：没有为了一个小功能引入一堆类/模式