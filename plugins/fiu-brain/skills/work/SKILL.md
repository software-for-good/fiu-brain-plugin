---
description: Work on a session goal with the FIU Brain: answer questions, think, draft. Reached from /start once the goal is known; not a session entry point of its own.
user-invocable: false
---

# Work with the brain

`/start` established who you work with and what for; reuse both. If this session did not run `/start`, take the identity from the `whoami:` line of the server instructions first. The guardrails at the end of this skill apply for the rest of the session.

## 1. Load context

Derive candidate labels from the goal and check them with the `labels` tool; never guess a slug. Call `context_pack` once, goal written in English, labels attached. Read it silently: company-wide atoms are company truth, scoped atoms are facts about one to a few named external parties, proposed atoms are not yet true and you say so whenever you lean on one. For anything before September 2026 the brain holds then-latest truths, notable milestones and important transitions only; older intermediate states were deliberately not backfilled. A gap in the deep past means "not recorded", never "it did not happen". Tell the human in one line how fresh the brain is and whether it holds anything on their topic; this is the only place that line belongs. When it holds nothing, say that plainly instead of filling the gap.

## 2. Work

- Cite atoms by filename when you use them; say when the brain has nothing rather than inventing FIU facts. Knowledge about FIU comes from the brain and the human, nowhere else.
- Look-up questions ("what do we know about X") get answered straight away, no friction: `search` with the right labels and English terms, answer from the atoms with filenames cited, nothing padded. If proposed atoms are all there is, answer with the caveat that founders have not confirmed them. End with the one-line source list.
- Generative work (a mail, a deck, a plan) waits until the human has given goal, audience and their own direction, per the guardrails.
- Before the first file of the session is created, load `fiu:work-folder` and follow it. A session that only answers questions never loads it.
- When the human states something that contradicts the brain, surface both and offer to record the correction at `/stop`.
- When the brain cannot answer a question, say so plainly. When the absence itself is worth recording (a colleague would act differently for knowing nothing is arranged), note an absence claim for `/stop`; every open question also lands in the `/stop` report.

## 3. Close

When the session produced anything worth remembering, remind the human to run `/stop`. Without `/stop`, nothing reaches the brain and no client history is built.

!`tail -n +6 "${CLAUDE_PLUGIN_ROOT}/skills/guardrails/SKILL.md"`
