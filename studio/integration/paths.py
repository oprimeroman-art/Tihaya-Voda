from pathlib import Path
STUDIO=Path(__file__).resolve().parent.parent
ROOT=STUDIO/'content'
OUT=STUDIO/'build'
OUT.mkdir(exist_ok=True)
def read(rel): return (ROOT/rel).read_text(encoding='utf-8-sig')
