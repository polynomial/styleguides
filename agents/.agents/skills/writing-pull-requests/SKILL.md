---
name: writing-pull-requests
description: MUST USE when writing a pull request's title or body, and after pushing to a branch with an open pull request.
---

# Writing pull requests

## Voice

The body must follow ASD-STE100 Simplified Technical English. [`simple-english`](../simple-english/SKILL.md) owns those rules, and the sentence caps in it apply here. Two more are specific to a PR body:

- Break the text often, with a line break, a bullet, or a heading, so a reviewer can scan it.
- The body renders as GitHub Flavored Markdown. Write each sentence on one line. Do not break a sentence across lines.

## Purpose

A PR body tells the reviewer **what to click** and **what to check**. It is not a record of how the change was made. The commits, the diff, and the ticket hold that better.

**The repository's own PR template goes at the top of the body.** The repo you open the PR against owns that template. Keep its fields and its wording. The sections below follow it. If the template also prescribes headings, the template wins for those.

## Pull request title

The pull request's own title says what a merge does. It is not a section in the body. A squash merge makes it the commit subject.

- Write one imperative phrase, as in "Cap the email webapp's young generation at 2500M".
- Aim for 50 characters, and do not go over 72. A ticket prefix counts.
- Do not end the title with a period.

## Sections

Why, Approach, Proof or Status: blocked, and Risks are mandatory, in this order. A TL;DR goes before Why only when the pull request title is not enough.

Keep each section to what a reviewer needs to act on, and keep the body to one screen. Risks may run as long as the risks require, because a change carries the risks it carries.

### TL;DR

Add it under a `## TL;DR` heading when the pull request title does not tell a reader what they need from a merge:

- The reviewer must make a decision.
- The Proof section is `Status: blocked`.
- The change has an effect that the title cannot hold, such as a removed endpoint or a changed default.

Write one or two sentences, and 50 words or fewer. Say what the title cannot, and do not repeat the title. Do not list files, tests, or links, because those go in Approach and Proof.

For example, under the title "Remove the v1 webhook endpoints": "No client called them in the last 90 days, so this removes them with no deprecation period. Confirm that no partner integration still uses them."

### Why

This follows Minto's SCR (Situation-Complication-Resolution) framework:

- **Situation:** State where things stand today. Assume the reader has no context. Give the facts they need to accept the problem.
- **Complication:** State the problem, not raw data.
- **Resolution:** What the change does about it. Answer first, reasoning second.

Name the one type or component the change is about, and no more. The file list belongs in Approach.

Do not:
- Retell how you found the problem. That is history, not situation.
- Present evidence without naming the problem. "Latency p99 is 4s" is data. "Users hit timeouts on every retry" is a complication.
- Bury the fix under context. Lead with the resolution.

### Approach

State the technical solution first. Say what the change does, and why this solution and not the one a reviewer expects. Google's CL description guide calls this the what and the why.

Then give the reading route. Say which files carry the change, where the reading starts, and what the reviewer can skip.

A small or obvious change gets one sentence of solution and no reading route. Name the files, do not describe them.

### Proof, or Status: blocked

The build decides which of the two you write. A branch that builds gives proof. A branch that does not build gives a section headed `Status: blocked` in its place, and the pull request goes to draft. A failing test blocks the same way.

**Proof.** Give the name and result of a test. A CI link, a screenshot, or a preview URL also works.

Name the test. Do not write the command that runs it, and do not list build steps.

**Status: blocked.** The reviewer needs to know what is broken and where, not how broken it is.

Give one bullet for each defect, and one line for each bullet. Name the file and the symbol.

When one defect spans more than three files, give the directory and the count. Do not list the files.

Link the failed CI run. Do not paste an error, and do not explain one.

Close with the names of the tests that will prove the change once the defects clear.

### Risks

A risk is what breaks in production if the change is wrong. It is not the state of the branch. A `Status: blocked` section above does not remove a risk from this one.

Look for these risks first:

- Regression for a caller or a client that already uses the code you changed.
- A rolling deploy that serves the old code and the new code at the same time.

Give each surviving risk a bold label, then four bullets under it:

```
- **Short label.**
  - What exists today that the change touches.
  - How the change alters that state.
  - What breaks if the change is wrong.
  - What the reviewer must verify.
```

Write the four bullets in that order. Do not label them. The order combines two established frameworks. The SEI/CMU risk statement gives "If [condition], then [consequence], because [cause]". FMEA gives what can fail, how it fails, and what happens when it does.

Name the specific file, field, or line in the fourth bullet. "Confirm nothing is wrong" is not a check.

A risk you checked and ruled out gets one line: what you checked, and what proves the change safe. That line is a finding for the reviewer, not a note about your own review.

## Before you open it

These five apply when you open the pull request. Skip them when you only rewrite the body.

1. Verify that the branch is not the default branch. The branch name must follow the repository's own branch naming convention.
2. Run `git fetch origin`. Verify that the branch is not behind the remote default branch.
3. Run `git status` and inspect the full diff. Verify that all changes are part of the requested work.
4. Run the repo's pre-commit and pre-push checks. Verify that they pass.
5. Verify that the user asked for the pull request. Pushing finished commits is the default, per [`verify-before-complete`](../verify-before-complete/SKILL.md).

## After every push

Compare the title and the body with `git diff <base>...HEAD`. Rewrite the title if it does not name what the branch does now. Update each section that the push made wrong, Proof included, and leave the others. If both still match, change nothing.

Edit the pull request. Do not post a comment in its place.

## What does not belong in the body

- The session's history: what you tried, what you corrected, or what a ticket said before you corrected it.
- The self-review pass. Do the review. Do not narrate it. A finding that changes where a reviewer must look belongs in Risks.
- A narration of the diff: which files moved, which classes changed, which imports were added.
- Another repo's template.
- **A closing keyword before a link.** `fix <link>` closes that PR on merge. Write `opened as <link>` or put the reference in a code span. Always-on rule: [`github-closing-keywords`](../../rules/github-closing-keywords.mdc).

## Composes with

- [`simple-english`](../simple-english/SKILL.md): the sentence rules, the word choice, and the self-check for every engineer-facing text.
- [`pr-comment-merge-policy`](../pr-comment-merge-policy/SKILL.md): review replies, attribution, the automated reviewer, merge gate.
- [`verify-before-complete`](../verify-before-complete/SKILL.md): the closing self-eval goes in your message to the user, not in the PR body.
- [`sub-repo-agents-md`](../../rules/sub-repo-agents-md.mdc): which repo's template applies.
