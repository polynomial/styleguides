# Declarations and manifests: decisions only, never runtime facts

Use this before you propose a file that someone must keep true: a manifest, a registry entry, a
governance declaration, a service catalog row, a config surface.

**The rule:** a declaration holds only what a person decided. Anything the system knows when it runs
(provider, model, version, principal, endpoint, deployed revision, timestamp, what it touched, what
it produced) goes in the record the system emits. A hand-maintained copy of a runtime fact will
drift, and a drifted declaration is worse than none, because it is evidence of a control that is
not operating.

## The three gates

Run all three before you add the artifact.

### 1. Prove no existing artifact already carries it

Find where the target repository already keeps this kind of information: its docs home, config
layer, log destination, or an existing registry. Search in the target repository's conventions, not
this one's. A new format beside an old one splits the answer in two, and people keep reading the
old one. "There is no existing pattern" is a claim you prove with a search.

### 2. Name what reads it

State the consumer in the pull request: the validator, the CI check, the collector, the dashboard,
or the person and the moment they open it. A destination that is written and never read is cost,
not capability. If the only honest answer is "nothing yet, but once N repositories carry it", ship
the consumer with it or do not ship the artifact.

### 3. Put every field on the right side

| The field is | Where it goes |
|---|---|
| something a person decided and will change deliberately | the declaration |
| something the system knows at run time | the emitted record |
| something derivable from either | neither — derive it |

If most fields land in the second row, the artifact is a log. Add emission instead of a file.

## Your open questions are your decisions

A pull request that asks the reviewer "should this be validated in CI?", "is this the right
location?", or "does this belong here at all?" has passed its own design to the reviewer. The author
can answer those with the tools in hand. If the answer is not known yet, the artifact is not ready.

Open questions are for real scope forks a reviewer must decide: a trade-off between two defensible
designs, or policy the author does not own. They are not for the choices the change is made of.

## Forbidden

- Adding a manifest, registry or schema without naming what reads it.
- A hand-maintained field that restates a fact the running system emits: model version, provider,
  principal, deployed revision, last-run time.
- A new declaration format where the repository's docs, config layer or log destination already
  carries that information, without proving it does not.
- A pull request whose open questions are the design decisions the change embodies.
- A `.sample` or template file with no filled instance and nothing that validates it.

## Reference case

One pull request added a root `agent.yaml` that held model provider, name and version that the
operation record already emitted, had no reader, and asked three open questions the review then
rejected. The fix kept the declaration as prose in a governance doc (purpose and owner, data use,
behavior, human controls, operational safeguards) and moved provider, model, version, prompt and
skill versions, tools and outcome into the per-run operation record.

## Related

- [`architecture-assessment-evidence`](../../.agents/skills/architecture-assessment-evidence/SKILL.md):
  the same consumer test, applied to scoring a component.
