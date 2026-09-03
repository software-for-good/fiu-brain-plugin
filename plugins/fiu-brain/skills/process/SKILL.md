---
description: Turn unprocessed sources in the FIU Brain into atoms, in small batches, as a conversation. This is where classification, labels and extraction happen.
disable-model-invocation: true
---

# /process

Ingest put sources in; you put knowledge in. One source at a time, resume-safe.

## 1. Gate

Call `whoami`. If the connector is missing, say so and stop. If `can_write` is false, explain kindly that processing writes atoms and needs a brain-write token, and stop. Processing also needs a shell (Claude Code or Cowork) to fetch sources; without one, say so and stop.

## 2. Agree the scope

Ask two things in one message: which scope (one person's sweep, one type, or the whole queue) and how many sources this round. Default five. Processing always runs newest first: a correction that arrived five minutes after the thing it corrects is read first, and the stale version drops as covered instead of being created and immediately superseded in the same round. You only ever see sources at your own clearance; the server filters the rest.

## 3. Fetch and read, one source at a time

Load `fiu:extraction-rules` once, before the first fetch: you read every source with its bar in mind, and its yield expectations decide how much of a source is worth reading at all. Then `list_raws` for the scope with `order` set to `desc`; it returns each source's id and the endpoint template. Fetch a source by curling `GET {mcp_path}/raws/{id}` (the same bearer token the connector uses) into a local file. Then read it locally and selectively: sections, a grep for a speaker or a topic, a slice at a time; re-reads cost nothing. One source at a time, never ahead. For meeting transcripts, extract from the transcript body and ignore a generated summary block at the top: knowledge is never built on a derived layer.

If a source turns out personal or private: extract nothing, quote nothing, and report it at the end so Rob can remove it; that removal is a manual operation on purpose.

## 4. Extract

Apply the extraction rules per source, `sources` set to the raw's id on every atom. Zero atoms is a normal outcome; say so and move on.

Before a candidate enters the round's list, `search` its entity labels. Four outcomes. New: keep it. Duplicate: drop it. Covered: the candidate is an older value of something a newer atom already answers; drop it, count it, and ask one question before moving on: does the change between then and now itself pass the bar? Usually not. When it does (a deliberate, reasoned shift in how FIU or a client works), the change becomes one atom, old and new named in the body, the moment of the change written out. Example: the brain holds "FIU prices campaigns as a percentage of media budget" (2025) and a 2022 mail prices a campaign at 450 euro per post. The 450 euro atom is never made; if the sources show the switch was a real 2023 decision, the atom is "In 2023 FIU moved campaign pricing from a fee per post to a percentage of media budget", with the old 450 euro fee in the body. Most transitions surface naturally anyway: newest first, the source that announced the change is processed before the sources living under the old regime, and the covered check is the net for changes no surviving source announced. Conflict: sources of the same age disagree; a proposal stating both values, per the rules. Events, decisions and reasons are never covered merely by being old. `supersedes` runs forward only, and stays in play: an atom from a newer source supersedes an older atom already in the brain; an older fact that would correct a newer atom is the rules' backfill-proposal case.

## 5. Verify the round

When the session has the codebase at hand, verify the round before showing it: send an agent over the claims that are about how the product or the tech works ("how does X work", "why doesn't Y work", what a feature does) and annotate each as verified, contradicted or not checkable; correct or drop contradicted claims and show the human what the code said. Verify nothing else: a claim the database could answer (subscription dates, prices, what is live) should not be an atom at all; that is bar test 2, applied at extraction, not an agent's search job. Without the codebase, skip this step and say so in the report.

## 6. Confirm, per round

Show the round's atoms as one compact numbered list grouped by source: title, kind, labels, and the verification note where one exists; zero-yield sources as a single count line. The human confirms, corrects or skips by number; do not walk through source by source and do not summarise sources back at them. The titles are the summary.

## 7. Submit and mark

`submit_atoms`, fix rejections, resubmit only those. Per source in the round, call `mark_raw_processed` only after that source's atoms were accepted, so an interrupted run resumes cleanly instead of losing or duplicating work.

## 8. Report and continue

Per round: sources processed, atoms accepted, rejected with reasons, dropped as covered (count plus one-line examples, so over-firing of the covered rule is visible early), personal sources flagged for removal, sources left in scope. Ask whether to continue with the next batch; stop when the human stops.
