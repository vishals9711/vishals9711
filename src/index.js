import 'dotenv/config';
import * as dataService from './services/dataService.js';
import * as templateService from './services/templateService.js';

async function main() {
  try {
    console.log('Fetching data...');
    const [header, stats, tech, spotlight, achievements] = await Promise.all([
      dataService.getHeaderAndBio(),
      dataService.getDynamicStats(),
      dataService.getTechArsenal(),
      dataService.getProjectSpotlight(),
      dataService.getAchievements(),
    ]);

    const data = {
      header,
      stats,
      tech,
      spotlight,
      achievements,
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
