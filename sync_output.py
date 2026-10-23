"""Mirror only generated public output at the legacy repository root."""
from pathlib import Path
import shutil
ROOT=Path(__file__).resolve().parent
# Explicit list only: never touch Hugo source, tooling, or .git.
for name in ['index.html','404.html','sitemap.xml','reading.css','reading.js','CNAME','.nojekyll','chapters','tonglu','dudong','reports','market.css']:
    target=ROOT/name
    if target.is_dir():shutil.rmtree(target)
    elif target.exists():target.unlink()
for source in (ROOT/'docs').iterdir():
    target=ROOT/source.name
    if source.is_dir():shutil.copytree(source,target)
    else:shutil.copy2(source,target)
print('Generated docs mirrored to repository root')
