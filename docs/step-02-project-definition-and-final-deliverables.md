# Step 02: Project Definition And Final Deliverables

> 目标：把这个项目到底是什么、它要实现什么、最后会产出什么，定义成一份不会和仓库现有文档冲突的共识稿。

## 1. Project Definition

`project-launch-blueprint` 是一套面向前端项目启动的分层方法论，也是一个可以被打包成 skill 的模板工程。

它的核心任务不是写单一业务功能，而是定义一条完整的工程流水线：

- 从原始 `analysis/` 开始
- 逐层收敛出业务能力、领域模型、状态机、API 契约、设计系统和垂直切片
- 用质量门禁确认这些产物可以进入实现
- 再由 `implementation` 把已验证产物翻译成真实原型代码
- 最后把这套方法和模板发布成可安装的 skill bundle

## 2. What It Is Building

这个项目最终在构建两类东西。

### 2.1 蓝图本体

蓝图本体是这套方法论在当前仓库里的完整定义，包括：

- 阶段顺序
- 输入输出规则
- 验证规则
- 回退机制
- CLI 和状态模型
- 发布约束

### 2.2 可复用 skill 模板

模板是这套方法论可以被安装到别的 Codex 环境中的发行形态。

它要让用户安装后能够：

- 接收项目输入
- 生成中间产物
- 进入 `implementation`
- 落成真实原型代码
- 继续提交到 GitHub 并可复用

## 3. What `implementation` Is Responsible For

`implementation` 是这个项目里最接近交付的一层。

它不再做高层抽象，而是把已经验证的产物映射到仓库里的真实文件和目录。

根据现有文档，它会产出：

- `implementation plan`
- `goal registry`
- `code scaffold map`
- `directory tree`
- `bootstrap manifest`
- `task batch list`
- `branch / commit plan`
- `verification plan`
- `implementation handoff report`

它的落点通常包括：

- `schemas`
- `api` / `repository`
- `service`
- `hook`
- `component`
- `page`
- `mock`
- `tests`

换句话说，`implementation` 的职责就是把前面阶段的中间产物，真正落实成可运行、可提交、可继续迭代的原型代码。

## 4. What Counts As Final Deliverables

这个项目的最终交付不是单个文件，而是一组可追踪的资产。

### 4.1 For This Repository

当前仓库的最终交付是：

- 这套 blueprint 文档
- CLI 与状态规范
- 模板复制协议
- 实现桥接协议
- 发布协议

### 4.2 For A User Project

当用户安装这个 skill 并开始使用时，最终交付是：

- 用户项目中的阶段产物
- 用户项目中的实现桥接结果
- 用户项目中的原型代码
- 用户项目中可被 Git 追踪的正式文件

### 4.3 For Skill Distribution

当这套项目被发布成 skill 时，最终交付是：

- 可安装的 skill bundle
- 可复制的模板结构
- 可验证的阶段契约
- 可继续推进到代码生成的实现层

## 5. What Must Be Preserved In Git

需要进入 Git 的，不只是手写代码，也包括 `implementation` 生成的正式代码树。

应该被追踪的内容包括：

- 原型代码
- 页面和组件
- 服务和仓储层
- schema 和类型
- 测试文件
- 必要的构建或配置文件
- 项目状态和审计记录中需要持久化的部分

不应该进入 Git 的，只能是临时执行过程文件，例如：

- 一次性缓存
- scratch 文件
- 生成中间态的临时草稿

## 6. Project Boundary Rule

这个项目的边界可以概括为一句话：

> 它负责定义一套从分析到原型代码再到 skill 发布的完整协议，而不是某个单独功能的业务实现。

如果要继续往下拆，下一步应该定义：

- 用户项目里正式代码目录的命名规则
- `implementation` 输出和 Git 提交之间的对应关系
- 哪些产物属于长期资产，哪些产物属于临时执行物

