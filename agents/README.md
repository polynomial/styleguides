# Agents

A way of working for AI coding agents, as a drop-in set of rules, skills and reference docs for
your repository. It is distilled from one engineering organisation's agent configuration, with the
company, its products, vendors, hosts, tickets and in-house commands removed. The gates, the
procedures, the Forbidden lists and the measured origin of each rule are what transfers.

Read first:

- [docs/agent_way_of_working.md](docs/agent_way_of_working.md): the whole discipline in one
  document. Each section is a gate an agent passes before a kind of action, with the specific
  evasions agents reached for named in its Forbidden list.
- [docs/cross_tool_ai_guidance.md](docs/cross_tool_ai_guidance.md): where guidance files live and
  how Cursor, Claude Code and the others load them, and why no tool owns the canonical copy.

## What is here

```text
agents/
  AGENTS.md                     universal entry point (Cursor, Codex, Gemini CLI, and others)
  CLAUDE.md                     Claude Code entry point: @AGENTS.md plus one @ line per rule
  .agents/
    rules/*.mdc                 24 always-on gates, each a floor plus a pointer to a skill or doc
    skills/<name>/SKILL.md      24 skills in the Agent Skills layout
  .claude/
    rules/<name>.md -> ../../.agents/rules/<name>.mdc    one symlink per rule (see CLAUDE.md)
    skills -> ../.agents/skills
  .cursor/
    rules -> ../.agents/rules
    skills -> ../.agents/skills
  docs/
    agent_way_of_working.md     the distillation
    cross_tool_ai_guidance.md   the layout and why
    investigations.md           how an investigation runs and is written up
    agent-evals.md              measuring an agent honestly; blind skill tests
    runbooks/                   production changes, secret-safe diagnostics, declarations
```

The skills, grouped by when they load:

| Before you act | Before you write code | Before you say done | Operations | Writing for others | Meta |
| --- | --- | --- | --- | --- | --- |
| behavioral-guidelines | coding-principles | verify-before-complete | oncall-investigation | simple-english | write-skill |
| context-research | finding-existing-patterns | agent-self-eval | rca-writing | writing-pull-requests | skill-from-conversation |
| plan-pre-research | reading-before-changing | prove-it-on-a-second-input | production-deploy-monitoring | writing-status-updates | doc-toc |
| evidence-before-changing-code | | root-cause-proof | monitoring-gap-analysis | linking-references | |
| | | | architecture-assessment-evidence | pr-comment-merge-policy | |

## Adopting it

1. Copy the contents of this directory (including the dot-directories and the symlinks) to the
   root of your repository. Symlinks are relative and survive the copy; `cp -R` on macOS and
   `cp -a` on Linux keep them as links.
2. Replace the **Platform map** section of `AGENTS.md` with your own: the repositories this one
   routes to, your environments, your shared commands. Everything else in the file is the
   discipline and does not need editing to be true.
3. Start a session in Claude Code or Cursor and confirm the rules loaded: ask the agent to name the
   always-on rules in effect. Claude Code reads `CLAUDE.md` and the `@` lines; Cursor reads
   `.cursor/rules`. Other tools read `AGENTS.md` and discover the skills through `.agents/skills/`.
4. Keep the loaded set under Claude Code's 150k-character limit for `CLAUDE.md` plus everything it
   imports. Past it, the tail is dropped without a warning.
5. Then do what the origin did: write the next rule only when an incident of your own tells you
   to, record the date and the measurement in it, and put the sentence the agent used to get past
   the gate in its Forbidden list. The eight steps in
   [Adopting this](docs/agent_way_of_working.md#18-adopting-this) say the rest.

A few rules name things your repository must supply before they bind: a run-monitor script for CI
runs, a monitor for the automated reviewer, a pinned tool environment, an institutional-context
tool. Where you have no such thing, the rule's Forbidden list still holds (no hand-rolled poll
loop, no self-merge, no interactive shell), and the pointer is a gap for you to fill.

## Keeping it company-agnostic

The origin checks every file here against this grep before publishing; the only hits allowed are
generic words used generically:

```bash
/usr/bin/grep -rniE 'extole|pluribus|showtime|unblocked|coderabbit|pagerduty|grafana|loki|jira|slack|intercom|sentry|hbase|kafka|bin/e-|nix-shell' agents/
```
