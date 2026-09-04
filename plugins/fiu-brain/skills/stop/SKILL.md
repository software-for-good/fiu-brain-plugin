---
description: Close an FIU Brain session. Harvests what this session learned, lets the human react, and submits it to the brain.
disable-model-invocation: true
---

# /stop

You curate this session into the FIU Brain. If this session has not loaded `fiu:guardrails` (no `/start` ran), load it now.

## 1. Gate

Call `whoami`. If the connector is missing, say so and stop. If `can_write` is false, explain kindly that this account's token has no brain-write ability, that reading is unaffected, and that `php artisan brain:token` (a founder or developer runs it) issues a writing token. Stop.

## 2. Extract

Load `fiu:extraction-rules` and apply it to everything learned in this session, including what the human told you, not only what you produced. Everything you write is English.

Action items and absence claims are atoms too; the extraction rules define both shapes. Nothing else: your own summaries and reasoning are not knowledge.

## 3. Show the harvest, then wait

Three blocks, most certain first, every line numbered so the human can react by number:

1. **Certain.** One compact list: title, kind, labels, clearance when not team. A single confirmation accepts them all.
2. **Doubtful.** One multiple choice per item: option A, option B, or skip. Never guess on the human's behalf.
3. **Proposals.** Named separately, with one line saying these go to the founders and are not truth until approved.

Nothing is sent before the human reacts. They may approve with a correction in one move ("akkoord, maar het was 1.200"): apply it and do not ask again. Record every correction verbatim for the report; that feedback is how the extraction rules get better.

## 4. Standing behind it

When you sense the human is passing on AI-made material without having engaged with it, check once, subtly and as a colleague, that they stand behind it before it goes out. One light question, their call, never repeated.

## 5. The session as a source

Submit the session transcript with `submit_raw` first (title, the full transcript, the session's start time as `source_at`); it enters processed, since this session already extracted, and its id goes into every atom's `sources`. When the tool is not on the connector yet, skip this silently; the atoms stand on their own.

## 6. Submit

Call `submit_atoms` with the confirmed batch, `sources` set when step 5 produced a raw. Errors come back per atom: fix those and resubmit only the failures, never anything unchanged.

## 7. Report

Accepted, by filename; left out, and why; the open questions this session could not answer, so the monthly raw review sees them. Then the verbatim list of corrections the human made.
