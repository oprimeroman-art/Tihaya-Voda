#!/usr/bin/env python3
"""Package the existing offline game and full Studio/project, with current sources."""
from pathlib import Path
import hashlib,json,zipfile
ROOT=Path(__file__).resolve().parents[1]
def package():
    project=ROOT/'game-project'; source=ROOT/'game/source-project.zip'
    with zipfile.ZipFile(source,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for f in sorted(project.rglob('*')):
            if f.is_file():z.write(f,f.relative_to(project))
    out=ROOT/'dist';out.mkdir(exist_ok=True)
    with zipfile.ZipFile(out/'Tihaya-Voda-Working-Build.zip','w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for dirname in ('game','game-editor','game-project','studio'):
            for f in sorted((ROOT/dirname).rglob('*')):
                if f.is_file():z.write(f,f.relative_to(ROOT))
        readme='Протокол «Тихая вода» — рабочая сборка\n\nРаспакуйте архив полностью.\ngame/index.html — игра; studio/index.html — Studio; game-editor/index.html — альтернативный игровой экспорт.\nПроект для импорта: game/source-project.zip.\nЗапуск в Chrome/Chromium двойным щелчком, интернет не требуется.\nСохранения: меню Esc; переносимый SAVE.json.\n\nЭто рабочая итерация, не объявленный законченный релиз. Часть окружения и постановки требует проверки; звуки и видео сохранены без изменений.\n'
        z.writestr('READ_ME_RU.txt',readme)
        report=ROOT/'reports/WORK_ITERATION.md'
        if report.exists():z.write(report,'QA_REPORT_RU.md')
    print(out/'Tihaya-Voda-Working-Build.zip')
if __name__=='__main__':package()
