#!/usr/bin/env python3
"""Set a repo up so babysitter's skills are in the / picker of every new cloud workspace. Run from the repo's root.

  cloud-setup.py vendor <skills dir> [--from <babysitter checkout>]
      copy the skills into <skills dir>/babysitter-<name>/, renamed and with their links rewritten (see below).
      Without --from, clones the latest release from GitHub first.
  cloud-setup.py apply vendored   vendor into .claude/skills, add the daily sync workflow, turn the plugin off
  cloud-setup.py apply hook       keep the plugin: add .claude/install-plugins.py and its SessionStart hook
  cloud-setup.py check            self-tests

Why vendor: Conductor starts a new cloud workspace's first session before the Setup script installs plugins,
and the app caches the picker's list, so plugin skills can be missing even after /reload-plugins. Skills
committed to .claude/skills/ are there from the first moment.

The rewrite: Claude Code names a project skill after its folder, and Conductor's picker shows the frontmatter
name, so both become babysitter-<name> (which also keeps doctor apart from Claude Code's built-in command).
Every `/babysitter:<name>` becomes `/babysitter-<name>`, and every `../<name>/` (one skill reaching a
sibling's files, e.g. ../hq/state.py) becomes `../babysitter-<name>/`. Each copy gets a .babysitter-source
file with the commit it came from, which doctor compares with the latest release.
"""
import json, os, re, shutil, subprocess, sys, tempfile

REPO = "aaroncohn/babysitter"
PLUGIN = "babysitter@babysitter"
HERE = os.path.dirname(os.path.realpath(__file__))
SKIP = {"cloud-setup"}  # needs the plugin's own files; run it from the plugin
STAMP = ".babysitter-source"
WORKFLOW = ".github/workflows/sync-babysitter-skills.yml"
HOOK = 'python3 "$CLAUDE_PROJECT_DIR/.claude/install-plugins.py" --if-missing --session-start'


def rewrite(text, names, skill_md):
    alt = "|".join(sorted(map(re.escape, names), key=len, reverse=True))
    text = re.sub(rf"\bbabysitter:({alt})\b", r"babysitter-\1", text)
    text = re.sub(rf"\.\./({alt})/", r"../babysitter-\1/", text)
    if skill_md:
        text = re.sub(r"^name: (?!babysitter-)", "name: babysitter-", text, count=1, flags=re.M)
    return text


def vendor(dest, source):
    root = os.path.join(source, "skills")
    names = sorted(n for n in os.listdir(root) if os.path.isfile(os.path.join(root, n, "SKILL.md")) and n not in SKIP)
    sha = subprocess.run(["git", "-C", source, "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip() or "unknown"
    os.makedirs(dest, exist_ok=True)
    for old in os.listdir(dest):  # replace every earlier copy, so a skill removed upstream goes here too
        if old.startswith("babysitter-"):
            shutil.rmtree(os.path.join(dest, old))
    for n in names:
        to = os.path.join(dest, "babysitter-" + n)
        shutil.copytree(os.path.join(root, n), to, ignore=shutil.ignore_patterns("__pycache__"))
        for d, _, files in os.walk(to):
            for f in files:
                p = os.path.join(d, f)
                try:
                    text = open(p, encoding="utf-8").read()
                except UnicodeDecodeError:
                    continue
                out = rewrite(text, names, f == "SKILL.md" and d == to)
                if out != text:
                    open(p, "w", encoding="utf-8").write(out)
        open(os.path.join(to, STAMP), "w").write(f"{REPO}@{sha}\n")
    print("vendored " + ", ".join("babysitter-" + n for n in names) + f" from {sha[:12]}")


def latest_checkout():
    tmp = tempfile.mkdtemp(prefix="babysitter-")
    subprocess.run(["git", "clone", "--quiet", "--depth", "1", f"https://github.com/{REPO}.git", tmp], check=True)
    return tmp


def settings(path=".claude/settings.json"):
    try:
        return json.load(open(path))
    except FileNotFoundError:
        return {}


def save(data, path=".claude/settings.json"):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, "w").write(json.dumps(data, indent=2) + "\n")


def apply(kind):
    s = settings()
    if kind == "vendored":
        src = latest_checkout()
        vendor(".claude/skills", src)
        os.makedirs(os.path.dirname(WORKFLOW), exist_ok=True)
        shutil.copy(os.path.join(HERE, "sync-babysitter-skills.yml"), WORKFLOW)
        s.setdefault("enabledPlugins", {})[PLUGIN] = False  # or every skill shows twice
        save(s)
        print(f"added {WORKFLOW}; set {PLUGIN} to false in .claude/settings.json")
    elif kind == "hook":
        shutil.copy(os.path.join(HERE, "install-plugins.py"), ".claude/install-plugins.py")
        s.setdefault("extraKnownMarketplaces", {})["babysitter"] = {"source": {"source": "github", "repo": REPO}, "autoUpdate": True}
        s.setdefault("enabledPlugins", {})[PLUGIN] = True
        start = s.setdefault("hooks", {}).setdefault("SessionStart", [])
        if not any(h.get("command") == HOOK for e in start for h in e.get("hooks", [])):
            start.append({"matcher": "startup|resume|clear|compact", "hooks": [{"type": "command", "command": HOOK, "timeout": 120}]})
        save(s)
        print("added .claude/install-plugins.py and its SessionStart hook to .claude/settings.json")
    else:
        sys.exit("apply vendored | apply hook")


def check():
    names = ["hq", "doctor", "safe-to-archive", "pause"]
    t = rewrite("name: hq\nrun `/babysitter:hq`, `/babysitter:safe-to-archive`, then ../hq/state.py and ../doctor/x;\n"
                "keep babysitter@babysitter, `/babysitter:…`, ../other/ and `/babysitter:hqx`\n", names, True)
    assert t.startswith("name: babysitter-hq\n"), t
    assert "`/babysitter-hq`, `/babysitter-safe-to-archive`" in t and "../babysitter-hq/state.py" in t and "../babysitter-doctor/x" in t, t
    assert "babysitter@babysitter" in t and "`/babysitter:…`" in t and "../other/" in t and "`/babysitter:hqx`" in t, t
    assert rewrite("name: babysitter-hq\n", names, True) == "name: babysitter-hq\n"  # running it twice changes nothing
    assert "description: name: x" in rewrite("name: hq\ndescription: name: x\n", names, True)


if __name__ == "__main__":
    check()
    a = sys.argv[1:]
    if a[:1] == ["vendor"] and len(a) >= 2:
        vendor(a[1], a[a.index("--from") + 1] if "--from" in a else latest_checkout())
    elif a[:1] == ["apply"] and len(a) == 2:
        apply(a[1])
    elif a[:1] != ["check"]:
        sys.exit(__doc__)
