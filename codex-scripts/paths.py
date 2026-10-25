from pathlib import Path
ROOT = Path(r'C:\Users\user\Desktop\TIHAYA_VODA_CODEX_PACK_V2')
STUDIO = ROOT / 'Gagarin_Panorama_Studio_2_8_RU_EN_OFFLINE/Gagarin_Panorama_Studio_2_8'
OUT = Path(__file__).resolve().parent.parent / 'outputs'
OUT.mkdir(exist_ok=True)
def read(rel): return (ROOT/rel).read_text(encoding='utf-8-sig')
