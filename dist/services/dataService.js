import * as github from '../clients/githubClient.js';
import * as wakatime from '../clients/wakatimeClient.js';
import * as llm from '../clients/llmClient.js';
import { getConfig } from '../config/config.js';
const config = getConfig();
const GITHUB_USERNAME = config.github.username;
export async function getHeaderAndBio() {
    const userReposPromise = github.listUserRepos(GITHUB_USERNAME);
    let topLanguage = 'JavaScript';
    let totalHours = 0;
    let latestRepo = 'profile-dynamo';
    if (config.wakatime.enabled && config.wakatime.apiKey) {
        try {
            const wakatimeStats = await wakatime.getStats('last_7_days');
            topLanguage = wakatimeStats.data.languages[0]?.name || topLanguage;
            totalHours = Math.round(wakatimeStats.data.total_seconds / 3600);
        }
        catch (error) {
            console.warn('WakaTime API unavailable, using default values:', error);
        }
    }
    else {
        console.log('WakaTime not configured, using default values');
    }
    try {
        const userRepos = await userReposPromise;
        latestRepo = userRepos.data[0]?.name || latestRepo;
    }
    catch (error) {
        console.warn('Could not fetch user repos:', error);
    }
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
    for (const repo of userRepos) {
        try {
            const languages = await github.getRepoLanguages(GITHUB_USERNAME, repo.name);
            Object.entries(languages.data).forEach(([lang, bytes]) => {
                if (languageStats[lang]) {
                    languageStats[lang] += bytes;
                }
                else {
                    languageStats[lang] = bytes;
                }
            });
        }
        catch (error) {
            console.warn(`Could not fetch languages for ${repo.name}:`, error.message);
        }
    }
    const totalBytes = Object.values(languageStats).reduce((sum, bytes) => sum + bytes, 0);
    const languagePercentages = {};
    for (const [lang, bytes] of Object.entries(languageStats)) {
        languagePercentages[lang] = ((bytes / totalBytes) * 100).toFixed(2);
    }
    const sortedLanguages = Object.entries(languagePercentages)
        .sort(([, a], [, b]) => parseFloat(b) - parseFloat(a))
        .slice(0, 8)
        .reduce((obj, [key, value]) => ({ ...obj, [key]: value }), {});
    return sortedLanguages;
}
export async function getTechStack() {
    const languages = await getLanguages();
    const techStack = await llm.generateTechStack({
        languages: Object.keys(languages),
    });
    return techStack.techStack;
}
export async function getGithubStats() {
    const [userData, userRepos, issues, pullRequests, contributions] = await Promise.all([
        github.getUserData(GITHUB_USERNAME),
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
        followers: userData.data.followers,
        following: userData.data.following,
        publicRepos: userData.data.public_repos,
        totalContributions: contributions.user.contributionsCollection.contributionCalendar.totalContributions,
    };
}
export async function getProjectSpotlight() {
    const userRepos = await github.listUserRepos(GITHUB_USERNAME);
    const repo = userRepos.data[0];
    if (!repo) {
        throw new Error('No repositories found');
    }
    const repoDetails = await github.getRepoContent(GITHUB_USERNAME, repo.name);
    let description = repo.description;
    if (!description || description.trim() === '') {
        const enhancedDescription = await llm.generateProjectDescription({
            repoName: repo.name,
            language: repo.language,
            stars: repo.stargazers_count,
            hasReadme: repoDetails.data.some((file) => file.name.toLowerCase().includes('readme')),
            fileCount: repoDetails.data.length
        });
        description = enhancedDescription.description;
    }
    return {
        name: repo.name,
        description: description || 'An amazing project showcasing modern development practices.',
        stars: repo.stargazers_count,
        language: repo.language || 'JavaScript',
        url: repo.html_url
    };
}
export async function getRecentActivity() {
    const contributions = await github.getContributionData(GITHUB_USERNAME);
    const recentCommits = contributions.user.contributionsCollection.contributionCalendar.weeks
        .slice(-12)
        .flatMap((week) => week.contributionDays)
        .filter((day) => day.contributionCount > 0)
        .slice(-30)
        .map((day) => ({
        date: day.date,
        count: day.contributionCount
    }));
    const recentRepos = await github.listUserRepos(GITHUB_USERNAME);
    const sortedRepos = recentRepos.data
        .filter((repo) => repo.pushed_at)
        .sort((a, b) => new Date(b.pushed_at || '').getTime() - new Date(a.pushed_at || '').getTime())
        .slice(0, 5);
    return {
        totalCommits: contributions.user.contributionsCollection.totalCommitContributions,
        recentCommits,
        recentRepos: sortedRepos.map((repo) => ({
            name: repo.name,
            pushed_at: repo.pushed_at || '',
            language: repo.language || 'Multiple Languages'
        }))
    };
}
export async function getWakaTimeData() {
    if (!config.wakatime.enabled || !config.wakatime.apiKey) {
        return null;
    }
    try {
        const stats = await wakatime.getStats('last_7_days');
        return {
            totalHours: Math.round(stats.data.total_seconds / 3600),
            topLanguage: stats.data.languages[0]?.name || 'JavaScript',
            languages: stats.data.languages.slice(0, 6).map((lang) => ({
                name: lang.name,
                percent: Math.round(lang.percent),
                hours: Math.round(lang.total_seconds / 3600)
            }))
        };
    }
    catch (error) {
        console.warn('Failed to fetch WakaTime data:', error);
        return null;
    }
}
//# sourceMappingURL=dataService.js.map