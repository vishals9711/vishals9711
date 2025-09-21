import { Octokit } from '@octokit/rest';
import { graphql } from '@octokit/graphql';

if (!process.env.GH_PAT_TOKEN) {
  throw new Error('GH_PAT_TOKEN environment variable is required');
}

const octokit = new Octokit({
  auth: process.env.GH_PAT_TOKEN,
});

const graphqlWithAuth = graphql.defaults({
  headers: {
    authorization: `token ${process.env.GH_PAT_TOKEN}`,
  },
});

// GitHub API response interfaces
interface GitHubUser {
  data: {
    followers: number;
    following: number;
    public_repos: number;
  };
}

interface GitHubRepo {
  name: string;
  stargazers_count?: number;
  language?: string | null;
  html_url: string;
  pushed_at: string | null;
  description: string | null;
}

interface GitHubRepoArray {
  data: GitHubRepo[];
}

interface GitHubLanguages {
  data: Record<string, number>;
}

interface GitHubRepoContent {
  data: Array<{
    name: string;
    type?: string;
    size?: number;
    path?: string;
  }>;
}

interface GitHubContributionData {
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

interface GitHubEvent {
  type: string | null;
  repo: {
    name: string;
  };
}

interface GitHubPublicEvents {
  data: GitHubEvent[];
}

export async function getUserData(username: string): Promise<GitHubUser> {
  return octokit.users.getByUsername({ username });
}

export async function listUserRepos(
  username: string
): Promise<GitHubRepoArray> {
  const result = await octokit.repos.listForUser({
    username,
    sort: 'pushed',
    per_page: 5,
  });
  return result as GitHubRepoArray;
}

export async function listAllUserRepos(
  username: string
): Promise<GitHubRepo[]> {
  const result = await octokit.paginate(octokit.repos.listForUser, {
    username,
    type: 'owner',
    sort: 'pushed',
    per_page: 100,
  });
  return result as GitHubRepo[];
}

export async function getRepoLanguages(
  owner: string,
  repo: string
): Promise<GitHubLanguages> {
  return octokit.repos.listLanguages({ owner, repo });
}

export async function getRepoContent(
  owner: string,
  repo: string
): Promise<GitHubRepoContent> {
  const result = await octokit.repos.getContent({ owner, repo, path: '' });
  return result as GitHubRepoContent;
}

export async function getContributionData(
  username: string
): Promise<GitHubContributionData> {
  const query = `
    query($username: String!) {
      user(login: $username) {
        contributionsCollection {
          totalCommitContributions
          totalRepositoriesWithContributedCommits
          contributionCalendar {
            totalContributions
            weeks {
              contributionDays {
                contributionCount
                date
              }
            }
          }
        }
      }
    }
  `;
  return graphqlWithAuth(query, { username });
}

export async function listPublicEvents(
  username: string
): Promise<GitHubPublicEvents> {
  return octokit.activity.listPublicEventsForUser({
    username,
    per_page: 100,
  });
}
