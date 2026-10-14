---
name: root-cause-proof
description: MUST USE before naming a root cause in any investigation, RCA, or "why is X broken, slow, or failing" question.
---

# Root-Cause Proof

You are about to write down a root cause. This skill is the gate. It exists because the cheap, wrong move — "this looks like last month's incident, so it's the same page-rendering bug" — passes every casual smell test and is still wrong. Where a repository carries an always-on proof-bar rule of its own, read it too: this skill is the procedure, that rule is the floor.

## The five failures this skill forbids

1. **Analogy-as-root-cause.** "Same as the last incident / same class as incident #XXXXX" is a **lead, not a conclusion.** A prior incident tells you where to look; it never tells you what is true now. You must re-derive the cause from live evidence and current code *this time*.
2. **Symptom-as-root-cause.** "The load balancer returned 5xx", "the service timed out", "the storage engine was slow", "the pod OOMed" are **symptoms/layers**, not the initial root cause. Stopping there produces a recommendation nobody can act on (or that's already done).
3. **Stale-reference-as-root-cause.** Naming a code path / bug / config from memory or an old write-up without opening the current source. The fix may already be deployed; the method may not exist anymore; the filter you're blaming may have been removed.
4. **Hypothesis-as-root-cause when the system was observable.** Reasoning your way to a cause you could have *watched* happen. A chain of plausible mechanisms, each eliminated and replaced by the next, is not investigation — it is guessing with extra steps. If the failure reproduces and you can instrument the thing that runs it, observe the transition rather than forming another hypothesis. Observation *locates* the mechanism; Gates 1-3 still have to prove it. See Gate 4.
5. **Empty-diff-as-proof.** "Pre-existing on the default branch", "unrelated to this branch", "was already broken" — asserted because `git diff <default>` on the implicated code path is empty. An empty diff proves the *code* did not change. It says nothing about the *behavior* when the branch changes anything the code runs on: an engine or framework version, a base image, a shared dependency package, a config default. Before writing "pre-existing", produce the same test passing elsewhere in a comparable window (CI history plus the test's own result, not a recollection) or re-run the failing case on the default branch. Without either, the origin is **unconfirmed** — and the two claims license opposite next actions (ship past it vs. block on it).

## Gate 1 — Separate symptom from cause; build the "why" chain to the INITIAL root cause

Write the causal chain explicitly, top (what paged) to bottom (deepest actionable cause). Each hop must be **evidenced**, not asserted. Keep asking "why" until the next "why" would leave the system you own:

```
Symptom:   load balancer 5xx page                      ← what fired
  why? →   requests exceed the load balancer idle timeout [cloud metrics: Latency max pinned, backend 5xx = 0]
  why? →   API threads block on storage-engine reads      [log system: no app errors; thread state]
  why? →   individual full-profile reads take 10–42 s     [log system: slow-response warnings, verbatim]
  why? →   the read scans the WHOLE column family of a    [SOURCE: FullProfileReader.java:335-346
           mega-row, decompresses + filters every cell              TableGetRowQuery.java:86-91]
           on one handler thread (CPU-bound)              [signature: low queue/fsread, high processing]
  why? →   one person accumulates unbounded `event|`      [entity: one person row, hydrated per Gate 3;
           columns in a single wide row/family                      schema single family, no TTL, init-tables.sh:4-7]
INITIAL ROOT CAUSE: unbounded per-person column growth in one wide row+family, read via a
whole-family Get. (Actionable: cap/rollup columns, per-collection column narrowing, TTL, or a
different read shape. NOT "the storage engine is slow" and NOT "the same bug as last time".)
```

Rules for the chain:
- A layer you cannot yet evidence is a **hypothesis** — label it and go get the evidence, or stop and say you're blocked. Do not silently promote it.
- Stop at the deepest layer that is (a) **proven** and (b) **actionable by someone**. "The disk was slow" is not a root cause if you haven't shown *why*; "a GC pause stalled the handler" is, if you proved it.
- If your "root cause" is a restatement of the symptom in different words, you have not found it.

## Gate 2 — Re-derive against CURRENT source (never trust the old story)

Before you name any code path, bug, config, or fix as the cause:
- **Open the file at current HEAD** and cite `file:line`. Do not cite from memory or a prior PR/write-up.
- **Check whether the thing you're blaming still exists / already changed.** `git log -- <path>` and read the relevant commit. If a fix landed after the last incident, your job is to explain why it recurred *despite* the fix — the cause is elsewhere.
- **Prove the code produces the observed signature.** Map the runtime evidence (log fields, metric shape) to what that code would do. Low queue time + high processing time + negligible file-read time is CPU-in-handler, which the code must actually explain.
- **Date a configuration read to the window you are explaining.** What you read now is evidence about a past failure only once you know it was live on the affected target then. A last-published or last-modified date that predates the observation is necessary, not sufficient — where the target keeps its own deployment or activation history, read that too — and a configuration published since explains nothing about before it.
- Search tools that honour `.gitignore` silently skip vendored and nested checkouts — use a search that does not (for example `rg --no-ignore --hidden`, or `command grep -rn` where the shell's `grep` is wrapped), and verify results are non-empty before concluding something is absent.

## Gate 3 — Hydrate every entity (no raw ids left in the doc)

A raw tenant id / user id / row key is not usable and not proof. Resolve it and link it. If you catch yourself writing "not decodable" or "the exact tenant is unknown," stop — decode it.

- **Know your id encodings.** E.g. a composite row key may be `reverse(userId) + "-" + tenantId` — read the code that defines the encoding and cite it (`file:line`), then decode: reverse the prefix digits for the user id, the suffix is the tenant id.
- **Resolve via the product's API or MCP**: tenant id → name / short name / type; tenant summary → pod, version, account owner, support owner; user id → identity key/value, version, and a ready-made link into the product's admin interface. User reads are usually **tenant-scoped** — select the owning tenant first or you get 403.
- **Discover more tools** through the API's tool search where it has one; when no tool covers it, search the product's API reference (its OpenAPI spec) to find the right operation rather than guessing.
- Every entity in the doc gets: id → human name (tenant name, user identity value) → a clickable admin-interface or dashboard link. The customer-impact chain must name real customers, not ids.

## Gate 4 — If it reproduces, observe it; stop theorising

Gates 1-3 assume the evidence is already in front of you. This gate is for the case where it is not, and you are tempted to reason instead of go get it. What it produces is **evidence, not a verdict**: a probe narrows where to look, and the cause still has to clear Gates 1-3 and the output contract — in particular Gate 2, re-deriving against current source — before you write it down.

**The stop rule.** Two disproven hypotheses about the same reproducible failure and you stop reasoning. Instrument it. Not a third theory, however good it looks — each one costs a full think-and-argue cycle and buys nothing when the mechanism is sitting there waiting to be printed.

**The signal that you are modelling the wrong state.** Unit tests pass while the real path fails. That is a strong signal to inspect *composition* first — wiring, ordering, or state a mock stands in for. It is not proof that the logic is correct, and it does not tell you the cause; it tells you that hypotheses formed by reading the units alone are likely to miss, because the units are the part already covered. When you see it, go to the running system.

**The cycle**, for a platform component deployed to a development environment:

1. Put probes at the decision points that would distinguish your hypotheses — the booleans you are guessing about, and the value before and after each step.
2. When you suspect a write is reaching the wrong instance, log something that identifies it. `System.identityHashCode` is a hash, not an identity: two distinct objects can share one, so a **mismatch** proves they differ while a **match** is only a hint. If the conclusion turns on identity, compare references directly or thread a correlation token through the objects you care about.
3. Use `LOG.warn`. `debug` may be off, and a probe you cannot read is a wasted cycle.
4. Redeploy only the component that serves the failing request (the repo's deploy helper, scoped to that one component), not the whole set.
5. Run the **single** reproducing test, not the suite.
6. Read the pod's logs (`kubectl logs`) by **parsing** the JSON, not by text-matching it. Text matching cannot reliably extract an escaped or nested field — a pattern like `"message":"[^"]*"` stops at the first escaped quote inside the value, so an intact value reads back truncated or empty.
7. Remove the probes before committing, and note that the environment still runs a probe build until it is redeployed.

Budget about ten minutes per cycle. Two of them usually beat an afternoon of theory.

**A probe is still production logging — bound what it prints.** These lines run in a real environment against real data, so the standing rule holds: no secrets, credentials, tokens, authorization headers, or PII, and no raw customer payloads. Log the things that discriminate between your hypotheses — booleans, counts, sizes, entity ids, the *shape* of a value — rather than the value itself. When you must see content, log a redacted or truncated form, or a one-way correlation id you can match across steps. If a probe would print an identity value or a payload to answer your question, find a different question.

**Probe the transitions, not the state you already believe.** Log what a step *decided* and what the value looked like on each side of it. A probe that only confirms your current theory tells you nothing when the theory is wrong.

## Gate 5 — Reproduce the reporter's case, not a symptom you can make

A reproduction that shows the reporter's symptom is not yet a reproduction of their cause. Gates 1-4 prove a mechanism; this gate makes sure the mechanism you proved is the one they hit.

- **Reproduce with their subject and their entry path.** Take the identifier — the code, the user, the record — out of the reporter's own message or URL and replay with that. A replay that passes on a subject you chose is not a failed reproduction: a per-subject decider imitates timing, caching and chance perfectly, so when two identical requests disagree, enumerate what else the request reaches (the subject's own record) before reaching for randomness. Measure the remedy on the subject that fails, not the one to hand.
- **A/B the shortcut before you let it into the answer.** An injected token, a forced state, a hand-assembled page is the likeliest contaminant. Compare your reproduction with the reporter's — screenshot against screenshot when the symptom is visual — and where they differ, that difference is your harness until proven otherwise.
- **Calibrate the probe before reading a difference.** Two probes must differ only in what you are testing: same user agent, same container or sandbox, same state. A default non-browser user agent is routinely classified as a bot and answered from a different container, which manufactures a one-sided difference from identical configurations. When diffing two built artifacts, mask ids, dates, brand strings and build numbers first. Claim only as wide as the calls you replayed; anything downstream you did not replay is unmeasured, not clean.
- **A chain of wrong outcomes is one decision per hop.** Each hop is decided by different machinery, and the hop already diagnosed is usually not the broken one. Read the identifiers in the reporter's own URLs to see which hop failed, re-measure each hop on its own, say which hop each number belongs to, and never carry a parameter's verdict from one hop to the next.
- **A retest that passes is one draw, not a retraction.** When a reporter says it worked on retry, answer with a failure rate over a repeated sequence plus a clean control that shows the configuration itself is fine and the sequence is what breaks. Acceptance is a separate, stricter run: treating the runs as independent draws with a stable failure rate, `n` clean runs rule out a residual failure rate `p` at 95% only when `n >= ln(0.05) / ln(1 - p)`. Start each run from fresh state so carried-over state does not correlate them, and say that the bound assumes independence — fresh state alone does not establish it. Size `n` from the smallest rate you would still act on and report the residual it rules out; "fixed" asserts zero, which no finite run establishes.

## Gate 6 — Check the instrument before a number leaves your hands

- **A negative claim is settled per record, not from a derived source.** "Only ever", "nobody did", "never fires" cannot be settled from a list, a report or an index that can omit rows. Confirm it per record before the number leaves your hands, and treat a request for examples of your number as a request to re-derive it.
- **A positive control proves the instrument can see things of that kind, never things of that age.** Before publishing a negative about an asynchronous write, compare the instrument's newest row with the event's own timestamp; a store that has not caught up reports absence for everything recent.
- **A proxy earns a proportion only after it agrees with a case you can see by eye.** A version counter, a default-looking value or a field's presence is a proxy until a known record agrees with it. Run it against that one case first.

## Output contract (what "proven" means before you write the doc)

Do not label a cause **confirmed** unless all hold (else label it **hypothesis** and say what's missing):

- [ ] **Why-chain** written symptom→initial cause, every hop evidenced, deepest layer is actionable (Gate 1).
- [ ] **Current-source citations** at HEAD `file:line`; you checked the blamed code still exists and isn't already fixed (Gate 2).
- [ ] **Signature mapping**: the runtime evidence (log fields / metric shape) is explained by that code.
- [ ] **Entities hydrated**: ids → names → admin-interface or dashboard links; impact chain names real customers (Gate 3).
- [ ] **Deterministic repro** where scope allows (replay the call / query and reproduce the signature), on the reporter's own subject and entry path (Gate 5), per the repository's own proof-bar rule where it carries one; if blocked, state the blocker and keep the cause provisional.
- [ ] **Numbers re-derived**: every count, negative and proportion in the doc was confirmed per record, and every proxy behind one agreed with a known case (Gate 6).
- [ ] **Backtrackable receipts**: full raw log line + a deep link into the log system with the exact query and time range for every log-based claim.
- [ ] **Not analogy**: the doc states the cause from this incident's own evidence. Prior incidents appear only as "recurrence history / prior art," explicitly separated from the proven cause.

## The fix-author pipeline

For a bug report or an incident you are working **as the fix author** — not the live on-call, who
has their own procedure and is who you hand off to on active customer impact — the gates above run
inside four stages, each with a template and each stopping short of a fix:

| Stage | Produces | Template |
| ----- | -------- | -------- |
| **Validate the report** — is it real, what likely caused it, has it happened before | Confirmed / Likely / Not Reproducible / Insufficient Information | [`references/findings-template.md`](references/findings-template.md) |
| **Plan the investigation** — three to five ranked hypotheses, each with confirm and disconfirm checks, in parallel tracks | Investigation plan | [`references/investigation-template.md`](references/investigation-template.md) |
| **Gather evidence** — code, logs, organizational signals, for *and against* each hypothesis | Correlation timeline; findings with confidence and source | [`references/evidence-template.md`](references/evidence-template.md) |
| **Recommend fixes** — only once the cause is Confirmed or Likely | Three tiers: immediate mitigation (a handoff, never executed from here), root-cause fix, prevention | [`references/fix-template.md`](references/fix-template.md) |

The habits the templates enforce: build the timeline first (last known good → what changed → first
symptom — most bugs start because something changed); split the research (what changed vs. whether
it happened before; an exact error message gets its own query); anchor on the system, not the alert
name; reject the first confirming signal; call out prior remediations that regressed; give every
durable change a revert path; never treat the institutional-context tool as a log store — the
repo's own log access is the evidence, and production telemetry goes through on-call. A durable
code change then goes to an implementation plan, not straight to a diff.
Headless, cap research and log loops at three per stage, emit the stage's template as the only
deliverable, and never mitigate, page, change production, or open a fix PR from here.

## When you are genuinely blocked

Say so, precisely, and keep the cause labeled **hypothesis** — do not round up to "confirmed" or fall back on the analogy. "The per-read cost points to a wide-row scan (code-proven), but I could not replay against the live row to reproduce the 42 s, so single-tenant attribution for the window is a hypothesis pending the log aggregation / access-log pull" is an honest, useful state. "Same as last time" is not.
