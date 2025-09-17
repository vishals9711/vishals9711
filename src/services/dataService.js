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

export async function getDynamicStats() {
  const [contributionData, userData, wakatimeStats] = await Promise.all([
    github.getContributionData(GITHUB_USERNAME),
    github.getUserData(GITHUB_USERNAME),
    wakatime.getStats('all_time'),
  ]);

  return {
    contributions: contributionData.user.contributionsCollection.contributionCalendar.totalContributions,
    repos: userData.data.public_repos,
    followers: userData.data.followers,
    codedHours: wakatimeStats.data.data.total_seconds / 3600,
  };
}

export async function getTechArsenal() {
  const userRepos = await github.listUserRepos(GITHUB_USERNAME);
  const languageStats = {};
  const repoLanguages = [];

  // Collect language data from recent repositories
  for (const repo of userRepos.data) {
    try {
      const languages = await github.getRepoLanguages(GITHUB_USERNAME, repo.name);
      const repoLangData = {
        repo: repo.name,
        languages: languages.data
      };
      repoLanguages.push(repoLangData);

      // Aggregate language statistics
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

  // Sort languages by usage
  const sortedLanguages = Object.entries(languageStats)
    .sort(([,a], [,b]) => b - a)
    .slice(0, 10) // Top 10 languages
    .map(([lang]) => lang);

  // Use LLM to enhance and categorize the tech stack
  const enhancedTechStack = await llm.generateTechStack({
    languages: sortedLanguages,
    repoLanguages: repoLanguages.slice(0, 5), // Recent 5 repos
    totalRepos: userRepos.data.length
  });

  return enhancedTechStack.techStack || sortedLanguages;
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

export async function getAchievements() {
  const [publicEvents, wakatimeStats, contributionData] = await Promise.all([
    github.listPublicEvents(GITHUB_USERNAME),
    wakatime.getStats('last_30_days'),
    github.getContributionData(GITHUB_USERNAME),
  ]);

  const achievements = {
    nightOwl: false,
    polyglot: false,
    onFire: false,
    ossChampion: false,
  };

  // Night Owl Logic
  const pushEvents = publicEvents.data.filter(e => e.type === 'PushEvent');
  const nightCommits = pushEvents.filter(e => {
    const hour = new Date(e.created_at).getUTCHours();
    return hour >= 0 && hour <= 5;
  });
  if (pushEvents.length > 0 && (nightCommits.length / pushEvents.length) > 0.3) {
    achievements.nightOwl = true;
  }

  // Polyglot Logic
  if (wakatimeStats.data.data.languages.length >= 4) {
    achievements.polyglot = true;
  }

  // On Fire Logic
  const weeks = contributionData.user.contributionsCollection.contributionCalendar.weeks;
  const last7Days = weeks.flatMap(w => w.contributionDays).slice(-7);
  if (last7Days.every(d => d.contributionCount > 0)) {
    achievements.onFire = true;
  }
  
  // OSS Champion Logic
  const mergedPRs = publicEvents.data.filter(e => 
    e.type === 'PullRequestEvent' && 
    e.payload.action === 'closed' && 
    e.payload.pull_request.merged &&
    e.repo.name.split('/')[0] !== GITHUB_USERNAME
  );
  if (mergedPRs.length > 0) {
    achievements.ossChampion = true;
  }

  return achievements;
}
