---
name: prove-it-on-a-second-input
description: Before publishing numbers from an analysis script, a report, a parser or any read-only code that reads a dataset, run it unchanged against a second dataset of the same kind. Use when a script has only ever run on the data it was written against -- one client, one vertical, one environment, one account, one file -- and its output is about to be quoted in a write-up, a PR, a ticket or a deck. The second run is a test, not a bonus analysis: code written against one dataset silently hardcodes it, and a number that has never moved has never been checked. For code that writes, see the Writable workloads section before running anything twice.
---

# Prove it on a second input

## Gate

**A script that has only ever run against one dataset is untested, however carefully it was written
and however plausible its output. Before its numbers are published, run it unchanged against a
second dataset of the same kind and read the output.**

The point is not to analyse the second dataset. The point is that the first dataset's peculiarities
are invisible while it is the only one: every assumption the code makes about it is satisfied by
construction, so nothing fails, nothing warns, and the output looks exactly as right as it would if
the code were correct.

## What the second run finds that review does not

Reading your own code does not surface these, because reading confirms the code does what you meant.
A second input asks whether what you meant was about the data or about *this* data.

| Defect | How it looks on one dataset | How the second run surfaces it |
|---|---|---|
| A filter hardcoded to the first dataset | correct results | wrong population, usually a familiar count in the wrong run |
| A computed number frozen into prose | correct sentence | the first dataset's number printed under the second's table |
| A lookup keyed on names only the first dataset uses | high coverage | a large unclassified bucket |
| A cohort, threshold or category chosen for the first dataset | a populated cohort | an empty one, often an `IndexError` |
| A label naming the first dataset | accurate heading | "58 banking clients" above 80 retail ones |
| A branch never taken | no error | a division by zero on an empty group |

## Procedure

1. **Name the second input before you start**, and pick a real one, not a copy of the first with a
   value changed. Another client, another vertical, another environment, another month, another
   account, the same report at a different window. It has to be able to disagree.
2. **Make the input a parameter, not an edit.** If running on the second dataset means changing a
   constant in the file, the parameter is missing and that is itself the first defect found. Scope
   the paths it reads and writes too, so the second run cannot overwrite the first's results --
   that is how a rehearsal destroys a real receipt.
3. **Run it unchanged and read every line of output**, not the exit code. Most of these defects exit
   zero. **A figure identical across two genuinely different datasets is a prompt to look, not a
   verdict**: check which paths the run actually read and how the figure is computed before calling
   it hardcoded, because some quantities really are invariant -- a schema's column count, a fixed
   threshold, a rate that happens to match. What identical output never is, is confirmation. Two runs
   agreeing tells you nothing until you know they read different bytes.
4. **Fix what it finds in the code**, not in the second run's output, then **re-run both datasets**
   and compare each against its published numbers. Both, because the fix changes the second dataset's
   result too and step 5 is about to report it: a figure produced by the pre-fix code is not the one
   the corrected code gives, and a regression the fix introduced on the second dataset is invisible if
   only the first is re-run. Movement is expected when the fix corrects the
   computation: a rule table that was matching only the first dataset's spellings will reclassify
   some of the first dataset's rows too, and that is the fix working. What matters is that **every
   difference is explained and the publication is updated to the corrected figure** -- name it as a
   correction rather than letting a number quietly change. Movement you cannot explain is the second
   defect, and it is the one most likely to reach a reader. Iterate: a fix that surfaces a new defect
   on either dataset sends you back to step 3.
5. **Say what the second run showed.** If the numbers differ, the difference is a result and belongs
   in the write-up -- it is often the most interesting thing the exercise produces. If they agree,
   say that too, and say it carefully: having confirmed in step 3 that the two runs read different
   data, agreement is *weak* evidence the first result was about the world rather than about the
   file. It is weak because two datasets can share the same defect, the same upstream producer or the
   same template. Two is better than one and it is not many.

## Writable workloads

Everything above assumes the code only reads. A migration, a backfill, a repair script or anything
else that writes cannot simply be run twice, and "run it on production's other tenant to see what
happens" is how a test becomes an incident.

For those, the same idea holds and the mechanics change: point the second run at an **isolated,
disposable copy** of the second dataset, use the tool's dry-run or plan mode first and read the plan,
and prove **idempotence** -- running it twice leaves the same state -- before it touches anything
shared. If none of that is available, this skill does not apply and the honest statement is that the
code has been exercised against one dataset only.

## When this does not apply

- One-off exploration whose numbers nobody will quote.
- Code whose input genuinely has one instance -- a single production cluster, a named account -- where
  the honest move is to say the result is about that instance and not to generalise from it.
- A second run that would cost real money or real time against a shared resource. Then say so, and say
  what remains unverified, rather than presenting a single-input result as though it had been tested.

## Forbidden

- Publishing numbers from a script that has only ever read one dataset, without saying so.
- Treating a clean exit on the second run as the check. The output is the check.
- Fixing a defect the second run found only in the second run's path, leaving the first run's code
  carrying it.
- Letting the second run write over the first run's cache, extracts or outputs.

## Why this exists

Added 2026-09-13, from the groundwork of a two-vertical analysis project. Four analysis scripts were
written and reviewed against one vertical's data -- 58 banking clients -- and every number they
produced was published. Running them unchanged against the 80 retail clients, which the work had
already recommended as the next step, found **six** defects in an afternoon:

- The vocabulary pull had `v.value='banking'` inside its legacy SQL, so the "retail" pull silently
  returned 634 banking campaigns across 58 banking clients and wrote them into the retail cache.
  Nothing failed.
- The launch catalogue hardcoded one program type as the cohort. Retail has zero adoptions of it;
  the script raised `IndexError` three sections into a run that had already printed a page of
  correct-looking output.
- The declared-allocation script printed "the weekly split wanders 6.7, 67.0 and 95.7 points" as
  literal prose -- banking's three numbers, under retail's table.
- The same script quoted "precision somewhere between 1% and 36%", again banking's bounds, for a
  vertical whose bounds are 2.4% and 72%.
- The campaign-purpose script matched sweepstakes by exact step name against banking's vocabulary.
  Retail spells that step differently, so 38 of its 50 sweepstakes campaigns landed in
  `unclassified` -- a gap that looked like a property of retail and was a property of the rule table.
- Two scripts read the package's bundled data directory instead of the run's data directory, so the
  second vertical's run read the first vertical's extracts and reported its pairs.

None of these is subtle in hindsight and none was visible in review. They were visible in about
twenty minutes of running the same code on different rows.

The second run also changed a published conclusion, which is the argument for doing it even when the
code is right: banking has **one** clean A/B test in three years, and the write-up said so in terms
that read as a statement about the platform. Retail has **31**. The finding was about credit unions,
not about the platform, and a single-vertical run could not tell the difference.

## Composes with

- [`evidence-integrity`](../../rules/evidence-integrity.mdc)
  -- a frozen number is the defect this finds most often; that rule says numbers are computed, never
  carried forward, and this says how to catch the ones you carried anyway.
- [`verify-before-complete`](../verify-before-complete/SKILL.md) -- the closing gate. "Has this run on
  a second input" is a requirement to enumerate there, not a separate ritual.
- [`behavioral-guidelines`](../behavioral-guidelines/SKILL.md) -- "learn by cheap experiment". This is
  the cheapest experiment available to any analysis, and it is usually skipped because the first run
  already produced an answer.
