import { defineCollection, z } from 'astro:content';
import { glob } from 'astro/loaders';

const projects = defineCollection({
  loader: glob({ pattern: '*.md', base: './src/content/projects' }),
  schema: z.object({
    title: z.string(),
    tag: z.string().optional(),
    link: z.string().optional(),
    site: z.string().optional(),
    weight: z.union([z.string(), z.number()]).optional(),
    hidden: z.boolean().optional(),
  }),
});

export const collections = { projects };
