"""Run immediately before publishing any source or output to a public branch.
No clock override is permitted: public Git source can leak unreleased chapters.
"""
from datetime import datetime, timezone
from pathlib import Path
from build_static import metadata
ROOT=Path(__file__).resolve().parent
now=datetime.now(timezone.utc)
for path in (ROOT/'content/chapters').glob('*.md'):
    if path.name.startswith('_'):continue
    meta,_=metadata(path)
    due=datetime.fromisoformat(meta.get('publishDate',meta['date']))
    assert due.tzinfo, 'Missing publication timezone'
    assert meta.get('draft','false').lower()!='true', f'Draft source cannot enter public tree: {path.name}'
    assert now>=due, f'NOT RELEASED: {path.name}; publication time {due.isoformat()}'
assert not list(ROOT.rglob('continuity-private*')), 'Private author notes in release tree'
print('Publication time gate passed for all chapter source files.')
