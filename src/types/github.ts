// GitHub API response interfaces
export interface GitHubUser {
  data: {
    followers: number;
    following: number;
    public_repos: number;
  };
}

export interface GitHubRepo {
  name: string;
  stargazers_count?: number;
  language?: string | null;
  html_url: string;
  pushed_at: string | null;
  description: string | null;
}

export interface GitHubRepoArray {
  data: GitHubRepo[];
}

export interface GitHubLanguages {
  data: Record<string, number>;
}

export interface GitHubRepoContent {
  data: Array<{
    name: string;
    type?: string;
    size?: number;
    path?: string;
  }>;
}

export interface GitHubContributionData {
  user: {
    contributionsCollection: {
      totalCommitContributions: number;
      totalRepositoriesWithContributedCommits: number;
      contributionCalendar: {
        totalContributions: number;
        weeks: Array<{
          contributionDays: Array<{
            contributionCount: number;
            date: string;
          }>;
        }>;
      };
    };
  };
}

export interface GitHubEvent {
  type: string | null;
  repo: {
    name: string;
  };
}

export interface GitHubPublicEvents {
  data: GitHubEvent[];
}
