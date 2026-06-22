# Template Spec

> 这份规范定义如何把 `project-launch-blueprint` 复制到任何新项目里。  
> 它不是新的业务阶段，而是蓝图的复制协议。
> 所有示例路径都以 `project-launch-blueprint/` 或新项目根目录为基准，必须使用相对路径。

## 1. Purpose

把当前蓝图抽象成一个可复用模板，保证新项目复制时：

- 目录结构一致
- 方法论一致
- 验证规则一致
- 输出格式一致
- 只是输入来源、业务命名和少量实现细节不同

## 2. Non-Negotiable Invariants

1. 先验证，再抽象。
2. 主输入优先，辅助证据只能用于核验、补漏和反例攻击。
3. 每层只做一件事。
4. 每层都必须有 `index.md`、`method.md`、`validation-rules.md`、`output-schema.md`、`prompt-templates.md`、`example-output.md`、`checklist.md`。
5. 每层输出都必须可回退。
6. 每层都必须有正向测试和负向测试。
7. 每层都必须定义清楚“什么不能进入这一层”。

## 3. Copy Model

新项目复制时，建议按以下顺序进行：

1. 复制目录骨架。
2. 复制 `index.md` 并替换项目名、阶段名和输入输出来源。
3. 复制 `cli-architecture.md`，保留命令树、状态模型和发布规则。
4. 复制 `workflow-state.md`，保留 revision-aware 状态机和回退规则。
5. 复制 `command-reference.md`，保留命令树和状态约束。
6. 复制 `method.md`，保留 workflow 骨架，只替换业务语义。
7. 复制 `validation-rules.md`，保留验证顺序和反例结构。
8. 复制 `output-schema.md`，保留字段结构，只替换命名。
9. 复制 `prompt-templates.md`，保留正向/负向审查提问。
10. 复制 `example-output.md`，保留占位模板。
11. 复制 `checklist.md`，保留完成判定。

## 4. What Can Change

允许变化的只有：

- 项目名
- 阶段名
- 主输入的具体文件名
- 输出对象的具体业务命名
- 某些字段是否适用
- 某层的辅助证据来源

不允许变化的有：

- 层级顺序
- 输入优先级
- 验证顺序
- 正向/负向测试要求
- 回退机制
- “每层只做一件事”的原则

## 5. How To Adapt

如果新项目的领域不同，优先做这三种适配：

1. 改输入源，不改方法骨架。
2. 改输出命名，不改输出语义。
3. 改例子内容，不改验证结构。

如果某一层完全不适用，删除该层前先确认：

- 它是否真的没有业务价值
- 删除后上游语义是否还能被下游完整承接
- 是否需要把它的职责并入相邻层

## 6. Anti-Patterns

- 只复制目录，不复制方法论。
- 只改文件名，不改语义边界。
- 把辅助证据提升为主输入。
- 把一层做成多层。
- 把 validation 当成可选项。
- 把 example-output 当成装饰文件。
- 让某层绕过回退点。

## 7. New Project Bootstrap

如果要从零创建一个新项目，推荐使用以下顺序：

1. 先复制 `template-spec.md`
2. 再复制 `cli-architecture.md`
3. 再复制 `workflow-state.md`
4. 再按模板创建总入口 `index.md`
5. 然后生成第一层目录
6. 再逐层生成后续目录
7. 最后把样板替换成项目专属内容

## 8. Review Gate

一个新项目只有在以下问题都能回答时，才算真正复制成功：

1. 这一层的主输入是什么？
2. 这一层的辅助证据是什么？
3. 这一层输出什么？
4. 这一层验证什么？
5. 这一层失败后回退到哪里？
6. 这一层为什么只做这些事？

## 9. Distribution Bundle

如果把这套方法论作为一个可复用发行包交给别的项目，最小交付物应该是：

- `README.md`
- `index.md`
- `template-spec.md`
- `cli-architecture.md`
- `workflow-state.md`
- `command-reference.md`
- 各阶段目录的 `index.md`
- 各阶段目录的 `method.md`
- 各阶段目录的 `validation-rules.md`
- 各阶段目录的 `output-schema.md`
- 各阶段目录的 `prompt-templates.md`
- 各阶段目录的 `example-output.md`
- 各阶段目录的 `checklist.md`
- `implementation/` 下的桥接文件

同时，对接方还要预留两个落点：

- `project space`，用于保存正式代码、测试、配置、必要状态记录和可追踪的中间产物
- `temporary execution space`，用于保存本机短暂缓存、敏感信息和可完全重建的噪音文件

其中 `implementation` 的输出和过程产物都应默认进入 `project space`，不能只停在临时执行区。

如果对方要直接开工，还应额外带上：

- 一个项目专属的原始 `analysis/` 目录样例
- 一个 `.project-launch-blueprint/projections/` 投影样例
- 一个最小可跑通的 `example-output`
- 一份阶段顺序说明
- 一份回退策略说明

## 10. Starter Snapshot

新项目的最小启动快照建议长这样：

1. `analysis/`
2. `.project-launch-blueprint/projections/`
3. `project-launch-blueprint/`
4. `project-launch-blueprint/template-spec.md`
5. `project-launch-blueprint/cli-architecture.md`
6. `project-launch-blueprint/workflow-state.md`
7. `project-launch-blueprint/command-reference.md`
8. `project-launch-blueprint/index.md`
9. `project-launch-blueprint/discovery/`
10. `project-launch-blueprint/domain-model/`
11. `project-launch-blueprint/state-machine/`
12. `project-launch-blueprint/api-contract/`
13. `project-launch-blueprint/design-system/`
14. `project-launch-blueprint/vertical-slice/`
15. `project-launch-blueprint/quality-gates/`
16. `project-launch-blueprint/implementation/`
17. 后续阶段目录按需补齐
18. 用户项目的正式代码树
19. 用户项目的过程产物目录
20. 用户项目的临时执行目录

## 11. Recommended Entry Order

如果别人拿到这套发行包，推荐阅读顺序是：

1. `README.md`
2. `index.md`
3. `cli-architecture.md`
4. `workflow-state.md`
5. `command-reference.md`
6. `template-spec.md`
7. 各阶段目录的 `index.md`
8. 各阶段目录的 `method.md`
9. 各阶段目录的 `example-output.md`
10. 各阶段目录的 `validation-rules.md`
11. 各阶段目录的 `output-schema.md`
12. 各阶段目录的 `prompt-templates.md`
13. 各阶段目录的 `checklist.md`
14. `implementation/` 下的桥接文件
