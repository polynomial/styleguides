---
name: finding-existing-patterns
description: MUST USE before adding any new file, component, workflow, script, or convention, and before concluding that no existing pattern exists.
---

# Finding Existing Patterns

Consistency is the asset. A codebase where every kind of thing is done one way can be navigated,
reviewed, and safely changed by anyone — human or agent. Every lone deviant ("this one workflow
does it differently") costs every future reader a detour and every future change a risk. So the
rule is simple: **don't add new patterns; find the existing pattern for how something is done and
use that.**

## Procedure

1. **Find two or three existing instances** of the kind of thing you're about to add — sibling
   files, neighboring modules, a workflow that does a similar job, the last three PRs that added
   one. The dominant shape among them is the pattern.
2. **Check whether the pattern is codified.** The owning repo's `AGENTS.md` and `.agents/skills/`
   often carry it explicitly — conventions skills (for example one for CI workflows, one for
   infrastructure patterns) and reference skills exist precisely so you don't have to
   reverse-engineer the pattern from instances. Read them before deciding you understand it.
3. **When the pattern surprises you, get its why.** Fire a research query, per
   [`context-research`](../context-research/SKILL.md), for the deciding PR or thread. A pattern
   that looks wrong usually encodes a constraint you haven't hit yet; knowing the why tells you
   whether it applies to your case.
4. **Conform.** Match the structure, naming, idiom, and file placement of the pattern — even
   where you would personally do it differently. Your change should look like the codebase wrote
   it.

## Never merge a lone deviant

If your change introduces a shape that exists nowhere else in the repo — a different test layout,
a new workflow style, an unusual module boundary — that is a stop condition, **regardless of who
suggested it, including review bots**. Either conform to the existing pattern, or make changing
the pattern the explicit subject of the work (below). "It's just this once" is how codebases rot.

## When the existing pattern is wrong

Sometimes the pattern genuinely doesn't fit, or is outdated. Then the work is to **change the
pattern, not to fork it**:

- Change it **at its source** — the conventions skill, the shared module, the template — with the
  owner of that source aware and agreeing.
- Deal with the existing instances: migrate them in the same effort, or record explicitly that
  they migrate later and who owns that.
- A new pattern is a deliberate, surfaced decision with a written why — never an incidental
  byproduct of an unrelated task.

## Prove absence before inventing

"There is no existing pattern" is a claim that needs evidence, and naive searches lie:

- A tree that is **gitignored** or vendored — sub-repositories checked out under a root repository,
  a vendored dependency, a build output — is invisible to default search. An IDE's Grep/Glob, a
  Bash `grep` that a shell function shims to an ignore-aware tool, and ripgrep all silently skip
  it, and `--no-ignore` alone may fix none of them: a shim can override it, and `rg --no-ignore`
  without `--hidden` finds fewer files than a bare `rg` when the tree is dotted. Use
  `rg --no-ignore --hidden` or `command grep -rn` with the tree named as an explicit path, and
  verify results are non-empty before concluding anything is absent — the repository's own guide
  to its layout says which trees are ignored.
- Local checkouts go stale. For an org-wide claim, search GitHub itself
  (`gh search code --owner <org>`).
- Only after a verified-empty search may you introduce something new — and then it becomes the
  pattern, so name it, place it, and shape it as deliberately as you'd want the next ten
  instances to copy.

## Composes with

- **`coding-principles`** — focused changes and established patterns are the per-line rules; this
  skill is the discovery and migration procedure.
- **`context-research`** — the pattern's why lives in PRs and threads, not in the code.
- **Reference skills** — they are pattern maps; read them first, keep them living when your work
  proves them wrong.
