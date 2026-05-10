# Novi Lab 哲学规格

状态：草案，用户已批准新增

本文记录 Phase 1 原型之后 Novi Lab 应遵循的上层哲学。它本身不直接替换已经接受的 v0 规格，而是解释后续实现和规格修订为什么应从“审计优先的控制平面”推进到“由反馈治理的研究 agent 系统”。

## 核心论点

提案：

Novi Lab 应是一个本地优先的研究 agent 操作系统，用来长期增强研究者探索、验证和迭代想法的能力。

核心问题不是 Novi 应该有多少 agent，也不是执行拓扑到底是 workflow、subagent tree、swarm、tree search，或者 runtime 到底是 DeepAgents、LangGraph、Codex、Claude Code 还是自研 harness。这些都是执行拓扑和实现工具。

更底层的问题是：

- 语言模型会把语言连贯性误认为真实进展；
- 复杂研究任务的 reward 稀疏且延迟；
- 如果 agent 系统缺少可靠的中间反馈，它会倾向于优化活动量、文本完整性、架构复杂度和叙事自洽，而不是真实性、新颖性、可复现性和决策价值。

因此，下一阶段 Novi 架构应受两条硬规则约束：

1. 没有新的外部反馈，置信度不得上升。
2. 长期自治必须有明确 reward、proxy 风险检查和停止条件。

模型可以生成假设、计划、解释、代码草稿和候选解读。Harness 必须决定什么算证据、什么可以进入长期记忆、信念何时可以变化、资源何时可以消耗、方向何时应该停止，以及何时需要人类或强模型介入。

## 为什么重要

提案：

研究 agent 有一种典型失败模式：它不断把故事讲得更圆，却逐渐失去和世界的接触。

这种失败看起来可能很高产：

- 一个概念获得了更好的名字；
- workflow 增加了更多阶段；
- agent 产出更多 review notes；
- report 更精致；
- reflection 文本显得更谨慎；
- memory 积累了简洁总结；
- experiment 在运行，但没有回答关键问题。

这些都不必然是进展。只有当它们连接到外部反馈，或减少不确定性并改变决策时，才有价值。

Novi 应把科学和工程进展看成由证据支持的状态变化，而不是更好的文字表达。系统应区分：

- idea：可能方向；
- hypothesis：值得测试的可证伪主张；
- belief：当前带不确定性的工作判断；
- evidence：来自 source、代码、数据、实验、benchmark、专家输入或失败观察的外部反馈；
- knowledge：按审阅规则进入长期记忆的主张；
- narrative：帮助组织工作的解释框架，但不能被当成证据。

## 反自洽机制

决策：

Novi 应包含 anti-coherence 机制。它的职责是在语言自洽伪装成真实性时打断系统。

系统应在关键节点追问：

- 当前方向是否被用户给出的词汇锚定，而这个词本身可能是错的？
- 新名字是否只是在包装旧想法或弱想法？
- 当前分类是否必要，还是只是让讨论显得系统？
- 是否有外部事实迫使我们改变信念？
- 当前问题是否应该被拒绝或重写，而不是继续回答？
- 当前行动是否减少不确定性，还是只是在增加活动量？
- agent 是否在重复没有新证据的解释？
- 是否应停止、降级、转向，或交给人类审阅？

Anti-coherence 不是普通 critic。普通 critic 仍然可能只是产出合理的评论文本。Anti-coherence 必须能改变控制流：

- 继续；
- 寻找外部反馈；
- 运行 sanity check；
- 降级 claim；
- 阻止 memory write；
- 切换到强模型；
- 询问用户；
- 停止或重定向任务。

## Reward Shaping

决策：

复杂研究任务 reward 稀疏。Novi 应为每个 workflow 定义 dense intermediate rewards，避免 agent 优化活动量。

正向 reward signal 示例：

- 找到相关 prior work cluster；
- 把 hypothesis 写成可证伪形式；
- 复现 baseline；
- sanity run 通过；
- negative result 排除了错误方向；
- ablation 支持某个机制；
- 多 seed 结果稳定；
- artifact 可以追溯到产生它的 command、data 和 code；
- 因新反馈矛盾而降级 claim；
- 在继续浪费预算前停止错误方向。

Proxy 风险示例：

- 只经过总结或反思，置信度却上升；
- report 风格更好，但没有新证据；
- experiment 在运行，但不会改变任何决策；
- memory 来自 narrative summary，而不是 evidence；
- agent 在失败后重复同一计划；
- workflow 扩张只是因为看起来更严谨，而不是每一步都有决策价值。

Workflow 应声明 reward signals 和 proxy risks。Harness 应用它们做 planning、stopping、model routing 和 review。

## Harness 高于 Prompt

决策：

Prompt instruction 必要但不充分。任何影响长期状态、置信度、记忆、权限、预算或不可逆动作的事情，都必须由 harness 控制。

模型负责：

- 理解任务；
- 生成候选；
- 局部推理；
- 写作；
- 提出计划；
- 解读反馈；
- 建议改进；
- 生成代码草稿或 coding brief。

Harness 负责：

- 状态管理；
- context assembly；
- tool execution；
- permission boundary；
- feedback capture；
- budget scheduling；
- model routing；
- failure recovery；
- memory write rules；
- claim 和 belief state；
- versioning；
- human checkpoint。

Claude Code、Codex、Aider、OpenHands 等成熟 coding agent 的主要启发是：有用自治发生在强 harness 内部，这个 harness 有文件系统、diff、shell、test、permission、user intervention 和 task boundary。Novi 应把同样的纪律带到研究和实验任务里。

## 核心对象

提案：

未来 Novi 设计应在 sessions、runs、skills、tools、memory、artifacts 之外提升以下对象的重要性。

### Claim

一个正在被考虑、测试、支持、削弱或拒绝的主张。

建议字段：

- id；
- statement；
- scope；
- status：idea、hypothesis、working_belief、supported、contradicted、abandoned；
- confidence；
- uncertainty；
- evidence_refs；
- counterevidence_refs；
- created_by；
- updated_by；
- last_feedback_at。

### Feedback Event

能影响 claim、plan、memory item 或 workflow 的外部信号。

示例：

- paper 或 source check；
- quote 或 source extraction；
- code execution result；
- experiment metric；
- benchmark result；
- failed command；
- test output；
- plot 或 dataset inspection；
- human correction；
- expert review；
- coding delegate result。

### Belief Update

一个受控的 claim 状态变化。

规则：

- 没有至少一个新的 feedback event，confidence 不得上升；
- reflection 只能澄清 uncertainty，不能升级 confidence；
- contradiction 应变成 counterevidence，不能藏在 summary prose 里；
- 有价值的 abandoned direction 应作为 negative memory 保持可搜索。

### Reward Signal

Workflow 内部表示某一步是真实进展、proxy 风险或应停止的事件。

### Narrative Check

由 harness 控制的检查点，可以打断当前框架并强制 reframing、evidence gathering、downgrade 或 stop。

### Improvement Candidate

对 agent prompt、skill、workflow、model route、tool、memory rule 或 coding delegate 的改进提案。

提出它的模型不应直接应用它。它应进入升级 workflow。

## Memory 哲学

决策：

Memory 不是保存精致总结的地方。Memory 是过去证据影响未来行为的受控接口。

Novi 应区分 memory 类型：

- hypothesis memory：合理但未验证的想法；
- evidence memory：有 source 或 result 支持的事实；
- experiment memory：commands、configs、metrics、failures、results；
- negative memory：被证伪的方向、失败策略和反例；
- strategy memory：在已知条件下多次有效的做法；
- agent memory：关于 prompts、tools、model routes 和 workflows 的经验；
- narrative memory：当前 framing，可用于定位，但不是 evidence。

规则：

- evidence、experiment、negative 和 strategy memory 可以影响未来 confidence；
- narrative memory 可以影响 context，但不能升级 claims；
- memory write 应引用 feedback events 或 artifacts；
- 高影响 memory write 应经过 review gate；
- self-reflection 可以提出 memory，但不能直接变成 knowledge。

## 反思与自我升级

决策：

Agent reflection 和 self-upgrade 应分三层。

### Prompt Workflow

Prompt 可以要求 agent 注意可能的改进：

- 什么有效；
- 什么失败；
- uncertainty；
- possible memory；
- possible skill；
- possible prompt change；
- possible workflow change；
- possible model-routing change。

这有用，但不具备权威性。

### Hooks

Hooks 应从系统事件可靠触发 reflection candidates：

- run ended；
- tool failed；
- 同一失败重复；
- 用户纠正了重要 claim；
- claim 被降级；
- 尝试写入 memory；
- budget 超限；
- workflow stall；
- coding delegate 返回 patch 或 failure；
- external feedback 反驳当前 narrative。

Hooks 应创建结构化 trigger，而不是静默改变 agent。

### Explicit Upgrade Workflow

任何长期变化都应走显式 workflow：

```text
trigger
→ collect evidence
→ diagnose pattern
→ propose change
→ validate on recent cases or a small benchmark
→ accept, reject, or revise
→ versioned write
```

这适用于 system prompts、skills、memory、workflow definitions、model routes、tool permissions 和 coding delegates。

## Model Routing

提案：

Novi 应区分低成本模型、强模型和 coding-specialized 模型角色。

低成本模型适合：

- formatting；
- summarization；
- log cleanup；
- source triage；
- first-pass extraction；
- simple classification；
- routine progress notes。

强模型适合：

- narrative checks；
- belief updates；
- experiment design；
- failure attribution；
- 决定是否停止；
- 决定 memory 是否可升级；
- high-impact planning；
- conflict resolution。

Codex、Claude Code、Aider、OpenHands 等 coding delegate 适合：

- 实现实验；
- 修复失败脚本；
- 运行测试；
- 产出 diff；
- 复现 baseline；
- 生成可执行反馈。

LiteLLM 是 provider routing、fallback 和 cost/performance 管理的候选组件。Routing 应基于决策风险，而不只是任务长度。

## Workflow 与拓扑

提案：

Workflow、subagents、swarms 和 tree search 应被视为执行拓扑。

固定 workflow 适合：

- 已知研究阶段；
- review gates；
- memory upgrades；
- belief updates；
- 昂贵动作；
- experiment lifecycle checkpoints。

Subagents 适合：

- context isolation；
- role specialization；
- tool 和 permission separation；
- model separation；
- long-running task delegation。

Swarm 或宽并行适合：

- 独立 literature search；
- candidate idea coverage；
- benchmark comparison；
- tasks 不共享状态时的参数或方法探索。

Tree search 适合：

- code 和 experiment-space exploration；
- algorithm variants；
- 有可评估 branch quality 的多步计划。

没有 feedback 和 reward definitions 的拓扑都不应被信任。

## Coding Delegates

提案：

Novi 应能调用成熟 coding agents，而不是只依赖 research agent 自己写代码。

主 research agent 应拥有研究问题和解释权。Coding delegate 应拥有有边界的实现工作：

- 接收 coding brief；
- 编辑文件或产出 patch；
- 运行 commands 或 tests；
- 报告 changed files、commands、outputs 和 failures；
- 返回成为 feedback events 的 artifacts。

Coding delegate 不应静默决定研究结论。它负责把系统接到可执行世界。Novi 再用这些结果做 belief updates、reward signals 和 next-step decisions。

## Related Works

本节把相关系统当作设计证据，而不是要复制的模板。

### DATAGEN

DATAGEN 使用 LangChain 和 LangGraph 构建可见的 multi-agent data-analysis workflow。它的 graph 显式经过 hypothesis、process、visualization、code、search、report、quality review、note taking 和 refinement 等 agent。

实践启发：

- 显式 graph 让 workflow structure 更容易理解；
- 专用 agent 有助于分离职责；
- quality review 可以成为流程节点。

对 Novi 的限制：

- 可见 graph 本身不能解决 belief calibration；
- 如果 quality review 不能改变控制流，它仍可能只是语言 critique；
- 该项目更接近固定 data-analysis assistant，而不是 feedback-governed research operating system。

参考：[DATAGEN](https://github.com/starpig1129/DATAGEN)

### EvoScientist

EvoScientist 是 DeepAgents-first 的 research assistant。它构建一个带 subagents、skills、memory、middleware、backends、LiteLLM-compatible model support 和可选 async subagents 的主 DeepAgent；async subagents 通过 `langgraph dev` 托管。

它的 research lifecycle 主要由 prompt 驱动：intake、plan、execute/debug、evaluate/iterate、write 和 verify。writing、data analysis 等长任务 subagents 可以部署成 LangGraph graphs，并异步调用。

实践启发：

- DeepAgents 适合作为 rich agent harness；
- skills 和 memory 是复杂研究任务的必要条件；
- async subagents 适合长任务；
- model routing、middleware 和 backends 是真实产品的一部分，不是外围功能。

对 Novi 的限制：

- prompt-driven workflow 仍可能漂移；
- memory 和 self-evolution 需要硬证据规则；
- 如果缺少显式 claim、feedback、reward 和 narrative-control 对象，强 AI scientist assistant 仍可能优化连贯活动量。

参考：[EvoScientist](https://github.com/EvoScientist/EvoScientist)

### 自动研究系统

更广泛的 auto-research 生态包括 AI-Scientist、AI-Scientist-v2、RD-Agent、AutoResearchClaw、Agent Laboratory、AI-Researcher、Biomni、DeepScientist、InternAgent 和 Karpathy 的 autoresearch。

实践启发：

- 端到端研究系统需要 literature review、ideation、coding、experiments、analysis、writing 和 review；
- 很多系统使用 custom harness，因为研究任务需要状态、工具、代码执行和领域反馈；
- coding agents 往往是 experiment stage 的关键基础设施；
- tree search、Docker isolation、git worktrees、benchmark loops 和 report generation 是反复出现的模式。

对 Novi 的限制：

- 很多系统强调 impressive end-to-end production，但没有显式化 belief state；
- 生成 papers、reports 或 experiments 不够，除非系统知道哪些 claims 真的被支持；
- Novi 应学习它们的 toolchain，而不是复制它们的产品范围。

参考：[Awesome Auto Research](https://github.com/handsome-rich/Awesome-Auto-Research-Tools)

### Coding Agents

Codex、Claude Code、Aider、OpenHands 和 SWE-agent 表明，语言模型嵌入带有 files、shell commands、diffs、tests、permissions 和 user intervention 的 harness 后，可靠性会显著提升。

实践启发：

- coding progress 比 research prose 更容易验证，因为 tests、commands 和 diffs 提供 dense feedback；
- 强 coding delegate 可以把 claims 转成可执行检查；
- harness 应把代码变化和输出捕获为 feedback events。

对 Novi 的限制：

- coding agents 本身不能解决 research judgment；
- 测试通过不等于 scientific importance；
- coding delegates 应是 research system 内部有边界的工具，而不是 research memory 或 conclusions 的拥有者。

参考：

- [Aider](https://github.com/Aider-AI/aider)
- [OpenHands](https://github.com/All-Hands-AI/OpenHands)
- [SWE-agent](https://github.com/SWE-agent/SWE-agent)

### DeepAgents 与 LangGraph

DeepAgents 提供 rich agent harness，包括 planning、filesystem、subagents、skills、memory、permissions 和 middleware。LangGraph 提供 stateful graph execution、checkpoints、interrupts、streaming 和 deployed graph support。

实践启发：

- DeepAgents 适合作为 autonomous node execution 的默认选择；
- LangGraph 适合显式 workflow 和 async/deployed graph execution；
- Novi 不需要在二者之间排他选择。

推荐 Novi 解释：

- 用 DeepAgents 承担 agent autonomy、tools、skills、memory 和 subagent delegation；
- 在需要显式 control flow、checkpoints、async jobs 或 review gates 时使用 LangGraph；
- belief updates、memory writes、rewards 和 irreversible actions 必须位于二者之上，由 Novi-owned harness logic 管理。

参考：

- [DeepAgents documentation](https://docs.langchain.com/oss/python/deepagents/overview)
- [LangGraph documentation](https://docs.langchain.com/oss/python/langgraph/overview)

## 产品后果

提案：

Novi 不应只是另一个 AI scientist assistant。它应是 feedback-governed research agent system。

这意味着：

- sessions 和 runs 仍有价值，但主要目的应是 research state 和 feedback，而不是重审计；
- memory 仍然必要，但 memory write rules 必须 evidence-based；
- skills 仍然必要，但应包含 feedback expectations 和 failure modes；
- model routing 应显式并且 risk-aware；
- coding delegates 应作为 evidence-generating workers 集成；
- workflow definitions 应包含 rewards 和 proxy risks；
- agent self-upgrade 应 versioned、validated、reversible；
- narrative checks 应成为 first-class control points。

这样的系统仍然可以直接帮助用户做研究。它也能帮助用户改进 agent 系统本身。这两个目标并不冲突：更强的研究 agent 依赖更好的 feedback、memory 和 upgrade mechanisms。

## 开放问题

开放：

- 哪种 claim ledger schema 对 Phase 2 足够轻量，而不会变成沉重 scientific database？
- 第一批 hooks 应实现哪些：run-end、tool-error、memory-write、user-correction，还是 claim-downgrade？
- narrative checks 应在每个 workflow stage 运行，还是只在影响 memory、confidence、budget 或 direction 的 gate 运行？
- human feedback 应如何表示：ordinary feedback events、privileged review events，还是两者都有？
- 不经显式用户批准，什么级别的自动 agent self-upgrade 可以接受？
- Codex、Claude Code、Aider、OpenHands 应如何集成：shell delegate、MCP tool，还是 explicit cowork participant？
- 哪些 rewards 可以自动计算，哪些需要模型或人类判断？
