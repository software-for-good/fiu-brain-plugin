---
description: Turn the queue of unprocessed sources in the FIU Brain into atoms, in small batches, as a conversation. This is where classification, labels and extraction happen. Reached from /start when a founder chooses to process the queue; not a session entry point of its own.
user-invocable: false
---

# Process the queue

Ingest put sources in; you put knowledge in. Reading goes source by source, delivery per round, resume-safe. This flow is reached from `/start`, which established who you work with; reuse it. If this session did not run `/start`, take the identity from the `whoami:` line of the server instructions before anything else. The guardrails at the end of this skill apply for the whole session.

## 1. Gate

If the connector is missing, say so and stop. If `can_write` is false, explain kindly that processing writes atoms and needs a brain-write token, and stop. Processing also needs a shell (Claude Code or Cowork) to fetch sources; without one, say so and stop.

## 2. Agree the scope

Ask two things in one message: which scope (one source type, or the whole queue) and how many sources this round. Default five. Processing always runs newest first (the server serves the queue that way): a correction that arrived five minutes after the thing it corrects is read first, and the stale version drops as covered instead of being created and immediately superseded in the same round. You only ever see sources at your own clearance; the server filters the rest.

## 3. Fetch and read, one source at a time

Load `fiu:extraction-rules` once, before the first fetch: you read every source with its bar in mind, and its yield expectations decide how much of a source is worth reading at all. At the start of every round call `index` with no arguments: the title of every company-wide atom, approved and still proposed, one line each. The context pack's index is budgeted and does not carry the previous round's atoms or a founder's decisions since; this call is complete and current, and it is what the compare step judges against. Then `list_raws` for the scope; it returns each source's id and the endpoint template. Fetch a source into a local file by curling the `endpoint` URL the listing returned, `{id}` filled in, sending the same bearer token the connector uses (it sits in the session's MCP config; in Claude Code, `claude mcp get fiu-brain`). Then read it locally and selectively: sections, a grep for a speaker or a topic, a slice at a time; re-reads cost nothing. One source at a time: fetch, read and extract it before touching the next. For meeting transcripts, extract from the transcript body and ignore a generated summary block at the top: knowledge is never built on a derived layer.

If a source turns out personal or private: extract nothing, quote nothing, and propose its deletion in the round's confirm step; a source without atoms can go, row and hosted file at once, and it is the human who says so. A source that contains a credential (a bearer token, a password) is proposed the same way, for deletion and for rotation. Until the human decides, the source is neither marked nor deleted.

## 4. Extract

Apply the extraction rules per source, `sources` set to the raw's id on every atom. Once the source's parties are known, call `index` with their labels (`websites/`, `partner/`, `prospect/`, `person/`) and statuses `["scoped", "company_wide", "proposed"]`: everything the brain holds on those parties, titles only, one call per source. Zero atoms is a normal outcome; say so and move on.

Run the funnel's compare step (extraction rules, step 8) on every candidate before it enters the round's list, against the round's index and the source's party index: new, duplicate, covered or conflict. Newest first makes most transitions surface naturally, because the source that announced a change is processed before the sources living under the old regime; the covered check is the net for changes no surviving source announced. Count covered drops and keep one-line examples for the report, so over-firing shows early.

## 5. Confirm, per round

Before showing the round, apply the two-claim test to every title: if the title splits into two sentences that each pass the bar, it is two atoms, whatever word joined them. One person per role atom. Show such a split pre-split, as two numbered rows, and say in the note of the second row that the two can be merged back; the human then merges by number instead of reconstructing your reasoning.

Present the round as tables, never as prose or a plain list.

- One table per source, with the source's citation above it. Columns: number, claim (the title), kind, labels, note (a doubt, or a source detail the human needs to judge). Claims about how the product works are not checked against the code here; that happens when a founder approves them.
- Number the claims continuously across all the source tables of the round, so the human can answer "2 drop, 17 prospect" without naming a source.
- Sources that yielded nothing get one sentence together under the tables, with their citations and ids. A table with no rows says less than a sentence does.
- One table for everything that did not make it. Columns: candidate, reason. The reason names the funnel step: failed the bar and which condition, filtered and which line, covered, duplicate, conflict. Nothing is dropped silently.
- The note column is where your judgement surfaces. Use it for a label you could argue either way, for the atom you would cut first if the human cuts one, and for a claim that only just passed the bar. A round in which every note is empty is a round that hid its doubts.
- Close with two or three sentences under the drop table: the covered drops as a fraction of all candidates, so over-firing shows early, and anything the human must know before confirming, such as a source proposed for deletion (its citation, and why).

The human confirms, corrects or skips by number. Do not walk through source by source and do not summarise sources back at them; the claims are the summary.

## 6. Submit and mark

`submit_atoms`, fix rejections, resubmit only those. Per source in the round, call `mark_raw_processed` once that source's atoms were accepted, or straight away when it has nothing to submit (zero candidates, everything dropped as duplicate or covered). A source is marked exactly when it needs no more work, so an interrupted run resumes cleanly instead of losing or duplicating work.

A source the human agreed to delete is deleted instead of marked: `delete_raw` with its id removes the row and the hosted file in the same call, and the source is gone from the queue for good. The server refuses a source that any atom already cites; then mark it processed and flag it in the report for a founder to sort out by hand. When `delete_raw` is not on the connector yet, do the same: mark it processed and flag it for manual removal.

Submit and mark every round before moving on: a source left unmarked is redone from scratch next run, and the corrections made on it are lost with it.

## 7. Report and continue

Per round, one table with one row per measure: sources processed, atoms accepted, atoms rejected with their reasons, what the human dropped or corrected in the confirm step, candidates dropped per reason with counts (covered drops with one-line examples, so over-firing shows early), sources deleted (personal material, a credential) and sources that could not be deleted because atoms cite them, sources left in scope. Name under the table every free label (`person/`, `partner/`, `prospect/`) that was created on first use this round, so the vocabulary never grows unnoticed. Then ask whether to continue with the next batch; stop when the human stops.

!`tail -n +6 "${CLAUDE_PLUGIN_ROOT}/skills/guardrails/SKILL.md"`
