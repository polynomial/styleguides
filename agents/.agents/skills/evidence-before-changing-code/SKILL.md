---
name: evidence-before-changing-code
description: MUST USE before any change prompted by an error, an error-tracker event, a support ticket, or "X used to work", and before naming a root cause.
---

# Evidence before changing code

Scopes Gate 2 ("Re-derive against CURRENT source") of
[`root-cause-proof`](../root-cause-proof/SKILL.md) to the moment that matters most for a
code-writing agent -- the instant before you write the fix, not just before you write the RCA
doc -- and carries the in-flight-work checks (step 2 below) that a fix must reconcile with.

## The failure this exists to prevent

A report can be accurate about a symptom and still ask you to reverse a deliberate decision. The
dangerous case is a report that never mentions the removal: restoring the thing looks responsive,
closing the report looks rigorous, and both are unilateral calls on a contradiction only the
removal's author can settle. The gate below makes you find the removal and ask that author. The
Example at the end is a real instance.

## Gate -- run before you write the change

Before adding, restoring, re-enabling, or "fixing forward" anything a report implies should exist:

0. **Fetch first, and name the refs you search** -- a precondition for steps 1-3, not a suggestion.
   Stale refs answer every history question below wrongly: a removal that landed after you
   branched, or work someone has in flight right now, is simply not there to find, and the gate
   passes green on absent evidence.
   ```bash
   git fetch origin && git remote set-head origin --auto >/dev/null
   base=$(git symbolic-ref --short refs/remotes/origin/HEAD | sed 's#^origin/##')
   ```
   Resolve the default branch rather than assuming `master` -- some repos are on `main`. Standing
   on a feature branch is normal -- that is where this gate runs, and it is not a reason to stop.
   What matters is that the commands below name their refs, because neither ref alone is enough:
   `HEAD` covers the default branch only up to your branch point, so it misses a removal landed
   since; `origin/"$base"` misses whatever is already committed on your own task branch. Search
   both. If you are instead searching a long-lived base checkout (the one your worktrees are cut
   from), fast-forward it first (`git pull --ff-only origin "$base"`), and stop and report -- do not
   reset, stash, or force -- if it is dirty, is not on the default branch, or the fast-forward would
   not be clean. That is the base-checkout freshness rule of the repo's worktree workflow, applied
   here.
1. **Search the target repo's history for the thing itself**, not just the symptom, across both
   refs:
   ```bash
   git log origin/"$base" HEAD --oneline -i --grep=<thing>
   git log origin/"$base" HEAD --oneline -S<symbol>   # pickaxe: added/removed this exact token
   ```
2. **If a commit removed it, read the PR it names and the ticket that PR names** before writing any
   code. Then decide by asking one question -- *does the report acknowledge that removal?* -- and
   there are exactly three answers, not two:
   - **The report acknowledges the removal and still asks for the change.** Follow the report. Recent
     history is context, not a veto; someone may well have decided to bring the thing back.
   - **The report never mentions the removal** (this was the originating case). **Stop and ask.** Do
     not silently restore it, and do not silently refuse or close the report on history alone -- both
     are unilateral calls on a contradiction you have no standing to settle. Ask **the author of the
     conflicting change**, by name, linking the commit, the PR, and the ticket: "your `<sha>`
     (`<removal ticket>`) dropped this on purpose; `<this ticket>` asks for it back and doesn't
     mention that -- which is right?" A generic "someone should confirm" is not asking.
   - **Nothing removed it; it never existed, or it broke another way.** Continue the gate; this is an
     ordinary fix.

   The trap in the middle case is that *both* exits feel like diligence. Restoring looks responsive;
   refusing looks rigorous. Neither one tells the person who made the conflicting change that their
   work is being reversed.
3. **Check what else is in flight on the same component**, so you don't fight or duplicate work
   already underway:
   ```bash
   gh pr list --repo <owner>/<repo> --state open --limit 30 --json number,title,author,updatedAt,headRefName
   gh pr list --repo <owner>/<repo> --state all --search "<component or symptom> in:title,body" --limit 20
   git log origin/"$base" --since="<relevant window>" --format="%h %ad %an %s" --date=iso -- <path>
   ```
   If one engineer's name keeps coming up, their open branches and their comments on the
   originating thread are primary sources -- read them.
4. **Fire a research query at the institutional-context tool** (the research tool over pull
   requests, chat, tickets, docs and incidents), scoped to the thing and the symptom, in parallel
   with the git/gh checks above. It surfaces prior PRs, rejected approaches, and incident history
   that neither git log nor gh will find on their own. If the tool is unavailable, record that in
   the write-up ("institutional context not checked -- research tool unavailable") and treat that
   context as unchecked; never write that context research was done. The git and `gh` checks in
   steps 1-3 stay mandatory either way -- they are not satisfied by, and do not substitute for, a
   research result you could not obtain.
5. **A referenced-but-unreadable source is a blocker, not a footnote.** If a chat thread, ticket,
   or doc is named and you cannot read it, say so and ask for it (paste it, grant access) before
   finalizing the change -- do not proceed on a "confirmed" or "hypothesis" that quietly skips it.

## The wire before the code

A report that names a mechanism -- a cookie, a header, a redirect, a CORS refusal, a missing row --
is a claim about what a live host sends. Read that first; the code only says what it should send.

- **Query the live host for what it actually sends.** Replay the reporter's own request -- their
  URL, method and request headers -- and read the response headers for the cookie name, its
  `Domain`, its flags and its lifetime; a `HEAD` can be answered differently from the `GET` or
  `POST` the reporter made, so use it only when the report is about `HEAD`. An `OPTIONS` preflight
  with the real `Access-Control-Request-*` headers proves an allowlist. Reproduce over the wire
  before designing a fix, and check every sibling host or service the client calls -- allowlists
  are kept separately and drift.
- **Read what the shipped default already sends before prescribing "fix it with parameter X".**
  Read the served artifact, not a checkout: if the default tag or component already sends X, the
  symptom took a different path. Prove a parameter is decisive, not merely honoured -- received in
  the log but not deciding. Re-check "does the defect still exist" from live surfaces, never from
  your previous answer; a rebuilt artifact that still carries the defect is stronger evidence than
  an unchanged one.
- **When a count decides the answer, read it through two independent paths.** Two versions of one
  list endpoint can disagree about what exists. An internal contradiction inside one response -- a
  child record present and its causal parent absent for the same root id -- means the list is
  truncated, not that the world is strange, when the endpoint returns both kinds of record under
  the same filters and authorization scope; when it does not, the missing parent is a scope fact
  and says nothing about truncation.

## Deliberate shapes: the same gate for a line you are removing or routing around

The report case above is one instance of a wider one: **some lines exist because something
broke**, and a diff that removes one looks identical to a diff that adds a feature. The cost shows
up weeks later as an absent guardrail. Run this before the first edit whenever the change deletes,
replaces, inlines, "simplifies" or reverts an existing line — or **adds a new path around one**:
a new caller, branch or overload that reaches the same behaviour without passing the existing
guard, which removed-line detection will not see.

The areas where a one-line change is load-bearing far from the diff, in any repo: execution
routing and durability, loop and rate cutoffs and dead-state gates, ack/nack and retry policy,
idempotency and dedupe guards, concurrency and ownership rules, which credential a call runs
under, timeouts and deadlines. Treat an edit there as in scope even when it only adds.

1. **Detect the decision.** `git log --oneline -S'<exact text of the line>' -- <path>` finds the
   commit that decided the current shape; for an additive change run it on the guard you might be
   bypassing. Resolve the SHA to its pull request from the SHA, not by keyword:
   `gh api repos/<owner>/<repo>/commits/<sha>/pulls --jq '.[].html_url'`. It applies when the
   commit or PR describes the shape as a fix, a safety property, an incident response or an
   explicit routing decision; a drive-by refactor or the original feature commit does not.
2. **Research why, not what.** Read the PR through the institutional-context tool, then run one
   deep research query: why was the guard introduced, what failure does it protect against, what
   replaced what. Follow the chain to the ticket and the thread; an unreadable source is a blocker.
3. **Write the verdict before editing**, one per decision found: **PRESERVES** (the guard still
   applies on every path it covered — say how), **NARROWS** (a smaller set of paths — name what is
   no longer covered and why that is safe), or **REVERSES** (some path it covered is now
   unguarded — name the protection lost, the metric or log that would show its absence, and either
   keep it or get explicit human sign-off). "CI is green" is not evidence a runtime budget or
   dead-state check survived; "the bad thing can't happen here" is not proof the cutoff still
   exists. A prior decision is a lead: re-derive it at current HEAD, since the guard may have moved.
4. **Carry the evidence into the change.** Keep a `Decision Evidence` block in the branch as you
   work — guard and `file:line`, introducing PR and date, incident or ticket, verdict — and add a
   `## Prior decisions` section to the commit body and the pull request body, one bullet per
   decision: the PR, what it established, and whether this change preserves, narrows, or reverses
   it. `none found` is a valid bullet; an absent section is not. When the verdict is NARROWS or
   REVERSES, leave the remaining guard discoverable in code by name, so the next editor hits step 1.

This gate produces evidence and a written verdict, never a block: a reversal with a named cost and
human sign-off is a legitimate outcome. One `git log -S`, one SHA lookup and one read of the PR is
the normal cost; twenty minutes of archaeology means the change is bigger than it looked, and that
is the finding. The originating case was a correct bug fix that called a method an earlier pull
request had deliberately replaced weeks before, to keep every asynchronous restart behind one
durable trigger — fifteen green checks, and one `git log -S` would have shown it.

## Reconciliation requirement

If an open PR, a recent commit, or institutional context touches the same thing your report is
about: read it fully before writing your fix, and state explicitly how your change relates to it
(confirms / contradicts / orthogonal / finishes it). If it contradicts your working hypothesis,
resolve the contradiction with evidence before touching code -- do not ship a fix premised on
facts another engineer's PR, or your own repo's history, already disproves.

## Forbidden

- Treating "there's an error" as proof the erroring thing should be added back, without checking
  why it isn't there.
- Writing a root-cause section, or a fix, without having run the git-history and open-PR checks
  above.
- Citing a prior incident, an old write-up, or a fix you remember from memory as the current
  state of the code -- re-derive against the file at current HEAD, `file:line`, every time. The
  old fix may already be deployed, reverted, or superseded.
- Proceeding past an unread, referenced chat thread or ticket because the bot/agent isn't in the
  channel or lacks access -- ask instead.
- Writing "confirmed" when a hop in the reasoning is actually a hypothesis you haven't evidenced.
- Treating recent history as an automatic veto over what the report asks for -- silently refusing, or
  closing the report as already-handled, is as unilateral as silently restoring. If the report does
  not acknowledge the removal, the answer is to ask, not to pick a side.
- Surfacing the contradiction to no one in particular. The person to ask is the author of the
  conflicting change; name them and link the commit, PR, and ticket.
- Recording the conflicting commit as a hedged aside ("worth a check", "possibly related") and then
  proceeding anyway. Finding it and not acting on it is the failure, not a mitigation of it.

## Composes with

- [`verify-before-complete/SKILL.md`](../verify-before-complete/SKILL.md) -- that skill gates the
  finish (did the output satisfy the request, and what's the lesson); this one gates the decision,
  earlier, to make the change at all.
- The repo's worktree workflow, where it keeps one -- base-checkout freshness is the same principle
  applied to reading code, not writing it: a stale checkout produces a stale, wrong history search
  too.

## Example

**Bad (restore):** "The error tracker says `LEGACY_PAYOUT` throws `Unknown payout provider type` ->
add `LEGACY_PAYOUT` back to the type union, ship a green gate, open the PR."

**Also bad (refuse):** "…`a1b2c3d` dropped it on purpose under `TICKET-247`, so `TICKET-253` is
invalid -> close it as already-handled." Same unilateral call, opposite direction, and the person
whose removal is being cited never hears that a ticket is asking to reverse it.

**Good:** "The error tracker says `LEGACY_PAYOUT` throws `Unknown payout provider type`, and
`TICKET-253` asks to display it. `git log origin/"$base" HEAD --oneline -i --grep=LEGACY_PAYOUT`
shows `a1b2c3d TICKET-247 Drop residual LEGACY_PAYOUT provider type`, eleven commits back, and
nothing re-adding it on either ref. Reading that PR and `TICKET-247`: removed on purpose, UI retired
under an earlier ticket, sole customer churned years ago.
`git grep -i legacy_payout origin/"$base" -- src/` returns nothing left to remove -- against the
fetched base, not a working tree that may be stale or dirty.

`TICKET-253` does not mention that removal, so this is not mine to settle either way. Asked the
author of `a1b2c3d` on the ticket, linking the commit, PR `#NNNN`, and `TICKET-247`: the type was
dropped deliberately three weeks ago and this ticket asks for it back without referencing that --
should it come back, or should `TICKET-253` be closed against the removal? Not writing code until
that answer lands."
