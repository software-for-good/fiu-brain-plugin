#!/usr/bin/env python3
"""FIU Brain transcript sweep: manifest a folder of meeting exports, pre-verdict mechanically
detectable drops, bucket meetings by counterpart, print the review lists, package the approved
files. Stdlib only; the AI reads the participants table and snippets and writes verdict lines.

Usage:
  transcript_sweep.py manifest <folder> <workdir>
  transcript_sweep.py participants <workdir> --owner <address> [--owner <address> ...]
  transcript_sweep.py apply-participants <workdir>
  transcript_sweep.py review <workdir>
  transcript_sweep.py package <workdir> <out.zip>

Export layout (one Granola export as seen on 2026-09-04): a title heading, then the lines
"Datum:", "Granola label:", "Voorstel labels:", "Deelnemers:" and "Granola ID:", then a
"Samenvatting" block and the "Transcript". Missing fields stay empty; nothing depends on all
of them being present. The meeting date comes from the filename (YYYYMMDD, the team's naming
convention) first, then from the Datum line, and only then from the file's modification time.

verdicts.tsv columns: file_id<TAB>verdict<TAB>clearance<TAB>note
verdicts: in | drop | sensitive | unsure. Later lines for the same id win.
The verdict-parsing helpers and the holding-financial screen are kept in sync with mail_sweep.py.
"""
import json
import re
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path

try:
    from zoneinfo import ZoneInfo
    LOCAL_TZ = ZoneInfo("Europe/Amsterdam")
except Exception:  # no tz database on this machine; UTC is the honest fallback
    LOCAL_TZ = timezone.utc

SNIPPET_BYTES = 2000
CLEARANCES = ("public", "team", "founders")
EXPORT_SUFFIXES = (".md", ".markdown", ".txt")
FILENAME_DATE = re.compile(r"(20\d{2})[-_]?(\d{2})[-_]?(\d{2})")
DATUM_VALUE = re.compile(r"(20\d{2})-(\d{2})-(\d{2})(?:[ T](\d{1,2}):(\d{2}))?")
HEADER_FIELDS = {
    "datum": re.compile(r"^[\s*_]*datum[\s*_]*:[\s*_]*(.+?)[\s*_]*$", re.I),
    "granola_label": re.compile(r"^[\s*_]*granola label[\s*_]*:[\s*_]*(.+?)[\s*_]*$", re.I),
    "proposed_labels": re.compile(r"^[\s*_]*voorstel labels[\s*_]*:[\s*_]*(.+?)[\s*_]*$", re.I),
    "participants": re.compile(r"^[\s*_]*deelnemers[\s*_]*:[\s*_]*(.+?)[\s*_]*$", re.I),
    "granola_id": re.compile(r"^[\s*_]*granola id[\s*_]*:[\s*_]*`?([^`\s]+)`?[\s*_]*$", re.I),
}
DERIVED_HEADING = re.compile(r"^#*\s*(summary|samenvatting|transcript|notes)\s*$", re.I)
SUMMARY_HEADING = re.compile(r"^#*\s*(summary|samenvatting)\b", re.I | re.M)
ADDRESS = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
# Financial/legal matters around the holding companies (SFG and KMPI/RDPI/KIWI): loans,
# shareholder documents, registry paperwork. Same screen as mail_sweep.py; keep them identical.
HOLDING_FINANCIAL = re.compile(
    r"(?i:\b(?:kmpi|rdpi)\b)"
    r"|\bKIWI\b"
    r"|(?i:\bkiwi\s*(?:b\.?\s?v\.?\b|holding|beheer))"
    r"|(?i:aandeelhoud|leningsovereenkomst|geldlening)"
    r"|(?i:software ?for ?good|\bkvk\b)"
)


def parse_header(text):
    """The header block sits in the first lines of the export; read until the first section
    heading after the fields, never further. Returns raw field values, empty when absent."""
    fields = {key: "" for key in HEADER_FIELDS}
    for line in text.splitlines()[:40]:
        stripped = line.strip()
        if not stripped:
            continue
        for key, pattern in HEADER_FIELDS.items():
            match = pattern.match(stripped)
            if match and not fields[key]:
                fields[key] = match.group(1).strip()
                break
        else:
            if DERIVED_HEADING.match(stripped) and any(fields.values()):
                break
    return fields


def title_of(path, text):
    for line in text.splitlines()[:10]:
        stripped = line.strip()
        if not stripped or DERIVED_HEADING.match(stripped):
            continue
        if any(pattern.match(stripped) for pattern in HEADER_FIELDS.values()):
            continue
        return stripped.lstrip("# ").strip()[:120]
    return path.stem[:120]


def split_list(value):
    return [item.strip().strip("[]") for item in value.split(",") if item.strip().strip("[]")]


def meeting_date(path, datum_value):
    """Filename first (YYYYMMDD), then the Datum line, then mtime. When filename and Datum name
    the same day, the Datum time is kept; a disagreeing Datum loses to the filename."""
    datum = None
    match = DATUM_VALUE.search(datum_value or "")
    if match:
        try:
            datum = datetime(int(match.group(1)), int(match.group(2)), int(match.group(3)),
                             int(match.group(4) or 0), int(match.group(5) or 0), tzinfo=LOCAL_TZ)
        except ValueError:
            datum = None
    match = FILENAME_DATE.search(path.name)
    if match:
        try:
            from_name = datetime(int(match.group(1)), int(match.group(2)), int(match.group(3)), tzinfo=LOCAL_TZ)
            if datum and datum.date() == from_name.date():
                return datum, "filename"
            return from_name, "filename"
        except ValueError:
            pass
    if datum:
        return datum, "datum"
    return datetime.fromtimestamp(path.stat().st_mtime, tz=LOCAL_TZ), "mtime"


def manifest(folder, workdir):
    folder, workdir = Path(folder), Path(workdir)
    snippets, metas = workdir / "snippets", workdir / "meta"
    snippets.mkdir(parents=True, exist_ok=True)
    metas.mkdir(parents=True, exist_ok=True)
    files = sorted(p for p in folder.iterdir() if p.is_file() and p.suffix.lower() in EXPORT_SUFFIXES)
    auto_lines = []
    with open(workdir / "manifest.tsv", "w", encoding="utf-8") as out:
        out.write("file_id\tdate\tdate_source\tsize_kb\thas_summary\tgranola_label\tparticipants\ttitle\tauto\n")
        for index, path in enumerate(files, start=1):
            text = path.read_text(encoding="utf-8", errors="replace")
            file_id = f"{index:04d}-{re.sub(r'[^a-zA-Z0-9-]', '', path.stem)[:40]}"
            (snippets / f"{file_id}.txt").write_text(text[:SNIPPET_BYTES], encoding="utf-8")
            header = parse_header(text)
            date, date_source = meeting_date(path, header["datum"])
            title = title_of(path, text)
            addresses = [a.lower() for a in ADDRESS.findall(header["participants"])]
            names = [p for p in split_list(header["participants"]) if not ADDRESS.search(p)]
            auto = "auto:holding-financial" if HOLDING_FINANCIAL.search(title + "\n" + text) else ""
            (metas / f"{file_id}.json").write_text(json.dumps({
                "file_id": file_id,
                "path": str(path),
                "type": "meeting_transcript",
                "source_at": date.isoformat(),
                "date_source": date_source,
                "title": title,
                "granola_id": header["granola_id"],
                "granola_label": ", ".join(split_list(header["granola_label"])),
                "proposed_labels": split_list(header["proposed_labels"]),
                "participants": sorted(set(addresses)),
                "participant_names": names,
                "has_summary": bool(SUMMARY_HEADING.search(text[:4000])),
                "size_bytes": path.stat().st_size,
            }, ensure_ascii=False, indent=2), encoding="utf-8")
            if auto:
                auto_lines.append(f"{file_id}\tdrop\t\t{auto}")
            out.write("\t".join([
                file_id,
                date.date().isoformat(),
                date_source,
                str(max(1, path.stat().st_size // 1024)),
                "yes" if SUMMARY_HEADING.search(text[:4000]) else "no",
                ", ".join(split_list(header["granola_label"]))[:40],
                ", ".join(sorted(set(addresses)))[:80],
                title,
                auto,
            ]) + "\n")
    (workdir / "verdicts.tsv").write_text("\n".join(auto_lines) + ("\n" if auto_lines else ""), encoding="utf-8")
    by_source = {}
    for meta_path in metas.glob("*.json"):
        source = json.loads(meta_path.read_text(encoding="utf-8"))["date_source"]
        by_source[source] = by_source.get(source, 0) + 1
    print(f"files: {len(files)}; auto-dropped: {len(auto_lines)}; dates from {by_source}; manifest: {workdir / 'manifest.tsv'}")


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
    """Latest verdict line per file id, note included (read_verdicts drops notes)."""
    path = Path(workdir) / "verdicts.tsv"
    latest = {}
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            fields = line.split("\t")
            if len(fields) >= 2 and fields[1] in ("in", "drop", "sensitive", "unsure"):
                latest[fields[0]] = (fields[1], fields[3] if len(fields) > 3 else "")
    return latest


def metas(workdir):
    for meta_path in sorted(Path(workdir).glob("meta/*.json")):
        yield json.loads(meta_path.read_text(encoding="utf-8"))


def meeting_counterparts(meta, owners):
    """The people a meeting is with: every participant address that is not the owner. A meeting
    without one (no addresses recorded, or the owner alone) files under (unlisted)."""
    counterparts = [a for a in meta.get("participants", []) if a not in owners]
    return counterparts if counterparts else ["(unlisted)"]


def participants_report(workdir, owners):
    workdir = Path(workdir)
    if not owners:
        sys.exit("pass every address the owner appears under: participants <workdir> --owner a@b [--owner c@d]")
    (workdir / "owners.txt").write_text("\n".join(owners) + "\n", encoding="utf-8")
    autos = {f for f, (_, note) in verdict_notes(workdir).items() if note.startswith("auto:")}
    rows = {}
    skipped = 0
    for meta in metas(workdir):
        if meta["file_id"] in autos:
            skipped += 1
            continue
        for address in meeting_counterparts(meta, owners):
            row = rows.setdefault(address, {"meetings": 0, "last": "", "labels": [], "examples": []})
            row["meetings"] += 1
            row["last"] = max(row["last"], (meta.get("source_at") or "")[:10])
            label = meta.get("granola_label") or ""
            if label and label not in row["labels"]:
                row["labels"].append(label)
            title = (meta.get("title") or "(no title)")[:50]
            if title not in row["examples"]:
                row["examples"].append(title)
    with open(workdir / "participants.tsv", "w", encoding="utf-8") as out:
        out.write("address\tmeetings\tlast_date\tgranola_labels\texamples\tverdict\tnote\n")
        for address in sorted(rows, key=lambda a: (-rows[a]["meetings"], a)):
            row = rows[address]
            out.write("\t".join([address, str(row["meetings"]), row["last"], " | ".join(row["labels"][:4]),
                                 " || ".join(row["examples"][-2:]), "", ""]) + "\n")
    print(f"counterparts: {len(rows)}; auto-dropped meetings left out of the table: {skipped}; "
          f"fill the verdict column (include/exclude/partial) in {workdir / 'participants.tsv'}")


def apply_participants(workdir):
    workdir = Path(workdir)
    owners = workdir / "owners.txt"
    if not owners.exists():
        sys.exit("owners.txt not found; run the participants command first")
    owners = [a for a in owners.read_text(encoding="utf-8").split() if a]
    counterpart_verdicts = {}
    unfilled = []
    for line in (workdir / "participants.tsv").read_text(encoding="utf-8").splitlines()[1:]:
        if not line.strip():
            continue
        fields = line.split("\t")
        verdict = fields[5].strip() if len(fields) > 5 else ""
        if verdict not in ("include", "exclude", "partial"):
            unfilled.append(fields[0])
        counterpart_verdicts[fields[0]] = verdict
    if unfilled:
        sys.exit(f"{len(unfilled)} counterparts still lack include/exclude/partial: "
                 f"{', '.join(unfilled[:8])}{' ...' if len(unfilled) > 8 else ''}")
    existing = verdict_notes(workdir)
    new_lines = []
    added_in = added_drop = kept_manual = 0
    partial_meetings = []
    for meta in metas(workdir):
        file_id = meta["file_id"]
        previous_note = existing.get(file_id, (None, ""))[1]
        if previous_note.startswith("auto:"):
            continue
        if file_id in existing and not previous_note.startswith("participant"):
            kept_manual += 1
            continue
        counterparts = meeting_counterparts(meta, owners)
        verdicts = [counterpart_verdicts.get(address) for address in counterparts]
        if None in verdicts:
            sys.exit(f"{file_id} has counterpart {counterparts[verdicts.index(None)]} "
                     f"that participants.tsv does not know; re-run participants")
        if "include" in verdicts:
            new_lines.append(f"{file_id}\tin\t\tparticipant:{counterparts[verdicts.index('include')]}")
            added_in += 1
        elif "partial" in verdicts:
            partial_meetings.append((file_id, meta.get("title", "")))
        else:
            new_lines.append(f"{file_id}\tdrop\t\tparticipant-excluded")
            added_drop += 1
    verdict_path = workdir / "verdicts.tsv"
    text = verdict_path.read_text(encoding="utf-8") if verdict_path.exists() else ""
    if text and not text.endswith("\n"):
        text += "\n"
    verdict_path.write_text(text + "".join(line + "\n" for line in new_lines), encoding="utf-8")
    print(f"in: {added_in}; drop: {added_drop}; per-meeting verdicts kept: {kept_manual}")
    if partial_meetings:
        print(f"partial counterparts leave {len(partial_meetings)} meetings for manual triage:")
        for file_id, title in partial_meetings:
            print(f"  {file_id}  {title[:70]}")


def review(workdir):
    verdicts = read_verdicts(workdir)
    rows = manifest_rows(workdir)
    for bucket in ("in", "sensitive", "drop", "unsure"):
        ids = [f for f, (v, _) in verdicts.items() if v == bucket]
        print(f"\n== {bucket} ({len(ids)})")
        for file_id in sorted(ids):
            fields = rows.get(file_id, [])
            print(f"  {file_id}  {fields[7] if len(fields) > 7 else ''}")
    mtime_rows = [f for f, fields in rows.items() if len(fields) > 2 and fields[2] == "mtime"]
    if mtime_rows:
        print(f"\n!! {len(mtime_rows)} files carry the export day as their date (no date in filename or Datum line): "
              f"{', '.join(mtime_rows[:10])}{' ...' if len(mtime_rows) > 10 else ''}")
    missing = coverage_check(workdir, verdicts)
    if missing:
        print(f"\n!! {len(missing)} files have no verdict yet: {', '.join(missing[:10])}{' ...' if len(missing) > 10 else ''}")


def package(workdir, out_zip):
    verdicts = read_verdicts(workdir)
    missing = coverage_check(workdir, verdicts)
    if missing:
        sys.exit(f"{len(missing)} files have no verdict; the owner's approval must cover everything. Missing: {', '.join(missing[:10])}")
    unsure = [f for f, (v, _) in verdicts.items() if v == "unsure"]
    if unsure:
        sys.exit(f"{len(unsure)} files still unsure; settle them before packaging")
    count = 0
    with zipfile.ZipFile(out_zip, "w", zipfile.ZIP_DEFLATED) as bundle:
        for file_id, (verdict, clearance) in sorted(verdicts.items()):
            if verdict not in ("in", "sensitive"):
                continue
            meta_path = Path(workdir) / "meta" / f"{file_id}.json"
            if not meta_path.exists():
                sys.exit(f"verdict names unknown file {file_id}; re-run manifest or fix verdicts.tsv")
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
            source = Path(meta.pop("path"))
            meta["clearance"] = "founders" if verdict == "sensitive" else clearance
            bundle.write(source, f"{file_id}/{source.name}")
            bundle.writestr(f"{file_id}/meta.json", json.dumps(meta, ensure_ascii=False, indent=2))
            count += 1
    print(f"packaged {count} transcripts into {out_zip}; dropped files stayed local")


if __name__ == "__main__":
    arguments = sys.argv[1:]
    if len(arguments) < 2:
        sys.exit(__doc__.strip().split("Usage:")[1].split("Export layout")[0].strip())
    command = arguments[0]
    if command == "manifest":
        manifest(arguments[1], arguments[2])
    elif command == "participants":
        owners = []
        while "--owner" in arguments:
            flag_index = arguments.index("--owner")
            owners.append(arguments[flag_index + 1].lower())
            del arguments[flag_index:flag_index + 2]
        participants_report(arguments[1], owners)
    elif command == "apply-participants":
        apply_participants(arguments[1])
    elif command == "review":
        review(arguments[1])
    elif command == "package":
        package(arguments[1], arguments[2])
    else:
        sys.exit(f"unknown command {command}")
