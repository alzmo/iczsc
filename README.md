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

## Independent series: 同路

The legacy book owns only `content/chapters/`, `/chapters/`, and its existing
home-page chapter list. Its cadence and all existing chapter links stay unchanged.
Tonglu owns `content/tonglu/chapters/`, `/tonglu/`, and `/tonglu/chapters/`.
Do not put Tonglu content in the legacy chapter directory. Do not change the
legacy Hugo `Section == chapters` selector to a global RegularPages collection.
Tonglu uses its own Hugo type/templates and the separate `build_tonglu.py`
renderer; both are called by the existing full-site build. No new publication
schedule is configured. Shared CSS/theme preferences are presentation only.

For each release, fetch fresh main and reconcile concurrent PRs. The original
backup anchor above is recovery history, not the current publication base.
Run `python build_static.py`, `python sync_output.py`,
`python validate.py --expected-chapters 13 --check-mirror`,
`python test_isolation.py`, and `python release_check.py` (real clock).
Update the legacy expected count only when that book gains a chapter.
The release gate covers both books recursively. Publish only reviewed prose;
never upload planning material or unreleased chapters, even to public branches.
Verify Pages deployment for the merge SHA and both books on the actual domain.

## Independent series: 渡冬

Dudong owns only `content/dudong/chapters/`, `/dudong/`, and
`/dudong/chapters/`, with its own Hugo type/templates and `build_dudong.py`.
The home page links all three books separately. Both existing books retain their
source directories, chapter numbering, navigation, and publication cadence.
Only editorially reviewed final chapters may enter this public repository.
Manuscripts, future outlines, editorial notes, and backups remain private.
No new automatic publication schedule is configured for Dudong.

For a full release, run the build and mirror commands above,
`python validate.py --expected-chapters 13 --check-mirror`,
`python test_isolation.py`, `python test_dudong.py`, and
`python release_check.py`. The expected chapter count in validate.py concerns
only the legacy book; update it only when that book gains a chapter.
Recheck fresh main and open PRs before publication; reconcile changes rather
than overwriting them. Verify the exact merge commit's Pages result and all
three books on the live domain.

The legacy Hugo permalink uses `:filename` to preserve the existing numbered
`/chapters/001/` URLs when a chapter does not declare a slug. This is a routing
compatibility fix, not a rewrite of any existing prose.

Dudong catalogs group only already-published chapters by volume. The original
first 40 chapters default to 第一卷 · 云州雪夜. Every later chapter must declare
its editorially confirmed `volume` number and `volumeTitle`. Never put an
unpublished volume or future chapter range into public catalog metadata.
Chapter URLs stay numbered and previous/next navigation continues across volumes.
