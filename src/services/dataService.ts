import * as github from '../clients/githubClient.js';
import * as wakatime from '../clients/wakatimeClient.js';
import * as llm from '../clients/llmClient.js';
import { getConfig } from '../config/config.js';

const config = getConfig();
const GITHUB_USERNAME = config.github.username;

interface BioData {
  topLanguage: string;
  latestRepo: string;
  totalHours: number;
  username: string;
}

interface HeaderData {
  bio: string;
}

export async function getHeaderAndBio(): Promise<HeaderData> {
  const userReposPromise = github.listUserRepos(GITHUB_USERNAME);

  let topLanguage = 'JavaScript'; // Default fallback
  let totalHours = 0;
  let latestRepo = 'profile-dynamo'; // Default fallback

  // Get WakaTime data if available
  if (config.wakatime.enabled && config.wakatime.apiKey) {
    try {
      const wakatimeStats = await wakatime.getStats('last_7_days');
      if (wakatimeStats?.data?.languages?.length > 0) {
        topLanguage = wakatimeStats.data.languages[0].name || topLanguage;
      }
      if (wakatimeStats?.data?.total_seconds) {
        totalHours = Math.round(wakatimeStats.data.total_seconds / 3600);
      }
    } catch (error) {
      console.warn('WakaTime API unavailable, using default values:', error);
    }
  } else {
    console.log('WakaTime not configured, using default values');
  }

  // Get latest repository
  try {
    const userRepos = await userReposPromise;
    latestRepo = userRepos.data[0]?.name || latestRepo;
  } catch (error) {
    console.warn('Could not fetch user repos:', error);
  }

  const bioData = await llm.generateBio({
    topLanguage,
    latestRepo,
    totalHours,
    username: GITHUB_USERNAME,
  } as BioData);

  return { bio: bioData.bio };
}

interface LanguagesData {
  [language: string]: string; // language -> percentage
}

export async function getLanguages(): Promise<LanguagesData> {
  const userRepos = await github.listAllUserRepos(GITHUB_USERNAME);
  const languageStats: Record<string, number> = {};

  // Collect language data from all repositories
  for (const repo of userRepos) {
    try {
      const languages = await github.getRepoLanguages(
        GITHUB_USERNAME,
        repo.name
      );
      Object.entries(languages.data).forEach(([lang, bytes]) => {
        if (languageStats[lang]) {
          languageStats[lang] += bytes as number;
        } else {
          languageStats[lang] = bytes as number;
        }
      });
    } catch (error: any) {
      console.warn(
        `Could not fetch languages for ${repo.name}:`,
        error.message
      );
    }
  }

  // Calculate percentages
  const totalBytes = Object.values(languageStats).reduce(
    (sum, bytes) => sum + bytes,
    0
  );
  const languagePercentages: Record<string, string> = {};

  for (const [lang, bytes] of Object.entries(languageStats)) {
    languagePercentages[lang] = ((bytes / totalBytes) * 100).toFixed(2);
  }

  // Sort languages by usage
  const sortedLanguages = Object.entries(languagePercentages)
    .sort(([, a], [, b]) => parseFloat(b) - parseFloat(a))
    .slice(0, 8) // Top 8 languages
    .reduce((obj, [key, value]) => ({ ...obj, [key]: value }), {});

  return sortedLanguages;
}

interface TechStackData {
  languages: string[];
}

interface GithubStats {
  stars: number;
  commits: number;
  contributedTo: number;
  followers?: number;
  following?: number;
  publicRepos?: number;
  totalContributions?: number;
}

export async function getTechStack(): Promise<string[]> {
  const languages = await getLanguages();
  const techStack = await llm.generateTechStack({
    languages: Object.keys(languages),
  } as TechStackData);
  return techStack.techStack;
}

export async function getGithubStats(): Promise<GithubStats> {
  // Following Octokit best practices: use simple, reliable endpoints
  const [userData, userRepos, contributions] = await Promise.all([
    github.getUserData(GITHUB_USERNAME),
    github.listAllUserRepos(GITHUB_USERNAME),
    github.getContributionData(GITHUB_USERNAME),
  ]);

  const totalStars = userRepos.reduce(
    (acc, repo) => acc + repo.stargazers_count,
    0
  );

  return {
    stars: totalStars,
    commits:
      contributions.user.contributionsCollection.totalCommitContributions,
    contributedTo:
      contributions.user.contributionsCollection
        .totalRepositoriesWithContributedCommits,
    followers: userData.data.followers,
    following: userData.data.following,
    publicRepos: userData.data.public_repos,
    totalContributions:
      contributions.user.contributionsCollection.contributionCalendar
        .totalContributions,
  };
}

interface ProjectData {
  repoName: string;
  language: string;
  stars: number;
  hasReadme: boolean;
  fileCount: number;
}

interface ProjectSpotlight {
  name: string;
  description: string;
  stars: number;
  language: string;
  url: string;
}

interface RecentActivity {
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
}

interface WakaTimeData {
  totalHours: number;
  topLanguage: string;
  languages: Array<{
    name: string;
    percent: number;
    hours: number;
  }>;
}

export async function getProjectSpotlight(): Promise<ProjectSpotlight> {
  const userRepos = await github.listUserRepos(GITHUB_USERNAME);
  const repo = userRepos.data[0];

  if (!repo) {
    throw new Error('No repositories found');
  }

  // Get additional repo details
  const repoDetails = await github.getRepoContent(GITHUB_USERNAME, repo.name);

  // Use LLM to generate an engaging description if the repo description is empty
  let description = repo.description;
  if (!description || description.trim() === '') {
    const enhancedDescription = await llm.generateProjectDescription({
      repoName: repo.name,
      language: repo.language,
      stars: repo.stargazers_count,
      hasReadme: repoDetails.data.some((file: any) =>
        file.name.toLowerCase().includes('readme')
      ),
      fileCount: repoDetails.data.length,
    } as ProjectData);
    description = enhancedDescription.description;
  }

  return {
    name: repo.name,
    description:
      description ||
      'An amazing project showcasing modern development practices.',
    stars: repo.stargazers_count,
    language: repo.language || 'JavaScript',
    url: repo.html_url,
  };
}

export async function getRecentActivity(): Promise<RecentActivity> {
  const contributions = await github.getContributionData(GITHUB_USERNAME);

  const recentCommits =
    contributions.user.contributionsCollection.contributionCalendar.weeks
      .slice(-12) // Last 12 weeks
      .flatMap((week: any) => week.contributionDays)
      .filter((day: any) => day.contributionCount > 0)
      .slice(-30) // Last 30 contributions
      .map((day: any) => ({
        date: day.date,
        count: day.contributionCount,
      }));

  const recentRepos = await github.listUserRepos(GITHUB_USERNAME);
  const sortedRepos = recentRepos.data
    .filter((repo: any) => repo.pushed_at) // Only include repos with pushed_at
    .sort(
      (a: any, b: any) =>
        new Date(b.pushed_at || '').getTime() -
        new Date(a.pushed_at || '').getTime()
    )
    .slice(0, 5);

  return {
    totalCommits:
      contributions.user.contributionsCollection.totalCommitContributions,
    recentCommits,
    recentRepos: sortedRepos.map((repo: any) => ({
      name: repo.name,
      pushed_at: repo.pushed_at || '',
      language: repo.language || 'Multiple Languages',
    })),
  };
}

export async function getWakaTimeData(): Promise<WakaTimeData | null> {
  if (!config.wakatime.enabled || !config.wakatime.apiKey) {
    return null;
  }

  try {
    const stats = await wakatime.getStats('last_7_days');

    // Debug the WakaTime response structure (safely)
    console.log('WakaTime response:', JSON.stringify(stats?.data, null, 2));

    // Handle different possible response structures
    if (!stats?.data) {
      console.warn('WakaTime response missing data property');
      return null;
    }

    const totalSeconds = stats.data.total_seconds || 0;
    const languages = stats.data.languages || [];

    return {
      totalHours: Math.round(totalSeconds / 3600),
      topLanguage: languages.length > 0 ? languages[0].name : 'JavaScript',
      languages: languages.slice(0, 6).map((lang: any) => ({
        name: lang.name,
        percent: Math.round(lang.percent || 0),
        hours: Math.round((lang.total_seconds || 0) / 3600),
      })),
    };
  } catch (error) {
    console.warn('Failed to fetch WakaTime data:', error);
    return null;
  }
}
