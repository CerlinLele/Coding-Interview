# Toy Robot 练习总结

练习目标：模拟 REA Pair Programming 面试

---

## 实现的功能

### BACKWARD 命令

机器人向当前朝向的反方向移动一步，朝向不变，遵守边界检查。

```python
def backward(self):
    if not self.is_placed():
        return False
    dx, dy = self.DIRECTION_DELTAS[self.facing]
    new_x, new_y = self.x - dx, self.y - dy
    if self.table.is_valid_position(new_x, new_y):
        self.history.append((self.x, self.y, self.facing))
        self.x, self.y = new_x, new_y
        self.move_count += 1
        return True
    return False
```

---

### UNDO 命令

撤销上一步状态改变操作，支持 MOVE、BACKWARD、LEFT、RIGHT，不支持撤销 PLACE。

**设计决策**：
| 问题 | 决策 | 理由 |
|------|------|------|
| 保存什么？ | 完整 `(x, y, facing)` 三元组 | 既有位置变化也有朝向变化 |
| 数据结构？ | list 作为栈 | append/pop 均 O(1) |
| 保存时机？ | 在各方法内部，操作成功后保存 | 失败的操作不应入栈 |
| PLACE 可被撤销？ | 否 | PLACE 是初始化，不是状态变化 |

```python
def undo(self):
    if not self.history:
        return False
    current_state = self.history.pop()
    if current_state[2] == self.facing:  # facing 未变 → 撤销的是移动
        self.move_count -= 1
    self.x, self.y, self.facing = current_state
    return True
```

---

### MOVE_COUNT 功能

REPORT 输出新增移动次数，格式变为 `x,y,FACING,count`。

**设计决策**：
| 问题 | 决策 | 理由 |
|------|------|------|
| BACKWARD 算 move？ | 算 | 位置发生了变化 |
| count 存在哪里？ | `self.move_count` 独立变量 | 与 history 职责分离 |
| UNDO 减 count？ | 减（仅撤销移动时）| 保持与 history 一致 |
| PLACE 重置 count？ | 不重置 | PLACE 是初始化操作 |

UNDO 判断是否减 count：比较 `current_state[2]`（旧 facing）与 `self.facing`（当前 facing），相等说明撤销的是移动操作。

---

### Obstacle（障碍物）功能

初始化时传入障碍物坐标，机器人无法移动到障碍物格子，行为与撞边界一致。

**设计决策**：
| 问题 | 决策 | 理由 |
|------|------|------|
| 数据存在哪里？ | `Table` | 障碍物是桌子属性，不是机器人的 |
| 数据结构？ | 二维数组 | 5x5 小表格适合密集表示；大稀疏表格应用 Set |
| 谁检查障碍物？ | `Table.is_valid_position()` | Single Responsibility |
| 运行时可添加？ | 否，初始化时传入 | 障碍物是固定状态，不是机器人操作 |

```python
table = Table(5, 5, obstacles=[(1, 2), (3, 3)])
robot = Robot(table)
```

Robot 不需要改动，`is_valid_position()` 自动拦截障碍物。

---

## 踩过的坑

### 坑 1：类变量 vs 实例变量

```python
class Robot:
    HISTORY = []  # ❌ 所有实例共享同一个列表
```

所有 Robot 实例共用一个 `HISTORY`，测试之间互相污染。

**修复**：在 `__init__` 中初始化 `self.history = []`。

**教训**：可变对象（list/dict）不能作为类变量；每个实例的独立状态必须在 `__init__` 中初始化。

---

### 坑 2：变量名大小写不一致

`__init__` 中定义 `self.history`，`undo()` 中使用 `self.HISTORY`，导致 `AttributeError`。

**教训**：类常量用大写（`DIRECTIONS`），实例变量用小写（`history`），保持一致。

---

### 坑 3：历史保存时机错误

在 `execute()` 中无条件保存历史，导致 UNDO 自己也被记录，pop 出来的是 UNDO 自己刚存的状态。

**修复**：历史保存逻辑移入各方法内部，`move()` 和 `backward()` 仅在新位置合法时保存，UNDO 不保存。

**教训**：精确控制保存时机；UNDO 这类元操作不应被记录。

---

### 坑 4：undo() 中双重递减

```python
current_state = self.history.pop()
if current_state[2] == self.facing:
    self.move_count -= 1  # 第一次

self.x, self.y, self.facing = current_state
self.move_count -= 1      # ❌ 多余的第二次
```

**修复**：删除最后一行。

---

### 坑 5：Mutable default argument

```python
def __init__(self, width, height, obstacles=[]):  # ❌ 所有实例共享同一个列表
```

**修复**：
```python
def __init__(self, width, height, obstacles=None):
    if obstacles is None:
        obstacles = []
```

**教训**：Python 函数默认参数在定义时求值一次，可变默认值会被所有调用共享。

---

### 坑 6：条件分支遗漏实例变量初始化

```python
def __init__(self, width, height, obstacles=None):
    self.width = width
    self.height = height
    if obstacles is None:
        obstacles = []  # ❌ 只设置了局部变量，self.obstacles 未初始化
    else:
        self.obstacles = [[0 for _ in range(width)] for _ in range(height)]
        for obstacle in obstacles:
            self.obstacles[obstacle[0]][obstacle[1]] = 1

def is_valid_position(self, x, y):
    return 0 <= x < self.width and 0 <= y < self.height and self.obstacles[x][y] == 0
    # ❌ 当 obstacles=None 时访问 self.obstacles 会报 AttributeError
```

当 `obstacles=None` 时，只重置了局部变量 `obstacles = []`，但 `self.obstacles` 属性从未被创建。后续调用 `is_valid_position()` 时访问 `self.obstacles[x][y]` 就会抛出 `AttributeError: 'Table' object has no attribute 'obstacles'`，导致全部测试失败（26 failed）。

**修复**：无论是否传入障碍物，都应始终初始化实例属性。

```python
def __init__(self, width, height, obstacles=None):
    self.width = width
    self.height = height
    # 始终初始化障碍物网格
    self.obstacles = [[0 for _ in range(width)] for _ in range(height)]
    # 如果提供了障碍物列表，标记它们
    if obstacles is not None:
        for obstacle in obstacles:
            self.obstacles[obstacle[0]][obstacle[1]] = 1
```

**教训**：实例变量必须在所有代码路径中都被初始化。条件分支中只初始化一部分路径会导致运行时错误。在 `__init__` 中，确保每个实例变量在方法结束前都被赋值。

---

## 重构：代码整合

### MOVE 与 BACKWARD 的合并

原先 `move()` 和 `backward()` 有大量重复逻辑：

```python
# ❌ 重复代码
def move(self):
    if not self.is_placed():
        return False
    dx, dy = self.DIRECTION_DELTAS[self.facing]
    new_x, new_y = self.x + dx, self.y + dy  # 正向
    # ... 相同的合法性检查、历史记录、网格更新逻辑

def backward(self):
    if not self.is_placed():
        return False
    dx, dy = self.DIRECTION_DELTAS[self.facing]
    new_x, new_y = self.x - dx, self.y - dy  # 反向
    # ... 完全相同的合法性检查、历史记录、网格更新逻辑
```

**重构方案**：增加 `direction` 参数，在方向差值层面处理正向/反向区别。

```python
def move(self, direction="forward"):
    """Move the robot one unit in the specified direction."""
    if not self.is_placed():
        return False
    
    dx, dy = self.DIRECTION_DELTAS[self.facing]
    if direction == "backward":
        dx, dy = -dx, -dy  # 反向：取反方向差值
    
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

**命令处理层**：通过参数区分命令意图。

```python
elif command == 'MOVE':
    self.move(direction="forward")

elif command == 'BACKWARD':
    self.move(direction="backward")
```

**优点**：
- ✓ 消除 31 行重复代码
- ✓ 修改一处即可同步两个方向的行为（边界检查、历史记录、网格更新）
- ✓ 新增方向逻辑时只需改一处

**教训**：相似的方法应在抽象层面寻找共同点，用参数或枚举区分变化部分，而非逐字复制代码。

---

## 多机器人功能

### 设计决策

| 问题 | 决策 | 理由 |
|------|------|------|
| 多机器人存储？ | 2D 数组 `table.robots[x][y]` | O(1) 碰撞检查，适合固定大小的表格 |
| 机器人标识？ | UUID + 名字 | 名字用于错误消息，UUID 保留扩展性 |
| 碰撞检测时机？ | `is_valid_position()` | 单一职责，place/move 都复用 |
| 错误信息？ | 返回字典 `{"success": bool, "message": str}` | 清晰的错误原因（边界/障碍物/机器人） |

### 实现进度

**第一阶段：基础多机器人支持**

- ✓ 机器人标识（UUID + 名字）
- ✓ 2D 网格追踪位置
- ✓ 碰撞检测和错误消息
- ✓ 网格在 place/move/backward/undo 中同步

**第二阶段：命令返回格式标准化**

- ✓ 所有命令返回 `{"success": bool, "message": str}`
- ✓ place() 返回详细验证结果
- ✓ move() 返回详细验证结果  
- ✓ left() 返回一致的字典格式
- ✓ right() 返回一致的字典格式
- ✓ undo() 返回一致的字典格式

**第三阶段：错误消息优化**

- ✓ 网格存储 (uuid, name) 元组而不是单独 UUID
- ✓ 碰撞错误消息显示机器人名字而不是 UUID
- ✓ 避免使用 Registry 模式，保持架构简洁

**第四阶段：位置追踪与查询**

- ✓ 引入 robot_positions 映射（UUID → 完整状态）
- ✓ 提供 update_robot_grid(uuid, name, x, y) 原子操作
- ✓ 提供 update_robot_position(uuid, position) 追踪
- ✓ 提供 get_robot_position(uuid) 查询接口

### 设计决策与权衡

| 问题 | 决策 | 理由 |
|------|------|------|
| UUID vs name | 两者都需要 | UUID 用于索引和持久化，name 用于用户消息 |
| 网格内容 | (uuid, name) 元组 | 避免外部 Registry，错误消息自包含 |
| robot_positions map 必要性 | 必要 | 允许通过 UUID 查询完整状态（未来持久化、序列化） |
| 网格更新原子性 | 多处调用更新方法 | place/move/undo 时同步更新网格和状态映射 |
| 错误消息格式 | 字典 `{"success": bool, "message": str}` | 所有命令一致，易于客户端处理 |

### 待解决的架构问题

- **Triple-state 问题**：Robot 持有 (x, y, facing, move_count)，Table.robots 网格持有 UUID，Table.robot_positions 持有完整状态。是否所有三个都必要？
- **Table 责任**：Table 是否应管理机器人生命周期，还是仅作为环境？当前设计：Robot 独立存在，Table 只是共享空间。
- **可扩展性**：2D 数组适合小表格；何时切换到 Set/Hash 结构？
- **并发**：多个机器人同时移动时的竞态条件？
- **机器人移除**：如何实现机器人离开表格？这会如何影响 UUID 和位置追踪？

---

## 测试覆盖

最终 **41 个测试**全部通过，覆盖：

**基础功能（13 个）**
- 位置验证（有效/无效）
- 机器人初始状态
- 放置命令（有效位置、无效位置、无效方向）
- 基本报告

**移动与旋转（14 个）**
- MOVE 命令（四个方向、边界阻止）
- LEFT/RIGHT 旋转（完整旋转周期）
- BACKWARD 命令（正向移动、边界阻止）
- 无放置时执行命令

**撤销与计数（12 个）**
- UNDO（单次、多次、超出历史）
- Move count 追踪（递增、旋转不计、失败不计）
- UNDO 回退 count（仅移动时减少）
- 失败操作不递增 count

**多机器人与碰撞（2 个）**
- 多机器人共存
- 碰撞检测（机器人间碰撞阻止移动）

**障碍物（2 个）**
- MOVE 被障碍物阻止
- BACKWARD 被障碍物阻止

**位置查询（1 个）**
- Table 通过 UUID 追踪和查询机器人位置
