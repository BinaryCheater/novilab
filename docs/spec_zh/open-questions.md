# 待确认问题

这些决策应在实现前解决，或明确标记为延后。

建议审阅流程：

1. 明显有答案的项标记为 `Decision`。
2. 把已接受的细节移动到对应 spec。
3. 仍未解决的取舍保留为 `Open`。

## Product Scope

Decision:

1. 第一用户是单个本地 researcher/developer，在一个 project directory 内工作。
2. 第一个有用 workflow 是 `research.review`：创建可审计 research run，捕获 records/artifacts，并提出可 review 的 memory。
3. V0 从 deterministic mock/local runner 和稳定 records 起步；当本地核心闭环可检查并具备 project-local provider config 后，可以选择连接真实 LLM。

## Storage

Decision:

1. V0 从 filesystem-only 开始。SQLite 延后到 query/index 需求被证明之后。
2. Durable structured records 从第一天开始必须是合法 YAML 或 JSONL。
3. Novi 写入或复制 artifacts 时应计算 content hash。引用但尚未 fetch/capture 的外部 artifacts 可以暂时没有 hash。
4. Runs 独立存储在 `.novi/runs/<run_id>/`，由 sessions 通过 `run_ids` 引用。

## CLI Behavior

Decision:

1. V0 使用显式 noun/verb 命令，例如 `novi run start`。
2. `novi chat` 延后；当前交互入口是 `novi ask`，它仍创建 run 并写 session messages。
3. 命令默认使用 active session。操作 session-scoped state 的命令在 shared options 支持后，也应接受 `--session <id>`。

## Skills

Decision:

1. 最小可接受的 `SKILL.md` 是可读 Markdown 文件，YAML frontmatter 可选。没有 frontmatter 时，Novi 尽量从 path/name 推导 `id`，从首段推导 `description`。
2. Built-in skills 默认从 installed package 读取。`novi init` 可以创建 `.novi/skills/` 用于 project-local skills，但不默认复制 built-ins。
3. Project-local skills 覆盖同 id 的 built-in skills，`novi skill list` 应显示 override。

## Tools And Policy

Decision:

1. `read_only` 默认允许并记录。`write_local` 只允许 workspace 内写入，并必须产生 event 和 artifact/diff reference。`shell`、`network`、`external_side_effect`、`physical_world` 在 v0 默认需要 approval 或禁用。
2. Shell execution 可以存在于 v0，但必须作为 sandboxed tool，默认需要 approval。
3. V0 tools 默认禁用 network access。`search_stub` 可以在没有真实 network access 时模拟 research outputs。
4. Failed 或 blocked tool calls 应记录 requested tool id、args reference、actor/agent、risk、policy result、status、error/block reason、timestamps 和任何 partial artifact refs。

## Agents

Decision:

1. V0 只默认提供概念上的 `orchestrator` 和 `auditor` roles。其他 roles 是 reserved names，不作为 active defaults。
2. V0 agent definitions 是 project-local defaults，并在 per-run participants 中保存 snapshot。
3. V0 记录 per-agent tool visibility 和 execution permission snapshot，即使 enforcement 很简单。
4. 一个 run 中多个 model profiles 后置。V0 通常每个 run/participant 记录一个 model profile。

## Model Providers And Context

Decision:

1. Phase 1 支持把 model 配置保存在 `.novi/novi.yaml`，环境变量作为 fallback。
2. OpenAI-compatible chat completions 足够支撑第一版 SiliconFlow-compatible path。
3. Model request boundary 分离 stable `system_prompt.md`、structured `model_messages.jsonl`、human-readable `prompt.md` 和 trace records。
4. 多轮对话会把最近的 user/assistant turns 作为 chat messages 发送。这符合 stateless chat-completions 的要求，并在 provider 支持时给 cache-friendly requests 提供稳定 prefix。

Open:

1. API keys 应继续保存在 `.novi/novi.yaml`，迁移到 `.novi/secrets.yaml`，只使用环境变量，还是接 OS keychain？
2. 当需要 Anthropic-style APIs 或更广泛 provider normalization 时，LiteLLM 是否应成为默认 provider gateway？
3. Novi 是否需要暴露 provider-specific cache-control hints，还是先只依赖稳定 message ordering？

## DeepAgents Boundary

Decision:

1. DeepAgents 是可选 execution kernel，不是 sessions、runs、tools、memory、artifacts 或 policies 的 source of truth。
2. DeepAgents tool calls 应进入 Novi Tool Runtime，并带 source attribution 记录。
3. DeepAgents working files 是 execution working memory；除非 Novi 明确 export，否则不是 artifacts。

Open:

1. 哪些 DeepAgents built-in tools 应直接启用、包装，或替换为 Novi tools？
2. DeepAgents subagents 应如何映射到 Novi platform agents 或 run participants？
3. 哪些 LangGraph checkpoint/resume 能力应暴露到 Novi run records？

## Memory

Decision:

1. V0 memory candidates 由本地用户通过 CLI accept/reject。Auditor 可以推荐，但不能 commit memory。
2. 当 claim 依赖 run output 或 external content 时，memory candidates 应包含 evidence artifact refs。纯 procedural/project notes 可以指向 run summary。
3. Stale memory 由一个新的 candidate 表示，并 supersede 已接受 entry；旧 entry 仍可读，并带 superseded reference。

## Later Integrations

Open:

1. V0 后哪个集成优先：MCP client、browser/search、training、simulation、ROS，还是 IM channel？
2. Codex 和 Claude Code 应建模为 tools、modules、workers，还是根据使用场景同时具备多种身份？
3. 在允许任何 physical-world robot command 前，最小 audit requirement 是什么？
