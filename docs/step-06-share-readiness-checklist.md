# Step 06: Share Readiness Checklist

> 目标：在对外分享仓库之前，先确认仓库看起来像一个稳定的 skill 项目，而不是一个还没整理完的本机开发现场。

## 1. What Should Stay

分享前应保留：

- `SKILL.md`
- `agents/openai.yaml`
- `README.md`
- `docs/`
- 业务和方法论文档
- 需要随仓库一起协作的源码和测试

## 2. What Should Not Be Shared As Product Shape

不要把这些内容当成仓库的产品形态去展示：

- `.venv/`
- `__pycache__/`
- `.pytest_cache/`
- 其他本机缓存目录
- 敏感信息

这些可以在本地存在，但不应该作为对外分享的内容重点。

## 3. Share Readiness Checklist

分享前检查：

- 仓库里是否有 skill 入口文件
- README 是否说明了这个仓库的用途
- docs 是否能指导新使用者入门
- 本地缓存是否被正确忽略
- 仓库是否没有暴露敏感信息
- 当前内容是否足够稳定，适合别人直接进入阅读或安装流程

## 4. Internal Rule

以后我们提到“这个仓库已经可以分享”，默认含义是：

- 它有清楚的 skill 入口
- 它有清楚的 README
- 它的 docs 能帮助使用者理解安装和初始化
- 它没有把本机临时开发痕迹当成产品内容
