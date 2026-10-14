#!/usr/bin/env python3
"""Insert or refresh a GitHub-compatible table of contents in markdown docs.

Idempotent: rewrites whatever sits between the TOC markers, so re-running after
editing headings just updates it.

    python scripts/add_doc_toc.py docs/investigations/foo.md
    python scripts/add_doc_toc.py --depth 3 --min-headings 8 agents-*.md
    python scripts/add_doc_toc.py --check agents-*.md      # CI / audit mode
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

BEGIN = "<!-- toc -->"
END = "<!-- /toc -->"
FENCE = re.compile(r"^\s*(```|~~~)")
ATX = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")
EXPLICIT_ANCHOR = re.compile(r"""<a\s+(?:name|id)\s*=\s*["']([^"']+)["']""", re.I)


UNDERSCORE_EMPHASIS = re.compile(r"(?<![A-Za-z0-9_])__?(?=\S)(.+?)(?<=\S)__?(?![A-Za-z0-9_])")


def strip_underscore_emphasis(text: str) -> str:
    """Unwrap _emphasis_ without touching an underscore inside an identifier.

    CommonMark only opens underscore emphasis at a non-alphanumeric boundary, so
    `6IrCt_IVk` and `notification_event_stream_processor` keep their underscores
    while `_italic_` and `__bold__` lose their delimiters -- which is what GitHub
    anchors from.
    """
    return UNDERSCORE_EMPHASIS.sub(r"\1", text)


def slugify(text: str) -> str:
    """Reproduce GitHub's heading-anchor algorithm.

    Order matters. Inline markdown is unwrapped to its visible text, HTML is
    dropped, then every character outside [a-z0-9 _-] is deleted and spaces
    become hyphens. Underscores survive unless they were emphasis delimiters.
    Hyphens are NOT collapsed -- that is why "Reproduction / verification
    queries" anchors as "reproduction--verification-queries".
    """
    s = re.sub(r"<[^>]+>", "", text)                     # html tags
    s = re.sub(r"!\[([^\]]*)\]\([^)]*\)", r"\1", s)      # images -> alt
    s = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", s)       # links -> text
    s = s.replace("`", "")                                # inline code
    s = re.sub(r"(\*\*|\*|~~)", "", s)                    # emphasis
    s = strip_underscore_emphasis(s)                      # keeps snake_case intact
    s = s.lower()
    s = re.sub(r"[^\w _\-]", "", s)                       # drop punctuation, §, —, …; keeps accented letters, as GitHub does
    return s.replace(" ", "-")


def visible(text: str) -> str:
    """Heading text as it should read inside the TOC link."""
    s = re.sub(r"<[^>]+>", "", text)
    s = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", s)
    s = re.sub(r"(\*\*|~~)", "", s)
    s = strip_underscore_emphasis(s)
    return s.strip()


def headings(md: str, depth: int) -> list[tuple[int, str, str]]:
    """(level, visible_text, anchor) for headings outside fenced code blocks."""
    out: list[tuple[int, str, str]] = []
    seen: dict[str, int] = {}
    in_fence = False
    fence_marker = ""
    for line in md.splitlines():
        f = FENCE.match(line)
        if f:
            marker = f.group(1)
            if not in_fence:
                in_fence, fence_marker = True, marker
            elif marker == fence_marker:
                in_fence = False
            continue
        if in_fence:
            continue
        m = ATX.match(line)
        if not m:
            continue
        level = len(m.group(1))
        raw = m.group(2)
        if level == 1 or level > depth:
            continue
        explicit = EXPLICIT_ANCHOR.search(raw)
        anchor = explicit.group(1) if explicit else slugify(raw)
        if not explicit:                                  # GitHub dedupes generated slugs
            n = seen.get(anchor, 0)
            seen[anchor] = n + 1
            if n:
                anchor = f"{anchor}-{n}"
        text = visible(raw)
        if text:
            out.append((level, text, anchor))
    return out


def render(items: list[tuple[int, str, str]]) -> str:
    base = min(lvl for lvl, _, _ in items)
    lines = [BEGIN, "## Contents", ""]
    for lvl, text, anchor in items:
        lines.append(f"{'  ' * (lvl - base)}- [{text}](#{anchor})")
    lines += ["", END]
    return "\n".join(lines)


def insertion_point(lines: list[str]) -> int:
    """Before the first real section heading, after any H1 + intro block."""
    in_fence = False
    fence_marker = ""
    for i, line in enumerate(lines):
        f = FENCE.match(line)
        if f:
            marker = f.group(1)
            if not in_fence:
                in_fence, fence_marker = True, marker
            elif marker == fence_marker:
                in_fence = False
            continue
        if in_fence:
            continue
        if re.match(r"^#{2,6}\s+", line):
            j = i
            while j > 0 and lines[j - 1].strip() in ("", "---", "***", "___"):
                j -= 1
            return j
    return len(lines)


def strip_toc(md: str) -> str:
    """Remove an existing TOC block so its own heading is never scanned."""
    return re.sub(re.escape(BEGIN) + r".*?" + re.escape(END), "", md, count=1, flags=re.S)


def apply(path: Path, depth: int, min_headings: int, check: bool) -> str:
    md = path.read_text(encoding="utf-8")
    items = headings(strip_toc(md), depth)
    if len(items) < min_headings:
        return "skip"

    toc = render(items)
    if BEGIN in md and END in md:
        new = re.sub(
            re.escape(BEGIN) + r".*?" + re.escape(END), lambda _: toc, md, count=1, flags=re.S
        )
        verb = "unchanged" if new == md else "refreshed"
    else:
        lines = md.splitlines()
        at = insertion_point(lines)
        block = [toc, ""]
        if at > 0 and lines[at - 1].strip():      # keep a blank line above the marker
            block.insert(0, "")
        lines[at:at] = block
        new = "\n".join(lines) + ("\n" if md.endswith("\n") else "")
        verb = "added"

    if check:
        return "ok" if verb == "unchanged" else f"NEEDS-TOC ({verb})"
    if verb != "unchanged":
        path.write_text(new, encoding="utf-8")
    return verb


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("paths", nargs="+", type=Path)
    ap.add_argument("--depth", type=int, default=2, help="deepest heading level to include (default 2)")
    ap.add_argument("--min-headings", type=int, default=6, help="skip docs with fewer headings (default 6)")
    ap.add_argument("--check", action="store_true", help="report without writing; non-zero exit if any need one")
    args = ap.parse_args()

    needs = 0
    for p in args.paths:
        if not p.is_file():
            print(f"  missing  {p}", file=sys.stderr)
            continue
        result = apply(p, args.depth, args.min_headings, args.check)
        if result == "skip":
            continue
        if result.startswith("NEEDS-TOC"):
            needs += 1
        print(f"  {result:<22} {p}")
    return 1 if needs else 0


if __name__ == "__main__":
    raise SystemExit(main())
