---
name: oncall-investigation
description: Must be read when given a pager link or incident id, or asked to triage an alert, an oncall page, a production incident, or production health.
---

# Oncall Investigation

## Trigger: a pager link auto-runs this whole workflow

A **pager link** (an incident or alert URL from the paging system) or a raw incident id in the user's message **is** the request to run this entire workflow end-to-end — live-state → mitigation-ready → RCA → investigation doc → pull request to the default branch. Do not stop at an incident summary and do not ask "want me to investigate?"; start immediately. This is enforced by the always-on [`investigation-contract`](../../rules/investigation-contract.mdc) rule. Pull the incident through the pager's API (the incident, its alerts, its notes) — never eyeball the URL — then follow the firing alert to its alerting rule → dashboard/panel → datasource → the infrastructure-as-code file the alert's source annotation names.

## RCA docs must embed graph snapshots (required)

The investigation doc must embed **rendered PNG snapshots** of the firing alert's panel(s) plus the supporting cause/symptom context panels, captured at RCA-creation time, each paired with a live dashboard deep-link scoped to the incident window. Render them read-only with the metrics system's panel renderer; commit the PNGs under `docs/investigations/<area>/<topic>_<YYYYMMDD>/images/` (same package directory as the write-up's `README.md`). The alert body's dashboard and panel links give the dashboard and panel identifiers to start from. A link-only RCA is incomplete — the reviewer should see the graphs in the PR. Never fabricate a chart; if the renderer is down, say so and fall back to deep-links.

## Fix skills that fail out-of-the-box (same session)

If any skill you use during the investigation has a wrong/missing command, tool path, metric name, or resource mapping, **fix that skill's SKILL.md (or its canonical owner in the owning repo) in the same session** and include the edit in the investigation PR. A skill that made you improvise will make the next agent improvise. (Originating ask: a 2026-07-18 webhook-delay investigation.)

## Phased workflow (summary)

The phases are **strictly ordered**. The `investigation-contract` rule enforces the order: phases 1–3 (issue-finding + mitigation-ready) **must complete** before phase 4 (RCA / timeline). Do not start phase 4 until the executive summary of phase 3 is written.

| Phase                     | Goal                           | Do                                                                                                                                                                                                                                      |
| ------------------------- | ------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **1 — Live state**        | What is broken right now?      | Live system inspection first: for example `kubectl get pods/nodes/events`, `aws describe-…`, target health, queue depth, replication state. Confirm the failing component(s) before reading any history.                               |
| **2 — Triage / severity** | Is prod impacted now?          | Read alert; current errors/latency in the metrics system; severity; blast radius from the live state in phase 1                                                                                                                         |
| **3 — Mitigation-ready**  | What can we do about it?       | Write the cheapest no-risk mitigation, plus any durable fixes. Each option lists: command, blast radius, revert path, verification signal. Present for approval if not auto-runnable. **Recurrence gate:** if prior-work checks show this is a repeat of a known family, "do nothing / let it auto-resolve" is forbidden as the recommendation — lead with durable-fix work executed this session (see [`investigation-contract`](../../rules/investigation-contract.mdc)). **Stop here and report unless told to continue.** |
| **4 — Context / RCA**     | True cause + when did it break | The pager incident; the CI run if CI; dashboards + log history; **unified UTC timeline** (deploy, CDN TTL, logs, backends); git/PR archaeology; pattern match; test hypotheses                                                           |
| **5 — Resolution**        | Fix + verify                   | Implement fix; **confirm metrics/logs**; don't stop at write-up                                                                                                                                                                         |
| **6 — Prevention**        | Less recurrence                | Leading indicators, alerts (absence/coverage), runbook, investigation PR in `docs/investigations/`. For recurrences: prevention is **executed, not proposed** — post the owning-ticket update / open the fix PR / create the escalation artifact in this session. **Monitoring gate:** name a detector, **backtest it over the real incident window** (replay it with the detector-replay tool the repo provides), and record first-alert date, lead time, alert volume and an explicit enable / observe-mode / don't-enable judgement — see the [`monitoring-gap-analysis`](../monitoring-gap-analysis/SKILL.md) skill. "No monitoring existed" is not an acceptable conclusion; "correct but too noisy to enable" is, with the numbers to back it |

## Collated timeline (complex incidents)

- Pull timestamps from **CI**, **the log system**, **CDN/cache**, **app logs** into one table (UTC).
- Include **CDN/browser TTL** — symptoms can lag deploy by hours.
- **Deploy correlation (always):** recent merges to the affected component (the institutional-context tool); autoscaling-group / deploy signals; **schema version bumps** and cache-behaviour PRs; 48h metric baseline before/after.

## Workflow (short)

1. **Live state first** — inspect the live failing component (pods, nodes, queues, replication, target health) **before** reading any history. One paragraph: "X is broken because Y, evidence: Z."
2. **Triage** — read the alert, assess severity, check current production impact
3. **Mitigation-ready** — write down options A/B/C, each with scope, blast radius, cost, feasibility, revert, and verification. Stop and present before taking further action unless told to continue — but write the investigation doc and open the PR regardless (the gate pauses action, not the durable record).
4. **Gather Context / Correlate** — _now_ query the metrics and log history, the cloud provider, Kubernetes events, the pager; build the unified UTC timeline; check deploy correlation
5. **Root Cause Analysis** — hypothesize, test with data, dig deeper than the surface
6. **Resolve** — implement the fix when authorized, don't just document recommendations
7. **Prevent** — identify leading indicators, add monitoring (especially **absence** and **coverage** alerts), document findings

## Tools

| Tool                           | Use for                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              |
| ------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| The metrics system             | Read the **alerting rule** by the identifier in the alert's view link, then the **dashboard panel** it points at (its query targets and which datasource each routes to), then query the metrics and logs. Sequence alert → dashboard → datasource before querying; a panel often routes to a different datasource than the one you would have guessed.                                                                                                                                                                                                                                                                                                                                                                                                                                                  |
| The cloud provider's CLI       | Cluster, instance and database status, for example `aws describe-…`.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
| Kubernetes                     | Pod status, events, logs, autoscaler scaling. **When a Kubernetes tool integration is denied cluster reads, use plain `kubectl`** — the tool's service account may be denied while `kubectl` is already authenticated, so `pods is forbidden … cannot list resource "pods"` is not "no Kubernetes access" (on one incident, pod specs, per-node executor packing and node allocatable — the evidence that identified the root cause — were only reachable via `kubectl`). Note `kubectl logs` returns only the tail the kubelet retains (~150 lines for a busy driver); for history use the log system. **On a workstation the tool reads whatever kubeconfig context is current**; `the server has asked for the client to provide credentials` means the wrong cluster, not missing access — switch context with `kubectl --context <cluster>`. **A read-only identity exported by the shell is preferred over the kubeconfig's profile**, so a runbook write such as `cordon` is refused with `cannot patch resource "nodes"`. An engineer runs the write with the read-only credentials unset. An agent does not use the engineer's identity. It hands over the command. Kernel journal lines from every node usually reach the log system under the journal job — `hung_task` stack traces, OOM kills and I/O errors need no SSH. |
| The pager                      | Incident details, service status, on-call schedules                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |
| The institutional-context tool | **Fire in parallel with the first log queries — not after.** Historical context (prior chat threads, tickets, past fixes) often resolves root cause before log analysis finishes. Run a research query on the error string, component name, and customer/service name immediately.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |

## Critical Rules

- **Issue-first, then root cause** — see [`investigation-contract`](../../rules/investigation-contract.mdc). Live system inspection and mitigation options come **before** log/git/PR history. Inverted order is a defect.
- **Always end with an investigation doc + open PR** — see [`investigation-contract`](../../rules/investigation-contract.mdc). This is mandatory for any material finding (root cause, timeline, ranked mitigations, or a "recovered on its own / no action needed" verdict), **even for a read-only investigation and even when you stop at the Phase 3 gate**. Do not offer the write-up as an optional follow-up ("want me to open a PR?") — produce it and report the link. The Phase 3 stop pauses further *action*, never the durable record.
- **Every mitigation option carries scope, cost, and feasibility** — see [`investigation-contract`](../../rules/investigation-contract.mdc). Rank by risk, lead with the surgical option, and for each option (including "no action" and each deferred durable fix) state scope, cost, and feasibility so the reader can weigh do-nothing vs. invest with real numbers.
- **Complete investigations fully** — once authorized past mitigation: identify root cause, implement fix, verify resolution, document
- **Root-cause proof bar is mandatory** — do not stop at "likely code path". Before declaring root cause, provide all of:
  1. **Runtime evidence** (live logs/metrics showing the failing signature),
  2. **Entity evidence** (the concrete conflicting/invalid object values from prod data),
  3. **Deterministic repro** (API/command replay that reproduces the same error code/message),
  4. **Code mapping** (where that exact error is generated in source).
  If any item is missing, root cause is incomplete and must be labeled as a hypothesis.
- **Always check deploy correlation** — look for recent pull requests to the component merged before the incident (in phase 4, not phase 1)
- **Always create a collated timeline** — map events from all sources chronologically (in phase 4)
- **Always verify timezone** — the pager may display local time, logs are UTC
- **Calculate timestamps dynamically** — never hardcode epoch values
- **Cite every finding** — every statement must be a verified fact with source, or explicitly marked as inference
- **Log proof must be backtrackable** — whenever a log line is used as root-cause evidence, include both:
  1. the **full raw log line** (verbatim, no truncation),
  2. a **deep link into the log system** that re-runs the exact query and time range used.
- **Verify negatives at the rawest layer** — see [`evidence-integrity`](../../rules/evidence-integrity.mdc). Before asserting "X is never sent / never happens", prove the log's emitter actually observes the traffic (path/method guards), then raw-string search the log group for the token you claim absent.
- **Check in-flight work before root cause** — see [`investigation-contract`](../../rules/investigation-contract.mdc). `gh pr list` (open + merged near the incident), `git log` on the component path, the institutional-context tool. Unreadable referenced chat threads are a blocker: ask the user to paste them.
- **Recurrence forbids "do nothing"** — see [`investigation-contract`](../../rules/investigation-contract.mdc). If the prior-work checks surface the same alert/failure fingerprint in earlier incidents, the recommendation must be durable-fix work executed this session (fix PR, owning-ticket comment with recurrence count + priority ask, or escalation artifact). "Let it auto-resolve" may only appear as a live-state status line; self-healing is a symptom, not a resolution.
- **Investigation doc structure mirrors the workflow** — Executive summary → Live-state evidence → Mitigation → _then_ Root cause / Timeline. Timeline-heavy summaries with thin mitigation are the symptom of inverted priority.
- **Every investigation doc includes a chat-context section + ADRs** — see [`investigation-contract`](../../rules/investigation-contract.mdc). The doc must capture each user prompt verbatim with what it drove, and every choice (which mitigation, what was deferred, what was NOT touched) goes in an ADR block (Status / Date / Context / Options considered / Decision / Consequences). Inline ADRs by default; standalone in `docs/decisions/` only if multi-investigation.

## Common Investigation Patterns

- **Service degradation** — error rates, latency, recent deploys
- **Test failure alerts** — CI logs, flaky vs real failures
- **Resource exhaustion (OOMKilled)** — memory limits, traffic spikes, sidecar containers
- **Database issues** — validate metrics against actual DB queries, check slow query log
- **Configuration issues** — recent config changes, routing rules, feature flags
- **Traffic spike cascading failures** — identify source, check rate limiting, backend lock contention
- **Several external uptime-check pages at once** — these are usually HTTP checks of hostnames that all alias to one ingress gateway; they are neither DNS nor pod alerts. Go straight to the gateway's load-balancer target health and the gateway pods. If the pods all show one restart at the same second, the evidence is in the **previous** container's proxy log (`previous: true`): a proxy segmentation-fault backtrace, while the pod's own termination reads `Completed`/exit 0.
- **A log collector restarting** — the pod is usually gone before you read the page, and so are its node's journal and pod logs, because the collector is what ships them. Read the exit first, from the last-terminated-reason and exit-code metrics the cluster exports; a collector's own container log may not reach the log system at all.
- **A pod stuck `Pending` on a node it has already been assigned to** — check that node's `Ready` before the image registry. A pod on a NotReady node stays `Pending`, and `Terminating` once deleted, until the Node object goes. A nodepool that only consolidates empty nodes will not remove a non-empty one, so the page lasts for hours. If the node's kernel journal stream shows hung tasks waiting on the network-link lock (`rtnl_dumpit`, `rtnetlink_rcv_msg`, `rtnl_lock`), the kernel lock is wedged: the kubelet is alive but cannot report status, and within hours it stops taking new pods, so a debug pod pinned to the node never starts. The hung-task detector caps at 10 reports and skips sleeping or newer tasks, so it never names the holder. Read the journal before an engineer deletes the node.
- **Mobile SDK errors forwarded from a client app** — iOS/Android client-side errors forwarded to the server after the fact, **not** server failures. A client-side error type that carries **no status** renders 400, 403, 500 and a dropped connection the same; count real statuses from the tokens that do carry one, and replay the request before calling it mis-targeted. Do NOT search access logs for correlation.

## Reproduction template (required for root-cause closeout)

When incident scope allows (especially auth/profile/reporting failures), include this exact evidence shape in the investigation doc:

1. **Customer symptom chain** (for example: `/accounts` -> upstream endpoint -> downstream status propagation).
2. **One concrete failing tuple** from logs (request params, caller, timestamp, status).
3. **Lookup call(s)** to fetch the target entity state for that tuple.
4. **Replay call(s)** with the same key/code/input to reproduce the platform error deterministically.
5. **Captured response payload** with error code, message and unique id.
6. **Source code reference** showing where that exact error payload is emitted.
7. **Backtrackable log receipt** for every log-based claim:
   - full raw line in the doc,
   - deep link into the log system for the exact query/time window.

Do not close root cause without this section unless hard-blocked by credentials/tooling; if blocked, state the blocker explicitly and keep root cause status as provisional.

## Investigation Branch Workflow

1. Create branch: `<descriptive-name>` — no tool-name prefix, no `/`
2. Write findings to `docs/investigations/`
3. Commit, push, open PR — even if investigation is incomplete

## Detailed Reference

For the package layout, the decision log and ADR templates, the mitigation ranking and the proof set, see [`docs/investigations.md`](../../../docs/investigations.md).
