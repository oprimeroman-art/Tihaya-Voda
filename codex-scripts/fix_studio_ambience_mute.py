from pathlib import Path
p=Path("studio/index.html")
s=p.read_text(encoding="utf-8")
old="lfoGain.connect(master.gain);noiseGain.connect(master);"
new="lfoGain.connect(noiseGain.gain);noiseGain.connect(master);"
if s.count(old)!=1: raise SystemExit(f"expected one ambience modulation hook, got {s.count(old)}")
s=s.replace(old,new,1);p.write_text(s,encoding="utf-8");print("PASS master mute remains absolute")
