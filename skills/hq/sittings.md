# Owner-check sittings

Read this when the user asks to clear the owner-check backlog (hq step 10). The aim: every open owner check, test, decision and action ends with an outcome or an owner, and the user's time goes only to what still needs a person, in two sittings instead of hundreds of one-off items.

## 1. Gather the list

Collect every open item, each with where it came from:
- `state.py item list --open` (the OA, OD and OT items)
- the owner checks still open in the roadmap (`owner check open: …` notes), and in archived changes' proposals and `retro.md`s

## 2. Hand it to a session as an OpenSpec change

Open a follow-up workspace the way step 9 does (a new workspace with a self-contained brief), and babysit it like any other. Brief it as in step 3, plus:

> Run this as one OpenSpec change, `owner-check-sitting-<date>`. Its ledger is `checks.md`, one table: `id | source | item | bucket | how to check / evidence | outcome`. Keep every item's ID. Sort each into one bucket:
> - **superseded**: a later change replaced it; name that change and what it changed. Only when that's true; when it kept part of it, narrow the item instead. When in doubt, it stays.
> - **already done**, with the evidence
> - **moved**: it belongs to another roadmap row; name it
> - **agent action**: you can do it; do it
> - **user action**: only the user can; tell me, it goes to Open Actions
> - **assumption**: a choice made without the user, for the desk sitting
> - **desktop check**: a desktop browser can judge it; run it yourself on dev and save a screenshot to `evidence/`
> - **device check**: it needs a real phone, tablet, screen reader or the user's own inbox, for the device sitting
>
> Then write the two sitting files and tell me when each is ready (`DESK SITTING READY`, `DEVICE SITTING READY`). Each failure becomes a new roadmap row in this change's PR, and its ledger outcome names it (`failed → <row>`). Open the PR as a draft until both sittings are done. Before archiving, every item has a final outcome or `owner: <row or OA/OT/OD id>`, and `owner-check.py` passes.

## 3. The desk sitting (assumptions)

`assumptions.md`: one list, the risky ones first (money, privacy, data loss, accessibility, copy users read), then grouped by area, one plain sentence each, with its evidence (a screenshot or a link). Where the agent suggests a change, it says now / why / proposal / recommendation.

Send it to Open Decisions as **one** item (examples/sitting.md): the user replies "all fine", or names the IDs they want changed. Each named ID becomes a roadmap row (`reversed → <row>`). Every ID they don't name is recorded as `accepted as built (<user>, <date>)`. That one reply is the decision: nothing is accepted by silence, so with no reply, nothing is recorded.

## 4. The device sitting

`device-script.md`: one numbered script, grouped by device (e.g. phone browser, screen reader, desktop browser, inbox), each step with its item IDs in brackets, where to go, what to do and what should happen. It says how long it takes, and that a fail needs a screenshot.

Before sending it, check the user can sign in on their phone (one short Open Tests item: "open <link> on your phone and sign in"; with `sign-in codes`, the agent can't read the phone's screen, so the user enters the code). Then send the script to Open Tests as **one** item (examples/sitting.md). The user replies per step: `pass`, `fail: <what happened>` or `skip`. Skipped steps keep their owner; fails become roadmap rows.

## 5. Close it out

When both sittings are answered: the ledger has every outcome, the old OA, OD and OT items it covered are marked (`state.py item set <ID> --status answered --note "sitting: <outcome>"`), the new rows are in the roadmap, `retro.md` is written, and the change is archived. Say in the next digest how many items closed, how many became rows, and how many still have an owner.
