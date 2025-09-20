import 'dotenv/config';
import * as dataService from './services/dataService.js';
import * as templateService from './services/templateService.js';

async function main() {
  try {
    console.log('Fetching data...');
    const [header, stats, languages, spotlight, techStack] = await Promise.all([
      dataService.getHeaderAndBio(),
      dataService.getGithubStats(),
      dataService.getLanguages(),
      dataService.getProjectSpotlight(),
      dataService.getTechStack(),
    ]);

    const data = {
      header,
      stats,
      languages,
      spotlight,
      techStack,
    };

    console.log('Generating README...');
    templateService.generateReadme(data);
    console.log('README generated successfully!');

  } catch (error) {
    console.error('Error updating profile:', error);
    process.exit(1);
  }
}

main();
