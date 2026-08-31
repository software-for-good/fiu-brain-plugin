---
description: Rules for turning knowledge into FIU Brain atoms. Read this before calling submit_atoms, in /stop, in the founder loop and in the mailbox sweep.
---

- One claim per atom. The title is the claim as one sentence; the content says it in plain English, one idea per sentence, guideline 1,024 characters, never more than 2,048.
- Same word for the same concept; service names exactly as the brain uses them; no idiom, no marketing language; numbers and dates unambiguous; state claims, mark doubt.
- `kind` is `observed` for a fact about specific named entities (one or a few), `proposal` for anything that generalises (a market, a trend, "German brands", how FIU works), whatever the source.
- `source_at` is the moment of the source (the mail, the meeting, the session), never the moment of processing. Dates inside the claim are written out in the text.
- Labels only from the vocabulary, and the vocabulary comes from the `labels` tool: call it before assigning labels (filter with `cluster` and `query`). Register-bound values (`websites/`, `service/`, `supermarket/`) must match its listing exactly; never guess a slug from a name. Curated values (`business_unit/`, `country/`, `theme/`, `type/`) are the fixed lists it shows. Free labels (`person/<email>`, `partner/`, `prospect/`) are created on first use; reuse a listed one when it fits. Competitors get only `theme/competition`.
- Attribute: in a client conversation "Heinz said …", in an internal meeting "Team assessment: …".
- Do not repeat what the brain already has. A correction or a newer truth is a new atom with `supersedes` set to the filename of the old one.

This is a short stub; the full rules follow.
