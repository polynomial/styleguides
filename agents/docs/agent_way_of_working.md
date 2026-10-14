# A way of working for AI agents doing engineering and operations

**Status:** Distillation (October 2026). Company-agnostic. Share freely.

This document distills how one engineering organization runs AI coding agents across production
investigation, debugging, code change, and documentation work. The rules below were not designed up
front. Each one was written after an agent did something wrong in a specific, measured way, and each
one has stayed because the failure stopped recurring. The product names, hostnames, ticket keys, and
incident numbers are removed here. The shape of the discipline is what transfers.

It is a companion to [Cross-tool AI agent guidance](cross_tool_ai_guidance.md), which covers where
guidance files live and how tools load them. This document covers what the guidance says.

How to read it: each section is a gate an agent passes before a kind of action. The "Forbidden" lists
are the most useful part. They name the specific evasions agents reach for, in the words the agents
used, and an agent reads a named evasion as a line it cannot cross far better than it reads a
principle.

<!-- toc -->
## Contents

- [1. The shape of the system](#1-the-shape-of-the-system)
- [2. Explore before you converge](#2-explore-before-you-converge)
- [3. Research before you rediscover](#3-research-before-you-rediscover)
- [4. Find the existing pattern](#4-find-the-existing-pattern)
- [5. Evidence before you change code](#5-evidence-before-you-change-code)
- [6. Plans contain decisions, not research](#6-plans-contain-decisions-not-research)
- [7. The investigation contract](#7-the-investigation-contract)
- [8. The proof bar for a root cause](#8-the-proof-bar-for-a-root-cause)
- [9. Evidence integrity](#9-evidence-integrity)
- [10. Production safety](#10-production-safety)
- [11. Finish the work](#11-finish-the-work)
- [12. Verify before you say done](#12-verify-before-you-say-done)
- [13. Prevention is a backtested detector](#13-prevention-is-a-backtested-detector)
- [14. Assessments are scored on receipts](#14-assessments-are-scored-on-receipts)
- [15. Writing for the people who were not in the session](#15-writing-for-the-people-who-were-not-in-the-session)
- [16. Pull requests and git, for an agent](#16-pull-requests-and-git-for-an-agent)
- [17. The learning loop](#17-the-learning-loop)
- [18. Adopting this](#18-adopting-this)
- [Sources](#sources)

<!-- /toc -->

## 1. The shape of the system

### Three kinds of guidance

- **Rules** are always-on gates. Short, loaded into every session, scoped to a moment ("before you
  write a fix", "before you say done"). They are the guarantee.
- **Skills** are procedures with a trigger. Loaded on demand when the task matches the trigger in the
  skill's description. They are the content.
- **References** are deep knowledge a skill points at. Never loaded by default.

A tool decides whether to load a skill. That decision is model-discretionary, so a skill marked
"must use" is a request, not a guarantee. **A rule is a gate plus a pointer to its skill, never a
copy of it.** The rule guarantees the skill gets read. The skill stays the single source of the
procedure. When the two are allowed to drift apart, the rule becomes a second, shorter, wrong copy.

### Every rule carries its origin

A rule that reads as arbitrary gets argued with. A rule that names the incident, the date, and the
measurement gets followed. Write "measured against the live system on this date, fifteen shapes, not
recalled from documentation", and then list what was measured. Write "an agent session wrote eight
such loops with the rule loaded the whole time, one of them polling every two minutes for four hours".
The origin is the argument.

### Every rule has a Forbidden list

The failure modes are not general. They are specific sentences an agent writes to get past the gate:
"should work", "pre-existing on master", "that needs the sponsor's sign-off", "worth a check", "let it
drain". Name them. A Forbidden list is a list of quotations from past sessions. Add to it when a new
evasion appears, and keep the old ones, because they come back.

### One home per practice

Working practices live in one place and every repository points at it. Each repository owns only
its own domain, mechanics, and conventions. A repository-local version of a shared practice is a
delta: it names the canonical, then adds what differs. Where the two disagree, the local one wins for
work done in that repository.

Before an agent acts on a repository's behalf, by editing a file, by commenting on its pull request,
by opening a ticket for it, or by posting about it, the agent reads that repository's own agent
guidance first. Writing *about* a repository is governed by its rules as much as editing it.

### Budget the always-on text

Every always-on rule is paid for in every session. Tools truncate silently past a size cap, and a
truncated rule set fails by quietly dropping the last rule. Keep rules short, keep the count small,
and move anything that is not a gate into a skill or a reference.

## 2. Explore before you converge

Reaching for convergence rules on a problem nobody has explored yet is how a team builds a careful,
expensive answer to the wrong question. For a non-trivial analysis, design, investigation, or review:

**Explore the problem.**

1. **Reason from the system, not the artifact.** Start from how the thing works: what the data is,
   who writes it, who reads it, how often, where the code runs. Then locate the problem inside that.
   Do not structure the analysis around the snippet you were handed.
2. **Start from observed behavior and the outcome somebody wants.** Go and look. Reproduce it, read the
   data, watch the traffic. The requested change is one person's hypothesis about how to get from the
   first to the second. It is evidence about the outcome, not a specification of it.
3. **Try more than one framing.** Write down the problem you were shown and one that moves the
   boundary, wider or narrower. A precise solution to the wrong-sized problem is still wrong. Say what
   is out of scope once you have chosen.
4. **Challenge the requirements that create the complexity.** A constraint you were handed is an
   input, not a law. When one forces a new dependency, a second copy of data, or a standing
   operational burden, price it out loud and ask the owner before building the machinery.
5. **Generate alternatives, then choose.** Put two or three real candidates on the table, including
   the boring one and the one that does nothing. One option with supporting reasons is advocacy.
6. **Learn by cheap experiment.** Replace "this is faster" with a measurement. If you cannot prove it
   yet, label it a hypothesis and name the experiment that would kill it.

**Converge on the design.**

7. **Make it work and prove it useful before making it fast.** Optimization is earned by a
   measurement on a running system.
8. **Simplicity is the default. Complexity is what needs the argument.** Count the whole cost of what
   you propose to keep: maintenance, deployment, observability, failure modes, the eventual migration
   away.
9. **Say where the design stops working.** "It fails above ten million rows, which is a hundred times
   today's volume" is a finished answer.
10. **Prefer reversible decisions. Escalate the irreversible.** A published name, a schema, an API
    shape, a data migration, and a new service are one-way doors. Raise those before the code exists.
11. **Record what you rejected, not only what you chose.** The reasons an option lost are the
    expensive part of the thinking and the part that gets lost. Put them in the pull request or the
    ticket, not in a code comment.

## 3. Research before you rediscover

Code search answers *what*. Only the organization's history answers *why*, *who*, and *when*: the
pull request that rejected the approach you are about to propose, the thread that argued for the
convention you are about to break, the incident with the same fingerprint.

- **Fire the history search at the start, in parallel with the first concrete step.** It costs no
  latency against your own first action and often returns the answer key. Do not wait until stuck,
  and do not wait to be asked.
- **Triggers:** the start of any planning, investigation, refactor, or feature task. "Why is it done
  this way." Behavior that does not match the code. An unfamiliar flag, class, or error string.
  Before writing new code. An incident. Before recommending a solution.
- **Leads, never verdicts.** History surfaces stale, superseded, and wrong context. Use it to know
  where to look, then prove every claim against current code or live evidence. If code confirms it,
  cite the code. If code contradicts it, the code wins.
- **An unreadable primary source is a blocker, not a footnote.** When a thread, ticket, or document
  is named and you cannot read it, say so and ask for it before finalizing. Never conclude past an
  unread source.
- **Record when the search was unavailable.** "Context not checked, tool unavailable" is honest.
  Writing that research was done when it was not is fabrication.

## 4. Find the existing pattern

Consistency is the asset. A codebase where every kind of thing is done one way can be navigated,
reviewed, and safely changed by anyone, human or agent. Every lone deviant costs every future reader
a detour.

1. **Find two or three existing instances** of the kind of thing you are about to add. The dominant
   shape is the pattern.
2. **Check whether the pattern is codified** in a conventions skill or reference before reverse
   engineering it.
3. **When the pattern surprises you, get its why** from history. A pattern that looks wrong usually
   encodes a constraint you have not hit yet.
4. **Conform**, even where you would do it differently. Your change should look like the codebase
   wrote it.

**Never merge a lone deviant**, regardless of who suggested it, including review bots. Either
conform, or make changing the pattern the explicit subject of the work: change it at its source, with
the owner aware, and migrate the existing instances or record who will.

**Prove absence before inventing.** "There is no existing pattern" is a claim. Naive searches lie:
ignored directories, stale checkouts, a search tool that silently skips what it is configured to
skip. Verify the search returned anything at all before concluding something is absent, and search
the hosted source for an organization-wide claim.

## 5. Evidence before you change code

**A bug report is evidence code broke. It is never evidence the code should exist.** A report can be
accurate about a symptom and still ask you to reverse a deliberate decision, and the dangerous
report is the one that never mentions the removal. Restoring the thing looks responsive. Closing the
report looks rigorous. Both are unilateral calls on a contradiction only the removal's author can
settle.

Before adding, restoring, re-enabling, or fixing forward anything a report implies should exist:

0. **Fetch first and name the refs you search.** Stale refs answer every history question wrongly and
   the gate passes green on absent evidence. Search both the default branch and your own branch.
1. **Search history for the thing itself**, not just the symptom: the commit message search and the
   pickaxe search for the exact symbol.
2. **If a commit removed it, read the pull request and the ticket it names.** Then ask one question,
   *does the report acknowledge the removal?*, with exactly three answers:
   - It acknowledges the removal and still asks. Follow the report. History is context, not a veto.
   - It never mentions the removal. **Stop and ask the author of the removal, by name**, linking the
     commit, the pull request, and the ticket. Do not restore. Do not refuse. A generic "someone
     should confirm" is not asking.
   - Nothing removed it. Continue. This is an ordinary fix.
3. **Check what else is in flight on the same component**: open pull requests, recent commits on the
   path, the engineer whose name keeps coming up. Their open branches are primary sources.
4. **State how your change relates** to anything you found: confirms, contradicts, orthogonal, or
   finishes it. Do not ship a fix premised on facts another engineer's branch already disproves.

**The same gate applies to a line you are removing or routing around.** Some lines exist because
something broke, and a diff that removes one looks identical to a diff that adds a feature. Before
deleting, inlining, "simplifying," or adding a new path around an existing guard in routing,
retries, rate cutoffs, idempotency, ownership, credentials, or timeouts:

1. Find the commit that decided the current shape with a pickaxe search on the exact line.
2. Research why, not what.
3. Write the verdict before editing: **PRESERVES**, **NARROWS** (name what is no longer covered and why
   that is safe), or **REVERSES** (name the protection lost and get explicit sign-off).
4. Carry the evidence into the pull request as a "Prior decisions" section. "None found" is a valid
   entry. An absent section is not.

**The wire before the code.** A report that names a mechanism, a cookie, a header, a redirect, a
missing row, is a claim about what a live host sends. Replay the reporter's own request and read what
comes back. The code only says what it should send.

### Forbidden

- Treating "there's an error" as proof the erroring thing should be added back.
- Citing a prior incident or a fix you remember as the current state of the code. Re-derive at the
  file at current HEAD, every time.
- Recording the conflicting commit as a hedged aside ("worth a check", "possibly related") and then
  proceeding anyway. Finding it and not acting on it is the failure.
- Surfacing the contradiction to no one in particular.

## 6. Plans contain decisions, not research

Do not write the plan until every unknown that can be resolved with read-only tools has been
resolved. Resolvable means: repository search, history, reading source and API docs, read-only
queries against live systems, and replaying a single failing request.

1. List the decisions the plan would otherwise defer: names, which file, scope counts, API semantics,
   merge blockers.
2. Resolve each with evidence. Cite the file, the search result, the commit, or the tool output.
3. Ask the user now about choices that are only theirs, not inside the plan. Headless, pick the
   default and record it.
4. Scan the draft for the forbidden phrases below. If any remain, keep researching.

**Forbidden inside a plan:** "investigate", "research", "figure out", "look at", "decide after
test", "compare X and Y then choose", "needs context", "TBD", "pending research", and any todo named
`investigate-*`, `decide-*`, or `test-*` when the answer is obtainable now.

Plan todos are implementation and verification only. Each deliverable names its exact files, its
quality gates, its merge path, and its post-merge check.

## 7. The investigation contract

A production symptom, an alert, an incident link, or a "why is X broken" question is the request to
run the whole investigation. Do not reply with only a summary, and do not ask whether to
investigate.

### The order is fixed

1. **Live state first.** Inspect the failing component now: processes, queues, replication, target
   health. Write one paragraph: "X is broken because Y in the current system. Evidence: Z."
2. **Ranked mitigations next.** Lowest blast radius first. Each option names its command, its
   blast radius, its revert, and the check that proves it worked.
3. **Root cause last.** Timeline, history, "when did it start", five whys.

Steps 1 and 2 are written down before step 3 starts. Measured on one investigation: twenty-eight
tool calls in the wrong order, one in the right one. A write-up that is heavy on timeline and light
on mitigation has the order inverted and is revised before merge.

**Forbidden before step 1 is done:** long log-range queries to find when a metric vanished, before
confirming the producer is alive. History archaeology before checking live infrastructure matches
the main branch. An executive summary that opens with a timeline.

### Ranking mitigations

The first option in the list is the recommendation. If you have only one option, you have not done
the ranking. Rank on these dimensions, low to high:

| Dimension | Low | High |
| --- | --- | --- |
| Path | observability or control plane | data plane |
| Component identity | sidecar, worker pod | front door, consensus member |
| Blast radius | one deployment | account |
| Reversibility | one-second undo | irreversible data change |
| Capacity required | none | must provision |
| Failure-mode bound | no worse than now | customer-visible incident |
| Durability | durable | temporary, same trap next cycle |

Rules: lead with surgical scope. Do not bundle a config change with a restart. They are two options.
A re-architecture is a follow-up ticket, not a mitigation. Never write "zero-risk". Every option,
including "no action" and each deferred durable fix, states **scope**, **cost** in honest units, and
**feasibility** (now, or blocked on whom), so the reader can weigh doing nothing against investing
with real numbers. If the lowest-risk option is reversible, scoped, and within your authority, state
it as the action you are taking.

```text
Recommended (least risk): <surgical change>
  Path / Scope / Blast radius / Reversibility / Cost / Feasibility / Failure mode
  Verification:   <command or query that proves it worked>
  Why this first: <what it avoids that the alternatives need>

Fallback (higher risk, only if recommended is blocked): <larger change>
  <same fields>
```

### "It self-resolved" is a status line, never the answer

Every answer to "why did it alert" contains, in this order: the mechanism with evidence, the ranked
mitigations even when the symptom has cleared, then the current live state as context. A short
resolution time is not evidence the incident did not matter. A second alert in the same family is
checked on its own, not assumed to be the first.

### A recurrence forbids "do nothing"

Two occurrences make a family. For a recurrence, count and cite the occurrences with their interrupt
cost, then lead with durable-fix work done this session: the fix with a pull request opened now, or
a comment on the owning ticket with the new count and a priority request, or a new ticket with the
family history, or an escalation artifact made now. "Let it drain", "let it auto-resolve", and
"do nothing (recommended)" are forbidden for a recurrence. Self-healing is a symptom of the missing
fix. Pointing at the thread where the fix "belongs" is not a deliverable.

### Check in-flight work before naming a cause

Other people change production components while you investigate. Before writing the root-cause
section: open pull requests on the component, pull requests merged around the window, recent commits
on the component's path, and the history search. If one touches the same code path as your
hypothesis, read its diff first and state whether your conclusion confirms it, contradicts it, or is
orthogonal.

### Break-fix: codify every live change

Ad-hoc production mitigations are allowed in break-fix mode. Leaving them only in the live system or
only in chat is not. Stabilize live, verify the symptom is gone, then before close-out: identify the
owning repository for each durable fix, write the durable form (infrastructure code, app config, a
committed script, a runbook), match live to code so the next deploy does not revert the fix, record
state-only operations with their exact commands, and open the pull request. "We will codify that in a
follow-up" when the user asked for the incident to be closed is forbidden. The follow-up is the
close-out.

### The write-up package

The trigger is a **material finding**, not whether you changed anything. A root cause, a timeline,
ranked mitigations, a decision, a recommendation, or a "recovered on its own" verdict is material. It
gets a package and a pull request even if every tool you used was read-only. If you are not sure a
finding is material, it is. The package is part of the investigation, not an offer. Do not end with
"want me to write this up?".

One directory per investigation, under an area, dated, with a `README.md` as the shareable link and
an `images/` directory beside it. Section order mirrors the workflow: executive summary (what is
broken and the recommended mitigation), live-state evidence, mitigation, then root cause and
timeline, then the decision log and the decision records.

Every log claim carries the full raw line, verbatim, and a deep link that re-runs the exact query
over the exact window. Every chart in a root-cause write-up is a rendered snapshot committed beside
the document, paired with a live link, because an auth-gated dashboard URL drifts and is not what the
reviewer six months out will see. Never draw a plausible-looking chart. If the renderer is down, say
so.

### Decision log and decision records

Every investigation document, every post-mortem, and every design that records decisions carries
both, in the document itself and not only in the pull request.

- **The decision log** is one numbered subsection per user prompt that shaped the work, quoted
  verbatim with typos kept, followed by a paragraph naming what it drove. Never remove a prompt that
  drove a correction. The log records mistakes as well as progress.
- **A decision record** exists for any point where one path was chosen over another: the mitigation,
  the scope, what was deliberately not touched, the severity routing. The test is whether a later
  reader of only this document would ask "why this way and not that way". Each record holds status,
  date, deciders, context, options considered with their risk profiles, the decision, and the
  consequences. A record with no options considered is forbidden. Statuses are Proposed, Accepted,
  Superseded, and Deferred. "Recommended" is not a status.

## 8. The proof bar for a root cause

The cheap, wrong move is "this looks like the last incident, so it is the same bug". It passes every
casual smell test and is still wrong.

### The five failures this gate forbids

1. **Analogy as root cause.** A prior incident is a lead, never a conclusion. Re-derive from this
   incident's evidence and current code.
2. **Symptom as root cause.** "The load balancer returned 5xx", "the service timed out", "the pod ran
   out of memory" are layers. Stopping there produces a recommendation nobody can act on.
3. **Stale reference as root cause.** Naming a code path from memory or an old write-up without
   opening current source. The fix may already be deployed. The method may not exist.
4. **Hypothesis as root cause when the system was observable.** A chain of plausible mechanisms,
   each replaced by the next, is guessing with extra steps. If it reproduces, instrument it.
5. **Empty diff as proof.** "Pre-existing on master" because the diff on the implicated path is
   empty. An empty diff proves the code did not change. It says nothing about behavior when the
   branch changes anything the code runs on: a framework version, a base image, a shared dependency,
   a config default.

### The gates

- **Build the why-chain** from what paged down to the deepest cause that is both proven and
  actionable by someone. Each hop carries evidence or is labelled a hypothesis. If your root cause
  restates the symptom in different words, you have not found it.
- **Re-derive against current source.** Open the file at HEAD and cite the line. Check the thing you
  are blaming still exists and was not already fixed. If a fix landed after the last incident, your
  job is to explain why it recurred despite the fix. Date a configuration read to the window you are
  explaining. What you read now explains a past failure only once you know it was live then.
- **Hydrate every entity.** A raw identifier is not usable and not proof. Resolve it to a name and a
  link. "Not decodable" is almost never true.
- **If it reproduces, observe it. Stop theorising.** Two disproven hypotheses about the same
  reproducible failure and you stop reasoning and instrument. Put probes at the decision points that
  distinguish your hypotheses, log what each step decided and the value on each side, redeploy only
  the component that serves the failing request, run the single reproducing test, and parse the
  output rather than text-matching it. A probe is production logging: no secrets, no personal data,
  no raw payloads. Budget ten minutes a cycle. Two cycles beat an afternoon of theory. Unit tests
  passing while the real path fails is the signal to inspect composition, not logic.
- **Reproduce the reporter's case, not a symptom you can make.** Replay with their subject and their
  entry path, taken from their own message or URL. A replay that passes on a subject you chose is not
  a failed reproduction. Calibrate the probe so two runs differ only in what you are testing. A
  retest that passes is one draw, not a retraction: answer with a failure rate over repeated runs
  and a clean control, and size the run from the smallest residual rate you would still act on.
- **Check the instrument before a number leaves your hands.** A negative claim ("only ever",
  "nobody did", "never fires") is settled per record, never from a list or an index that can omit
  rows. A positive control proves the instrument sees things of that kind, never things of that age.
  A proxy earns a proportion only after it agrees with a case you can see by eye.

### The output contract

Do not label a cause **confirmed** unless all of these hold. Otherwise label it **hypothesis** and say
what is missing.

- [ ] Why-chain written, every hop evidenced, deepest layer actionable.
- [ ] Current-source citations at HEAD, and the blamed code checked to still exist.
- [ ] The runtime signature (log fields, metric shape) is explained by that code.
- [ ] Entities hydrated. The impact chain names real customers.
- [ ] A deterministic reproduction on the reporter's own subject, or the named blocker.
- [ ] Every count, negative, and proportion re-derived per record.
- [ ] Full raw log line plus deep link for every log claim.
- [ ] The cause is stated from this incident's evidence. Prior incidents appear only under
      "recurrence history", separated from the proven cause.

When you are blocked, say so precisely and keep the cause labelled a hypothesis. "The per-request cost
points to a wide-row scan, code-proven, but I could not replay against the live row, so single-tenant
attribution for the window is a hypothesis pending the access-log pull" is an honest, useful state.
"Same as last time" is not.

## 9. Evidence integrity

Every number, record, and negative claim is produced by a real, clean, re-runnable observation.
Never carried forward, reconstructed, or fabricated.

- **Numbers are computed, never carried forward.** A figure in a document, a pull request, or a
  message comes from a committed, re-runnable script or command whose verbatim output you quote. Pin
  its window. Annotate every epoch with its UTC time. When an upstream figure is fixed, re-derive
  every downstream one. On one audit, five of five carried-forward numbers were wrong.
- **Never hand-type an epoch.** Compute it, and check the year.
- **Raw data is saved verbatim at acquisition.** Never reconstruct, template-diff, or summarize a raw
  record. Re-fetch it or mark it unverified. Large payloads go to object storage, not git.
- **A negative claim names its observation point.** Before "X never happens", prove the emitter's
  guards cover the traffic, then confirm with a raw-string count at the rawest layer.
- **Output from a failed command is untrusted.** Fix the command, get exit zero, then read it.
- **Never fabricate work.** Every claimed run, iteration, or result maps to a real tool call in this
  session. If you did not run it, say so.

### Measuring an agent

A number produced by driving an agent (tool-call counts, an eval result, an A/B arm) has its own
traps. The failure mode is not a wrong answer. It is a plausible one that looks like data.

1. **Name the subject in every programmatic prompt.** An agent that has to ask which account is
   meant reaches no tool and returns a well-formed response a harness records as success. A
   zero-tool-call answer is a harness defect, not a cheap answer. Do not average a run where most
   questions reached no tool.
2. **A green check is not evidence the evals passed** when the shards are non-blocking. Read the
   shard log.
3. **Gate on a deterministic assertion, not a borderline judge.** A judge scoring near its threshold
   is a coin toss. Keep the judge for the qualitative axis.
4. **Compare arms only on equal denominators.** Report the answered count per arm. Never divide by
   the asked count to make the columns line up.
5. **A rehearsal must not be able to overwrite a real result.** Dry-run output goes to its own path.
6. **A blind test never loads its answer key first.** The initial question and its attachments are
   allowed inputs. The expert's answer is read only to grade. Research grounded in the stack trace
   is allowed. Research framed on the specific incident so that the write-up comes back as the answer
   is not.

### Prove it on a second input

A script that has only ever run against one dataset is untested, however carefully it was written.
Before its numbers are published, run it unchanged against a second dataset of the same kind and read
every line of the output. Name the second input before you start, and make it a parameter, not an
edit. If running on the second dataset means changing a constant in the file, that is the first
defect found. A figure identical across two different datasets is a prompt to look, not a verdict.
Fix what it finds in the code, re-run both, and name every changed figure as a correction.

Origin: four analysis scripts reviewed against one vertical, every number published. The second
vertical found six defects in an afternoon, including a filter hardcoded to the first vertical inside
the SQL, a cohort that did not exist in the second vertical, and the first vertical's numbers
printed as literal prose under the second's table. The second run also changed a published
conclusion: a finding about the platform was a finding about one vertical.

## 10. Production safety

- **Infrastructure is code, reviewed, and deployed by CI.** An agent does not run infrastructure
  commands imperatively against a live environment. It makes the code change, pushes, and lets CI
  take it from there. Dispatching CI *is* "letting CI take it".
- **Infrastructure on a shared state: read the full plan first.** Apply only your own resources from
  a saved, scoped plan proven additive-only (N add, zero change, zero destroy). Never apply drift you
  did not author. Prefer a dedicated resource over mutating a drifted shared one. Scoped teardown
  mirrors the scoped apply.
- **Never destroy by target.** It destroys every dependent. Five targets once planned seventeen
  destroys. Delete precisely with the cloud CLI, then apply by target to recreate.
- **Prove recovery before destroying.** Replace the component with its data intact, confirm it
  serves on its port with its health command, and only then discard data. "Running" is not proof. A
  plan is not proof a rebuild boots. "It booted last month" is no evidence for an image selected by
  "most recent".
- **Stream state-changing commands in full.** Never pipe a plan, an apply, a deploy, a migration, or
  a build through `tail`, `head`, `grep`, or a pager. `tee` to a file if needed.
- **Explicit approval before the dangerous class** of storage-engine repair, restarts of stateful
  singletons, and metadata edits.
- **A replay into a production queue is a production data mutation.** Sort, de-duplicate, scope, and
  test first. Validate downstream. Open the customer-facing ticket naming the affected users.
- **Secrets:** identify a credential by a hash prefix, its length, and its first few characters.
  Prove it works by status codes. Never print one. Enumerate every consumer of a shared secret before
  changing it. A leak found along the way is reported by file and commit with a live/not-live test,
  and the value is never pasted.
- **A config fix is verified at the point of harm, not at the setting.** A queue between the setting
  and the harm means a correct fix can leave the incident at full severity for hours. Read the
  setting back, count the harmful work per interval, look for a tail-off, and if there is none,
  measure the lag in event time and state the recovery gate as "when the watermark passes the fix
  time".
- **The stated scope belongs in the default.** When the user has said "global", the cautious option is
  the one behind a flag, not the reverse. Ranking by blast radius is for presenting choices. Once the
  scope is stated, that ranking must not quietly become the deliverable's default.

## 11. Finish the work

- **Run it. Do not hand it over.** If you have the access, run the command yourself: reads and writes
  alike, including dispatching CI, deploying through the sanctioned pipeline, and re-running a job.
  Capture a baseline, know the revert, watch it land, verify the live effect. Stop only for
  irreversibility, authority you lack, or a step the user reserved, and then name the single blocking
  step.
- **A safe action is never "unavailable" until you have exhausted the paths.** A tool pinned to the
  wrong account means list the profiles and use the right one. A schema or validation error is your
  malformed call: re-read the tool's schema before calling the tool broken. One auth error across
  unrelated tools means an inherited environment variable, so check that first.
- **Read the matching skill before improvising a tool path.**
- **A failure is not done.** After a failure, diagnose it and try a different approach. Never mark a
  todo complete on a failed or partial attempt. If truly blocked, state what you tried, each error,
  and what would unblock it.
- **Execute necessary follow-ons. Do not just name them.** When your own work surfaces something the
  task genuinely needs (test coverage for the behavior you changed, a document your change made
  stale, a cleanup your change orphaned), do it in the same session or ticket it. "Say the word and
  I'll add it" wastes a round trip on work that was never optional.
- **A non-selection is not consent.** When the user answers your options with a question, research
  it and re-present the options. Never proceed with an unchosen option or rebrand it as "hybrid" or
  "interim".
- **Do the literal ask.** When something blocks an explicit instruction (a stale branch, a guardrail,
  a missing file), stop and say what is in the way, then ask. Never quietly route around the user's
  intent with an alternative you decided was safer.
- **On corrective feedback, rebuild the artifact.** Restate "done" in the user's words, then
  regenerate it clean. No banners, no correction blocks, no retained superseded analysis. A correction
  that makes the artifact longer is a red flag.
- **A consolidation deletes what it subsumes, in the same pull request**, with a deletion ledger and
  a re-runnable proof that nothing references what was removed.
- **Declarations hold decisions. Emitted records hold runtime facts.** Before adding a manifest, a
  registry, or a config surface, prove no existing artifact carries it and name what reads it. A
  hand-maintained copy of a runtime fact will drift, and a drifted declaration is evidence of a
  control that is not operating. A pull request whose open questions are the design decisions the
  change embodies has passed its own design to the reviewer.

## 12. Verify before you say done

Do not mark a todo complete, tell the user a task is done, or post a final answer until the original
request has been re-read and every requirement verified against actual output.

When the brief is to make something **work**, the deliverable is the working result. A precise
account of why it still fails is a status update. A tool returning 200 or an agent saying "done" is a
claim. Read the end state back through a second path before you report it.

1. **Re-read the original brief**, the first prompt, any attached plan or ticket, and every
   mid-task scope change. Quote it. Do not rely on memory.
2. **Enumerate requirements**, explicit and implicit, as a checklist.
3. **Verify each against actual output**, citing one line of evidence per item: a path, an exit code,
   a URL, a tool output snippet. Verify what was produced, not what was intended.
4. **List gaps.** Any item without evidence is a gap. Partial counts as a gap. Sort each into
   **blocking** (evidence is obtainable now) or **deferred** (the evidence cannot exist yet). Deferred
   is for evidence that is impossible now, never for work you did not do. If you could go get it, it
   is blocking.
5. **Fix every blocking gap before proceeding.** Each deferred item names its owner, its trigger, the
   exact evidence that will settle it, and where it is recorded.
6. **Self-evaluate, unprompted**, in two or three sentences closing the message: what the request
   turned out to be against what it first looked like, the earliest point the evidence to know that
   was already available, and the one habit that would have caught it sooner. If the lesson
   generalizes, name where it should land, and land it as its own change, never folded into the task's
   pull request.
7. **Only then complete**, with the checklist showing every item verified or explicitly deferred.

### Forbidden

- Completing on intent: "should work", "the code looks right".
- Marking the last todo done with commits sitting unpushed. Work nobody else can see is not
  delivered.
- Reclassifying a blocking gap as deferred to get to "done".
- **Inventing an authority gate to excuse work you could have done.** "That needs the sponsor's
  sign-off", "that is a product decision", where no such gate was stated by the user, a rule, or the
  brief. Capability and permission are the two reasons part of a brief can be left undone, and both
  are facts about the world you can point at. A gate you reasoned your way to is a preference wearing
  a constraint's clothes. If a part genuinely needs someone's decision, the deliverable is to ask
  them, now.
- **Reporting a multi-part brief as complete with a named part undone.** N of M is not done. It is N
  of M, and the headline says so. A visible, unexplained hole in the headline reads as evidence that
  nothing else was checked either. In the originating case that suspicion was right: running the
  fifth step found six defects in the four that had been called done.
- Staging a tree while a background job is writing into it. A verbatim output truncated mid-write
  looks exactly like a short one.
- Reporting a documented failure as done when the brief was to make the thing work.

## 13. Prevention is a backtested detector

Every post-mortem answers "would monitoring have caught this?" with evidence, not intent. "We had no
monitoring for this" is not a conclusion, and neither is "add monitoring" without the signal, the
data source, and the noise cost.

1. **Classify the incident shape first.** Almost every detector fires on a transition out of a
   healthy state, so "worked, then broke" is usually detectable today and the question is why the
   alert was missed or dismissed. "Never worked since launch" is structurally invisible to those
   detectors and needs a ratio against an independent expectation.
2. **Inventory what exists. Do not guess.** Check every layer independently: is the data produced, is
   the alert logic enabled, is the capability scheduled anywhere.
3. **Confirm the negative at the alert channel, not the config.** Read where alerts land and their
   disposition. A family that fires and is always closed "won't do" is not monitoring. The dismissal
   rate is usually the real finding.
4. **Name a concrete detector** and classify the work as turn on, tune, augment, or build.
5. **Backtest it over the real incident window.** Report, always together: first alert date and lead
   time against actual discovery (the benefit), alerts per week across the window (the cost), and
   which live detectors stayed silent (proves the gap instead of asserting it). Scope the replay to
   the incident. A detector firing ten months earlier is a different claim.
6. **Judge it. Noise is the gate, and the judgement is a discussion point.** A detector being correct
   is not sufficient reason to enable it. Noise is per-subject, so derive thresholds from each
   subject's own baseline. A chronic condition needs a digest, not an alert. Lead time alone rewards
   bugs, so read it with volume beside it. Record an explicit enable, observe-mode, or do-not-enable
   verdict with the numbers.
7. **Cause-side and harm-side detectors do not substitute for each other.** A config audit is blind
   to harm with no config drift. A state monitor is blind to drift that has not yet caused harm.
   Propose both and say why.

Every recommendation carries its class, an existing data source, the alert primitive, a
false-positive analysis, its backtest numbers, and an owner. Put the table in the post-mortem itself,
not only in a repository document. A backtest that lives only in git does not become a decision.

### A deploy watch is an experiment, not a dashboard vigil

It has a hypothesis (what could this change break?), a control (what did this signal do before?),
and a falsifiable prediction. The failure mode this prevents is not missing a regression. It is
reporting one that was never there, because an alarming, wrong finding during a release costs more
trust than silence.

- Establish the payload, not the run. Classify the diff: most of it cannot produce a signal.
- Find the signal in the source: the metric registry the caller touches, the logger name, the message
  template, the exception types thrown and caught, and the level each logs at. A failure path that
  logs at warning is invisible to any alert filtered to error. Say so.
- Baseline before the rollout starts, for every signal you intend to judge, as a distribution with a
  sample count and the set of distinct normalized signatures already present. Prove the rollout had
  not started when you sampled.
- Compare like for like or not at all. Latency is diurnal. The valid control is the previous deploy
  at the same phase. Counters reset on rolling restart.
- Report no percentile below twenty samples, and no p95 or p99 below a hundred. Carry n in every
  percentile you state.
- Separate deploy-caused from deploy-transient with three questions: is it confined to the
  replacement window, does the baseline already contain it, and does a same-shaped component behave
  differently.
- Say what "no errors" does not prove: a loosened validator, a format change, a wrong value in a
  record, and a path that runs a handful of times an hour.

## 14. Assessments are scored on receipts

A capability is scored where it is implemented, not where the vendor documents it.

- **Answer whether the component should exist before scoring how well it is built.** What does it
  buy that the system loses without it, today, at measured load? If the answer is empty or
  speculative, that is the finding. Naming a pattern ("this is an outbox") is vocabulary, not value.
- **Ground the baseline before reading the argument.** Pin the commit. Verify the state of every pull
  request the argument leans on. Four states are routinely conflated: merged code is a shipped
  mechanism. A merged docs-only change is a plan. An open proposal has real execution risk. A
  closed, unmerged pull request means the capability does not exist, and this is the one that gets
  cited as if it shipped.
- **Audit every credited capability**, and run the check almost nobody runs: does the producer have
  a consumer? A destination written and never read is cost, not capability. One such grep turned a
  five-out-of-five isolation score into a two.
- **Check the rubric**: a criterion counted several times, an existence lens missing, a post-hoc
  override, a deciding lens quietly removed, a gate only one option can pass, the incumbent scored as
  zero-risk. Run sensitivity under at least the weighting the opposing case would choose.
- **When you reverse a previous assessment**, name what you adopt from it, correct its factual errors
  in place, and run the decisive test: hold their rubric verbatim, correct only the scores, report
  both totals. If the answer flips under their own rubric, the disagreement was never about method.
- **Separate what is owed regardless**: findings that are pure cost under every option, pulled out so
  they are not blocked behind a decision that may take weeks.
- **One current answer.** The first sentence answers the commissioning question. Fold corrections
  into the text where they live. One scorecard. History in the decisions document and in git.

## 15. Writing for the people who were not in the session

### Simple English

Engineer-facing text (a pull request body, a review reply, a ticket, a message to an engineer) is
written so a tired reader needs one pass. Active voice with the actor named. One instruction per
sentence. Twenty words for a procedure sentence, twenty-five for a description. Condition first, then
command. No semicolons, no em dashes, no phrasal verbs. One word for one meaning through the whole
document. Delete words that carry no fact: simply, robust, comprehensive, leverage, "it is worth
noting".

Two things a rewrite never does: cut a hedge to reach a word count (the hedge is the confidence, and
confidence is content), and drop a safety condition, an exception, or a scope qualifier.

Check for the tells that read as machine output: "not X, but Y", a closing line that repeats the
point, a row of fragments, a run-up before the answer, an argument with nobody, three items where you
have two or four, a guess that fills a gap, a sentence about the text instead of the subject.

### A pull request body says what to click and what to check

It is not a record of how the change was made. Four mandatory sections in this order, one screen
total:

- **Why**, as situation, complication, resolution. The problem, not raw data. Lead with the fix.
- **Approach**: the solution first, why this one and not the one a reviewer expects, then the reading
  route.
- **Proof**, naming the test and its result, or **Status: blocked** with one line per defect and the
  failed run linked.
- **Risks**: what breaks in production if the change is wrong, each with what exists today, how the
  change alters it, what breaks, and the specific thing the reviewer must verify. A risk checked and
  ruled out gets one line.

Not in the body: the session's history, the self-review narration, a narration of the diff, the
closing self-eval. After every push, compare the title and body with the diff and edit the pull
request rather than posting a comment in its place.

### A status update is a pointer into the durable record

Four parts: what is proven (each claim with its receipt), what is not done (named gaps with status),
where the work lives (links), and the single next outcome. A receipt is a count with a denominator, a
named test or run, or a live read-back, never an adjective. "474/474 on the target configuration",
not "tests pass". Disclose a prior claim that turned out wrong, never silently correct it: what you
believed, what checked it, what changed. State the scope boundary the reader would otherwise have to
check ("no production change made"). Default to one post. A second post earns its place only by
naming one fact the first explicitly left open.

### Link what you name

A reader who sees a bare ticket key or "the design doc" must find it before they can check it. Link
each pull request, ticket, commit, repository, document, run, thread, and dashboard at its first
mention, with the identifier or title as the link text. Build a URL only from an identifier you read
in a source. Never guess a number or a path. A link to lines of code is pinned to a commit. A metric
or log is linked with its query and its window. A file in the tree is linked relatively, because a
relative link follows the branch the reader has checked out.

### A closing keyword before a reference is a command

"fix", "close", or "resolve" in any tense directly before an issue or pull request reference, in a
pull request body, title, or commit message, closes the target when the text merges, in any
repository the merging account can write to, and a pull request is as valid a target as an issue.
Meaning does not matter. "This does not fix #7" closes #7. Only a token between, a code span, or an
HTML comment makes it inert. Write "opened as <link>". This closed three pull requests in one
organization before it was measured, one of them then announced as a rejection.

### Every agent-authored comment says so

A comment posted under a human's token opens with a disclosure line naming the agent and the posting
account. The body text is the only signal that an agent wrote it. Reviewers must never mistake an
agent comment for the human whose account carries it.

## 16. Pull requests and git, for an agent

- **Push before you say done.** When the brief is met, commit, push, and open the pull request,
  partial work and negative findings included, in every participating repository. A worktree is
  scratch space that gets purged. The pushed branch is the record.
- **Branch names describe the work.** No tool prefix and no slash. `broker-lag-rca-20260904`, not
  `cursor/investigate`. If a repository's own rules prescribe a prefix, fix the rule in the same
  session rather than quietly complying.
- **Open the pull request at the first commit, not at the end.** Never as a draft for an
  investigation, even an incomplete one.
- **Agents never merge their own pull request.** It ends the session open, non-draft, checks green,
  for a human to merge. Merge only on the user's explicit instruction in this session, never with an
  auto-merge or an admin override.
- **Never force push**, in any spelling: `--force`, `--force-with-lease`, a plus-refspec, a plain push
  after a rebase, or deleting the remote branch and pushing it again. Rewriting a published branch
  discards work no one in the session can see, and the dependent pull request comes back with
  conflicts in files that should have merged cleanly. Merge the new base into the branch instead.
  Where a rewrite has already happened locally, name the branch, name what the push would break, and
  leave the decision with the human.
- **Resolve the threads you fixed, and only those.** If you agree and make the change, reply with the
  commit and what changed, then resolve. If you decline, dispute, defer, or do only part, reply with
  your reasoning and leave it open. Never resolve a thread to end a disagreement. Reply on each
  thread, never as one summary comment.
- **Never hand-roll a loop that polls the hosting platform.** Use the one script that owns the poll
  interval and the deadline. For anything else (review state, comments, whether something merged),
  read it once when you need it. A hand-rolled loop eats a shared API budget and waits on a condition
  that can never arrive: a run that was never dispatched is indistinguishable from a running one, and
  one was waited on for twenty hours. The tell is a loop and the platform CLI in the same script. Your
  tooling's own examples may show the prohibited pattern. The rule wins. A watch's exit condition must
  be reachable without a human: waiting for a pull request to be merged is not a terminating
  condition.
- **Use exactly one backgrounding mechanism.** A background flag on a command that also ends in a
  shell ampersand backgrounds it twice, and the tool reports success when the wrapper shell returns,
  not when the real command finishes.
- **Sync first.** Before work grounded in repository state, fetch and check how far behind the
  default branch the checkout is. A stale checkout is a stale skill set and a stale history search,
  silently.

## 17. The learning loop

The system improves because every session that hits friction leaves a change behind, in the right
place, without contaminating the user's work.

- **Fix the skill that failed in the same session.** If a skill's documented command, tool path,
  metric name, or resource mapping was wrong, correct it and include the edit in the same pull
  request as the work. A skill that made you improvise will make the next agent improvise. Prefer a
  copy-pasteable fix over a vague note.
- **A lesson never rides on the task's branch.** The closing self-eval proposes the wording and names
  the place. Landing it is its own scoped change, from an isolated worktree, on a branch named for
  the source branch plus a suffix, touching only guidance paths, opened as a separate pull request a
  human may ignore. Before opening, survey the open harvest pull requests and join one that
  prescribes behavior for the same trigger. Five parallel harvests of one learning with three
  inconsistent recipes is the case this exists for.
- **Route a lesson by what it is.** An always-on constraint goes in a rule. A repeatable procedure
  extends an existing skill first and creates a new one only for a distinct workflow. A
  cross-repository practice goes to the shared home. Detailed reference goes in docs, linked from the
  owning skill. A personal preference goes in an uncommitted personal location, never a shared file.
  A one-off flake is not persisted.
- **Guidance is operational and short.** The instruction, its trigger, and, only where the rule would
  otherwise look arbitrary, the one fact that makes it necessary. No incident narrative in the rule.
  The story belongs in the pull request.
- **A fact about code goes in the cheapest container that enforces it**, tried in order: a test, when
  a machine can check it. One sentence under the principle it instantiates. A path-scoped rule. A
  skill, only for a procedure with a trigger phrase a request will contain.
- **Knowledge goes to the product, not the agent.** When an assistant answered wrongly, the first
  question is whether the gap is knowledge (the agent could reach everything and did not know how to
  think) or a tool gap (a needed observation is unreachable). Most gaps are knowledge gaps. The fix
  is a skill the assistant loads, proven by a blind A/B on the deployed agent with the answer key
  held back, and an honest null ("the current agent already answers well") is a valid result.
- **Keep a baseline before you diagnose.** Ask the deployed assistant the question first, in the
  reporter's own words. One call settles whether it answers correctly, cannot answer, or answers
  confidently and wrongly. The third is the expensive case because nothing about it looks like a
  failure.
- **Budget the guidance and ratchet it down.** Caps on always-on text only move down. Compression
  passes that found twenty percent of a lesson corpus was provenance, and condensed rules that
  graduate into the owning repository, are how the budget is met.

## 18. Adopting this

1. **Start with five gates, not fifty.** Evidence before changing code. Verify before complete.
   Root-cause proof. The investigation order. Never force push. Each as a short rule that points at
   a fuller skill.
2. **Write each rule from an incident you have.** If you have not had the incident, you do not need
   the rule yet. When you do have it, write the date, the measurement, and the sentence the agent
   used to get past the gate, and put that sentence in the Forbidden list.
3. **Make the rule the floor and the skill the procedure.** Never copy the procedure into the rule.
4. **Keep one copy of everything.** A repository that departs from the shared practice names its
   departure as a delta on the same name.
5. **Make verification a requirement of the brief, not a ritual.** "Has this run on a second input"
   and "did you read the end state back through a second path" are checklist items, not virtues.
6. **Put the decision log and decision records in the artifact**, not in the chat. A later reader of
   only the document must be able to see why each path was chosen and what the user actually asked.
7. **Measure the rules against behavior.** Record which skills load in which sessions. An agent that
   writes the forbidden loop with the rule loaded the whole time is telling you the rule is in the
   wrong place or the wrong words.
8. **Treat your tooling's examples as unsanctioned.** A harness ships worked examples of exactly the
   patterns these rules forbid. The rule wins, and the rule has to say so, because the example is the
   proximate guidance at the moment the agent reaches for the tool.

## Sources

The body above stands alone. The rules and skills it was distilled from ship beside it, in
company-agnostic form, so a reader can go from a section here to the gate that enforces it:

- Working practices, as skills: [`behavioral-guidelines`](../.agents/skills/behavioral-guidelines/SKILL.md),
  [`coding-principles`](../.agents/skills/coding-principles/SKILL.md),
  [`finding-existing-patterns`](../.agents/skills/finding-existing-patterns/SKILL.md),
  [`context-research`](../.agents/skills/context-research/SKILL.md),
  [`evidence-before-changing-code`](../.agents/skills/evidence-before-changing-code/SKILL.md),
  [`plan-pre-research`](../.agents/skills/plan-pre-research/SKILL.md),
  [`root-cause-proof`](../.agents/skills/root-cause-proof/SKILL.md),
  [`verify-before-complete`](../.agents/skills/verify-before-complete/SKILL.md),
  [`prove-it-on-a-second-input`](../.agents/skills/prove-it-on-a-second-input/SKILL.md),
  [`reading-before-changing`](../.agents/skills/reading-before-changing/SKILL.md),
  [`simple-english`](../.agents/skills/simple-english/SKILL.md),
  [`writing-pull-requests`](../.agents/skills/writing-pull-requests/SKILL.md),
  [`writing-status-updates`](../.agents/skills/writing-status-updates/SKILL.md),
  [`linking-references`](../.agents/skills/linking-references/SKILL.md),
  [`pr-comment-merge-policy`](../.agents/skills/pr-comment-merge-policy/SKILL.md),
  [`agent-self-eval`](../.agents/skills/agent-self-eval/SKILL.md),
  [`write-skill`](../.agents/skills/write-skill/SKILL.md).
- Operations practices, as skills:
  [`oncall-investigation`](../.agents/skills/oncall-investigation/SKILL.md),
  [`rca-writing`](../.agents/skills/rca-writing/SKILL.md),
  [`monitoring-gap-analysis`](../.agents/skills/monitoring-gap-analysis/SKILL.md),
  [`production-deploy-monitoring`](../.agents/skills/production-deploy-monitoring/SKILL.md),
  [`architecture-assessment-evidence`](../.agents/skills/architecture-assessment-evidence/SKILL.md),
  [`skill-from-conversation`](../.agents/skills/skill-from-conversation/SKILL.md),
  [`doc-toc`](../.agents/skills/doc-toc/SKILL.md).
- The always-on rules under [`.agents/rules/`](../.agents/rules/), one floor per gate above.
- The references [`investigations.md`](investigations.md), [`agent-evals.md`](agent-evals.md),
  [`production-changes`](runbooks/production-changes.md),
  [`secret-safe-diagnostics`](runbooks/secret-safe-diagnostics.md), and
  [`declarations-and-manifests`](runbooks/declarations-and-manifests.md).
- The entry points [`AGENTS.md`](../AGENTS.md) and [`CLAUDE.md`](../CLAUDE.md), which make the
  rules load.
