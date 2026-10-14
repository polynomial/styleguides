# Investigation Plan Template

## Incident Summary

Symptom, severity, blast radius, start time, sources.

## Related Work Already In Flight

Existing investigations, chat threads, on-call docs, open PRs.

## System Context

Short architecture notes with citations; module paths verified against the repo (use its module map where it keeps one).

## Ranked Hypotheses

For each (3–5):

| Field | Content |
| ----- | ------- |
| Statement | |
| Supporting evidence | |
| Confirm | Steps / queries |
| Disconfirm | Steps / queries |
| Owner track | A / B / C |

## Parallel Investigation Tracks

Tracks that can run concurrently without stepping on each other.

## Escalation Triggers

When to hand to the production on-call investigation procedure, when an on-call owner should page, when to notify customer support. This procedure does not page.

## Next Skill

the **Gather evidence** stage of [`root-cause-proof`](../SKILL.md) with this plan as recommended input.
