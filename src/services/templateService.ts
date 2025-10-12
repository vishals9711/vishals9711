import ejs from 'ejs';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { ProfileData } from '../types/index.js';
import { getConfig } from '../config/config.js';
import {
  generateTechBadge,
  generatePercentageBadge,
} from '../utils/badgeGenerator.js';

import { Config } from '../config/config.js';

interface TemplateData extends ProfileData {
  config: Config;
  generateTechBadge: (techName: string) => string;
  generatePercentageBadge: (language: string, percentage: string) => string;
}

const config = getConfig();

const TEMPLATE_PATH = path.resolve(config.output.templatePath);
const OUTPUT_PATH = path.resolve(config.output.readmePath);

export function generateReadme(data: ProfileData): void {
  const template = fs.readFileSync(TEMPLATE_PATH, 'utf-8');
  const templateData: TemplateData = {
    ...data,
    config,
    generateTechBadge,
    generatePercentageBadge,
  };
  const rendered = ejs.render(template, templateData);
  fs.writeFileSync(OUTPUT_PATH, rendered);
}
