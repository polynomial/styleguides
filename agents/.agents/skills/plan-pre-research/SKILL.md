---
name: plan-pre-research
description: MUST USE before CreatePlan, before switching to plan mode, and before presenting an implementation blueprint for approval.
---

# Plan pre-research

## Gate

**Do not write the plan (Cursor `CreatePlan`, Claude Code plan mode, or a final implementation blueprint presented for approval) until every unknown that can be resolved with available read-only tools has been resolved.**

Resolvable means: repo grep/glob, git log/blame, reading source and API docs, MCP read-only queries (the metrics system, AWS, Kubernetes, the institutional-context tool, the ticket tracker, and so on), or replaying a single failing request with corrected inputs.

## Procedure (run before writing the plan)

1. **List decisions the plan would otherwise defer** — parameter names, which file to change, scope counts, API semantics, which branch/PR, merge blockers.
2. **Resolve each with evidence** — cite file paths, grep results, commit SHAs, or tool output. One-line ADR per non-obvious choice.
3. **User-only choices** — if two paths are genuinely equal and preference is the user's, ask the user **now** (headless: pick the default and record it), not inside the plan.
4. **Self-check** — scan the draft plan for forbidden phrases (below). If any remain, keep researching or deciding; do not publish.

## Forbidden inside plans

Plans must not contain phases or todos that defer knowable work:

- "investigate…", "research…", "figure out…", "look at…", "decide after test", "compare X vs Y then choose"
- "needs context", "TBD", "pending research", "validate viability in plan"
- Todos named `test-*` / `decide-*` / `investigate-*` when the answer is obtainable before planning

**Plan todos are implementation and verification only** — edit files, run named tests, push, open PR, post-merge checks.

## Required plan content

Each deliverable in the plan still needs:

1. Exact files and diff-level code sketches
2. Named quality gates (commands, test files, CI checks)
3. Merge path (branch, target, approvals)
4. Post-merge verification

Pre-research supplies **decided outcomes and citations** inside those sections — not open questions.

## Examples

**Bad (research left in plan):**

> Phase 0: Grep the server repository for `client_access_token` vs `access_token`, then decide whether to keep the rename.

**Good (research done, plan is blueprint):**

> Keep `access_token` — `QueryParameterAccessTokenExtractor` only reads `access_token` (server repository). No code change; reply on review thread with citation.

**Bad:**

> Todo: investigate whether `useBuiltComponentsByIds` exists.

**Good:**

> Refactor `useFilteredViewIdsBySuperUser` to call `useBuiltComponentsByIds` from `src/resources/components/composables/useBuiltComponentsByIds.ts` (see plan code block).

## Composes with

- **The plan-writing procedure** — whatever writes the plan once this gate is satisfied: hydrate,
  draft with context inlined, owner intent, validate, present
- A repository's own always-on `plans-are-blueprints` rule, where it carries one — validation before plan; this skill is the **procedure** for that validation
- **Switching to plan mode** — run this skill's procedure before switching, or before writing the plan
