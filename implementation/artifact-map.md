# Artifact Map

> 这份表专门回答：蓝图里的每个产物，最后应该落到代码仓库的哪里。

## 1. Blueprint to Code Mapping

| Blueprint Artifact | Code Purpose | Typical Location | Notes |
| --- | --- | --- | --- |
| `Codex goal` | 冻结本次原型生成目标 | 任务说明、实现计划、分支标题 | 先决定这次要生成什么 |
| `discovery capability map` | 定义功能范围和能力边界 | `features/`、路由清单、任务拆分 | 先决定做什么，再决定怎么做 |
| `domain model map` | 定义领域对象、边界和责任 | `types/`、`services/`、`repositories/` | 不直接翻译成页面组件 |
| `state machine map` | 定义流程阶段和状态转移 | `hooks/`、流程控制器、状态枚举 | 约束页面和 API 的行为 |
| `api contract map` | 定义请求、响应、错误和幂等 | `api/`、`repositories/`、`schemas/` | 作为边界契约使用 |
| `design system map` | 定义 token、组件和状态样式 | `components/`、样式变量、Storybook | 用来统一 UI 语言 |
| `vertical slice map` | 定义单能力完整闭环 | `app/`、`features/`、`hooks/`、`services/`、`repositories/`、`mocks/` | 这是最接近真实实现的骨架 |
| `quality-gates validation report` | 决定是否允许合并/发布 | `tests/`、CI、release checklist | 不通过就不进入发版 |
| `technical-solution.md` | 约束技术栈、目录和运行方式 | 仓库级技术说明 | 作为工程约束，不作为业务语义来源 |

## 2. What Not To Map

以下内容不要直接从蓝图里“硬翻译”进代码：

- 页面标题
- 按钮文案
- 临时视觉风格
- 手工操作步骤
- 没有通过验证的推断

## 3. Mapping Rules

- 一个 capability 最少对应一个可实现的功能切片
- 一个 state machine 最少对应一个可执行的状态流转实现
- 一个 API contract 最少对应一个 repository 或 endpoint 入口
- 一个 design system 产物最少对应一个可复用组件或 token
- 一个 quality gate 最少对应一个测试或发布检查项

## 4. Mapping Strategy

先做最小映射，再逐步展开：

1. 先把 `Codex goal` 映射成实现范围
2. 再把已通过验证的产物映射到目录
3. 再把目录映射到文件
4. 再把文件映射到函数、组件和测试
5. 最后把文件映射到提交和发布动作
