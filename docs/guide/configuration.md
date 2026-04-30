# 配置说明

## 模型配置

Novi 当前支持 OpenAI-compatible chat-completions provider。配置写入 `.novi/novi.yaml`。

### SiliconFlow

```bash
novi configure model siliconflow \
  --model "deepseek-ai/DeepSeek-V4-Flash" \
  --api-key "YOUR_API_KEY"
```

默认 base URL：

```text
https://api.siliconflow.cn/v1
```

### OpenAI-compatible

```bash
novi configure model openai-chat \
  --model "MODEL_NAME" \
  --base-url "https://provider.example.com/v1" \
  --api-key "YOUR_API_KEY"
```

### 检查配置

```bash
novi doctor model
```

CLI 不会回显 API key，只显示是否已设置。

## Kernel

常用 kernel：

- `deepagents`：默认 LLM 路径，适合真实 task、ingest、ask。
- `simple`：deterministic fallback，适合测试记录结构，不调用真实模型。

示例：

```bash
novi task "研究目标" --kernel deepagents
novi task "研究目标" --kernel simple
```

## 工作区配置文件

主要配置位于：

```text
.novi/novi.yaml
.novi/agents/
.novi/workflows/
.novi/skills/
.novi/tools/
```

各 YAML 文件的结构和手动编辑原则见 [YAML 配置](yaml-config.md)。

当前 API key 存储仍是原型方案。后续应迁移到更安全的 secrets 文件、环境变量或系统 keychain。
