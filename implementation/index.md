# Implementation Bridge

> 这不是新的业务阶段。  
> 它是把已经通过质量门禁的蓝图产物，翻译成真实代码与交付任务的落地桥。  
> 这套文件同时也是一份 `Codex goal` 驱动的标准实现模板，专门用于一键生成原型代码。

## 1. What This Is

这组文件负责把前面各层的“可验证语义”转换成“可执行代码计划”，让新项目可以直接按同一套规则落到仓库结构、模块边界、测试和发布流程里。

implementation 也会冻结已批准的上游输入 inventory / coverage matrix，确保实现计划能逐项对账到每个输入来源。

它的目标不是写散点代码，而是把一个明确的 `goal` 翻译成：

- implementation plan
- goal registry
- code scaffold map
- task batch list
- directory tree
- bootstrap manifest
- branch / commit plan
- verification plan
- implementation handoff report

## 2. When To Use

在以下场景使用这组文件：

- 前面的 `quality-gates` 已经通过，准备开始正式编码
- 需要把蓝图翻译成目录、文件、模块和任务
- 需要让 LLM 直接参与 scaffold、实现和验证
- 需要把文档产物变成可追踪的工程动作
- 需要用一个清晰的 `goal` 直接驱动原型代码生成

## 3. What It Consumes

- `discovery capability map`
- `domain model map`
- `state machine map`
- `api contract map`
- `design system map`
- `vertical slice map`
- `quality-gates validation report`
- `technical-solution.md`
- frozen upstream input inventory

## 4. What It Produces

- implementation plan
- code scaffold map
- task batch list
- branch / commit plan
- verification plan
- implementation handoff report

## 4.1 Standard Template Bundle

这层的标准模板应当至少包含：

- `method.md`
- `artifact-map.md`
- `bootstrap.md`
- `commands.md`
- `validation-rules.md`
- `output-schema.md`
- `prompt-templates.md`
- `example-output.md`
- `checklist.md`
- `../cli-architecture.md`
- `../workflow-state.md`
- `../command-reference.md`

## 5. Reading Order

1. 先读 `../cli-architecture.md`
2. 再读 `../workflow-state.md`
3. 再读 `../command-reference.md`
4. 再读 `method.md`
5. 再读 `artifact-map.md`
6. 然后读 `bootstrap.md`
7. 再读 `commands.md`
8. 再读 `validation-rules.md`
9. 再读 `output-schema.md`
10. 再读 `prompt-templates.md`
11. 再读 `example-output.md`
12. 最后读 `checklist.md`

## 6. Design Rule

这组文件只负责翻译，不负责重新定义业务、状态、契约或视觉语言。
