# 晚班地图师 · ICZSC

Public read-only serialized fiction at https://iczsc.com/.
The existing Hugo source structure and GitHub Pages deployment remain unchanged:
source is `content/`, `layouts/`, `static/`; Pages publishes `main:/docs`.
Do not change DNS, CNAME, deployment settings, or unrelated branches.

## Build

Preferred: `hugo --cleanDestinationDir`, then `python sync_output.py`.
This environment did not have Hugo; its local release candidate was generated
with the explicitly limited, dependency-free renderer:
`python build_static.py`, then `python sync_output.py`.
The fallback supports plain paragraphs, `##` headings, and horizontal rules;
it rejects unsupported Markdown rather than silently mangling it.
It reads the real current time by default and excludes draft/future chapters.
Run `python validate.py --expected-chapters 1 --check-mirror` for chapter 1.
Update the expected count on later releases. Root static files intentionally
mirror `docs/` to preserve the repository's existing output arrangement.

## Publication safety

Chapters live in `content/chapters/001.md`, etc., ordered by unique `weight`.
Use explicit `+08:00` dates and publishDate. First release is scheduled for
2026-10-18 00:30 Asia/Shanghai (2026-10-17 16:30 UTC).
Never push an unreleased chapter to any public branch, even with `draft: true`.
Before any public commit/push, run `python release_check.py` with the real clock.
A test build with `--now` is only a private preview, never permission to publish.
Keep future drafts, plot outlines, and continuity notes entirely outside this repo.
Only the completed first chapter is in this release candidate.

Before releasing, recheck the remote main SHA and open pull requests. If main
changed from bbb888ef669aa5fe54bd19aa150671ee9dc80304, stop and reconcile instead
of overwriting it. Do not touch add-referral-link or move-referral-side-20260821.
Use a dedicated feature branch and reviewable PR; verify Pages succeeds and
iczsc.com serves the correct first chapter after merge. No database or visitor
write endpoints. No analytics, external fonts, or third-party scripts.

## Recovery

Old site remains recoverable at commit
bbb888ef669aa5fe54bd19aa150671ee9dc80304 in alzmo/iczsc.
A complete Git bundle and tree archive were also retained privately before edits.
If rollback is necessary, restore that tree in a new commit after checking remote
state; do not force-push or delete repository history.

## Promotion

Keep the original disclosed 狗狗加速 promotion URL and all of
`target="_blank" rel="sponsored nofollow noopener noreferrer"` intact.
