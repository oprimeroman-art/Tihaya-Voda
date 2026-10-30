#!/usr/bin/env python3
"""Package the existing editable project reproducibly; never regenerate media."""
from pathlib import Path
from zipfile import ZipFile, ZipInfo, ZIP_DEFLATED
ROOT=Path(__file__).resolve().parents[1]
def package():
 target=ROOT/'game/source-project.zip'
 with ZipFile(target,'w',ZIP_DEFLATED) as archive:
  for file in sorted((ROOT/'game-project').rglob('*')):
   relative=file.relative_to(ROOT/'game-project')
   if not file.is_file() or any(part.startswith('.') for part in relative.parts):continue
   entry=ZipInfo(relative.as_posix(),date_time=(2026,1,1,0,0,0));entry.compress_type=ZIP_DEFLATED;entry.external_attr=0o100644<<16
   archive.writestr(entry,file.read_bytes())
 print('Packaged existing editable project:',target.relative_to(ROOT),target.stat().st_size,'bytes')
if __name__=='__main__':package()
