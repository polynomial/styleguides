---
name: skill-from-conversation
description: Must be read when asked to "build a skill so the agent could have answered this", to codify a recurring resolution, to close an assistant or MCP answer gap from a real thread, or when the assistant answered wrongly or denied a capability.
---

# Build a skill from a solved conversation

You are given a conversation where a human expert solved something (a chat thread link, a
support-desk ticket, or a problem statement plus the answer that worked). Goal: make the agent able
to reach that same answer **on its own, blind**, by encoding the missing judgment as a skill — and
prove it. This is the generalized loop behind the investigation that produced it.

**Before publishing any number from this run:** read [`agent-evals.md`](../../../docs/agent-evals.md) (measurement gates and blind-test rules).

## Take the baseline before you diagnose anything

**Ask the deployed assistant the question first, in the reporter's own words, naming the account, and
keep the tool sequence.** One call. It settles which of three cases you are in — it answers
correctly and there is no gap, it cannot answer, or it answers confidently and wrongly — and the
third is the expensive one, because nothing about it looks like a failure. Skipping this is how a
session ends up reasoning about which guidance should have loaded when the cheap question was
whether the capability was reachable at all. It is also Pass A of §6, already taken.

## Golden rule: blind means blind

Follow the blind-test rules in [`agent-evals.md`](../../../docs/agent-evals.md). The *initial question*
and any admin-interface or notification URLs in it are allowed inputs. The expert's answer is the
**answer key** — you read it to reverse-engineer and to grade, but the agent under test must never
see it. Keep two clearly separated activities: (1) the **blind run** (agent answers from the
question + the skill only) and (2) the **review vs reference** (you compare to the expert). Never
let the answer key leak into the blind run.

## The loop

### 1. Capture the question and the answer key
Read the full thread (all replies, not just the first). Extract, verbatim: the **initial
question** (the blind input) and the **final answer** the expert converged on — root cause, the
evidence they used, the remediation, and any "recurring / known issue" framing. Hydrate raw ids
(client, campaign, person) to names + admin-interface links via the product's API or MCP.

### 2. Reverse-engineer the expert's path
Write down the ordered steps the expert actually took — which surface they looked at, which field
was the tell, what they compared against, how they confirmed timing. Identify the **crux step**
(the one observation that cracked it). This becomes the spine of the skill's judgment.

### 3. Verify the root cause independently, live
Re-derive the conclusion from current platform state using read-only tools (the product's API or
MCP, the metrics system, reports). Confirm the expert's tell is really there and really explains the
symptom. If you cannot reproduce it, stop — you do not yet understand the problem well enough to
teach it.

### 4. Decide: knowledge gap or tool gap?
The pivotal question. For each artifact the expert used, ask *"can an agent already reach this
with an existing tool?"*
- **Everything reachable, agent just didn't know how to think** → **knowledge gap** → a catalog
  **skill** (the common case).
- **A needed observation is genuinely unreachable** (no tool exposes it) → **tool gap** → a change
  to the assistant's tool server (new/extended tool), plus a skill to use it.
- **The agent needs public product context** → a **product-docs** page (route via the docs repo's
  own authoring procedure), possibly with a skill.
State this explicitly; it decides which repo you touch. Most "the agent should have known this"
gaps are knowledge gaps.

### 5. Author the skill (catalog)
Runtime skills live in the assistant's skill catalog, one `SKILL.md` per skill under that repo's
layout, and are auto-discovered by the assistant's tool search (no wiring change). Follow the
catalog's **content boundaries**: judgment scaffolding, not a runbook — **no client names, no
AI-product names, no internal ticket links, no tool signatures/schemas/step-by-step tool calls** in
the body. Teach what to distinguish, which evidence matters, the known failure mode, the remediation
shape, and what *not* to conclude. Pair with an eval case in the catalog's eval set (disabled until
a fixture exists). Register per that repo's rules.

### 6. Prove it blind (A/B on the deployed agent)
No local stack is needed when the deployed endpoint loads the catalog from a branch. Push your
catalog branch, then compare **Pass A** (current production catalog) vs **Pass B** (your catalog
branch) on the *same agent*, asking the initial question with no answer key:

```bash
set -a; source <the assistant's credentials env file>; set +a   # the API key the harness reads
python3 <the eval harness> <client_id> <agent> -        < q.txt   # Pass A: production catalog
python3 <the eval harness> <client_id> <agent> <branch> < q.txt   # Pass B: your branch
```

- **When a run looks like a dead endpoint, suspect the caller.** The eval harness's own docstring
  carries the measured traps — the endpoint's path and its asynchronous shape, and why probing it
  without a token makes every path look alive. Read it there rather than from a copy here.
- **Gate on strings, not on reading the answers.** Assert the wrong claim absent and the right one
  present, and count tool calls per arm; per the measurement gates in [`agent-evals.md`](../../../docs/agent-evals.md) a zero-tool answer to a
  question that needs account data is a harness defect rather than a cheap result, and arms are only
  comparable on equal answered counts.
- **Agent names are resolved server-side from the deployed catalog**, not your branch — use a
  deployed name. A branch-only agent name 404s.
- Prefer running **both arms on the agent real users hit**; corroborate on the read-only
  single-response assistant, which is less likely to wedge.
- For a batch/rigorous version, use the repo's batch eval and judge harnesses, pointed at your
  catalog branch, with an LLM/ground-truth judge instead of eyeballing one answer.

### 7. Grade honestly, then iterate
Compare Pass B to the answer key: did it reach the crux, the root cause, and the correct
remediation? A skill "works" when the blind agent independently lands the expert's conclusion.
If Pass A already answers well, there may be no real gap — say so (an honest null is a valid
result; one earlier run of this loop ended exactly there). Report **every run including
wedges/flakes** — do not cherry-pick ([`evidence-integrity`](../../rules/evidence-integrity.mdc)).

**Op gotchas (deployed agent API):** calls run minutes; on the originating system the gateway 502'd
conversations past ~556s and some act-shaped prompts wedged the escalation-capable agent — retry,
keep the client timeout < 600s, and run long calls in a subagent (background bash jobs get killed).

### 8. Ship
- **Catalog PR** (draft) with the skill + eval + the A/B evidence table.
- **Investigation PR** (draft, in the operations repo) with the investigation doc (reverse-engineered
  steps, live verification, gap analysis, verbatim blind A/B, decision log + ADRs per
  [`investigation-contract`](../../rules/investigation-contract.mdc)) and a short summary doc,
  cross-linking the catalog (and any tool-server/product-docs) PRs.
- If step 4 found a tool or docs gap, open those PRs too and link them.

## Definition of done
A conversation went in; out came a merged-ready skill whose blind A/B shows the deployed agent
reaching the expert's answer without help, plus the docs that prove it and the PRs that ship it.

## Related
- Blind discipline and measurement gates: [`agent-evals.md`](../../../docs/agent-evals.md)
- A/B harnesses: the repo's batch eval harnesses and its blind eval script
- Public-docs route: the docs repo's own authoring procedure
