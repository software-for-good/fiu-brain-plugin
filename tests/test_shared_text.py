"""Every copy of a shared text matches its source (README, "Shared text").

The Claude app's chat and Cowork do not run the shell lines Claude Code expands inside a skill, so a
text that several skills need is copied into each of them. This test fails, with a diff, until every
copy matches its source again. Run it before every commit: python3 -m unittest discover -s tests
"""

import difflib
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS = ROOT / "plugins" / "fiu-brain" / "skills"

# source file -> the skills whose SKILL.md carries its text word for word
COPIES = {
    SKILLS / "guardrails" / "SKILL.md": ["start"],
    ROOT / "shared" / "identity.md": ["start", "stop", "optimise", "work", "meeting", "process", "process-proposals"],
    ROOT / "shared" / "reading-the-brain.md": ["process", "stop"],
}


def body(path: Path) -> str:
    """The text of a file without its frontmatter, trimmed."""
    text = path.read_text(encoding="utf-8")
    if text.startswith("---\n"):
        text = text.split("\n---\n", 1)[1]
    return text.strip()


def mismatch(source: Path, target: Path, expected: str, text: str) -> str:
    """Point at where the copy drifted: a diff against the closest lines of the target."""
    want = expected.splitlines()
    have = text.splitlines()
    closest = difflib.get_close_matches(want[0], have, n=1, cutoff=0.5)
    header = f"{target.relative_to(ROOT)} does not carry the text of {source.relative_to(ROOT)} word for word. Edit the source, then copy it over."
    if not closest:
        return header + "\nNo line of the copy resembles the first line of the source:\n" + want[0]
    start = have.index(closest[0])
    diff = difflib.unified_diff(
        want,
        have[start:start + len(want)],
        str(source.relative_to(ROOT)),
        str(target.relative_to(ROOT)),
        lineterm="",
    )
    return header + "\n" + "\n".join(diff)


class SharedTextTest(unittest.TestCase):
    def test_every_copy_matches_its_source(self) -> None:
        for source, skills in COPIES.items():
            expected = body(source)
            for skill in skills:
                target = SKILLS / skill / "SKILL.md"
                with self.subTest(source=str(source.relative_to(ROOT)), copy=skill):
                    text = target.read_text(encoding="utf-8")
                    if expected not in text:
                        self.fail(mismatch(source, target, expected, text))


if __name__ == "__main__":
    unittest.main()
