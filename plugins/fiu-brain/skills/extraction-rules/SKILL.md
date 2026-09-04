---
description: The rules for turning knowledge into FIU Brain atoms. Load this before calling submit_atoms, in /stop, in fiu:process, and in any ingest. If a rule here disagrees with a rule anywhere else, this file wins.
user-invocable: false
---

# Extraction rules

Every atom in the brain is made with these rules. `/stop`, `fiu:process` and every ingest load this same file and never restate it.

## 1. What the brain holds

Say what goes in before asking what stays out. The brain serves three uses, and every atom belongs to one of them.

**Account management and sales: observed atoms.** Knowledge about a named client, partner, prospect or contact that the next conversation or the next deal turns on:

- agreements and agreed numbers: prices, commissions, budgets, volumes, deadlines, terms, with who agreed and when
- their position, preference, objection or constraint
- their plans and milestones, dated: a launch, a go-live, a campaign window, a postponement. "Chicks Love Food planned to launch its member environment CLF Club in mid-September 2026." That is a plan a colleague prepares for, not scheduling
- the sales trail from first interest onward: who showed interest in what and when, what was offered at what price, accepted or rejected, and why. Nova holds subscriptions once they run; the funnel before that lives only here
- who does what on their side: role, decision maker, a change of role
- what is not arranged with them yet, when a colleague would act differently for knowing it, dated in the body; the atom that arranges it later supersedes it
- a deliberate deviation from how FIU normally works for them, with the reason
- why something with them failed, stalled or succeeded
- an agreed action item, as observed: "Agreed: Robert sends the Heinz rate card before 5 September 2026." A commitment is a decision; bare scheduling still is not
- relationship colour the contact volunteered in a work setting and would expect a good account manager to remember: a holiday, a move, a new colleague, a preference for calls over mail

**Support: proposals on the service label.** How a service behaves, as it was explained to someone: the answer given to a real question, a known limitation, a gotcha, a workaround, what an integration needs from the other side, what a service is in one sentence. "During an Any to Basket trial a rate limit of one basket per minute applies" belongs here, even when one client hit it and even though the docs mention it: that a fact exists somewhere does not put it in a colleague's head. Support atoms come from questions actually asked and things learned the hard way, so the brain grows a real FAQ rather than a copy of the docs. They are proposals because they apply to everyone; a founder confirms them before they are repeated to clients.

**Company knowledge: proposals.** How FIU works and what it does or does not do: pricing rules and policies, ways of working, definitions, decisions with who decided and why, market knowledge, notable firsts and milestones (dated and precise, so they never need correcting), important transitions (one atom for the change, old and new named in the body, dated at the change; the replaced state gets no atom of its own), and everything about supermarkets, whose arrangements apply to every client.

**The bar.** One test, both halves must hold: would a colleague, a month from now, act or decide differently for knowing this, and does it stand alone, readable without the source by someone who was not there? That a fact is also in the docs, on the website, in the code or in a mail does not fail the bar.

**Numbers.** An agreed number is always an atom. A measured number (traffic, saves, conversion, a share) is an atom only when someone used it to decide or to persuade, and then dated and attributed in the body: "On 1 September 2026 Rob told Lemone that FIU's traffic is 70 to 80 percent mobile." A source full of figures (a report, a table, a dashboard export) gets one atom that says what it is and points at the raw; the figures themselves stay in the raw, which colleagues can read when they must.

**What stays out.** Three lists, from wide to narrow.

- For every atom: live register state the database owns and that changes under the brain's feet (which websites exist, contact details, subscriptions, orders, what is live now); a stray dashboard number; the logistics of a conversation (meeting slots, availability, who calls whom); speculation with no owner; the argument of an article or document you were handed; your own reasoning or a summary of the session.
- For observed atoms about external contacts: nothing about health, nothing learned outside the work relationship, no judgments about the person. Everything else they volunteered is allowed when it helps the next conversation.
- For company-wide atoms and for FIU's own people: strictly nothing personal, nothing HR (salary, performance, contracts, reviews). Skip it, quote nothing, and report that the source contained personal material.

**Calibration** (never a target): a support or account thread 1 to 4 atoms, a multi-month thread up to 8, an hour of meeting 3 to 8, a strategy document 3 to 10, a working session 0 to 3. Zero is a normal outcome; say so and move on. Distrust repetition more than a count: thirty atoms that restate each other mean the bar slipped, and every weak atom taxes every future session that has to scan past it.

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

Observed atoms go live without approval, so the lane is decided by scope, never by certainty:

- `observed`: the claim is about one to a few named external parties and carries their labels: `websites/`, `partner/`, `prospect/`, `person/`. At least one, expected one to three, never more than 15. The server refuses an observed atom outside that range and points at the proposal lane; apply the rule yourself before it has to.
- `proposal`: everything else. Anything that applies to everyone or generalises: a service and how it behaves, a supermarket and what is arranged with it, a market, a trend, "German brands", a rule, how FIU works. Also anything that contradicts an existing agreed atom. A founder decides.

A service or supermarket label never makes an atom observed, and a client label is not a vehicle for a general claim: "Lemone hit the one-basket-per-minute trial limit" is the rate limit in disguise. The rate limit is a proposal; what Lemone did is at most an observed footnote, if a colleague would act on it.

"Heinz DE thinks our rates are high" is observed. "German brands find our rates high" is a proposal, however sure you are.

A claim that contradicts an agreed atom becomes a proposal that states both values in the body and names the atom it contradicts. Never pick a side silently.

## 4. source_at

The moment of the source: the mail, the meeting, the session. Never the moment of processing. Send it as ISO 8601 with the timezone offset; the server stores UTC and rejects future times. If a source from today says "last month Heinz said X", the atom carries today's source date and the body writes out the month. A source with no date gets the delivery time and "date unknown" in the body.

## 5. Labels

Call the `labels` tool before assigning any label. Never guess a slug from a name.

- Register-bound (`websites/`, `service/`, `supermarket/`) must match the tool's listing exactly. No match means no label; report the name so it can be added to the register.
- A service is labelled at group level: `service/r2b`, `service/a2b`. The tiers of one service hardly differ in what the brain knows about them, so the tier slug (`service/r2b-custom`) is added only when the claim is about that tier specifically and the distinction would change what a colleague does, and then the atom carries both, group and tier, so a search on the group finds everything.
- Curated (`business_unit/`, `country/`, `theme/`, `type/`) come from the fixed lists the tool shows.
- Free (`person/<email>`, `partner/`, `prospect/`) reuse a listed value when one fits; create a new one only when it is genuinely new.
- Competitors get `theme/competition` only, never a label of their own.

One claim touching several entities is ONE atom with several entity labels; never duplicate an atom per client. Label what the claim is about, not everything it mentions. One to six labels is normal; every observed atom carries one to 15 external-entity labels (section 3).

## 6. Clearance

Omit the field and the server defaults to team, raised automatically to the floor of the sources and labels. Use `founders` only when the fact itself is founders-sensitive (deal terms under wraps, HR-adjacent business facts, acquisition interest); use `public` only for facts FIU would put on its website. The server enforces the floors: an atom can never sit below its sources or its labels, and never above your own clearance. A label above your clearance is simply unusable; if that surprises you, tell the human instead of retrying.

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

An atom, had Anna said it: "Heinz DE launches its new recipe site on 15 October 2026." A client's launch date is a plan a colleague prepares for, not scheduling.

From the same week, all proposals because they apply to everyone: "During an Any to Basket trial a rate limit of one basket per minute applies." "FIU has no telephone customer service." "Flink shows a buy button only when its own share of a recipe's ingredients is available."

Wrong, as observed: "Lemone hit the one-basket-per-minute trial rate limit." A general rule wearing a client label; the rate limit is a proposal.

Wrong: "Heinz DE approved Q4, cut the budget and wants creators earlier." Three claims in one.
Wrong: "Q4 update Heinz." Not a claim.
Wrong, as observed: "Brands are cutting German budgets in 2026." It generalises: proposal or nothing.
