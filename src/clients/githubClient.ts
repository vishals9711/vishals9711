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

// Using any types for GitHub API responses due to complex and variable structures
// interface UserData { data: any }
// interface RepoData { data: any[] }
// interface SearchData { data: { total_count: number } }
// interface ContributionData { user: any }

export async function getUserData(username: string): Promise<any> {
  return octokit.users.getByUsername({ username });
}

export async function listUserRepos(username: string): Promise<any> {
  return octokit.repos.listForUser({
    username,
    sort: 'pushed',
    per_page: 5,
  });
}

export async function listAllUserRepos(username: string): Promise<any[]> {
  return octokit.paginate(octokit.repos.listForUser, {
    username,
    type: 'owner',
    sort: 'pushed',
    per_page: 100,
  });
}

export async function getRepoLanguages(
  owner: string,
  repo: string
): Promise<any> {
  return octokit.repos.listLanguages({ owner, repo });
}

export async function getRepoContent(
  owner: string,
  repo: string
): Promise<any> {
  return octokit.repos.getContent({ owner, repo, path: '' });
}

export async function getContributionData(username: string): Promise<any> {
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

export async function listPublicEvents(username: string): Promise<any> {
  return octokit.activity.listPublicEventsForUser({
    username,
    per_page: 100,
  });
}
