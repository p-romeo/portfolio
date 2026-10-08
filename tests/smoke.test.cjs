const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');

const dist = path.join(__dirname, '..', 'dist');

test('built site links to the current, consistent resume files', () => {
  const html = fs.readFileSync(path.join(dist, 'index.html'), 'utf8');
  const llms = fs.readFileSync(path.join(dist, 'llms.txt'), 'utf8');
  const links = [...html.matchAll(/href="\/(Paul-Romeo-Resume-[^"]+\.(?:pdf|docx))"/g)].map((m) => m[1]);
  assert.equal(links.length, 2);
  assert.match(html, /Online Stores &amp; IT/);
  assert.doesNotMatch(html, /single threat actor|payment processors|takedowns in progress/i);
  assert.ok(llms.includes(links.find((name) => name.endsWith('.pdf'))));
  for (const name of links) {
    const source = name.endsWith('.pdf') ? 'Paul-Romeo-Resume.pdf' : 'tools/Paul-Romeo-Resume.docx';
    assert.deepEqual(fs.readFileSync(path.join(dist, name)), fs.readFileSync(path.join(__dirname, '..', source)));
  }
});
