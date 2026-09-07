---
description: Founders only. Work through the proposed company-wide atoms in one conversation, with the context to decide each one. Reached from /start when a founder chooses to approve company-wide atoms; not a session entry point of its own.
user-invocable: false
---

# Approve company-wide atoms

This flow is reached from `/start`, which established who you work with; reuse it. If this session did not run `/start`, take the identity from the `whoami:` line of the server instructions before anything else. The guardrails at the end of this skill apply for the whole session.

A company-wide atom applies to everyone, so it enters as `proposed` and becomes company truth only here. Scoped atoms never pass through this flow; they are live from the moment they are accepted.

## 1. Gate

If the connector is missing, say so and stop. If `can_approve` is false, say kindly that company-wide atoms are approved by founders, that everything else in the brain works as normal for this account, and that `/start` offers the goals that fit; stop.

If the `approve`, `decline` and `update_atom` tools are not on the connector, say up front which are missing and that this session can only prepare a decision list, then ask whether that is still wanted.

## 2. Load

`search` with `statuses: ["proposed"]`. Group by label rather than by date; a founder decides better on ten related claims than on ten unrelated ones. Within a group, most certain first.

## 3. Verify product claims against the code

Proposed atoms about how the product or the tech works (what a feature does, how an integration behaves, a limit, a rule the software applies) are checked against the FIU codebase before a founder approves them; the process flow does not check them, because approval is where company truth is minted and where a founder with code access is present.

- When the FIU codebase is among the session's working folders, send an agent over those atoms and mark each one verified, contradicted or not checkable. The verdict and what the code says go into the code check column of the tables in step 4, next to the claim. A contradicted claim is approved with an edit or declined, never approved as it stands.
- When the codebase is not available, say so once and ask whether the founder wants to add it before deciding. If they cannot or will not, leave the product claims open and continue with the rest; they wait for a founder who has code access.
- Never approve a product claim that was neither verified nor explicitly waived by the founder.

## 4. Present

Present the queue as tables, never as prose or a plain list. The tables are the decision screen: complete beats short here, whatever the guardrails say about length elsewhere.

- One table per label group, the group's label and the source citations above it. Columns: number, claim (the title), labels, source date, code (one word: verified, partly, contradicted, overtaken, not checkable, or a dash for a claim that is not about the product), decision (approve, edit, decline, open).
- Cells stay short: a title, slugs, a date, a word. A terminal lays a table out in columns only while every cell fits a line or two; a sentence in a cell turns the table back into prose with bars in it. Everything that needs a sentence goes under the table, by number.
- Number the atoms continuously across all the group tables, so the founder can answer "1 to 4 approve, 9 decline, 12 open" without naming a group.
- Under each table, one line per number that needs one: what the code says, with a file reference the founder can open, and for a contradicted or partly verified row what the edit or the decline would be; and the note, which is where your judgement surfaces: the doubt behind the decision, the row you would decline first, a clearance that could be lowered, a directly related live atom in half a sentence (one `search` on the title's key terms; do not go hunting further), a body that says more than its title. A group in which every note is empty is a group that hid its doubts.
- Bodies live under the table too. Give in full and by number the body of every row the founder must read to decide: a recommended edit (current body and proposed replacement, both in full), a contradiction, a supersession. Say once under the tables that the other bodies are available by number.
- When an atom carries `proposes_to_supersede`, `get` the target and show both as two numbered rows under the table, the proposed one first, so the founder sees what changes.
- Close with two or three sentences under the tables: how many proposals, how many are product claims and how the verdicts fell, and anything that blocks a decision, such as the codebase not being available or a contradiction with a live atom.

## 5. Decide, per group

The founder rules by number or by group, in one word where they can; walk the items one by one only where they ask. Do not walk group by group and do not summarise atoms back at them; the claims are the summary. Per item the founder can:

- approve
- approve with an edit: show the corrected title or body in full first, because the founder approves wording, not intention; then call `update_atom` with the corrected title, body, labels or clearance (a proposed atom is editable until it is decided; its filename stays), then approve it
- decline, always with a reason; the reason is what stops the claim coming back
- leave it open

Before approving anything that contradicts an existing company-wide atom, show both and ask which supersedes which; never resolve a contradiction yourself. Where clearance can be lowered, offer it: knowledge that arrived as founders material but is useful to the team should not stay locked up by accident.

## 6. Write

Call `update_atom`, `approve` and `decline`, one atom per call. Until those exist on the connector, produce the decisions as a clean list and say explicitly that nothing was written to the brain yet.

## 7. Report

Approved, declined with reasons, left open, and how many proposed atoms remain.

!`tail -n +6 "${CLAUDE_PLUGIN_ROOT}/skills/guardrails/SKILL.md"`
