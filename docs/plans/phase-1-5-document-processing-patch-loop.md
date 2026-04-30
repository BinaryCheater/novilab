# Phase 1.5 Document Processing Patch Loop Plan

## Goal

Implement the first skill-driven document processing loop: an imported document
can be processed into an analysis note and, when the user provides an explicit
target, a reviewable document patch contribution that can be checked and
accepted without allowing silent edits.

## Scope

- Deterministic `document-merge` processing first.
- Target paths limited to `.novi/knowledge/`, `.novi/workflows/`, and
  `.novi/skills/`.
- Agent-generated patch contributions carry source refs from the import,
  source artifact, processing run, and analysis note artifact.
- Accept performs a check first, applies only when valid, and records merge
  metadata.
- If the target changed since patch generation, accept marks the contribution
  as `conflict` and does not modify the target.

## Tasks

1. Add tests for `novi process <contrib> --workflow document-merge --target <path>`.
2. Add deterministic processing records and artifacts.
3. Add `document_patch` contribution records with patch and proposed content.
4. Add `novi contribution check`.
5. Extend `novi contribution accept` to apply patch contributions.
6. Add `novi contribution request-changes`.
7. Verify full CLI test suite.

## Deferred

- Real LLM patch generation.
- External worker bundles.
- Workflow and skill patch target behavior beyond the same patch machinery.
- Automatic target selection.
