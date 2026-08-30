---
description: Close an FIU Brain session. Harvests what this session learned and submits it to the brain.
disable-model-invocation: true
---

1. Load the `fiu-brain:extraction-rules` skill and apply it to everything learned in this session.
2. Show the harvest in three blocks, sorted by certainty: certain (one summarising confirmation), doubtful (multiple choice per item), candidate proposals (named separately). Offer any unanswered question as missing knowledge.
3. After the user confirms, call `submit_atoms`. Fix rejected atoms from the returned errors and submit them again.
4. Report what was accepted, by filename, and what was left out.

This is a short stub; the full skill follows.
