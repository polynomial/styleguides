---
name: architecture-assessment-evidence
description: Must be read before writing, editing, or reviewing an architecture assessment, options matrix, technology-selection doc, ADR set, or anything under docs/assessments/, before recommending to adopt, keep, remove, or reverse a component, and before crediting one with a vendor capability such as dead-letter, retry, or replay.
---

# Architecture assessment: evidence standard

The binding rule is [`assessments`](../../rules/assessments.mdc). This skill is the procedure.

**The one-line standard: a capability is scored where it is implemented, not where the vendor
documents it.**

## When this applies

- Any file under `docs/assessments/`.
- Any weighted decision matrix, anywhere.
- Any doc recommending adopting, keeping, removing, or replacing a component.
- **Reviewing** someone else's assessment PR — the reviewer runs the same audit as the author.
- Any proposal that reverses a merged recommendation.

## Phase 0 · Answer whether the component should exist

Before you score how well a component is built, answer in writing: **what does it buy that the
system loses without it, today, at measured load?** State it concretely, not as a pattern name or a
future hope. If the answer is empty or speculative ("we might need fan-out later"), that is the
finding. Record it before you score anything, and do not recommend hardening, migrating or renaming
a component whose value you have not established.

**Naming a pattern is not justifying it.** "This is an outbox / CQRS / saga" gives vocabulary, not
value. Check the pattern's preconditions against code and data (for example, check an "immutable
log" claim against the migration history for in-place updates), and show its benefits are actually
exercised.

## Phase 1 · Ground the baseline before reading the argument

Do this **first**, before reading the doc you are auditing or writing. Otherwise you inherit its
framing.

```bash
# Pin the commit everything will be cited against
cd <repo> && git fetch origin --quiet
git rev-parse origin/<default-branch> && git log -1 --format=%cI origin/<default-branch>
```

Verify the state of **every** PR the argument leans on. Do not take a doc's word for it:

```bash
for n in <pr numbers>; do
  gh pr view $n --repo <org>/<repo> --json number,state,mergedAt,mergeable,additions,deletions \
    --jq '"\(.number) | \(.state) | merged=\(.mergedAt) | mergeable=\(.mergeable) | +\(.additions)/-\(.deletions)"'
done
```

Four states change scores and are routinely conflated:

| State | What it is |
|---|---|
| `MERGED`, code | shipped mechanism — scoreable as built |
| `MERGED`, docs only (`+N/-0` under `docs/`) | a **plan**. Score its cost and risk, never its capability |
| `OPEN` / `CONFLICTING` | a proposal. Its defects (no soak, hard cutover) are real and belong on the execution-risk lens |
| `CLOSED`, unmerged | **the capability does not exist.** This is the one that gets cited as if it shipped |

## Phase 2 · Audit every credited capability

For each capability an option is credited with, find it or declare it absent. Build a table like this
and put it at the top of the matrix doc:

| Claimed capability | Configured? | Receipt |
|---|---|---|

Search patterns that repeatedly find the gap:

```bash
# Is there really a dead-letter / retry / error handler?
git grep -n "dead\|Dlt\|DLT\|deadLetter\|ErrorHandler\|Recoverer\|backoff" origin/<default-branch> -- '<module>/src/main/**' '**/application*.yml'

# Is the "backpressure" real, or a nack/re-seek?
git grep -n "\.pause()\|\.resume()\|BindingsLifecycle\|nack(" origin/<default-branch> -- '*.java'

# Durability actually configured?
git grep -n "replicas(\|partitions(\|replication.factor\|retention" origin/<default-branch>
```

**Then the check almost nobody runs: does the producer have a consumer?**

```bash
# Take every destination/topic/queue/table name the doc credits, and grep it repo-wide
git grep -rn "<destination-name>" origin/<default-branch>
```

A destination that appears only as a producer binding and in a plan document is **written and never
read** — cost, not capability. On the originating incident this single grep turned a 5/5 isolation
score into a 2/5 and found that every event was being written to the message broker twice.

**And the check that decides "is this fan-out or a doorbell":** follow the consumer from its entry
point and see whether it uses the payload or re-reads the store.

```bash
# trace: listener -> handler -> service. Look for getMessages / findById / re-read of state
```

If the consumer re-reads the database to get its context, the transport is a notification bus. It is
not log-based fan-out, and replay/rebuild/fan-out value cannot be credited to it.

## Phase 3 · Measure load and harm

"At current scale" is a number, a window, and the query — or it is nothing. Both sides:

- **Load** the component carries (throughput at peak and typical).
- **Harm** the component causes (work destroyed, requests failed, incidents).

```bash
# Log-query pattern (for example CloudWatch Logs Insights; the log system's equivalent works the same way)
aws logs start-query --region <region> --log-group-name <log-group> \
  --start-time $START --end-time $NOW \
  --query-string 'fields @timestamp,@message | filter @message like /<marker>/ | stats count() by bin(1h)'
```

Write the window and the query into the doc. Never carry forward a throughput figure from a previous
version of the assessment — re-measure it.

## Phase 4 · Check the rubric before you score

| Defect | Test |
|---|---|
| One criterion counted several times | Sum the weights of lenses that would move together on the same fact. If that sum decides the matrix, collapse them into one lens |
| Existence lens missing | Is there a weighted lens asking "what does this buy that the alternative does not, at measured load"? If not, add it. A rubric of only operational lenses scores hardening an unjustified component as progress |
| Post-hoc override | Does the recommendation override the scorecard with an unscored factor? Any criterion that can change the answer must be a weighted lens. If an override feels necessary, fix the rubric |
| A deciding lens quietly removed or demoted | Diff the rubric against the previous version. Any removal or demotion needs an ADR |
| A gate only one option can pass | Does the gate state invariants, or does it state scope? "Must replace every consumer at once" is scope |
| Incumbent scored as zero-risk | "Do nothing" preserves whatever the current design is doing, including harm |

Then: write the weighted total out term by term, and run sensitivity under **at least** the weighting
the opposing case would choose. A recommendation that only survives your own weighting is not a
recommendation.

## Phase 5 · When you reverse a previous assessment

1. **Name what you adopt from it.** A re-derivation that adopts nothing has probably not read it.
2. **Correct the old document's factual errors in place, including your own side's**, per
   [Phase 7](#phase-7--keep-the-doc-set-to-one-current-answer). One current answer; no banners, no
   superseded matrices, no correction blocks.
3. **Run the decisive test — hold their rubric, correct only the scores:**

   > Take the other assessment's lenses and weights **verbatim**. Change nothing about the framing.
   > Replace only the score cells with receipt-backed values. Report both totals.

   If the answer flips under their own rubric, the disagreement was never about method, and saying so
   is more useful than arguing about weights. If it does not flip, they have a real methodological
   point and you must engage it.

## Phase 6 · Separate what is owed regardless

Some findings are pure cost under **every** option — a write-only topic, an unbounded cancellation,
a missing dead-letter path. Pull those out under their own heading with the harm quantified, so they
are not blocked behind a decision that may take weeks. This is the most actionable output an
assessment produces.

## Phase 7 · Keep the doc set to one current answer

A `docs/assessments/<name>/` set (or any multi-document investigation) conveys one current answer.
When a finding changes a conclusion, rewrite the presentation documents in the same commit:

- **Answer first.** The README's first sentence answers the commissioning question directly, in
  plain language. If the question was "does X have value?", that answer opens the README. Every
  presentation document agrees with it.
- **Fold, do not annotate.** Rewrite a falsified claim where it lives. No dated `> Correction`
  blocks, no supersession banners, no superseded analyses kept "as audit trail".
- **One scorecard.** Exactly one matrix, re-derived under current facts, whose ranking agrees with
  the recommendation. Delete superseded matrices. State a near-tie as a near-tie and name the
  tiebreaker.
- **History in one place.** The decisions doc carries the ADRs (current status only), the decision
  log with user prompts verbatim, and a short summary of what each pass concluded and what
  superseded it. Link git or the PR for full prior text.
- **Re-derive registers.** Rewrite a gap register or worklist from a superseded recommendation as
  the current worklist. Per-item "disposition under the new plan" scaffolding is a drafting step,
  not a deliverable.

Forbidden: two documents or scorecards in the set that disagree about the recommendation; a README
summary that lags the newest finding. Origin: one assessment set whose README and scorecards were
found disagreeing with each other after a later pass changed the conclusion.

## Failure modes this exists to prevent

- Scoring a message broker's, a database's, or a framework's *documented* behaviour instead of this
  system's configuration.
- Citing a **closed, unmerged** PR's capability as if it shipped.
- Treating a doc-only merge as a shipped mechanism.
- Crediting isolation to lanes with no consumer, or fan-out to consumers that re-read the store.
- Reversing a merged recommendation without auditing whether the rubric or the evidence produced the
  difference.
- Carrying a throughput number forward from a previous version instead of re-measuring it.
- Scoring how well a component is built before establishing that it should exist.

## Worked example

The origin of this skill is a 2026-08-17 re-derivation of a messaging-posture assessment that
reversed a merged recommendation. Its options-and-matrix doc shows the capability audit table, the
doorbell trace, the harm measurement, the nine-lens rubric, and the hold-their-rubric-correct-the-scores
test. Its current-state doc shows a Zachman teardown with `path:line` receipts and why the *Why* cell
is the one that decides it.
