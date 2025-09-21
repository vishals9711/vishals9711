import ejs from 'ejs';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { getConfig } from '../config/config.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const config = getConfig();

const TEMPLATE_PATH = path.resolve(config.output.templatePath);
const OUTPUT_PATH = path.resolve(config.output.readmePath);

interface ProfileData {
  header: {
    bio: string;
  };
  stats: {
    stars: number;
    commits: number;
    contributedTo: number;
    followers?: number;
    following?: number;
    publicRepos?: number;
    totalContributions?: number;
  };
  languages: Record<string, string>;
  spotlight: {
    name: string;
    description: string;
    stars: number;
    language: string;
    url: string;
  };
  techStack: string[];
  recentActivity: {
    totalCommits: number;
    recentCommits: Array<{
      date: string;
      count: number;
    }>;
    recentRepos: Array<{
      name: string;
      pushed_at: string;
      language: string;
    }>;
  };
  wakatimeData: {
    totalHours: number;
    topLanguage: string;
    languages: Array<{
      name: string;
      percent: number;
      hours: number;
    }>;
  } | null;
}

export function generateReadme(data: ProfileData): void {
  const template = fs.readFileSync(TEMPLATE_PATH, 'utf-8');
  const rendered = ejs.render(template, data);
  fs.writeFileSync(OUTPUT_PATH, rendered);
}
