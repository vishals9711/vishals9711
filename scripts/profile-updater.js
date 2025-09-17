import GitHubClient from './github-client.js';
import WakatimeClient from './wakatime-client.js';
import DataProcessor from './data-processor.js';
import TemplateEngine from './template-engine.js';
import LlmClient from './llm-client.js';
import fs from 'fs/promises';
import path from 'path';
import { fileURLToPath } from 'url';
import 'dotenv/config';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

class ProfileUpdater {
  constructor(githubToken, wakatimeKey, llmApiKey) {
    this.githubClient = new GitHubClient(githubToken);
    this.wakatimeClient = new WakatimeClient(wakatimeKey);
    this.llmClient = new LlmClient(llmApiKey); // Instantiate LlmClient
    this.dataProcessor = new DataProcessor(this.llmClient); // Pass llmClient to DataProcessor
    this.templateEngine = new TemplateEngine(); // Instantiate TemplateEngine
  }

  async run() {
    console.log("🚀 Starting Profile Dynamo update process...");
    console.log("=".repeat(100));

    try {
      // Step 1: Fetch all data from APIs
      console.log("Fetching data from APIs...");
      const rawData = await this._fetchAllData();

      // Step 2: Process raw data into formatted content
      console.log("Processing data...");
      const processedData = await this._processData(rawData);

      // Step 3: Generate the final README
      console.log("Generating README...");
      await this._generateReadme(processedData, 'README.md');

      console.log("✅ Profile update process completed successfully!");
    } catch (error) {
      console.error(`❌ Profile update failed: ${error.message}`);
      process.exit(1);
    }
  }

  async _fetchAllData() {
    const rawData = {
      github_stats: null,
      github_recent_repos: null, // Changed from github_pinned
      github_languages: null,
      wakatime_stats: null,
    };

    // Fetch GitHub profile statistics
    try {
      console.log("Fetching GitHub profile statistics...");
      rawData.github_stats = await this.githubClient.fetchProfileStats();
      console.log("GitHub profile statistics fetched successfully");
    } catch (error) {
      console.error(`Failed to fetch GitHub profile stats: ${error.message}`);
    }

    // Fetch GitHub recent repositories (changed from pinned)
    try {
      console.log("Fetching GitHub recent repositories...");
      rawData.github_recent_repos = await this.githubClient.fetchRecentRepositories();
      console.log("GitHub recent repositories fetched successfully");
    } catch (error) {
      console.error(`Failed to fetch GitHub recent repositories: ${error.message}`);
    }

    // Fetch GitHub language statistics
    try {
      console.log("Fetching GitHub language statistics...");
      rawData.github_languages = await this.githubClient.fetchLanguageStats();
      console.log("GitHub language statistics fetched successfully");
    } catch (error) {
      console.error(`Failed to fetch GitHub language stats: ${error.message}`);
    }

    // Fetch Wakatime coding statistics
    try {
      console.log("Fetching Wakatime coding statistics...");
      rawData.wakatime_stats = await this.wakatimeClient.fetchCodingStats();
      console.log("Wakatime coding statistics fetched successfully");
    } catch (error) {
      console.error(`Failed to fetch Wakatime stats: ${error.message}`);
    }

    return rawData;
  }

  async _processData(rawData) {
    const processedContent = {};

    // Process GitHub data
    const githubStats = rawData.github_stats;
    const githubRecentRepos = rawData.github_recent_repos; // Changed from github_pinned
    const githubLanguages = rawData.github_languages;

    const githubCombinedStats = {
        total_contributions: githubStats?.total_contributions || 0,
        total_prs: githubStats?.total_prs || 0,
        total_issues: githubStats?.total_issues || 0,
        recent_repos: githubRecentRepos || [], // Changed from pinned_repos
        top_languages: githubLanguages || {},
    };

    const githubProcessed = await this.dataProcessor.processGithubData(githubCombinedStats);
    processedContent.CONTRIBUTION_STATS = githubProcessed.contribution_stats;
    processedContent.PINNED_REPOS = githubProcessed.pinned_repos; // This placeholder name remains the same in the template
    processedContent.GITHUB_LANGUAGES = githubProcessed.github_languages;

    // Process Wakatime data
    const wakatimeStats = rawData.wakatime_stats;
    const wakatimeProcessed = this.dataProcessor.processWakatimeData(wakatimeStats);
    processedContent.WAKATIME_SUMMARY = this.dataProcessor.generateComprehensiveWakatimeSummary(wakatimeStats);

    // Generate dynamic sections using LLM through DataProcessor
    processedContent.DYNAMIC_ABOUT_SECTION = await this.dataProcessor.generateDynamicAboutSection(githubCombinedStats, wakatimeStats);
    processedContent.FUN_FACTS = await this.dataProcessor.generateFunFacts(githubCombinedStats, wakatimeStats);
    processedContent.DYNAMIC_TECH_STACK = this.dataProcessor.generateDynamicTechStack(githubCombinedStats, wakatimeStats);
    processedContent.MOTIVATIONAL_QUOTE = await this.dataProcessor.generateMotivationalQuote(githubCombinedStats, wakatimeStats);
    processedContent.CODING_STREAK_MESSAGE = this.dataProcessor.generateCodingStreakMessage(githubCombinedStats);

    // Generate dynamic GitHub stats URLs
    const githubStatsUrls = this.dataProcessor.generateDynamicGithubStatsUrls("vishals9711"); // Replace with actual username if dynamic
    processedContent.GITHUB_STATS_CARD = githubStatsUrls.stats_card;
    processedContent.GITHUB_STREAK_STATS = githubStatsUrls.streak_stats;
    processedContent.GITHUB_TOP_LANGUAGES = githubStatsUrls.top_languages;
    processedContent.GITHUB_TROPHIES = githubStatsUrls.trophies;

    // Add last updated timestamp
    processedContent.LAST_UPDATED = new Date().toLocaleString('en-US', { month: 'long', day: 'numeric', year: 'numeric', hour: 'numeric', minute: 'numeric', hour12: false, timeZoneName: 'short' });

    return processedContent;
  }

  async _generateReadme(processedData, outputPath) {
    try {
      await this.templateEngine.processTemplate(processedData, outputPath); // Pass processedData and output path
      console.log("README generation completed successfully");
    } catch (error) {
      console.error(`Error generating README: ${error.message}`);
      throw error;
    }
  }
}

// Main execution
const GITHUB_TOKEN = process.env.GH_PAT_TOKEN;
const WAKATIME_API_KEY = process.env.WAKATIME_API_KEY;
const LLM_API_KEY = process.env.LLM_API_KEY; // New LLM API Key

if (!GITHUB_TOKEN) {
  console.error("GH_PAT_TOKEN environment variable not set");
  process.exit(1);
}

if (!WAKATIME_API_KEY) {
  console.error("WAKATIME_API_KEY environment variable not set");
  process.exit(1);
}

if (!LLM_API_KEY) {
  console.warn("LLM_API_KEY environment variable not set. LLM features will use static fallbacks.");
  // Do not exit, allow the script to run with static fallbacks.
}

const updater = new ProfileUpdater(GITHUB_TOKEN, WAKATIME_API_KEY, LLM_API_KEY);
updater.run();
