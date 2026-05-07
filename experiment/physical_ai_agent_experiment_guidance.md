# 面向 Physical AI Prototype 的 Agent 实验与开发指导文档

## 0. 文档目的

本文档用于指导后续实验设计和系统开发。核心问题不是“如何从零构建一个实验 harness”，而是围绕以下几个问题形成清晰实验路线：

1. 这个方向是否只是 Claude Code + LeRobot + SOP 的工程封装？
2. 如何设计 benchmark，验证 agent workflow 是否真的有用？
3. prompt、workflow、skill、SOP 各自贡献是什么？
4. prototype build 如何服务于 physical AI 系统设计，而不是变成模块堆叠？
5. self-improving 应该何时引入？是否应该一开始就研究？
6. 如何让系统既有 AI agent 研究价值，又有实际辅助科研价值？

本文档的立场：

> 当前阶段不应直接追求“全自动科研 agent”或“self-improving scientist”。更合理的目标是构建一个 human-gated、physical-prior-guided 的 prototype design agent，用于辅助研究者从模糊的具身智能问题中提炼假设、构建最小 prototype、运行验证、归因失败，并收敛到更简单、更正确的系统设计。

---

## 1. 核心判断

### 1.1 如果只是 Claude Code + skill + LeRobot，科研价值有限

Claude Code 已经能完成大量代码修改、命令执行、repo 理解、debug 和自动化工程任务。LeRobot 这类框架也已经提供了机器人学习中的数据、模型、训练、评估和真实机器人接口。

因此，如果系统的主要能力是：

- 给 LeRobot 加模块；
- 自动写训练脚本；
- 自动跑 baseline；
- 自动生成实验报告；
- 用 skill 文件塞入一套 SOP；

那么它更像是 robotics coding assistant，而不是有独立研究价值的 agent 框架。

这类系统有使用价值，但难以构成核心研究贡献。

### 1.2 真正值得研究的是“设计判断”而不是“代码执行”

面向 Physical AI 的 prototype agent 不应只回答：

> 能不能把代码跑起来？

而应回答：

> 给定一个 physical task，什么系统结构是必要的？什么模块是多余的？当前失败来自 perception、planning、control、grounding、action abstraction、data，还是 evaluation mismatch？

也就是说，benchmark 和系统设计应重点评估 agent 是否具备以下能力：

- 从任务约束中提取 physical priors；
- 推出最小充分架构；
- 避免盲目堆叠热门模块；
- 用 prototype 验证系统设计假设；
- 从实验失败中做出合理归因；
- 根据失败决定是加模块、删模块、改 action abstraction，还是重新定义任务；
- 形成可复用的 design rule。

---

## 2. 目标系统定位

### 2.1 不应定义为“自动科研 agent”

直接定义为自动科研 agent 会过大，容易滑向：

- 自动读论文；
- 自动生成 idea；
- 自动写代码；
- 自动跑实验；
- 自动写论文；
- 自动 reviewer 打分。

这类框架已有不少类似尝试，但多数核心仍是 workflow + search + engineering automation。对于具身智能这种反馈慢、目标不清、物理约束强的领域，全自动早期风险很高。

### 2.2 更合适的定位

建议定义为：

> 一个 human-gated physical AI prototype design agent，用于在研究者给定任务、embodiment 和初始研究假设后，自动进行 physical prior extraction、minimal architecture proposal、prototype build、failure diagnosis 和 design simplification，辅助研究者收敛到最小充分的 embodied AI 系统架构。

关键词：

- human-gated：人类保留研究判断权；
- physical-prior-guided：不是一般代码 agent，而是围绕物理约束做设计；
- prototype-first：用可执行 prototype 暴露问题；
- minimal sufficient architecture：目标不是堆复杂系统，而是找最小正确结构；
- failure-driven：通过失败归因指导下一步设计。

---

## 3. Prototype Build 的研究含义

### 3.1 Prototype 不是 mini-product

这里的 prototype 不应是“把 perception、planner、memory、world model、VLA、RL、IL、retrieval 都接起来”的大系统。

更合理的定义是：

> Prototype 是一个 design probe，用于验证某个 physical AI 系统设计假设。

也就是说，prototype 的目标不是展示一个完整机器人系统，而是回答具体问题，例如：

- 这个任务是否需要显式 task planning？
- 这个任务是否需要 long-term memory？
- 这个任务是否需要 object-centric representation？
- 当前失败是否来自 action abstraction mismatch？
- simple BC 是否已足够？
- VLA 是否真的提供边际收益？
- closed-loop correction 是否比 high-level planner 更关键？
- sim success 是否能预测 real-world success？

### 3.2 Prototype 应该引导系统设计

一个有效的 prototype build loop 应该产生系统设计判断，而不是只产生可运行代码。

推荐输出：

1. physical task specification；
2. physical prior analysis；
3. minimal architecture hypothesis；
4. prototype plan；
5. implementation result；
6. evaluation result；
7. failure attribution；
8. simplification / escalation decision；
9. design rule。

其中最重要的是第 7-9 项。没有 failure attribution 和 design rule，prototype build 很容易退化为工程推进。

### 3.3 复杂性应该存在于搜索空间，而不是最终系统

系统可以允许候选方法空间很复杂，例如包含：

- BC；
- diffusion policy；
- VLA；
- object detector；
- grasp proposal；
- skill primitive；
- memory；
- symbolic planner；
- closed-loop controller；
- world model。

但 prototype 的目标应是从复杂候选空间中收敛到简单结构。

原则：

> 每新增一个模块，必须声明它预期解决的 failure mode。没有对应 failure mode，不允许加模块。每个高级模块都需要 ablation。

---

## 4. Physical-Prior-Guided Workflow

### 4.1 为什么 workflow 不能只是 SOP 文本

SOP 可以写进 Claude Code skill，但这不等于 agent framework 有实质贡献。

真正的 workflow 应该是外部强制的研究状态机，而不是一段提示词。

SOP 形式：

> 请先分析任务，再设计实验，再实现 prototype，再分析失败。

Workflow 形式：

- Stage 1 没有输出 task spec，不允许进入 Stage 2；
- Stage 2 没有 physical priors，不允许提出 architecture；
- Stage 3 没有 minimal baseline，不允许引入复杂模块；
- Stage 4 没有 evaluation plan，不允许实现；
- Stage 5 实验失败后，必须归因到 failure ontology；
- Stage 6 没有 evidence，不允许形成 design rule。

Agent 框架相对于 Claude Code + skill 的关键差异应体现在这里。

### 4.2 推荐 workflow

#### Stage 1: Task Normalization

输入：

- task description；
- embodiment；
- observation space；
- action space；
- success condition；
- failure condition；
- available data；
- simulator / real robot constraints。

输出：标准化任务规格。

#### Stage 2: Physical Prior Extraction

分析：

- horizon: short / long；
- observability: full / partial；
- contact richness: low / high；
- semantic demand: low / high；
- dynamics sensitivity: low / high；
- feedback frequency requirement: low / high；
- precision demand: low / high；
- generalization axis: object / scene / instruction / embodiment；
- safety constraint；
- action abstraction suitability。

输出：physical prior table。

#### Stage 3: Minimal Architecture Hypothesis

基于 Stage 2，提出最小充分架构。

要求：

- 明确选择哪些模块；
- 明确暂时不选择哪些模块；
- 对每个模块给出 physical justification；
- 对每个不选模块给出排除理由；
- 避免默认使用 LLM planner / memory / world model / VLA。

#### Stage 4: Prototype Plan

输出：

- 需要改哪些 repo 文件；
- 需要哪些 config；
- 需要哪些 dataset / checkpoint；
- 需要哪些 evaluation scripts；
- 最小 smoke test 是什么；
- 预计 failure modes 是什么。

#### Stage 5: Implementation

约束：

- 只实现最小架构；
- 不允许提前堆高级模块；
- 不允许绕过 evaluation；
- 所有新增模块必须绑定一个明确 failure mode 或 hypothesis。

#### Stage 6: Verification

至少包括：

- unit test；
- smoke test；
- minimal evaluation；
- log completeness check；
- result reproducibility check。

#### Stage 7: Failure Diagnosis

失败必须归因到明确类别，例如：

- perception failure；
- control failure；
- planning failure；
- grounding failure；
- action abstraction mismatch；
- data coverage issue；
- simulator artifact；
- reward / evaluation mismatch；
- interface bug；
- latency issue；
- task specification ambiguity。

禁止只输出：

- “模型不够强”；
- “需要更多数据”；
- “可以用更大的模型”；
- “可以加入 planner”；
- “可以继续优化”。

除非这些建议绑定了具体证据。

#### Stage 8: Simplification or Escalation

根据 failure diagnosis 决定：

- 是否保持当前最小架构；
- 是否删除无效模块；
- 是否加入一个最小新模块；
- 是否修改 action abstraction；
- 是否修改 evaluation；
- 是否重新定义任务；
- 是否请求人类判断。

#### Stage 9: Design Rule Extraction

最终输出一条或多条 design rule，例如：

> 对于 short-horizon tabletop manipulation，如果语言指令固定且主要失败来自 pose perturbation，则优先验证 closed-loop correction，而不是加入 high-level language planner。

Design rule 必须包含：

- applicable conditions；
- evidence；
- counterexample risk；
- confidence；
- required future validation。

---

## 5. Benchmark 设计原则

### 5.1 Benchmark 应该测什么

不应只测：

- 代码是否跑通；
- 训练是否完成；
- 指标是否提升；
- 报告是否完整。

应重点测：

- 是否识别正确 physical bottleneck；
- 是否提出合理 minimal architecture；
- 是否避免不必要模块；
- 是否选择正确 action abstraction；
- 是否提出有效 ablation；
- 是否能从失败中做出正确归因；
- 是否能把实验结果转化为 design rule；
- 是否减少 human debugging / decision cost。

### 5.2 Benchmark 不是完整 harness，而是 small-but-hard seed

当前阶段不需要构建庞大的 benchmark。建议先构造 12-20 个高质量任务，甚至第一阶段可以从 6 个任务开始。

任务应覆盖少数关键 physical AI 设计陷阱，而不是追求数量。

推荐任务类型：

#### Type A: Short-horizon, low-semantic, control/contact-heavy

例子：

- simple pick-and-place；
- pushing；
- insertion；
- pose-sensitive grasping。

设计陷阱：

- agent 可能错误加入 LLM planner、memory、semantic graph、world model。

合理设计倾向：

- object/local geometry representation；
- closed-loop visuomotor policy；
- simple skill primitive；
- compliance / force / tactile if needed。

评测重点：

- 是否避免过度架构化；
- 是否识别主要瓶颈是 control/contact/perception，而非 high-level reasoning。

#### Type B: Long-horizon, compositional, semantic-heavy

例子：

- 多物体整理；
- 根据语言约束完成多步任务；
- household object rearrangement。

设计陷阱：

- agent 可能只上 monolithic policy，忽略 decomposition。

合理设计倾向：

- semantic grounding；
- task decomposition；
- skill library；
- state / memory；
- low-level policy separation。

评测重点：

- 是否识别 long-horizon decomposition 必要性；
- 是否分离 high-level planning 和 low-level control。

#### Type C: Partial Observability / Object Permanence

例子：

- object search；
- 需要记住暂时不可见目标；
- navigation + manipulation。

设计陷阱：

- agent 继续堆 perception，而忽略 memory / belief state。

合理设计倾向：

- spatial memory；
- object belief state；
- uncertainty-aware exploration。

#### Type D: Action Abstraction Mismatch

例子：

- 低层 joint/action planning horizon 过长；
- token-level planning 无法落到稳定控制；
- high-level plan 与 motor primitive 不匹配。

设计陷阱：

- agent 直接在错误 action granularity 上规划。

合理设计倾向：

- macro action；
- skill primitive；
- closed-loop controller；
- receding horizon。

#### Type E: Sim-to-Real / Evaluation Mismatch

例子：

- sim success 高，但扰动或真实场景失败；
- benchmark 指标奖励错误行为；
- offline metric 与真实执行不一致。

设计陷阱：

- agent 盲信 benchmark 或继续调参。

合理设计倾向：

- failure-specific evaluation；
- domain randomization；
- real correction data；
- revised metric。

---

## 6. 对照实验设计

### 6.1 不要简单比较“Claude Code vs 我的 agent”

这种比较不够严谨，因为差异可能来自：

- prompt 更详细；
- skill 更完整；
- workflow 更强；
- 工具权限不同；
- evaluation 不同；
- 人类调参更多；
- Claude Code 本身足够强。

应该把变量拆开。

### 6.2 三个主要变量

#### Prompt

模型看到的自然语言指令。

- P0: naive task prompt；
- P1: physical-prior-aware prompt。

P1 包含：

- 先分析 physical priors；
- 优先 minimal architecture；
- 每个模块必须绑定 failure mode；
- 避免无证据加入复杂模块；
- 输出 failure diagnosis 和 design rule。

#### Workflow

外部强制执行的状态机。

- W0: free-form execution；
- W1: enforced staged workflow。

关键点：workflow 不能只是 prompt 里的说明，而应由系统外部记录、检查、gate。

#### Skill / Library

可复用知识和操作模板。

- S0: no skill library；
- S1: fixed physical AI skill library。

S1 可以包含：

- physical prior schema；
- task taxonomy；
- architecture templates；
- failure ontology；
- ablation templates；
- LeRobot recipes；
- evaluation templates；
- anti-patterns。

第一阶段不要让 skill 自动更新，否则变量会混乱。

### 6.3 推荐实验组

#### Group A: Naive Claude Code baseline

配置：

> P0 + W0 + S0

目的：测 Claude Code 原生能力。

#### Group B: Prompt-only

配置：

> P1 + W0 + S0

目的：测一个好 prompt 是否已经足够。

#### Group C: Workflow-only

配置：

> P0-minimal + W1 + S0

目的：测外部强制流程本身是否有效。

注意：这里的 prompt 只能提供每一步需要输出的最小格式，不应注入过多 physical AI 知识，否则会和 skill/prompt 变量混淆。

#### Group D: Prompt + Workflow

配置：

> P1 + W1 + S0

目的：测 prompt 与 workflow 对齐后的效果。

这是核心系统基础版。

#### Group E: Prompt + Workflow + Fixed Skill Library

配置：

> P1 + W1 + S1

目的：测 reusable physical AI skill 是否带来额外收益。

这是目标系统的非 self-improving 版本。

#### Optional Group F: Human Expert Scaffold + Claude Code

配置：

> human-written design plan + Claude Code implementation

目的：提供 upper bound，比较 agent 设计与人类专家设计差距。

---

## 7. 主要实验假设

### H1: Workflow improves reliability

强制 workflow 相比单 prompt 更稳定，seed variance 更小。

指标：

- runnable prototype rate；
- stage completion rate；
- invalid output rate；
- number of failed commands；
- variance across seeds。

### H2: Physical-prior prompt improves design quality

physical-prior-aware prompt 能减少错误模块选择和过度设计。

指标：

- unnecessary module count；
- key module omission rate；
- architecture rationale score；
- minimality score。

### H3: Workflow improves diagnosis more than coding

workflow 未必显著提升代码成功率，但可能显著提升 failure attribution、ablation quality 和 design rule quality。

这是一个重要的预期结果。如果成立，说明系统贡献不在 coding，而在 research/design behavior shaping。

### H4: Skill library improves transfer

固定 skill library 在新任务上减少重复错误。

指标：

- cross-task success；
- repeated failure rate；
- human intervention count；
- design consistency across tasks。

### H5: Aligned prompt + workflow + skill is best, but not because of prompt length

预期最佳配置是 P1 + W1 + S1。但需要谨慎解释：

- 如果 prompt-only 已接近最佳，说明 workflow 价值有限；
- 如果 workflow-only 已很强，说明外部流程约束是主因；
- 如果 skill library 提升最大，说明可复用领域知识比 agent orchestration 更关键；
- 如果三者组合才明显好，说明 prompt、workflow、skill 需要对齐。

---

## 8. 评价指标

### 8.1 Execution Metrics

基础执行指标：

- prototype 是否跑通；
- unit tests 是否通过；
- eval script 是否能运行；
- 是否生成有效 logs；
- 是否遵守 repo constraints；
- 是否在预算内完成。

这些指标必要，但不是核心。

### 8.2 Physical Design Metrics

核心指标：

- 是否识别正确 physical bottleneck；
- 是否提出合理 minimal architecture；
- 是否避免不必要模块；
- 是否正确选择 action abstraction；
- 是否区分 high-level planning 与 low-level control；
- 是否提出有效 ablation；
- 是否基于证据进行 architecture escalation / simplification。

建议采用 expert rubric 评分，例如 1-5 分。

### 8.3 Failure Diagnosis Metrics

评估 failure attribution：

- 归因是否正确；
- 是否混淆 perception / control / planning / grounding / data / evaluation；
- 是否提出能验证归因的下一步实验；
- 是否避免空泛建议；
- 是否识别 benchmark 或 task specification 的问题。

### 8.4 Research Utility Metrics

评估系统是否真的帮助研究：

- human intervention count；
- time to useful design decision；
- number of unsupported claims；
- number of meaningful ablations proposed；
- number of design rules accepted by human；
- number of false design rules rejected；
- reduction in unnecessary experiments。

### 8.5 Cost Metrics

实用成本：

- token cost；
- wall-clock time；
- tool calls；
- failed command count；
- compute cost；
- human review time。

---

## 9. Self-Improving 的边界

### 9.1 第一阶段不要引入跨任务 self-improving

当前阶段应固定：

- prompt；
- workflow；
- skill library；
- evaluator rubric；
- budget；
- tasks。

允许：

- within-task debug loop；
- within-task limited patching；
- within-task failure-driven retry。

不允许：

- agent 根据前几个任务自动修改 skill；
- agent 自动修改 workflow；
- agent 自动重写 prompt；
- agent 自动更新 evaluator；
- agent 在 held-out task 前吸收测试反馈。

原因：如果一开始引入 self-improving，很难判断提升来自 workflow、prompt、skill、经验积累，还是 benchmark overfitting。

### 9.2 Self-improving 应该作为第二阶段问题

第一阶段问题：

> 固定 physical-prior-guided workflow / skill 是否优于 naive Claude Code 和 prompt-only？

第二阶段问题：

> agent 能否基于实验反馈自动改进 workflow、skill、failure ontology 或 design rule library？

这两个问题应分开做。

### 9.3 Self-improving 的合理更新对象

不建议一开始让 agent 改模型参数。更合理的更新对象：

- failure database；
- design rule library；
- task-to-architecture mapping；
- anti-pattern library；
- evaluator calibration examples；
- human feedback memory；
- workflow routing policy；
- experiment selection policy。

### 9.4 判断 self-improving 是否真实有效

必须满足：

- 更新前后在 held-out tasks 上提升；
- 不是只记住 benchmark；
- 不是增加 prompt 长度带来表面提升；
- 更新内容可解释；
- 可以 ablate memory / updated skill；
- 人类能审计哪些经验被采纳。

---

## 10. Agent 框架相对 SOP 的实质提升点

如果只是 SOP，Claude Code skill 可以做到类似效果。

Agent 框架要有实质提升，必须提供以下能力之一或多个：

### 10.1 Statefulness

维护研究状态：

- 当前 hypothesis 是什么；
- 哪些假设已被测试；
- 哪些实验支持/反驳了假设；
- 当前处于 exploration、verification、debugging、simplification 还是 reporting；
- 哪些设计规则已被证据支持。

### 10.2 External Gating

外部强制流程，防止模型跳步：

- 没有 physical priors 不允许 implementation；
- 没有 failure mode 不允许加模块；
- 没有 ablation 不允许宣称模块有用；
- 没有 evidence 不允许生成 design rule。

### 10.3 Artifact Discipline

每一步都有结构化产物：

- task spec；
- prior table；
- architecture decision record；
- experiment plan；
- logs；
- failure report；
- design rule；
- human decision record。

### 10.4 Failure-to-Design Mapping

从失败到设计决策，而不是从失败到“再试试”。

例如：

- pose perturbation failure → closed-loop correction；
- wrong object target → grounding module；
- horizon explosion → skill primitive / macro action；
- sim success but real failure → revise evaluation / collect real correction data；
- low-level instability → controller/action interface issue，而非 planner issue。

### 10.5 Human-Gated Research Judgment

明确哪些节点需要人类判断：

- research problem reframing；
- task abstraction validity；
- design rule acceptance；
- real-robot risk；
- novelty / usefulness judgment；
- whether to continue a direction。

### 10.6 Long-Term Research Memory

系统应逐渐积累：

- accepted design rules；
- rejected design rules；
- common false diagnoses；
- task classes and architecture matches；
- human preference patterns；
- failed experiment rationales。

这部分可以作为后续 self-improving 的基础。

---

## 11. 如何避免工程灌水

### 11.1 不要把贡献写成“我们做了一个 agent 框架”

这太泛，也容易被认为只是工程集成。

更好的研究问题是：

> 在 physical AI prototype construction 中，显式 physical-prior workflow 是否能改善系统设计质量、失败归因质量和最小架构收敛能力？

### 11.2 贡献应落在三个方面

#### Contribution 1: Benchmark

一个 small-but-hard 的 physical AI prototype design benchmark。

它不是测普通 coding，而是测：

- physical prior extraction；
- architecture selection；
- prototype execution；
- failure diagnosis；
- design simplification。

#### Contribution 2: Workflow

一个 physical-prior-guided workflow：

> physical priors → minimal architecture → prototype → failure diagnosis → simplification → design rule。

重点是 workflow 如何改变 agent 的研究行为，而不是多 agent 分工本身。

#### Contribution 3: Empirical Findings

目标是得到可解释的经验发现，例如：

- prompt-only 能提升 rationale，但不能稳定提升 runnable prototype；
- enforced workflow 主要提升 failure diagnosis 和 ablation quality；
- skill library 对跨任务迁移贡献最大；
- naive Claude Code 倾向于过度添加高级模块；
- physical-prior workflow 能减少无效复杂度，但不一定提升短期 success rate；
- human gates 对 design rule quality 很关键。

这类发现比“框架跑通了”更有技术探索价值。

---

## 12. 开发路线建议

### Phase 1: Fixed Workflow Validation

目标：验证固定 workflow / prompt / skill 是否有效。

配置：

- no cross-task self-improving；
- fixed benchmark seed；
- fixed evaluation rubric；
- controlled comparison groups。

重点问题：

- workflow 是否比 prompt-only 更稳定；
- skill library 是否带来迁移收益；
- agent 是否减少过度设计；
- agent 是否改善 failure diagnosis。

### Phase 2: Research Utility Deployment

目标：让系统真正帮助当前 physical AI 研究。

功能：

- 帮助把模糊研究想法转成 hypothesis；
- 自动生成 physical prior table；
- 生成 minimal prototype plan；
- 跑初步实验；
- 输出 failure report；
- 维护 design rule memory。

人类角色：

- 选择研究问题；
- 判断 task abstraction 是否合理；
- 审核 failure diagnosis；
- 接受或拒绝 design rule。

### Phase 3: Bounded Self-Improving

目标：研究 agent 是否能改进自身的 skill / workflow / evaluator。

允许更新：

- skill library；
- failure ontology；
- design rule library；
- experiment selection policy；
- evaluator examples。

不建议一开始更新：

- base model weights；
- unrestricted workflow；
- unreviewed long-term memory。

### Phase 4: Learned Critic / Taste Model

如果积累足够 human feedback，可训练或校准：

- idea evaluator；
- physical plausibility critic；
- minimality critic；
- failure attribution classifier；
- design rule ranker；
- experiment value estimator。

这比单纯依赖 LLM prompt reviewer 更可能产生稳定科研品味。

---

## 13. 当前最小实验计划

建议从小规模开始。

### Step 1: 构造 6 个任务

覆盖：

- 2 个 short-horizon manipulation；
- 2 个 long-horizon compositional task；
- 2 个 partial observability / memory / action abstraction task。

每个任务需要：

- task spec；
- expected physical priors；
- expected minimal architecture；
- known design trap；
- evaluation script；
- expert rubric；
- allowed resources / constraints。

### Step 2: 先跑 3 个组

- Group A: naive Claude Code；
- Group B: prompt-only；
- Group D: prompt + workflow。

每个任务每组至少 3 seeds。

### Step 3: 加 skill library

加入：

- Group E: prompt + workflow + fixed skill。

比较 skill 是否显著提升跨任务表现。

### Step 4: 分析结果

重点分析：

- 是否跑通；
- 是否识别 physical bottleneck；
- 是否过度加模块；
- 是否遗漏关键模块；
- failure diagnosis 是否正确；
- 是否提出有效 ablation；
- 是否形成可信 design rule；
- 人类需要介入多少次。

---

## 14. 对“科研 intuition”的现实判断

### 14.1 Agent workflow 不能凭空赋予科研直觉

Frozen foundation model + SOP / workflow 可以提升：

- 执行稳定性；
- 流程纪律；
- 实验覆盖；
- 失败记录；
- 设计空间搜索；
- 人类反馈组织。

但它很难凭空获得：

- 真正问题感；
- 长期科研品味；
- 强物理直觉；
- 对模糊问题的深层重构；
- 新范式创造。

这些通常需要：

- 高质量科研轨迹数据；
- 专家偏好数据；
- 失败案例数据；
- 实验反馈；
- learned critic / reward model；
- 甚至基模级别的 embodied / scientific reasoning 能力提升。

### 14.2 但 agent 可以外化并积累“研究直觉”

Agent 可以通过外部机制积累：

- case memory；
- failure memory；
- method applicability map；
- task-to-architecture mapping；
- human accepted/rejected design decisions；
- design rules；
- anti-patterns。

这不等于模型本身学会科研，但可以形成一个有用的外部 research memory system。

---

## 15. 最终建议

当前应优先做：

> fixed workflow + fixed skill + small-but-hard benchmark + human-gated evaluation。

暂时不应做：

> unrestricted self-improving scientist。

第一阶段最重要的问题是：

> 在相同 Claude Code / base model 条件下，physical-prior-guided workflow 和 skill 是否能让 agent 从“完成代码任务”提升为“做出更好的 physical AI 系统设计判断”？

如果答案是否定的，说明这个方向可能只是 SOP 工程封装。

如果答案是肯定的，那么后续再引入：

- long-term memory；
- self-improving skill；
- learned critic；
- human feedback based taste model；
- outer-loop automatic research agent。

一句话总结：

> 先验证 agent workflow 是否能改善 physical AI prototype design 的判断质量，再谈 self-improving 和自动科研。

