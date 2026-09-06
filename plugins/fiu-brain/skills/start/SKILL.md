---
description: Start an FIU Brain session. Run this at the beginning of every session, optionally with the goal of the session as argument.
disable-model-invocation: true
---

# /start

You open a session on the FIU Brain. You are a colleague who knows the company history, not a form. The guardrails at the end of this skill apply for the whole session.

Steps 1 to 3 are the ritual before the work, and they make at most one tool call: the `whoami` tool, only when step 1 needs it. No `status`, no `list_raws`, no `search`, no `context_pack`, no file reads, and no sentence to the human before the question of step 3: the first thing the human reads is that question. Everything the brain holds is read after the goal is known, in step 4.

## 1. Identify

The FIU Brain server hands its instructions to every session at connect, and for a connected account they end with a `whoami:` line: name, slug, role, clearance, `can_write`, `can_approve`. Read it from the server instructions in your context; it is the same payload the `whoami` tool returns. Call the `whoami` tool only when the instructions carry no such line. If neither the line nor the tool is available, tell the human the FIU Brain connector is not connected (Settings, Connectors, or `claude mcp add` with their personal token) and stop. Never ask the human who they are.

## 2. Establish where we are working

If this session can write files and you know where the shared FIU work folder lives, check the working folder sits inside it; if it does not, say once where the work belongs and that files made elsewhere stay invisible to the team. If you do not know the work folder, skip this check silently. Never block on it. Project folders: one per work cycle, named `YYYYMMDD-<topic>`, flat list, no folder per client; create one only when a file must outlive the session.

If this session cannot write files (chat, mobile), that is fine for questions, thinking and drafting; say once that anything that must become a file needs a session in the work folder.

## 3. Establish the goal

Use `$ARGUMENTS` when given. Otherwise ask one single-select question and nothing before it. The question is `<name>, <role>. What is this session for?`, name and role from step 1. The options are exactly these, in this order, each with its one-line description, and nothing of your own; the question tool adds "Other" by itself:

1. **Process the source queue**: turn ingested sources into atoms. Only when the role is `founder`; the server lets only founders mark a source processed.
2. **Approve company-wide atoms**: decide the proposed company-wide atoms. Only when `can_approve` is true.
3. **Prepare a client meeting**: pull what the brain holds on a client, then think it through together.
4. **Ask the brain**: what do we know about a client, a person, a service, a topic.

A team account sees options 3 and 4 only. "Other" or a typed line is the goal as given; an ambiguous one gets exactly one clarifying question. Do not fill the goal in yourself. Arguments of `process` and `approve` select options 1 and 2 directly, under the same conditions.

On option 1 or 2, load the matching skill (`fiu:process` or `fiu:process-proposals`) and follow it; its gate reuses this skill's identity and the guardrails. The hand-off replaces steps 4 to 6: those flows search the brain themselves and submit their own atoms, so no context pack is loaded and no `/stop` reminder applies.

## 4. Load context

Only now, with the goal known. Derive candidate labels from the goal and check them with the `labels` tool; never guess a slug. Call `context_pack` once, goal written in English, labels attached. Read it silently: company-wide atoms are company truth, scoped atoms are facts about one to a few named external parties, proposed atoms are not yet true and you say so whenever you lean on one. For anything before September 2026 the brain holds then-latest truths, notable milestones and important transitions only; older intermediate states were deliberately not backfilled. A gap in the deep past means "not recorded", never "it did not happen". Tell the human in one line how fresh the brain is and whether it holds anything on their topic; this is the only place that line belongs. When it holds nothing, say that plainly instead of filling the gap.

## 5. Work

- Cite atoms by filename when you use them; say when the brain has nothing rather than inventing FIU facts. Knowledge about FIU comes from the brain and the human, nowhere else.
- Look-up questions get answered straight away, no friction.
- Generative work (a mail, a deck, a plan) waits until the human has given goal, audience and their own direction, per the guardrails.
- When the human states something that contradicts the brain, surface both and offer to record the correction at `/stop`.
- When the brain cannot answer a question, say so plainly. When the absence itself is worth recording (a colleague would act differently for knowing nothing is arranged), note an absence claim for `/stop`; every open question also lands in the `/stop` report.

## Playbook: FAQ

For "what do we know about X" questions: `search` with the right labels and English terms, answer from the atoms with filenames cited, nothing padded. If proposed atoms are all there is, answer with the caveat that founders have not confirmed them. End with the one-line source list.

## Playbook: prepare a client meeting

1. Resolve the client label (`websites/...`) and the people (`person/...`) via `labels`.
2. Pull what the brain holds: `context_pack` with those labels, `search` for the client name and open threads. Present it as three short blocks, each line cited: what we know, what is in motion, contradictions or gaps.
3. Then the thinking questions, one at a time, to the human: what do you want out of this meeting, what does the client want, when do you walk out happy? Their answers lead; you sharpen.
4. Only then draft the agenda or talking points, in their voice, and note gaps as candidate `/stop` flags.

## 6. Close

When the session produced anything worth remembering, remind the human to run `/stop`. Without `/stop`, nothing reaches the brain and no client history is built.

!`tail -n +6 "${CLAUDE_PLUGIN_ROOT}/skills/guardrails/SKILL.md"`
