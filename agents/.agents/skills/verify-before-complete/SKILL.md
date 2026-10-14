---
name: verify-before-complete
description: MUST USE before marking any task, ticket, or PR complete, or posting a final answer.
---

# Verify before complete

## Gate

**Do not mark a todo complete, tell the user a task is done, or post a final chat or PR answer
until the original request has been re-read and every requirement verified against actual
output.**

## Outcome briefs

When the brief is to make something **work**, the deliverable is the working result. A precise account of why it still fails is a status update, not completion.

- Drive it to an actual success and link it: the created record, the green run, the completed conversation. If you cannot, say so as a failure or a request for input.
- A tool returning `200` or an agent saying "done" is a claim. Read the end state back through a second path, such as a direct API read, a query or an independent re-run, before you report it.
- A conclusion drawn from one vantage point (one permission scope, one mode, one search phrasing) is a hypothesis until you rule out that the vantage point produced it.

## Procedure

1. **Re-read the original brief** -- the user's first prompt, any attached plan or ticket, and any
   mid-task scope changes. Quote or paraphrase verbatim; do not rely on memory.
2. **Enumerate requirements** -- list every explicit deliverable and every implicit expectation
   (PR open, tests pass, a specific file exists, live verification, no unrelated files touched,
   etc.) as a checklist.
3. **Verify each against actual output** -- for every item, cite one line of evidence: file path,
   command exit code, PR URL, tool output snippet. Verify what was **produced**, not what was
   **intended**.
   A live test proves the fix for the account, identity and environment it ran in. Name them. If
   the target is derived from the caller's identity, show that a second identity reaches the right
   resource -- the same one when the target is shared, its own assigned one when the target is
   per-identity -- or list it as an open gap.
4. **List gaps** -- any checklist item without evidence is a gap. Partial counts as a gap. Sort each
   gap into exactly one of two states: **blocking** (evidence is obtainable now) or **deferred**
   (the evidence cannot exist yet -- it needs a release, a downstream repo's adoption, or elapsed
   time). Deferred is for evidence that is impossible now, never for work you did not do; if you
   could go get it, it is blocking.
5. **Iterate** -- fix every blocking gap before proceeding. Do not mark todos complete or declare
   done while a blocking gap remains. Each deferred item must name its owner, its trigger, the exact
   evidence that will settle it, and where it is recorded (a ticket, or an unchecked PR checkbox) --
   a deferral nobody will be handed is a gap wearing a better label.
6. **Self-evaluate, unprompted** -- write two or three sentences to close your final message to
   the user, placed last, below the checklist Step 7 describes: what the request turned
   out to be, against what it first looked like; the earliest point the evidence to know that was
   already available; and the one habit that would have caught it sooner. Skip this step only for
   a one-line answer that carries no lesson. If the lesson generalises beyond this one task, do
   not merely report it -- name the place that will apply it next time (a skill, a rule, a prompt
   this agent or a future one reads) and propose the wording. Landing it is its own scoped change,
   authorized separately: shared agent guidance is never edited as a side effect of the task that
   taught the lesson, and never folded into that task's commit or PR. Route it per
   [`agent-self-eval`](../agent-self-eval/SKILL.md), which keeps skill improvement off the user's
   work branch and off the critical path.
   This self-eval is for the user, in the closing message, and two or three sentences is the whole
   budget. It is not a PR section: transplanted into a PR body and expanded into an enumeration of
   everything a review pass found, it buries the findings a reviewer actually needs. What belongs in
   a body is in [`writing-pull-requests`](../writing-pull-requests/SKILL.md).
7. **Only then complete** -- mark the final todo done and summarize for the user with the checklist
   showing every item as verified or as an explicitly labelled deferred follow-up, and the Step 6
   self-eval closing it. Never present a deferred item as verified, and never let the two blur into
   one "done" line.

## Forbidden

- Completing on intent ("should work", "the code looks right").
- Skipping the re-read because "we just finished."
- Marking the last todo done with open blocking gaps.
- Marking the last todo done with commits sitting unpushed. Work nobody else can see is not
  delivered, and a worktree can be deleted with the session -- so pushing is the default, not a
  judgement call. The only exception is work the user explicitly scoped as local-only; that is not
  licence to push past the scope you were given, and if a push would exceed it, say so rather than
  quietly widening or quietly skipping it.
- Reclassifying a blocking gap as deferred to get to "done" -- deferral is for evidence that cannot
  exist yet, not for verification you chose to skip.
- **Inventing an authority gate to excuse work you could have done.** "That needs the sponsor's
  sign-off", "that is a product decision", "that would be a judgement call this session does not get
  to make" -- where no such gate was stated by the user, by a rule, or by the brief. Capability
  ("I cannot") and permission ("I am not allowed to") are the two reasons a part of a brief can be
  left undone, and both are facts about the world that you can point at. A gate you reasoned your way
  to during the task is a preference wearing a constraint's clothes. If you think a part genuinely
  needs someone's decision, the deliverable is to ask them, in this session, and say you are waiting.
- **Reporting a multi-part brief as complete with a named part undone**, however fully the other
  parts were delivered and however clearly the omission is disclosed further down. N of M is not
  done; it is N of M, and the headline has to say so.
- **Staging a tree while a background job is writing into it.** `git add -A` stages whatever has been
  flushed at that instant -- the snapshot is taken then, not at commit time, so committing later does
  not save you -- and a verbatim output truncated mid-write looks exactly like a short one --
  no error, no marker, and a diff that reads as deletion. Let the job finish, or stage named paths it
  is not touching. Measured 2026-09-13: a committed analysis output went from 1,510 lines to 721,
  stopping between two outcomes, because the commit landed while the analysis script was mid-run.
- Summarizing success without citing actual artifacts.
- Reporting a documented failure as done when the brief was to make the thing work.
- Treating the self-eval step as optional decoration -- outside a one-line answer, if it surfaces
  nothing, say so briefly rather than omitting it, so its absence is a decision, not an oversight.
- Moving the self-eval into a pull request body, or growing it there into a log of the session. It
  closes the message to the user; a PR body has different readers and its own budget.
- Slipping a skill, rule, or prompt edit into the task's own commit because the self-eval produced
  a lesson. Propose it; land it separately, once authorized.

## Why the self-eval step exists

A green gate can sit on an unasked question. On one ticket an agent restored a payout provider type
that had been removed on purpose. The evidence of the removal was already in its context, and only
a closing "what did this turn out to be" check would have surfaced it. The Example below walks
through it.

## Why the invented-authority line exists

2026-09-13, one pull request. The brief was "complete the next steps outlined in [a document]". The
document named five. Four were done well; the fifth -- re-run the analysis on a second vertical --
was read-only work the session had the access, the scripts and the time to do. It was not done, on
the stated grounds that spending the shared report queue was "a sponsor's decision". No sponsor gate
existed: the brief's own rules of engagement allowed the pulls, and the session had written *in the
same document*, in its own words, that "reading production is within the brief's rules of engagement
and a pull is not a production change" -- and then declined anyway. The session reported the goal
met, with the omission disclosed in a caveat.

The user's response is the reason this is a Forbidden line and not a note: *"i dont understand why a
goal of 'complete the next steps' would return goal success and then say 'Step 5 -- retail: not
started.' ... i sort of assume all of the work in here was shit quality."* That inference is the real
cost. A visible, unexplained hole in the headline does not read as one missing part; it reads as
evidence that nothing else was checked either -- and in that instance the suspicion was right, because
running the fifth step immediately found six defects in the four that had been called done.

Note what did **not** fail here: this skill's Step 4 already said "Deferred is for evidence that is
impossible now, never for work you did not do; if you could go get it, it is blocking." The guidance
was correct and specific. What it did not anticipate was the evasion of manufacturing a *permission*
reason rather than a capability one, which Step 4's wording does not cover. That is now named above.

## Composes with

- [`prove-it-on-a-second-input/SKILL.md`](../prove-it-on-a-second-input/SKILL.md) -- when the brief's
  remaining part is "run it on the other dataset", doing it is both the missing deliverable and the
  test of everything already delivered. In the incident above it was the same action twice over.
- [`evidence-before-changing-code/SKILL.md`](../evidence-before-changing-code/SKILL.md) -- this
  skill gates the **finish**; that one gates the **decision to add/restore something** partway
  through.
- The repo's worktree workflow, where it keeps one -- its verification section is this skill's
  worktree-setup-specific instance.
- [`agent-self-eval/SKILL.md`](../agent-self-eval/SKILL.md)
  -- the friction-detection counterpart: it fires on session signals (MCP failures, retry loops,
  tool thrash, ignored guidance) and owns where a durable lesson gets routed. Step 6 here is the
  every-task floor; that skill is the mechanism once a lesson is worth persisting.

## Example

**Bad:**

> All todos complete. The payout provider factory should render `LEGACY_PAYOUT` correctly now.

**Good:**

> Checklist:
> 1. Verified -- history checked before writing code: `git log origin/"$base" HEAD --oneline -i
>    --grep=LEGACY_PAYOUT` shows `a1b2c3d` (`TICKET-247`) dropped the type deliberately three weeks
>    ago.
> 2. Verified -- `TICKET-253` does not reference that removal; re-read the description, not just the
>    comments.
> 3. Verified -- asked the author of `a1b2c3d` on `TICKET-253`, linking the commit, its PR, and
>    `TICKET-247`; they confirmed the removal stands and the ticket was filed off the error-tracker
>    symptom.
> 4. Verified -- nothing stale left behind: `git grep -i legacy_payout origin/"$base" -- src/` is
>    empty, so there is no residual reference to clean up either.
> 5. Verified -- `TICKET-253` closed against `TICKET-247` with that confirmation quoted; no code
>    change shipped, and the reason is on the ticket rather than only in this session.
> 6. Deferred -- the error-tracker event stops once the reporter retires the test tenant generating
>    it. Cannot exist yet; owner the reporter, trigger that retirement, evidence a zero-event query
>    for `Unknown payout provider type` over 48h. Recorded as a follow-up on `TICKET-253`.
>
> Self-eval: the request read as "the type is missing, add it back," but the history check showed a
> deliberate removal the ticket never mentions -- so the deliverable turned out to be a question,
> not a diff, and the answer came from the person who made the removal rather than from me. The
> evidence was available before the first line of code. The habit: run the history check before
> writing, and treat "history contradicts the ask" as something to escalate, never something to
> settle alone -- restoring and refusing are both settling it.
