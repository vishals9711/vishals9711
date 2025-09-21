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
export function generateReadme(data) {
    const template = fs.readFileSync(TEMPLATE_PATH, 'utf-8');
    const rendered = ejs.render(template, data);
    fs.writeFileSync(OUTPUT_PATH, rendered);
}
//# sourceMappingURL=templateService.js.map