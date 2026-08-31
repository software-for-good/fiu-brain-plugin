#!/usr/bin/env python3
"""FIU Brain mail sweep: split an mbox into thread folders plus a manifest,
pre-verdict the mechanically detectable drops, print the review lists, package
the approved threads. Stdlib only. The AI reads manifest and snippets and
appends to verdicts.tsv; this script moves every byte.

verdicts.tsv columns: thread_id<TAB>verdict<TAB>clearance<TAB>note
verdicts: in | drop | sensitive | unsure. Later lines for the same id win.
The verdict-parsing helpers are kept in sync with transcript_sweep.py.
"""
import json
import mailbox
import re
import sys
import zipfile
from datetime import datetime, timezone
from email.header import decode_header, make_header
from email.utils import parsedate_to_datetime
from html import unescape
from pathlib import Path

SNIPPET_BYTES = 3000
CLEARANCES = ("public", "team", "founders")
EPOCH = datetime(1970, 1, 1, tzinfo=timezone.utc)
NOREPLY = re.compile(r"^(no-?reply|noreply|notifications?|mailer-daemon|calendar-notification|do-?not-?reply)@", re.I)


def decoded(value):
    if value is None:
        return ""
    try:
        return str(make_header(decode_header(value))).replace("\t", " ").replace("\n", " ").strip()
    except Exception:
        return str(value)[:200]


def body_text(message):
    plain, html_fallback = [], []
    for part in message.walk():
        if part.get_content_maintype() == "multipart":
            continue
        content_type = part.get_content_type()
        if content_type not in ("text/plain", "text/html"):
            continue
        try:
            payload = part.get_payload(decode=True) or b""
            text = payload.decode(part.get_content_charset() or "utf-8", errors="replace")
        except Exception:
            continue
        if content_type == "text/plain":
            plain.append(text)
        else:
            text = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", text, flags=re.S | re.I)
            html_fallback.append(unescape(re.sub(r"<[^>]+>", " ", text)))
    chosen = plain if plain else html_fallback
    return re.sub(r"[ \t]+", " ", "\n".join(chosen)).strip()


def thread_key(message):
    gm_thrid = message.get("X-GM-THRID")
    if gm_thrid:
        return f"g{gm_thrid.strip()}"
    subject = re.sub(r"^(re|fwd?|fw)(\[\d+\])?:\s*", "", decoded(message.get("Subject")).lower()).strip()
    references = (message.get("References") or message.get("In-Reply-To") or "").split()
    anchor = references[0] if references else (message.get("Message-ID") or subject or "none")
    return "t" + re.sub(r"[^a-z0-9]", "", (subject + anchor).lower())[:40]


def message_date(message):
    try:
        parsed = parsedate_to_datetime(message.get("Date"))
    except Exception:
        return None
    if parsed is None:
        return None
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)


def auto_verdict(messages):
    for message in messages:
        if message.get("List-Id") or message.get("List-Unsubscribe"):
            return "auto:newsletter-or-list"
        if any(part.get_content_type() == "text/calendar" for part in message.walk()):
            return "auto:calendar-invite"
    sender = decoded(messages[-1].get("From"))
    address = sender.split("<")[-1].strip("> ")
    if NOREPLY.match(address):
        return "auto:notification-sender"
    return None


def split(mbox_path, workdir):
    workdir = Path(workdir)
    threads_dir = workdir / "threads"
    threads_dir.mkdir(parents=True, exist_ok=True)
    threads = {}
    for message in mailbox.mbox(mbox_path):
        threads.setdefault(thread_key(message), []).append(message)

    auto_lines = []
    with open(workdir / "manifest.tsv", "w", encoding="utf-8") as manifest:
        manifest.write("thread_id\tdate\tfrom\tto\tsubject\tmessages\tsize_kb\tattachments\tauto\n")
        for index, (key, messages) in enumerate(sorted(threads.items()), start=1):
            messages.sort(key=lambda m: message_date(m) or EPOCH)
            thread_id = f"{index:04d}-{key[:24]}"
            folder = threads_dir / thread_id
            folder.mkdir(exist_ok=True)
            box = mailbox.mbox(folder / "thread.mbox")
            box.lock()
            try:
                box.clear()
                for message in messages:
                    box.add(message)
                box.flush()
            finally:
                box.unlock()
                box.close()
            text = "\n\n---\n\n".join(
                f"From: {decoded(m.get('From'))}\nDate: {decoded(m.get('Date'))}\n\n{body_text(m)}" for m in messages
            )
            (folder / "thread.txt").write_text(text, encoding="utf-8")
            (folder / "snippet.txt").write_text(text[:SNIPPET_BYTES], encoding="utf-8")
            last_date = message_date(messages[-1]) or message_date(messages[0])
            (folder / "meta.json").write_text(json.dumps({
                "thread_id": thread_id,
                "message_ids": [decoded(m.get("Message-ID")) for m in messages if m.get("Message-ID")],
                "participants": sorted({decoded(m.get("From")) for m in messages} | {decoded(m.get("To")) for m in messages if m.get("To")}),
                "subject": decoded(messages[-1].get("Subject")),
                "source_at": last_date.isoformat() if last_date else None,
                "messages": len(messages),
            }, ensure_ascii=False, indent=2), encoding="utf-8")
            auto = auto_verdict(messages)
            if auto:
                auto_lines.append(f"{thread_id}\tdrop\t\t{auto}")
            size_kb = max(1, sum(len(m.as_bytes()) for m in messages) // 1024)
            manifest.write("\t".join([
                thread_id,
                last_date.date().isoformat() if last_date else "unknown",
                decoded(messages[-1].get("From"))[:60],
                decoded(messages[-1].get("To"))[:60],
                decoded(messages[-1].get("Subject"))[:120],
                str(len(messages)),
                str(size_kb),
                "yes" if any(p.get_filename() for m in messages for p in m.walk()) else "no",
                auto or "",
            ]) + "\n")
    (workdir / "verdicts.tsv").write_text("\n".join(auto_lines) + ("\n" if auto_lines else ""), encoding="utf-8")
    print(f"threads: {len(threads)}; auto-dropped: {len(auto_lines)}; manifest: {workdir / 'manifest.tsv'}")


def read_verdicts(workdir):
    verdict_path = Path(workdir) / "verdicts.tsv"
    if not verdict_path.exists():
        sys.exit("verdicts.tsv not found; triage the manifest first")
    verdicts = {}
    for number, line in enumerate(verdict_path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        fields = line.split("\t")
        if len(fields) < 2 or fields[1] not in ("in", "drop", "sensitive", "unsure"):
            sys.exit(f"verdicts.tsv line {number} is malformed: {line[:80]!r}")
        clearance = fields[2].strip() if len(fields) > 2 and fields[2].strip() else "team"
        if clearance not in CLEARANCES:
            sys.exit(f"verdicts.tsv line {number}: clearance must be one of {CLEARANCES}, got {clearance!r}")
        verdicts[fields[0]] = (fields[1], clearance)
    return verdicts


def manifest_rows(workdir):
    lines = (Path(workdir) / "manifest.tsv").read_text(encoding="utf-8").splitlines()[1:]
    return {line.split("\t")[0]: line.split("\t") for line in lines if line.strip()}


def coverage_check(workdir, verdicts):
    missing = sorted(set(manifest_rows(workdir)) - set(verdicts))
    return missing


def review(workdir):
    verdicts = read_verdicts(workdir)
    rows = manifest_rows(workdir)
    for bucket in ("in", "sensitive", "drop", "unsure"):
        ids = [t for t, (v, _) in verdicts.items() if v == bucket]
        print(f"\n== {bucket} ({len(ids)})")
        for thread_id in sorted(ids):
            fields = rows.get(thread_id, [])
            print(f"  {thread_id}  {fields[4] if len(fields) > 4 else ''}")
    missing = coverage_check(workdir, verdicts)
    if missing:
        print(f"\n!! {len(missing)} threads have no verdict yet: {', '.join(missing[:10])}{' ...' if len(missing) > 10 else ''}")


def package(workdir, out_zip):
    verdicts = read_verdicts(workdir)
    missing = coverage_check(workdir, verdicts)
    if missing:
        sys.exit(f"{len(missing)} threads have no verdict; the owner's approval must cover everything. Missing: {', '.join(missing[:10])}")
    unsure = [t for t, (v, _) in verdicts.items() if v == "unsure"]
    if unsure:
        sys.exit(f"{len(unsure)} threads still unsure; settle them before packaging")
    count = 0
    with zipfile.ZipFile(out_zip, "w", zipfile.ZIP_DEFLATED) as bundle:
        for thread_id, (verdict, clearance) in sorted(verdicts.items()):
            if verdict not in ("in", "sensitive"):
                continue
            folder = Path(workdir) / "threads" / thread_id
            if not folder.is_dir():
                sys.exit(f"verdict names unknown thread {thread_id}; no such folder under threads/")
            meta = json.loads((folder / "meta.json").read_text(encoding="utf-8"))
            meta["clearance"] = "founders" if verdict == "sensitive" else clearance
            meta["type"] = "mail_thread"
            bundle.writestr(f"{thread_id}/meta.json", json.dumps(meta, ensure_ascii=False, indent=2))
            bundle.write(folder / "thread.mbox", f"{thread_id}/thread.mbox")
            bundle.write(folder / "thread.txt", f"{thread_id}/thread.txt")
            count += 1
    print(f"packaged {count} threads into {out_zip}; dropped threads stayed local")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        sys.exit("usage: mail_sweep.py split <mbox> <workdir> | review <workdir> | package <workdir> <out.zip>")
    command = sys.argv[1]
    if command == "split":
        split(sys.argv[2], sys.argv[3])
    elif command == "review":
        review(sys.argv[2])
    elif command == "package":
        package(sys.argv[2], sys.argv[3])
    else:
        sys.exit(f"unknown command {command}")
