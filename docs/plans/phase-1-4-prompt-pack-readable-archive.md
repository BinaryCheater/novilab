# Phase 1.4 Prompt Pack And Readable Archive Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make Novi ready for an LLM executor by writing human-readable prompt packs, timelines, and memory candidate companions while preserving structured YAML/JSONL ledgers where needed.

**Architecture:** Add a small prompt builder that compiles system instructions, run objective, active agent, context pack, skills, and visible tools into `prompt.md`. Keep `model_request.yaml` as the structured executor handoff, and add Markdown companions for event timelines and memory candidates.

**Tech Stack:** Python 3.9+, Markdown files, YAML metadata, JSONL ledgers, pytest.

---

## Tasks

1. Add failing tests for `prompt.md`, `model_request.yaml`, `timeline.md`, and `novi run prompt`.
2. Add failing tests for memory candidate `.md` companions.
3. Implement `src/novi_lab/prompts.py`.
4. Integrate prompt pack and memory Markdown writing into the deterministic runner.
5. Add `novi run prompt <run_id>`.
6. Run full regression and smoke tests.
