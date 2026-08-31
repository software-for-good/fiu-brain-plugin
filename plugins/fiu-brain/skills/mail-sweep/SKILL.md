---
description: Once per person. Turn a mailbox export into a filtered, consented package of mail sources for the FIU Brain. Runs locally; nothing personal ever leaves the laptop. Does not create atoms.
disable-model-invocation: true
---

# /mail-sweep

You turn a mailbox export into a package of sources. The script moves every byte; you read as little content as possible (the manifest, snippets, capped excerpts for the unsure) and write verdict lines. `/process` makes the atoms later, after ingest.

Needs a shell (Claude Code or Cowork). Without one, say so and point at the runbook: export, then run this skill where a shell exists.

## 1. Scope and export

Confirm whose mailbox and which period (default: everything work-related, however old). The owner exports it themselves, which is what makes this opt-in: Google Takeout, mail only, optionally limited to a label they applied first. Ask for the path to the `.mbox` file.

## 2. Split (script, no reading)

Run `scripts/mail_sweep.py split <mbox> <workdir>`. It writes one folder per thread (`thread.mbox` verbatim, `thread.txt` decoded, `snippet.txt` first 3KB) and one `manifest.tsv`: thread id, last date, from, to, subject, message count, size, attachments, and an `auto` column. Mechanically detectable noise (newsletters and lists, calendar invites, no-reply senders) is already written to `verdicts.tsv` as `drop` with an `auto:` note; you do not triage those, and the owner still sees them at review. You have read nothing yet.

## 3. Triage the manifest

Read `manifest.tsv` in chunks of a few hundred lines and append one verdict per remaining thread to `verdicts.tsv`, tab-separated: `thread_id`, verdict (`in`, `drop`, `sensitive`, `unsure`), clearance (empty means team), note. A later line for the same id overrides an earlier one, so you can also overrule an `auto:` drop. Judge on content, not direction; an internal thread recording a client decision is `in`.

Always `drop`, and never quote anywhere:

- personal and private mail: health, family, anything not work
- employment matters: contracts, salaries, reviews, anything HR
- newsletters, notifications, invoices, system mail, calendar invitations
- threads that only arrange logistics

`sensitive` (suggested clearance `founders`) is for work content the team should not see: deal terms under wraps, founder-only strategy. `unsure` is honest; do not force it.

## 4. Snippets for the unsure

For each `unsure`, read `threads/<id>/snippet.txt` only; when the snippet does not settle it, read at most the first 10KB of `thread.txt`, never the whole file. Update the verdict. Bodies of `drop` threads are never opened.

## 5. The owner reviews, then approves

Run `scripts/mail_sweep.py review <workdir>`: it prints the three lists, subjects only. The owner corrects and approves. This is the consent gate; never skip it, never summarise it away. Nothing proceeds without their explicit yes.

## 6. Package and hand over

Run `scripts/mail_sweep.py package <workdir> <out.zip>`: only approved threads enter the zip, each as `.mbox` + `.txt` + `meta.json` (message ids, thread id, participants, source date, clearance). Dropped threads never leave the laptop.

The zip goes to Rob for `php artisan brain:ingest-raws`. If it contains `sensitive` threads, hand it over through Drive or a protected archive, not plain mail. Report counts per verdict and anything that failed; remind the owner the drop list stays theirs and is never uploaded anywhere.
