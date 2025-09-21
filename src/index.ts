import 'dotenv/config';
import * as dataService from './services/dataService.js';
import * as templateService from './services/templateService.js';

interface ProfileData {
  header: {
    bio: string;
  };
  stats: {
    stars: number;
    commits: number;
    prs: number;
    issues: number;
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
      wakatimeData
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
