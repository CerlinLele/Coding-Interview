# Toy Robot 单机器人系统 - 设计总结

练习目标：实现完整的单机器人系统，支持基础命令、撤销、移动计数、障碍物

---

## Question 1.1: BACKWARD 命令实现

**问题**：如何实现机器人向后移动？

**场景**：机器人在 (2, 2) 面向 NORTH，执行 BACKWARD 应移动到 (2, 1)。

**选项**：

**(A) 在 move() 中加参数**：

```python
def move(self, backward=False):
    direction = -1 if backward else 1
    # ...
```

- ✅ Pro: 代码复用，DRY
- ❌ Con: 命令语义不清，违反 SRP（move 责任太多）

**(B) 单独实现 backward()**：

```python
def backward(self):
    dx, dy = self.DIRECTION_DELTAS[self.facing]
    new_x, new_y = self.x - dx, self.y - dy
    if self.table.is_valid_position(new_x, new_y):
        self.x, self.y = new_x, new_y
        self.move_count += 1
        return True
    return False
```

- ✅ Pro: 清晰、独立、易测试
- ✅ Pro: 与 move() 对称
- ❌ Con: 代码有重复

**(C) 提取公共方法**：

```python
def _move_in_direction(self, direction_multiplier):
    # 共享逻辑
```

- ✅ Pro: DRY，无重复
- ❌ Con: 增加中间层，复杂度上升

**你的答案**：B ✅

**设计反馈**：

单独实现 `backward()` 是最好的选择。虽然有代码重复，但：

1. **清晰性 > DRY**：两个独立命令，实现分离，易理解
2. **对称性**：`move()` 和 `backward()` 平行，用户期望
3. **未来维护**：若 backward 有特殊逻辑，不用改 move

**决策确认**：`backward()` 单独实现，即使有代码重复。

**后续重构：消除重复**

在代码发展过程中，发现 `move()` 和 `backward()` 有大量重复逻辑。虽然最初选择了分离的设计（便于理解），但当两个方法都需要同步修改时（如添加历史记录、网格更新、障碍物检查），重复成为维护成本。

重构方案：用参数统一两个方法。

**观察**：两个方法唯一的区别是方向。
```python
# move()：new_x = self.x + dx, new_y = self.y + dy
# backward()：new_x = self.x - dx, new_y = self.y - dy
```

**重构后的实现**：
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
        self.table.robots[self.x][self.y] = None
        self.x = new_x
        self.y = new_y
        self.move_count += 1
        self.table.robots[new_x][new_y] = self
        return True
    
    return False
```

**命令处理层更新**：
```python
elif command == 'MOVE':
    self.move(direction="forward")

elif command == 'BACKWARD':
    self.move(direction="backward")
```

**权衡分析**：

| 维度 | 分离实现 (B) | 参数化统一 | 结论 |
|------|-----------|---------|------|
| **代码行数** | 31 行重复 | 无重复，集中 | 参数化优 |
| **维护成本** | 改一处要改两处 | 改一处 | 参数化优 |
| **理解难度** | 立即明白 | 需读参数文档 | 分离优 |
| **适用时机** | Level 1（快速）| Level 1+ 追问（重构） | 都有场景 |

**何时重构**：
- 有时间且面试官暗示"代码有重复" → 重构
- 时间紧张 → 保持分离实现
- 面试官明确要求 DRY → 立即重构

**面试官期望的表现**：
1. 先做出 B 方案（清晰、正确）
2. 面试官追问"有没有办法优化"时，说出参数化思路
3. 指出权衡："参数化去重，但多一个参数需要文档"
4. 快速实现并验证测试通过

**教训**：最优的架构不是一开始就完美，而是随代码增长而演进。清晰 > 完美。

---

## Question 1.2: 历史记录保存时机

**问题**：何时保存历史记录才能让 UNDO 工作正确？

**场景**：
```
执行顺序: MOVE → MOVE → LEFT → BACKWARD → UNDO
预期结果: 恢复到 BACKWARD 前的状态
```

**选项**：

**(A) 在 execute() 中无条件保存**：

```python
def execute(self, command):
    old_state = (self.x, self.y, self.facing)
    self.history.append(old_state)  # 先保存
    if command == 'MOVE':
        self.move()
    # ...
```

- ❌ Pro: 集中管理历史
- ❌ Con: 失败的命令也被记录
- ❌ Con: UNDO 本身也被记录，导致 pop 出错误的状态

**(B) 操作成功后在各方法内保存**：

```python
def move(self):
    new_x, new_y = self.calculate_new_position()
    if self.table.is_valid_position(new_x, new_y):
        self.history.append((self.x, self.y, self.facing))  # 成功后保存
        self.x, self.y = new_x, new_y
        return True
    return False
```

- ✅ Pro: 只有成功操作被记录
- ✅ Pro: UNDO 自己不被记录
- ✅ Pro: 逻辑清晰，每个方法掌控自己的历史

**(C) 用装饰器管理**：

```python
@save_history
def move(self):
    # ...
```

- ✅ Pro: 集中，无重复
- ❌ Con: 魔法，难调试
- ❌ Con: 装饰器不知道操作是否成功

**你的答案**：B ✅

**踩坑记录**：

第一次犯的错误是选择 A，导致：

```
历史堆栈: [state1, state2, state3, UNDO_cmd]
                              ↑ 错误：UNDO本身也被记
pop() → UNDO_cmd（错！应该是 state3）
```

**修复过程**：
1. 移除 execute() 中的 `history.append()`
2. 在 `move()`、`backward()`、`left()`、`right()` 中分别检查成功后保存
3. `undo()` 方法不保存历史

**教训**：元操作（UNDO、REDO）不应被记录。历史只记录状态改变，不记录查询或撤销操作。

**决策确认**：操作成功后在各方法内保存历史，UNDO 不入栈。

---

## Question 2.1: UNDO 判断逻辑

**问题**：UNDO 时如何判断撤销的是移动还是旋转？

**背景**：
- 移动操作（MOVE、BACKWARD）改变位置和 move_count
- 旋转操作（LEFT、RIGHT）只改变朝向，不改 move_count

UNDO 后需要：
- 如果撤销的是移动 → 减 move_count
- 如果撤销的是旋转 → 保持 move_count 不变

**场景**：
```
初始: (1, 1, NORTH, count=0)
MOVE → (1, 2, NORTH, count=1) 历史:[1,1,N]
LEFT → (1, 2, WEST, count=1) 历史:[1,2,N]
UNDO → (1, 2, NORTH, count=1) ✅ count 不变（撤销的是旋转）
```

**选项**：

**(A) 比较朝向**：

```python
def undo(self):
    old_state = self.history.pop()  # (x, y, facing)
    if old_state[2] == self.facing:  # facing 相同 → 是移动操作
        self.move_count -= 1
    self.x, self.y, self.facing = old_state
    return True
```

- ✅ Pro: 简单有效
- ✅ Pro: 无需额外数据结构
- ✅ Pro: 恢复所有三个维度 (x, y, facing)

**(B) 在历史中标记操作类型**：

```python
self.history.append({
    'state': (x, y, facing),
    'op': 'move'  # 标记操作类型
})
```

- ✅ Pro: 显式清晰
- ❌ Con: 内存开销大
- ❌ Con: 增加复杂度

**(C) 分离位置和朝向历史**：

```python
self.position_history = [(x, y), ...]  # 仅移动
self.facing_history = [facing, ...]    # 仅旋转
```

- ✅ Pro: 明确的职责分离
- ❌ Con: 两个历史要同步，复杂
- ❌ Con: UNDO 需要选择撤销哪个

**你的答案**：A ✅

**设计反馈**：

选项 A 是聪明的最小设计。洞察：
- 移动改变位置和朝向 → 恢复的 `old_state[2]` 与当前 `self.facing` 不同
- 旋转只改朝向 → 恢复的 `old_state[2]` 与当前 `self.facing` 相同

判断逻辑如下表：

| 操作 | 前 | 后 | 历史记录 | old_state[2] | self.facing | 判定 |
|------|----|----|---------|-------------|-------------|------|
| MOVE N→S | (1,1,N) | (2,1,S) | (1,1,N) | N | S | 不同 → 减 count ✅ |
| LEFT | (1,1,N) | (1,1,W) | (1,1,N) | N | W | 相同？❌ 错！ |

等等，我逻辑有问题。让我重新思考。

实际逻辑应该是：
- LEFT: (1,1,N) → (1,1,W)，历史保存 (1,1,N)
- UNDO: pop (1,1,N)，恢复 x,y,facing，现在 facing=N，之前是 W
  - old_state[2]=N，self.facing(现在)=W，不相同
  - 意味着旋转了（朝向变了），UNDO 后朝向恢复，但位置没变 → 不减 count ✅

我之前的理解反了。让我用实际场景验证：

```
状态1: (1, 2, NORTH, count=1)
执行 LEFT → (1, 2, WEST, count=1)，历史入栈：(1, 2, NORTH)
执行 UNDO:
  old_state = pop() = (1, 2, NORTH)
  old_state[2] = NORTH（旧朝向）
  self.facing = WEST（当前朝向）
  NORTH == WEST? 否
  所以这里意味着朝向变过，只有旋转改朝向，所以不减 count ✓
```

```
状态2: (1, 2, NORTH, count=1)
执行 MOVE → (1, 3, NORTH, count=2)，历史入栈：(1, 2, NORTH)
执行 UNDO:
  old_state = pop() = (1, 2, NORTH)
  old_state[2] = NORTH
  self.facing = NORTH
  NORTH == NORTH? 是
  这意味着位置变过但朝向没变，只有移动改位置不改朝向，所以减 count ✓
```

哦我明白了，逻辑是对的！对比：
- 如果 `old_state[2] == self.facing`：位置变了、朝向没变 → 移动操作 → 减 count
- 如果 `old_state[2] != self.facing`：朝向变了 → 旋转操作 → 不减 count

**踩坑记录**：

第一版有 bug：

```python
def undo(self):
    if not self.history:
        return False
    current_state = self.history.pop()
    if current_state[2] == self.facing:
        self.move_count -= 1     # 第一次减
    self.x, self.y, self.facing = current_state
    self.move_count -= 1         # ❌ 错误：又减了一次！
    return True
```

结果：UNDO 后 count 被减了两次。修复：删除第二个 `self.move_count -= 1`。

**教训**：精确掌握条件逻辑，避免双重处理。

**决策确认**：比较朝向来判断操作类型，简洁高效。

---

## Question 2.2: 移动计数设计

**问题**：BACKWARD 算不算移动？count 应该存在哪里？PLACE 重置 count 吗？

**选项对比表**：

| 问题 | 选项 A | 选项 B | 选项 C | **选择** |
|------|--------|--------|--------|---------|
| **BACKWARD 算 move** | 不算 | 算 | 不算 | **B** ✅ |
| **count 存储** | Robot 字段 | 表格字段 | 外部计数器 | **A** ✅ |
| **UNDO 减 count** | 无条件减 | 仅移动时减 | 根据操作类型减 | **B** ✅ |
| **PLACE 重置** | 重置 | 不重置 | 有条件重置 | **B** ✅ |

**详细设计**：

**(1) BACKWARD 算移动**：
```python
def backward(self):
    # ...
    if valid:
        self.history.append((self.x, self.y, self.facing))
        self.x, self.y = new_x, new_y
        self.move_count += 1  # ✅ 算一次
```

理由：BACKWARD 改变了位置，就是移动。

**(2) count 存在 Robot**：
```python
class Robot:
    def __init__(self, table):
        self.move_count = 0  # ✅ 实例变量
```

理由：count 是机器人自身的属性，不是表的属性。

**(3) UNDO 有条件地减**：
```python
if old_state[2] == self.facing:  # 移动操作
    self.move_count -= 1
```

理由：旋转操作不改位置，不应减 count。

**(4) PLACE 不重置**：
```python
def place(self, x, y, facing):
    # 不做 self.move_count = 0
    self.x = x
    self.y = y
    self.facing = facing
```

理由：PLACE 是初始化操作，不是状态变化。count 从 0 开始是自然的（新 Robot 本就是 0）。

**REPORT 输出**：
```python
def report(self):
    return f"{self.x},{self.y},{self.facing},{self.move_count}"
```

**踩坑记录**：

曾考虑过把 count 存在 Table：
```python
class Table:
    def __init__(self):
        self.robot_move_counts = {}  # {robot_id: count}
```

但问题：
- Robot 每次移动都要调 table 更新，破坏封装
- count 是 Robot 的生命周期属性，不应分散

**教训**：属性应存在拥有者对象。count 由 Robot 管理是最自然的。

**决策确认**：
- BACKWARD 算移动 ✅
- count 是 Robot 实例变量 ✅
- UNDO 时有条件地减 count ✅
- PLACE 不重置 count ✅

---

## Question 3.1: 障碍物存储和检查

**问题**：障碍物数据存在哪里？谁负责检查？运行时能添加吗？

**场景**：初始化时传入障碍物列表，机器人无法移动到障碍物位置。

**选项**：

**(A) 存在 Robot，Robot 自己检查**：

```python
class Robot:
    def __init__(self, obstacles):
        self.obstacles = obstacles
    
    def move(self):
        if (new_x, new_y) in self.obstacles:
            return False
```

- ❌ Con: 每个 Robot 复制一份数据（浪费）
- ❌ Con: Robot 需要知道 Table 的实现细节

**(B) 存在 Table，Table 检查**：

```python
class Table:
    def __init__(self, width, height, obstacles=None):
        self.obstacles = [[0 for _ in range(width)] for _ in range(height)]
        if obstacles:
            for x, y in obstacles:
                self.obstacles[x][y] = 1
    
    def is_valid_position(self, x, y):
        return (0 <= x < self.width and 
                0 <= y < self.height and 
                self.obstacles[x][y] == 0)
```

- ✅ Pro: 单一数据源（表）
- ✅ Pro: 单一职责（Table 验证）
- ✅ Pro: 易扩展（加障碍物、加碰撞检查）

**(C) 运行时动态添加**：

```python
table.add_obstacle(2, 2)
table.remove_obstacle(2, 2)
```

- ⚠️ Pro: 灵活
- ❌ Con: 复杂，引入状态变化
- ❌ Con: 可能导致机器人被困

**你的答案**：B（存在 Table）+ 初始化时指定（不支持运行时添加）✅

**设计反馈**：

选项 B 完美应用 Single Responsibility Principle：
- Table 拥有表的配置（大小、障碍物）
- Robot 仅关心自己的状态（位置、朝向、历史）
- `is_valid_position()` 是 Table 的"验证器"，一处检查所有合法性

**数据结构选择**：

| 表大小 | 选项 | 优点 | 缺点 |
|-------|------|------|------|
| 5×5 ~ 1000×1000 | 2D 数组 | 检查快 O(1) | 内存占用大 |
| 1M×1M + 10 障碍 | Set | 内存省 | 检查稍慢 O(1) |

当前用 2D 数组，对 5×5 表足够。

**踩坑记录**：

第一版代码：

```python
def __init__(self, width, height, obstacles=None):
    self.width = width
    self.height = height
    if obstacles is None:
        obstacles = []  # ❌ 只设局部变量
    else:
        self.obstacles = [[0 for _ in range(width)] for _ in range(height)]
        for obstacle in obstacles:
            self.obstacles[obstacle[0]][obstacle[1]] = 1
        # 另一分支才初始化 self.obstacles
```

导致当 `obstacles=None` 时，`self.obstacles` 不存在。后续 `is_valid_position()` 访问 `self.obstacles[x][y]` 抛 AttributeError。

修复：

```python
def __init__(self, width, height, obstacles=None):
    self.width = width
    self.height = height
    # ✅ 始终初始化障碍物网格
    self.obstacles = [[0 for _ in range(width)] for _ in range(height)]
    # 如果提供了障碍物，标记它们
    if obstacles is not None:
        for obstacle in obstacles:
            self.obstacles[obstacle[0]][obstacle[1]] = 1
```

**教训**：实例变量必须在所有代码路径中初始化。条件分支中遗漏初始化是常见运行时 bug。

**决策确认**：
- 障碍物存在 Table ✅
- Table.is_valid_position() 负责检查 ✅
- 初始化时指定，不支持运行时添加 ✅

---

## 踩过的坑总结

### 坑 1：类变量 vs 实例变量

```python
class Robot:
    HISTORY = []  # ❌ 所有实例共享！
    
    def __init__(self, table):
        self.table = table
        # 没有初始化 self.history
```

**症状**：多个 Robot 实例的测试互相污染。

**根因**：可变类变量被所有实例共享。

**修复**：
```python
class Robot:
    def __init__(self, table):
        self.history = []  # ✅ 实例变量
```

**教训**：可变对象（list、dict）必须作为实例变量在 `__init__` 中初始化，不能作为类变量。

---

### 坑 2：变量名大小写不一致

```python
def __init__(self):
    self.history = []

def undo(self):
    self.HISTORY.pop()  # ❌ AttributeError：不存在的属性
```

**症状**：运行时 AttributeError。

**修复**：
- 类常量用大写：`DIRECTION_DELTAS`、`DIRECTIONS`
- 实例变量用小写：`history`、`move_count`
- 保持一致

---

### 坑 3：可变默认参数

```python
def __init__(self, width, height, obstacles=[]):  # ❌
    self.obstacles = obstacles
```

**症状**：所有 Table 实例共享同一个 obstacles 列表。

**修复**：
```python
def __init__(self, width, height, obstacles=None):
    if obstacles is None:
        obstacles = []
    self.obstacles = obstacles
```

**教训**：Python 函数默认参数在定义时求值一次。可变默认值会被所有调用共享。

---

### 坑 4：条件分支遗漏初始化

```python
def __init__(self, obstacles=None):
    if obstacles is None:
        obstacles = []  # ❌ 只设局部变量
    else:
        self.obstacles = [[...]]  # 另一分支才初始化

def is_valid_position(self, x, y):
    return ... and self.obstacles[x][y] == 0  # ❌ 当 None 时崩溃
```

**症状**：26 个测试失败，AttributeError。

**根因**：一个分支忘了初始化实例变量。

**修复**：无条件初始化所有实例变量。

```python
def __init__(self, obstacles=None):
    self.obstacles = [[0 for _ in range(width)] for _ in range(height)]
    if obstacles is not None:
        for obstacle in obstacles:
            self.obstacles[obstacle[0]][obstacle[1]] = 1
```

**教训**：在 `__init__` 中，确保每个实例变量在所有代码路径中都被赋值一次。

---

### 坑 5：历史保存时机错误

```python
def execute(self, command):
    self.history.append((self.x, self.y, self.facing))  # 无条件保存
    self.move()  # 可能失败

def move(self):
    if not valid:
        return False  # 失败，但历史已入栈
```

**症状**：失败的操作也被记录，UNDO 回退了不应记录的操作。

修复：成功后才保存。

---

### 坑 6：UNDO 双重递减

```python
def undo(self):
    old_state = self.history.pop()
    if old_state[2] == self.facing:
        self.move_count -= 1  # 第一次
    self.x, self.y, self.facing = old_state
    self.move_count -= 1  # ❌ 第二次，多余！
```

**症状**：UNDO 后 count 少了 2（或更多）。

**修复**：删除多余的递减行。

---

## 最终测试覆盖

✅ 37 个测试全部通过

| 功能类别 | 测试数 | 覆盖点 |
|---------|--------|---------|
| 基础命令 | 8 | PLACE、MOVE、LEFT、RIGHT、REPORT |
| BACKWARD | 4 | 正常移动、边界阻止、各方向 |
| UNDO | 8 | 单次、多次、超出历史、各操作类型 |
| MOVE_COUNT | 6 | 计数、旋转不计、失败不计、UNDO 回退 |
| Obstacle | 5 | MOVE 被阻、BACKWARD 被阻、各位置 |
| 边界 + 其他 | 6 | 边界检查、非法命令、状态一致性 |

---

## 设计原则总结

| 原则 | 体现 | 为什么重要 |
|------|------|----------|
| **单一职责** | Table 验证、Robot 执行 | 改表的验证逻辑时不动 Robot |
| **不过度工程** | BACKWARD 不复用 move | 代码清晰 > DRY，简单 > 抽象 |
| **精确初始化** | 所有实例变量无条件初始化 | 避免运行时 AttributeError |
| **历史与元操作分离** | UNDO 自己不入栈 | 操作链清晰，撤销可靠 |
| **条件判断精确** | 朝向相同判定移动 | 避免双重处理 |

---

## 下一步：多机器人扩展

本设计为多机器人系统奠定基础：
- ✅ Robot 独立管理自己的历史和 count
- ✅ Table 验证所有合法性
- ✅ 清晰的 Robot ↔ Table 界面

扩展时需要：
1. 给 Robot 加 UUID 唯一标识
2. Table 用混合存储（dict + 2D grid）管理多个 Robot
3. Table.is_valid_position() 加入碰撞检测
4. 保持 API 向后兼容
