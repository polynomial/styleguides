# Investigations — how to run one and write it up

**Skill:** [`oncall-investigation`](../.agents/skills/oncall-investigation/SKILL.md) runs the phases.
This doc holds the standards each phase must meet. Proof of cause: [`root-cause-proof`](../.agents/skills/root-cause-proof/SKILL.md).

<!-- toc -->
## Contents

- [Order of work: live state, then mitigation, then cause](#order-of-work-live-state-then-mitigation-then-cause)
- [Ranking mitigations](#ranking-mitigations)
- [Answering "why did it alert"](#answering-why-did-it-alert)
- [Recurring incidents need a durable fix](#recurring-incidents-need-a-durable-fix)
- [Check in-flight work before naming a cause](#check-in-flight-work-before-naming-a-cause)
- [Proof bar for a root cause](#proof-bar-for-a-root-cause)
- [A pager link is a full investigation request](#a-pager-link-is-a-full-investigation-request)
- [Break-fix: codify every live change](#break-fix-codify-every-live-change)
- [The write-up package](#the-write-up-package)
- [Decision log and ADRs](#decision-log-and-adrs)
- [Branch, PR and end state](#branch-pr-and-end-state)

<!-- /toc -->

---

## Order of work: live state, then mitigation, then cause

For any live or recent production symptom ("X is missing", "Y is failing", "Z is slow"), the order is fixed:

1. **What is broken now.** Read the live state of the failing component: pods, nodes, queues, processes, replication, target health. Write one paragraph: "X is broken because Y in the current system. Evidence: Z."
2. **What we can do about it.** Write ranked mitigation options (see [Ranking mitigations](#ranking-mitigations)). Each option names the command, the blast radius, the revert, and the check that proves it worked. The cheapest option with no risk must be on the list.
3. **Only then** chase root cause, timeline, git history, "when did it start", and five-whys.

Steps 1 and 2 must be complete and written down before step 3 starts. Step 3 findings go in the **Root cause** and **Timeline** sections, not in the summary or mitigation sections.

Forbidden before step 1 is done:

- Long log range queries to find when a metric vanished, before you confirm the producer is alive.
- Git archaeology on infrastructure repos before you check that live infrastructure matches the default branch.
- PR, chat or ticket narrative work before you inspect the live cluster.
- An executive summary that opens with a timeline ("The metric fell off on …").

Required order, measured on one investigation of missing gateway logs (28 calls in the wrong order, 1 call in the right one):

```text
1. kubectl get pods / nodes / events / target-health    (1–3 tool calls)
2. Document mitigation options A/B/C with blast radius
3. Then logs / git history / PR archaeology to harden the timeline
```

Out of scope: RCA write-ups of already-resolved incidents (timeline-first by nature, see [`rca-writing`](../.agents/skills/rca-writing/SKILL.md)), rule or skill design, capacity planning and cost questions.

## Ranking mitigations

Rank every production-affecting change by risk and lead with the lowest-risk, most surgical option. The first option in a list is the recommendation. If you have only one option, you have not done the ranking: look for a smaller one.

### Risk dimensions (low to high)

1. **Path:** observability or control plane < management plane (Helm, IaC, secrets, IAM not on the traffic path) < data plane (proxies, gateways, load balancers, schedulers).
2. **Pod identity:** sidecar or DaemonSet companion < worker pod < stateful singleton < front door, load-balancer target, or consensus member.
3. **Blast radius:** one Deployment or DaemonSet < namespace < cluster < account.
4. **Reversibility:** `kubectl patch` undo (1 s) < Helm rollback (1 min) < IaC revert and apply (5–15 min) < image rebuild < schema or data change (irreversible).
5. **Capacity required:** none < existing headroom < the autoscaler must provision < zone rebalance.
6. **Failure-mode bound:** no worse than now < transient degradation < short outage of one component < customer-visible incident.
7. **Durability:** durable < durable but brittle (manual re-apply) < temporary (same trap next cycle).

### Rules

- Lead with surgical scope. Fix the permission, not the pods: "let the log collector schedule on those N nodes", not "rebuild the gateway pods".
- Do not bundle. A one-line config change and a pod roll plus that change are two options with different risk.
- Match scope to the failure. A re-architecture is a follow-up ticket, not a mitigation option.
- State the trade-off. "A reverts faster and does not touch traffic. B is durable but needs a deploy."
- Never write "zero-risk". Write "lowest-risk available" and give the real blast radius.
- If the lowest-risk option is reversible, scoped, and within your authority, state it as the action you are taking. Ask only for higher-risk options or actions the user has gated. Do not ask permission for the safest option when the user already asked for the system to be restored.
- Offer a verification-first variant when one exists, for example a `kubectl patch` live test before the Helm or IaC change.
- Every option carries **scope, cost and feasibility**, including "no action / self-recovers" and each deferred durable fix:
  - **Scope:** what the change touches and how far its intended effect reaches. This is different from blast radius, which is what breaks if it goes wrong.
  - **Cost:** effort to build and to run, in honest units. A `kubectl patch` is minutes. A threshold change is about an hour plus a PR. A schema change is a coordinated migration. A load-balancer migration is a multi-week project. Name recurring cost for brittle fixes.
  - **Feasibility:** can we do it now, or is it blocked on another team, a deploy window, change approval, an upstream ticket, or capacity.

Forbidden: a higher-risk option first because it is the "standard" one. Asking the user to choose between a safe and an unsafe option without saying which is safer. Doing the larger "proper" change in the same step as the surgical fix. They are two changes and two PRs.

Out of scope: greenfield or local-only work, docs or test-only edits, planning with no change executed.

### Option template

```text
Recommended (least risk): <surgical change>
  Path:           <observability | management-plane | data-plane>
  Scope:          <what it touches / how far the intended effect reaches>
  Blast radius:   <single component | namespace | cluster>
  Reversibility:  <kubectl undo | helm rollback | IaC revert | irreversible>
  Cost:           <minutes | ~hour+PR | days | multi-week project; recurring cost if brittle>
  Feasibility:    <doable now by us? | blocked on <dependency / owner / approval / window / capacity>>
  Failure mode:   <bounded by current state | transient degradation | customer-visible>
  Verification:   <command/query that proves it worked>
  Why this first: <what it avoids that the higher-risk alternatives need>

Fallback (higher risk, only if recommended is blocked): <larger change>
  <same fields>
  Why this is fallback: <specific risk the recommended option avoids>
```

For "no action — self-recovers", fill it in too (scope: none, cost: monitoring only, feasibility: immediate), and fill in the deferred durable fixes, so the reader can weigh doing nothing against the durable fix with real numbers.

## Answering "why did it alert"

When asked why something alerted, whether it is broken, or how to mitigate it, the live state is a status line, never the answer. "It already resolved" is not an answer. Every such answer contains, in this order:

1. **The mechanism:** what happened, with evidence (log lines, metrics, deploy or PR correlation). Do not restate the alert text. If the mechanism is not known yet, say what is proven and what is not.
2. **Mitigation:** ranked options, even when the symptom has cleared. "Nothing to do" is valid only when the mechanism is fully explained and no durable follow-up is worth naming. That is rare.
3. **Current live state**, as context after 1 and 2.

Forbidden:

- Opening with "not broken right now", "self-resolved", or "resolved after N minutes".
- Treating a short resolution time as evidence the incident did not matter.
- Assuming a second alert in the same family is the same as the first without checking it. Check every alert the user names.

Origin: two pager alerts on 2026-08-17. The first answer led with "self-resolved" and missed a live fleet-wide stall.

## Recurring incidents need a durable fix

An incident is a recurrence when a prior investigation doc, PR, ticket or thread shows the same alert or failure fingerprint. Two occurrences make a family. The in-flight-work check and the institutional-context query usually surface it.

For a recurrence:

1. **Count and cite.** "Nth incident in this family", with links and the interrupt cost (N pages × triage time). Show why a fix not worth it at N=1 is worth it now.
2. **Lead with durable-fix work done in this session**, in this order of preference:
   - Implement the fix when it is in reach (for example a minimum-executor bump, alert re-keying, an autoscaler input change), with a PR opened now.
   - If an owning ticket exists, post a comment with the new occurrence, the frequency, and a request to raise priority.
   - If no ticket exists, create one with the family history.
   - Escalate to the owning team with the count, as a chat or ticket artifact made now.
3. "No live action needed" can appear only as a live-state status line, never as the recommendation. Self-healing, including recovery by restart, is a symptom of the missing fix.
4. If another team owns the fix, the deliverable is the escalation artifact you produce in this session. Pointing at the thread where the fix "belongs" is not a deliverable.

Forbidden: "do nothing (recommended)" or any synonym ("let it drain", "let it auto-resolve") for a recurrence. Deferring to a ticket without touching it. Prevention work listed as optional after a do-nothing recommendation.

The live-symptom ranking in [Ranking mitigations](#ranking-mitigations) still applies. The recurrence check lands in the triage output, and the fix work is the prevention-phase deliverable, executed and not only proposed. Origin: the fifth stream-processing-delay page in about three weeks.

## Check in-flight work before naming a cause

Other people change production components while you investigate. Run all of these before you write the root-cause section:

1. **Open PRs on the component's repo**, and PRs merged around the incident window:

   ```bash
   gh pr list --repo <owner>/<repo> --state open --limit 30 --json number,title,author,updatedAt,headRefName
   gh pr list --repo <owner>/<repo> --state all --search "<component or symptom> in:title,body" --limit 20
   ```

2. **Recent commits on the component path**, not the whole repo. Note who is committing. That engineer's open branches and chat messages are primary sources.

   ```bash
   git fetch origin <default> && git log origin/<default> --since="<incident window start>" --format="%h %ad %an %s" --date=iso -- <component path>
   ```

3. **A research query at the institutional-context tool** scoped to the component and the window, in addition to any URL the user gave.
4. **An unreadable referenced source is a blocker.** If a linked chat thread, ticket or doc cannot be read (bot not in channel, permission denied), ask the user to paste it or grant access before you finalize a cause. If you continue, state the gap in the doc.

If an open PR or recent commit touches the same code path as your hypothesis, read its diff and description first. State in the doc whether your conclusion confirms it, contradicts it, or is orthogonal to it. If it contradicts your hypothesis, resolve that with evidence before you design a fix. Do not ship a parallel fix built on facts another PR disproves. Origin: one investigation where an open PR in a sibling repository already held the real cause.

## Proof bar for a root cause

A root cause is not confirmed until it has all six:

1. **Runtime evidence:** logs or metrics that show the live failure signature.
2. **Concrete entity evidence:** the exact values involved (the conflicting key, code or id), hydrated to names and an admin-interface or dashboard link through the product's API. "Not decodable" is almost never true.
3. **Deterministic reproduction:** an API call or command replay that returns the same error code and message.
4. **Code mapping at current HEAD:** the `file:line` that produces the error, opened now and not recalled from a prior write-up. Confirm the code still exists and was not already fixed. If a fix landed since the last incident, explain why it recurred.
5. **Customer impact chain:** the path from the customer-facing symptom to the cause (for example `/accounts` → upstream `403` → customer `500/503`), naming real hydrated customers.
6. **Log receipts** for every log claim: the full raw log line, verbatim, and a deep link into the log system with the exact query and time range.

If one item is missing, label the cause a **hypothesis** and keep going.

- **Go past symptom layers.** "Load balancer 5xx", "timed out", "the database was slow" and "pod OOMed" are symptoms. Write the symptom-to-cause chain with evidence at each hop. Stop at the deepest layer that is both proven and actionable.
- **A prior incident is a lead, never the proof.** Re-derive "same as incident N" from this incident's evidence and current code. Prior incidents go in a separate "recurrence history / prior art" section.

Forbidden: stopping at "likely code path" without a replay. Treating correlation as proof. Claiming a cause without one concrete failing tuple, and without a failing-versus-succeeding comparison when the failure is intermittent. Leaving out the customer chain when the alert came from an upstream integration. A log claim without a link and the full line. Naming a code path from memory. Leaving raw ids unhydrated.

**Allowed exception:** if tooling or access blocks reproduction, document the blocked step, the exact command or API that failed, the permission needed, and keep the cause provisional.

## A pager link is a full investigation request

A message with a pager link (an incident or alert URL), or a raw incident id, is a standing instruction to run the whole `oncall-investigation` workflow. Do not reply with only a summary. Do not ask "want me to investigate?".

1. Read the `oncall-investigation` skill, then run its phases in order: live state, triage and severity, ranked mitigations, RCA with a unified UTC timeline and deploy and in-flight-work correlation to the [proof bar](#proof-bar-for-a-root-cause), then prevention.
2. Pull the incident through the pager's API for the firing alert, metric, rule id and value. Do not read it off the URL.
3. Follow the alert to its source: alert rule → dashboard and panel → datasource → the infrastructure-as-code file that defines the rule.
4. Write the [package](#the-write-up-package) and open the [PR](#branch-pr-and-end-state).
   - **Embed graph snapshots.** Include rendered images of the firing alert's panels and the supporting cause and symptom panels, captured when you write the RCA. Give each one a live dashboard deep link scoped to the incident window. Render them read-only and commit them under the package's `images/`. A link-only RCA is incomplete. Never fabricate a chart. If the renderer is unavailable, say so and use deep links.
5. Do not make production changes unless the user authorizes it and the change passes the immutable-infrastructure, break-fix and ranking rules. Document the mitigations and let the owning team and CI apply them.

**Fix skills that failed out of the box, in the same PR.** If a skill's documented command, tool path, metric name or resource mapping was wrong, correct its `SKILL.md` or its reference doc with what worked and the trap you hit. Prefer a copy-pasteable fix (the exact metric path, the pod or CRD naming, the quoting trap) over a vague note. Origin: one page where the system's investigation skill lacked the executor-to-driver mapping and the cause-versus-symptom metric names.

## Break-fix: codify every live change

Ad-hoc production mitigations are allowed in break-fix mode: a service update through the cloud CLI, a security-group rule, an IaC import, a `/tmp` helper, a one-line IaC patch. Leaving them only in the live system or only in chat is not allowed. Order: stabilize live first, verify the symptom is gone, then codify before close-out.

Close-out in the same session, before "done":

1. Identify the owning repo for each durable fix. A cross-repo incident gets commits in each owning repo.
2. Write the durable form: IaC, app config, a script under `scripts/`, an investigation doc, a skill or rule update. Not `/tmp`, not chat.
3. Match live to code. Encode hand-patched service, security-group or task-definition values in IaC or the deploy path, so the next apply or deploy does not revert or duplicate the fix.
4. Record state-only operations (an IaC import, manual rule ids, task-definition revisions applied by CLI) with the exact commands and resource addresses in the doc or PR body.
5. Commit and push on a branch named for the work. See [Branch, PR and end state](#branch-pr-and-end-state).
6. Open a PR to the default branch, never `--draft`.
7. Sweep: `git status` clean for intended changes, no unpushed commits on material work.

| What you changed live | Codify as |
| --- | --- |
| A service's health-check grace period, CPU or memory | The service's IaC |
| Security group ingress rule | An IaC rule resource, plus an import if already applied by hand |
| Task-definition environment variables | The service module's environment block in IaC |
| One-off CLI investigation script | `scripts/<area>/` in the owning repo |
| Incident timeline, commands, ADRs | `docs/investigations/<area>/<topic>_<date>/README.md` |
| New agent constraint from the incident | a rule or skill in the operations repo (with its `CLAUDE.md` `@` line if it is a rule) |

Forbidden: restoring production with hand-patched resources and ending with no PR. "We will codify that in a follow-up" when the user asked for the incident to be closed. The follow-up PR is the close-out. Findings only in chat when commits were made elsewhere. Reporting CI green while uncommitted IaC sits in the tree. A manual service or task-definition update with no matching IaC or deploy-script change.

If codifying is blocked (no git access, or the user asked for local-only), say so and list what is still uncodified. Break-fix does not replace approval for dangerous operations such as a storage-engine repair.

## The write-up package

The trigger is a **material finding**, not whether you changed anything. A root cause, a timeline, ranked mitigations, an ADR-worthy decision, a recommendation someone will act on, or a "recovered on its own / no action needed" verdict is material. It gets a package and a PR even if every tool you used was read-only (metrics, logs, cloud reads, API reads). If you are not sure a finding is material, it is.

The package and PR are part of the investigation, not an offer. Do not end with "want me to write this up?". This holds when you stop at the mitigation gate: the gate pauses action (deeper RCA, executing a fix), not the write-up.

One directory per investigation, under an area (`platform/`, `infrastructure/`, `messaging/`, `storage/`, …):

```text
docs/investigations/<area>/<topic>_<YYYYMMDD>/
  README.md          # primary write-up (the shareable master link)
  images/            # rendered panel images, charts
  …                  # receipts, exports, scripts, notes for this investigation
```

- Record findings as you go.
- Client- and incident-specific details go in the package. The reference docs stay abstract and reusable.
- The stable pointer is the directory on the default branch. Follow-up sessions edit or add files in the same directory. Do not start a parallel flat file or a second directory for the same incident.
- Large or regenerable raw data goes to object storage, not git, with a small receipt committed beside the write-up.

README section order:

1. **Executive summary:** what is broken now and the recommended mitigation.
2. **Live-state evidence:** `kubectl`, cloud `describe` outputs, API outputs.
3. **Mitigation:** immediate, durable, and out-of-scope follow-ups, each with scope, cost and feasibility.
4. **Root cause / timeline / git history.**
5. **Decision log and ADRs** (see below).

A doc that is heavy on timeline and light on mitigation has the order inverted and must be revised before merge.

**Exempt from the package and PR:** a trivial lookup with no durable finding (a metric's current value, whether a pod runs, a dashboard URL). Exploration the user framed as throwaway. Work the user asked to keep local-only, which you still state back to them.

## Decision log and ADRs

Every investigation doc (and every RCA under `docs/rcas/`, and every design doc that records decisions) contains both of these, in the doc itself and not only in the PR description.

### Decision log

- Heading: `## Decision log` or `## Process retrospective and chat-driven revisions`.
- One numbered subsection per user prompt that shaped the work. Skip "ok" and "sounds good".
- Quote the prompt verbatim, in italics or a blockquote. Keep typos. Never paraphrase and attribute it to the user.
- Follow each with a paragraph naming what it drove: a doc section, a commit, an ADR, a rule, a production action, a follow-up PR. Cross-link.
- Oldest first.
- Never remove a prompt that drove a correction. The log records mistakes as well as progress.

### ADRs

Record an ADR for any point where one path was chosen over another: the mitigation chosen, scope (fixed now versus deferred, what is deliberately not touched), tool or approach, what we chose not to do, severity and routing (what pages, what only tickets), rule or skill changes. Do not record an ADR for a fact, a tool output, or a routine implementation detail. The test: would a later reader of only this doc ask "why this way and not that way"?

ADRs are inline, next to the section they decide, numbered per document. A decision that binds several investigations gets its own file at `docs/decisions/<NNNN>-<slug>.md`, referenced from each. Link to an ADR as `docs/investigations/<area>/<topic>_<YYYYMMDD>/README.md#adr-002`.

```markdown
### ADR-NNN: <short imperative title>

- **Status:** Proposed | Accepted | Superseded by ADR-MMM | Deferred
- **Date:** YYYY-MM-DD
- **Deciders:** <people / roles>
- **Context:** <one paragraph: the situation and what is at stake>
- **Options considered:**
  - **Option A — <name>:** <one sentence + risk profile>
  - **Option B — <name>:** <one sentence + risk profile>
  - **Option C — <name>:** <one sentence + risk profile>
- **Decision:** <the chosen option, and one sentence on why over the others>
- **Consequences:** <what changes, good and bad; what gets easier or harder; follow-ups now required>
```

Forbidden: decisions buried in prose. An ADR with no "Options considered". A status of "Recommended" (the statuses are Proposed, Accepted, Superseded, Deferred).

Related locations: designs (proposed decisions) at `docs/designs/<topic>_<YYYYMMDD>.md`, runbooks an ADR requires at `docs/runbooks/<topic>.md`.

## Branch, PR and end state

1. Start from the current default branch:

   ```bash
   git fetch origin && git checkout <default> && git pull
   git checkout -b <descriptive-name>
   ```

   For work that also touches another repo, use the repository's workspace or worktree helper so every participating repo is on the same branch.
2. Name the branch for the work: `config-lint-corpus`, `broker-lag-rca-20260904`. No tool-name prefix (`cursor/`, `claude/`) and no `/`.
3. Commit and push (`git push -u origin HEAD` on the first push).
4. Open a PR to the default branch with `gh pr create`. Title it for the investigation. Link the package directory or its `README.md` and the incident references. Never `--draft`, even for incomplete work. A small doc tweak and a full RCA get the same treatment.
5. The PR ends **OPEN, non-draft, for a human to merge**. Get the checks green and read the automated reviewer first. Do not merge it yourself unless the user tells you to in this session.
6. Verify before you report done:

   ```bash
   gh pr view <n> --json state,isDraft   # OPEN, false
   ```

   Then report the link and say it needs a human to merge.

Forbidden: declaring an investigation finished with commits and no PR, or with a PR you merged yourself. Ending a session with unpushed commits on material findings, unless the user asked for local-only. Answering a production "why is X broken" question in chat only when the answer is a real RCA. Citing "read-only research" as the reason to skip the doc.
