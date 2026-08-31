---
description: The rules for turning knowledge into FIU Brain atoms. Load this before calling submit_atoms, in /stop, in /process, and in any ingest. If a rule here disagrees with a rule anywhere else, this file wins.
---

# Extraction rules

Every atom in the brain is made with these rules. `/stop`, `/process` and every ingest load this same file and never restate it.

## 1. The bar: does this deserve an atom?

One test per candidate claim, all three parts must hold:

1. **Would a colleague, a month from now, act or decide differently for knowing this?**
2. **Is it not already derivable** from the registers, dashboards or code? (Which websites exist, contact details, live supermarkets: the systems hold those.)
3. **Does it stand alone?** Readable without the source, by someone who was not there.

Make an atom for:

- decisions and agreements, with who agreed and when
- a client's position, preference, objection or constraint
- agreed numbers: prices, commissions, budgets, volumes, deadlines
- who does what at a client: role, decision maker, a change of role
- a deliberate deviation from how FIU normally works, plus the reason
- why something failed, stalled or succeeded
- how FIU works: definitions, service descriptions, pricing rules, ways of working (these become proposals)
- an agreed action item, as observed: "Agreed: Robert sends the Heinz rate card before 5 September 2026." A commitment is a decision; bare scheduling still is not
- a question the brain could not answer, flagged during a session, as a proposal whose title is the question itself, ending in a question mark (the one exception to the title shape)

Never make an atom for:

- scheduling, logistics, availability, small talk
- anything the registers already hold
- status that is stale within weeks and was not a decision
- personal or private matters: health, family, performance, salary, anything HR. Skip them, never quote them anywhere, and report that the source contained personal material
- speculation with no owner ("we could maybe ...") unless someone decided it
- the argument of an article or document you were handed; only a company-wide takeaway becomes a proposal
- your own reasoning, or a summary of the session

**Expected yield** (the anti-explosion dial): a mail thread gives 0 to 3 atoms, an hour of meeting 3 to 8, a working session 0 to 3. Zero is a normal outcome; say so and move on. Thirty atoms from one source means you are keeping material these rules say to skip. Every weak atom taxes every future session that has to scan past it.

When in doubt, leave it out. A missing atom costs one question later. A wrong atom gets repeated as truth.

## 2. Shape

- One claim per atom. A sentence joining two facts with "and" is two atoms.
- The title is the claim as one full English sentence, specific enough to stand alone in a list of a thousand titles. "Heinz DE approved the Q4 2026 campaign on 26 August 2026.", not "Q4 proposal update". It ends with a period and stays under 200 characters.
- The body states the claim in plain English, one idea per sentence, with only the context needed to act on it. Guideline 1,024 characters, hard maximum 2,048. Shorter is always better. If the body needs a second idea to make sense, that second idea is either its own atom or padding.
- Same word for the same concept, every time. Service names exactly as the brain writes them. Spell out an abbreviation on first use in the body: "recipe to basket (R2B)".
- Numbers and dates unambiguous: "10 percent of media budget", "26 August 2026". Never "last month" or "the usual fee".
- State claims. Mark doubt explicitly in the text ("Heinz has not confirmed this").
- No idiom, no metaphor, no marketing language. Everything in English, whatever language the source spoke.

## 3. observed or proposal

- `observed`: a fact about one or a few named entities. Live immediately, no approval.
- `proposal`: anything that generalises beyond named entities (a market, a trend, "German brands", a rule, how FIU works), and anything that contradicts an existing agreed atom. A founder decides.

The test is scope, not certainty. "Heinz DE thinks our rates are high" is observed. "German brands find our rates high" is a proposal, however sure you are.

A claim that contradicts an agreed atom becomes a proposal that states both values in the body and names the atom it contradicts. Never pick a side silently.

## 4. source_at

The moment of the source: the mail, the meeting, the session. Never the moment of processing. Send it as ISO 8601 with the timezone offset; the server stores UTC and rejects future times. If a source from today says "last month Heinz said X", the atom carries today's source date and the body writes out the month. A source with no date gets the delivery time and "date unknown" in the body.

## 5. Labels

Call the `labels` tool before assigning any label. Never guess a slug from a name.

- Register-bound (`websites/`, `service/`, `supermarket/`) must match the tool's listing exactly. No match means no label; report the name so it can be added to the register.
- Curated (`business_unit/`, `country/`, `theme/`, `type/`) come from the fixed lists the tool shows.
- Free (`person/<email>`, `partner/`, `prospect/`) reuse a listed value when one fits; create a new one only when it is genuinely new.
- Competitors get `theme/competition` only, never a label of their own.

One claim touching several entities is ONE atom with several entity labels; never duplicate an atom per client. Label what the claim is about, not everything it mentions. One to six labels is normal, and almost every observed atom carries at least one entity label.

## 6. Clearance

Omit the field and the server defaults to team, raised automatically to the floor of the sources and labels. Use `founders` only when the fact itself is founders-sensitive (deal terms under wraps, HR-adjacent business facts, acquisition interest); use `public` only for facts FIU would put on its website. The server enforces the floors: an atom can never sit below its sources or its labels, and never above your own clearance. A label above your clearance is simply unusable; if that surprises you, tell the user instead of retrying.

## 7. Attribution

Write who said it, in the body:

- client or partner conversation: "Heinz DE said ..."
- internal meeting: "Team assessment: ..."
- a document: "The 2026 rate card states ..."

## 8. Do not repeat the brain

Check the context pack and `search` before submitting. The server bounces exact duplicates (same title and content) with a pointer; everything reworded is your judgement, so look first.

A correction or a newer truth is a new atom with `supersedes` set to the old filename. The server enforces: same clearance, target still live and head of its chain, strictly earlier source time, observed only over observed. A proposal with `supersedes` records intent; the swap happens at approval. If your new fact is older than the atom it would replace, submit it as a proposal with "backfill" in the body.

Read server errors, fix the atom, resubmit only the failures. Never resubmit anything unchanged, and never re-propose a claim that was declined; the error carries the reason.

## 9. The submit contract

`submit_atoms` takes a list of atoms; each atom is validated on its own and the result says per atom what happened. Fields:

| field | meaning |
|---|---|
| `title` | the claim, one English sentence, max 200 chars |
| `content` | the claim in plain English, guideline 1,024, max 2,048 |
| `kind` | `observed` or `proposal` |
| `labels` | slugs from the `labels` tool |
| `sources` | ids of raws this came from, when processing raws |
| `source_at` | ISO 8601 moment of the source |
| `clearance` | omit for team; `founders` or `public` deliberately |
| `supersedes` | filename of the atom this corrects |

The markdown frontmatter people see in exports is rendered by the server from these fields; you never write frontmatter yourself.

## 10. Worked example

Source, client call, 26 August 2026: "Anna van Heinz zei dat ze de Q4 aanvraag goedkeuren maar dat het budget van 60k naar 45k gaat omdat Duitsland is gekort. Ze wil de creators eerder zien dan vorig jaar. We spreken elkaar dinsdag weer."

Three atoms, labels `websites/heinz-de` and `person/anna@heinz.com`:

1. "Heinz DE approved the Q4 2026 campaign on 26 August 2026." (observed)
2. "Heinz DE reduced the Q4 2026 campaign budget from 60,000 to 45,000 euro because the German budget was cut." (observed)
3. "Heinz DE wants to see the creator selection earlier in the process than in 2025." (observed)

Not an atom: the next appointment. That is scheduling.

Wrong: "Heinz DE approved Q4, cut the budget and wants creators earlier." Three claims in one.
Wrong: "Q4 update Heinz." Not a claim.
Wrong, as observed: "Brands are cutting German budgets in 2026." It generalises: proposal or nothing.
