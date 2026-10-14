---
name: production-deploy-monitoring
description: Must be read when asked to monitor or watch a production deploy, confirm a release is safe, check whether a rollout broke anything, or report a deploy outcome. For "could we have caught this" after an incident use monitoring-gap-analysis.
---

# Monitoring a production deploy

**A deploy watch is an experiment, not a dashboard vigil.** It has a hypothesis (what could this
change break?), a control (what did this metric do before?), and a falsifiable prediction. Set up in
that order and most findings are decided in minutes. Skip it and you will spend the window chasing
platform noise that predates the deploy, then report a scare or an all-clear you cannot defend.

The failure mode this skill exists to prevent is not missing a regression. It is **reporting one that
was never there** — because alarming, wrong findings during a release cost more trust than silence.

## Do it in this order

1. Establish the payload — what changed, not what ran.
2. Decide what each change could plausibly move, and whether that is observable at all.
3. Find the signal in the code, not the metric browser.
4. Baseline it **before the rollout starts**, and prove the rollout had not started.
5. Arm a watch with thresholds derived from that baseline.
6. Judge every hit against a like-for-like comparison before reporting it.

Steps 1–4 are cheap and must happen before the rollout. Once pods start cycling, the pre-state is
gone and every later comparison is guesswork.

## Establish the payload, not the run

The deploy run's own commit is usually the **tooling** version, not the payload. Resolve the payload
separately: find the previously deployed revision, and diff. The dispatch timestamp is the reliable
anchor — the payload is typically the target repo's default-branch tip at the moment of dispatch, not
its tip now.

Then classify the diff, because most of it cannot produce a signal:

| In the diff | Can it regress production? |
|---|---|
| Lockfile / dependency-manifest churn | Only via the library's behaviour |
| Test, fixture, end-to-end test, docs, skill files | No |
| Deletions of already-unreachable code | No — check the endpoint removal shipped earlier |
| New or modified production source | Yes |
| A dependency whose **default behaviour** changed | Yes, and this is the one people miss |

A diff of hundreds of files that is entirely lockfiles plus one dependency bump has exactly one
risk surface. Narrowing to it is most of the work, and it tells you what to watch instead of watching
everything.

Read the change author's own risk analysis before forming your own. A good PR body names the
behavioural deltas and the things it could not establish; that list is your watch list, and its
"not established" section is where the real risk lives. Confirm its claims against current source
rather than trusting them — a claim that a fallback is byte-identical, or that an appended config
still applies, is checkable in minutes and worth checking.

Also establish what the pipeline itself verifies. If the deploy workflow runs no post-deploy smoke
test, a green run proves the rollout mechanics succeeded and pods came up — never that behaviour is
correct. Say so when you report, and check whether the pre-merge verification the change needed
actually ran and passed, rather than assuming a merged change was gated.

## Find the signal in the code, not the metric browser

Searching a metric namespace or a log stream for a library or feature name usually returns nothing
useful, and absence there proves nothing. **Both signal families are declared in source**, named for
the caller's domain rather than the dependency, and often several layers out from the code that
changed. Read them out of the code; do not guess them from a browser.

Start the same way for both: find the class that invokes the changed code, then walk outward through
its callers. Stop at the first caller that instruments or logs — that layer, not the library, is
where your queries come from.

### Metrics

Take the metric names from the registry that caller touches. Two things to check while you are there:

- **Which declared names are actually called.** A declared-but-never-invoked counter is a common
  outcome, and it means the thing you hoped to count is invisible no matter how you query it.
- **How the name maps into the namespace.** Where dotted metric names become hierarchical paths, a
  metric declared `a.b.c` sits several levels deep and a shallow wildcard will never match it. Search
  at the depth the naming implies.

### Log lines

Read the actual logging statements on the path and lift the query straight out of them:

- **The logger name** — usually the declaring class. This is what you match on, per the free-text trap
  below.
- **The message template**, so you match the literal, invariant part of the string rather than the
  interpolated ids that differ per occurrence.
- **The exception types** thrown *and* caught. These are the most stable, most searchable tokens on
  the path, and the catch blocks tell you which failures are translated into something else before
  they surface — a translated exception is logged under a different name than the one thrown.
- **The level each one logs at.** Check it; do not assume.

**The level is the trap.** A failure path that logs at `WARN` is invisible to any query or alert
filtered to `ERROR`, so a clean ERROR-scoped search over a genuinely failing path returns zero and
reads as health. Establish the level from the source before you trust an empty result — and if the
path's failures only ever reach `WARN`, note that **no ERROR-based alert rule can fire on it**. That
is a detection gap worth reporting on its own; hand it to
[`monitoring-gap-analysis`](../monitoring-gap-analysis/SKILL.md) rather than leaving it as an aside.

### When there is nothing

If a path is neither instrumented nor logged, say so plainly rather than substituting a proxy and
implying it measures the change. Some behavioural changes — values written into records, a validator
that grew more permissive, output formatting — are **not observable in telemetry at all**. That is a
finding worth reporting, not a gap to paper over.

Tooling: the metrics system's query interface for metric and log queries; for windows past the hot
retention, whatever the repo provides for historical queries; and where a metric store has no query
tool of its own, the script the repo provides for it.

## Baseline before the rollout starts, and prove it

Capture the pre-state while the build is still running, and capture it for **every signal you intend
to judge** — each metric series *and* each log query. Baselining one and not the other is how a
pre-existing error signature gets reported as a regression.

**For a metric series**, a baseline is not one number — it is a **distribution with a sample count**:
n, p50, p95, p99, max, and the count of samples beyond the threshold you intend to alert on. `max`
over a long window is the most useful single figure, because it tells you what this metric has never
exceeded.

**For a log query**, baseline two things:

- **The rate** — occurrences per fixed window, per component, over several windows rather than one, so
  you know the normal spread and not just a single sample.
- **The set of distinct signatures** present, normalised (ids, hex, timestamps and counts collapsed)
  so variants of one error fold together. This is the part people skip, and it is the only thing that
  lets you say a signature is *new* rather than merely *noticed*. Without it, every error you read for
  the first time looks like it started today.

Take the control over a window long enough to cover a full traffic cycle, and — for anything you will
call "new" — long enough to span several unrelated deploys. A control drawn from the same hour as the
deploy is not a control.

**Then prove the rollout had not started when you sampled.** Job-level start times settle it. This is
also the cheapest possible refutation of any early spike: if no pod had been replaced, the deploy
cannot be the cause, and one timestamp check saves an investigation.

## Comparing: like-for-like or not at all

Most false findings come from comparing the wrong two things.

- **Latency and throughput are diurnal.** A trough-hour figure against a business-hours figure differs
  by multiples with nothing wrong. Never judge post-deploy latency against a pre-deploy absolute taken
  at a different time of day.
- **The valid control is the previous deploy at the same phase** — the same number of minutes after its
  rollout finished. Cold JIT, empty caches and fresh connection pools make every rollout look like a
  regression against a warm fleet; the previous rollout's curve shows what that shape normally is.
- **Check whether the platform produced the same excursion with no deploy running.** A spike smaller
  than one the same metric threw spontaneously hours earlier is not a finding.

## Traps that manufacture false findings

**Counters reset on rolling restart.** Cumulative counters summed across a fleet *drop* as pods are
replaced, so deltas across a rollout window go negative and appear to show catastrophic traffic loss.
Prefer event-based counts (log occurrences) during the window, use the absolute level of small
counters, or a reset-tolerant derivative — and only trust fleet deltas once the rollout has settled.

**Free-text log matching hits payloads, not errors.** Log lines routinely embed the whole request or
event — headers, bodies, context fields — so a search for a feature or library name matches ordinary
traffic. Scope to the **logger name** or a stack frame instead. Every new pattern gets sanity-checked
against a pre-rollout window before you arm anything on it: *a pattern whose baseline is thousands of
lines cannot detect anything.*

**Some log streams swamp every query.** Customer-side or client-SDK log files can outnumber
server-side errors by orders of magnitude. Learn which they are for the datasource and exclude them
by filename in every query; otherwise a real count of 1 arrives as a count of millions.

**A metric index retains paths that no longer receive data.** Presence in a metric tree is not proof
a build, host, or feature is live — and neither is a query returning *any* non-null point, because a
retained historical point satisfies that long after emission stopped. Window the query to the period
you are judging and require a non-null point **inside that window** before using the series as a
baseline or as evidence of liveness.

**Thresholds without a control, and statistics without a sample size.** A "p50" over two samples is
the slower of two samples. Two rules, and the first has a number so it can actually be enforced:

- **Report no percentile below n=20, and no p95/p99 below n=100.** Beneath that, give the raw ordered
  values and the count instead — at small n that is both honest and more actionable than a statistic.
  Carry n in every percentile you state, in watch output and in the report, so the next reader can
  apply the same rule to your numbers.
- **Derive the alert threshold from the measured control**, not from a round number. If the control
  never exceeded X across hundreds of samples, one sample above X is signal; if the control regularly
  exceeds X, three of them are not.

## Separate deploy-caused from deploy-transient

A rolling restart reliably produces errors that are the *mechanism*, not a defect:

- **Consumer-group rebalance** on any queue consumer whose pods are replaced — offset-commit failures
  for revoked partitions, consumer-shutdown timeouts. Confined to the replacement window.
- **Cold-start latency** for the first requests against a fresh JVM or a fresh connection pool.
- **Shutdown-path races** in components being terminated. Note whose code runs: during a rolling
  deploy the shutdown path executes in the **outgoing** pods, so a new shutdown error reflects the
  *previously* deployed build, not the one arriving.

Three questions separate transient from caused:

1. **Is it confined to the replacement window**, and does it stop when the rollout finishes?
2. **Does the platform baseline already contain it?** Measure the same signature over days spanning
   several unrelated deploys. Recurring noise at a steady rate is a standing issue, not this deploy's.
3. **Does a same-shaped component behave differently?** If two components share the changed dependency
   and the same usage pattern and only one is affected, the dependency is probably not the cause. This
   is the strongest cheap discriminator available.

Keep known baseline noise written down per platform, with its measured rate, so the next watch does
not re-investigate it.

## What "no errors" does not prove

Zero errors is weak evidence for a whole class of change. Ask what the failure mode *looks like*
before treating absence of errors as safety:

| Change | Failure mode | Visible as an error? |
|---|---|---|
| Parser or validator loosened | Accepts input it used to reject | No |
| Serialization / format change | Malformed output downstream | No |
| Value mapping or classification change | Wrong values in records and reports | No |
| Retry or timeout added | Slower success instead of fast failure | No — latency only |
| API removal, config error, resource missing | Exception | Yes |

For the silent classes, the pre-merge measurement is the assurance and production telemetry is not.
Say which one is actually covering the change; do not let a clean log search read as a clean bill of
health.

Sparse call paths need the same honesty. If the changed path runs a handful of times an hour — batch
delivery, scheduled jobs, admin-triggered actions — the deploy window will not exercise it, and a
quiet window says nothing. Establish the call rate, say plainly that the path went unexercised, and
name what would exercise it. A regression in a path that runs on a customer's schedule can surface
days later, long after the watch ended.

## Arming the watch

Watch the run to a terminal state with the run-monitor script the repo provides rather than a
hand-rolled poll loop — it owns the interval and the deadline, and a run that was never dispatched is
otherwise indistinguishable from one still running.

For the telemetry watch, emit only lines you would act on, and make each one carry its own context —
the observed value, the control it violates, and the sample count. An alert reading `2 of 8 calls over
600ms; control was 0 of 949` is actionable; `LATENCY HIGH` sends the next reader back to the beginning.

Cover failure as well as progress: a watch that greps only for the bad signature stays silent through
a crash, and silence looks identical to health.

## Reporting, and revising

Report the payload, the signals with their controls, and the verdict per signal. State the residual
risk the watch could not cover — the sparse path, the silent failure mode, the metric that does not
exist.

**Small samples move fast, and a conclusion drawn at n=2 will often not survive n=25.** Re-check
before escalating, label anything unproven a hypothesis rather than a cause (see
[`root-cause-proof`](../root-cause-proof/SKILL.md)), and when the reading
changes, report the current one and say plainly that it changed. A finding that softened is worth more
than a scare left standing.

Close with the honest self-evaluation
[`verify-before-complete`](../verify-before-complete/SKILL.md) requires —
including which of your own alerts were false and why, because a miscalibrated watch is a defect in
the work product, not a footnote.

## Verification

The watch was done properly if you can answer all of these:

- What was the payload, and which part of it could regress production?
- For each risk, which signal would move — or is it unobservable, and did you say so?
- Did the metric names and log queries come **out of the source** — registry names, logger names,
  message templates, exception types, and the level each logs at — or were they guessed from a
  browser?
- Does any failure path on the change log only at `WARN`? If so, did you say that no ERROR-based alert
  can fire on it?
- What is the control, for each signal: window, n, and either the value the metric never exceeded or
  the log rate and the set of signatures already present?
- Had the rollout started when the baseline was taken?
- For every alert that fired: transient, baseline noise, or caused — and on what evidence?
- What could this watch not cover?
