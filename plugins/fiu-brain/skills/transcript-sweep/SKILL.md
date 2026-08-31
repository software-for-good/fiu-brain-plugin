---
description: Once per person. Turn a folder of exported meeting transcripts into a filtered, consented package of sources for the FIU Brain. Runs locally. Does not create atoms and does not classify content.
disable-model-invocation: true
---

# /transcript-sweep

Same pipeline as `/mail-sweep`, simpler input: the export already has one file per meeting. Your only job here is the privacy gate: in or out. Content classification, labels and atoms belong to `/process`, after ingest; doing any of that here would duplicate the extraction rules and drift.

Needs a shell. Expect a folder of up to several hundred Granola exports; some start with a generated summary, some do not.

## 1. Scope

Confirm whose transcripts and the folder path. Files are stored verbatim, summary blocks included; `/process` ignores the summary when extracting (knowledge is never built on a derived layer), but the source stays untouched.

## 2. Manifest (script, no reading)

Run `scripts/transcript_sweep.py manifest <folder> <workdir>`: one line per file with id, date (from the filename, else file time), size, a summary-present flag and a title (first real line, falling back to the filename), plus a snippet per file under `snippets/`.

## 3. Triage, deliberately light

Well over 99 percent of these are work. Judge from the manifest line alone: verdict `in` by default, `drop` when the title clearly says personal, `sensitive` (clearance founders) when the title says founders-only business such as deal terms or HR-adjacent strategy, `unsure` when the title says nothing. For `unsure`, read the snippet in `snippets/<id>.txt` only. Append verdicts to `verdicts.tsv`, tab-separated: `file_id`, verdict, clearance (empty means team), note; a later line for the same id wins. Do not read full transcripts to hunt for the one personal meeting; a stray personal transcript gets caught at `/process` and reported for removal, which is the accepted trade.

## 4. The owner reviews, then approves

`scripts/transcript_sweep.py review <workdir>` prints the lists, titles only. The owner corrects and approves; nothing proceeds without their yes.

## 5. Package and hand over

`scripts/transcript_sweep.py package <workdir> <out.zip>`: approved files verbatim plus `meta.json` each (source date, title, clearance, type meeting_transcript). Zip goes to Rob for `php artisan brain:ingest-raws`; dropped files never leave the laptop. Report the counts.
