# Phase 1.5 Kernel Adapter Skeleton Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add the kernel boundary needed to connect DeepAgents while keeping current tests deterministic and model-free.

**Architecture:** Keep the current deterministic runner as the `simple` kernel. Add a small kernel validation layer and a `deepagents` optional dependency skeleton. Extend prompt archives with cache-friendly parts and executor placeholders.

**Tech Stack:** Python 3.11+, uv, optional DeepAgents/LangChain dependencies, pytest.

---

## Tasks

1. Raise project Python requirement to `>=3.11`.
2. Add `deepagents` optional dependency group.
3. Add failing tests for `--kernel simple` and missing `--kernel deepagents` dependency.
4. Add `src/novi_lab/kernels.py`.
5. Add prompt part files and manifest.
6. Add `response.md` and `model_calls.jsonl` placeholders.
7. Verify with Python 3.12.
