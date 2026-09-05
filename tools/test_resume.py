"""Run with python -B tools/test_resume.py; checks text without fonts or fpdf2."""
import json
from pathlib import Path
import runpy
import sys
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

root = Path(__file__).resolve().parent
spec = json.loads((root / 'resume_spec.json').read_text(encoding='utf-8'))
pdf = MagicMock(w=612, pages_count=1)
pdf.get_y.return_value = 0
pdf.get_string_width.return_value = 50
with patch.dict(sys.modules, fpdf=SimpleNamespace(FPDF=lambda **kwargs: pdf)):
    runpy.run_path(str(root / 'resume.py'))
actual = [call.args[2] for call in pdf.method_calls
          if call[0] in ('cell', 'multi_cell') and call.args[2] != '-']
expected = [text for block in spec['blocks'] for text in
            (block['items'] if block['type'] == 'bullet_list' else
             [block.get('text', ''.join(run['text'] for run in block.get('runs', [])))])]
assert ''.join(''.join(actual).split()) == ''.join(''.join(expected).split())
pdf.output.assert_called_once_with('Paul-Romeo-Resume.pdf')
print('PASS: every resume block renders once, in order, with unchanged wording')
