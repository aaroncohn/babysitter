# Example: the final report

Step 8. The product is made up.

---

**All three changes are live on production** as of 9:12 am EST (commit `4f2e1c9`), mode: standard.

**Shipped**

| change | PR | archive PR | merged | archived | seen working |
| --- | --- | --- | --- | --- | --- |
| Shared folders (m11) | #214 | #217 | ✅ | ✅ | ✅ screenshots on dev, in PR #214 |
| Magic-link sign-in (m12) | #219 | #223 | ✅ | ✅ | ✅ on dev; on a phone: OT006 open |
| Note export to PDF (m14) | #221 | #224 | ✅ | ✅ | ✅ you opened one at 8:50 am |

Full CI on main ✅ (run 5120), dev ✅ (health endpoint serves `4f2e1c9`), production ✅ (deploy 311, https://app.example.com serves `4f2e1c9`, one migration applied: `folders_shared_at`).

**Skipped:** explore-m15-search (still exploring; not touched).

**Open actions: 0 · Open decisions: 2 (OD012, OD014) · Open tests: 3 (OT006, OT007, OT008)**
Open Decisions and Open Tests are the workspaces of those names. OA004 (the production e-mail key) came back done at 8:40 am and the release waited for it.

**Retros**
- Shared folders: M as estimated; nothing failed; one batched decision (the folder icon) kept.
- Magic-link sign-in: M as estimated; CI on main broke once after the merge (an expired e-mail test key). Next time: check test keys before the e-mail suite.
- Note export: really an L, not M; the export needed its own job. Next time: size anything that renders files as L.
- Across them: test keys and file rendering cost the most time.

**Follow-ups**
1. The export runs on the web server; if PDFs get slow, move it to a job (the session left a note in `docs/export.md`).

**Clean-up**
- archive-m11-shared-folders: ✅ safe to archive
- archive-m12-magic-link: ✅ safe to archive
- archive-m14-export: ⛔ one untracked file, `.context/export-sample.pdf`; delete it or keep it, then archive

I'll keep watching the three queues and carry out answers as they come back.
