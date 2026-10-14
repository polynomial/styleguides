---
name: rca-writing
description: Must be read when asked to write an RCA, root cause analysis, or post-mortem for a past incident, or to publish one to the team wiki's RCA page.
---

# RCA Writing

## Workflow

| Phase | Goal | Tools |
|-------|------|-------|
| **1 — Context Gathering** | Reconstruct what happened | Chat search + thread reads |
| **2 — Template Discovery** | Start from the local template, cross-check the wiki | The repo's local RCA template + the wiki's API / the institutional-context tool |
| **3 — Critical Review** | Challenge what you've found before writing | Your judgment |
| **4 — Draft & Publish** | Land the markdown draft in a PR, then publish to the wiki | git + `gh pr create` + the wiki's page-creation API |

## Phase 1: Context Gathering

Incidents leave traces across multiple channels. Search iteratively — one search is never enough.

### Search Strategy

1. **Broad keyword search** with date filters to find primary threads:
   ```
   query: "<keyword> after:YYYY-MM-DD before:YYYY-MM-DD"
   sort: "timestamp", sort_dir: "asc"
   ```
2. **Channel-specific searches** — incidents typically span:
   - the escalation channel — escalation tickets, technical discussion, impact analysis
   - the engineering help channel — initial reports, cross-team escalations
   - the oncall channel — alert triage, pager correlation
   - the RCA tracking channel — RCA tracking, due dates, discussion notes
   - customer-specific channels — external reports, customer-facing symptoms
3. **Read full threads** — parent messages rarely tell the full story. Read every thread you find in full. The critical details (impact numbers, root cause identification, revert decisions) are almost always in replies.
4. **Follow cross-references** — chat messages link to other threads, dashboards, pull requests, and tickets. Chase each one. A PR link tells you *what changed*; a dashboard link tells you *what broke*.

### What to Extract

| Data point | Where to find it |
|---|---|
| Incident start time | First error report or earliest log timestamp mentioned |
| Incident end time | Confirmation of fix deployed / notifications stopped |
| Root cause | Technical discussion in the escalation or engineering help threads |
| Impact numbers | Reports, dashboard links, or explicit counts in threads |
| Related PRs | Pull request links in chat messages (both the causing PR and the fix PR) |
| Related tickets | Ticket keys referenced in the threads |
| Deploy/build details | CI links, build failures, retry attempts |
| Customer-facing symptoms | Customer channel messages, support team reports |

### Context Quality Gate

Before proceeding, verify you have:
- [ ] Clear incident start and end times (with timezone)
- [ ] Root cause identified with supporting evidence
- [ ] Impact quantified (failure count, affected %, duration)
- [ ] Timeline of key events (discovery, diagnosis, fix, deploy, verification)
- [ ] Links to relevant chat threads, PRs, tickets

If any are missing, search more specifically. Don't proceed with gaps — an RCA with a vague timeline or unquantified impact isn't useful.

## Phase 2: Template Discovery

**Do not hardcode the RCA format.** Use the local mirror as the canonical layout, and cross-check against the live wiki template before publishing.

### Local template (canonical drafting copy)

- The repo's local RCA template — a verbatim mirror of the wiki template, formatted as proper markdown, with two extra required sections (Decision log + ADRs) appended per [`investigation-contract.mdc`](../../rules/investigation-contract.mdc).
- Use this file as your starting point. It is always available even when the wiki's API access is not.
- **If you change the local template, update the wiki in the same PR. If the wiki has drifted, update the local template in the same PR.** The two must match section-for-section, except for the two appended sections (Decision log + ADRs) which are required for repo-side investigations and not part of the upstream wiki template.

### Wiki references

The wiki holds an RCA parent page, under which every published RCA lives, and a template page that is the source of truth for the layout. The local template's header names both.

### Steps

1. **Copy the local template** into `docs/investigations/<area>/<topic>_<YYYYMMDD>/README.md` (date is the **incident date**; create the directory first) and start filling it in. Remove sections that aren't relevant to your incident — an RCA full of "N/A" answers is noise. Keep sections where you have real content or where the absence itself is a meaningful finding.
2. **Cross-check against the live wiki template** before publishing — the upstream template can drift. Fetch the template page in markdown through the wiki's API. If sections, questions, or labelling requirements differ, **update the local template in the same PR** so the next agent starts from a faithful copy. If the wiki's API is unavailable, fall back to the institutional-context tool's URL fetch on the template page.
3. Optionally read a recent RCA child of the parent page to see how others filled it in.
4. Keep the **Process retrospective** and **Decisions** sections from the local template — they are required by [`investigation-contract.mdc`](../../rules/investigation-contract.mdc) for any investigation under `docs/investigations/`. They do not appear on the wiki page once published; they live in the repo-side draft.

### Title Convention

`RCA YYYY-MM-DD <Short Description>` — the date is the **incident date**, not the writing date.

## Phase 3: Critical Review

Before writing, challenge your own findings. This is the most important phase.

### Timeline Scrutiny

- **Verify causation, not just correlation.** A deploy happened before the incident — does the thread actually confirm it caused the issue, or are you assuming?
- **Check for gaps.** If the incident started at 7 PM and wasn't noticed until 8 AM, explain *why* it was silent for 13 hours. That gap is itself a finding.
- **Get the fix timeline right.** Don't just say "fix deployed." Include failed build attempts, workarounds, and the actual confirmation that the fix worked. The path from "we know the cause" to "production is healthy" is often messy and worth documenting.

### Impact Scrutiny

- **Distinguish total requests from affected requests.** "8,967 failures" means nothing without "out of 44,302 total."
- **Identify who was affected.** Not all users hit the same code path — which ones were impacted?
- **Check for downstream effects.** Did the incident cause notifications, false alerts, or customer-visible error messages beyond the primary failure?

### Root Cause Scrutiny

- **Go one level deeper than the obvious.** "We pointed reads at the replica" is what happened. *Why* it caused a failure (the endpoint has a write path that wasn't obvious) is the root cause. Why that write path wasn't obvious (the endpoint is called `get_or_create` but was treated as read-only) is the systemic issue.
- **Identify detection gaps.** If the endpoint returned HTTP 200 with empty body, that's not just a bug — it's a monitoring blind spot worth calling out.

### Monitoring Scrutiny (required — see the [`monitoring-gap-analysis`](../monitoring-gap-analysis/SKILL.md) skill)

Every RCA/CIA must answer "would monitoring have caught this?" with evidence, not intent. Use the **monitoring-gap-analysis** skill and put the result **in the document**:

1. **Classify the incident shape first.** "Worked then broke" is usually visible to existing detectors — ask why the alert was missed, dismissed or mistuned. **"Never worked since launch" is structurally invisible**, because almost every detector in a fleet fires on a transition out of a healthy state.
2. **Name a concrete detector** and classify the work TURN_ON / TUNE / AUGMENT / BUILD.
3. **Backtest it over the real incident window** with the detector-replay tool the repo provides: first alert date, lead time vs actual discovery, and which live detectors stayed silent. Run reports ad hoc to get the historical window — don't settle for the last 90 days.
4. **Report the alert volume next to the lead time**, and record an explicit **enable / don't-enable / observe-mode** judgement. A detector may be correct and still too noisy to turn on — that verdict is a valid, valuable outcome, and it belongs in the CIA as a discussion point rather than being silently dropped.
5. **Check the alert channel, not just the config.** Automated alerts land in the ticket tracker's support queue as `<shortname>: <alert>` assigned to the monitoring account. Report the **disposition mix** — a family that fires and is always closed `Won't Do` is not working monitoring.

### Next Steps Scrutiny

- **Every next step should be actionable and linkable.** "Improve monitoring" is not a next step. "Add a metrics-system alert for SQL exceptions in the client API" is. Link to a ticket if one exists.
- **Monitoring next steps carry their backtest numbers.** "Enable the concentration detector — 43-day lead, 0.35 alerts/week" is actionable; "add fraud alerting" is not.
- **Separate quick fixes from systemic improvements.** The revert fixed the immediate issue. The longer-term fix (separating read/write paths) is a different work item.
- **Don't invent next steps from thin air.** If the chat threads don't discuss follow-up work, note what you'd recommend but flag that it wasn't discussed yet.

## Phase 4: Draft & Publish

### Step 0 — Embed graph snapshots (required)

**Every RCA / investigation doc must embed rendered snapshots of the firing alert's panel(s) plus the supporting context panels, captured at RCA-creation time.** A committed PNG is what the reviewer, the next oncall, and someone six months out actually see; an auth-gated dashboard URL is not (and its time range drifts). The graphs also catch what prose misses — in a 2026-07-18 webhook RCA the consumer-lag snapshot exposed that consumer-group lag had exceeded a threshold the text had assumed was never crossed.

- Render with the metrics system's read-only panel renderer. Commit the PNGs next to the doc under `docs/investigations/<area>/<topic>_<YYYYMMDD>/images/` and pair **each** image with a **live dashboard deep-link** scoped to the incident window.
- At minimum: the exact panel the alert points at (the alert body's dashboard and panel links give the identifiers), plus the panels that show cause vs symptom for this incident class (e.g. for stream-delay: processing delay, batch duration, batch size, executors, broker lag).
- **Never fabricate a chart** (violates [`evidence-integrity`](../../rules/evidence-integrity.mdc)). If the renderer is unavailable, say so explicitly in the doc and fall back to deep-links only — do not draw a plausible-looking graph.

### Step 1 — Land the markdown draft in a PR (required)

Per [`investigation-contract.mdc`](../../rules/investigation-contract.mdc) the draft must live in git **before** publishing on the wiki:

1. Create an investigation branch: `git checkout -b <topic>-<YYYYMMDD>` — no tool-name prefix, no `/`.
2. File the draft at `docs/investigations/<area>/<topic>_<YYYYMMDD>/README.md` (date is the **incident** date; one directory per investigation).
3. Commit, push, and **open a PR to the default branch** (`gh pr create`, never `--draft` — say in the body which impact numbers are still TBD). Land it in the end state [`agent-pull-requests.mdc`](../../rules/agent-pull-requests.mdc) prescribes and verify with `gh pr view <n> --json state`.

### Step 2 — Publish to the wiki

When the markdown is ready (or the user explicitly requests publishing of an in-progress draft), create the wiki page. **Strip the repo-only sections** (`## Process retrospective and chat-driven revisions` and `## Decisions` / ADRs) — those stay in the markdown only; the wiki body should match the upstream template.

```
create page(
  parent: <the RCA parent page>,
  title: "RCA YYYY-MM-DD <Short Description>",
  format: markdown,
  status: current,
  body: "<markdown content with Decision log + ADRs removed>"
)
```

### Step 3 — Backfill the wiki page id into the repo

After publication, capture the new wiki page id and (optionally, when the page is final) drop a sibling export under `docs/rcas/<page_id>_RCA_<YYYY-MM-DD>_<short_description>.md` so the published RCA becomes part of the searchable repo-side history (matching the repo's existing `docs/rcas/` convention). Reference the wiki page id in the original `docs/investigations/<area>/<topic>_<YYYYMMDD>/README.md` header.

### Writing Principles

- **Neutral language** — describe events, not blame. Use handles, not full names.
- **Link everything** — chat threads, PRs, tickets, dashboards. An RCA is a reference document.
- **Quantify** — "20.2% failure rate over 13.5 hours" not "some users were affected."
- **Be mechanistically specific** — "The `id_generator` INSERT failed on the read-only replica" not "the database had issues."
- **Include the full fix arc** — from diagnosis through failed builds to successful deploy and verification.
- **Show, don't just link, the graphs** — embed rendered panel PNGs (Phase 4, Step 0) so the evidence is visible in the doc/PR itself, each with a live deep-link.
