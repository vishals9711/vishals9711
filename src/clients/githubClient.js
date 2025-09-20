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

export async function getUserData(username) {
  return octokit.users.getByUsername({ username });
}

export async function listUserRepos(username) {
  return octokit.repos.listForUser({
    username,
    sort: 'pushed',
    per_page: 5,
  });
}

export async function listAllUserRepos(username) {
  return octokit.paginate(octokit.repos.listForUser, {
    username,
    type: 'owner',
    sort: 'pushed',
    per_page: 100,
  });
}

export async function getSearchData(query) {
  return octokit.search.issuesAndPullRequests({
    q: query,
  });
}

export async function getRepoLanguages(owner, repo) {
  return octokit.repos.listLanguages({ owner, repo });
}

export async function getRepoContent(owner, repo) {
  return octokit.repos.getContent({ owner, repo, path: '' });
}

export async function getContributionData(username) {
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

export async function listPublicEvents(username) {
  return octokit.activity.listPublicEventsForUser({
    username,
    per_page: 100,
  });
}
