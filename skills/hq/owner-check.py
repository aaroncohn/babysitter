#!/usr/bin/env python3
"""No owner check without an owner. Read-only; run from a repo's root.

  owner-check.py [file ...]   fail on any line that says an owner check is open but names no owner
  owner-check.py check        self-tests

With no files, it reads the roadmap files git tracks (roadmap*.md, anywhere). A line about an owner check that
is "open" must name who carries it, as `owner: <id>`: a roadmap row still to do (`owner: 4.21`) or a queue item
(`owner: OT012`), comma separated for several. Without that, "done" quietly comes to mean "merged": one fast-moving
project piled up hundreds of owner checks nobody held. Projects can run this in CI.
"""
import re, subprocess, sys

CHECK = re.compile(r"owner[ -]?checks?", re.I)
# "open" as a word, not "opened", "open-in-new-tab", or the Open Actions/Tests/Decisions queues
OPEN = re.compile(r"(?<![\w-])open(?![\w-])(?! (?:actions?|tests?|decisions?)\b)", re.I)
OWNER = re.compile(r"owner: `?([\w.]+)`?((?:, `?[\w.]+`?)*)", re.I)


def problems(lines, where="?"):
    out = []
    for n, line in enumerate(lines, 1):
        if not (CHECK.search(line) and OPEN.search(line)):
            continue
        if not OWNER.search(line):
            out.append(f"{where}:{n}: an owner check is open but names no owner (add `owner: <roadmap row or OA/OT/OD id>`): {line.strip()[:120]}")
    return out


def tracked_roadmaps():
    files = subprocess.run(["git", "ls-files"], capture_output=True, text=True).stdout.splitlines()
    return [f for f in files if re.search(r"(^|/)roadmap[^/]*\.md$", f, re.I)]


def check():
    rows = ["| 3 | c | done (#1). Owner check open: export on iPhone |",
            "| 4 | d | done (#2). Owner checks open: x, owner: OT012 |",
            "| 5 | e | done (#3). Owner check still open, Owner: `4.21`. |",
            "| 6 | f | done (#4); owner check opened in a new tab |",
            "| 7 | g | done (#5); owner checks went to Open Tests |",
            "- owner checks still open",
            "| 8 | h | done; all owner checks passed |"]
    p = problems(rows, "r")
    assert [x.split(":")[1] for x in p] == ["1", "6"], p


if __name__ == "__main__":
    check()
    args = sys.argv[1:]
    if args == ["check"]:
        sys.exit(0)
    found = []
    for f in args or tracked_roadmaps():
        try:
            found += problems(open(f, encoding="utf-8").read().splitlines(), f)
        except OSError as e:
            sys.exit(f"owner-check: {e}")
    if found:
        print(f"owner-check: {len(found)} open owner check(s) with no owner:\n" + "\n".join(found))
        sys.exit(1)
    print("owner-check: every open owner check names its owner")
