---
description: Turn the queue of unprocessed sources in the FIU Brain into atoms, in small batches, as a conversation. This is where classification, labels and extraction happen. Reached from /start when a founder chooses to process the queue; not a session entry point of its own.
user-invocable: false
---

# Process the queue

Ingest put sources in; you put knowledge in. Reading goes source by source, delivery per round, resume-safe. This flow is reached from `/start`, which has loaded `fiu:guardrails` and called `whoami`; reuse both. If this session did not run `/start`, load `fiu:guardrails` and call `whoami` now, before anything else.

## 1. Gate

If the connector is missing, say so and stop. If `can_write` is false, explain kindly that processing writes atoms and needs a brain-write token, and stop. Processing also needs a shell (Claude Code or Cowork) to fetch sources; without one, say so and stop.

## 2. Agree the scope

Ask two things in one message: which scope (one source type, or the whole queue) and how many sources this round. Default five. Processing always runs newest first (the server serves the queue that way): a correction that arrived five minutes after the thing it corrects is read first, and the stale version drops as covered instead of being created and immediately superseded in the same round. You only ever see sources at your own clearance; the server filters the rest.

## 3. Fetch and read, one source at a time

Load `fiu:extraction-rules` once, before the first fetch: you read every source with its bar in mind, and its yield expectations decide how much of a source is worth reading at all. Then `list_raws` for the scope; it returns each source's id and the endpoint template. Fetch a source into a local file by curling the `endpoint` URL the listing returned, `{id}` filled in, sending the same bearer token the connector uses (it sits in the session's MCP config; in Claude Code, `claude mcp get fiu-brain`). Then read it locally and selectively: sections, a grep for a speaker or a topic, a slice at a time; re-reads cost nothing. One source at a time: fetch, read and extract it before touching the next. For meeting transcripts, extract from the transcript body and ignore a generated summary block at the top: knowledge is never built on a derived layer.

If a source turns out personal or private: extract nothing, quote nothing, still mark it processed like any finished source so it stops resurfacing in the queue, and flag it in the report so Rob can remove the raw itself; that removal is a manual operation on purpose. A source that contains a credential (a bearer token, a password) is flagged the same way, for rotation and for removal from the raw.

## 4. Extract

Apply the extraction rules per source, `sources` set to the raw's id on every atom. Zero atoms is a normal outcome; say so and move on.

Run the funnel's compare step (extraction rules, step 8) on every candidate before it enters the round's list: new, duplicate, covered or conflict. Newest first makes most transitions surface naturally, because the source that announced a change is processed before the sources living under the old regime; the covered check is the net for changes no surviving source announced. Count covered drops and keep one-line examples for the report, so over-firing shows early.

## 5. Confirm, per round

Before showing the round, apply the two-claim test to every title: if the title splits into two sentences that each pass the bar, it is two atoms, whatever word joined them. One person per role atom.

Present the round as tables, never as prose or a plain list.

- One table per source, with the source's citation above it. Columns: number, claim (the title), kind, labels, note (a doubt, or a source detail the human needs to judge). Claims about how the product works are not checked against the code here; that happens when a founder approves them. Sources that yielded nothing are one line under the tables, together, with their count and ids.
- One table for everything that did not make it. Columns: candidate, reason. The reason names the funnel step: failed the bar and which condition, filtered and which line, covered, duplicate, conflict. Nothing is dropped silently.

The human confirms, corrects or skips by number. Do not walk through source by source and do not summarise sources back at them; the claims are the summary.

## 6. Submit and mark

`submit_atoms`, fix rejections, resubmit only those. Per source in the round, call `mark_raw_processed` once that source's atoms were accepted, or straight away when it has nothing to submit (zero candidates, everything dropped as duplicate or covered, personal). A source is marked exactly when it needs no more work, so an interrupted run resumes cleanly instead of losing or duplicating work.

Submit and mark every round before moving on: a source left unmarked is redone from scratch next run, and the corrections made on it are lost with it.

## 7. Report and continue

Per round, one table with one row per measure: sources processed, atoms accepted, atoms rejected with their reasons, candidates dropped per reason with counts (covered drops with one-line examples, so over-firing shows early), sources flagged for removal (personal material, a credential), sources left in scope. Then ask whether to continue with the next batch; stop when the human stops.
