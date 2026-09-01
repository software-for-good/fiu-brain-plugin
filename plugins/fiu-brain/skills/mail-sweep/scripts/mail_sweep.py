#!/usr/bin/env python3
"""FIU Brain mail sweep: split one or more mbox exports into thread folders
plus a manifest, pre-verdict mechanically detectable drops, print the review
lists, package the approved threads. Stdlib only; memory stays flat however
large the mailbox, and Inbox/Sent exports merge into one thread when they
share a Gmail thread id; a message exported in both files counts once.

Usage:
  mail_sweep.py split <workdir> <mbox> [<mbox> ...] [--limit N]
  mail_sweep.py review <workdir>
  mail_sweep.py package <workdir> <out.zip>

verdicts.tsv columns: thread_id<TAB>verdict<TAB>clearance<TAB>note
verdicts: in | drop | sensitive | unsure. Later lines for the same id win.
The verdict-parsing helpers are kept in sync with transcript_sweep.py.
"""
import json
import re
import sys
import zipfile
from datetime import datetime, timezone
from email import message_from_bytes
from email.header import decode_header, make_header
from email.parser import BytesHeaderParser
from email.utils import parsedate_to_datetime
from html import unescape
from pathlib import Path

SNIPPET_BYTES = 3000
HEADER_CAP = 64 * 1024
CLEARANCES = ("public", "team", "founders")
EPOCH = datetime(1970, 1, 1, tzinfo=timezone.utc)
NOREPLY = re.compile(r"^(no-?reply|noreply|notifications?|mailer-daemon|calendar-notification|do-?not-?reply)@", re.I)


def decoded(value):
    """Header values fold across lines (CR, LF, tabs); the manifest is a TSV, so every kind of
    whitespace collapses to one space in both the decode path and the fallback."""
    if value is None:
        return ""
    try:
        text = str(make_header(decode_header(value)))
    except Exception:
        text = str(value)[:200]
    return re.sub(r"[\r\n\t\s]+", " ", text).strip()


def message_date(message):
    try:
        parsed = parsedate_to_datetime(message.get("Date"))
    except Exception:
        return None
    if parsed is None:
        return None
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)


def thread_key(message):
    gm_thrid = message.get("X-GM-THRID")
    if gm_thrid:
        return f"g{gm_thrid.strip()}"
    subject = re.sub(r"^(re|fwd?|fw)(\[\d+\])?:\s*", "", decoded(message.get("Subject")).lower()).strip()
    references = (message.get("References") or message.get("In-Reply-To") or "").split()
    anchor = references[0] if references else (message.get("Message-ID") or subject or "none")
    return "t" + re.sub(r"[^a-z0-9]", "", (subject + anchor).lower())[:40]


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


def scan_offsets(mbox_paths, limit):
    """Pass 1: per message, record (file_index, start, end) and its parsed headers only."""
    header_parser = BytesHeaderParser()
    records = []
    for file_index, mbox_path in enumerate(mbox_paths):
        seen = 0
        with open(mbox_path, "rb") as handle:
            offset = 0
            start = None
            header_bytes = b""
            in_headers = False
            for line in handle:
                if line.startswith(b"From "):
                    if start is not None:
                        records.append((file_index, start, offset, header_parser.parsebytes(header_bytes)))
                    seen += 1
                    if limit and seen > limit:
                        start = None
                        break
                    start = offset
                    header_bytes = b""
                    in_headers = True
                elif in_headers:
                    if line in (b"\n", b"\r\n"):
                        in_headers = False
                    elif len(header_bytes) < HEADER_CAP:
                        header_bytes += line
                offset += len(line)
            if start is not None:
                records.append((file_index, start, offset, header_parser.parsebytes(header_bytes)))
    return records


def auto_verdict(headers_list, has_calendar):
    for headers in headers_list:
        if headers.get("List-Id") or headers.get("List-Unsubscribe"):
            return "auto:newsletter-or-list"
    if has_calendar:
        return "auto:calendar-invite"
    sender = decoded(headers_list[-1].get("From"))
    address = sender.split("<")[-1].strip("> ")
    if NOREPLY.match(address):
        return "auto:notification-sender"
    return None


def split(workdir, mbox_paths, limit):
    workdir = Path(workdir)
    threads_dir = workdir / "threads"
    threads_dir.mkdir(parents=True, exist_ok=True)

    records = scan_offsets(mbox_paths, limit)
    threads = {}
    for record in records:
        threads.setdefault(thread_key(record[3]), []).append(record)

    def last_date(thread_records):
        dates = [message_date(headers) for _, _, _, headers in thread_records]
        return max((d for d in dates if d), default=EPOCH)

    ordered = sorted(threads.items(), key=lambda item: last_date(item[1]))
    handles = [open(path, "rb") for path in mbox_paths]
    auto_lines = []

    try:
        with open(workdir / "manifest.tsv", "w", encoding="utf-8") as manifest:
            manifest.write("thread_id\tdate\tfrom\tto\tsubject\tmessages\tsize_kb\tattachments\tauto\n")
            for index, (key, thread_records) in enumerate(ordered, start=1):
                thread_records.sort(key=lambda record: message_date(record[3]) or EPOCH)
                thread_id = f"{index:04d}-{key[:24]}"
                folder = threads_dir / thread_id
                folder.mkdir(exist_ok=True)

                texts = []
                message_ids = []
                participants = set()
                has_attachments = False
                has_calendar = False
                size = 0
                written = 0
                seen_ids = set()
                headers_list = [record[3] for record in thread_records]

                with open(folder / "thread.mbox", "wb") as thread_mbox:
                    for file_index, start, end, headers in thread_records:
                        header_id = decoded(headers.get("Message-ID"))
                        if header_id and header_id in seen_ids:
                            continue
                        if header_id:
                            seen_ids.add(header_id)
                        written += 1
                        handles[file_index].seek(start)
                        raw = handles[file_index].read(end - start)
                        thread_mbox.write(raw)
                        if not raw.endswith(b"\n"):
                            thread_mbox.write(b"\n")
                        size += len(raw)
                        message = message_from_bytes(raw.split(b"\n", 1)[1] if raw.startswith(b"From ") else raw)
                        texts.append(f"From: {decoded(message.get('From'))}\nDate: {decoded(message.get('Date'))}\n\n{body_text(message)}")
                        if message.get("Message-ID"):
                            message_ids.append(decoded(message.get("Message-ID")))
                        participants.add(decoded(message.get("From")))
                        if message.get("To"):
                            participants.add(decoded(message.get("To")))
                        for part in message.walk():
                            if part.get_filename():
                                has_attachments = True
                            if part.get_content_type() == "text/calendar":
                                has_calendar = True

                text = "\n\n---\n\n".join(texts)
                (folder / "thread.txt").write_text(text, encoding="utf-8")
                (folder / "snippet.txt").write_text(text[:SNIPPET_BYTES], encoding="utf-8")

                last = headers_list[-1]
                thread_last_date = last_date(thread_records)
                (folder / "meta.json").write_text(json.dumps({
                    "thread_id": thread_id,
                    "message_ids": message_ids,
                    "participants": sorted(participants),
                    "subject": decoded(last.get("Subject")),
                    "source_at": thread_last_date.isoformat() if thread_last_date != EPOCH else None,
                    "messages": written,
                }, ensure_ascii=False, indent=2), encoding="utf-8")

                auto = auto_verdict(headers_list, has_calendar)
                if auto:
                    auto_lines.append(f"{thread_id}\tdrop\t\t{auto}")

                manifest.write("\t".join([
                    thread_id,
                    thread_last_date.date().isoformat() if thread_last_date != EPOCH else "unknown",
                    decoded(last.get("From"))[:60],
                    decoded(last.get("To"))[:60],
                    decoded(last.get("Subject"))[:120],
                    str(written),
                    str(max(1, size // 1024)),
                    "yes" if has_attachments else "no",
                    auto or "",
                ]) + "\n")
    finally:
        for handle in handles:
            handle.close()

    (workdir / "verdicts.tsv").write_text("\n".join(auto_lines) + ("\n" if auto_lines else ""), encoding="utf-8")
    print(f"messages: {len(records)}; threads: {len(threads)}; auto-dropped: {len(auto_lines)}; manifest: {workdir / 'manifest.tsv'}")


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
    return sorted(set(manifest_rows(workdir)) - set(verdicts))


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
    arguments = sys.argv[1:]
    if len(arguments) < 2:
        sys.exit(__doc__.strip().split("Usage:")[1].split("verdicts.tsv")[0].strip())
    command = arguments[0]
    if command == "split":
        limit = 0
        if "--limit" in arguments:
            flag_index = arguments.index("--limit")
            limit = int(arguments[flag_index + 1])
            del arguments[flag_index:flag_index + 2]
        split(arguments[1], arguments[2:], limit)
    elif command == "review":
        review(arguments[1])
    elif command == "package":
        package(arguments[1], arguments[2])
    else:
        sys.exit(f"unknown command {command}")
