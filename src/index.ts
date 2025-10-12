import 'dotenv/config';
import * as dataService from './services/dataService.js';
import * as templateService from './services/templateService.js';
import { ProfileData } from './types/index.js';

async function main(): Promise<void> {
  try {
    console.log('Fetching common data...');
    const { userRepos, contributions } = await dataService.getCommonData();

    console.log('Fetching remaining data...');
    const languages = await dataService.getLanguages(userRepos);

    const [header, stats, spotlight, techStack, recentActivity, wakatimeData] =
      await Promise.all([
        dataService.getHeaderAndBio(userRepos),
        dataService.getGithubStats(userRepos, contributions),
        dataService.getProjectSpotlight(userRepos),
        dataService.getTechStack(languages),
        dataService.getRecentActivity(userRepos, contributions),
        dataService.getWakaTimeData(),
      ]);

    const data: ProfileData = {
      header,
      stats,
      languages,
      spotlight,
      techStack,
      recentActivity,
      wakatimeData,
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
