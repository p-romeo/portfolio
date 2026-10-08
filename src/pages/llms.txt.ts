import type { APIRoute } from 'astro';
import { getCollection } from 'astro:content';

export const GET: APIRoute = async () => {
  const projects = (await getCollection('projects'))
  .filter((p) => !p.data.hidden)
  .sort((a, b) => Number(a.data.weight ?? 99) - Number(b.data.weight ?? 99));
  const titles = projects.map((p) => p.data.title).join(', ');
  const llms = [
    '# Paul Joseph Romeo: Cybersecurity & IT',
    '',
    '> Online stores and day-to-day IT at a small family shoe and boot business.',
    '> WGU cybersecurity graduate working toward incident response and digital forensics.',
    '',
    '## Pages',
    '',
    '- [Home](https://paulromeo.net/): about, experience, certifications, skills, résumé',
    `- [Projects](https://paulromeo.net/projects/): ${titles}`,
    '- [Résumé (PDF)](https://paulromeo.net/Paul-Romeo-Resume-20261008.pdf): résumé download',
    '',
    '## Contact',
    '',
    '- Email: paul@paulromeo.net',
    '',
  ].join('\n');
  return new Response(llms, { headers: { 'Content-Type': 'text/plain; charset=utf-8' } });
};
