---
description: Once per person. Turn a folder of exported meeting transcripts into a filtered, consented package of sources for the FIU Brain. Runs locally; nothing personal ever leaves the laptop. Does not create atoms and does not classify content.
disable-model-invocation: true
---

# /transcript-sweep

Same pipeline as `/mail-sweep`, simpler input: one export file per meeting, each opening with a header block (title, `Datum`, `Granola label`, `Voorstel labels`, `Deelnemers`, `Granola ID`), then a generated summary, then the transcript. Your only job here is the privacy gate: in or out, and at which clearance. Content classification, labels and atoms belong to `fiu:process`, after ingest, which applies its own second filter to every source; doing any of that here would duplicate the extraction rules and drift.

Needs a shell (Claude Code or Cowork). Expect hundreds to a few thousand exports per person.

## 1. Scope

Confirm whose transcripts, the folder path, and every address the owner appears under in `Deelnemers`. Files are stored verbatim, summary blocks included; `fiu:process` ignores the summary when extracting (knowledge is never built on a derived layer), but the source stays untouched.

## 2. Manifest (script, no reading)

Run `scripts/transcript_sweep.py manifest <folder> <workdir>`: one line per file with id, date, date source, size, a summary flag, the Granola label, the participants and the title, plus `meta/<id>.json` per file and a snippet under `snippets/`. The date comes from the filename (`YYYYMMDD`, the team's naming convention) first, then from the `Datum` line, and only then from the file's modification time; `date_source` says which, and `mtime` rows get a second look at review because a re-export stamps every file with the export day. Meetings touching financial or legal matters around the holding companies drop as `auto:holding-financial`, the same screen `/mail-sweep` uses; the owner still sees them at review. You have read nothing yet.

## 3. Verdicts per counterpart, not per meeting

Run `scripts/transcript_sweep.py participants <workdir> --owner <address>`, repeating `--owner` for every address of the owner. It buckets the remaining meetings by counterpart, every non-owner address in `Deelnemers`, meetings without one under `(unlisted)`, and writes `participants.tsv`: one line per counterpart with meeting count, last date, the Granola labels seen and example titles. Colleagues appear as counterparts like anyone else; an internal meeting is judged, not waved through. Fill the verdict column: `include` (meetings with them belong in the brain), `exclude` (never work content), `partial` (genuinely mixed; costs per-meeting work later). Judge on content and never quote: personal and private matters and anything HR (one-to-ones about performance, salary, contracts) are `exclude`, and so is anything financial or legal around the FIU holding companies that the screen missed.

Show the owner the filled table in those three buckets, largest first; they correct at counterpart level and can ask what a counterpart's meetings are about. Only then read that counterpart's snippets: the header and the start of the summary, never the transcript body.

## 4. Apply, then triage only the leftovers

Run `scripts/transcript_sweep.py apply-participants <workdir>`: a meeting with at least one included counterpart goes `in` (clearance team), a meeting with only excluded counterparts drops, and meetings riding on `partial` counterparts alone are printed for manual triage. Triage just those in `verdicts.tsv`, tab-separated: `file_id`, verdict (`in`, `drop`, `sensitive`, `unsure`), clearance (empty means team), note. Judge from the manifest row; when that does not settle it, read `snippets/<id>.txt`. Recurring meetings share a title stem: decide the series once and write the same verdict for each. A later line for the same id overrides an earlier one, so per-meeting lines beat counterpart rules; this is also how the owner overrides any verdict at review. `sensitive` (clearance `founders`) is for work content the team should not see: deal terms under wraps, founder-only strategy. `unsure` is honest; do not force it, but settle it before packaging.

## 5. The owner reviews, then approves

Run `scripts/transcript_sweep.py review <workdir>`: it prints the verdict lists, titles only, and flags files dated from their modification time. The owner corrects and approves. This is the consent gate; never skip it, never summarise it away. Nothing proceeds without their explicit yes.

## 6. Package and hand over

Run `scripts/transcript_sweep.py package <workdir> <out.zip>`: only approved meetings enter the zip, each as the export file verbatim plus `meta.json` (source date and where it came from, title, Granola id and labels, participants, clearance, type meeting_transcript). Dropped files never leave the laptop.

The zip goes to Rob for `php artisan brain:ingest-raws`. If it contains `sensitive` meetings, hand it over through Drive or a protected archive, not plain mail. Report counts per verdict and anything that failed; remind the owner the drop list stays theirs and is never uploaded anywhere.
