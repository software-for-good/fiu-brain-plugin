---
description: Turn the queue of unprocessed sources in the FIU Brain into atoms, in small batches, as a conversation: which sources, in what order, how a round is shown and confirmed, and what is written back. The rules for what becomes an atom are in fiu:extraction-rules. Reached from /start when a founder chooses to process the queue; not a session entry point of its own.
user-invocable: false
---

# Process the queue

You process source (raws) into knowledge. Reading goes source by source, delivery per round, resume-safe. This flow is reached from `/start`, which established who you work with and carries the guardrails that apply for the whole session; reuse both. If this session did not run `/start`, take the identity from the `whoami:` line of the server instructions and load `fiu:guardrails` before anything else.

Load `fiu:extraction-rules` before the first source is fetched. It owns what counts as an atom and how one is written, labelled, scoped and compared with the brain; this skill never restates those rules, it names the step and sets when it runs. What is left here is the loop: which sources, in what order, how they are fetched, how a round is shown and confirmed, and what is written back.

## 1. Gate

If the connector is missing, say so and stop. If the role is not `founder`, say kindly that only a founder can mark a source processed, that everything else in the brain works as normal for this account, and that `/start` offers the goals that fit; stop. If `can_write` is false, explain kindly that processing writes atoms and needs a brain-write token, and stop. Processing also needs a shell (Claude Code or Cowork) to fetch sources; without one, say so and stop.

## 2. Agree the scope

Ask two things in one message: which scope (one source type, or the whole queue) and how many sources this round. Default five. Processing always runs newest first (the server serves the queue that way): a correction that arrived five minutes after the thing it corrects is read first, and the stale version drops as covered instead of being created and immediately superseded in the same round. You only ever see sources at your own clearance; the server filters the rest.

## 3. Fetch and read, one source at a time

Call `list_raws` for the scope; it returns each source's id and the endpoint template. Fetch a source into a local file by curling the `endpoint` URL the listing returned, `{id}` filled in, sending the same bearer token the connector uses (it sits in the session's MCP config; in Claude Code, `claude mcp get fiu-brain`). Then read it locally and selectively: sections, a grep for a speaker or a topic, a slice at a time; re-reads cost nothing. One source at a time: fetch, read and extract it before touching the next. Read each source the way extraction rules step 1 prescribes for its type, and let the yields of step 2 decide how much of it is worth reading at all.

A source that turns out personal or private yields nothing (extraction rules, step 7) and is proposed for deletion in the round's confirm step: a source without atoms can go, row and hosted file at once, and it is the human who says so. A source that contains a credential (a bearer token, a password) is proposed the same way, for deletion and for rotation. Until the human decides, the source is neither marked nor deleted.

## 4. Extract

Apply the extraction rules per source, `sources` set to the raw's id on every atom.

The compare step needs two `index` calls, and this skill sets only when they run: the company-wide one once per round, before the first candidate of the round is judged, and the party one once per source, once that source's parties are known. Step 8 carries their arguments. The context pack of the session start replaces neither: it is budgeted, and it predates the previous round's atoms.

Every candidate goes through step 8 before it enters the round's list. Newest first makes most transitions surface naturally, because the source that announced a change is processed before the sources living under the old regime; the covered check is the net for changes no surviving source announced. Count covered drops and keep one-line examples for the report, so over-firing shows early.

## 5. Confirm, per round

A candidate the split rule (extraction rules, step 3) breaks in two is shown pre-split, as two numbered rows, with a note on the second row saying the two can be merged back; the human then merges by number instead of reconstructing your reasoning.

Present the round as tables, never as prose or a plain list.

- One table per source, with the source's citation above it. Columns: number, claim (the title), kind, labels, note (a doubt, or a source detail the human needs to judge). Claims about how the product works are not checked against the code here; that happens when a founder approves them.
- Number the claims continuously across all the source tables of the round, so the human can answer "2 drop, 17 prospect" without naming a source.
- Sources that yielded nothing get one sentence together under the tables, with their citations and ids. A table with no rows says less than a sentence does.
- One table for everything that did not make it. Columns: candidate, reason. The reason names the funnel step: failed the bar and which condition, filtered and which line, covered, duplicate, conflict. Nothing is dropped silently.
- The note column is where your judgement surfaces. Use it for a label you could argue either way, for the atom you would cut first if the human cuts one, and for a claim that only just passed the bar. A round in which every note is empty is a round that hid its doubts.
- Close with two or three sentences under the drop table: the covered drops as a fraction of all candidates, so over-firing shows early, and anything the human must know before confirming.

The human confirms, corrects or skips by number. Do not walk through source by source and do not summarise sources back at them; the claims are the summary.

## 6. Submit and mark

`submit_atoms`, fix rejections, resubmit only those. Per source in the round, call `mark_raw_processed` once that source's atoms were accepted, or straight away when it has nothing to submit (zero candidates, everything dropped as duplicate or covered). A source is marked exactly when it needs no more work, so an interrupted run resumes cleanly instead of losing or duplicating work.

A source the human agreed to delete is deleted instead of marked: `delete_raw` with its id removes the row and the hosted file in the same call, and the source is gone from the queue for good. The server refuses a source that any atom already cites; then mark it processed and flag it in the report for a founder to sort out by hand.

Submit and mark every round before moving on: a source left unmarked is redone from scratch next run, and the corrections made on it are lost with it.

## 7. Report and continue

Per round, one table with one row per measure: sources processed, atoms accepted, atoms rejected with their reasons, what the human dropped or corrected in the confirm step, candidates dropped per reason with counts (covered drops with one-line examples, so over-firing shows early), sources deleted (personal material, a credential) and sources that could not be deleted because atoms cite them, sources left in scope. Name under the table every free label (`person/`, `partner/`, `prospect/`) that was created on first use this round, so the vocabulary never grows unnoticed. Then ask whether to continue with the next batch; stop when the human stops.
