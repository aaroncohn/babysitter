---
name: cloud-setup
description: Set this repo up so babysitter's skills are in the / picker of every new Conductor cloud workspace, from its first session. Either commits copies of the skills to .claude/skills/ with a daily GitHub Action that keeps them current (recommended), or keeps the plugin installed with an install script and a SessionStart hook that tells a session to /reload-plugins when plugins land late. Writes files and shows the diff; never commits. Run with `/babysitter:cloud-setup`.
disable-model-invocation: true
---

# cloud-setup

In a new cloud workspace, Conductor starts the first session before the repository's Setup script has installed plugins, and the app caches the `/` picker's list, so `/babysitter:` skills can be missing even after `/reload-plugins`. This sets the repo up so they aren't. Run it from the repo's root, in a workspace on a fresh branch.

1. Read `.claude/settings.json` (it may not exist) and check for `.claude/skills/babysitter-*/` or `.claude/install-plugins.py` from an earlier run. Say what's there.
2. Ask, in one message, and wait for the letter:
   - **a. Copies of the skills in the repo (recommended).** They're in the picker from the first moment. A GitHub Action refreshes them daily and pushes any change to the default branch. They're named `/babysitter-hq`, `/babysitter-doctor` and so on (a dash, not a colon), and the plugin is turned off in this repo so nothing shows twice. Costs: a few hundred KB in the repo, and a daily commit when babysitter changes.
   - **b. Keep the plugin installed.** An install script for the Setup script, plus a `SessionStart` hook that installs what's missing and, when plugins landed after the session started, tells it to `/reload-plugins`. The picker may still miss them until a new chat; typing the full `/babysitter:…` name works.
3. Run `python3 <this skill's dir>/cloud-setup.py apply vendored` for a, or `apply hook` for b. It writes the files and edits `.claude/settings.json`, keeping everything else in it.
4. Show `git status --short` and the `settings.json` diff. Don't commit or push: tell the user to commit it on a branch and merge it the way the repo does.
5. Then tell them what's left, which only they can do:
   - **a:** the workflow needs to push. If the repo or organization restricts it, allow it under Settings → Actions → General → Workflow permissions ("Read and write"), or change the workflow's last step to open a PR. If the repo requires a particular commit author, set it in that step. After merging, run it once: `gh workflow run sync-babysitter-skills.yml`. If the repository's Setup script in the cloud organization settings installs the babysitter plugin, remove that line.
   - **b:** set the repository's Setup script, in Conductor's cloud organization settings (not `.conductor/settings.toml`, which is local-only), to `python3 .claude/install-plugins.py`.
   - Either way: `/babysitter:doctor` (`/babysitter-doctor` with a) in a new cloud workspace confirms it.
