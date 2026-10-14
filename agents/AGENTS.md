# Agent Operations Guide

This file is the entry point for any AI coding agent working in this repository. It is an index.
The procedures live in the skills under [`.agents/skills/`](.agents/skills/), the always-on gates in
[`.agents/rules/`](.agents/rules/), and the long-form knowledge in [`docs/`](docs/). Replace the
bracketed placeholders with your own platform map; leave the habits and the rules alone until an
incident of your own tells you to change one.

## The Golden Road

Agents start here. This repository holds the **how-we-work skills**: the discipline that applies to
any task in any repository. A repository this one routes to holds only what is its own: its domain
knowledge, its mechanics, its conventions. This file owns *how* work is done, plus whatever
cross-repository surfaces no single repository can own.

Working from here means four habits:

1. **Route to the owning repository, then follow its rules.** Find where the work belongs. When you
   dive into any repository, read its `AGENTS.md`/`CLAUDE.md` and browse its `.agents/skills/`
   first, and follow them for everything inside it: that repository's standards govern its files;
   this file governs the crossing.
2. **Research before you rediscover.** Fire a query at your institutional-context tool at the start
   of any non-trivial task, in parallel with your first concrete step. See
   [`context-research`](.agents/skills/context-research/SKILL.md). The why, who, and when behind the
   code live there, not in the code.
3. **Don't invent a second way.** Find the existing pattern for how something is done and use it.
   See [`finding-existing-patterns`](.agents/skills/finding-existing-patterns/SKILL.md). New
   patterns are deliberate decisions, never side effects.
4. **Gate your work.** Reasoning discipline before you act
   ([`behavioral-guidelines`](.agents/skills/behavioral-guidelines/SKILL.md)), shared code
   discipline before you write ([`coding-principles`](.agents/skills/coding-principles/SKILL.md)),
   research before you plan ([`plan-pre-research`](.agents/skills/plan-pre-research/SKILL.md)),
   proof before you name a root cause
   ([`root-cause-proof`](.agents/skills/root-cause-proof/SKILL.md)), verification before you say
   "done" ([`verify-before-complete`](.agents/skills/verify-before-complete/SKILL.md)).

## How-We-Work Skills

The skills live under [`.agents/skills/`](.agents/skills/) ([Agent Skills](https://agentskills.io/)
layout; `.claude/skills` and `.cursor/skills` symlink there), and every `SKILL.md`'s frontmatter
`description` states when to use it. Tools that support the standard surface them automatically;
when yours does not, list that directory and read the descriptions before concluding no skill
covers your task. This file deliberately keeps no index of them: a second copy of each description
drifts from the skill it summarizes.

Discovery only tells you a skill exists. What makes one **mandatory** is stated here: the four
habits above, the Critical Rules at the end of this file, and, for each skill an always-on rule
gates, the matching rule in [Rules](#rules) below.

## Rules

Skill loading is model-discretionary: a tool surfaces a skill's name and description, and the model
decides whether the task matches closely enough to read the body. For the skills this file asks
every session to apply unconditionally, that discretion is exactly the gap: the obligation to read
them needs a mechanism that is *not* discretionary.

Always-on rules live under [`.agents/rules/*.mdc`](.agents/rules/) (`alwaysApply: true`). Cursor
reads them through the `.cursor/rules` symlink. Claude Code pulls them via `@` imports in
[`CLAUDE.md`](CLAUDE.md), each pointed at a `.claude/rules/<name>.md` symlink (Claude Code's `@`
import does not resolve a `.mdc` path, a glob, or a directory; see `CLAUDE.md`'s own note). Each
rule is a short gate plus a pointer to the skill's full procedure, never a copy of it. The skill
remains the single source of the procedure; the rule only guarantees the skill gets read.

Three shapes of rule are worth knowing:

- **A gate on a whole skill.** `behavioral-guidelines`, `coding-principles`,
  `finding-existing-patterns`, `evidence-before-changing-code`, `verify-before-complete`,
  `root-cause-proof`, `plan-pre-research`, `context-research`, `write-skill`, `simple-english`,
  `writing-pull-requests`, `linking-references`, `assessments`.
- **A gate on one section of a skill**, because that decision comes up mid-turn, long after the
  skill's trigger has passed: `never-force-push` and `resolve-addressed-threads`.
- **A fact or a contract with no skill behind it**, which every session needs before it acts:
  `github-closing-keywords` (a closing keyword before a reference is a command GitHub executes on
  merge, in any repository), `sub-repo-agents-md` (read the target repository's own agent config
  first), `investigation-contract`, `production-safety`, `evidence-integrity`, `finish-the-work`,
  `deliverables`, `agent-pull-requests`, `local-environment`.

The writing rules (`simple-english`, `writing-pull-requests`, `linking-references`) are rules
because their trigger is invisible: an agent about to open a pull request, or about to write a
ticket, does not know a skill governs the text, so it writes its own defaults, and those defaults
are a log of the session that produced the change.

Adding a new always-on rule: create `.agents/rules/<name>.mdc`, symlink it into
`.claude/rules/<name>.md`, and add the `@` import line to `CLAUDE.md`. Cursor needs no step. Keep
the whole loaded set under Claude Code's 150k-character limit.

## Platform map

[Replace this section. It is the part of this file that is yours: the repositories this one routes
to and what each owns, the environments and what each is for, the shared commands and what they
do. Keep it a map, not a manual: the workflow for each item lives in a skill. Two behaviours the
origin of this file learned to write down here: a command whose effect is not visible from the
call site (a name that gets normalised, an account that is always your own), and a tool whose
documented example shows a pattern the rules forbid.]

## Reference docs

Long-form guides live under [`docs/`](docs/). Use the skill for your task first, since it links to
the right one. The cross-cutting ones:

- [docs/agent_way_of_working.md](docs/agent_way_of_working.md): the whole discipline in one
  document, each section a gate, with the measured origin of each rule.
- [docs/cross_tool_ai_guidance.md](docs/cross_tool_ai_guidance.md): where guidance files live and
  how each tool loads them.
- [docs/investigations.md](docs/investigations.md): how an investigation runs and is written up:
  order of work, mitigation ranking, proof bar, package layout, decision log, decision records.
- [docs/agent-evals.md](docs/agent-evals.md): measuring an agent honestly; blind skill tests.
- [docs/runbooks/](docs/runbooks/): production changes, secret-safe diagnostics, declarations and
  manifests.

## Where to add guidance

- **Always-on constraint:** add it to the closest `.agents/rules/*.mdc` as a gate plus a pointer. A
  new rule file also needs a `.claude/rules/<name>.md` symlink and an `@` line in `CLAUDE.md`.
- **Repeatable workflow:** `.agents/skills/<name>/SKILL.md`, per
  [`write-skill`](.agents/skills/write-skill/SKILL.md).
- **Deep reference:** a new or extended document under `docs/`, linked from a skill.
- **A quick command cheatsheet:** the platform map above.

## Critical Rules

Invariants of this repository. They have no skill behind them: read them here.

- **Infrastructure is immutable and CI-managed.** Changes to infrastructure are made in code,
  reviewed in a pull request, and deployed by CI. Never run an infrastructure tool imperatively
  against a live environment. Make the code change, push to a branch or open a PR as requested,
  and let CI take it from there.
- **Read a repository's `AGENTS.md` before working in it.** When a task involves any repository
  this one routes to, read its `AGENTS.md` before starting work. It carries structure, deploy model,
  and conventions not covered here.
- **Execute necessary follow-ons; don't just name them.** When your own work surfaces something
  the task genuinely needs (missing test coverage for the behavior you changed, a doc your change
  made stale, a cleanup your change orphaned), do it in the same session, or ticket it if it can't
  be done now. Identifying a necessary follow-on and then merely offering it back wastes a round
  trip on work that was never optional. Reserve the question for genuine scope decisions,
  destructive actions, and alternatives the user must pick between.
- **A closing keyword before a GitHub reference is a command, not a description.** `fix`, `close`
  or `resolve` (any tense) directly before `#N`, `owner/repo#N`, a URL or a markdown link, in a
  pull request body, title or commit message, closes that issue or pull request when the text
  merges, across repositories. Say `opened as <link>` or wrap the reference in a code span.
  Always-on rule: [`github-closing-keywords`](.agents/rules/github-closing-keywords.mdc).
- **Never hand-roll a loop that polls GitHub.** For an Actions run, call the run-monitor script
  your repository provides, which owns the poll interval and the deadline. For anything else
  GitHub exposes (checks, review state, comments, whether a pull request has merged) **do not
  watch it at all**: read it once when you need it. A hand-rolled loop gets both wrong in the same
  direction: it polls fast enough to eat into an API budget shared by every workflow and agent in
  the organisation, and it waits on a condition that can never arrive. A run that was never
  dispatched is indistinguishable from a running one, and has been waited on for about twenty
  hours.
  - **The tell is a loop and `gh` in the same script.** If you are writing `while true`, `until`,
    or a `sleep` next to a `gh` or `api.github.com` call, stop and use the script instead.
  - **Your tooling's own examples may show the prohibited pattern.** Agent harnesses ship worked
    examples of exactly this loop. Those examples are not sanctioned here; this rule wins.
  - **A watch's exit condition must be reachable without a human.** Waiting for a pull request to
    be merged or approved is not a terminating condition; a background watch set on one runs until
    somebody notices. Watch the run, then stop.

## Skills

Read the skill **before** starting the work it covers, not after. Its own description states when
that is. This file keeps no second copy of the list, because a copy drifts from the skill it
summarises.

**A repository's own skills govern inside that repository.** When the work is in another
repository, that repository's definition of a capability overrides and appends to this one's: read
this repository's, then the other's, and where they differ the other's wins for work done there.
This holds for every skill, which is why none of them say so.
[`write-skill`](.agents/skills/write-skill/SKILL.md) owns how to write one.
