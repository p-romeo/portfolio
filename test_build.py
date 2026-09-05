"""Run with python3 -B test_build.py; builds without existing output."""
import os
from pathlib import Path
import shutil
import tempfile

import build

certs = build.parse_certs(
    '- **Test** | Issuer | 2026 | logo:test.svg | credential_id: ABC '
    '| verify_url:https://example.com/verify | icon_text: T\n'
    '- **Other** | Issuer | 2025'
)
assert certs[0] == dict(name='Test', issuer='Issuer', year='2026', url='',
                       logo='test.svg', credential_id='ABC',
                       verify_url='https://example.com/verify', icon_text='T')
assert 'credential_id' not in certs[1]
root = Path(__file__).resolve().parent
with tempfile.TemporaryDirectory() as tmp:
    shutil.copytree(root, tmp, dirs_exist_ok=True,
                    ignore=shutil.ignore_patterns('.git', '.wrangler', 'site', '__pycache__'))
    os.chdir(tmp)
    build.ROOT = tmp
    build.CONTENT = str(Path(tmp) / 'content')
    build.SITE = str(Path(tmp) / 'site')
    build.render()
    site = Path('site')
    assert (site / 'index.html').read_text().count('class="badge"') == 15
    assert (site / 'projects/index.html').read_text().count('<article ') == 8
    for source in ('Paul-Romeo-Resume.pdf', 'tools/Paul-Romeo-Resume.docx'):
        assert (site / Path(source).name).read_bytes() == Path(source).read_bytes()
    for name in ('robots.txt', 'sitemap.xml', 'llms.txt'):
        assert 'https://paulromeo.net/' in (site / name).read_text()
    os.chdir(root)
print('PASS: certificate metadata, clean build, 15 badges, 8 projects, downloads, discovery files')
