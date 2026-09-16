"""Static asset/link and secret-pattern checks; stdlib-only, no secret values printed."""
import json
import re
import subprocess
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urljoin, urlsplit

root = Path(__file__).resolve().parents[1]
site = root / 'site'
class Page(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.links, self.ids = [], set()
        self.feed(text)
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if 'id' in a: self.ids.add(a['id'])
        for key in ['href', 'src']:
            if key in a: self.links.append(a[key])

pages = {p.relative_to(site).as_posix(): Page(p.read_text()) for p in site.rglob('*.html')}
failures, checked, external = [], 0, set()
for name, page in pages.items():
    for link in page.links:
        url = urlsplit(urljoin('https://local.invalid/' + name, link))
        if url.scheme not in ['http', 'https']: continue
        if url.netloc != 'local.invalid':
            external.add(link)
            continue
        target = unquote(url.path).lstrip('/')
        if not target or target.endswith('/'): target += 'index.html'
        checked += 1
        if not (site / target).is_file(): failures.append(f'{name}: missing {target}')
        elif url.fragment and target in pages and unquote(url.fragment) not in pages[target].ids:
            failures.append(f'{name}: missing fragment {target}#{url.fragment}')
patterns = {
    'private key': rb'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----',
    'GitHub token': rb'gh[pousr]_[A-Za-z0-9]{30,}',
    'AWS access key': rb'AKIA[0-9A-Z]{16}',
    'API secret assignment': rb'(?i)(?:api[_-]?key|secret|password)\s*[:=]\s*[\"\'][A-Za-z0-9_./+-]{20,}',
}
tracked = subprocess.check_output(['git', 'ls-files', '-z'], cwd=root).decode().split('\0')
for name in filter(None, tracked):
    data = (root / name).read_bytes()
    for label, pattern in patterns.items():
        if re.search(pattern, data): failures.append(f'{name}: possible {label} (value withheld)')
print(json.dumps({'internal_references_checked': checked, 'external_urls': sorted(external), 'tracked_files_scanned': len(list(filter(None, tracked))), 'failures': failures}, indent=2))
assert not failures
