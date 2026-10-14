---
name: simple-english
description: Must be read before writing a pull request body, a review comment, a commit message, a ticket, or a written answer to an engineer.
---

# Simple English

ASD-STE100 is a controlled language. The aerospace industry built it so that a tired mechanic cannot misread an instruction. Engineers need it for the same reason. A reviewer reads your text once, at the end of a long day, and must act on it correctly.

Write so that the reader needs one pass. Every rule below serves that.

## Where this applies

Apply it to engineer-facing text:

- A pull request body, title, or commit message.
- A review comment, a review summary, or a reply to review feedback.
- A ticket summary, description, or comment.
- A written answer to an engineer about work in this codebase.

Do not apply it to:

- Code, identifiers, commands, flags, file paths, or quoted error text. Copy these exactly.
- Customer-facing marketing copy, taglines, and brand text. STE removes persuasion by design.
- OpenAPI field descriptions. These are out of scope.

A skill that owns a document type wins on shape and length. [`writing-pull-requests`](../writing-pull-requests/SKILL.md) owns the shape of a pull request body. The sentence caps below apply to it as they do to every other engineer-facing text.

## Sentence shape

These rules are mechanical. You can point at the word that breaks each one.

1. Use the active voice and name the actor. Write "the job writes the file", not "the file is written".
2. Use simple tenses. Write "we received the report", not "we have received the report".
3. Write one instruction per sentence.
4. Cap a procedure sentence at 20 words. Cap a description sentence at 25 words.
5. Put the condition first, then the command. "If the build fails, read the log."
6. Do not use a semicolon. Write two sentences.
7. Do not use an em dash. Name the relation with "because", "but", or "for example".
8. Do not use a phrasal verb. Write "start the job", not "spin up the job".
9. Cap a noun chain at three words. Break a longer chain with a preposition, as in "the timeout for the connection pool".
10. Keep the articles, keep the word "that", and use no contractions. STE is short sentences with full grammar, not telegraph style.
11. Cap a paragraph at six sentences and one topic.
12. Use a numbered or bulleted list for three or more steps.

## Word choice

ASD publishes a dictionary of approved words. The dictionary is licensed, and this skill holds no license to redistribute it, so it cannot verify dictionary compliance. Apply the principle instead. Pick the plainest common word, then use it the same way every time.

- **One word, one meaning, through the whole document.** Pick one verb for one action. Do not rotate "check", "verify", "confirm", and "validate" for the same act. Do not write `config` on one line and `settings` on the next.
- **Name an action with a verb.** Write "analyze the log", not "perform an analysis of the log".
- **Delete a word that carries no fact.** The common ones are simply, seamlessly, robust, powerful, comprehensive, crucial, leverage, "in order to", and "it is worth noting".
- **Delete stacked hedges that assert nothing.** "This may potentially help to improve" states no claim.
- **Define a technical term at first use, in four words or fewer.** Do not define a product name or a standard name such as Postgres, S3, or HTTP.

Use American spelling.

## Modals: two different words spelled the same

STE allows three modals: `must`, `can`, and `will`. That rule governs **requirement strength**. A requirement is `must`. A possibility is `can`. Delete a "should" that means `must`.

That rule does not govern **confidence**. "The timeout may have caused the retry storm" states how sure you are, and confidence is content. A shorter sentence that promotes a hedge to a fact makes a different claim. It does not simplify the old one.

Keep the hedge, and keep the compound tense that carries it. This is the most common way an STE rewrite goes wrong, because a word cap tempts you to cut exactly these words. [`root-cause-proof`](../root-cause-proof/SKILL.md) requires the hedge until its evidence checklist passes.

## What a rewrite must never do

- Add a fact the source did not state. A rewrite that reads better because it supplies a cause, a number, or a mechanism is no longer a rewrite.
- Drop a safety condition, an exception, or a scope qualifier to reach a word count. Keep the longer sentence, and say why you kept it.
- Shorten quoted error text, a security warning, or a confirmation before a destructive action.
- Change code, an identifier, a command, or a file path.

## AI tells

A sentence can follow every rule above and still read as machine output. Check for these habits. A single match is a weak signal. Several matches in one text are a strong signal. Leave a phrase alone inside a quotation, a title, a name, or text that discusses the phrase.

### Staging instead of stating

- **"Not X, but Y."** "This is not a cleanup, it is a fix." Write the claim on its own: "This is a fix." The same habit has two more forms. One splits the contrast into two sentences: "This does not mean X. It means Y." The other ends on a short negative tail: "The options come from the selected item, no guessing." Keep the negative half when X is a real cause, scope, or exception, or a belief that the reader stated.
- **A closing line that repeats the point.** "That is the real win." "Let that sink in." Delete it. Keep a short last sentence only when it adds a new fact or consequence.
- **A row of fragments.** "No retries. No backoff. No alerts." Merge them into one sentence with a specific claim: "The job has no retry, no backoff, and no alert."
- **A run-up before the answer.** "Here is what you need to know." "Here is the thing." Delete it and give the answer.
- **A saying that sounds deep.** "The real question is", "at its core", "what really matters". The frame adds no fact. Delete it and state the claim.
- **An argument with nobody.** "To be clear", "A tempting approach would be", "Some might say". The text answers an objection that nobody raised. Delete it. Keep a rejected alternative that a reader would weigh, and keep an objection that the text answers in full.
- **Three items where you have two or four.** "It is faster, safer, and cleaner." Write the number of items you have.

### Inflated words

- **Stock AI words.** delve, pivotal, key (as an adjective), enhance, bolster, showcase, highlight and underscore (as verbs), landscape, intricate, meticulous, testament, valuable. Replace each with the plain word, or delete it.
- **A long verb in place of "is" or "has".** "serves as", "stands as", "acts as", "boasts", "features", "offers". Write "is", "are", or "has".
- **A claim of importance.** "This is a critical improvement." Give the measurement the source gives, or delete the claim.
- **A vague link between two things.** "associated with", "tied to", "linked to", "in connection with". Name the relation: "calls", "owns", "writes", "causes". If the source does not name the relation, keep the vague word. Do not invent one.
- **Authority with no name.** "Industry best practice", "experts agree", "it is widely known". Name the source and what it says, or delete the claim.

### Leftovers from the chat and the draft

- **Chat phrases.** "Great question", "You are right", "I hope this helps", "Let me know if", "Want me to". Delete the wrapper and keep the content.
- **A guess that fills a gap.** "This was likely added for performance." If the source does not say why, write that the source does not say why. Do not supply a plausible reason.
- **A sentence about the text.** "This PR introduces", "This section explains", "The table below compares". Write about the subject, not about the text.
- **A sentence about your previous draft.** "This revision improves the wording." The reader never saw the draft. Delete it.
- **A first sentence that repeats its heading.** Under "Risks", the first sentence is not "This section lists the risks." Start with the first risk.

### Formatting

- **Decoration in headings and lists.** Title Case headings, emoji, arrows, and a horizontal rule between each section. Use sentence case, and keep decoration out of headings and list items. Name what the section holds, not an effect: "How the options compare", not "The decision, on one screen".

## Replies

Put the decision in the first sentence. Then add only what the reader does not have.

## Self-check before you publish

Search the text for each item below. Change a match only when it breaks a rule above and the rewrite keeps the source meaning:

1. `;` and `—`
2. `has been`, `have been`, and `was being`
3. `should`, `might`, and `could` used for a requirement
4. `, making`, `, allowing`, and `, enabling`
5. A second word for an act another word already names
6. A sentence over 25 words

Then read your three longest sentences aloud. Split any sentence that needs a second pass.

## Limits

This skill makes text clear. It does not make weak content true. A hollow paragraph rewritten under these rules is a clean, short, hollow paragraph. If the text has nothing to say, say that instead of polishing it.

Stop when the sentence is unambiguous, not when it is shortest. Cutting words is not the goal.

No tool guarantees ASD-STE100 compliance. The standard is a free request at [asd-ste100.org](https://www.asd-ste100.org/STE_downloads.html).
