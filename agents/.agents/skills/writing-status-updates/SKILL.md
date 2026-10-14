---
name: writing-status-updates
description: Must be read before posting a progress or outcome update — a chat thread, a ticket comment, or a tracking PR — on work spanning more than one sitting.
---

# Writing status updates

An update exists so a reader can trust the state of the work without opening the PRs, the
ticket, or the CI run themselves. It is a pointer into the durable record — the PR, the doc,
the ticket — never a substitute for it: a number in it must be the same number the record
computed, and a claim in it must be checkable by clicking through.

This skill is for a message to readers who were **not in the session** — a chat thread, a
ticket comment, a status comment on a tracking PR. Two adjacent cases are owned elsewhere:
the PR body itself is [`writing-pull-requests`](../writing-pull-requests/SKILL.md); the
closing message to the user in *this* session (the self-eval before saying "done") is
[`verify-before-complete`](../verify-before-complete/SKILL.md).

## The shape

Four parts, used only as many as the update needs:

1. **What's proven** — true right now, each claim with its receipt.
2. **What's not done** — named gaps with their current status, not "still working on it."
3. **Where the work lives** — links: PR per repo, doc, ticket.
4. **Next** — the single next concrete action, not "will keep iterating."

A pure completion message collapses this to "done, here's the proof, here are the links."

## A receipt is a count with a denominator, a named test/run/link, or a live read-back — never an adjective

| Don't write | Write |
|---|---|
| "tests pass" | "474/474 on the target configuration" |
| "the suite ran clean" | "`suite-a` passed, `suite-b` passed, `suite-c` 870/874" (name the exception rather than rounding up) |
| "found the cause" | "`StreamSession.java:41` at `aff35b6`, replay reproduces the same stack trace" |
| "rolled it out" | "71/76 accounts verified via receipt JSON, 5 named remaining" |
| "deploy is out" | "run `33902531442` green; read the live config back and it shows the new value" |

A completion claim — "done," "resolved," "verified" — is written only after it has cleared
[`verify-before-complete`](../verify-before-complete/SKILL.md): read the end state back from a
second vantage point, not the actor's own success message. The update reports that check; it
doesn't substitute for it.

## Disclose a prior claim that turned out wrong; never silently correct it

If an earlier post in the same thread said something that turned out to be wrong, say so in the
next one, in three parts — what you believed, what checked it, what changed:

> "I first wrote this up as \<X\> — that was wrong. \<The check that disproved it\> found \<Y\>,
> so it's actually \<Z\>."

A thread with a silent correction reads as more confident over time than the evidence supports.
Ties to [`root-cause-proof`](../root-cause-proof/SKILL.md): same discipline, applied to what you
tell a reader rather than only to what you write in a doc.

## State the scope boundary the reader would otherwise have to check

For each boundary the brief actually set — no production change, nothing merged, no customer data
touched, read-only, no ticket transitioned — write one line saying which side of it the work
stayed on, even unprompted. The test: *would the reader act differently if they assumed the
opposite?* If yes, it belongs in the update.

## Default to one post

Post once. Do not add follow-up posts to narrate progress, restate state, or announce a
correction as new chatter — that is what re-notifies everyone in someone else's shared space for
no new information.

The one exception: a fact the first post explicitly left open (a dispatched-but-unverified
action, a check still running) has since resolved. That earns exactly one short follow-up
naming the resolved fact, nothing else — not a second full report, and not a "still looking at
X" ping that adds no new fact.

If a reader has asked to be kept updated in a specific thread, follow their instruction over
this default — but the content rule still holds: post only when a new fact exists.

## Close with a named outcome, not an activity

"Reproduce the failure against a fresh environment with evidence captured live, then re-run the
suite clean before this is ready to merge" tells the reader what "done" will look like. "Will
keep working on it" tells them nothing.

## Forbidden

- "Tests pass" / "the suite is green" with no counts, names, or links.
- Quietly revising an earlier claim in a later post without saying it was wrong and how you
  found out.
- Declaring "done" or "resolved" without the proof next to the claim, or without having run
  `verify-before-complete` first.
- A wall of prose paragraphs instead of scannable, receipted bullets.
- A second post that restates state instead of naming one new resolved fact.
- A next step phrased as an activity ("keep iterating") rather than an outcome ("re-run X clean,
  then merge").

## Template

```
What's proven
- <claim> — <count/denominator | test name + result | link>
What's not done
- <gap> — <current status>; <if a prior post was wrong: "I first wrote X; <check> showed Y">
No <scope boundary> made or attempted.
Where the work lives: <PR per repo>, <doc>, <ticket>
Next: <one outcome, phrased so "done" is recognisable>
```

## Why this exists

Originating case: a multi-day status thread for a major-version upgrade of the stream processor,
whose first post had this shape, and whose one legitimate follow-up closed exactly one fact that
the first post left open. That fact was a dispatched teardown, confirmed complete.
