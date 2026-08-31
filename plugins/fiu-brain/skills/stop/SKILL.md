---
description: Close an FIU Brain session. Harvests what this session learned, lets the user react, and submits it to the brain.
disable-model-invocation: true
---

# /stop

You curate this session into the FIU Brain.

## 1. Gate

Call `whoami`. If the connector is missing, say so and stop. If `can_write` is false, explain kindly that this account's token has no brain-write ability, that reading is unaffected, and that `php artisan brain:token` (a founder or developer runs it) issues a writing token. Stop.

## 2. Extract

Load `fiu-brain:extraction-rules` and apply it to everything learned in this session, including what the user told you, not only what you produced. Everything you write is English.

Action items and missing-knowledge flags are atoms too; the extraction rules define both shapes. Nothing else: your own summaries and reasoning are not knowledge.

## 3. Show the harvest, then wait

Three blocks, most certain first, every line numbered so the user can react by number:

1. **Certain.** One compact list: title, kind, labels, clearance when not team. A single confirmation accepts them all.
2. **Doubtful.** One multiple choice per item: option A, option B, or skip. Never guess on the user's behalf.
3. **Proposals.** Named separately, with one line saying these go to the founders and are not truth until approved.

Nothing is sent before the user reacts. They may approve with a correction in one move ("akkoord, maar het was 1.200"): apply it and do not ask again. Record every correction verbatim for the report; that feedback is how the extraction rules get better.

## 4. Workslop check

If the session produced something that goes to a colleague or a client, apply the workslop check from `fiu-brain:guardrails` once. Never block, never repeat it.

## 5. The session as a source

When a raw-submission tool is available on the connector, submit the session transcript as a raw first, so its id can go into the atoms' `sources`. Until that tool exists, skip this silently; the atoms stand on their own.

## 6. Submit

Call `submit_atoms` with the confirmed batch, `sources` set when step 5 produced a raw. Errors come back per atom: fix those and resubmit only the failures, never anything unchanged.

## 7. Report

Two lines: accepted, by filename; left out, and why. Then the verbatim list of corrections the user made.
