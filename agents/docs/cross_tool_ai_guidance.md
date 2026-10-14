# Cross-Tool AI Agent Guidance: A Practical Philosophy

**Status:** Working model (April 2026), updated October 2026 for the `.agents/` layout and the Claude Code import limitation measured since. Company-agnostic. Share freely.

<!-- toc -->
## Contents

- [The Problem](#the-problem)
- [The Mental Model](#the-mental-model)
- [The Architectural Insight](#the-architectural-insight)
- [Decision Framework](#decision-framework)
- [The Agent Skills Standard](#the-agent-skills-standard)
- [Rules File Format](#rules-file-format)
- [Communicating the System to Your Team](#communicating-the-system-to-your-team)
- [Common Mistakes](#common-mistakes)
- [Migration Path for Existing Repos](#migration-path-for-existing-repos)

<!-- /toc -->


## The Problem

AI coding assistants are multiplying. Cursor, Claude Code, Codex, Gemini CLI, JetBrains Junie -- most teams now use more than one. Each tool has its own configuration system: `.cursor/rules/*.mdc`, `CLAUDE.md`, `AGENTS.md`, `.windsurfrules`, `.copilot-instructions.md`. The natural result is that teams either:

1. **Pick one tool and lock in.** Guidance lives in `.cursor/rules/` and Claude Code users get nothing.
2. **Duplicate everything.** The same coding standards exist in three formats, drift immediately, and nobody trusts any of them.
3. **Dump everything into one giant file.** A 2000-line `.cursorrules` or `AGENTS.md` that loads into every session regardless of relevance, wasting context and reducing adherence.

All three approaches fail as teams grow, tools change, and the guidance itself evolves.

## The Mental Model

AI agent guidance falls into three categories. Mixing them together is the root of most organizational problems.

### Rules

Small, persistent constraints that should always (or conditionally) be in context. Coding standards, safety prohibitions, naming conventions.

**Characteristics:**
- Under 50 lines
- Either always-applied or scoped to file patterns (e.g., `**/*.java`)
- The AI should never have to decide whether to read these -- they're either in context or not
- Changed infrequently

**Examples:**
- "Never use kubectl to restart pods"
- "Follow JAVA_CODING_STANDARDS.md when editing Java files"
- "Always check environment connectivity before deploying"

### Skills

Procedural workflows the AI follows when performing a specific task. Build-and-deploy steps, test execution recipes, incident investigation runbooks.

**Characteristics:**
- Under 500 lines
- Auto-discovered by description keywords -- loaded on demand, not always
- Invokable explicitly (`/build-deploy`) or triggered by context ("deploy my changes")
- Follow the [Agent Skills open standard](https://agentskills.io/) (`SKILL.md` with YAML frontmatter)
- Can bundle scripts, templates, and reference files alongside the instructions

**Examples:**
- "Build and deploy changes to a development environment"
- "Query a development environment's logs"
- "Investigate a pager alert end-to-end"

### Reference Documents

Large, detailed material that the AI reads on demand when a skill or rule points to it. Coding standards documents, architecture guides, environment capability matrices.

**Characteristics:**
- Over 200 lines
- Never loaded into every session -- too expensive in context
- Linked from skills and rules that say "read this before proceeding"
- Written for humans and AI alike

**Examples:**
- A 270-line Java coding standards document
- An environment connectivity guide with capability matrices
- Database access credentials and connection instructions

## The Architectural Insight

The key realization is that **no tool should own the canonical content**. Content should live in a tool-agnostic location, and each tool should consume it through its native mechanism.

```
.agents/                      <- canonical, committed to git
  rules/                      <- .mdc files with combined frontmatter
  skills/                     <- SKILL.md per the Agent Skills standard

.cursor/
  rules -> ../.agents/rules   <- directory symlink
  skills -> ../.agents/skills <- directory symlink

.claude/
  rules/<name>.md -> ../../.agents/rules/<name>.mdc   <- one symlink per rule
  skills -> ../.agents/skills <- directory symlink

CLAUDE.md                     <- @imports each .claude/rules/<name>.md
AGENTS.md                     <- universal index (Cursor, Codex, Gemini CLI)
```

### Why This Works

**Skills are trivially portable.** Both Cursor and Claude Code use `SKILL.md` with identical YAML frontmatter (`name`, `description`). This is the [Agent Skills](https://agentskills.io/) open standard, maintained by Anthropic and supported across tools. A directory symlink from each tool's skill location to `.agents/skills/` is all that's needed.

**Rules require a small adaptation.** Cursor needs `.mdc` files with `globs:`/`alwaysApply:` frontmatter for full activation control. Claude Code `@`-imports from `CLAUDE.md`, but an `@` import resolves only a literal path ending in `.md`: it silently ignores a `.mdc` path, a glob and a directory (measured on Claude Code CLI 2.1.228). So the canonical `.mdc` files in `.agents/rules/` serve Cursor directly (via the directory symlink) and Claude Code through one `.claude/rules/<name>.md` symlink per rule, each named by an `@` line in `CLAUDE.md`. One set of files, two consumption paths, and the per-rule symlink is the one piece of ceremony.

**The entry points are tool-specific, but minimal.** `CLAUDE.md` exists for Claude Code. `AGENTS.md` exists for Cursor/Codex/Gemini. These are thin shells -- a few imports and a quick reference table. The actual content lives in `.agents/`.

### The Trade-off

Claude Code loses its native `paths:` scoping for rules (since they're imported via `CLAUDE.md`, they're always-loaded). For most repos this is fine -- rules are small and few. If you have dozens of file-scoped rules, you'd need a different approach.

## Decision Framework

When an engineer wants to add new AI guidance to a repo, they should ask one question:

**"What kind of guidance is this?"**

- **A constraint the AI must always follow?** -> `.agents/rules/your-rule.mdc` with `alwaysApply: true`. Symlink it to `.claude/rules/your-rule.md` and add `@.claude/rules/your-rule.md` to `CLAUDE.md`.
- **A standard that applies to specific file types?** -> `.agents/rules/your-rule.mdc` with `globs: ["**/*.java"]`. Same symlink and `@` line.
- **A step-by-step workflow?** -> `.agents/skills/your-skill/SKILL.md`. Auto-discovered by both tools via symlinks. No extra step.
- **Deep reference material?** -> Root-level `.md` file. Link to it from the relevant skill or rule.
- **A quick command cheatsheet?** -> `AGENTS.md` quick reference table.

This framework should be documented in `AGENTS.md` itself so engineers encounter it naturally.

## The Agent Skills Standard

The [Agent Skills](https://agentskills.io/) specification is the cross-tool format for procedural workflows. A skill is a directory containing a `SKILL.md` file:

```
my-skill/
  SKILL.md           <- required: frontmatter + instructions
  scripts/           <- optional: executable code
  references/        <- optional: detailed docs
  assets/            <- optional: templates, schemas
```

The `SKILL.md` frontmatter is minimal:

```yaml
---
name: build-deploy
description: Build and deploy changes to a development environment. Use when
  building code, deploying changes, or redeploying a component.
---
```

The `description` field is critical -- it's how tools decide whether to auto-load the skill. Front-load the key use case. Be specific about trigger words.

Skills support progressive disclosure: the description (~100 tokens) is always in context for discovery, the full `SKILL.md` body loads only when activated, and reference files load only when the skill explicitly reads them.

## Rules File Format

Rules use `.mdc` (Markdown Cursor) format with YAML frontmatter. The same file works for both Cursor (via directory symlink) and Claude Code (via `@import` in `CLAUDE.md`).

```yaml
---
description: Safety constraints for AI agents
alwaysApply: true
---
# Prohibited Actions
- NEVER use kubectl to restart or recreate pods
- NEVER run the full end-to-end test suite in dev environments
```

Frontmatter fields:
- `description` -- helps the agent decide if the rule is relevant (Cursor uses this for agent-selected rules)
- `globs` -- file patterns that trigger the rule (e.g., `["**/*.java"]`)
- `alwaysApply` -- if `true`, included in every session regardless of context

## Communicating the System to Your Team

The `.agents/` directory should be self-documenting. Include a short `README.md`:

```markdown
# .agents/ — Cross-Tool AI Agent Configuration

This directory is the single source of truth for all AI agent guidance in this repo.
Both .cursor/ and .claude/ consume it via symlinks — never edit files in those directories directly.

  .agents/rules/    -> coding standards, safety constraints (.mdc files)
  .agents/skills/   -> procedural workflows (SKILL.md per the Agent Skills standard)

Adding a new rule: Create .agents/rules/your-rule.mdc, symlink it to .claude/rules/your-rule.md,
then add @.claude/rules/your-rule.md to CLAUDE.md.
Adding a new skill: Create .agents/skills/your-skill/SKILL.md. Both tools discover it automatically.
```

`AGENTS.md` should list every skill and rule with a one-line description so engineers can discover what's available without browsing hidden directories.

## Common Mistakes

**Putting procedural workflows in rules.** A 60-line build-and-deploy runbook is a skill, not a rule. Rules are constraints; skills are recipes. If your rule has numbered steps, it's probably a skill.

**Making skills too large.** If your `SKILL.md` exceeds 500 lines, split it. Move detailed reference material into `references/` files that the skill links to. The AI loads the full skill body on activation -- large skills waste context on irrelevant details.

**Forgetting the CLAUDE.md import.** When you add a new rule to `.agents/rules/`, Cursor picks it up automatically via the symlink. Claude Code does not -- you must add the `.claude/rules/new-rule.md` symlink and an `@.claude/rules/new-rule.md` line to `CLAUDE.md`. This is the one manual step in the system, and it fails silently: an `@` line naming a missing file is skipped without an error.

**Duplicating constraints in skills.** If a safety constraint matters (like "never use kubectl to restart pods"), it belongs in an always-applied rule, not buried in a skill that might not load. Skills can reference rules, but should not be the only place a constraint appears.

**Treating AGENTS.md as a dump.** `AGENTS.md` should be a lean index -- a quick reference table and links to skills/rules. It should not contain the full text of every workflow and standard. That's what skills and rules are for.

## Migration Path for Existing Repos

If you already have `agents-*.md` files or a large `.cursorrules`:

1. **Create the scaffold.** `.agents/rules/`, `.agents/skills/`, symlinks, `CLAUDE.md`.
2. **Start with one rule.** Extract your most critical safety constraint into `.agents/rules/prohibited-actions.mdc`. Validate it loads in both tools.
3. **Convert one skill.** Take your most-used procedural workflow and make it a `SKILL.md`. Validate auto-discovery.
4. **Migrate incrementally.** One file at a time. Keep old files alongside new ones until the team confirms the new system works.
5. **Clean up.** Update `AGENTS.md` to point to skills/rules. Delete the old `agents-*.md` files. Add the decision framework.

Don't try to migrate everything at once. Prove the symlink approach works with one rule and one skill before committing to the full migration.
