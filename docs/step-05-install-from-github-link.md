# Step 05: Install From GitHub Link

> 目标：把“别人通过 GitHub 链接安装这个 skill”这件事讲清楚，供后续对话和操作时直接引用。

## 1. What The Link Is For

GitHub 链接的作用有两层：

- 作为协作仓库入口，方便别人查看、克隆、继续开发
- 作为 skill 载体，让 Codex 识别这个仓库中的 skill 入口并完成安装

前者是现在就成立的，后者依赖 Codex 的 GitHub 导入/安装流程和仓库内的 skill 入口文件。

## 2. What Must Exist In The Repo

仓库里至少要有这些内容，Codex 才能把它当成 skill 来读：

- `SKILL.md`
- `agents/openai.yaml`
- `README.md`
- `docs/step-04-user-manual.md`
- `docs/step-03-project-space-and-artifact-classes.md`

## 3. Suggested User Flow

对于协作者，建议的最短路径是：

1. 打开共享的 GitHub 链接
2. 在 Codex 中把这个仓库作为 skill 导入或安装
3. 先读 README
4. 再读用户手册
5. 在目标项目里执行 `plb init`
6. 再用 `plb status` 确认初始化状态

## 4. What To Tell Collaborators

对外介绍时只需要说清楚两件事：

- 这个仓库可以作为 skill 被安装到 Codex
- 安装后先执行初始化，再开始进入阶段推进

不要把内部的过程产物、状态设计、验证细节一开始就塞给第一次接触的人。

## 5. Internal Note

在后续对话里，如果我们提到“通过 GitHub 链接安装这个 skill”，默认就是指：

- 仓库已经具备 `SKILL.md`
- 仓库已经具备 skill 元数据
- 使用者可以通过分享链接进入并安装

如果后面要补更具体的安装按钮、界面文案或操作截图，再单独加一页说明。
