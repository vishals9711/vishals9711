import 'dotenv/config';
import * as dataService from './services/dataService';
import * as templateService from './services/templateService';
import { ProfileData } from './types';

async function main(): Promise<void> {
  try {
    console.log('Fetching data...');
    const [
      header,
      stats,
      languages,
      spotlight,
      techStack,
      recentActivity,
      wakatimeData,
    ] = await Promise.all([
      dataService.getHeaderAndBio(),
      dataService.getGithubStats(),
      dataService.getLanguages(),
      dataService.getProjectSpotlight(),
      dataService.getTechStack(),
      dataService.getRecentActivity(),
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
