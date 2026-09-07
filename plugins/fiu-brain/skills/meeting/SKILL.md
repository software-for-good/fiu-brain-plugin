---
description: Prepare a client meeting with the FIU Brain: pull what the brain holds on the client, think it through with the human, then draft. Reached from /start; not a session entry point of its own.
user-invocable: false
---

# Prepare a client meeting

`/start` established who you work with; reuse it. If this session did not run `/start`, take the identity from the `whoami:` line of the server instructions first. The guardrails at the end of this skill apply for the rest of the session.

## 1. Resolve

If the goal did not name them, ask which client and which meeting in one question. Resolve the client label (`websites/...`) and the people (`person/...`) via the `labels` tool; never guess a slug.

## 2. Pull

`context_pack` once with those labels, the goal in English; `search` for the client name and the open threads. Read silently: company-wide atoms are company truth, scoped atoms are facts about one to a few named external parties, proposed atoms are not yet true and you say so whenever you lean on one. Present it as three short blocks, each line cited by filename: what we know, what is in motion, contradictions or gaps. Say in one line how fresh what the brain holds on this client is; when it holds nothing, say that plainly instead of filling the gap.

## 3. Think it through

The thinking questions, one at a time, to the human: what do you want out of this meeting, what does the client want, when do you walk out happy? Their answers lead; you sharpen.

## 4. Draft

Only then draft the agenda or talking points, in their voice. Before the first file of the session is created, load `fiu:work-folder` and follow it. Gaps and contradictions found along the way are candidate flags for `/stop`; when the human states something that contradicts the brain, surface both and offer to record the correction there.

## 5. Close

Remind the human to run `/stop`: the preparation itself is client history the brain should hold.

!`tail -n +6 "${CLAUDE_PLUGIN_ROOT}/skills/guardrails/SKILL.md"`
