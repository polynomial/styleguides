---
name: linking-references
description: Must be read before writing text that names a pull request, a commit, a ticket, a repository, a chat thread, a document, a CI run, or a dashboard for another person to read, chat replies included.
---

# Linking references

A reader who sees `PROJ-1234` or "the plan in the design doc" must find the thing before they can check it. A link takes one click. A bare name takes a search, and on some surfaces no search finds it.

## Link the first mention

- Link each pull request, ticket, commit, repository, document, CI run, chat thread, and dashboard the first time the text names it.
- A progress update in chat is text another person reads. Link in it as you do in the final answer.
- Do not link the later mentions of the same target. The exception is a section that a reader can land on alone, such as Risks in a pull request body.
- Use the identifier or the title as the link text, as in `[PROJ-1234](https://tracker.example.com/browse/PROJ-1234)` or `[owner/repo#2096](https://github.com/owner/repo/pull/2096)`.
- Do not use "here", "this PR", "link", or a raw URL as the link text.
- Link what the reader needs to check or act on. A list of every source you read is not a reference.

A ticket key that a naming convention puts in a branch name, a commit subject, or a title prefix stays bare. It is a label there. Link the ticket in the body.

## Know what the surface links for you

Where the surface turns a short form into a link, the short form is the link. Everywhere else, write the link yourself.

| Surface | Links for you | Write the link yourself |
|---|---|---|
| GitHub pull request body, comment, review, issue | `#N`, `owner/repo#N`, a commit SHA, a bare URL | A ticket key. A repository has no autolink for the tracker's keys unless someone configured one, so `PROJ-1234` renders as plain text |
| Committed Markdown file | A bare URL | `#N`, `owner/repo#N`, a SHA, and a ticket key. GitHub autolinks them only in conversations. A file in the tree gets a relative link, per [`write-skill`](../write-skill/SKILL.md) » Link files relatively |
| The ticket tracker | An issue key on the same tracker | A GitHub reference. The link syntax depends on the write path, because the API and the editor can take different markup |
| Chat | A bare URL | A ticket key and `#N`. Use the chat tool's own link syntax, for example `<url\|text>` |
| A chat answer to the user | A bare URL | Everything else, as `[text](url)` |

Do not put a URL in a pull request title. Keep it in the body.

## Link only what you resolved

- Build a URL only from an identifier you read in a source, such as tool output, an API response, or the branch name. Do not guess a ticket number, a pull request number, or a path.
- A URL from a fixed pattern needs no extra check, for example a tracker browse URL from a key you read. A URL that you assemble from the parts of a UI route needs a check: open it, and verify that it lands on what you claim.
- If you cannot resolve a reference, put the name in a code span and say that you could not link it. Do not present an unresolved identifier as a link.

## Pick the link that stays correct

| Target | Link to |
|---|---|
| Lines of code, outside the repository's own files | A GitHub blob URL pinned to a commit SHA, as in `https://github.com/<owner>/<repo>/blob/<sha>/<path>#L10-L20`. A branch URL moves when the branch changes |
| A chat message | The message permalink, not the channel |
| A CI failure | The failed job, not the workflow |
| A metric or a log query | The deep link into the metrics or log system with the exact query and the time window |
| A document in a shared drive or wiki | The document URL, with the heading anchor when you cite one section |

## Do not

- Write `fix`, `close`, or `resolve` directly before a link. GitHub closes the target on merge, per [`github-closing-keywords`](../../rules/github-closing-keywords.mdc).
- Put a link inside code, a command, a fenced block, or an identifier.

## Verification

Before you publish, search the text for references that are not links:

```bash
grep -noE '(^|[^/A-Za-z0-9-])[A-Z][A-Z0-9]+-[0-9]+|#[0-9]+\b|\b[0-9a-f]{7,40}\b' <file>
```

For each hit, one of these must be true:

- The hit is linked at its first mention.
- The surface links it for you, per the table above.
- It is a label, or it is in a code span because a link would be wrong there, for example next to a closing keyword. A code span does not replace a link.

Then read the text for "the PR", "the ticket", "the doc", "the thread", and "the run" with no link near them.
