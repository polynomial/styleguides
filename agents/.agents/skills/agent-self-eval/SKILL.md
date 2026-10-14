---
name: agent-self-eval
description: Must be read after a substantive turn that hit friction, when the user asks to capture or remember what worked, and after they ask to push a work branch.
---

# Agent self-eval

Detect friction, capture what worked, and turn the reusable part into concise repository guidance —
without retaining transcripts, and never on the user's work branch.
[`verify-before-complete`](../verify-before-complete/SKILL.md) step 6 is the every-task floor, a
two-sentence closing self-eval. This skill is the mechanism once that self-eval, or a session's
signals, surface something worth persisting.

## Goals and non-goals

1. Name reusable failure modes without building a transcript warehouse.
2. Propose the smallest durable update that prevents recurrence.
3. Keep guidance changes off the user's work branch and off the critical path of their push.

Never: score people or productivity; retain full transcripts; persist secrets, customer data,
credentials, or payloads; delay the user's requested push or pull request; commit, push, or open a
pull request the user has not authorized; edit shared guidance as a side effect of the task that
taught the lesson.

## Triggers

| Trigger | Action |
| --- | --- |
| A substantive turn meets a threshold below | Diagnose the friction; propose durable guidance when warranted |
| The user says looping, stuck, MCP failed, too slow, or gives negative feedback | Treat as a threshold hit |
| The user asks to capture, remember, or make a skill or rule from a successful conversation | Run the success capture below |
| The user asks to push or open a pull request for work branch `XXX` | Finish that first, then run the push-time harvest |

A bare push is enough to *evaluate*, never enough to *persist*. If no threshold fires and nothing
reusable exists, stay silent.

## Failure thresholds

| Signal | Threshold |
| --- | --- |
| `mcp_error` | One hard MCP or tool failure this turn, or the same tool fails twice in the session |
| `loop` | The same tool and arguments three times, or two retries producing no new evidence |
| `tool_thrash` | Tool calls in one turn that kept producing no new evidence toward the request |
| `wrong_context` | Work used the wrong repository, module, service, or API, or the user corrected a fundamental premise |
| `wrong_owner` | A public service or boundary-owning interface gained behaviour outside its established purpose |
| `ignored_guidance` | Violating `AGENTS.md` or an active skill caused rework |
| `cost_spike` | The turn was disproportionate to the request |
| `user_friction` | Explicit negative feedback on the agent run |

Evaluate `tool_thrash` per user turn; one wait or monitor mechanism is not repeated polling. A
threshold hit still yields no durable update when the cause is a transient external failure, or a
definitive permission boundary with no reusable recovery.

## The self-eval record

```text
Self-Eval
  outcome:    ok | friction | failed
  signals:    [mcp_error | loop | tool_thrash | ...] | none
  severity:   0-3
  evidence:   <one to three sanitized bullets>
  guidance:   none | one sentence
```

Severity 0 means no friction. In session: name the threshold and severity, cite sanitized evidence,
separate a reusable process failure from a transient tool failure, and find the guidance that
already owns the behaviour — if it exists, explain the missed application rather than duplicating
it. Ask before writing shared guidance unless the user already asked for that update.

## Success capture

Confirm the success signal first: "this worked", "capture this", "make a skill". A bare "commit it"
is not one.

Use only the current conversation or a transcript the user names. Keep candidates that generalise
beyond the file at hand, corrected an agent mistake, reflect a team convention, or would prevent a
likely defect. Reject what is client-specific, short-lived, speculative, or already covered. Propose
before editing shared files unless the user asked for the edit.

## Routing a lesson

| Finding | Destination |
| --- | --- |
| Always-applied repository standard or safety constraint | The repo's `AGENTS.md`, or an always-on rule where the repo keeps them |
| Repeatable workflow or recovery procedure | An existing `.agents/skills/<name>/SKILL.md` first; a new skill only for a distinct workflow ([`write-skill`](../write-skill/SKILL.md)) |
| Cross-repository working practice | The repository that owns the how-we-work skills, where the organisation keeps one |
| Detailed reference | The repo's docs, linked from the owning skill |
| Personal preference | The repo's local, uncommitted personal-rules location; never a shared file |
| One-off flake or task detail | Do not persist |

Prefer updating an existing owner over creating overlapping guidance. Shared guidance is
operational and short: the instruction, its trigger, and — only where the rule would otherwise look
arbitrary — the one fact that makes it necessary. No incident narrative, no user names, no
conversation dumps. The story belongs in the pull request.

## Push-time harvest

After the user's push or pull request is complete, never before and never blocking it:

1. Build a **Session Friction Brief** from this conversation only: source branch `XXX`, the session
   goal in one sentence, the signals and severity, sanitized evidence bullets, candidate guidance
   updates, the existing guidance paths that nearly cover the failure (from the repo's `AGENTS.md`
   and its `.agents/skills/` descriptions, not a crawl of sibling `SKILL.md` bodies), and an
   authorization object stating whether the user explicitly authorized commit, push and pull request
   for the *separate* guidance change. That is `false` unless they said so in those words. Personal
   rules that forbid follow-up agents, commits, pushes or PRs end the harvest before it starts.
2. Severity 0 with nothing reusable: skip, and say so in one line.
3. **Name the harvest branch:** the source branch with every `/` replaced by `-`, runs of `-`
   collapsed, plus `-skill-updates` (`feature/foo` → `feature-foo-skill-updates`). If the sanitized
   name already ends in `-skill-updates`, do not harvest. Use that one name for the branch, the
   idempotency check, and what you tell the user.
4. Launch a **background** agent with the brief embedded in its prompt — it does not inherit the
   conversation — and return to the user at once, saying only that the harvest started and what it
   may open.

The background agent, in order:

1. **Survey the open harvests first, and again just before opening or updating the PR.** List every
   open pull request labelled `agent-skill-updates` (with `changedFiles` beside the listed `files`,
   which caps at 100 — page `pulls/<n>/files` when they differ) and every open PR whose head is the
   harvest branch, since a label is not guaranteed. Read the diff of each whose files **or title**
   touch the brief's subject: two harvests are the same learning when they prescribe behaviour for
   the same trigger, whatever their source branches. Same learning → join it, pushing the delta to
   its `-skill-updates` head and never a human's feature branch, or comment that this session
   reproduced it and return `no PR: covered by #<n>`. Wrong or weaker → review it with this
   session's evidence and return `no PR: reviewed #<n>`. A survey that cannot be completed returns
   `no PR: harvest survey unavailable`. Five parallel harvests of one learning with three
   inconsistent recipes is the case this exists for (measured 2026-08-15, in one repository's run
   of sixteen harvest pull requests opened in a day).
2. **Work in an isolated worktree**, never the feature checkout and never `git stash` to make room.
   Resolve the repo's default branch rather than assuming `master` (some repos are on `main`):
   `git fetch origin`, `git remote set-head origin --auto`, then read `<default>` from
   `git symbolic-ref --short refs/remotes/origin/HEAD`. Then
   `git worktree add -b <harvest> <path> origin/<default>`. For an existing remote harvest branch,
   fetch it, add the worktree on the local branch (or `-b … origin/<harvest>` when none exists) and
   `git merge --ff-only origin/<harvest>` inside it. A refused fast-forward is divergence: stop and
   report, never force. Keep an existing branch's history and iterate on it; recreate from
   `origin/<default>` only when its tip carries non-guidance paths.
3. **Touch only agent-guidance paths**: `.agents/skills/**`, the repo's rules and shared agent
   markdown, `.cursor/rules/**`, `AGENTS.md`, `CLAUDE.md`, the repo's root agent reference docs.
   Never production source, tests, build files, CI, feature commits from the source branch, or
   personal rules. Cite product paths in skill text; never edit them for a citation. Prefer updating
   the skill the brief named over adding one.
4. **Prove it before the PR opens or updates**: `git fetch origin` and
   `git diff --name-only origin/<default>...HEAD` must succeed, else `no PR: diff gate could not run`,
   and every path must be in the set above, else fix the branch or return `no PR: non-guidance files
   in harvest diff`. Never open a contaminated PR for humans to sort out.
5. **Open or update the PR** from the harvest branch into `<default>`, never stacked onto the source
   branch, titled `skill-updates from <source>: <short failure theme>`, labelled
   `agent-skill-updates` (create it with color `5319E7` if missing — no label, no PR). The body
   gives the friction signals, what this iteration adds over prior harvest commits, the files, the
   source branch, and that merging is optional human review. Push with `git push -u origin HEAD`
   and never force push ([`never-force-push`](../../rules/never-force-push.mdc)). To bring an
   existing harvest branch up to date, merge `origin/<default>` into it rather than rebasing.
6. Return the PR URL, or `no PR: <reason>`. The foreground reports a guidance pull request only when
   that URL comes back, and never presents a task identifier as a link.
