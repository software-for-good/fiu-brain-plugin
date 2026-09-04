---
description: The rules for turning knowledge into FIU Brain atoms, as one funnel run per source. Load this before calling submit_atoms, in /stop, in fiu:process, and in any ingest. If a rule here disagrees with a rule anywhere else, this file wins.
user-invocable: false
---

# Extraction rules

Every atom in the brain is made with this funnel. `/stop`, `fiu:process` and every ingest run the funnel once per source and never restate it. Everything you write is English, whatever language the source spoke.

## Who owns what

The brain is one of four systems. Each system owns its own kind of knowledge, and the brain holds only its own kind: meaning, and the answers people actually ask for. One principle settles every overlap with the docs and the code: a question asked is the ticket in.

| System | What it owns | What that means for atoms |
|---|---|---|
| The FIU database: Nova, the registers, the dashboards | The current state: which websites exist, contact details, subscriptions, orders, what is live now, and the figures. | A current value is never an atom. The story of how that value came about (who agreed it, when, and why) is an atom. |
| The codebase and the docs | The complete reference for how the product works. | The brain never copies that reference. It holds the asked subset: a question that a colleague, a partner or a client actually asked, with the answer they got, is an atom, because the question proves the knowledge is needed in sessions and the docs are not in the session. Documentation copied without anyone having asked is not an atom. |
| The raws | The full text and every figure of a source. | A colleague reads a raw when they must. An atom points at a raw instead of copying it. |
| The brain | Meaning: what was agreed, planned, decided or explained, and why; and the answers to the questions people actually ask. | This funnel extracts that meaning. |

## Atom scope

Scope is whom a claim concerns. There are two kinds of atom, and the kind is named after the scope.

- A `scoped` atom concerns one to a few named external parties and carries their labels. A scoped atom is live as soon as the server accepts it, because a wrong scoped atom does damage only inside its own scope.
- A `company_wide` atom applies to everyone: a service, a supermarket, a rule, the market, how FIU works. A company-wide atom enters the brain as `proposed`, and a founder approves it before it counts as truth, because it becomes what FIU repeats to everyone.

## Clearance

Clearance is who may see something. It applies to atoms and to raws alike, and it is independent of scope. The three levels are `public`, `team` and `founders`.

- The default is `team`. Omit the field and the server sets it, raised to the highest clearance among the atom's sources and labels.
- Use `founders` only when the fact itself is founders-sensitive: deal terms under wraps, HR-adjacent business facts, acquisition interest.
- Use `public` only for facts FIU would put on its website.
- The server enforces the floors. An atom never sits below its sources or its labels, and never above your own clearance. A label above your clearance is unusable; if that surprises you, tell the human instead of retrying.

## 1. Take the source

The source arrives in one of three ways. `/stop` gives you the session you are in, `fiu:process` gives you a raw fetched from the queue, and an ingest gives you its files. Read each type of source in its own way.

- A meeting transcript: read the transcript body. Ignore a generated summary block at the top, because knowledge is never built on a derived layer.
- A Claude session: the whole session is the source, both what you produced and what the human said. What the human said weighs more than what you produced.
- A mail thread: read the messages in order. Quoted text inside a reply repeats an earlier message, so read each message once. The last message holds the latest state of the thread.
- A document, a deck or a storyline: read it as an argument. Only the decisions it records and the company-wide takeaways survive the bar; the argument itself does not.

## 2. Find what passes the bar

Test one candidate claim at a time. All three conditions must hold.

- A colleague who reads the claim a month from now acts or decides differently for knowing it.
- The claim stands alone: someone who was not there can read it without the source.
- The claim is settled: it happened, it was agreed, it was decided, or it is a client's dated plan. A draft, an open question, a status that changes next week or a claim that nobody owns is not knowledge yet. Such a candidate goes in the report, and the decision it leads to becomes the atom later.

Whether a fact also stands in the docs, in the code, on the website or in a mail does not decide the bar; the three conditions do. For knowledge about the product, a question asked is the ticket in: the docs are the complete reference, and the brain holds the part people actually ask about.

- Passes: "Chicks Love Food planned to launch its member environment CLF Club in mid-September 2026." A client's dated plan is something a colleague prepares for.
- Fails: "We speak again on Tuesday." That is the logistics of the conversation.
- Passes: "FIU decided on 27 August 2026 not to attend a partner's event, because winning and keeping creators needs no such event." A decision with its reason passes, whatever the decision is about.
- Fails: "Zesty 2.0 is organised around arriving, staying and returning." That is a draft storyline for a session that has not been held.

Typical yields are calibration, never a target: a support or account thread gives 1 to 4 atoms, a multi-month thread up to 8, an hour of meeting 3 to 8, a strategy document 3 to 10, a working session 0 to 3. Zero is a normal outcome; say so and move on. Distrust repetition more than a count. When in doubt, leave the claim out: a missing atom costs one question later, and a wrong atom gets repeated as truth.

## 3. Split

Split a claim until a smaller piece would stop reading on its own. One claim per atom: a sentence that joins two facts with "and" is two atoms, and a sentence with a semicolon is probably two atoms. A claim about roles names one person per atom. An agreed action item is an atom of its own, separate from the decision that produced it.

- One atom: "Chicks Love Food agreed to Any to Basket at 50 euro per month with a one-year minimum on 16 July 2026."
- A second atom, not a clause of the first: "Chicks Love Food requires the Any to Basket contract to be cancellable monthly after the first year."

## 4. Write

- The title is the claim as one full English sentence. It is specific enough to stand alone in a list of a thousand titles, it ends with a period, and it stays under 200 characters. "Heinz DE approved the Q4 2026 campaign on 26 August 2026.", not "Q4 proposal update".
- The body states the claim in plain English, one idea per sentence, with only the context a colleague needs to act on it. The guideline is 1,024 characters and the hard maximum is 2,048. If the body needs a second idea to make sense, that idea is its own atom or it is padding.
- The body says who said it: "Heinz DE said ...", "Team assessment: ...", "The 2026 rate card states ...".
- Dates and numbers are unambiguous: "26 August 2026", "10 percent of media budget", never "last month" or "the usual fee". State claims. Mark doubt in the text: "Heinz has not confirmed this."
- Use the same word for the same concept, write service names exactly as the brain writes them, and spell out an abbreviation on first use: "recipe to basket (R2B)". No idiom, no metaphor, no marketing language.
- Numbers. An agreed number is always an atom. A measured number (traffic, saves, conversion, a share) is an atom only when someone used it to decide or to persuade, and then the body dates and attributes it: "On 1 September 2026 Rob told Lemone that FIU's traffic is 70 to 80 percent mobile." A source full of figures gets one atom that says what the set shows and points at the raw. The figures that carry the argument get atoms of their own; the supporting figures stay in the raw.
- An agreed action item reads like this: "Agreed: Robert sends the Heinz rate card before 5 September 2026." A commitment is a decision; bare scheduling is not.
- An absence that matters reads like this: "At the time of writing FIU has no pricing agreement with Jumbo." The body carries the date, and the atom that arranges the matter later supersedes it.
- A transition gets one atom for the change, with the old and the new state named in the body and dated at the moment of the change. The replaced state gets no atom of its own. A milestone carries an exact date and a specific fact, so that it never needs correcting.

## 5. Label

Call the `labels` tool before assigning any label; never guess a slug. Label what the claim is about, not everything it mentions; one to six labels is normal. If no label fits, you probably have no atom.

| Cluster | Mode | What atoms with this label are for |
|---|---|---|
| `websites/`, `partner/`, `prospect/` | Websites are register-bound; partners and prospects are free labels. | The relationship with that party: agreements, positions, dated plans, the sales trail from first interest onward, roles on their side, deviations from how FIU normally works, what is not yet arranged, relationship colour. |
| `person/<email>` | Free, for external contacts only. | The people in those relationships: who does what, what they said, what they want. |
| `service/` | Register-bound. Use the group slug (`service/r2b`). Add the tier slug (`service/r2b-custom`) only when the claim is about that tier, and then carry both. | What the service is, how it behaves, the questions people ask about it, its development and its history. |
| `supermarket/` | Register-bound. | What is arranged with a supermarket and how the integration works. |
| `business_unit/` | Curated. | How FIU works, per business unit: how finance invoices a client, how legal handles a contract, how support answers a partner. |
| `theme/`, `type/`, `country/` | Curated. | Facets for finding things: the theme of a claim, the type of party it concerns, the country it applies to. |

- A register-bound value must match the tool's listing exactly. No match means no label; report the name so it can be added to the register.
- A free label reuses a listed value when one fits. Create a new one only when the party is genuinely new. Competitors get `theme/competition` only and never a label of their own (blueprint B3).
- One claim that touches several parties is one atom with several labels, never one atom per party.

## 6. Scope

Scope follows from the labels, and scope is decided by whom the claim concerns.

- A claim that concerns one to a few named external parties and carries their labels (`websites/`, `partner/`, `prospect/`, `person/`) is `scoped`. It carries at least one such label, usually one to three, and never more than 15. The server refuses a scoped atom outside that range and points at company-wide.
- Every other claim is `company_wide`: a service and how it behaves, a supermarket and what is arranged with it, a rule, a market, "German brands", how FIU works. A claim that contradicts an existing company-wide atom is company-wide too; its body states both values and names the atom it contradicts, and it never picks a side silently.

One guard: a client label is never a vehicle for a general claim. "Lemone hit the one-basket-per-minute trial limit" is the rate limit in disguise. The rate limit is company-wide, and what Lemone did is at most a scoped footnote if a colleague would act on it. "Heinz DE thinks our rates are high" is scoped; "German brands find our rates high" is company-wide.

## 7. Filter

This step is the safety net after the bar. A candidate that passed step 2 and is not caught here stays.

- Always out: a current value the database owns; a dashboard figure that nobody used; the logistics of a conversation (meeting slots, availability, who calls whom); speculation with no owner; the argument of an article or document you were handed; your own reasoning or a summary of the session.
- `person/`: nothing about health, nothing learned outside the work relationship, no judgments about the person. What a contact volunteered at work and would expect a good account manager to remember stays.
- `websites/`, `partner/`, `prospect/`: no scheduling of the conversation. A client's dated plan is not scheduling and stays.
- `service/`: a question that a colleague, a partner or a client actually asked, with its answer, stays; a question asked is the ticket in. Documentation copied without anyone having asked is out.
- `business_unit/`, and anything about FIU's own people: nothing personal, nothing HR: salary, performance, contracts, reviews. Skip it, quote nothing, and report that the source contained personal material.

## 8. Compare with the brain

Check the context pack and `search` each candidate's entity labels before the candidate enters the list. The server bounces exact duplicates with a pointer; everything reworded is your judgement, so look first. There are four outcomes.

- New: keep the candidate.
- Duplicate: drop the candidate.
- Covered: the candidate is an older value of something a newer atom already answers. Drop it, count it, and ask once whether the change between then and now itself passes the bar. Usually it does not. When it does, because the change was a deliberate and reasoned shift in how FIU or a client works, the change becomes one transition atom. Example: the brain holds "FIU prices campaigns as a percentage of media budget" (2025) and a 2022 mail prices a campaign at 450 euro per post. The 450 euro atom is never made. If the sources show that the switch was a real 2023 decision, the atom is "In 2023 FIU moved campaign pricing from a fee per post to a percentage of media budget", with the old fee in the body. Events, decisions and reasons are never covered merely by being old.
- Conflict: sources of the same age disagree. Make one company-wide atom that states both values.

A correction or a newer truth is a new atom with `supersedes` set to the old atom's filename. The server enforces: same clearance, target still live and head of its chain, strictly earlier source time, scoped over scoped. A company-wide correction records the intent and the swap happens at approval. An older fact that would correct a newer atom goes in as company-wide with "backfill" in the body.

Read server errors, fix the atom, and resubmit only the failures. Never resubmit anything unchanged, and never resubmit a claim that was declined; the error carries the reason.

## 9. Clearance and date

- Set the clearance per the Clearance section above. In most cases you omit the field.
- Set `source_at` to the moment of the source: the mail, the meeting, the session. Never use the moment of processing. Send ISO 8601 with the timezone offset; the server stores UTC and rejects future times. A source from today that says "last month Heinz said X" carries today's date, and the body writes out the month. A source with no date gets the delivery time, and the body says "date unknown".

## The submit contract

`submit_atoms` takes a list of atoms. Each atom is validated on its own, and the result says per atom what happened.

| field | meaning |
|---|---|
| `title` | the claim, one English sentence, max 200 characters |
| `content` | the claim in plain English, guideline 1,024 characters, max 2,048 |
| `kind` | `scoped` or `company_wide` |
| `labels` | slugs from the `labels` tool |
| `sources` | ids of the raws this came from, when processing raws |
| `source_at` | ISO 8601 moment of the source |
| `clearance` | omit for team; `founders` or `public` deliberately |
| `supersedes` | filename of the atom this one corrects |

The frontmatter people see in exports is rendered by the server from these fields; you never write it.
