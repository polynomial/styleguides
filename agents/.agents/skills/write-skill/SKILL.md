---
name: write-skill
description: MUST USE before creating, renaming, moving, or materially editing any SKILL.md, in any repository.
---

# Write a Skill

Create skills that agents can discover at the right time and execute reliably without loading
unnecessary context.

## Choose the right artifact

A skill is reusable guidance for performing a capability or exercising judgment in a problem
space. Use a skill when an agent needs instructions at invocation time to:

1. decide when the capability applies;
2. perform it correctly;
3. produce or verify the expected result.

Do not use a skill for:

- an always-on safety or style constraint that belongs in repository rules or `AGENTS.md`;
- durable domain knowledge that belongs in documentation or a reference;
- a one-time decision, investigation, or migration whose history belongs in a pull request, ticket,
  or dated document;
- instructions already owned by another skill.

A fact about code goes in the cheapest container that enforces it, tried in this order:

1. A test, when a machine can check the fact: an enum and its hand-written lists, an endpoint's
   replace-or-merge semantics, a migrator's backfill. A test fails in CI for the person who
   forgot; prose hopes a future agent loaded it.
2. One sentence under the principle it instantiates, in the rule or skill that already states
   that principle. An incident is an example of a principle, and an example lives with its
   principle, not in a file of its own.
3. A path-scoped rule, when the fact is tied to files and no existing rule covers them.
4. A skill, only for a procedure with a trigger phrase a request will contain.

A repository fact that none of these can hold is a candidate for a ticket, not for prose: if the
fact is "this path returns a bare 500", the durable fix is the typed error.

When detailed domain knowledge is required during execution, keep the decision and workflow in the
skill and link to the owning reference. When the missing artifact is a living architectural
reference rather than a workflow, follow the owning repository's reference-authoring guidance.

## Establish ownership before writing

Read the target repository's `AGENTS.md`, `CLAUDE.md`, and existing skills. Search for the same
capability and neighboring triggers before creating another file.

Place cross-repository working practices in the root repository, the one an agent session starts
from and that checks the other repositories out beneath it. Place language, framework,
product-domain, and repository-operation skills with their owning repository. Extend or replace
the existing source when one already owns the capability; do not create a competing version.

When a skill moves to its owning repository, the repository it left may keep a **discovery stub**
so a session started there still finds it: a `SKILL.md` whose frontmatter names the trigger and
says where the canonical lives, and whose body — directly after the title heading — opens with a
line starting `**Canonical skill:**` linking to it, relatively. That opening line is the contract
the skill sync reads: a stub is never registered into a root-repository session, because that
session sees the canonical directly. A skill with its own content above the pointer is not a stub
and is registered. Do
not write a stub for a skill that has not moved, and do not add content below the pointer that
the canonical should carry.

When a repository has conventions of its own for a capability the root repository already owns, it
keeps them as a **delta**, not as a second skill: the same directory name as the root skill, in the
owning repository; a description opening `Delta to the root repository's <name> for <repo>: read in
addition to it when …`; and a body opening with a line starting `**Extends:**` that names the root
skill first — `` **Extends:** the root repository's `<name>` ``, then its relative link. The name is
the primary reference: in a root session the canonical is registered under exactly that name, and a
reader who meets the delta through a registered link name (a sync that registers sub-repository
skills into the root session under a prefixed name) sees a relative path that only resolves because
the kernel expands the symlink before applying `..`. The path is for the file system; the name is
for the reader.
A delta is registered into a root session (a stub is not),
and a skill audit classifies the name collision as `canonical + delta`; a sub-repository copy
that neither stubs nor extends is `DIVERGENT`, which is a defect to resolve one way or the other.

## Our layout and naming

Coding-agent skills live at `.agents/skills/<skill-name>/SKILL.md`, in every repository. The
directory name is at most 64 characters of lowercase letters, digits, and hyphens, with a hyphen
only between two words, and frontmatter `name` is identical to it. Both
agents discover the directory through committed symlinks — `.claude/skills` and, where the repo
allows it, `.cursor/skills` — so a skill placed anywhere else is invisible.

Frontmatter carries `name` and `description` and nothing else unless the repository's `AGENTS.md`
asks for more. Register the skill wherever that `AGENTS.md` keeps its index, if it keeps one —
keeping none is a deliberate choice, because a second copy of each description drifts from the
skill it summarizes — and follow the repository's own checks.

Use a short, stable name that describes the capability: full words, and a verb and object where one
reads naturally. Avoid names based on projects, teams, tools, or implementation history unless that
context is what identifies the capability. Avoid vague names such as `helper`, `utils`, or `data`.

There is one exception, and it is a different loader rather than a different style: a repository
that also serves **platform** skills to a product's own AI agents from a separate tree may have a
loader that requires its own naming (for example underscore-separated names) plus its own
frontmatter, tool declarations, registration, and evaluations. Follow that loader's standards when
writing one. Note that such a repository's own **coding-agent** skills still sit in `.agents/skills/`
with hyphenated names like everywhere else, so the two trees are not competing conventions — they
are two runtimes in one repo. Do not carry either one's rules into the other, and do not normalize
them here: that is a migration with a deprecation path.

Everywhere else, match the convention above rather than inventing a local variant.

## Link files relatively, at the depth the layout implies

One pattern, everywhere. The multi-repository layout, where the root repository checks every
sub-repository out into a fixed directory beneath it, is a required invariant of this tree — the
root's repository registry gives every repo a target directory under `<subrepos>/`, and every
shared script depends on it. So **a link to a file the layout provides is relative**, and only
things that are not files in the tree — a pull request, an issue, a ticket, a chat thread — are
URLs.

| From | To | Prefix |
|---|---|---|
| `<subrepos>/<repo>/.agents/skills/<skill>/SKILL.md` | its own repo root | `../../../` |
| | a sibling subrepo | `../../../../<other>/` |
| | the root repository | `../../../../../` |
| `<root>/.agents/skills/<skill>/SKILL.md` | the root repository | `../../../` |
| | a subrepo | `../../../<subrepos>/<repo>/` |

`.claude/skills` is a symlink to `.agents/skills`, so reading through it does not change the
depth. Note the count: from a skill directory the repo root is **three** levels up, not two —
`<skill>` → `skills` → `.agents` → root. Getting that wrong is the single most common defect a
link audit reports, and it fails silently, because a link that resolves nowhere renders as a
link.

Why relative and not a URL for the same file: a relative link follows the branch you have
checked out, so a reviewer reading a branch sees that branch. A URL pinned to the default branch
shows them the default branch instead — which is wrong exactly when it matters, during review of
a change to the file being linked.

An audit enforces this in both directions: a dead-link check catches a relative link at the wrong
depth, and an in-tree-URL check catches the same reference written as a URL.

## Write the description for discovery

The description says when an agent must read the skill, and nothing else. Follow the pattern of
the sibling skill descriptions in this directory for style. Lead with the trigger, in the words a
request is likely to contain, and add a routing boundary when a neighboring skill could be picked
instead. Every session pays for every description on every turn, so keep it to a sentence or two,
well under the 1,024-character limit. Ensure it is YAML compliant.

A description is a retrieval key, so measure what it selects. Count the commits in the last year
that touch the code the body is about, and compare with the commits the trigger phrase would
match. A trigger that matches every change in the repository ("use before any backend change
here") selects nothing, and every session pays for the description while the body applies to a
few percent of changes. When the body is a list of unrelated facts, the trigger cannot be
narrowed, and that is the sign the facts belong in the containers above rather than in a skill.

State the trigger once, in the description. Do not restate it in the body, in another skill, or in
a rule: every copy lengthens what an agent reads and can drift from the description. The body opens
on what to do once the skill applies. Another skill may link to this one, but it does not repeat
when to use it. The exception is a skill gated by one of the always-on rules that the repository's
`AGENTS.md` names, whose rule carries the trigger as its gate.

## Write only the body the task needs

There is no heading template. Add a section only when it contributes to correct discovery or
execution. The sections that usually earn their place are:

- **Purpose** for the successful outcome;
- **Use when** for trigger details and nearby exclusions;
- **Inputs** for information that is genuinely required;
- **Instructions** for the workflow, decisions, constraints, and edge cases;
- **Output** when downstream structure or content matters;
- **References** for supporting knowledge;
- **Examples** when rules alone leave realistic ambiguity;
- **Verification** for evidence that the skill produced the intended result.

Instructions are actionable and ordered when sequence matters. Be specific where a mistake is
costly and leave room for judgment where several approaches are valid. Give one default and the case
that needs another, not a menu of equal options. Where output can be checked, write the loop in: run
the check, fix what it reports, and run it again until it passes. Use one term for each concept. Do
not restate obvious model capabilities or prescribe exact tool calls when the tool choice is not part
of correctness.

Write what to do. Add a prohibition only for a mistake agents have made repeatedly, and only when
you cannot fix the tool or the environment so the mistake cannot happen. The list of things not to
do never ends, and each entry costs every reader.

Name a section for its content, without a number, and do not count the sections in the text. A
numbered heading or "the four sections" has to change when a section is added, and every reference
to `§2` breaks with it. Refer to a section by its name, as in `writing-pull-requests` » Why. A
numbered list of steps is fine where the order matters.

## Keep the skill small and current

Prefer concise instructions over background explanation. Assume the reader is a capable model and
add only what it would not already know.

Keep the `SKILL.md` body under 500 lines and 20,000 characters, about 5,000 tokens; most skills need
a quarter of that. Near either limit, split rather than tighten: keep the decisions and the workflow
in `SKILL.md` and move detailed documentation, schemas, policies, and representative data into
`references/` beside it. Link each reference directly from `SKILL.md` and say when to read it, since
a link inside a reference is often read only in part, and open a reference over 100 lines with a
table of contents.

State each fact once in the skill. A checklist item names what to check; it does not repeat the
rule's numbers or reasons. Before publishing an edit, read the whole skill and merge anything your
change repeats. An edit is as long as its point: when bringing in guidance from an outside guide,
keep only what would change how an agent here acts, and put it in the sentence it belongs beside.

Do not use the skill as a changelog. Authorship, lineage, design discussion, prior behavior, and
rejected wording normally belong in Git history, pull requests, tickets, or design documents.
Include history only when it changes how the current task must be performed, and state the current
way rather than an instruction that depends on a date.

Tense is the test, and it applies to every sentence rather than only to examples. A skill is written
in the present imperative: what to do, what holds now, what to check. A sentence in the past tense —
"every call was", "nobody read it that way", "the author changed the rule after the incident" — is
describing the record whatever its subject, and the record belongs where records go. The pull
request that prompts a skill edit is the strongest pull toward this, because the investigation is
fresh and feels like the reason: write the rule the investigation produced, not the before and after
it moved between. A reader who wants the derivation has
`git log -S '<the wording>' -- '.agents/skills/<skill-name>/SKILL.md'`.

Examples must clarify behavior that rules cannot express cleanly, and run no longer than that
takes. Show the decision, not the story around it: a narrated incident — who reported what, which
ticket, what was found in which order — is a record, so cite it in a line and keep the example to
the judgment it turned on. A repeated or exhaustive example set is reference material, not skill
content. Where the output's style is the point, a few input and output pairs teach it better than
a description of it.

When a step must come out the same every time, ship a script under `scripts/` and say whether the
agent runs it or reads it. Running it puts only its output in the context; reading it puts in the
whole source, so say run unless the agent needs to adapt the code. The script fails with a message
that says what to fix. For a batch or destructive operation, have the agent write its plan to a file
and check it with the script before applying it.

## Writing process

A skill fixes failures you have seen, not ones you imagine.

1. Identify the repeatable task and the owning repository.
2. Search for an existing skill, rule, or reference that already owns it.
3. Read that repository's `AGENTS.md` for where skills are registered and which checks run.
4. Run a few realistic requests without the skill, note where the agent goes wrong, and turn that
   into at least three scenarios with the expected outcome.
5. Write the name and discovery description.
6. Identify the minimum inputs the agent cannot retrieve itself.
7. Write the least instruction that makes the scenarios pass: the decisions and their sequence,
   and constraints only for mistakes the scenarios showed.
8. Define the output and verification only where they matter.
9. Move detailed knowledge into references, deterministic steps into scripts, and remove history.
10. Run the scenarios in a fresh session that has only the skill, on each model it will run on, and
    watch what the agent does. A bundled file it never opens is badly linked or not needed, a
    reference it reads every time belongs in `SKILL.md`, and a rule it skips needs more prominence,
    not more words. Where the repository keeps evaluations, add the scenarios there.
11. Register the skill wherever the owning repository's `AGENTS.md` keeps an index, if it keeps one, and run its checks.

Run the scenarios again whenever the skill changes materially.

When renaming, moving, or removing a skill, update every registration and reference in the same
change.

## Review checklist

Before publishing, verify:

- The artifact is a skill rather than a rule, reference, or one-time record.
- The owning repository is explicit.
- The path is `.agents/skills/<skill-name>/SKILL.md`, the name is hyphen-separated, and frontmatter
  `name` matches the directory.
- The name identifies the capability.
- The description makes the trigger and nearby boundaries clear.
- The trigger appears only in the description, or also in the always-on rule that gates the skill.
- The body is actionable rather than descriptive, tells the agent nothing it already knows, and is
  within the size limit.
- Each fact appears once, and each prohibition answers a repeated mistake that a tool or
  environment fix could not prevent.
- No heading carries a number, the text does not count its sections, and references name a
  section rather than number it.
- Required inputs are minimal and distinguish retrievable context.
- Durable knowledge is referenced instead of duplicated.
- Every bundled file is linked directly from `SKILL.md` with when to read or run it.
- History and lineage are outside the skill unless operationally necessary, and no sentence outside
  that exception is in the past tense.
- Examples add information rather than repeat instructions, and none narrates an incident at
  length.
- Links resolve from the skill's independent repository, not only from a nested checkout.
- Registrations, references, and evaluations match the final name and path.
- The scenarios pass in a fresh session, without hidden context.
- Every remaining section materially improves discovery or execution.

Run the owning repository's checks and inspect the final diff before requesting review.
