#!/usr/bin/env python3
"""FIU Brain mail sweep: split one or more mbox exports into thread folders plus a
manifest, set aside mechanically detectable mail unread, build the page on which the
owner chooses per sender, record and apply those choices, print the review, package
the approved threads. Stdlib only; memory stays flat however large the mailbox, and
Inbox/Sent exports merge into one thread when they share a Gmail thread id; a message
exported in both files counts once.

Usage:
  mail_sweep.py split <workdir> <mbox> [<mbox> ...] [--limit N]
  mail_sweep.py senders <workdir> --owner <address> [--owner <address> ...]
  mail_sweep.py page <workdir> [--open]
  mail_sweep.py record-choices <workdir> <handover.txt>
  mail_sweep.py apply-senders <workdir>
  mail_sweep.py review <workdir> [--all]
  mail_sweep.py package <workdir> <out.zip>

advice.tsv, written by the AI: address or @domain<TAB>include|partial|exclude<TAB>reason.
choices.tsv, written only by record-choices: the owner's verdict per sender.
verdicts.tsv columns: thread_id<TAB>verdict<TAB>clearance<TAB>note
verdicts: in | drop | sensitive | unsure. Later lines for the same id win. The note says
who decided: auto: (the split), sender: and sender-excluded: (the owner's choices),
triage: (the AI, for threads with a partial sender on them), owner: (the owner, per thread).
The verdict-parsing helpers are kept in sync with transcript_sweep.py.
"""
import hashlib
import json
import re
import sys
import zipfile
from collections import Counter
from datetime import datetime, timezone
from email import message_from_bytes
from email.header import decode_header, make_header
from email.parser import BytesHeaderParser
from email.utils import getaddresses, parsedate_to_datetime
from html import unescape
from pathlib import Path

SNIPPET_BYTES = 3000
HEADER_CAP = 64 * 1024
CLEARANCES = ("public", "team", "founders")
SENDER_VERDICTS = ("include", "partial", "exclude")
EPOCH = datetime(1970, 1, 1, tzinfo=timezone.utc)
NOREPLY = re.compile(r"^(no-?reply|noreply|notifications?|mailer-daemon|calendar-notification|do-?not-?reply)@", re.I)
ADDRESS = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
INTERNAL_DOMAINS = ("foodinfluencersunited.com", "foodinfluencersunited.nl")
# Private mail services are not a company: their addresses are judged one by one.
PRIVATE_PROVIDERS = {"gmail", "googlemail", "hotmail", "outlook", "live", "msn", "icloud", "me", "mac",
                     "yahoo", "ymail", "aol", "gmx", "proton", "protonmail", "pm"}
PRIVATE_DOMAINS = {"kpnmail.nl", "kpnplanet.nl", "planet.nl", "ziggo.nl", "home.nl", "xs4all.nl", "hetnet.nl",
                   "chello.nl", "casema.nl", "upcmail.nl", "telfort.nl", "tele2.nl", "quicknet.nl", "zeelandnet.nl",
                   "online.nl", "caiway.nl", "solcon.nl", "versatel.nl", "telenet.be", "skynet.be"}
SIGNATURE_FILENAME = re.compile(r"^(image(\d{3,})?\.(png|jpe?g|gif)|oledata\.mso|~wrd.*\.jpg|logo.*\.(png|jpe?g|gif)|signature.*\.(png|jpe?g))$", re.I)
FOOTER_LOGO_MAX_BYTES = 30_000
# Financial/legal matters around the holding companies (SFG, written out as Software for
# Good, and KMPI/RDPI/KIWI): loans, shareholder documents. Bare "kiwi" is fruit in a food
# company's mail, so it only counts uppercase or with corporate context; SFG only counts
# uppercase. Bare "kvk" is not on the list: Dutch partners print their KvK number in every
# signature. The screen reads screen_text(), never sender names or addresses.
HOLDING_FINANCIAL = re.compile(
    r"(?i:\b(?:kmpi|rdpi)\b)"
    r"|\bKIWI\b"
    r"|(?i:\bkiwi\s*(?:b\.?\s?v\.?\b|holding|beheer))"
    r"|(?i:aandeelhoud|leningsovereenkomst|geldlening)"
    r"|(?i:software ?for ?good)|\bSFG\b"
)
# Lines in a mail body that say who wrote or received a quoted message.
QUOTED_PARTY_LINE = re.compile(r"^[>\s]*(?:from|van|to|aan|cc|bcc|reply-to|antwoord aan|sender|afzender)\s*:", re.I)
QUOTED_WROTE_LINE = re.compile(r"^[>\s]*(?:on|op)\b.{0,200}\b(?:wrote|schreef)\b", re.I)
TEMPLATE = Path(__file__).resolve().parent.parent / "assets" / "sender-choices.html"
HANDOVER_HEAD = re.compile(r"sweep\s+(\w+)\s*\|\s*advice\s+(\w+)\s*\|\s*(\d+)\s+senders")
HANDOVER_LINE = re.compile(r"^(include|partial|exclude)\s+(\S+)(?:\s+\(advice:\s*\w+\))?$")
HANDOVER_TOTALS = re.compile(r"totals:\s*include\s+(\d+)\s*\|\s*partial\s+(\d+)\s*\|\s*exclude\s+(\d+)")


def is_real_attachment(part):
    """A signature/footer image is not a real attachment; only count parts a sender
    actually meant to share as a file. Gmail marks pasted signature images as
    attachment-disposition with a generic name (image.png, 50KB banners included),
    so images are judged by name always and by size when embedded via cid:."""
    filename = part.get_filename()
    if not filename:
        return False
    if not part.get_content_type().startswith("image/"):
        return True
    if SIGNATURE_FILENAME.match(decoded(filename)):
        return False
    if not ("inline" in (part.get("Content-Disposition") or "").lower() or part.get("Content-ID")):
        return True
    try:
        size = len(part.get_payload(decode=True) or b"")
    except Exception:
        size = 0
    return size >= FOOTER_LOGO_MAX_BYTES


def addresses(value):
    return [address.lower() for address in ADDRESS.findall(decoded(value))]


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


def screen_text(subject, bodies):
    """What the holding screen reads: the subject and what people wrote, never who wrote
    it. Header lines, quoted From/To lines and addresses stay out, so mail from a sender
    called Software for Good is judged by its text, and the name in that text counts."""
    kept = [subject]
    for body in bodies:
        kept.extend(ADDRESS.sub(" ", line) for line in body.splitlines()
                    if not (QUOTED_PARTY_LINE.match(line) or QUOTED_WROTE_LINE.match(line)))
    return "\n".join(kept)


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


def auto_verdict(headers_list, calendar_flags, participant_addresses, screen):
    """Set aside, unread, what the owner never engaged with: every message must look like
    list, calendar or robot mail, so one human reply anywhere keeps the thread.
    FIU-internal-only threads go too, so classified internal mail (contracts,
    founder-to-founder matters) can never leak into the brain through a sweep; one
    external participant anywhere in the thread lifts that rule. What is left drops when
    its text touches the holding companies, whoever participates; checking that last
    means every auto:holding-financial thread is one the owner's sender choices would
    otherwise have decided, so the review lists exactly those."""
    if all(h.get("List-Id") or h.get("List-Unsubscribe") for h in headers_list):
        return "auto:newsletter-or-list"
    if calendar_flags and all(calendar_flags):
        return "auto:calendar-invite"
    if all(NOREPLY.match(decoded(h.get("From")).split("<")[-1].strip("> ")) for h in headers_list):
        return "auto:notification-sender"
    if participant_addresses and all(a.split("@")[-1] in INTERNAL_DOMAINS for a in participant_addresses):
        return "auto:fiu-internal-only"
    if HOLDING_FINANCIAL.search(screen):
        return "auto:holding-financial"
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
    auto_kinds = Counter()

    try:
        with open(workdir / "manifest.tsv", "w", encoding="utf-8") as manifest:
            manifest.write("thread_id\tdate\tfrom\tto\tsubject\tmessages\tsize_kb\tattachments\tauto\n")
            for index, (key, thread_records) in enumerate(ordered, start=1):
                thread_records.sort(key=lambda record: message_date(record[3]) or EPOCH)
                thread_id = f"{index:04d}-{key[:24]}"
                folder = threads_dir / thread_id
                folder.mkdir(exist_ok=True)

                texts = []
                bodies = []
                message_ids = []
                participants = set()
                sender_counts = {}
                recipients = set()
                calendar_flags = []
                attachment_names = []
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
                        body = body_text(message)
                        texts.append(f"From: {decoded(message.get('From'))}\nDate: {decoded(message.get('Date'))}\n\n{body}")
                        bodies.append(body)
                        if message.get("Message-ID"):
                            message_ids.append(decoded(message.get("Message-ID")))
                        participants.add(decoded(message.get("From")))
                        if message.get("To"):
                            participants.add(decoded(message.get("To")))
                        from_addresses = addresses(message.get("From"))
                        if from_addresses:
                            sender_counts[from_addresses[-1]] = sender_counts.get(from_addresses[-1], 0) + 1
                        for recipient_header in ("To", "Cc", "Bcc"):
                            recipients.update(addresses(message.get(recipient_header)))
                        message_calendar = False
                        for part in message.walk():
                            if is_real_attachment(part):
                                attachment_names.append(decoded(part.get_filename()))
                            if part.get_content_type() == "text/calendar":
                                message_calendar = True
                        calendar_flags.append(message_calendar)

                unique_attachments = list(dict.fromkeys(attachment_names))
                text = "\n\n---\n\n".join(texts)
                (folder / "thread.txt").write_text(text, encoding="utf-8")
                (folder / "snippet.txt").write_text(text[:SNIPPET_BYTES], encoding="utf-8")

                last = headers_list[-1]
                thread_last_date = last_date(thread_records)
                (folder / "meta.json").write_text(json.dumps({
                    "thread_id": thread_id,
                    "message_ids": message_ids,
                    "participants": sorted(participants),
                    "senders": sorted(sender_counts),
                    "sender_counts": sender_counts,
                    "recipients": sorted(recipients),
                    "subject": decoded(last.get("Subject")),
                    "source_at": thread_last_date.isoformat() if thread_last_date != EPOCH else None,
                    "messages": written,
                    "attachments": unique_attachments,
                }, ensure_ascii=False, indent=2), encoding="utf-8")

                auto = auto_verdict(headers_list, calendar_flags, set(sender_counts) | recipients,
                                    screen_text(decoded(last.get("Subject")), bodies))
                if auto:
                    auto_lines.append(f"{thread_id}\tdrop\t\t{auto}")
                    auto_kinds[auto[5:]] += 1

                manifest.write("\t".join([
                    thread_id,
                    thread_last_date.date().isoformat() if thread_last_date != EPOCH else "unknown",
                    decoded(last.get("From"))[:60],
                    decoded(last.get("To"))[:60],
                    decoded(last.get("Subject"))[:120],
                    str(written),
                    str(max(1, size // 1024)),
                    ", ".join(unique_attachments[:3])[:80],
                    auto or "",
                ]) + "\n")
    finally:
        for handle in handles:
            handle.close()

    (workdir / "verdicts.tsv").write_text("\n".join(auto_lines) + ("\n" if auto_lines else ""), encoding="utf-8")
    kinds = ", ".join(f"{kind} {count}" for kind, count in auto_kinds.most_common())
    print(f"messages: {len(records)}; threads: {len(threads)}; set aside unread: {len(auto_lines)}"
          f"{f' ({kinds})' if kinds else ''}; manifest: {workdir / 'manifest.tsv'}")


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


def verdict_notes(workdir):
    """Latest verdict line per thread id, note included (read_verdicts drops notes)."""
    path = Path(workdir) / "verdicts.tsv"
    latest = {}
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            fields = line.split("\t")
            if len(fields) >= 2 and fields[1] in ("in", "drop", "sensitive", "unsure"):
                latest[fields[0]] = (fields[1], fields[3] if len(fields) > 3 else "")
    return latest


def short_hash(text):
    return hashlib.sha1(text.encode("utf-8")).hexdigest()[:12]


def read_owners(workdir):
    path = Path(workdir) / "owners.txt"
    if not path.exists():
        sys.exit("owners.txt not found; run the senders command first")
    return [a for a in path.read_text(encoding="utf-8").split() if a]


def thread_metas(workdir):
    for meta_path in sorted(Path(workdir).glob("threads/*/meta.json")):
        yield json.loads(meta_path.read_text(encoding="utf-8"))


def set_aside(workdir):
    """Thread id -> kind, for every thread the split set aside unread. It stays outside the
    sender choices even when the owner pulls it back in at the review (an owner: line)."""
    path = Path(workdir) / "verdicts.tsv"
    kinds = {}
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            fields = line.split("\t")
            if len(fields) > 3 and fields[3].startswith("auto:"):
                kinds.setdefault(fields[0], fields[3][5:])
    return kinds


def thread_correspondents(meta, owners):
    """The people a thread is with: its non-owner senders; for owner-only threads
    the non-owner recipients; pure self-mail files under (self)."""
    senders = [a for a in meta.get("senders", []) if a not in owners]
    if senders:
        return senders, "sender"
    recipients = [a for a in meta.get("recipients", []) if a not in owners]
    if recipients:
        return recipients, "recipient"
    return ["(self)"], "self"


def sender_kind(address):
    if address == "(self)":
        return "self"
    domain = address.split("@")[-1]
    if domain in INTERNAL_DOMAINS:
        return "colleague"
    if domain in PRIVATE_DOMAINS or domain.split(".")[0] in PRIVATE_PROVIDERS:
        return "private"
    return "company"


def senders_report(workdir, owners):
    """senders.tsv holds facts only (who, how much, which subjects), never a decision, so
    running this again loses nothing: the advice lives in advice.tsv, the owner's
    choices in choices.tsv."""
    workdir = Path(workdir)
    if not owners:
        sys.exit("pass every address the owner sends from: senders <workdir> --owner a@b [--owner c@d]")
    (workdir / "owners.txt").write_text("\n".join(owners) + "\n", encoding="utf-8")
    skipped = set_aside(workdir)
    rows = {}
    names = {}
    for meta in thread_metas(workdir):
        if meta["thread_id"] in skipped:
            continue
        for participant in meta.get("participants", []):
            for name, address in getaddresses([participant]):
                name = name.strip(" \"'")
                if name and "@" not in name:
                    names.setdefault(address.lower(), Counter())[name] += 1
        correspondents, seen_as = thread_correspondents(meta, owners)
        for address in correspondents:
            row = rows.setdefault(address, {"seen_as": seen_as, "threads": 0, "mails": 0, "last": "", "examples": []})
            row["threads"] += 1
            if seen_as == "sender":
                row["mails"] += meta.get("sender_counts", {}).get(address, 0)
            else:
                row["mails"] += meta.get("messages", 0)
            row["last"] = max(row["last"], (meta.get("source_at") or "")[:10])
            subject = (meta.get("subject") or "(no subject)")[:50]
            if subject not in row["examples"]:
                row["examples"].append(subject)
    with open(workdir / "senders.tsv", "w", encoding="utf-8") as out:
        out.write("address\tname\tdomain\tkind\tseen_as\tthreads\tmails\tlast_date\texamples\n")
        for address in sorted(rows, key=lambda a: (-rows[a]["mails"], a)):
            row = rows[address]
            name = names[address].most_common(1)[0][0][:80] if address in names else ""
            domain = address.split("@")[-1] if "@" in address else ""
            out.write("\t".join([address, name, domain, sender_kind(address), row["seen_as"], str(row["threads"]),
                                 str(row["mails"]), row["last"], " || ".join(row["examples"][-2:])]) + "\n")
    domains = len({address.split("@")[-1] for address in rows})
    print(f"senders: {len(rows)} at {domains} domains; set-aside threads left out: {len(skipped)}; "
          f"next: your advice per sender in {workdir / 'advice.tsv'}, then the page command")


def read_senders(workdir):
    path = Path(workdir) / "senders.tsv"
    if not path.exists():
        sys.exit("senders.tsv not found; run the senders command first")
    lines = path.read_text(encoding="utf-8").splitlines()
    header = lines[0].split("\t") if lines else []
    if "kind" not in header:
        sys.exit("senders.tsv comes from an older version of this script; run the senders command again")
    return {fields[0]: dict(zip(header, fields)) for fields in (line.split("\t") for line in lines[1:] if line.strip())}


def merged_advice(workdir, senders):
    """advice.tsv, written by the AI: one line per address or @domain. An address line beats
    a domain line, a later line beats an earlier one of the same kind. Private mail
    services take no domain line: their people are judged one by one. The page is only
    ever built from a list in which every sender has advice."""
    path = Path(workdir) / "advice.tsv"
    if not path.exists():
        sys.exit("advice.tsv not found; write the advice per sender first")
    kinds = {row["domain"]: row["kind"] for row in senders.values() if row["domain"]}
    by_address, by_domain = {}, {}
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip() or line.startswith("#"):
            continue
        fields = line.split("\t")
        key = fields[0].strip().lower()
        verdict = fields[1].strip() if len(fields) > 1 else ""
        reason = re.sub(r"\s+", " ", fields[2]).strip() if len(fields) > 2 else ""
        if verdict not in SENDER_VERDICTS:
            sys.exit(f"advice.tsv line {number}: advice must be include, partial or exclude, got {verdict!r}")
        if key.startswith("@"):
            if key[1:] not in kinds:
                sys.exit(f"advice.tsv line {number}: no sender at {key[1:]}")
            if kinds[key[1:]] == "private":
                sys.exit(f"advice.tsv line {number}: {key[1:]} is a private mail service; advise its addresses one by one")
            by_domain[key[1:]] = (verdict, reason)
        elif key in senders:
            by_address[key] = (verdict, reason)
        else:
            sys.exit(f"advice.tsv line {number}: {key} is not in senders.tsv")
    advice = {}
    for address, row in senders.items():
        found = by_address.get(address) or by_domain.get(row["domain"])
        if found:
            advice[address] = found
    missing = [address for address in senders if address not in advice]
    if missing:
        sys.exit(f"{len(missing)} senders have no advice yet: {', '.join(missing[:8])}{' ...' if len(missing) > 8 else ''}")
    return advice


def sweep_id(workdir, owners):
    return short_hash(str(Path(workdir).resolve()) + "|" + ",".join(sorted(owners)))


def advice_fingerprint(advice):
    return short_hash("\n".join(f"{address}\t{advice[address][0]}" for address in sorted(advice)))


def judged_threads(workdir, owners, senders):
    """Correspondent lists of every thread the owner's sender choices decide."""
    skipped = set_aside(workdir)
    threads = []
    for meta in thread_metas(workdir):
        if meta["thread_id"] in skipped:
            continue
        correspondents, _ = thread_correspondents(meta, owners)
        unknown = [a for a in correspondents if a not in senders]
        if unknown:
            sys.exit(f"senders.tsv is out of date ({unknown[0]} is missing); run the senders command again")
        threads.append((meta, correspondents))
    return threads


def outcome(verdicts):
    """A partial sender anywhere on a thread sends it to the AI. Otherwise include beats
    exclude: nobody writes confidential things with an included contact on the thread.
    Only threads with excluded senders alone stay out."""
    if "partial" in verdicts:
        return "read"
    return "in" if "include" in verdicts else "out"


def page(workdir, open_browser):
    workdir = Path(workdir)
    owners = read_owners(workdir)
    senders = read_senders(workdir)
    threads = judged_threads(workdir, owners, senders)
    advice = merged_advice(workdir, senders)
    if not TEMPLATE.exists():
        sys.exit(f"the page template is missing: {TEMPLATE}")
    index = {address: number for number, address in enumerate(senders)}
    rows = manifest_rows(workdir)
    dates = sorted(fields[1] for fields in rows.values() if fields[1] != "unknown")
    data = {
        "sweep": sweep_id(workdir, owners),
        "advice": advice_fingerprint(advice),
        "owners": owners,
        "period": [dates[0], dates[-1]] if dates else None,
        "conversations": len(rows),
        "setAside": dict(Counter(set_aside(workdir).values())),
        "senders": [{
            "a": address, "n": row["name"], "d": row["domain"], "k": row["kind"],
            "t": int(row["threads"]), "m": int(row["mails"]), "l": row["last_date"],
            "x": [example for example in row["examples"].split(" || ") if example],
            "adv": advice[address][0], "why": advice[address][1],
        } for address, row in senders.items()],
        "threads": [sorted({index[a] for a in correspondents}) for _, correspondents in threads],
    }
    payload = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("<", "\\u003c")
    out = workdir / "sender-choices.html"
    out.write_text(TEMPLATE.read_text(encoding="utf-8").replace("__SWEEP_DATA__", payload), encoding="utf-8")
    advised = Counter(verdict for verdict, _ in advice.values())
    print(f"page for {len(senders)} senders ({advised['include']} include, {advised['partial']} partial, "
          f"{advised['exclude']} exclude advised): {out}")
    if open_browser:
        import webbrowser
        opened = webbrowser.open(out.resolve().as_uri())
        print("opened in the browser" if opened else "no browser could be opened here; give the owner the path")


def record_choices(workdir, handover_path):
    """The owner's hand-over from the page becomes choices.tsv, the record of their
    decision: the advice the page showed, overridden by every choice they made. Nothing
    else writes that file, and apply-senders refuses it once it was edited."""
    workdir = Path(workdir)
    owners = read_owners(workdir)
    senders = read_senders(workdir)
    threads = judged_threads(workdir, owners, senders)
    advice = merged_advice(workdir, senders)
    lines = [line.strip() for line in Path(handover_path).read_text(encoding="utf-8").splitlines() if line.strip()]
    head = next((match for match in map(HANDOVER_HEAD.search, lines) if match), None)
    if not head:
        sys.exit("no 'sweep ... | advice ... | ... senders' line: ask the owner to paste the whole hand-over")
    if head.group(1) != sweep_id(workdir, owners):
        sys.exit("this hand-over belongs to another sweep")
    if head.group(2) != advice_fingerprint(advice) or int(head.group(3)) != len(senders):
        sys.exit("the advice or the sender list changed after the page was built: rebuild the page; the owner's "
                 "choices stay saved in their browser; then ask them to hand over again")
    if "end of choices" not in (line.lower() for line in lines):
        sys.exit("the hand-over is cut off ('end of choices' is missing): ask the owner to paste it again")
    final = {address: advice[address][0] for address in senders}
    for line in lines:
        match = HANDOVER_LINE.match(line)
        if not match:
            continue
        address = match.group(2).lower()
        if address not in senders:
            sys.exit(f"{address} is not in this sweep's sender list")
        final[address] = match.group(1)
    totals = next((match for match in map(HANDOVER_TOTALS.search, lines) if match), None)
    counted = Counter(final.values())
    if not totals or tuple(map(int, totals.groups())) != (counted["include"], counted["partial"], counted["exclude"]):
        sys.exit("the totals line does not match the choices: ask the owner to paste the whole hand-over again")
    body = "address\tverdict\tadvice\tchanged\n" + "".join(
        f"{address}\t{verdict}\t{advice[address][0]}\t{'yes' if verdict != advice[address][0] else ''}\n"
        for address, verdict in final.items())
    recorded = datetime.now(timezone.utc).isoformat(timespec="seconds")
    (workdir / "choices.tsv").write_text(
        f"# the owner's choices, recorded {recorded}; sweep {head.group(1)}; advice {head.group(2)}; rows {short_hash(body)}\n"
        + body, encoding="utf-8")
    changed = [(address, advice[address][0], verdict) for address, verdict in final.items() if verdict != advice[address][0]]
    print(f"recorded the owner's choices for {len(final)} senders in {workdir / 'choices.tsv'}: "
          f"{counted['include']} include, {counted['partial']} partial, {counted['exclude']} exclude; "
          f"{len(changed)} {'differs' if len(changed) == 1 else 'differ'} from the advice")
    for address, before, after in changed:
        print(f"  changed: {address}: {before} -> {after}")
    landing = Counter()
    for _, correspondents in threads:
        verdicts = {final[a] for a in correspondents}
        where = outcome(verdicts)
        landing[where] += 1
        landing["in with exclude"] += where == "in" and "exclude" in verdicts
        landing["read with include"] += where == "read" and "include" in verdicts
    print(f"conversations: {landing['in']} go in unread ({landing['in with exclude']} of those with an excluded sender "
          f"on them too); the AI reads {landing['read']} ({landing['read with include']} of those with an included "
          f"sender on them); {landing['out']} stay out (excluded senders only)")


def read_choices(workdir, senders):
    path = Path(workdir) / "choices.tsv"
    if not path.exists():
        sys.exit("choices.tsv not found: the owner has not handed over their choices; build the page and wait for them")
    lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
    seal = re.search(r"rows (\w+)", lines[0]) if lines else None
    if not seal or seal.group(1) != short_hash("".join(lines[1:])):
        sys.exit("choices.tsv was changed outside record-choices; only a hand-over from the owner can change it")
    choices = {}
    for line in lines[2:]:
        fields = line.rstrip("\n").split("\t")
        choices[fields[0]] = fields[1]
    missing = [address for address in senders if address not in choices]
    if missing:
        sys.exit(f"{len(missing)} senders have no choice from the owner ({', '.join(missing[:5])}); "
                 f"rebuild the page and ask them to hand over again")
    return choices


def apply_senders(workdir):
    """The owner's choices decide every thread (see outcome()): a partial sender anywhere
    sends it to the AI, and it waits as unsure until read; otherwise an included sender
    takes it in, unread, whoever else is on it; excluded senders alone keep it out. A
    thread the owner decided by hand keeps that decision; an AI triage line holds while a
    partial sender is on the thread."""
    workdir = Path(workdir)
    owners = read_owners(workdir)
    senders = read_senders(workdir)
    choices = read_choices(workdir, senders)
    existing = verdict_notes(workdir)
    rows = manifest_rows(workdir)
    new_lines = []
    counts = Counter()
    triage = []
    for meta, correspondents in judged_threads(workdir, owners, senders):
        thread_id = meta["thread_id"]
        latest = existing.get(thread_id, (None, ""))
        if latest[1].startswith("owner:"):
            counts["owner"] += 1
            continue
        verdicts = [choices[a] for a in correspondents]
        if "partial" in verdicts:
            if latest[1].startswith("triage:"):
                counts["triaged"] += 1
                continue
            line = ("unsure", "triage-pending")
            triage.append((thread_id, correspondents))
        elif "include" in verdicts:
            line = ("in", f"sender:{correspondents[verdicts.index('include')]}")
            counts["in"] += 1
            counts["in with exclude"] += "exclude" in verdicts
        else:
            line = ("drop", f"sender-excluded:{correspondents[0]}")
            counts["drop"] += 1
        if latest != line:
            new_lines.append(f"{thread_id}\t{line[0]}\t\t{line[1]}")
    verdict_path = workdir / "verdicts.tsv"
    text = verdict_path.read_text(encoding="utf-8") if verdict_path.exists() else ""
    if text and not text.endswith("\n"):
        text += "\n"
    verdict_path.write_text(text + "".join(line + "\n" for line in new_lines), encoding="utf-8")
    print(f"in, unread: {counts['in']} ({counts['in with exclude']} of those with an excluded sender on them too); "
          f"out: {counts['drop']} (excluded senders only); read by the AI already: {counts['triaged']}; "
          f"the owner's own calls kept: {counts['owner']}")
    if triage:
        print(f"the AI reads {len(triage)} conversations (a partial sender is on each), marked unsure until decided:")
        for thread_id, correspondents in triage:
            fields = rows.get(thread_id, [])
            print(f"  {thread_id}  {fields[1] if len(fields) > 1 else ''}  {fields[4] if len(fields) > 4 else ''}"
                  f"  [{', '.join(f'{a} {choices[a]}' for a in correspondents)}]")


REVIEW_BUCKETS = (
    # (verdict, note prefix, label, listed in full without --all)
    ("in", "sender:", "in, unread: an included sender", False),
    ("in", "triage:", "in, after the AI read it", True),
    ("in", "owner:", "in: the owner's call at this check", True),
    ("sensitive", "", "in, founders only (sensitive)", True),
    ("drop", "sender-excluded:", "out: excluded senders only", False),
    ("drop", "triage:", "out: the AI read it and it does not belong", True),
    ("drop", "owner:", "out: the owner's call at this check", True),
    ("drop", "auto:holding-financial", "out: holding paperwork (Software for Good, SFG, KMPI, RDPI, KIWI, shares, loans)", True),
    ("drop", "auto:newsletter-or-list", "out: newsletters and mailing lists", False),
    ("drop", "auto:calendar-invite", "out: calendar invites", False),
    ("drop", "auto:notification-sender", "out: automated mail", False),
    ("drop", "auto:fiu-internal-only", "out: only FIU colleagues on it", False),
    ("unsure", "", "unsure: to settle with the owner", True),
)


def review(workdir, show_all):
    """Counts for everything; in full only what no person decided on the page (what the AI
    read, what the holding screen set aside) plus sensitive, unsure and the owner's own
    calls. --all lists every conversation."""
    notes = verdict_notes(workdir)
    rows = manifest_rows(workdir)
    buckets = {label: [] for _, _, label, _ in REVIEW_BUCKETS}
    other = []
    for thread_id, (verdict, note) in notes.items():
        label = next((label for v, prefix, label, _ in REVIEW_BUCKETS if v == verdict and note.startswith(prefix)), None)
        (buckets[label] if label else other).append((thread_id, note))
    print(f"{len(rows)} conversations")
    for _, _, label, _ in REVIEW_BUCKETS:
        if buckets[label]:
            print(f"  {len(buckets[label]):6d}  {label}")
    if other:
        print(f"  {len(other):6d}  other")
    for _, _, label, listed in REVIEW_BUCKETS + (("", "", "other", True),):
        entries = other if label == "other" else buckets[label]
        if not entries or not (listed or show_all):
            continue
        print(f"\n== {label} ({len(entries)})")
        for thread_id, note in sorted(entries):
            fields = rows.get(thread_id, [])
            reason = note.split(":", 1)[1].strip() if note.startswith(("triage:", "owner:")) else ""
            print(f"  {thread_id}  {fields[1] if len(fields) > 1 else ''}  {fields[4] if len(fields) > 4 else ''}"
                  f"{f'  [{reason}]' if reason else ''}")
    missing = coverage_check(workdir, notes)
    if missing:
        print(f"\n!! {len(missing)} threads have no verdict yet: {', '.join(missing[:10])}{' ...' if len(missing) > 10 else ''}")


def package(workdir, out_zip):
    read_choices(workdir, read_senders(workdir))
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
        sys.exit(__doc__.split("Usage:")[1].split("\n\n")[0].strip())
    command = arguments[0]
    if command == "split":
        limit = 0
        if "--limit" in arguments:
            flag_index = arguments.index("--limit")
            limit = int(arguments[flag_index + 1])
            del arguments[flag_index:flag_index + 2]
        split(arguments[1], arguments[2:], limit)
    elif command == "senders":
        owners = []
        while "--owner" in arguments:
            flag_index = arguments.index("--owner")
            owners.append(arguments[flag_index + 1].lower())
            del arguments[flag_index:flag_index + 2]
        senders_report(arguments[1], owners)
    elif command == "page":
        page(arguments[1], "--open" in arguments)
    elif command == "record-choices":
        record_choices(arguments[1], arguments[2])
    elif command == "apply-senders":
        apply_senders(arguments[1])
    elif command == "review":
        review(arguments[1], "--all" in arguments)
    elif command == "package":
        package(arguments[1], arguments[2])
    else:
        sys.exit(f"unknown command {command}")
