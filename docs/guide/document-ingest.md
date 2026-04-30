# 文档导入

文档导入用于把用户或协作者提供的材料保存为 artifact，并交给 agent 分析、整理、提出合并方案。

## 基本用法

```bash
novi ingest notes.md --hint "这份材料可能和接触先验有关"
```

多文件：

```bash
novi ingest note-a.md note-b.md --hint "把这些实验观察整理进知识库"
```

挂到 task：

```bash
novi ingest notes.md --task task_... --hint "作为这个研究任务的背景材料"
```

## Target 是否必须手动指定

不必须。默认主路径是不指定 `--target`，让模型根据 hint、导入内容和知识库上下文判断：

- 是否应该修改已有文档；
- 是否应该创建新文档；
- 是否只提出问题或 integration plan；
- 是否产生多个 proposal。

只有当你明确知道目标文件时，才使用：

```bash
novi ingest notes.md --target .novi/knowledge/topics/physical-priors.md
```

## 输出协议

DeepAgents 路径会把 WorkflowSpec、document skills、hint、导入文档和库上下文放进 prompt。模型可以写 working files：

```text
/analysis_note.md
/integration_plan.md
/proposed.md
/proposals.json
```

也可以返回 JSON：

```json
{
  "analysis_markdown": "...",
  "integration_plan_markdown": "...",
  "proposals": [
    {
      "path": ".novi/knowledge/topics/example.md",
      "rationale": "...",
      "proposed_markdown": "..."
    }
  ],
  "questions_for_human": []
}
```

Novi 会把 analysis 归档为 artifact，把 proposals 转成 `document_patch` contributions。

## Review

检查：

```bash
novi review --check
```

让 deterministic reviewer 做初审：

```bash
novi review --check --agent
```

接受安全 proposal：

```bash
novi accept --reviewed
```

## Source 要求

Agent 产生的 patch contribution 要求严格 source refs。人类来源可以放宽，但仍应保留 attribution。

