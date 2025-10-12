import * as github from '../clients/githubClient.js';
import * as wakatime from '../clients/wakatimeClient.js';
import * as llm from '../clients/llmClient.js';
import { getConfig } from '../config/config.js';
import {
  HeaderData,
  LanguagesData,
  TechStackData,
  GithubStats,
  ProjectSpotlight,
  RecentActivity,
  WakaTimeData,
} from '../types/index.js';
import { WakaTimeLanguage } from '../types/index.js';
import { BioData, ProjectData } from '../types/index.js';
import { GitHubRepo } from '../types/index.js';
type Contributions = {
  user: {
    contributionsCollection: {
      totalCommitContributions: number;
      totalRepositoriesWithContributedCommits: number;
      contributionCalendar: {
        totalContributions: number;
        weeks: {
          contributionDays: {
            date: string;
            contributionCount: number;
          }[];
        }[];
      };
    };
  };
};

const config = getConfig();
const GITHUB_USERNAME = config.github.username;

export async function getCommonData(): Promise<{
  userRepos: GitHubRepo[];
  contributions: Contributions;
}> {
  const [userRepos, contributions] = await Promise.all([
    github.listAllUserRepos(GITHUB_USERNAME),
    github.getContributionData(GITHUB_USERNAME),
  ]);
  return { userRepos, contributions };
}

export async function getHeaderAndBio(userRepos: GitHubRepo[]): Promise<HeaderData> {
  let topLanguage = 'JavaScript';
  let totalHours = 0;
  let latestRepo = 'profile-dynamo';

  if (config.wakatime.enabled && config.wakatime.apiKey) {
    try {
      const wakatimeStats = await wakatime.getStats('last_7_days');
      const languages = wakatimeStats.languages || [];
      const totalSeconds = wakatimeStats.total_seconds || 0;
      if (languages.length > 0 && languages[0]?.name) {
        topLanguage = languages[0]?.name;
      }
      if (totalSeconds) {
        totalHours = Math.round(totalSeconds / 3600);
      }
    } catch (error) {
      console.warn('WakaTime API unavailable, using default values:', error);
    }
  } else {
    console.warn('WakaTime not configured, using default values');
  }

  if (userRepos.length > 0 && userRepos[0]?.name) {
    latestRepo = userRepos[0]?.name;
  }

  const bioData = await llm.generateBio({
    topLanguage,
    latestRepo,
    totalHours,
    username: GITHUB_USERNAME,
  } as BioData);

  return { bio: bioData.bio };
}

export async function getLanguages(
  userRepos: GitHubRepo[]
): Promise<LanguagesData> {
  const languageStats: Record<string, number> = {};

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
    } catch (error: unknown) {
      console.warn(
        `Could not fetch languages for ${repo.name}:`,
        error instanceof Error ? error.message : String(error)
      );
    }
  }

  const totalBytes = Object.values(languageStats).reduce(
    (sum, bytes) => sum + bytes,
    0
  );
  const languagePercentages: Record<string, string> = {};

  for (const [lang, bytes] of Object.entries(languageStats)) {
    languagePercentages[lang] = ((bytes / totalBytes) * 100).toFixed(2);
  }

  const sortedLanguages = Object.entries(languagePercentages)
    .sort(([, a], [, b]) => parseFloat(b) - parseFloat(a))
    .slice(0, 8)
    .reduce((obj, [key, value]) => ({ ...obj, [key]: value }), {});

  return sortedLanguages;
}

export async function getTechStack(
  languages: LanguagesData
): Promise<string[]> {
  const techStack = await llm.generateTechStack({
    languages: Object.keys(languages),
  } as TechStackData);
  return techStack.techStack;
}

export async function getGithubStats(
  userRepos: GitHubRepo[],
  contributions: Contributions
): Promise<GithubStats> {
  const userData = await github.getUserData(GITHUB_USERNAME);
  const totalStars = userRepos.reduce(
    (acc, repo) => acc + (repo.stargazers_count ?? 0),
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

export async function getProjectSpotlight(
  userRepos: GitHubRepo[]
): Promise<ProjectSpotlight> {
  const repo = userRepos[0];

  if (!repo) {
    throw new Error('No repositories found');
  }

  const repoDetails = await github.getRepoContent(GITHUB_USERNAME, repo.name);

  let description = repo.description;
  if (!description || description.trim() === '') {
    const enhancedDescription = await llm.generateProjectDescription({
      repoName: repo.name,
      language: repo.language,
      stars: repo.stargazers_count ?? 0,
      hasReadme: repoDetails.data.some((file) =>
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
    stars: repo.stargazers_count ?? 0,
    language: repo.language || 'JavaScript',
    url: repo.html_url,
  };
}

export async function getRecentActivity(
  userRepos: GitHubRepo[],
  contributions: Contributions
): Promise<RecentActivity> {
  const recentCommits =
    contributions.user.contributionsCollection.contributionCalendar.weeks
      .slice(-12)
      .flatMap((week) => week.contributionDays)
      .filter((day) => day.contributionCount > 0)
      .slice(-30)
      .map((day) => ({
        date: day.date,
        count: day.contributionCount,
      }));

  const sortedRepos = userRepos
    .filter((repo) => repo.pushed_at)
    .sort(
      (a, b) =>
        new Date(b.pushed_at || '').getTime() -
        new Date(a.pushed_at || '').getTime()
    )
    .slice(0, 5);

  return {
    totalCommits:
      contributions.user.contributionsCollection.totalCommitContributions,
    recentCommits,
    recentRepos: sortedRepos.map((repo) => ({
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
    const totalSeconds = stats.total_seconds || 0;
    const languages = stats.languages || [];

    return {
      totalHours: Math.round(totalSeconds / 3600),
      topLanguage:
        languages.length > 0
          ? languages[0]?.name || 'JavaScript'
          : 'JavaScript',
      languages: languages.slice(0, 6).map((lang: WakaTimeLanguage) => ({
        name: lang.name || 'JavaScript',
        percent: Math.round(lang.percent || 0),
        hours: Math.round((lang.total_seconds || 0) / 3600),
        total_seconds: lang.total_seconds,
        digital: lang.digital,
        decimal: lang.decimal,
        text: lang.text,
        minutes: lang.minutes,
      })),
    };
  } catch (error) {
    console.warn('Failed to fetch WakaTime data:', error);
    return null;
  }
}
