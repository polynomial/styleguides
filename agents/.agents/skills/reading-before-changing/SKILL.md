---
name: reading-before-changing
description: The concrete checks to run before scoping a code change, changing a limit or default, reviewing a proposed plan, or claiming a change works — each one a read of the system that regularly overturns a request's premise. Use before designing any backend change in any repository, before answering "can the API return X" or "we do not record Y", before endorsing a list of endpoints or an incident plan, and before reporting a fix as done. Repository-specific traps live in that repository's own skills; this skill carries only what is true of any codebase.
---

# Reading before changing

[`behavioral-guidelines`](../behavioral-guidelines/SKILL.md) says to start from observed
behaviour rather than the request. These are the reads that do that, collected from changes where
skipping one produced a wrong design, a wrong answer, or a wrong "done". Each is one check. Run the
ones whose trigger matches. None needs a separate report; what a check changes about the design
still goes in the pull request.

## Before you scope the change

- **Check whether the capability already exists and is switched off.** A request to enable
  something for a new class of thing (an account type, an environment, a plan tier) usually names
  a capability that exists behind a hardcoded allowlist of two or three values. Measure it across
  every existing class first. The change is then "stop keying on the class", and there is often an
  older ticket asking for exactly that.
- **Find the workaround people use today.** It is load-bearing, and the new class silently breaks
  it. Check whether that same workaround caused the incident you were sent to fix.
- **Treat "I tried the obvious control and it did nothing" as a claim to check, not a user error.**
  Open the method the failing rule calls and confirm it reads what the control writes. Two sibling
  methods in one class that answer the same question by different paths is the fastest tell.
- **Two people describing different symptoms may be two bugs, not a disagreement to settle.**
  Enumerate the conditions guarding the broken line and check each reported symptom against them
  before deciding how many bugs you have.
- **Before adding a field to a persisted record, find what the record is projected onto.** Grep for
  the class name and read every producer, relay and stream that carries it. A database column
  accepts a megabyte of base64; a message-bus record does not, and nothing in the type says so.
- **"We do not record X" is a claim about projection, not storage.** Before asking for a capture
  path, grep the persistence layer for the raw payload X arrives in. A server that stores a request
  or registration whole already has the field; the work is a read of a row that exists.
- **Before moving onto an endpoint, read its controller, not only the reference client.** The
  client shows the happy path; the controller shows the authorization and error paths the client
  never exercises, and those change the design. Confirm the route is live in production by finding
  a live caller using it; a 401 from an unknown path proves nothing when authentication runs before
  routing.
- **Read the existing tests over the code before changing a line of it.** A test written from
  observed behaviour asserts the bug and keeps it policy. Changing that assertion is right; say in
  the pull request that the test asserted the old behaviour and why the new assertion is correct.
- **Before changing how one implementation of a shared method behaves, read every implementation
  and every caller.** An interface method is often implemented once per layer (a REST builder, a
  JavaScript builder, a context API builder), and a guard present in one and absent in another is
  the defect, not the convention. Count the guards where the value is forwarded, not where the
  setter stores it, and keep a guard only where the value genuinely cannot arrive empty on
  purpose.
- **When a value is computed in more than one layer, check every layer before answering.** A
  derived value is often computed in the API model, in the server's own context and in the client,
  and usually one layer lacks the fallback the others have. Before returning a derived value in a
  nullable field, find what writes the field back: a writable field stores the derived value as
  real on the next save. Prefer a separate read-only field.
- **Copy a precedent's shape, not its write site.** Ask when your value first exists in the request
  lifecycle; a sibling written at bootstrap was written there only because it was known then.
  Writing at the wrong site records nothing with every test green. Say in the pull request why your
  write site differs from the pattern you were told to follow.
- **Enum additions have hand-written twins.** Grep for an existing member of the enum: workflow
  `choice` inputs, CLI argument maps, curated value sets. Each compiles fine and silently never
  offers the new value. Pin the enum and each list together with a test, and assert deliberate
  absences so the next reader knows someone looked.
- **When asked to make every sibling behave like X, census the siblings first.** One that already
  half-implements X is your control: it proves X was intended, and its rows are the ones that must
  not move in your before/after matrix.
- **A setting whose display name matches the words on the page may be read in only one arm of a
  template conditional.** Before writing to it, open the template and read the `if`/`else` around
  the variable, and prove with live data which arm real traffic takes.
- **A matching name is circumstantial; matching contents are not.** Prove an artifact is the one on
  the reported screen by the variables it passes, not by its name.
- **When a report carries a deep link, the ids in that URL name the record the reporter was looking
  at.** Fetch that record and compare it with a healthy sibling of the same type before reading the
  code that edits it. "My edit does not render" is a data question first and a code question second.
- **Before concluding an endpoint refuses a request, send it exactly as the real client sends it.**
  Copy the client's full request shape from its code: the body it sends or omits, and every query
  parameter of its request object, not only the ones the mechanism is about. A missing parameter
  returns a smaller result set, not an error. Treat a 400 you provoked as your bug until the
  client's exact request also fails.
- **The screen is a form over an endpoint.** Before handing work back as someone else's job, open
  the page that does it and read its service module; the request it sends is the specification of
  the work.
- **A control that is always disabled, empty or uneditable usually reads a field the endpoint never
  returns.** Call the endpoint for several records and grep the server for the field name before
  reading the component. Before deleting a dead check, ask whether the rule it enforced lives
  elsewhere, and say "this gate lives somewhere else", not "this gate was pointless". Read the save
  payload in the same pass: omitting a field on a partial update means unchanged, and clearing it
  takes an explicit null.
- **When a locked control's tooltip names who may act, verify that the gate implements that
  policy.** A gate that is a hand-maintained list of ids rots with nothing failing; date it with
  `git log -S` on one entry and replace it with the access model the page already uses.
- **Before building on a field seen in one response, fetch the same record over the other
  transport.** A snapshot endpoint and an event feed can name the same payload differently, and the
  type checker cannot see across that seam. When a picker silently omits a row, grep the fetch for
  `allSettled` or another swallowed rejection before looking for a filter.
- **A client's parameter types are a hand-maintained subset of the server's.** Read the server's
  request class before concluding a filter does not exist. Prove a declared parameter live by
  checking that every returned row matches it, and measure the unfiltered result before adding one.

## Before you change a limit, default or configuration value

- **An unset property is not an absent bound.** In Spring the live default is in the
  `@Value("${key:default}")` that reads it; grep the source tree for the property name, not only the
  resource files, before saying a timeout, limit or flag is missing.
- **The number in the config file is not the number that binds.** Find what counts the thing and
  what owns the counter: an in-process counter is scoped to the process that holds it, which may be
  one task of many behind the same load balancer. Then name both places the number
  could move, a code default (a deploy) and an environment variable in the service's infrastructure
  (an apply), and check for an existing override before saying which.
- **Removing a default applied at read time changes every record written without it.** Sweep the
  stored records first. Stored records often hold the effective value, defaults included, so they
  say nothing about what callers actually sent; say so rather than implying the sweep covered it.
- **Before designing a validation that would have prevented an incident, read the operation log.**
  If the existing check already fired and an operator overrode it, the fix is a check the existing
  override cannot clear, on its own axis with its own override, not another check under the same
  flag.

## Before you endorse a plan or a list

- **A proposed list of endpoints or hostnames is checked by calling every one.** A wildcard DNS
  record makes an unbuilt name answer, which removes the only "not deployed yet" signal. Read each
  service's own limits; the cap that bites is server-side and scoped differently from the one the
  browser test measured.
- **A load-incident plan is judged on whether it bounds the amplifier or the admission.** Read the
  ingress yourself: what created the work, and does the ingress already have a dedupe mechanism it
  is not using for this path? Check the plan's stated cause in the code before endorsing a plan
  built on it.
- **A ticket that asks for prose can ask you to publish something false.** Verify the behaviour in
  the implementation before writing documentation or API copy. When one rule generates copy onto
  many targets, simulate it over the whole corpus and read every output first; derive the sentence
  from something machine-checkable rather than asserting it.
- **Before proposing an alert on a missing value, measure how many live records lack it.** Absence
  is often the norm, and an alert on it pages the whole estate on day one. Read the code that
  enforces the value before naming a threshold; only the enforcer says whether absence is a state or
  a preference. A guarded step that fires proves the values in its guard exist and nothing more, so
  date the values before treating a firing alert as proof that a capture path is still live.

## Before you say it works

- **When a change feeds a generated artifact, diff the artifact, not only the source.** Generate it
  at the base and head revisions from explicit checkouts (two worktrees, not `git stash`, which is a
  no-op once the change is committed) and compare every object. A generator with conditional logic
  removes things your diff never mentions. Report counts over an identical set. Build the baseline
  in a detached worktree at the parent commit (`git worktree add --detach <dir> <parent-sha>`),
  share one dependency install by symlinking it in, and never edit the working tree while the
  baseline builds; a diff where a line you just added appears on both sides is a contaminated
  baseline.
- **A generated artifact is not a published one.** The consumer's own script, the workflow that
  copies the artifact onward, is the authority on what ships. Read it before trusting the document
  that describes the artifact.
- **Merged is not deployed.** Find the deploy run, or submit the smallest real job that exercises
  the changed path and read its result.
- **Separate "the query is wrong" from "the records are older than the code" by varying only the
  time window.** Hold everything else constant. Date the code with `git log -S<symbol>` and blame
  the guard line rather than the setter. On a shallow clone both commands return plausible wrong
  answers, so deepen it first.
- **A recommended index is a hypothesis about selectivity and plan choice.** Measure the plan and
  its timing on the same engine version against the real value distribution before shipping; the
  optimizer can pick the index where it loses. Prove a query rewrite by running old and new over
  identical data and diffing the result sets both ways.
- **When the suite that would prove the fix cannot run where you are, put the negative control
  inside the test.** Assert the broken behaviour on the same subject immediately before asserting
  the fixed one; without it, a green run passes with the bug intact.
- **A green build proves nothing about a build-time construct.** Preprocessors pass what they do not
  recognise through as literal text. After introducing one, grep the emitted artifact for the
  construct's own name; anything that survives was never compiled. Audit the artifact for the
  property you claim to have fixed, not the source. When one mode, locale or client must stay
  untouched, build the artifact at your commit and at its parent, normalise away the wrapper you
  introduced, and diff every declaration.
- **A fetched artifact is source, not execution.** Reading a bundle tells you which filter and which
  list are live; a branch that depends on the runtime (`isMobile()`, a feature probe) is proven only
  by running it. Say which half of the answer is inference.
- **When an element is installed in several places, enumerate every match** and report each with
  where it sits. A loop that keeps the first or last match reports the wrong state for the one the
  reader is looking at.
- **Prove a one-field write by diffing the whole flattened record before and after.** Expect exactly
  the change you named plus the record's own version bump. Reading the field back proves only that
  field, and "the thing asked about works" is a different claim from "nothing else changes". When
  writing up a change already made, re-derive each step from the code rather than transcribing the
  earlier answer.
- **When a write must not go live, read the published version's own timestamp afterwards**, not the
  draft's, and confirm it did not move.
- **An md5 match on an upload proves the transfer, not the bytes.** Render the stored file from the
  content endpoint and assert its shape before trusting the receipt.

### When the check is a harness you built

- **When no test renders the code you changed, build the render check yourself.** Bundle the real
  module with the repo's own bundler, stub its services, render it, and read the output back. Run
  the identical harness at HEAD and at `git show origin/master:<path>` and diff the two.
  Byte-identical output apart from the one intended difference is proof. A difference that also
  appears in the master arm is a pre-existing quirk, not a regression; do not fix it.
- **A layout claim needs a real browser, not jsdom.** Measure items per row, wrapping, column width
  and overflow in both arms at a sweep of real viewport widths, including the tablet band a single
  desktop viewport misses. Use probes, not eyes: `scrollWidth - innerWidth` for horizontal
  overflow, and `elementFromPoint` at the edge walked up to the first painted background for
  edge-to-edge claims. Prove the candidate fix in the same run with `page.addStyleTag` and confirm
  no other box moved. What jsdom cannot see includes a fixed-size control whose flex track shrinks
  to fit a narrow cell.
- **Every literal a comparison harness reads comes from the build under test, never typed.** Class
  names, scope attributes, custom-property names, values and markup are all things your diff can
  change, and a hardcoded one reports "unchanged" in both arms, which is also what a probe that
  matched nothing reports. Grep the emitted output for each identifier before probing, assert that
  a harness substitution matched, and never supply in the fixture a value the before arm should be
  measuring. Make the harness print a loud marker such as `NO RULE IN BUILD` and stop when it
  cannot place a probe; then decide whether the probe or the file is wrong.
- **Before editing a component for a shared fix, confirm something imports it.** A file nobody
  imports emits nothing, and the edit does not ship. Shared CSS added for a new control reaches
  every caller regardless of the prop that shows it, so measure every caller in both prop states, in
  both builds. Diff geometry relative to the component's own box, not page coordinates, and cluster
  children into flex lines by vertical overlap rather than by distinct `top` values. Assert your
  stub fired before reading anything else from the run: a control missing from every arm looks like
  a disabled feature, not a dead stub.
- **Read every number against the feature's purpose, not against the declaration you wrote.**
  `overflow: auto` working is good news only when the content is meant to scroll; for a snippet a
  person copies, a `scrollWidth` above the client width is clipping. A probe that confirms your CSS
  did what you typed is not a probe that the screen is usable. Re-measure at several real widths
  against the parent commit.
- **Drive the failure arm.** A happy-path run cannot see an optimistic success message; the tell in
  the source is state written beside a call rather than after its result. Add the failing arm to the
  stub's contract from the start, assert the prompt stays open and the success message is absent,
  then flip it back and assert the retry lands.
- **A harness negative about a timed behaviour is your own settle window until proved otherwise.**
  Grep the component library for delay defaults on whatever you drove (`hideAfter`, `showAfter`,
  transition durations) and make the settle window several times the largest. Never print a bare
  count of something the test can confuse; print what you counted.
- **Count `node_modules` before the first grep into a package or the first gate in a handed
  checkout.** If `ls node_modules | wc -l` is 0, run `npm ci`: an empty install makes every
  dependency probe a false negative and lets `npx` install an unrelated package of the same name.
  Run probes from inside the project, because resolution starts from the working directory. A gate
  then fails with exit 127 (`command not found`), not a dependency error, and a wrapper
  (`cmd > log; echo exit=$?; tail log`) reports the wrapper's status; read the gate's own exit code
  from its log.

## Composes with

- [`behavioral-guidelines`](../behavioral-guidelines/SKILL.md) — the reasoning discipline these
  checks serve.
- [`evidence-before-changing-code`](../evidence-before-changing-code/SKILL.md) — the history check
  before restoring anything a report implies is missing.
- [`root-cause-proof`](../root-cause-proof/SKILL.md) — the proof bar before naming a cause; the
  last section here is its fixing-side counterpart.
- [`coding-principles`](../coding-principles/SKILL.md) §7 — tests that can disprove the change.
