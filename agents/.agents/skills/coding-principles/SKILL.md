---
name: coding-principles
description: MUST USE before writing, reviewing, or refactoring code in any language, including shell scripts and infrastructure definitions.
---

# Coding Principles

These principles apply to all code — application source, infrastructure definitions, and the
scripts that operate them. A type checker is one more gate where the language has one, not the
condition for these principles applying. They describe how code is written across the
organisation's repositories and languages. A repository owns its domain,
framework, and language conventions; those rules add concrete expressions of this shared layer.

Before editing, state the intended behavior and the cheapest check that can disprove the change.
Read [`behavioral-guidelines`](../behavioral-guidelines/SKILL.md) first when deciding what to build,
and use [`verify-before-complete`](../verify-before-complete/SKILL.md) before declaring the result
complete.

## 1. Names communicate the domain

Use descriptive full words. Avoid abbreviations, single-letter names, type information in names,
and context already supplied by the containing type or module. A name describes what a value means
in the domain, not how it happens to be represented.

When a change makes an internal name inaccurate, rename it in the same change. Internal names are
maintainable code, not permanent contracts.

## 2. Obvious code documents itself

Prefer obvious, conventional code. A person or language model familiar with the repository should
be able to predict its behavior from its names, types, control flow, and established structure. Use
guard clauses instead of deep nesting and named intermediate values instead of dense expressions.
Hidden behavior, action at a distance, surprising indirection, and implicit conversion cost more
than the lines they save.

Express intent through descriptive names, types, small focused methods, and named concepts. Do not
write explanatory implementation comments. If the code needs a comment to be understood, improve
the code until its intent is evident.

Put non-obvious constraints, rationale, and rejected alternatives in the pull request or ticket,
not in code comments. The only exceptions are documentation and directives required by the
language or tooling; keep them minimal and do not use them to narrate the implementation.

## 3. Complexity is represented in the design

Put behavior on the concept that owns it. Keep responsibilities narrow, public surfaces minimal,
entry points focused on orchestration, and implementation details behind their boundary. Extract
meaningful concepts when they make real complexity visible; do not add layers, interfaces, or
extension points for hypothetical reuse.

Use the conventional shape of the language and framework. A departure must solve a demonstrated
problem and is the part of the design that needs justification.

## 4. Contracts are explicit in types

Represent absence and valid states with the language's type system. Prefer closed types and
exhaustive handling where the domain is closed. Do not encode absence or variants as undocumented
sentinel values.

Where the language has no type system, the contract is carried by validation at the boundary and by
names that state what a value is. The obligation to make an invalid state unrepresentable does not
lapse with the type checker.

Validate and normalize untrusted or external input at the system boundary. Inside that boundary,
trust declared contracts instead of adding defensive checks for states the types prohibit. If an
invalid state remains representable, improve the contract rather than scattering checks.

An empty collection is a value, not an absence. A guard such as `if (!values.isEmpty())` makes
an explicit empty list indistinguishable from the method never being called, and silently
discards a caller's "none" signal. Represent "not supplied" with `Optional` or an omissible
type, and let an empty collection mean empty.

## 5. One problem has one established pattern

Search current code and prior decisions before solving a problem again. Follow the established
language, framework, and repository pattern. Keep one canonical implementation and one canonical
source of guidance; copies and competing approaches drift.

An existing pattern is evidence, not an automatic veto. When it is wrong, change it deliberately
at its source and migrate affected uses rather than introducing one local exception. Follow
[`finding-existing-patterns`](../finding-existing-patterns/SKILL.md) for the discovery and
migration procedure.

## 6. Fail loudly and log once

Never swallow a failure or replace an impossible state with a plausible default. Classify failures
with the language's native mechanism — typed errors or results where it has them, exit status in a
shell — and propagate them until the boundary that can handle them.

Log an unhandled failure once, at the terminal boundary. Include stable, safe identifiers and
enough structured context to locate the failed operation. Exclude credentials, personal data,
unnecessary payloads, and duplicate stack traces.

## 7. Tests can disprove the change

A test for new or corrected behavior must fail without the change, exercise a real interface, and
assert the exact outcome, property, or invariant that matters. A refactor's tests instead prove the
behavior did not move, so they pass before and after — write them, or check they already exist,
before you start. Keep tests deterministic: control time and randomness, await observable conditions
instead of sleeping, and do not widen production visibility or add test-only entry points.

When behavior intentionally changes, update the test's name and expectation. Do not delete the
test merely because the old assertion now fails.

## 8. Every addition earns its place

An abstraction, setting, dependency, exported value, metric, or extension point needs a
demonstrated consumer or use case. Defaults restated as configuration, wrappers used once, and
flexibility nobody requested are liabilities rather than preparation.

Name the source of unavoidable constants and limits.

## 9. Changes are focused and complete

Every changed line traces to the requested behavior. Avoid unrelated cleanup, formatting, and
refactoring. Match the surrounding style even when another style would also work.

Finish the change you started. Remove imports, branches, references, configuration, tests, and
documentation made stale by your replacement or removal. Do not use the task as permission to
remove unrelated pre-existing code.

## 10. Published contracts change through migration

Treat externally referenced names, identifiers, schemas, application programming interfaces,
serialized forms, metric names, and lock names as contracts. Do not rename or repurpose them as an
incidental cleanup.

When a contract must change, make the compatibility boundary and migration explicit. Order the
transition so old and new participants can coexist where required, prove repeated migration is
safe, and remove the old path only after its consumers have moved.

## 11. Observability is actionable

Diagnostics use stable names, bounded dimensions, correlation identifiers, and enough state to
distinguish operationally different outcomes. Asynchronous work distinguishes queued, started,
completed, cancelled, timed out, and failed states when those states require different responses.

Do not emit a metric or log merely because it is easy to add. Name the decision or action it
supports, reuse information already emitted, and avoid dimensions that grow with clients,
entities, or requests.

## 12. Machines enforce mechanical standards

Formatting and other objectively checkable rules belong in formatters, static analysis, compiler
settings, structural checks, or agent guidance. A mechanical defect repeatedly found by a human
reviewer is a missing automated check.

Functional changes carry no incidental formatting churn. Run the owning repository's checks and
inspect their results rather than claiming a change should pass.

## 13. The change carries its proof

The pull request or ticket explains why the approach fits established patterns, which prior
decisions it preserves or reverses, alternatives considered, known risks, unresolved concerns,
and the evidence used to verify it. Code review should not have to reconstruct the judgment from
the diff.

Use the cheapest check that can disprove the change, inspect its result, and do not claim success
while a required check is failing. Follow
[`verify-before-complete`](../verify-before-complete/SKILL.md) for the completion gate.

## 14. Tools have predictable effects

Read operations are side-effect free. Mutation operations are idempotent through a stable
idempotency key or a natural uniqueness constraint whenever the underlying system permits it.

When idempotency cannot be guaranteed, report explicitly whether the outcome is unknown or
non-retryable and require outcome verification before another attempt. A repository that owns
agent-facing tools carries the concrete expression of this rule for them.

## Ownership

This file owns cross-repository code principles. Repository guidance owns only its language,
framework, domain, and operational deltas. Deployment mechanics remain with their owning
repositories.

To amend: open a pull request against this file and update dependent repository guidance when the
change alters their stated boundary.
