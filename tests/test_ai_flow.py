import importlib.util
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts/ai_docs.py'
spec = importlib.util.spec_from_file_location('ai_docs', SCRIPT)
docs = importlib.util.module_from_spec(spec)
spec.loader.exec_module(docs)

class AgentDocsTests(unittest.TestCase):
    def test_code_mapping(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / 'navigation.md'
            path.write_text('---\ntitle: Navigation\nsummary: Room changes\ncode_paths: ["studio/**"]\n---\nContent\n', encoding='utf-8')
            m, b = docs.parse_doc(path)
            self.assertEqual(len(docs.related('studio/index.html', [(path, m, b)])), 1)
            self.assertEqual(docs.related('game/index.html', [(path, m, b)]), [])
            self.assertEqual(m['code_paths'], ['studio/**'])
    def test_legacy_indexed(self):
        original = docs.DOCS
        try:
            with tempfile.TemporaryDirectory() as d:
                docs.DOCS = Path(d)
                p = docs.DOCS / 'archive.txt'
                p.write_text('Old content', encoding='utf-8')
                self.assertIn('archive.txt', docs.render([(p, {}, 'Old content')]))
        finally:
            docs.DOCS = original

if __name__ == '__main__':
    unittest.main()
