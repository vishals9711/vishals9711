import * as github from '../clients/githubClient.js';
import * as wakatime from '../clients/wakatimeClient.js';
import * as llm from '../clients/llmClient.js';

const GITHUB_USERNAME = 'vishals9711';

export async function getHeaderAndBio() {
  const [wakatimeStats, userRepos] = await Promise.all([
    wakatime.getStats('last_7_days'),
    github.listUserRepos(GITHUB_USERNAME),
  ]);

  const topLanguage = wakatimeStats.data.data.languages[0].name;
  const latestRepo = userRepos.data[0].name;
  const totalHours = Math.round(wakatimeStats.data.data.total_seconds / 3600);

  const bioData = await llm.generateBio({ 
    topLanguage, 
    latestRepo, 
    totalHours,
    username: GITHUB_USERNAME 
  });
  return { bio: bioData.bio };
}

export async function getLanguages() {
  const userRepos = await github.listAllUserRepos(GITHUB_USERNAME);
  const languageStats = {};

  // Collect language data from all repositories
  for (const repo of userRepos) {
    try {
      const languages = await github.getRepoLanguages(GITHUB_USERNAME, repo.name);
      Object.entries(languages.data).forEach(([lang, bytes]) => {
        if (languageStats[lang]) {
          languageStats[lang] += bytes;
        } else {
          languageStats[lang] = bytes;
        }
      });
    } catch (error) {
      console.warn(`Could not fetch languages for ${repo.name}:`, error.message);
    }
  }

  // Calculate percentages
  const totalBytes = Object.values(languageStats).reduce((sum, bytes) => sum + bytes, 0);
  const languagePercentages = {};
  for (const [lang, bytes] of Object.entries(languageStats)) {
    languagePercentages[lang] = ((bytes / totalBytes) * 100).toFixed(2);
  }

  // Sort languages by usage
  const sortedLanguages = Object.entries(languagePercentages)
    .sort(([,a], [,b]) => b - a)
    .slice(0, 8) // Top 8 languages
    .reduce((obj, [key, value]) => ({ ...obj, [key]: value }), {});

  return sortedLanguages;
}

export async function getGithubStats() {
  const [userRepos, issues, pullRequests, contributions] = await Promise.all([
    github.listAllUserRepos(GITHUB_USERNAME),
    github.getSearchData(`is:issue author:${GITHUB_USERNAME}`),
    github.getSearchData(`is:pr author:${GITHUB_USERNAME}`),
    github.getContributionData(GITHUB_USERNAME)
  ]);

  const totalStars = userRepos.reduce((acc, repo) => acc + repo.stargazers_count, 0);

  return {
    stars: totalStars,
    issues: issues.data.total_count,
    prs: pullRequests.data.total_count,
    commits: contributions.user.contributionsCollection.totalCommitContributions,
    contributedTo: contributions.user.contributionsCollection.totalRepositoriesWithContributedCommits,
  };
}

export async function getProjectSpotlight() {
  const userRepos = await github.listUserRepos(GITHUB_USERNAME);
  const repo = userRepos.data[0];

  // Get additional repo details
  const repoDetails = await github.getRepoContent(GITHUB_USERNAME, repo.name);
  
  // Use LLM to generate an engaging description if the repo description is empty
  let description = repo.description;
  if (!description || description.trim() === '') {
    const enhancedDescription = await llm.generateProjectDescription({
      repoName: repo.name,
      language: repo.language,
      stars: repo.stargazers_count,
      hasReadme: repoDetails.data.some(file => file.name.toLowerCase().includes('readme')),
      fileCount: repoDetails.data.length
    });
    description = enhancedDescription.description;
  }

  return {
    name: repo.name,
    description: description,
    stars: repo.stargazers_count,
    language: repo.language,
    url: repo.html_url
  };
}
