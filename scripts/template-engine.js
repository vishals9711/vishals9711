import fs from 'fs/promises';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

class TemplateEngine {
  constructor(templatePath = "README.template.md") {
    this.templatePath = path.resolve(__dirname, '..', templatePath); // Resolve relative to project root
  }

  async loadTemplate() {
    try {
      const templateContent = await fs.readFile(this.templatePath, 'utf-8');
      console.log(`Successfully loaded template from ${this.templatePath}`);
      return templateContent;
    } catch (error) {
      console.error(`Error loading template file ${this.templatePath}:`, error);
      throw error;
    }
  }

  async populateTemplate(template, data) {
    if (!template) {
      console.warn("Empty template provided");
      return "";
    }

    if (!data) {
      console.warn("No data provided for template population");
      return template;
    }

    let populatedContent = template;
    let replacedCount = 0;

    for (const placeholder in data) {
      let value = data[placeholder];
      // If the value is a promise, await its resolution
      if (value instanceof Promise) {
        try {
          value = await value;
        } catch (error) {
          console.error(`Error resolving promise for placeholder {${placeholder}}:`, error);
          value = `Error: Failed to load ${placeholder}`; // Fallback for failed promises
        }
      }

      const placeholderPattern = new RegExp(`{${placeholder}}`, 'g');
      if (populatedContent.match(placeholderPattern)) {
        populatedContent = populatedContent.replace(placeholderPattern, String(value));
        replacedCount++;
        // console.debug(`Replaced placeholder {${placeholder}}`);
      }
    }

    // Check for any remaining unreplaced placeholders
    const remainingPlaceholders = populatedContent.match(/\{([^}]+)\}/g);
    if (remainingPlaceholders && remainingPlaceholders.length > 0) {
      console.warn(`Unreplaced placeholders found: ${remainingPlaceholders.join(", ")}`);
    }

    console.log(`Template population completed. Replaced ${replacedCount} placeholders`);
    return populatedContent;
  }

  async saveReadme(content, outputPath = "README.md") {
    if (!content) {
      console.warn("Empty content provided for README generation");
      return;
    }

    try {
      // Create backup of existing README if it exists
      const backupPath = `${outputPath}.backup`;
      try {
        const existingContent = await fs.readFile(outputPath, 'utf-8');
        await fs.writeFile(backupPath, existingContent, 'utf-8');
        console.log(`Created backup at ${backupPath}`);
      } catch (error) {
        if (error.code !== 'ENOENT') { // Ignore if file doesn't exist for backup
          console.warn(`Could not create backup: ${error.message}`);
        }
      }

      // Write the new README content
      await fs.writeFile(outputPath, content, 'utf-8');
      console.log(`Successfully saved README to ${outputPath}`);
    } catch (error) {
      console.error(`Error writing README file ${outputPath}:`, error);
      throw error;
    }
  }

  async processTemplate(data, outputFileName = "README.md") {
    try {
      // Resolve the output path relative to the project root
      const projectRoot = path.resolve(__dirname, '..');
      const outputPath = path.join(projectRoot, outputFileName);

      // Load template
      const templateContent = await this.loadTemplate();

      // Populate with data
      const populatedContent = await this.populateTemplate(templateContent, data);

      // Save final README
      await this.saveReadme(populatedContent, outputPath);

      console.log("Template processing completed successfully");
    } catch (error) {
      console.error(`Template processing failed: ${error.message}`);
      throw error;
    }
  }
}

export default TemplateEngine;
