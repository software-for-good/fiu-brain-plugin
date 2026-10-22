---
description: Close an FIU Brain session. Harvests what this session learned, lets the human react, and submits it to the brain.
disable-model-invocation: true
---

# /stop

You curate this session into the FIU Brain. This is the only place atoms are submitted: no skill submits before the human types `/stop`, and here nothing is submitted before the human has seen the atoms of step 3 and confirmed. If this session did not run `/start`, load `fiu:guardrails` now.

In a `fiu:process` session, the round the human confirmed there is the harvest: skip steps 2 to 5 and go to `fiu:process` step 6, which submits and marks it.

## 1. Gate

Take the identity from the `whoami:` line at the end of the FIU Brain server instructions: name, slug, role, clearance, `can_write` and `can_approve`. Not every client passes those instructions on, so when the line is not in your context, call the brain's `whoami` tool once: it returns the same payload. If that call fails too, the connector is not connected (Settings, Connectors, or `claude mcp add` with a personal token): say so and stop. If `can_write` is false, explain kindly that this account's token has no brain-write ability, that reading is unaffected, and that `php artisan brain:token` (a founder or developer runs it) issues a writing token. Stop.

## 2. Extract

Load `fiu:extraction-rules` and apply it to everything learned in this session, including what the human told you, not only what you produced. Everything you write is English. In the compare step of the funnel, search the brain as below: the context pack of the session start is budgeted and is not the brain of now.

The compare step (extraction rules, step 8) reads the brain through `search`, once per candidate: the candidate's title and content as the query, with a blank line between them, `statuses` `["scoped", "company_wide", "proposed", "declined", "deprecated"]`, `limit` 10 and no labels. The brain ranks the query by meaning and by words together, so it returns the atom that says the same in other words and the atom that shares a name, whatever labels either carries, in full and nearest first. Those are the atoms to compare the candidate with. Search for every candidate, even when an earlier search seemed to cover it: each candidate has its own nearest atoms. Candidates that are not submitted yet are not in the brain; compare them with each other yourself.

Action items and absence claims are atoms too; the extraction rules define both shapes. Nothing else: your own summaries and reasoning are not knowledge.

## 3. Show the harvest, then wait

Three tables, most certain first, every row numbered so the human can react by number. Never prose, never a plain list.

1. **Certain.** Columns: number, claim, kind, labels, clearance when not team. A single confirmation accepts them all.
2. **Doubtful.** Columns: number, claim, option A, option B. The human picks A, B or skip. Never guess on the human's behalf.
3. **Company-wide.** Columns: number, claim, labels. One line above the table says these enter as proposed, go to the founders and are not truth until approved.

Nothing is sent before the human reacts. They may approve with a correction in one move ("akkoord, maar het was 1.200"): apply it and do not ask again. Record every correction verbatim for the report; that feedback is how the extraction rules get better.

## 4. Standing behind it

When you sense the human is passing on AI-made material without having engaged with it, check once, subtly and as a colleague, that they stand behind it before it goes out. One light question, their call, never repeated.

## 5. The session as a source

Submit the session transcript with `submit_raw` first (title, the full transcript, the session's start time as `source_at`); it enters processed, since this session already extracted, and its id goes into every atom's `sources`.

## 6. Submit

Call `submit_atoms` with the confirmed batch, `sources` set when step 5 produced a raw. Errors come back per atom: fix those and resubmit only the failures, never anything unchanged.

## 7. Report

Accepted, by filename; left out, and why; the open questions this session could not answer, so the monthly raw review sees them. Then the verbatim list of corrections the human made.
