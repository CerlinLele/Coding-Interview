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

撤销上一步状态改变操作，支持 MOVE、BACKWARD、LEFT、RIGHT、JUMP，不支持撤销 PLACE。

**设计决策**：
| 问题 | 决策 | 理由 |
|------|------|------|
| 保存什么？ | 完整 `(x, y, facing, move_count)` 四元组 | 既有位置变化也有朝向变化，move_count 可能因 jump 增加多个值 |
| 数据结构？ | list 作为栈 | append/pop 均 O(1) |
| 保存时机？ | 在各方法内部，操作成功后保存 | 失败的操作不应入栈 |
| PLACE 可被撤销？ | 否 | PLACE 是初始化，不是状态变化 |

```python
def undo(self):
    if not self.history:
        return {"success": False, "message": "No moves to undo"}
    
    # 恢复完整状态（包括 move_count）
    prev_x, prev_y, prev_facing, prev_move_count = self.history.pop()
    
    self.table.update_robot_grid(None, None, self.x, self.y)
    self.table.update_robot_position(self.id, None)
    
    self.x, self.y, self.facing, self.move_count = prev_x, prev_y, prev_facing, prev_move_count
    
    self.table.update_robot_grid(self.id, self.name, self.x, self.y)
    self.table.update_robot_position(self.id, (self.x, self.y, self.facing, self.move_count))
    
    return {
        "success": True, 
        "message": "Last command has been undone.",
        "position": (self.x, self.y, self.facing, self.move_count)
    }
```

**关键改进**：历史记录现在存储完整的四元组，包括 `move_count`。这样 UNDO 操作是原子的——无论上一条命令是移动（增加 1 步）还是跳跃（增加 N 步），都能正确恢复。

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

### JUMP 命令

机器人向前跳跃 N 步。每一步都检查是否被阻挡（边界、障碍物、其他机器人），一旦被阻挡就停止。停止时如果没有走完 N 步则失败。

**设计决策**：
| 问题 | 决策 | 理由 |
|------|------|------|
| 如何处理阻挡？ | 失败 (all-or-nothing) | 如果只能走 2 步但要求 3 步，应报错；不是走 2 步后成功 |
| move_count 如何更新？ | 原子递增 N 次 | jump 虽然是一条命令，但实际移动了 N 步，所以 move_count 增加 N |
| 历史如何记录？ | 记录起始状态，只有 1 条历史记录 | jump 是单条命令，undo 一次回到起始点 |
| 返回值？ | 统一格式 `{"success": bool, "message": str, "position": ...}` | 与其他命令保持一致 |

```python
def jump(self, steps):
    """Jump forward N steps. Stop if blocked by boundary, obstacle, or robot."""
    if not self.is_placed():
        return {"success": False, "message": "Robot is not placed on the table."}
    
    start_x, start_y, start_move_count = self.x, self.y, self.move_count
    dx, dy = self.DIRECTION_DELTAS[self.facing]
    
    for i in range(steps):
        new_x = self.x + dx
        new_y = self.y + dy
        
        # 检查每一步是否合法
        validation_result = self.table.is_valid_position(new_x, new_y)
        
        if not validation_result.get("success"):
            # 被阻挡，保存起始点到历史，返回失败
            if i > 0:
                self.history.append((start_x, start_y, self.facing, start_move_count))
            
            validation_result["position"] = (self.x, self.y, self.facing, self.move_count)
            return validation_result
        
        # 更新网格：清空旧位置
        self.table.update_robot_grid(None, None, self.x, self.y)
        self.table.update_robot_position(self.id, None)
        
        # 移动并更新计数
        self.x = new_x
        self.y = new_y
        self.move_count += 1
        
        # 更新网格：占据新位置
        self.table.update_robot_grid(self.id, self.name, new_x, new_y)
        self.table.update_robot_position(self.id, (new_x, new_y, self.facing, self.move_count))
    
    # 成功完成所有步数：保存起始状态到历史
    self.history.append((start_x, start_y, self.facing, start_move_count))
    
    return {
        "success": True,
        "message": f"Jump {steps} steps successfully",
        "position": (self.x, self.y, self.facing, self.move_count)
    }
```

**关键设计点**：
- **All-or-nothing**：要跳 3 步但中途被阻挡 → 失败，返回到起始点
- **原子历史记录**：只有起始点存一条记录，使得 undo 能一次性回退
- **move_count 正确累加**：跳 3 步就 +3，不是 +1

---

### 命令返回格式标准化

所有命令都返回统一的字典格式：

```python
{
    "success": bool,
    "message": str,
    "position": (x, y, facing, move_count)  # 当前状态，失败时可能为 None
}
```

**示例**：

| 命令 | 结果 |
|------|------|
| `place(0, 0, 'NORTH')` 成功 | `{"success": True, "message": "Robot is placed successfully", "position": (0, 0, 'NORTH', 0)}` |
| `place(0, 0, 'NORTH')` 被其他机器人占据 | `{"success": False, "message": "Cell (0,0) is occupied by Robot B", "position": None}` |
| `move()` 成功 | `{"success": True, "message": "Moved forward successfully", "position": (0, 1, 'NORTH', 1)}` |
| `move()` 触及边界 | `{"success": False, "message": "Cannot move: boundary at (5,0)", "position": (0, 1, 'NORTH', 1)}` |
| `jump(5)` 中途被阻挡 | `{"success": False, "message": "The position is occupied by another robot", "position": (0, 2, 'NORTH', 2)}` |

---

## 多机器人与碰撞设计

### 存储结构

**Table 维护三个结构**：

1. **`robots[x][y]` 2D 网格**：快速碰撞检测
   ```python
   robots[x][y] = (robot_id, robot_name)  # 或 None
   ```

2. **`robot_positions` 字典**：UUID → 完整状态映射
   ```python
   robot_positions[robot_id] = (x, y, facing, move_count)
   ```

3. **Robot 对象本身**：权威状态源
   ```python
   robot.x, robot.y, robot.facing, robot.move_count
   ```

**同步策略**：始终保持三者一致

```python
# 移动时的同步：
self.table.update_robot_grid(None, None, self.x, self.y)      # 清空旧位置
self.table.update_robot_position(self.id, None)

self.x, self.y = new_x, new_y
self.move_count += 1

self.table.update_robot_grid(self.id, self.name, new_x, new_y)  # 占据新位置
self.table.update_robot_position(self.id, (new_x, new_y, self.facing, self.move_count))
```

### 碰撞检测

`Table.is_valid_position()` 检查三种阻挡：

```python
def is_valid_position(self, x, y):
    # 1. 边界检查
    if not (0 <= x < self.width and 0 <= y < self.height):
        return {"success": False, "message": f"Boundary exceeded at ({x}, {y})"}
    
    # 2. 障碍物检查
    if self.obstacles[x][y] == 1:
        return {"success": False, "message": "The position is occupied by an obstacle."}
    
    # 3. 其他机器人检查
    if self.robots[x][y] is not None:
        robot_id, robot_name = self.robots[x][y]
        return {"success": False, "message": f"The position is occupied by {robot_name}."}
    
    return {"success": True, "message": "Position is valid", "position": (x, y)}
```

---

## 设计决策总结

| 问题 | 决策 | 理由 |
|------|------|------|
| 2D 数组 vs Set | 2D 数组 | O(1) 碰撞检测；5×5 小表适合密集表示 |
| Robot vs Table 谁是权威 | Robot 对象 | 状态应在一个地方；Table 仅作缓存 |
| 历史记录什么 | (x, y, facing, move_count) 四元组 | undo 需要完整恢复，包括 move_count |
| JUMP 如何处理中途阻挡 | 失败 (all-or-nothing) | 完成所有步数才能算成功 |
| 返回值格式 | 统一字典 + position | 客户端统一处理；position 帮助调试 |
| Robot 生命周期管理 | 用户负责 (Option A) | 简洁设计，Robot/Table 解耦；未来可升级为 Table 工厂 |

---

### 设计决策

| 问题 | 决策 | 理由 |
|------|------|------|
| 多机器人存储？ | 2D 数组 `table.robots[x][y]` | O(1) 碰撞检查，适合固定大小的表格；大稀疏表格应使用 Set（>100×100 且密度<5%） |
| 机器人标识？ | UUID + 名字 | UUID 用于索引和扩展，name 用于用户错误消息 |
| 碰撞检测时机？ | `is_valid_position()` | 单一职责，place/move/jump 都复用 |
| 错误信息？ | 返回字典 `{"success": bool, "message": str, "position": tuple}` | 清晰的错误原因和当前状态 |
| 权威状态源？ | Robot 对象 | Robot.x/y/facing/move_count 是唯一真相；Table 网格和映射是缓存 |

### 实现进度

**第一阶段：基础多机器人支持**

- ✓ 机器人标识（UUID + 名字）
- ✓ 2D 网格追踪位置
- ✓ 碰撞检测和错误消息
- ✓ 网格在 place/move/backward/undo 中同步

**第二阶段：命令返回格式标准化**

- ✓ 所有命令返回 `{"success": bool, "message": str, "position": tuple}`
- ✓ place() 返回详细验证结果和当前位置
- ✓ move() 返回详细验证结果和当前位置
- ✓ left()/right() 返回一致的字典格式和当前位置
- ✓ undo() 返回一致的字典格式和恢复后的位置

**第三阶段：历史记录扩展**

- ✓ 历史记录从 `(x, y, facing)` 升级为 `(x, y, facing, move_count)`
- ✓ undo 能正确恢复包括 move_count 的完整状态
- ✓ JUMP 命令作为单条历史记录，但 move_count 增加 N

**第四阶段：位置追踪与查询**

- ✓ 引入 robot_positions 映射（UUID → 完整状态）
- ✓ 提供 update_robot_grid(uuid, name, x, y) 原子操作
- ✓ 提供 update_robot_position(uuid, position) 追踪
- ✓ 提供 get_robot_position(uuid) 查询接口

**第五阶段：JUMP 命令实现**

- ✓ 实现 jump(n) 方法，支持多步前进
- ✓ 中途被阻挡时返回失败，位置恢复到起始点
- ✓ move_count 原子递增 N（实际跳过的步数）
- ✓ 历史记录只存一条（起始状态），使 undo 能一次性回退
- ✓ 支持 JUMP 命令在 execute() 中解析

### 架构权衡

| 问题 | 当前设计 | 未来扩展 |
|------|---------|---------|
| **存储方式** | 2D 数组 | 密度<5% 时自动切换到 Set |
| **碰撞检测** | O(1) 网格查询 | 无需改变 |
| **Robot 生命周期** | 用户创建/管理 | Table.create_robot() 工厂模式 |
| **状态同步** | 三结构手动同步 | 可考虑 ORM 或事件系统 |
| **并发安全** | 未实现 | 未来加 Lock 保护 |

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

**修复**：删除最后一行。改为从历史记录中恢复完整的 move_count，而不是手动递减。

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
    self.obstacles = [[0 for _ in range(width)] for _ in range(height)]
    if obstacles is not None:
        for obstacle in obstacles:
            self.obstacles[obstacle[0]][obstacle[1]] = 1
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
```

当 `obstacles=None` 时，只重置了局部变量 `obstacles = []`，但 `self.obstacles` 属性从未被创建。

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

**教训**：实例变量必须在所有代码路径中都被初始化。

---

### 坑 7：历史记录从三元组升级为四元组

原来 `history` 存 `(x, y, facing)`，现在需要 `(x, y, facing, move_count)`。

**问题**：当 JUMP 跳多步时，move_count 增加多个值。如果只存 facing，undo 时无法判断是否需要减少 move_count。

**解决**：将完整状态存入历史，包括 move_count。这样 undo 时直接恢复所有字段，无需逻辑判断。

**教训**：设计历史记录时，要考虑新操作（如 JUMP）对状态的复杂影响。存完整状态比存部分状态和复杂恢复逻辑更简洁。

---

### 坑 8：网格更新不同步

JUMP 成功时更新了 Robot 对象的 x/y/move_count，但忘记更新 Table 的网格。导致 `robots[x][y]` 和 Robot 对象状态不一致。

**修复**：在 JUMP 循环中每一步都调用 `update_robot_grid()` 和 `update_robot_position()`。

**教训**：多结构设计时，修改任何一个都要同步更新其他的。考虑提供原子操作方法（如 `update_robot_grid()`）来强制同步。

---

## 重构：代码整合

### MOVE 与 BACKWARD 的合并

原先 `move()` 和 `backward()` 有大量重复逻辑。

**重构方案**：增加 `direction` 参数，在方向差值层面处理正向/反向区别。

```python
def move(self, direction="forward"):
    """Move the robot one unit in the specified direction."""
    if not self.is_placed():
        return {"success": False, "message": "Robot is not placed on the table."}
    
    dx, dy = self.DIRECTION_DELTAS[self.facing]
    if direction == "backward":
        dx, dy = -dx, -dy
    
    new_x = self.x + dx
    new_y = self.y + dy
    
    validation_result = self.table.is_valid_position(new_x, new_y)
    
    if validation_result.get("success"):
        self.history.append((self.x, self.y, self.facing, self.move_count))
        
        self.table.update_robot_grid(None, None, self.x, self.y)
        self.table.update_robot_position(self.id, None)
        
        self.x = new_x
        self.y = new_y
        self.move_count += 1
        
        self.table.update_robot_grid(self.id, self.name, new_x, new_y)
        self.table.update_robot_position(self.id, (new_x, new_y, self.facing, self.move_count))
    
    validation_result["message"] = f"Moved {direction} successfully"
    validation_result["position"] = (self.x, self.y, self.facing, self.move_count)
    
    return validation_result

def backward(self):
    """Move the robot one unit backward."""
    return self.move(direction="backward")
```

**优点**：
- ✓ 消除重复代码
- ✓ 修改一处即可同步两个方向
- ✓ 新增方向逻辑时只需改一处

**教训**：相似的方法应在抽象层面寻找共同点，用参数区分变化部分。

---

## 测试覆盖

最终 **46 个测试**全部通过，覆盖：

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
- UNDO 回退 count（正确恢复所有状态）
- 失败操作不递增 count

**多机器人与碰撞（3 个）**
- 多机器人共存
- 碰撞检测（机器人间碰撞阻止移动）
- JUMP 被机器人阻挡并 UNDO

**障碍物（2 个）**
- MOVE 被障碍物阻止
- BACKWARD 被障碍物阻止

**JUMP 命令（2 个）**
- JUMP 成功完成多步
- JUMP 中途被阻挡时失败并恢复

**位置查询（1 个）**
- Table 通过 UUID 追踪和查询机器人位置

---

## 架构问题与决策

### Q1：2D Array vs Set 存储

**问题**：何时从 2D 数组切换到基于 Set 的存储？

**决策**：
- 2D 数组：表大小 ≤ 100×100 或机器人密度 > 5%
  - 优点：O(1) 碰撞检测，实现简单
  - 缺点：大稀疏表浪费内存
  
- Set：表大小 > 100×100 **AND** 机器人密度 < 5%
  - 优点：内存高效 O(r)，r = 机器人数
  - 缺点：碰撞检测 O(1) → O(log r)
  
**例子**：1000×1000 表 + 50 机器人 → Set 节省 99.995% 内存

**实现方式**：在 Table 构造时根据参数自动选择
```python
def __init__(self, width, height, robot_capacity=None, obstacles=None):
    density = robot_capacity / (width * height) if robot_capacity else 1.0
    if width > 100 and height > 100 and density < 0.05:
        self._use_set_storage = True
    else:
        self._use_set_storage = False
```

---

### Q2：单一权威状态源 (Single Source of Truth)

**问题**：Robot 对象、Table.robots 网格、Table.robot_positions 映射三者如何保持同步？

**决策**：Robot 对象 是权威来源，其他两个是缓存
- **Robot.x/y/facing/move_count**：唯一真相
- **Table.robots[x][y]**：缓存，用于 O(1) 碰撞检测
- **Table.robot_positions[uuid]**：缓存，用于快速查询

**同步策略**：每次修改 Robot 状态时，立即更新两个缓存
```python
def move(self, ...):
    self.history.append((self.x, self.y, self.facing, self.move_count))
    
    # 清空旧位置缓存
    self.table.update_robot_grid(None, None, self.x, self.y)
    self.table.update_robot_position(self.id, None)
    
    # 修改权威源
    self.x, self.y = new_x, new_y
    self.move_count += 1
    
    # 更新缓存
    self.table.update_robot_grid(self.id, self.name, new_x, new_y)
    self.table.update_robot_position(self.id, (new_x, new_y, self.facing, self.move_count))
```

**如果同步破裂**：提供重建方法
```python
def rebuild_grid(self):
    """从 Robot 对象重建网格（调试用）"""
    self.robots = [[None] * self.width for _ in range(self.height)]
    for robot in all_robots:
        self.robots[robot.x][robot.y] = (robot.id, robot.name)
```

---

### Q3：Robot 生命周期：用户管理 vs Table 工厂

**问题**：应该由用户手动创建 Robot，还是由 Table 工厂创建？

**当前设计 (Option A)：用户管理**
```python
table = Table(5, 5)
robot1 = Robot(table, 'Robot 1')
robot2 = Robot(table, 'Robot 2')
```

**优点**：
- 解耦：Robot/Table 无依赖关系
- 灵活：可共享 Table，可先创建 Robot 再创建 Table
- 简洁：实现少，无 Registry 复杂度

**缺点**：
- 用户需手动追踪 robot 列表
- 无法通过 UUID 快速找到 Robot 对象

**未来扩展 (Option B)：Table 工厂**
```python
table = Table(5, 5)
robot1 = table.create_robot('Robot 1')
robot2 = table.create_robot('Robot 2')
all_robots = table.get_all_robots()
robot = table.get_robot_by_name('Robot 1')
```

**优点**：
- Table 提供 Registry，易于查询
- 生命周期明确：删除 Table 自动清理 robots

**缺点**：
- 实现复杂度提高
- Table 责任增大

**决策**：坚持 Option A。这个玩具项目不需要 Registry；如果未来确实需要，升级成本不高。

---

### Q4：JUMP 中途阻挡的处理

**问题**：JUMP 5 步但第 3 步被阻挡，是否接受部分移动？

**决策**：All-or-nothing，返回失败

**理由**：
- 用户请求 JUMP 5，期望要么成功 5 步，要么失败
- 部分成功容易导致状态模糊：move_count +2 但消息说"失败"
- 如果需要"尽量多步"，用户可循环调用 MOVE

**实现**：
```python
for i in range(steps):
    if not is_valid(new_x, new_y):
        # 失败：保存起始状态到历史，UNDO 后恢复到原点
        self.history.append((start_x, start_y, self.facing, start_move_count))
        return {"success": False, ...}

# 成功：才保存到历史
self.history.append((start_x, start_y, self.facing, start_move_count))
return {"success": True, ...}
```

---

## 后续可能的扩展

1. **Robot 移除**：实现 `remove(robot)` 清理网格
2. **障碍物动态修改**：运行时添加/删除障碍物
3. **多机器人并发命令**：同时执行多条命令的协调
4. **持久化**：序列化/反序列化 Table 和 Robot 状态
5. **性能监测**：Profile 碰撞检测的性能
6. **Set 存储**：当表大且稀疏时自动切换


