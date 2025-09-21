import ejs from 'ejs';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { ProfileData } from '../types';
import { getConfig } from '../config/config';
import { generateTechBadge } from '../utils/badgeGenerator.js';

interface TemplateData extends ProfileData {
  config: {
    github: {
      username: string;
    };
    social: {
      linkedin?: string;
      github?: string;
      twitter?: string;
      website?: string;
    };
  };
  generateTechBadge: (techName: string) => string;
}

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const config = getConfig();

const TEMPLATE_PATH = path.resolve(config.output.templatePath);
const OUTPUT_PATH = path.resolve(config.output.readmePath);

export function generateReadme(data: ProfileData): void {
  const template = fs.readFileSync(TEMPLATE_PATH, 'utf-8');
  const templateData: TemplateData = {
    ...data,
    config: {
      github: {
        username: config.github.username,
      },
      social: config.social,
    },
    generateTechBadge,
  };
  const rendered = ejs.render(template, templateData);
  fs.writeFileSync(OUTPUT_PATH, rendered);
}
