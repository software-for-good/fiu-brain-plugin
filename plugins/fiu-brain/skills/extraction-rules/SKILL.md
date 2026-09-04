---
description: The rules for turning knowledge into FIU Brain atoms, as one funnel run per source. Load this before calling submit_atoms, in /stop, in fiu:process, and in any ingest. If a rule here disagrees with a rule anywhere else, this file wins.
user-invocable: false
---

# Extraction rules

Every atom in the brain is made with this funnel. `/stop`, `fiu:process` and every ingest run it per source and never restate it. Everything you write is English, whatever language the source spoke.

## Who owns what

The brain is one of four systems and holds only what the other three cannot say.

| System | Owns | So |
|---|---|---|
| The FIU database: Nova, the registers, the dashboards | current state: which websites exist, contact details, subscriptions, orders, what is live now, the figures | never an atom; the story of how it got there is |
| The codebase and the docs | how the product works, in full detail | an answer given to a real question is an atom; the docs re-typed are not |
| The raws | the full text and every figure of a source | a colleague reads a raw when they must; an atom points at it instead of copying it |
| The brain | meaning: what was agreed, planned, decided or explained, and why | that is what this funnel extracts |

Two kinds of atoms, named by scope. Scope is whom a claim is about; clearance (public, team, founders) is who may see it, and the two never mix.

- `scoped`: about one to a few named external parties, carrying their labels. Live at once, because a wrong scoped atom does damage only inside that scope.
- `company_wide`: applies to everyone: a service, a supermarket, a rule, the market, how FIU works. Enters as `proposed` and a founder approves it, because it becomes what FIU repeats to everyone.

## 1. Take the source

`/stop` hands you the session, `fiu:process` a fetched raw, an ingest its files. Read the source itself: for a meeting transcript the transcript body, never a generated summary at the top, because knowledge is never built on a derived layer. What the human told you is source too, not only what you produced.

## 2. Find what passes the bar

Three conditions, all must hold, one candidate claim at a time.

- A colleague, a month from now, acts or decides differently for knowing it.
- It stands alone: readable without the source, by someone who was not there.
- It is settled: it happened, was agreed, was decided, or it is a client's dated plan. A draft, an open question, a status that changes next week or a claim nobody owns is not knowledge yet; it goes in the report, and the decision it leads to becomes the atom.

That a fact is also in the docs, in the code, on the website or in a mail does not fail the bar. That a fact exists somewhere does not put it in a colleague's head.

- Yes: "Chicks Love Food planned to launch its member environment CLF Club in mid-September 2026." A client's dated plan; a colleague prepares for it.
- No: "We speak again on Tuesday." The logistics of the conversation.
- Yes: "During an Any to Basket trial a rate limit of one basket per minute applies." Explained to a partner who hit it; the docs mentioning it changes nothing.
- No: "As of 31 August 2026 FIU is waiting on Flink's development status." Status that changes next week and that nobody decided.
- No: "Zesty 2.0 is organised around arriving, staying and returning." A draft storyline for a session not yet held.
- Yes: "FIU decided on 27 August 2026 not to attend Lemone's event of 22 September 2026, because winning and keeping creators needs no such event." A decision with its reason, whatever it is about.

Typical yield, never a target: a support or account thread 1 to 4 atoms, a multi-month thread up to 8, an hour of meeting 3 to 8, a strategy document 3 to 10, a working session 0 to 3. Zero is a normal outcome; say so and move on. Distrust repetition more than a count. When in doubt, leave it out: a missing atom costs one question later, a wrong atom gets repeated as truth.

## 3. Split

Split until a piece would stop reading on its own. One claim per atom: a sentence joining two facts with "and" or a semicolon is two atoms. One person per role atom. An action item and an absence are atoms of their own.

- One: "Chicks Love Food agreed to Any to Basket at 50 euro per month with a one-year minimum on 16 July 2026."
- Another: "Chicks Love Food requires the Any to Basket contract to be cancellable monthly after the first year."
- Not one: "Sophia Mather leads the FIU project at Flink and Sascha Nawrot is the tech counterpart." Two people, two atoms.

## 4. Write

- The title is the claim as one full English sentence, specific enough to stand alone in a list of a thousand titles, ending with a period, under 200 characters. "Heinz DE approved the Q4 2026 campaign on 26 August 2026.", not "Q4 proposal update".
- The body states the claim in plain English, one idea per sentence, with only the context needed to act on it. Guideline 1,024 characters, hard maximum 2,048. If the body needs a second idea to make sense, that idea is its own atom or padding.
- Who said it, in the body: "Heinz DE said ...", "Team assessment: ...", "The 2026 rate card states ...".
- Dates and numbers unambiguous: "26 August 2026", "10 percent of media budget", never "last month" or "the usual fee". State claims; mark doubt in the text: "Heinz has not confirmed this."
- The same word for the same concept, service names exactly as the brain writes them, an abbreviation spelled out on first use: "recipe to basket (R2B)". No idiom, no metaphor, no marketing language.
- Numbers: an agreed number is always an atom. A measured number (traffic, saves, conversion, a share) is an atom only when someone used it to decide or to persuade, dated and attributed: "On 1 September 2026 Rob told Lemone that FIU's traffic is 70 to 80 percent mobile." A source full of figures gets one atom that says what the set shows and points at the raw; the figures that carry the argument get atoms of their own, the supporting ones stay in the raw.
- An agreed action item: "Agreed: Robert sends the Heinz rate card before 5 September 2026." A commitment is a decision; bare scheduling is not.
- An absence that matters: "At the time of writing FIU has no pricing agreement with Jumbo.", dated in the body; the atom that arranges it later supersedes it.
- A transition: one atom for the change, old and new named in the body, dated at the change; the replaced state gets no atom of its own. A milestone: exact date, specific fact, so it never needs correcting.

## 5. Label

Call the `labels` tool before assigning any label; never guess a slug. Label what the claim is about, not everything it mentions; one to six labels is normal. If no label fits, you probably have no atom.

| Cluster | Mode | Atoms with this label are for |
|---|---|---|
| `websites/`, `partner/`, `prospect/` | websites register-bound; partner and prospect free | the relationship with that party: agreements, positions, dated plans, the sales trail from first interest, roles on their side, deviations from how FIU normally works, what is not yet arranged, relationship colour |
| `person/<email>` | free, external contacts only | the people in those relationships: who does what, what they said, what they want |
| `service/` | register-bound: the group (`service/r2b`); the tier (`service/r2b-custom`) added only when the claim is about that tier, and then both | what the service is, how it behaves, its development and its history |
| `supermarket/` | register-bound | what is arranged with a supermarket and how the integration works |
| `business_unit/` | curated | how FIU works, per function: finance, accounts, sales, tech, legal, support, strategy, communication |
| `theme/`, `type/`, `country/` | curated | facets for finding things: trends, competition, services, events; brand, agency, platform, influencer, supermarket; ISO country codes |

- Register-bound values must match the tool's listing exactly. No match means no label; report the name so it can be added to the register.
- Free labels reuse a listed value when one fits; a new one only when it is genuinely new. Competitors get `theme/competition` only, never a label of their own.
- One claim touching several parties is one atom with several labels, never one atom per party.

## 6. Scope

Scope follows from the labels.

- The claim is about one to a few named external parties and carries their labels (`websites/`, `partner/`, `prospect/`, `person/`): `scoped`. At least one such label, expected one to three, never more than 15; the server refuses anything else and points at company-wide.
- Anything else: `company_wide`. A service and how it behaves, a supermarket and what is arranged with it, a rule, a market, "German brands", how FIU works. Also anything that contradicts an existing company-wide atom; that atom states both values in the body and names the atom it contradicts, never picking a side silently.

One guard: a client label is never a vehicle for a general claim. "Lemone hit the one-basket-per-minute trial limit" is the rate limit in disguise; the rate limit is company-wide, and what Lemone did is at most a scoped footnote if a colleague would act on it. Scope is decided by whom the claim concerns, never by how sure you are: "Heinz DE thinks our rates are high" is scoped, "German brands find our rates high" is company-wide, however sure you are.

## 7. Filter

The safety net after the bar. One line per case; if a candidate is not caught here and passed step 2, it stays.

- Always out: current state the database owns; a dashboard figure nobody used; the logistics of a conversation (meeting slots, availability, who calls whom); speculation with no owner; the argument of an article or document you were handed; your own reasoning or a summary of the session.
- `person/`: nothing about health, nothing learned outside the work relationship, no judgments about the person. What they volunteered at work and would expect a good account manager to remember stays.
- `websites/`, `partner/`, `prospect/`: no scheduling of the conversation. A client's dated plan is not scheduling and stays.
- `service/`: only what was explained to someone or learned the hard way. The docs re-typed are out.
- `business_unit/`, and anything about FIU's own people: nothing personal, nothing HR: salary, performance, contracts, reviews. Skip it, quote nothing, and report that the source contained personal material.

## 8. Compare with the brain

Check the context pack and `search` each candidate's entity labels before it enters the list. The server bounces exact duplicates with a pointer; everything reworded is your judgement, so look first. Four outcomes.

- New: keep it.
- Duplicate: drop it.
- Covered: the candidate is an older value of something a newer atom already answers. Drop it, count it, and ask once whether the change between then and now itself passes the bar. Usually not. When it does, a deliberate and reasoned shift in how FIU or a client works, the change becomes one transition atom. The brain holds "FIU prices campaigns as a percentage of media budget" (2025) and a 2022 mail prices a campaign at 450 euro per post: the 450 euro atom is never made, and if the sources show the switch was a real 2023 decision, the atom is "In 2023 FIU moved campaign pricing from a fee per post to a percentage of media budget", the old fee in the body. Events, decisions and reasons are never covered merely by being old.
- Conflict: sources of the same age disagree. One company-wide atom stating both values.

A correction or a newer truth is a new atom with `supersedes` set to the old filename. The server enforces: same clearance, target still live and head of its chain, strictly earlier source time, scoped over scoped. A company-wide correction records the intent and swaps at approval. An older fact that would correct a newer atom goes in as company-wide with "backfill" in the body.

Read server errors, fix the atom, resubmit only the failures. Never resubmit anything unchanged, and never resubmit a claim that was declined; the error carries the reason.

## 9. Clearance and date

- Clearance: omit the field and the server defaults to team, raised to the floor of the sources and labels. `founders` only when the fact itself is founders-sensitive: deal terms under wraps, HR-adjacent business facts, acquisition interest. `public` only for facts FIU would put on its website. An atom never sits below its sources or its labels, nor above your own clearance; a label above your clearance is unusable, and if that surprises you, tell the human instead of retrying.
- `source_at`: the moment of the source, the mail, the meeting, the session, never the moment of processing. ISO 8601 with the timezone offset; the server stores UTC and rejects future times. A source from today that says "last month Heinz said X" carries today's date, and the body writes out the month. A source with no date gets the delivery time and "date unknown" in the body.

## The submit contract

`submit_atoms` takes a list of atoms; each is validated on its own and the result says per atom what happened.

| field | meaning |
|---|---|
| `title` | the claim, one English sentence, max 200 chars |
| `content` | the claim in plain English, guideline 1,024, max 2,048 |
| `kind` | `scoped` or `company_wide` |
| `labels` | slugs from the `labels` tool |
| `sources` | ids of raws this came from, when processing raws |
| `source_at` | ISO 8601 moment of the source |
| `clearance` | omit for team; `founders` or `public` deliberately |
| `supersedes` | filename of the atom this corrects |

The frontmatter people see in exports is rendered by the server from these fields; you never write it.
