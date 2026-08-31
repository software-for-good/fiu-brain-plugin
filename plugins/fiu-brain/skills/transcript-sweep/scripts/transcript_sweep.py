#!/usr/bin/env python3
"""FIU Brain transcript sweep: manifest a folder of transcript exports, print
the review lists, package the approved files. Stdlib only; the AI reads
manifest and snippets and appends to verdicts.tsv.

verdicts.tsv columns: file_id<TAB>verdict<TAB>clearance<TAB>note
verdicts: in | drop | sensitive | unsure. Later lines for the same id win.
The verdict-parsing helpers are kept in sync with mail_sweep.py.
"""
import json
import re
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path

SNIPPET_BYTES = 2000
CLEARANCES = ("public", "team", "founders")
DATE_PATTERN = re.compile(r"(20\d{2})[-_]?(\d{2})[-_]?(\d{2})")
DERIVED_HEADING = re.compile(r"^#*\s*(summary|samenvatting|transcript|notes)\s*$", re.I)


def file_date(path):
    match = DATE_PATTERN.search(path.name)
    if match:
        try:
            return datetime(int(match.group(1)), int(match.group(2)), int(match.group(3)), tzinfo=timezone.utc), "filename"
        except ValueError:
            pass
    return datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc), "mtime"


def title_of(path, text):
    for line in text.splitlines()[:10]:
        stripped = line.strip()
        if stripped and not DERIVED_HEADING.match(stripped):
            return stripped.lstrip("# ").strip()[:120]
    return path.stem[:120]


def manifest(folder, workdir):
    folder, workdir = Path(folder), Path(workdir)
    snippets = workdir / "snippets"
    snippets.mkdir(parents=True, exist_ok=True)
    files = sorted(p for p in folder.iterdir() if p.is_file() and p.suffix.lower() in (".md", ".txt"))
    path_lines = []
    with open(workdir / "manifest.tsv", "w", encoding="utf-8") as out:
        out.write("file_id\tdate\tdate_source\tsize_kb\thas_summary\ttitle\n")
        for index, path in enumerate(files, start=1):
            text = path.read_text(encoding="utf-8", errors="replace")
            file_id = f"{index:04d}-{re.sub(r'[^a-zA-Z0-9-]', '', path.stem)[:40]}"
            (snippets / f"{file_id}.txt").write_text(text[:SNIPPET_BYTES], encoding="utf-8")
            date, date_source = file_date(path)
            out.write("\t".join([
                file_id,
                date.date().isoformat(),
                date_source,
                str(max(1, path.stat().st_size // 1024)),
                "yes" if re.search(r"^#*\s*(summary|samenvatting)", text[:2000], re.I | re.M) else "no",
                title_of(path, text),
            ]) + "\n")
            path_lines.append(f"{file_id}\t{path}\t{date.isoformat()}")
    (workdir / "paths.tsv").write_text("\n".join(path_lines) + ("\n" if path_lines else ""), encoding="utf-8")
    if not (workdir / "verdicts.tsv").exists():
        (workdir / "verdicts.tsv").write_text("", encoding="utf-8")
    print(f"files: {len(files)}; manifest: {workdir / 'manifest.tsv'}")


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
        ids = [f for f, (v, _) in verdicts.items() if v == bucket]
        print(f"\n== {bucket} ({len(ids)})")
        for file_id in sorted(ids):
            fields = rows.get(file_id, [])
            print(f"  {file_id}  {fields[5] if len(fields) > 5 else ''}")
    missing = coverage_check(workdir, verdicts)
    if missing:
        print(f"\n!! {len(missing)} files have no verdict yet: {', '.join(missing[:10])}{' ...' if len(missing) > 10 else ''}")


def package(workdir, out_zip):
    verdicts = read_verdicts(workdir)
    missing = coverage_check(workdir, verdicts)
    if missing:
        sys.exit(f"{len(missing)} files have no verdict; the owner's approval must cover everything. Missing: {', '.join(missing[:10])}")
    if any(v == "unsure" for v, _ in verdicts.values()):
        sys.exit("unsure files remain; settle them before packaging")
    paths = {}
    for line in (Path(workdir) / "paths.tsv").read_text(encoding="utf-8").splitlines():
        if line.strip():
            file_id, path, iso = line.split("\t")
            paths[file_id] = (path, iso)
    rows = manifest_rows(workdir)
    count = 0
    with zipfile.ZipFile(out_zip, "w", zipfile.ZIP_DEFLATED) as bundle:
        for file_id, (verdict, clearance) in sorted(verdicts.items()):
            if verdict not in ("in", "sensitive"):
                continue
            if file_id not in paths:
                sys.exit(f"verdict names unknown file {file_id}; re-run manifest or fix verdicts.tsv")
            source_path, iso = paths[file_id]
            source = Path(source_path)
            fields = rows.get(file_id, [])
            bundle.write(source, f"{file_id}/{source.name}")
            bundle.writestr(f"{file_id}/meta.json", json.dumps({
                "file_id": file_id,
                "type": "meeting_transcript",
                "source_at": iso,
                "date_source": fields[2] if len(fields) > 2 else "unknown",
                "title": fields[5] if len(fields) > 5 else source.stem,
                "clearance": "founders" if verdict == "sensitive" else clearance,
            }, ensure_ascii=False, indent=2))
            count += 1
    print(f"packaged {count} transcripts into {out_zip}; dropped files stayed local")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        sys.exit("usage: transcript_sweep.py manifest <folder> <workdir> | review <workdir> | package <workdir> <out.zip>")
    command = sys.argv[1]
    if command == "manifest":
        manifest(sys.argv[2], sys.argv[3])
    elif command == "review":
        review(sys.argv[2])
    elif command == "package":
        package(sys.argv[2], sys.argv[3])
    else:
        sys.exit(f"unknown command {command}")
