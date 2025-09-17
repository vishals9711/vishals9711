import ejs from 'ejs';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const TEMPLATE_PATH = path.join(__dirname, '../../README.template.md');
const OUTPUT_PATH = path.join(__dirname, '../../README.md');

export function generateReadme(data) {
  const template = fs.readFileSync(TEMPLATE_PATH, 'utf-8');
  const rendered = ejs.render(template, data);
  fs.writeFileSync(OUTPUT_PATH, rendered);
}
