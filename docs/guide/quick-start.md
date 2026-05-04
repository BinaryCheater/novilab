# 快速开始

## 1. 初始化

在你的项目目录中运行：

```bash
novi init
```

检查状态：

```bash
novi status
```

## 2. 配置模型

SiliconFlow 示例：

```bash
novi configure model siliconflow \
  --model "deepseek-ai/DeepSeek-V4-Flash" \
  --api-key "YOUR_API_KEY"
```

通用 OpenAI-compatible provider：

```bash
novi configure model openai-chat \
  --model "MODEL_NAME" \
  --base-url "https://provider.example.com/v1" \
  --api-key "YOUR_API_KEY"
```

检查配置：

```bash
novi doctor model
```

## 3. 跑一个有产物的 research loop

```bash
novi task "围绕接触先验整理已有知识，形成一版研究假设和下一步行动" --steps 2
```

如果目标是快速完成 topic、证据、实验迭代和物理先验候选的闭环，使用：

```bash
novi task "围绕接触先验分析材料，设计下一轮最小实验，并抽取隐含物理先验" \
  --workflow research-iteration \
  --kernel deepagents \
  --rounds 1
```

查看输出：

```bash
novi output latest
novi trace latest
novi artifact list
```

继续推进：

```bash
novi task list
novi task continue task_... --rounds 1
```

## 4. 导入文档

```bash
novi ingest notes.md --hint "和接触先验相关，整理进知识库"
```

挂到已有 task：

```bash
novi ingest notes.md --task task_... --hint "作为这个研究任务的背景材料"
```

## 5. Review 和接受变更

如果产生 proposal：

```bash
novi review --check --agent
novi accept --reviewed
```

按 task 过滤：

```bash
novi review --task task_... --check --agent
novi accept --reviewed --task task_...
```

## 开发源码运行

在仓库内运行源码版本：

```bash
uv run --extra dev --extra deepagents novi --help
uv run --extra dev --extra deepagents novi task "研究目标" \
  --workflow research-iteration \
  --rounds 1
```
