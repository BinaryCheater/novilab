# Phase 1.3 LLM Connect Ready Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Prepare Novi for a real LLM executor by making agent configuration and read-only tool execution usable through CLI-controlled runtime boundaries.

**Architecture:** Extend `agents.py` with small update helpers for list fields and model profile assignment. Extend `tools.py` with deterministic local read-only adapters and a manual call path. Keep CLI commands thin and keep all tool execution behind `execute_tool()`.

**Tech Stack:** Python 3.9+, argparse, PyYAML, subprocess for read-only git status, pytest.

---

## Tasks

1. Add failing tests for agent configuration commands.
2. Implement `grant-tool`, `revoke-tool`, `add-skill`, and `set-model`.
3. Add failing tests for manual tool calls through scope/policy.
4. Implement `filesystem.read`, `git.status`, and `novi tool call`.
5. Run full regression and smoke tests.
