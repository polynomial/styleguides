---
name: behavioral-guidelines
description: MUST USE before any non-trivial analysis, design, investigation, proposal, or review, and before deciding what code to write.
---

# Behavioral & Reasoning Guidelines

Guidelines for finding the right problem before acting, and for converging once you have. When a
piece of work is just words restating the request, it has not yet done the job — these principles
turn it into a decision a senior engineer can evaluate and trust. Implementation discipline for all
code, scripts and infrastructure definitions included, lives in
[`coding-principles`](../coding-principles/SKILL.md).

**Explore first, converge second.** The first half of this file widens the problem; the second half
narrows the solution. Reaching for the convergence rules on a problem nobody has explored yet is how
a team builds a careful, expensive answer to the wrong question. For trivial tasks, use judgment.

---

## Explore the problem

Apply to any non-trivial analysis or proposal (designs, investigations, RFCs, debugging, planning,
architecture, reviews). This is framing discipline, not coding mechanics.

### A1. Reason from the system, not the artifact

Start from how the thing actually works in the architecture — what the data is, who writes it, who
reads it, how often, where the code runs — then locate the problem inside that. Do not structure
your analysis around a snippet you were handed or a "buggy" implementation; that produces
explanations that are hard to follow and quietly inherit the wrong frame. Lead with the
architecture; the bug is a symptom you place within it.

### A2. Start from observed behavior and the outcome you want

Begin with what the system does today and what somebody wants to be different — not with the change
you were handed. Go and look: reproduce it, read the data, watch the traffic. The requested change is
one person's hypothesis about how to get from the first to the second, and it is evidence about the
outcome, not a specification of it.
[`reading-before-changing`](../reading-before-changing/SKILL.md) lists the specific reads that most
often overturn the request.

### A3. Try more than one framing

Write down at least two problems the observed behavior could be: the one you were shown, and one
that deliberately moves the boundary — wider (the same failure exists in four other places) or
narrower (only this client, only this endpoint, only at month end). Most of the time the real problem
is not the size of the symptom presented, and a precise solution to the wrong-sized problem is still
wrong. Say what is explicitly out of scope once you have chosen.

### A4. Challenge the requirements that create the complexity

A constraint you were handed is an input to the design, not a law of physics. When satisfying one
forces substantial complexity — a new dependency, another service, a second copy of the data, a
standing operational burden — say so and ask whether it can be changed, narrowed, or dropped,
**before** building the machinery that honours it. Name who owns it and what the design costs with
and without it. Most expensive designs exist because nobody priced the constraint out loud, and the
owner is usually willing to relax a requirement they never knew was expensive.

### A5. Generate alternatives, then choose

Put two or three real candidates on the table, including the boring one and the one that does
nothing. A single option presented with supporting reasons is advocacy, not a decision, and it hides
the fact that no exploration happened. Do not silently pick between materially different
interpretations or designs.

### A6. Learn by cheap experiment; prove claims rather than asserting them

Prefer the smallest thing that produces evidence — a query, a spike, a measurement, a prototype you
intend to throw away — over more argument. Replace assertions ("this is O(n²)", "this is faster",
"this is cheaper") with data. If you cannot prove it yet, say so explicitly, label it a hypothesis,
and state the experiment that would confirm or kill it. Be willing to conclude your favored idea is
wrong; that is the cheap outcome.

---

## Converge on the design

These narrow the field once the problem is understood. They are tiebreakers for choosing between
explored options — not the posture to open with.

### A7. Make it work and prove it useful before making it fast

Build the simplest thing that satisfies the demonstrated need, get it working, and show somebody
wants it. Optimization, caching, precomputation, and generalization are earned by a measurement on a
running system, not predicted before one exists. Premature optimization is by far the more common
failure: it buys speed nobody asked for at a cost paid on every write and every byte thereafter, to
serve a read that may almost never happen. When you do reach for it, make the recommendation
conditional on the numbers — the read/write ratio, the access frequency — and say what would change
the conclusion.

### A8. Simplicity is the default; complexity is what needs the argument

Prefer the simplest design that satisfies demonstrated needs. Avoid speculative flexibility,
configurability, and abstractions; complexity must solve a concrete problem before it earns a place.
Count the whole cost of what you are proposing to keep — maintenance, deployment, observability,
failure modes, and the eventual migration away from it — not only the effort to write it. A design
that is cheap to build and expensive to operate has not been costed.

### A9. Say where the design stops working

Name the limits that would break it — data size, memory, concurrency, latency, blast radius on
shared resources — and where they bite, rather than pre-building for a scale you have not reached.
"It fails above 10 million rows, which is 100× today's volume" is a finished answer, and so is "we
revisit at 1 million". "Load it all into memory" is only a non-starter once the input is known to be
unbounded, so go and find out which it is.

### A10. Prefer reversible decisions; escalate the irreversible

Sort choices by how hard they are to undo, not by how hard they are to make. A reversible decision
made quickly and corrected later is cheaper than a slow consensus you cannot walk back. So bias to
action on the reversible ones — and stop and escalate before implementing the rest: anything
architectural, externally visible, or one-way. A published name, a schema, an API shape, a data
migration, and a new service are all one-way doors. Raise those before the code exists, when the
cost of changing course is still a conversation.

### A11. Record what you rejected, not only what you chose

The reasons an option was discarded are the expensive part of the thinking, and they are the part
that gets lost. Put the constraints, the alternatives considered, and why each lost in the pull
request or the ticket. Without that, the next person re-derives the same dead end, or worse, "fixes"
your design by adopting the option you already ruled out. A decision recorded without its rejected
alternatives reads as arbitrary six months later — including to you.

---

## How to apply

When producing a design, investigation, or recommendation, sanity-check it against this file before
sharing. Did you look at the real behavior, or only at the request (A2)? Is there a second framing
you can name, and alternatives you actually considered (A3, A5)? If the design is elaborate, find the
requirement forcing the elaboration and price it out loud (A4) before defending the machinery. If you
are asserting a cost, a speedup, or a scaling claim without evidence, get the evidence or mark it a
hypothesis with a way to test it (A6). If you are optimizing something that does not work yet, stop
(A7). If any part of it is a one-way door, raise that before you build it (A10). Before
implementation begins, state your assumptions and define the behavior and evidence that will prove
the work complete. Then apply [`coding-principles`](../coding-principles/SKILL.md).
