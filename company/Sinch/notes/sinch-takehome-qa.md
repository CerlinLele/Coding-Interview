# Sinch Take-home Q&A

## 1. 这份 coding test 怎么理解

- 这是一个 Spring Boot 的 SMS routing service。
- 核心是 3 个接口：
  - `POST /messages`
  - `GET /messages/{id}`
  - `POST /optout/{phoneNumber}`
- 重点不在算法，而在：
  - 分层是否清晰
  - 状态流转是否合理
  - 错误处理是否完整
  - 测试是否覆盖关键场景

## 2. 这题算不算下一轮 live AI coding

- 可以理解成 `take-home + live extension`。
- 不是纯现场从零写，而是先交一个可运行方案，面试时再基于这份代码继续扩展。
- 面试里大概率会看：
  - 你是否真的理解自己写的代码
  - 能否快速加新规则
  - 是否能解释设计取舍

## 3. 能不能用 AI

- 可以，而且题目原文是明确鼓励使用 AI 工具。
- 适合让 AI 帮忙的部分：
  - 搭项目骨架
  - 写样板代码
  - 补测试
  - 整理 README
- 但你需要自己真正理解：
  - carrier routing
  - opt-out 影响
  - status flow
  - 以后怎么扩展

## 4. 这个项目起什么名字比较好

- 推荐：`sinch-sms-router`
- 原因：
  - 直接对应题目
  - 专业、清楚
  - 适合作为 Git repo 名

## 5. Maven vs Gradle

- 推荐：`Maven`
- 原因：
  - `start.spring.io` 支持自然
  - 评审者更容易快速读懂
  - 配置更少，适合 2-3 小时内完成
  - 这题的重点不在构建工具

## 6. package 选什么，jar 还是 war

- 推荐：`jar`
- 原因：
  - Spring Boot 默认方式
  - 内嵌容器更简单
  - 适合小型服务
  - 不需要传统外部容器部署

## 7. 目前最稳的组合

- 项目名：`sinch-sms-router`
- 构建工具：`Maven`
- packaging：`jar`
- 交付重点：
  - 代码可读
  - 单元测试
  - README 里写清 assumptions

