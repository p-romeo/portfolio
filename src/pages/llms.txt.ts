import type { APIRoute } from 'astro';
import { getCollection } from 'astro:content';

export const GET: APIRoute = async () => {
  const projects = (await getCollection('projects'))
  .filter((p) => !p.data.hidden)
  .sort((a, b) => Number(a.data.weight ?? 99) - Number(b.data.weight ?? 99));
  const titles = projects.map((p) => p.data.title).join(', ');
  const llms = [
    '# Paul Joseph Romeo — Cybersecurity & IT',
    '',
    '> IT & security administrator at Belmont Leather Co: phishing defense,',
    '> endpoint & network security; working toward a full incident-response role.',
    '',
    '## Pages',
    '',
    '- [Home](https://paulromeo.net/): about, experience, certifications, skills, résumé',
    `- [Projects](https://paulromeo.net/projects/): ${titles}`,
    '- [Résumé (PDF)](https://paulromeo.net/Paul-Romeo-Resume.pdf): current résumé, kept up to date',
    '',
    '## Contact',
    '',
    '- Email: pauljromeo@proton.me',
    '',
  ].join('\n');
  return new Response(llms, { headers: { 'Content-Type': 'text/plain; charset=utf-8' } });
};
