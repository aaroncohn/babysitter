#!/usr/bin/env python3
"""Install the Claude Code plugins enabled in .claude/settings.json, at project scope. Safe to re-run.
Added by `/babysitter:cloud-setup` (github.com/aaroncohn/babysitter); lives at .claude/install-plugins.py.

  python3 .claude/install-plugins.py                                  install every enabled plugin (the Setup script)
  python3 .claude/install-plugins.py --if-missing --session-start     the SessionStart hook: install what's missing, and
                                                                      tell the session if plugins landed after it started
  python3 .claude/install-plugins.py check                            self-tests

In a new cloud workspace, Conductor starts the first session while the Setup script is still installing, so that
session loads no plugins. Claude Code only loads plugins at startup or on /reload-plugins, so the hook tells the
session to have the user send it. The app caches the / picker's list, so it can stay stale until a new chat; typing a
skill's full name works meanwhile.
"""
import json, os, shutil, subprocess, sys, tempfile, time

ROOT = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
SETTINGS = os.path.join(ROOT, ".claude", "settings.json")
LOCK = os.path.join(os.path.expanduser("~"), ".claude", "install-plugins.lock")
WAIT, STALE = 100, 300  # seconds: how long to wait for the lock, and when a lock left by a killed run is stale


def installed(root=ROOT):
    config = os.environ.get("CLAUDE_CONFIG_DIR") or os.path.join(os.path.expanduser("~"), ".claude")
    try:
        plugins = json.load(open(os.path.join(config, "plugins", "installed_plugins.json"))).get("plugins", {})
    except (OSError, ValueError):
        return set()
    return {p for p, installs in plugins.items()
            if any(i.get("scope") == "user" or i.get("projectPath") == root for i in installs)}


def enabled(settings):
    return [p for p, on in (settings.get("enabledPlugins") or {}).items() if on]


def late_notice(late, now):
    # Plugins enabled but missing when the session started, and installed by now: tell the session.
    ready = [p for p in late if p in now]
    if not ready:
        return None
    msg = (f"plugins installed after this session started: {', '.join(ready)}. Send /reload-plugins to load them in this "
           "chat; the / picker may still miss them until you open a new chat, but typing a skill's full name works.")
    return {"systemMessage": msg, "hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext":
            msg + " Until /reload-plugins runs, their skills are missing from this session; if the user asks for one, "
            "tell them to send /reload-plugins first."}}


def take_lock(lock=LOCK, wait=WAIT, stale=STALE):
    # The Setup script and the first session's hook can run at once; two `marketplace add`s of one repo fail. Take turns.
    os.makedirs(os.path.dirname(lock), exist_ok=True)
    deadline = time.time() + wait
    while time.time() < deadline:
        try:
            os.mkdir(lock)
            return True
        except FileExistsError:
            try:
                if time.time() - os.stat(lock).st_mtime > stale:
                    shutil.rmtree(lock, ignore_errors=True)
                    continue
            except FileNotFoundError:
                continue
            time.sleep(1)
    return False


def main(args):
    original = open(SETTINGS).read()
    settings = json.loads(original)
    want = enabled(settings)
    late = [p for p in want if p not in installed()] if "--session-start" in args else []
    got = take_lock()
    failed = []
    try:
        have = installed() if "--if-missing" in args else set()
        todo = [p for p in want if p not in have]
        if todo:
            if not shutil.which("claude"):
                sys.exit("[install-plugins] claude CLI not on PATH; plugins not installed")
            run = lambda *a: subprocess.run(["claude", "plugin", *a, "--scope", "project"], cwd=ROOT,
                                            stdout=subprocess.DEVNULL).returncode == 0
            for name, m in (settings.get("extraKnownMarketplaces") or {}).items():
                src = m.get("source", {})
                if not run("marketplace", "add", src.get("repo") or src.get("url") or src.get("path", "")):
                    failed.append(f"marketplace {name}")
            for p in todo:
                if run("install", p):
                    print(f"[install-plugins] installed {p}", file=sys.stderr)
                else:
                    failed.append(p)
    finally:
        open(SETTINGS, "w").write(original)  # the CLI rewrites settings.json; keep the committed file as it was
        if got:
            shutil.rmtree(LOCK, ignore_errors=True)
    notice = late_notice(late, installed())
    if notice:
        print(json.dumps(notice))
    if failed:
        sys.exit("[install-plugins] failed: " + ", ".join(failed))


def check():
    assert enabled({"enabledPlugins": {"a@m": True, "b@m": False}}) == ["a@m"]
    assert late_notice(["a@m"], set()) is None
    n = late_notice(["a@m", "b@m"], {"a@m"})
    assert "a@m" in n["systemMessage"] and "b@m" not in n["systemMessage"] and n["hookSpecificOutput"]["hookEventName"] == "SessionStart"
    d = tempfile.mkdtemp()
    os.makedirs(os.path.join(d, "plugins"))
    json.dump({"plugins": {"a@m": [{"scope": "project", "projectPath": "/r"}], "b@m": [{"scope": "project", "projectPath": "/x"}],
                           "c@m": [{"scope": "user"}]}}, open(os.path.join(d, "plugins", "installed_plugins.json"), "w"))
    old = os.environ.get("CLAUDE_CONFIG_DIR")
    os.environ["CLAUDE_CONFIG_DIR"] = d
    try:
        assert installed("/r") == {"a@m", "c@m"}
    finally:
        os.environ.pop("CLAUDE_CONFIG_DIR") if old is None else os.environ.update(CLAUDE_CONFIG_DIR=old)
    lock = os.path.join(d, "lock")
    assert take_lock(lock) and not take_lock(lock, wait=0.5)  # held: the second run waits, then gives up
    os.utime(lock, (0, 0))
    assert take_lock(lock, wait=2)  # a stale lock from a killed run is cleared
    shutil.rmtree(d)


if __name__ == "__main__":
    check()
    if sys.argv[1:] != ["check"]:
        main(sys.argv[1:])
