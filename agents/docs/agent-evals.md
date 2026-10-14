# Agent evals: measurement gates and blind tests

Read this before you publish any number produced by driving an AI assistant or agent (a tool-call
count, an eval result, an A/B arm, an adoption share), and before you run a blind test of a skill.
The failure mode is not a wrong answer. It is a plausible one that looks like data.

Companion to [`evidence-integrity`](../.agents/rules/evidence-integrity.mdc): that rule says
recompute rather than carry forward, and this doc says to point the computation at the right thing.

## The five measurement gates

### 1. Name the scope, and treat zero tool calls as a scoping failure

An assistant that serves many tenants is not scoped by the harness that drives it. If the prompt
text does not name the tenant or account, it asks which one is meant, reaches no tool, and returns
a well-formed response that a harness records as a success.

- Name the scope in every programmatic prompt.
- A zero-tool-call answer is a harness defect, not a data point or a cheap answer.
- A run where most questions reached no tool measures nothing. Do not average it.

Measured: 13 questions without the account gave 2.15 tool calls per question (9 of 13 reached no
tool). The same 13 naming it gave 22.69.

### 2. A green check on an eval pull request is not evidence that its evals passed

Eval shards may be non-blocking. A shard reports `success` while cases fail inside it. Read the
shard log before you claim an eval passes:

```bash
gh run view --repo <owner>/<repo> --job <job-id> --log | grep -E "FAILED|passed,"
```

### 3. Gate on a deterministic assertion, not a borderline judge

A judge that scores near its threshold is a coin toss. One criterion scored 0.43, then passed, then
0.69 against a 0.7 threshold on unchanged behavior.

- Gate the claim under test on something deterministic, for example a string the answer must or must
  not contain. Keep the judge for the qualitative axis.
- If a judge criterion is worth keeping but the agent does not meet it, disable the case with the
  measured score written down. Do not leave CI knowingly red, and do not quietly delete the standard.

### 4. Compare arms only on equal denominators

A question that returns no answer adds no tool calls, so an arm's total and mean are over the
answered questions, not the asked ones. `227/12` beside `295/13` reads as a 23% improvement that did
not happen.

- Report the answered count per arm.
- Never divide by the asked count to make the columns line up.

### 5. A rehearsal must not be able to overwrite a real result

Dry-run output goes to its own path. A rehearsal once wrote 25 receipts over a fleet's namespace, and a
real install replaced one of them a minute later.

### Forbidden

- A tool-call or cost figure from a run whose prompts did not name the scope.
- Averaging a run in which questions returned zero tool calls, or counting those as cheap answers.
- "The evals passed" from a green check rather than the shard log.
- Gating CI on a judge criterion measured near its threshold.
- Comparing arm totals or means across different answered counts without saying so.
- A dry run and a real run that share an output path.

Source: one fleet-wide rollout of a per-tenant configuration, measured end to end.

## Blind skill tests

A blind test checks that a skill guides an agent from an **initial prompt** to a **target
conclusion** (for example, "run the reporter's question and reach what the expert concluded"). The
agent must not load the answer key first.

### Forbidden during a blind run

1. Resolving the source chat thread that holds the engineering analysis.
2. Reading prior write-ups for the same incident (gold-standard docs, run-throughs that embed the
   expert's conclusions) before the blind run is complete.
3. Institutional-context queries framed on the specific incident so that the thread or ticket
   write-up comes back as the answer (for example "What did the expert say about this customer in
   April 2026?").
4. Presenting thread-informed findings as if they came only from the product's API, the log system
   or other tool calls.

### Allowed

- The verbatim input the user specified: alert text, error snippet, and admin-interface or
  notification URLs in the prompt. These are first-class inputs.
- Skill-directed tools: the product's API or MCP, the metrics system, reports, direct API calls
  with a scoped token.
- Code and history research grounded in stack traces and class names, not in the incident narrative.
  For example: "What recent changes were made to `PersonShareBuilderImpl`?"
- Resolving a commit or PR URL, but only after you found that URL through git history, the
  institutional-context tool or GitHub search, not from the thread.

### After the blind run

Compare the blind run to the reference analysis in a separate step labeled "review vs reference",
then update the skill. Do not merge review conclusions into the blind run log as if tools produced
them.
