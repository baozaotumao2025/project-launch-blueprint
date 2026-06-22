# Step 03: Project Space And Artifact Classes

> 目标：把用户安装 skill 之后，项目目录里哪些东西属于正式资产、哪些属于临时执行物、哪些必须随 `implementation` 落到代码树里，定义清楚。

## 1. Core Split

用户项目里至少要分成三类空间：

### 1.1 Skill Space

这是安装在 Codex 全局里的能力包。

它负责：

- 提供模板、规范和命令
- 读取用户项目状态
- 生成或推进项目产物

它本身不应该被当作用户项目的业务代码目录。

### 1.2 Project Space

这是用户当前仓库里的正式空间。

它负责承载：

- blueprint 文档
- 阶段产物
- `implementation` 生成的原型代码
- 测试
- 必要的配置
- 状态和审计信息

只要是用户最终要继续开发、要提交、要发布的内容，都应该在这里。

### 1.3 Temporary Execution Space

这是执行过程里的临时空间。

它负责承载：

- scratch
- cache
- 临时 review packet
- 一次性导出结果
- 中间计算结果

这类文件在本项目里默认也属于项目历史的一部分，应当保留在仓库中，除非它们只是本机短暂缓存、敏感信息或可完全重建的噪音文件。

## 2. Artifact Classes

为了避免混淆，我们把所有产物分成四类。

### 2.1 Permanent Blueprint Artifacts

这类产物是方法论本体的一部分，通常应该长期保留。

典型包括：

- `README.md`
- `index.md`
- `cli-architecture.md`
- `workflow-state.md`
- `command-reference.md`
- `template-spec.md`
- 各阶段目录的契约文档

### 2.2 Generated Project Artifacts

这类产物是 skill 在用户项目里生成的，但它们是正式资产。

典型包括：

- `implementation` 生成的代码骨架
- `schema`
- `api/repository`
- `service`
- `hook`
- `component`
- `page`
- `mock`
- `tests`

这些内容必须进入用户仓库的正式代码树，并由 Git 追踪。

这里提到的 `src/`、`tests/` 只是目录示例，不特指当前这个 skill 仓库本身，也不意味着用户项目一定只能用这两个名字。
如果某个用户项目的正式代码树叫 `app/`、`features/`、`modules/` 或其他名字，也应该按同样规则纳入 `project space`。

### 2.3 Persistent Runtime Artifacts

这类产物不一定是代码，但需要长期保留，便于追踪状态和审计。

典型包括：

- `.project-launch-blueprint/state.db`
- `.project-launch-blueprint/audits/`
- `.project-launch-blueprint/exports/`
- `.project-launch-blueprint/logs/`
- `.project-launch-blueprint/backups/`

这些通常放在隐藏目录下，但它们不是纯临时缓存。

### 2.4 Disposable Runtime Artifacts

这类产物只服务于单次执行。

典型包括：

- 临时 diff
- 中间草稿
- 一次性 reviewer packet
- 调试日志
- 本地 scratch 文件

这类内容应该尽量隔离在临时目录。

在本项目里，默认策略是“能帮助别人接手、复盘、继续推进的过程产物都进 Git”。
真正不进入 Git 的，只保留下面几类：

- 本机短暂缓存
- 可重新生成的噪音文件
- 密钥、令牌和其他敏感信息
- 第三方依赖缓存和大体积构建缓存

## 3. Directory Rule

项目目录里应该遵守一个简单规则：

- `永久方法论` 放在文档目录
- `正式实现产物` 放在代码目录
- `持久运行记录` 放在隐藏状态目录
- `一次性执行物` 放在临时目录

这样可以避免把原型代码、状态记录和临时草稿混在一起。

## 4. `implementation` 落点

`implementation` 生成的东西不能停留在“计划层”。

它必须落成用户项目里的正式文件，例如：

- 目录骨架
- 页面组件
- 业务服务
- 数据访问层
- mock
- 测试
- 配置

这也是为什么 `implementation` 不是“可选运行态”，而是整个项目里把蓝图翻译成代码的最后桥段。

## 5. Git Rule

是否进入 Git，按“是不是项目可追踪资产”来判断，不按“是不是最终代码”来判断。

### 5.1 Should Commit

应该提交的内容：

- 原型代码
- 文档
- 测试
- 配置
- 必要的状态和审计记录
- 阶段中间产物
- review packet 的持久版本
- 生成计划和执行记录
- 可帮助接手的过程产物

### 5.2 Should Not Commit

不应该提交的内容：

- 本机短暂缓存
- 密钥、令牌和其他敏感信息
- 第三方依赖缓存
- 可完全重建的噪音文件
- 大体积二进制构建缓存

### 5.3 Borderline Case

如果一个生成物既是临时生成的，又会被后续步骤持续读取，或者对接手者有解释价值，那它应当被定义为“可追踪资产”，默认进入 Git。

## 6. Validation Criteria

这一步通过时，必须满足：

- 能把用户项目里的内容分成正式资产和临时执行物
- 能说明 `implementation` 的落点是正式代码树
- 能说明哪些目录要进 Git，哪些不应该进 Git
- 能把状态目录和代码目录分开
- 能避免把原型代码放进 scratch 区

## 7. Next Step

下一步应该继续定义：

- `implementation` 的正式代码目录建议结构
- 每类产物对应的默认文件位置
- 从 `goal registry` 到实际文件的映射顺序
