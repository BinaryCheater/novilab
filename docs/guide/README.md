# Novi Lab 说明文档

这个目录放面向使用者和维护者的说明文档。它解释 Novi 的设计逻辑、当前功能、使用方式和预期行为；开发记录应放在 `docs/impl/`，规格草案应放在 `docs/spec/` 和 `docs/spec_zh/`。

## 推荐阅读顺序

1. [核心概念](concepts.md)
2. [快速开始](quick-start.md)
3. [配置说明](configuration.md)
4. [YAML 配置](yaml-config.md)
5. [CLI 说明](cli.md)
6. [Workflow 模型](workflows.md)
7. [Research Loop](research-loop.md)
8. [文档导入](document-ingest.md)
9. [Review 与 Artifacts](review-and-artifacts.md)
10. [故障排查](troubleshooting.md)

## 当前主线

Novi 当前最重要的闭环是：

```text
task objective
-> workflow step
-> model/kernel run
-> artifacts and trace
-> optional proposals
-> review gate
-> accepted state enters later context
```

用户应该主要关注研究目标、导入材料、review 决策和高层文件。低层 id、patch、trace、JSONL 记录用于审计和排错，不应成为日常使用负担。
