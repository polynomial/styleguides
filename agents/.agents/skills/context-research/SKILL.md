---
name: context-research
description: MUST USE before the first query against the institutional-context tool, and at the start of any non-trivial planning, investigation, refactor, migration, feature, or incident task.
---

# Context Research

The institutional-context tool indexes pull requests, chat, tickets, docs, incidents and code
history across every repository. Skipping it risks duplicating a rejected approach, violating a
convention someone already argued for, stomping on in-flight work, or re-deriving a conclusion that
already exists.

## When to fire it

**At the start, in parallel.** A research query costs near-zero latency against your own first
step and frequently returns the answer key — the prior thread, the runbook, the incident with the
same fingerprint. Do not wait until you are stuck, and do not wait to be asked.

Triggers:

- Start of any planning, investigation, refactor, migration, or feature task.
- "Why does this exist?" or "why is it done this way?" — code cannot answer these.
- Behavior does not match the code. Check history before assuming the code is wrong.
- An unfamiliar class, service, endpoint, flag, config key, or error string.
- Before writing new code — the pattern, bug, fix, or helper may already exist (see
  [`finding-existing-patterns`](../finding-existing-patterns/SKILL.md)).
- An incident, alert, or outage. Connect affected systems to recent changes and prior fixes.
- Filtered activity lookups — "PRs merged last week in auth", "open incidents tagged ingestion".
- Before recommending a solution, to verify it was not already tried, rejected, or superseded.
- A referenced primary source you cannot open. Ask for it rather than concluding past it.

## The tools

| Tool | Use |
| --- | --- |
| A research query | Primary. Semantic and relational research across all sources. Query in plain language — a complete phrase of symptom, component and goal, not bare keywords. |
| A URL fetch | You already have the URL. Cheaper and deterministic, and returns hydrated content. |
| A conventions lookup | Team conventions the tool has extracted for an area. |

Where the research query takes an **effort** axis:

- `low` — a targeted lookup anchored on one entity, URL, file, or question.
- `medium` — exploratory, with no single anchor.
- `high` — planning, architecture, migration, incident retro, cross-system investigation. Default to
  `high` whenever you are producing a plan or design.

Where it takes a steering **instruction**, that shapes which results surface without changing what
is searched: "prefer design decisions and rejected alternatives over API docs", "prioritize incident
post-mortems", "focus on who owns this and recent changes".

## Leads, never verdicts

The institutional-context tool surfaces stale, superseded and simply wrong context — an old design
doc, an abandoned PR, a reverted decision. Use it to know **where to look** and **what to check**,
then prove every claim against current code or live evidence.

Nothing is fact on the tool's authority alone. If code confirms it, cite the code. If code
contradicts it, the code wins. If neither settles it, it stays an open question or goes to the
owner.

When the tool cites a primary source you cannot read, say so and ask. Never finalize a conclusion
past an unread primary source.

## When the deliverable is an answer, not a change

1. **Classify the question** — architecture, tradeoff, history, incident, or how-to. This picks the
   effort level and the follow-ups.
2. **Primary query** — one research query at `high`, or `medium` for a narrow history question,
   phrased as the real question.
3. **Follow-ups** — a URL fetch on the promising citations, the actual code for anything the
   answer asserts about current behavior, and one or two `low`-effort re-angles if the primary pass
   missed a facet.
4. **Synthesize with citations** — inline citations on load-bearing claims, plus a short Sources
   list. Label inference as inference, and never present an uncited claim as established fact.

Abort and say so when the sources genuinely conflict or the question needs an owner's judgment. A
cited "here is the conflict, here is who can resolve it" beats a confident synthesis.
