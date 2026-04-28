# 待确认问题

这些决策应在实现前解决，或明确标记为延后。

建议审阅流程：

1. 明显有答案的项标记为 `Decision`。
2. 把已接受的细节移动到对应 spec。
3. 仍未解决的取舍保留为 `Open`。

## Product Scope

Open:

1. 第一用户是谁：单个本地 researcher/developer、lab team，还是 external users？
2. 第一个有用 workflow 是什么：research review、code maintenance、experiment design，还是 physical-AI run audit？
3. V0 是否应立即连接真实 LLM，还是先用 mock/local runner 和稳定 records 起步？

## Storage

Open:

1. V0 是否包含 SQLite，还是先从 filesystem-only records 开始？
2. 所有 durable records 是否从第一天开始就必须是合法 YAML/JSON？
3. Artifacts 在 v0 是否总是计算 content hash？
4. Sessions 是否包含 runs，还是 runs 独立存储并由 sessions 引用？

## CLI Behavior

Open:

1. 命令风格应是 `novi run start`，还是更短的 `novi run`？
2. `novi chat` 应进入第一个 milestone，还是等 runs 和 sessions 稳定后再加？
3. 命令是否要求 active session，还是所有命令都允许 `--session <id>`？

## Skills

Open:

1. 最小可接受的 `SKILL.md` 形态是什么？
2. Novi 应把 built-in skills 复制到 `.novi/skills/`，还是从 installed package 读取？
3. Project-local skills 是否覆盖同 id 的 built-in skills？

## Tools And Policy

Open:

1. 哪些 risk levels 默认需要 approval？
2. Shell execution 是否应存在于 v0，即使是 sandboxed？
3. V0 tools 是否默认禁用 network access？
4. Failed 或 blocked tool calls 应记录哪些内容？

## Agents

Open:

1. 除了 `orchestrator` 和 `auditor`，默认还应有哪些 agent roles？
2. Agent definitions 应放在 global、project、session，还是三者都支持？
3. V0 是否就应按 agent 配置 tool visibility 和 tool execution permission？
4. 一个 run 在 v0 是否支持多个 model profiles，还是后置？

## Memory

Open:

1. 谁可以接受 memory candidates：只有 user、只有 auditor，还是低风险 summary 可以 policy-driven auto-accept？
2. Memory candidates 是否必须包含 artifact references？
3. stale 或 superseded memory 应如何表示？

## Later Integrations

Open:

1. V0 后哪个集成优先：MCP client、browser/search、training、simulation、ROS，还是 IM channel？
2. Codex 和 Claude Code 应建模为 tools、modules、workers，还是根据使用场景同时具备多种身份？
3. 在允许任何 physical-world robot command 前，最小 audit requirement 是什么？
