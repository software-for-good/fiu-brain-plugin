---
description: Turn unprocessed sources in the FIU Brain into atoms, in small batches, as a conversation. This is where classification, labels and extraction happen.
disable-model-invocation: true
---

# /process

Ingest put sources in; you put knowledge in. One source at a time, resume-safe.

## 1. Gate

Call `whoami`. If the connector is missing, say so and stop. If `can_write` is false, explain kindly that processing writes atoms and needs a brain-write token, and stop. If the raw tools (`list_raws`, `mark_raw_processed`) are not on the connector, the server side of processing has not shipped yet: say exactly that and stop. Processing also needs a shell (Claude Code or Cowork) to fetch sources; without one, say so and stop.

## 2. Agree the scope

Ask two things in one message: which scope (oldest first, one person's sweep, one type) and how many sources this round. Default five. You only ever see sources at your own clearance; the server filters the rest.

## 3. Fetch and read, one source at a time

`list_raws` for the scope; it returns each source's id and the endpoint template. Fetch a source by curling `GET {mcp_path}/raws/{id}` (the same bearer token the connector uses) into a local file. Then read it locally and selectively: sections, a grep for a speaker or a topic, a slice at a time; re-reads cost nothing. One source at a time, never ahead. Work in chronological order so a later source can supersede an earlier one. For meeting transcripts, extract from the transcript body and ignore a generated summary block at the top: knowledge is never built on a derived layer.

If a source turns out personal or private: extract nothing, quote nothing, and report it at the end so Rob can remove it; that removal is a manual operation on purpose.

## 4. Extract

Load `fiu:extraction-rules` and apply it per source, `sources` set to the raw's id on every atom. Mind the yield expectations in the rules; zero atoms is a normal outcome, say so and move on.

## 5. Confirm, per source

Show the atoms as one compact numbered list of title, kind and labels. The human confirms, corrects or skips by number; do not walk through them one by one and do not summarise the source back at them. The titles are the summary.

## 6. Submit and mark

`submit_atoms`, fix rejections, resubmit only those. Call `mark_raw_processed` only after the source's atoms were accepted, so an interrupted run resumes cleanly instead of losing or duplicating work.

## 7. Report and continue

Per round: sources processed, atoms accepted, rejected with reasons, personal sources flagged for removal, sources left in scope. Ask whether to continue with the next batch; stop when the human stops.
