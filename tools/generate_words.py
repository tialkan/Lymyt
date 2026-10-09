"""Render the same UTF-8 word deck for the firmware and public guide."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
words = json.loads((ROOT / 'data/words.json').read_text())
assert 0 < len(words) <= 32
assert len({w['en'] for w in words}) == len(words)
quote = lambda value: json.dumps(value, ensure_ascii=False)
header = '#pragma once\n// Generated from data/words.json; edit the JSON, then run tools/generate_words.py.\n'
header += 'struct WordCard { const char* en; const char* tr; };\n'
header += 'static const WordCard WORDS[] = {\n'
header += '\n'.join('  {' + quote(w['en']) + ', ' + quote(w['tr']) + '},' for w in words)
header += '\n};\nstatic const unsigned WORD_COUNT = sizeof(WORDS) / sizeof(WORDS[0]);\n'
(ROOT / 'firmware/Lymyt/Words.h').write_text(header)

