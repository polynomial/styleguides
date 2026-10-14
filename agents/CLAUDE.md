@AGENTS.md
@.claude/rules/agent-pull-requests.md
@.claude/rules/assessments.md
@.claude/rules/behavioral-guidelines.md
@.claude/rules/coding-principles.md
@.claude/rules/context-research.md
@.claude/rules/deliverables.md
@.claude/rules/evidence-before-changing-code.md
@.claude/rules/evidence-integrity.md
@.claude/rules/finding-existing-patterns.md
@.claude/rules/finish-the-work.md
@.claude/rules/github-closing-keywords.md
@.claude/rules/investigation-contract.md
@.claude/rules/linking-references.md
@.claude/rules/local-environment.md
@.claude/rules/never-force-push.md
@.claude/rules/plan-pre-research.md
@.claude/rules/production-safety.md
@.claude/rules/resolve-addressed-threads.md
@.claude/rules/root-cause-proof.md
@.claude/rules/simple-english.md
@.claude/rules/sub-repo-agents-md.md
@.claude/rules/verify-before-complete.md
@.claude/rules/write-skill.md
@.claude/rules/writing-pull-requests.md

## Why this file exists alongside AGENTS.md

Claude Code reads `CLAUDE.md`. It does not read `AGENTS.md` as a rules source in the same way, and
it has no equivalent of Cursor's glob-scoped auto-attach for rule files. `@AGENTS.md` imports the
whole guide so a Claude Code session starts with the map and the habits; the lines above
additionally guarantee the how-we-work skills that `AGENTS.md` already asks every session to apply.
Reading a skill body is model-discretionary, so the obligation to read it has to live somewhere
that is not.

## Why the rule imports point at `.claude/rules/`

An `@` import resolves a literal path ending in `.md`. It silently ignores a `.mdc` path, a glob
(`@.agents/rules/*.mdc`), and a directory (`@.agents/rules/`). This was measured empirically on
Claude Code CLI 2.1.228 and has held since.

So `.claude/rules/<name>.md` is a committed symlink to the real rule file under `.agents/rules/`,
and the import points at the symlink. Each rule keeps exactly one copy, nothing is renamed or
moved. `.claude/rules/` is an extension adapter for one tool, in the same spirit as the
`.claude/skills` symlink. Cursor needs no such adapter: `.cursor/rules` symlinks the whole
directory.

Adding a rule? Add the symlink and the `@` line, or Claude Code will not see it:

```bash
ln -s ../../.agents/rules/<name>.mdc .claude/rules/<name>.md
```

An import naming a file that no longer exists is skipped silently and does not break the imports
after it, so this file fails by quietly missing a rule rather than by erroring. Keep the whole
loaded set under Claude Code's 150k-character limit; past it, the tail is dropped without a
warning.

## A monitoring tool is not a licence to poll GitHub

`AGENTS.md`'s Critical Rules forbid hand-rolling a loop that polls GitHub. Agent harnesses ship
worked examples of exactly that loop (`while true; do gh pr checks ...; sleep 30; done`). The
example is the proximate guidance at the moment you reach for the tool, which is exactly why it
gets followed: one session wrote eight such loops with the rule loaded the whole time, one of them
polling every 120 seconds for four hours because its exit condition was a human merging a pull
request.

A monitor tool remains the right tool for streaming a long-running command. Give it the
repository's own run-monitor script, which owns the poll interval and the deadline, rather than a
loop of your own. No hook enforces this, so the rule holds only if you follow it: a monitored
command never contains a loop around `gh` or `api.github.com`.

## A Bash call's own `run_in_background` is one mechanism, not two

Setting the Bash tool's `run_in_background: true` on a command that *also* ends in a shell `&`
backgrounds it twice. The tool reports "completed (exit code 0)" as soon as the wrapper shell
returns from launching the detached child, not when the real command finishes, so a long-running
command that later fails is already reported as a clean success, and the wrapper's own exit code
is the only one the tool call captured.

Use exactly one backgrounding mechanism: `run_in_background: true` on the foreground command, with
no trailing `&`. Trust a backgrounded call's own completion status only when the command whose
exit code matters is the last command executed in that call.
