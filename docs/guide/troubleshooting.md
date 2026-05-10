# 故障排查

## 命令没有输出或像卡住

先看最新 run：

```bash
novi output latest
novi trace latest
```

如果是 `ingest` 或 DeepAgents 调用，模型响应可能需要等待。CLI 会打印加载 workflow、创建 run、等待模型、归档响应、创建 contribution 等阶段。

## API key 看起来没生效

检查当前目录是不是同一个 workspace：

```bash
pwd
novi status
novi doctor model
```

`doctor model` 只显示 key 是否设置，不显示 key 内容。

## SOCKS proxy 报错

如果环境使用 SOCKS proxy，需要 deepagents extra 中包含 socks 支持。开发期运行：

```bash
uv sync --extra all
```

## 找不到 contribution

通常是复制了带 `.yaml` 后缀的文件名，或者变量指向旧 id。优先用更高层命令：

```bash
novi process
novi accept latest
novi accept all
```

需要列出：

```bash
novi contribution list
```

## Task 无法继续

如果提示 pending review contributions，先处理 review gate：

```bash
novi review --task task_... --check --agent
novi accept --reviewed --task task_...
novi task continue task_...
```

## DeepAgents 虚拟文件和 `.novi/` 路径

DeepAgents working files 是虚拟执行空间。模型不应直接读取 `.novi/...` 路径作为真实文件；Novi 会把导入文档、库上下文、目标文档和 workflow 信息放进 prompt，作为权威输入。

