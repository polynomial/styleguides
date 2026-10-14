# Fix Recommendations Template

## Summary

Root cause stance (Confirmed / Likely), current impact, and top recommended next action.

## Immediate Mitigation

Recommendations for on-call / ops (not actions for the fix author to execute in production). For each option:

- Action
- Blast radius
- Time to effect
- Rollback / revert path
- Verification signal
- Historical notes (if tried before)
- Owner: production on-call vs the fix author vs customer support

## Root Cause Fix

For each option:

- Approach, with paths and build targets verified against the repo
- Why it addresses the cause
- Risk / regression history
- Test plan sketch (unit / end-to-end)
- Suggested follow-on: an implementation plan, before any diff

## Prevention

Monitoring, alerts, tests, runbooks, killswitches, guardrails.

## Explicitly Rejected Options

Approaches considered and why not (cite prior incidents/PRs).

## Handoff

- Live prod still burning → the production on-call investigation procedure
- Durable code change → an implementation plan, then the repo's own development workflow
