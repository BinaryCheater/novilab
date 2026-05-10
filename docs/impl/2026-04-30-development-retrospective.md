# 经验之谈

经过两天的开发，多次榨干两个 GPT plus 账号的额度，novilab 项目能以一个比较弱的功能跑起来了。不过还没做真实应用的检验测试，实际上还有很多待定/没想清楚的地方，需要一起想。

由于不熟软件工程，之前也没做过软件开发的工作，甚至不太算得上会编程，这也算是我的一次软件项目经理练习。

### 坑 1：
Agent 很会写代码，但 Agent 不会天然满足你的需求，你需要清晰的 spec，当你以为 spec 够清晰的时候，总是会有无穷细节出来填满你的注意力和 context。

### 坑 2：
我使用了 superpowers skill，这是广受好评 star 最多的软件开发 skill，他让我的开发进度变得高度有序、可靠、稳定，几乎不会报错，功能推进一板一眼。但代价就是进度很慢，一次只做很有限的 feature，我不清楚这是否符合 vibe coding 时代的作风。

### 坑 3：
重复造轮子。vibe coding 时代并不是不能重复造轮子，但重复造轮子会导致慢、出 bug、反复踩前人的坑。我用了 deepagents/langgraph 以及一些其他在定制 agent 中有效的开源项目，尽管如此在实现闭环的过程中，codex 仍然展现了强烈的 overdesign 倾向（ ai coding 中很普遍的现象，过度抽象、过度设计、过度包装），导致逻辑不清晰，我自己都搞不太明白怎么用了。

---

上次开发 GPU architecture agent 的时候为了快速实现 MVP，直接用 codex 做执行层，直接避免了全部的封装复杂度，直接关注核心问题闭环。而这次为了协作、复用、知识库、可审计、可自我迭代、可靠的自动化，进行了对 harness （agent 框架） 本身的探索，摸清了很多机制问题，但也踩了很多坑。

我现在觉得类似的 agent 不是 codex 的替代，而是 ralph loop 的替代。

Vibe coding 时代每个人都应该学会做产品经理......

---

回到这个项目本身，仍然有几个点需要结合实际进行探讨：

1. 现在出现了 overdesign 倾向，把有些 workflow 构造和管理的工作从上游接过来了，导致实现目标变得越来越复杂。需要 fallback，目前是想把 workflow、multiagent 相关的东西摘干净，只做一个中间层接口，具体逻辑交给上游，避免在这上面浪费时间，要不要直接 fallback 到 langgraph 配置甚至直接调用 codex，要看能不能满足需求。
2. Skills 承载面向实际任务（physical AI）与实际目标（发现先验）的能力，如何设计 skill，需要哪些 skill，是一个需要试的问题。目前还没做这方面。（不是越多越好，不能假设 ai 一定能迭代出来一个好的，如何约束）
3. 知识库如何设计。karpathy 的模式在规模大、联系弱的时候并不好用，可能需要一些新的技巧，比如类似[GitHub - garrytan/gbrain: Garry's Opinionated OpenClaw/Hermes Agent Brain · GitHub](https://github.com/garrytan/gbrain)这种。以及探索有没有什么速度很快理解能力够用的小模型能作为知识库管理的接口。
