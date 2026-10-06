---
description: Once per person. Turn a mailbox export into a filtered, consented package of mail sources for the FIU Brain. Runs locally; nothing personal ever leaves the laptop. Does not create atoms.
disable-model-invocation: true
---

# /mail-sweep

You help a colleague, the owner, turn their mailbox export into a package of sources. The script moves every byte; you read as little as possible and say what you read; the owner decides, twice: per sender on a page in their browser, and at the final check. `fiu:process` makes the atoms later, after ingest.

A sweep is a session entry point of its own, so the guardrails are not in your context: load `fiu:guardrails` now; they apply for the rest of the session.

Needs a shell (Claude Code or Cowork). Without one, say so and point at the runbook: export, then run this skill where a shell exists.

## How you talk

The owner is handing you their mailbox. Every message should make it easy to trust what happens to it:

- **The whole route first.** Before the first step, say what will happen, the two moments they decide, what you read and what you never read, and that nothing leaves the laptop before they approve the package. The opening below.
- **Their words, not the script's.** Conversation (not thread), sender, set aside, goes into the brain, stays out. Name a file, column or command only when they ask.
- **Say what you read.** At every step, say what you looked at and what you did not. Until step 5 that includes: no mail opened.
- **Numbers, not adjectives.** How many conversations, senders, changes; never "most" or "a lot".
- **Their choice is final.** Never change it and never re-argue it. If you think a choice is a mistake, say so once with your reason, then follow it.
- **No pressure.** They can stop and pick up later; the page keeps their choices in their browser.
- **Plain about problems.** When something fails, say what failed and what it means for their mail.
- **Gates are shown, not summarised.** The brevity rule never shortens what the owner decides on: the page, the record of their choices, the final check.
- Talk in the owner's language; the page itself is in English.

The opening, in your own words:

> Here is how this goes. You decide twice, and nothing leaves this laptop until you approve the package at the end; then it goes to Rob for the brain.
> 1. You export your mail from Google; I walk you through it.
> 2. A script on this laptop splits it into conversations and sets aside, unread, what never belongs: newsletters, calendar invites, automated mail, mail between FIU colleagues only, and paperwork around the holding companies.
> 3. I advise per sender, from their name, address, how much you mailed and two subject lines. I open no mail for this.
> 4. You choose per sender on a page in your browser: include, partial or exclude. Your choice is final.
> 5. I read only the conversations that a sender you marked partial is on, and leave out what doesn't belong. Then you check the result before anything is packaged.

## 1. Scope and export

Confirm whose mailbox and which period (default: everything work-related, however old). The owner exports it themselves, which is what makes this opt-in. Walk them through it:

1. Optional narrowing: in Gmail, apply a label (say `brain-sweep`) to what they are willing to share; exporting everything and filtering here works too.
2. Go to takeout.google.com with the work account, choose "Deselect all", then tick only Mail.
3. Click "All Mail data included": keep everything, or tick specific labels; always include both Inbox and Sent, because a conversation lives half in each and the split merges them into one thread.
4. Next step: export once, `.zip`, 50GB size. Smaller sizes split the mailbox into numbered parts (`Inbox-001.mbox`, `Inbox-002.mbox`); parts are fine, keep them all.
5. Google mails a download link (minutes for small boxes, hours for gigabytes). Download, extract; the `.mbox` files sit under `Takeout/Mail/`.

Ask for the paths of all `.mbox` files, parts included; the split takes them in one run.

## 2. Split (script, no reading)

Run `scripts/mail_sweep.py split <workdir> <mbox> [<mbox> ...]`, all export files in one run so threads merge across them. It streams in two passes (headers, then byte slices), so memory stays flat however large the export; a multi-gigabyte mailbox takes minutes. For a first look before the real run, `--limit N` processes only the first N messages per file. It writes one folder per thread (`thread.mbox` verbatim, `thread.txt` decoded, `snippet.txt` first 3KB) and one `manifest.tsv`, ordered oldest thread first: thread id, last date, from, to, subject, message count, size, real attachment filenames (signature and footer images are filtered out), and an `auto` column.

What it sets aside goes into `verdicts.tsv` as `drop` with an `auto:` note, and nobody reads it:

- `newsletter-or-list`, `calendar-invite`, `notification-sender`: only when the owner never engaged; every message in the thread must be list mail, a calendar invite or from a no-reply sender, so one human reply keeps a thread. Known cost: a single never-answered mail from a sender whose mail platform stamps list headers goes unseen; the colleague who answered it catches that conversation in their own sweep.
- `fiu-internal-only`: every participant on an FIU domain (foodinfluencersunited.com, foodinfluencersunited.nl). Internal mail can carry classified content (contracts, founder-to-founder matters) that a sweep must never push into the brain; one external participant anywhere in the thread lifts the rule. Internal knowledge reaches the brain through sessions, not sweeps.
- `holding-financial`: what is left, when its text touches the holding companies: "Software for Good" or `SFG` (uppercase), KMPI, RDPI, KIWI as a company, shareholders (`aandeelhoud...`), loan agreements. The screen reads the subject and what people wrote, never who wrote it: sender names, quoted From/To lines and e-mail addresses do not count, so mail from a sender called Software for Good is judged by its text. A KvK number does not count either; partners print it in every signature. These are the only set-aside conversations the owner sees listed at the final check, because a word decided them, not a person.

Tell the owner the counts per kind, in their words. You have read nothing yet.

## 3. Your advice per sender

Run `scripts/mail_sweep.py senders <workdir> --owner <address>`, repeating `--owner` for every address the owner sends from. It writes `senders.tsv`: one line per correspondent of the conversations left (the non-owner senders; for owner-only threads the recipients; pure self-mail as `(self)`), with display name, domain, kind (`company`, `private`, `colleague`, `self`), conversation and mail counts, last date and two subjects. It holds facts only, so running it again loses no decision.

Write your advice in `advice.tsv`, tab-separated: an `address` or `@domain`, then `include`, `partial` or `exclude`, then a reason of a few words. A domain line covers everyone at that company; an address line beats it. Private mail services (gmail.com and the like) take no domain line: judge those people one by one. Judge from the table only; open no mail for this:

- `include`: conversations with them belong in the brain: clients, prospects, partners, influencers, suppliers about the work.
- `exclude`: never work content: personal and private contacts (health, family, anything not work), employment matters (contracts, salaries, reviews, anything HR), whoever handles the holding companies' money and paperwork (accountants, notaries, banks, subsidy advisers), billing, system and marketing senders.
- `partial`: genuinely mixed, so the AI reads every conversation they are on. Say in the reason what is mixed.

The owner reads your reasons on the page: plain, short, never quoting mail, never more private than needed ("personal", not what it is about). Include beats exclude (step 5): nobody writes confidential things with an included contact on the conversation, so excluding someone never keeps a conversation with an included contact out. A partial sender anywhere sends a conversation to the AI, so colleagues who also handle holding, HR or founder matters are usually `partial`.

## 4. The owner chooses (the first gate)

Only when every sender has advice, run `scripts/mail_sweep.py page <workdir> --open`. It refuses while advice is missing or the sender list is out of date, so the owner never sees a half list; it writes `sender-choices.html` into the workdir and opens it in their browser. If no browser opened (Cowork), tell them where the file is and to open it in Chrome or Firefox. Never mention or show the page before this moment.

The page groups senders per company domain, the highest mail volume first, with your advice in pencil and their choice in ink. A company that is all include or all exclude is folded into one line, which keeps the page short; the owner opens or folds any company with a click. A bar shows live where their conversations land: into the brain unread, read by the AI first, staying out, and each sender shows how the others on its conversations change that. Their choices save in their browser as they go, so closing the tab loses nothing, and the page has no internet access.

Tell them, in your own words:

> Your page is open. For each sender you choose include, partial or exclude; my advice is filled in, change anything you like. Companies that are all include or all exclude are folded into one line; click a name to see who is in it. Include wins over exclude: a conversation with an included sender on it goes in. A partial sender on a conversation means I read it first. Take your time; everything saves in your browser. When you're done, click "I'm done" and paste what it gives you here.

Then wait. Do not apply, summarise or move on until the hand-over arrives. If they ask what a sender writes, read that sender's `threads/<id>/snippet.txt` files and answer without quoting; that is the only reading allowed before the hand-over.

When they paste the hand-over, write it verbatim to `<workdir>/handover.txt` and run `scripts/mail_sweep.py record-choices <workdir> <workdir>/handover.txt`. It checks that the paste is complete and belongs to this sweep and this advice, then writes `choices.tsv`, the owner's verdict per sender, sealed: only this command writes it, and apply-senders and package refuse an edited one. Never change a choice yourself; a change is a new hand-over from the page, which still holds their choices. If you change the advice after building the page, rebuild it and ask for a new hand-over; record-choices refuses the old one.

Reflect back what it printed, in their words: senders per choice, every sender they changed from your advice, and where their conversations land. That is the record of their decision; then move on.

## 5. Apply, then read the conversations a partial sender is on

Run `scripts/mail_sweep.py apply-senders <workdir>`. Per conversation:

- a partial sender on it: you read it, whoever else is on it. The command lists these with every sender's choice, and marks them `unsure` until you decide;
- otherwise an included sender on it: it goes in, unread, clearance team, also when an excluded sender is on it;
- otherwise, excluded senders only: it stays out, unread.

So partial decides, for every conversation a partial sender is on, whether it goes in.

Tell the owner how many conversations you are about to read, and whose. Per conversation: the manifest row first; when that does not settle it, `threads/<id>/snippet.txt`; then at most the first 10KB of `thread.txt`, never the whole file. You judge confidentiality yourself; the owner names nothing per sender. Leave out what does not belong in a shared brain: personal and private matters, employment matters, the holding companies' money and paperwork, mail that is no work content at all. Work content the team should not read (deal terms under wraps, founder-only strategy) goes in as `sensitive`, clearance `founders`. Write one line per conversation in `verdicts.tsv`, tab-separated: `thread_id`, verdict (`in`, `drop`, `sensitive`, `unsure`), clearance (empty means team), and the note `triage: <reason in a few words>`, never a quote. `unsure` is honest; the owner settles it at the check. A later line for the same id wins.

## 6. The owner checks (the second gate)

Run `scripts/mail_sweep.py review <workdir>`. It counts every conversation per reason and lists in full only what no person decided on the page: what you read and decided, with your reasons; the holding paperwork the screen set aside; sensitive; unsure. Show it in full, in their words; `--all` lists everything when they ask.

They can pull any conversation in or out: write their call as a line with the note `owner: <their reason>`; it beats every other line, and apply-senders never overrides it. Settle every unsure with them. This is the consent gate for the package: nothing proceeds without their explicit yes.

## 7. Package and hand over

Run `scripts/mail_sweep.py package <workdir> <out.zip>`: it refuses without the owner's recorded choices or while anything is unsure, and only approved threads enter the zip, each as `.mbox` + `.txt` + `meta.json` (message ids, thread id, participants and senders, source date, clearance). Dropped threads never leave the laptop.

The zip goes to Rob for `php artisan brain:ingest-raws`. If it contains `sensitive` threads, hand it over through Drive or a protected archive, not plain mail. Report counts per verdict and anything that failed; remind the owner the drop list stays theirs and is never uploaded anywhere.
