---
description: Once per person. Turn a mailbox export into a filtered, consented package of mail sources for the FIU Brain. Runs locally; nothing personal ever leaves the laptop. Does not create atoms.
disable-model-invocation: true
---

# /mail-sweep

You turn a mailbox export into a package of sources. The script moves every byte; you read as little content as possible (the sender table, snippets, capped excerpts for the leftovers) and write verdict lines. `/process` makes the atoms later, after ingest.

Needs a shell (Claude Code or Cowork). Without one, say so and point at the runbook: export, then run this skill where a shell exists.

## 1. Scope and export

Confirm whose mailbox and which period (default: everything work-related, however old). The owner exports it themselves, which is what makes this opt-in. Walk them through it:

1. Optional narrowing: in Gmail, apply a label (say `brain-sweep`) to what they are willing to share; exporting everything and filtering here works too.
2. Go to takeout.google.com with the work account, choose "Deselect all", then tick only Mail.
3. Click "All Mail data included": keep everything, or tick specific labels; always include both Inbox and Sent, because a conversation lives half in each and the split merges them into one thread.
4. Next step: export once, `.zip`, 50GB size. Smaller sizes split the mailbox into numbered parts (`Inbox-001.mbox`, `Inbox-002.mbox`); parts are fine, keep them all.
5. Google mails a download link (minutes for small boxes, hours for gigabytes). Download, extract; the `.mbox` files sit under `Takeout/Mail/`.

Ask for the paths of all `.mbox` files, parts included; the split takes them in one run.

## 2. Split (script, no reading)

Run `scripts/mail_sweep.py split <workdir> <mbox> [<mbox> ...]`, all export files in one run so threads merge across them. It streams in two passes (headers, then byte slices), so memory stays flat however large the export; a multi-gigabyte mailbox takes minutes. For a first look before the real run, `--limit N` processes only the first N messages per file. It writes one folder per thread (`thread.mbox` verbatim, `thread.txt` decoded, `snippet.txt` first 3KB) and one `manifest.tsv`, ordered oldest thread first: thread id, last date, from, to, subject, message count, size, real attachment filenames (signature and footer images are filtered out), and an `auto` column. Mechanically detectable noise is already written to `verdicts.tsv` as `drop` with an `auto:` note, but only when the owner never engaged: every message in the thread must be list mail, a calendar invite, or from a no-reply sender, so one human reply keeps a thread alive. You never look at auto-dropped threads; the owner still sees them at review. Known cost: a single never-answered mail from a sender whose mail platform stamps list headers drops unseen; the mailbox of the colleague who answered it catches that conversation instead. Threads where every participant sits on an FIU domain (foodinfluencersunited.com, foodinfluencersunited.nl) also drop, as `auto:fiu-internal-only`: internal mail can carry classified content (contracts, founder-to-founder matters) that a sweep must never push into the brain, and one external participant anywhere in the thread lifts the rule. This also keeps wiki@ notes and self-mail out; internal knowledge reaches the brain through sessions, not mail sweeps. Threads touching financial or legal matters between the holding companies (loans, shareholder documents; the screen matches KMPI, RDPI, KIWI and aandeelhouder/lening terms in the decoded text) drop as `auto:holding-financial`, whoever participates. The owner can still overrule any single thread at review. You have read nothing yet.

## 3. Verdicts per sender, not per thread

Run `scripts/mail_sweep.py senders <workdir> --owner <address>`, repeating `--owner` for every address the owner sends from. It buckets the remaining threads by correspondent — the non-owner senders; for owner-only threads the recipients; pure self-mail as `(self)` — and writes `senders.tsv` with thread and mail counts, auto-dropped threads left out. Read that table instead of the manifest: one line per correspondent, recognisable by domain. Fill its verdict column: `include` (conversations with them belong in the brain), `exclude` (never work content: personal senders, billing, system and marketing mail), `partial` (genuinely mixed; rare, costs per-thread work later). Judge on content, not direction, and never quote anywhere: personal and private mail (health, family, anything not work) and employment matters (contracts, salaries, reviews, anything HR) are always `exclude`, and so is anything financial or legal between the FIU holding companies (loans between SFG and KMPI/RDPI/KIWI, shareholder documents), even when the split's keyword screen missed it.

Show the owner the filled table in those three buckets, largest mail count first; they correct at sender level and can ask what a sender writes — only then read that sender's snippets.

## 4. Apply, then triage only the leftovers

Run `scripts/mail_sweep.py apply-senders <workdir>`: a thread with at least one included correspondent goes `in` (clearance team), a thread with only excluded correspondents drops, and threads riding on `partial` senders alone are printed for manual triage. Triage just those few in `verdicts.tsv`, tab-separated: `thread_id`, verdict (`in`, `drop`, `sensitive`, `unsure`), clearance (empty means team), note. Judge from the manifest row; when that does not settle it, read `threads/<id>/snippet.txt`, then at most the first 10KB of `thread.txt`, never the whole file. A later line for the same id overrides an earlier one, so per-thread lines beat sender rules — this is also how the owner overrides any verdict at review. `sensitive` (suggested clearance `founders`) is for work content the team should not see: deal terms under wraps, founder-only strategy. `unsure` is honest; do not force it, but settle it before packaging. Bodies of `drop` threads are never opened.

## 5. The owner reviews, then approves

Run `scripts/mail_sweep.py review <workdir>`: it prints the verdict lists, subjects only. The owner corrects and approves. This is the consent gate; never skip it, never summarise it away. Nothing proceeds without their explicit yes.

## 6. Package and hand over

Run `scripts/mail_sweep.py package <workdir> <out.zip>`: only approved threads enter the zip, each as `.mbox` + `.txt` + `meta.json` (message ids, thread id, participants and senders, source date, clearance). Dropped threads never leave the laptop.

The zip goes to Rob for `php artisan brain:ingest-raws`. If it contains `sensitive` threads, hand it over through Drive or a protected archive, not plain mail. Report counts per verdict and anything that failed; remind the owner the drop list stays theirs and is never uploaded anywhere.
