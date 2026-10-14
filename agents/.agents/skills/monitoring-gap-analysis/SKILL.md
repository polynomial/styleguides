---
name: monitoring-gap-analysis
description: Must be read before writing a CIA or RCA Prevention section, or when asked "could we have caught this", "why didn't this alert", or what monitoring would catch it next time.
---

# Monitoring gap analysis

Turns "could we have caught it?" into a reviewable artifact: a per-detection verdict
against the customer's real monitoring surface, plus a ranked list of work in four
classes — **TURN_ON**, **TUNE**, **AUGMENT**, **BUILD**.

Read this before writing any CIA (customer impact analysis) or RCA "Prevention
Opportunities" section. Prevention items that are not one of those four classes,
against a named data source, are aspirations and will not ship.

**Required for every CIA and RCA.** It is not complete until it names at least one concrete detector,
backtests it over the real incident window, and records an enable or don't-enable judgement with the
alert volume. "We had no monitoring for this" is not a conclusion, and neither is "add monitoring"
without the signal, the data source and the noise cost.

## The rule that makes this worth doing

**Almost every detector in a monitoring fleet fires on a *transition out of a healthy state*.**
Drop, zero-drop, stalled, and the contribution-rate floor all need prior healthy
history. So:

- "It worked and then broke" → usually detectable today; ask why the alert was
  missed, dismissed, or mistuned.
- "It never worked since launch" → **structurally undetectable** today. Measured on
  one fleet's funnel monitor: its post-handler removes zeros in preprocessing and
  marks a series ignored when it is empty afterwards, rendering it in alert bodies
  only as `(has only zero values)`. Its contribution-rate evaluator returns early
  when the rate is 0, and when the previous value was already below the floor it
  *deletes* the z-score and zero-drop results too.

Classify the incident on that axis first. It determines whether the answer is
"tune what we have" or "we have nothing, here is what to build".

## Procedure

### 1. Classify the incident shape

| Shape | Example | Where detection must come from |
|---|---|---|
| Worked, then broke | share clicks drop to zero | existing funnel monitors — ask why they were dismissed |
| Never worked since launch | an eligibility path that never produced a conversion | a ratio against an independent expectation; not the funnel's own history |
| Distribution | one referrer, 120 friends | referrals-per-advocate concentration |
| Structure | a referred person becomes a referrer, and chains | relationship-graph depth + friend→advocate velocity |
| Config drift | fraud screening off / non-standard thresholds | program configuration audit |

### 2. Inventory what exists — do not guess

Run the repo's read-only detection-coverage audit for the account. It reads the
account's scheduled report runners, its report post-handlers (and their built
form), its report types, and every consumer program's built triggers, then
evaluates them against the repo's detection catalog.

The detection surface is four layers — check all four, they fail
independently:

1. **Report runners** — is the data even produced? A disabled or paused runner
   means the monitor below it never sees anything.
2. **Report post-handlers** — the alert logic. Legacy handlers are usually
   `enabled: false` with the component-based build-time handlers live; `enabled`
   may itself be a build-time expression, so do not read it as a boolean.
3. **Program triggers** — fraud screening and quality gates.
4. **Report types** — capability that exists but is never run. A fraud-insights
   report is the standing example: available for every account, scheduled for
   none of the four audited.

### 3. Confirm the negative at the alert channel

Never conclude "no monitoring existed" from config alone. Automated alerts land in
the ticket tracker's support queue as `<account shortname>: <alert name>`, assigned
to the monitoring account. Query that queue for the shortname prefix over the
incident window, newest first.

Then read the **disposition**. A family that fires and is always dismissed is not
monitoring. One account received 10 automated funnel alerts over 18 months and 9
closed `Won't Do`; another's one fraud alert was closed in under a minute and later
tagged as a monitoring failure. Report the dismissal rate — it is usually the real
finding.

Alert bodies are the best available documentation of what the monitor can say. The
grammar is: `have an anomalous drop`, `have dropped to zero`, `have been stalled`,
`have fallen under the configured threshold of N%`. Anything outside that grammar
is not something the monitor can currently tell you.

### 4. Find the silent-since-launch paths

Run the repo's zero-baseline scan against the account and the runner that feeds
the funnel monitor.

It reconstructs exactly the set the monitor discards, ranked P1–P4. **P1 is a lead,
not a finding.** Verify every P1 against sibling metrics before writing it down —
on one account, `converted / Conversions = 0` for 92 days looked alarming and was
structural, because the same step's rewarded-friend conversions were 21 and the
account's outcome was modelled on a different pair of events.

### 5. Score the fraud shapes

Run the repo's referral-structure scan over the account's full network-relationships
report download.

Two data-source traps, both proven:

- **A "biggest networks" report is rank-limited.** For one account it returned 22
  networks of up to 30 edges; the actual 16-edge ring apex was *absent*. A
  mid-sized ring hides behind legitimate large networks. Same family as a
  "people by IP > 5" filter that hid another account's rotating-VPN accounts.
  Source structural detection from full relationships, not a top-N view.
- **The report carries no edge timestamp**, so burst and friend→advocate velocity
  cannot be computed from it — those need the relationship API, which does carry
  dates.

Calibration note: the real ring measured was **depth 2**, so a depth ≥ 3 threshold
misses it. Depth 2 alone is normal refer-a-friend behaviour, so it reports MEDIUM
and escalates on velocity.

### 6. Backtest it — this step is not optional

A proposed detector is a hypothesis until it is replayed against the window in which the incident actually happened.

- **Fraud / referral shapes** need dated edges: pull the relationship graph from the
  apex person to depth 2 with the repo's graph-pull script, then replay the detector
  over those edges with the repo's detector-replay script, giving it the discovery
  date and writing the backtest under `docs/investigations/monitoring/`.
- **Funnel-metric shapes**: replay the detector-replay script over a date / value /
  denominator series (the metric and its upstream metric), with the discovery date.
  It replays the **live** detectors too, so their silence is shown.

**Get the real historical window.** Do not settle for whatever the last scheduled report covers:

- The report the monitor watches can usually be re-run for any window with an explicit historical time range **plus** a period, so the exact series the monitor sees can be reconstructed for the whole incident. This is how one account's 71-week incident window was obtained.
- The per-person relationships endpoint returns **dated** referral edges; the network-relationships report does not. Crawl from the apex.
- Check the download format before parsing — one report's downloads were JSONL, not a JSON array.

**Scope the replay to the incident**, with `--since` / `--until`. Crawling from an advocate returns their whole history, and a detector firing 10 months before the incident is a different claim from catching the incident — sometimes it is the false positive the customer warned you about.

Report, always together:

| What | Why |
|---|---|
| First alert date + **lead time** vs actual discovery | the benefit |
| **Alerts/week** across the window | the cost |
| Which **live** detectors stayed silent | proves the gap instead of asserting it |

### 7. Judge it — noise is the gate, and the judgement is a discussion point

**A detector being correct is not sufficient reason to enable it.** Write the trade-off down and leave the decision with whoever would receive the alerts. Measured examples:

| Result | Judgement |
|---|---|
| 43-day lead, **0.35** alerts/week (a concentration detector) | recommend enabling |
| 43-day lead, **2.68** alerts/week (a velocity detector on the same account) | observe mode; escalate only combined with concentration |
| 5-day lead, **6.48** alerts/week, firing since 2024-09 (a second account) | **recommend not enabling at these thresholds** |
| 467-day lead, **0.98** alerts/week for 68 of 71 weeks (a never-healthy account) | enable as a **weekly digest**, never as a per-period alert |

Three rules that fall out of this:

- **Noise is per-account.** The same detector at identical thresholds: 0.22/week at one account, 0.35 at another, 6.48 at a third. Derive thresholds from each account's own baseline.
- **A chronic condition needs a digest, not an alert.** If the condition stays true until someone fixes it, a per-period alert is guaranteed alert fatigue. Do **not** respond by removing an existing suppression — route chronic states to a low-frequency channel.
- **Lead time alone rewards bugs.** One concentration detector originally showed a 51-day lead purely because the first referrer of the day trivially owns 100% of two referrals. A minimum-volume floor gave the honest 43 days *and* cut volume by a third. Always read lead time with volume beside it.

### 8. Write the recommendations

Every item needs: **class** (TURN_ON / TUNE / AUGMENT / BUILD), **data source that
already exists**, **the alert primitive**, **a false-positive analysis**, its
**backtest numbers**, and an **owner**. Rank by leverage, cheapest-and-safest
first. State honestly when a proposed detection could not have caught the incident
— on one account, augmenting the funnel monitor would *not* have helped, because
the affected step was not one of the 13 steps in the report it monitors.

**Put the parsed results in the CIA itself**, not only in a repo doc: a table of
detector / first alert / lead time / alerts-per-week, plus Action Plan items with
owners. A backtest that lives only in git does not become a decision.

Add or amend a detection in the repo's detection catalog so the next incident
inherits it. Every entry must carry `false_positive_notes` — the tests enforce
that.

## Traps

- **`enabled` is not always a boolean.** Component handlers carry a build-time
  expression; treat non-`false` as enabled and say so.
- **Utility programs are not programs.** Monitoring, global, integration, helper
  and configuration campaigns are extension / integration / configuration
  programs. Auditing fraud screening across the raw program list manufactures
  false positives; filter to consumer programs first.
- **The marker check proves capability, not configuration.** A string in the
  compiled bundle means the code can do it. A contribution-rate block
  (`enable: true`, `lowerBoundThreshold: 1`) is a bundle-wide default identical
  across accounts — so "account A alerts and account B does not" is about the
  data crossing the floor, not about per-account setup.
- **More data is not more monitoring.** Scheduling a fraud-insights report produces
  reports nobody reads unless a post-handler or a review cadence is attached.
- **Never size an age/staleness threshold on a tail percentile.** The tail is
  contaminated by the incident you are trying to catch: one account's own p99
  time-to-earn was 50 days *because* a re-evaluation released its 114 frozen
  rewards, so a p99-derived threshold is 65 days and never fires on a recurrence.
  Use the **median**, which is robust to that and still sees a designed hold,
  because a designed hold moves the whole population (a boosted campaign on another
  account: p50 = 35.00 **and** p99 = 35.01). The repo's stuck-reward calibration
  script does this, including a thin-sample guard — per account **and per
  campaign**, because an account can look readable while one of its campaigns has
  6 resolved against 1,128 open.
- **A pile of pending things is not evidence of a stall.** A fast-growing or
  long-cycle program looks identical to a frozen one on the open population alone —
  one account showed 458 open against 12 resolved and was perfectly healthy, having
  grown 40x in two months. What settles it is what happened to the items **old
  enough to have finished**: a healthy long cycle empties its old age buckets, a
  freeze leaves them full (the calibration script's outcome-by-age view). Neither
  the open/resolved ratio nor the age histogram of open items distinguishes the two.
- **Don't propose removing a suppression.** The chronic-underperformance early
  return exists so a legitimately-below-floor account is not alerted every period
  forever. Route chronic states to a low-frequency digest instead.

## Cause-side and harm-side detectors do not substitute for each other

When an incident has a configuration cause, it is tempting to propose only the config audit — it is cheaper
and quieter. Propose **both**, and say why: one fleet sweep measured the non-overlap. It found three
accounts actively losing rewards (8,064 people, 44 and 10), and **all three had zero config drift** — the
audit is blind to them. Meanwhile a fourth account carried six drifted controllers and had frozen
**nothing**, because its campaign was still live — the harm-side monitor is blind to it.

The audit catches the known class before harm; the state monitor catches unknown causes after harm starts.
Shipping one means accepting the other's blind spot.

## Related

- The repo's detection catalog — the detections, verdicts, actions — and its read-only
  monitoring scripts: the coverage audit, the zero-baseline scan, the structure scan,
  the graph pull, the detector replay, and for stuck/stalled-state detection
  specifically a resumable fleet sweep, a sweep-progress reader, the median-threshold
  calibration with thin-sample guards and the outcome-by-age view, a weekly replay
  backtest, the shared detector rule, and a **cause-side** rule-state drift audit
  (run it on demand after a component-library change, a fleet migration, or a
  stuck-reward report, not on a cron)
- The repo's monitoring test fixtures, including the pyramid-shaped referral ring
- [**oncall-investigation**](../oncall-investigation/SKILL.md), [**root-cause-proof**](../root-cause-proof/SKILL.md) — run those first; this skill answers prevention, not cause
- A scheduled monitor that pages is the build path once a BUILD item is agreed
- Infrastructure alerting lives in the metrics system; this skill covers customer-program detection
