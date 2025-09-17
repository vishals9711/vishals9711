import { makeBadge } from 'badge-maker';

class DataProcessor {
  constructor(llmClient) {
    this.llmClient = llmClient;
  }

  formatTimeDuration(seconds) {
    if (seconds <= 0) {
      return "0 mins";
    }

    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);

    if (hours > 0 && minutes > 0) {
      return `${hours} hrs ${minutes} mins`;
    } else if (hours > 0) {
      return `${hours} hrs`;
    } else {
      return `${minutes} mins`;
    }
  }

  formatNumber(number) {
    return number.toLocaleString();
  }

  generateLanguageBarChart(languages, maxLanguages = 5) {
    if (!languages || languages.length === 0) {
      return "No language data available";
    }

    const sortedLanguages = [...languages].sort((a, b) => b.total_seconds - a.total_seconds);
    const topLanguages = sortedLanguages.slice(0, maxLanguages);

    if (topLanguages.length === 0) {
      return "No language data available";
    }

    const maxTime = topLanguages[0].total_seconds;
    const barWidth = 20;

    const chartLines = [];
    for (const lang of topLanguages) {
      const barLength = maxTime > 0 ? Math.floor((lang.total_seconds / maxTime) * barWidth) : 0;
      const filledBar = "█".repeat(barLength);
      const emptyBar = "░".repeat(barWidth - barLength);
      const bar = filledBar + emptyBar;

      const timeStr = this.formatTimeDuration(lang.total_seconds);

      // Pad language name to 12 characters for alignment
      const paddedName = lang.name.padEnd(12);
      const percentage = lang.percentage.toFixed(1);

      const line = `${paddedName} ${bar} ${percentage}% (${timeStr})`;
      chartLines.push(line);
    }

    return chartLines.join("\n");
  }

  processGithubData(githubStats) {
    const processed = {};

    // Format contribution statistics
    const contributions = this.formatNumber(githubStats.total_contributions);
    const prs = this.formatNumber(githubStats.total_prs);
    const issues = this.formatNumber(githubStats.total_issues);

    processed["contribution_stats"] = (
      `📈 **${contributions}** contributions this year\n` +
      `🔀 **${prs}** pull requests opened\n` +
      `🐛 **${issues}** issues created`
    );

    // Format recent repositories (changed from pinned)
    if (githubStats.recent_repos && githubStats.recent_repos.length > 0) {
      const repoLines = await Promise.all(githubStats.recent_repos.map(async repo => {
        const stars = this.formatNumber(repo.stars);
        let techStack = "";

        if (this.llmClient && process.env.LLM_API_KEY) {
          const prompt = `Given the repository name: ${repo.name}, description: ${repo.description}, and languages: ${repo.languages.join(', ')}. Extract no more than 3-5 *core* technologies/frameworks/libraries that define its tech stack as a comma-separated string. For example: 'React, Node.js, Python, Flask, TypeScript, MongoDB'. Do not include any introductory phrases like "Tech Stack:" or "This project uses:". Just the comma-separated list.`;
          try {
            techStack = await this.llmClient.generateText(prompt);
            // Clean up any extra markdown or unwanted characters from LLM output
            techStack = techStack.replace(/['"`*]/g, '').trim();
          } catch (error) {
            console.error(`LLM generation failed for tech stack of ${repo.name}, falling back:`, error);
          }
        }

        return `- **[${repo.name}](${repo.url})** - ${repo.description} (${repo.primary_language}) ⭐ ${stars}${techStack ? ` - Tech Stack: ${techStack}` : ''}`;
      }));
      processed["pinned_repos"] = repoLines.join("\n"); // Placeholder name remains PINNED_REPOS
    } else {
      processed["pinned_repos"] = "No recent repositories available";
    }

    // Format top languages
    if (githubStats.top_languages && Object.keys(githubStats.top_languages).length > 0) {
      const totalBytes = Object.values(githubStats.top_languages).reduce((sum, bytes) => sum + bytes, 0);
      const languageTimes = Object.entries(githubStats.top_languages).map(([name, bytes_count]) => ({
        name,
        total_seconds: bytes_count, // Using bytes as proxy for time
        percentage: totalBytes > 0 ? (bytes_count / totalBytes) * 100 : 0,
      }));
      processed["github_languages"] = this.generateLanguageBarChart(languageTimes);
    } else {
      processed["github_languages"] = "No language data available";
    }

    return processed;
  }

  processWakatimeData(wakatimeStats) {
    const processed = {};

    // Format total coding time
    const totalTime = this.formatTimeDuration(wakatimeStats.total_seconds);
    processed["total_coding_time"] = `⏱️ **${totalTime}** coding time this week`;

    // Format language statistics with bar chart
    if (wakatimeStats.languages && wakatimeStats.languages.length > 0) {
      processed["wakatime_languages"] = this.generateLanguageBarChart(wakatimeStats.languages);
    } else {
      processed["wakatime_languages"] = "No language data available";
    }

    // Format editor statistics
    if (wakatimeStats.editors && wakatimeStats.editors.length > 0) {
      const editorLines = wakatimeStats.editors.slice(0, 3).map(editor => {
        const name = editor.name || 'Unknown';
        // The Python script used `percent` from Wakatime API, but our Node.js client calculates percentage based on total_seconds.
        // We need to re-calculate percentage here if it's not present in the editor object directly.
        const totalSeconds = wakatimeStats.total_seconds;
        const editorSeconds = editor.total_seconds || 0;
        const percentage = totalSeconds > 0 ? (editorSeconds / totalSeconds * 100).toFixed(1) : 0;
        const timeStr = this.formatTimeDuration(editorSeconds);
        return `- **${name}**: ${percentage}% (${timeStr})`;
      });
      processed["editors"] = editorLines.join("\n");
    } else {
      processed["editors"] = "No editor data available";
    }

    // Format operating system statistics
    if (wakatimeStats.operating_systems && wakatimeStats.operating_systems.length > 0) {
      const osLines = wakatimeStats.operating_systems.slice(0, 3).map(osData => {
        const name = osData.name || 'Unknown';
        const totalSeconds = wakatimeStats.total_seconds;
        const osSeconds = osData.total_seconds || 0;
        const percentage = totalSeconds > 0 ? (osSeconds / totalSeconds * 100).toFixed(1) : 0;
        const timeStr = this.formatTimeDuration(osSeconds);
        return `- **${name}**: ${percentage}% (${timeStr})`;
      });
      processed["operating_systems"] = osLines.join("\n");
    } else {
      processed["operating_systems"] = "No operating system data available";
    }

    return processed;
  }

  generateComprehensiveWakatimeSummary(wakatimeStats) {
    const processed = this.processWakatimeData(wakatimeStats);

    const summaryLines = [
      `📊 **Coding Activity (Last 7 Days)**`,
      ``,
      processed["total_coding_time"],
      ``,
      `**Top Languages:**`,
      "```",
      processed["wakatime_languages"],
      "```",
      ``,
      `**Editors:**`,
      processed["editors"],
      ``,
      `**Operating Systems:**`,
      processed["operating_systems"],
    ];

    return summaryLines.join("\n");
  }

  generateDynamicTechStack(githubStats, wakatimeStats) {
    // Base tech stack badges (always included)
    const baseBadges = [
      `![JavaScript](https://img.shields.io/badge/javascript-%23323330.svg?style=for-the-badge&logo=javascript&logoColor=%23F7DF1E)`,
      `![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)`,
      `![TypeScript](https://img.shields.io/badge/typescript-%23007ACC.svg?style=for-the-badge&logo=typescript&logoColor=white)`,
      `![HTML5](https://img.shields.io/badge/html5-%23E34F26.svg?style=for-the-badge&logo=html5&logoColor=white)`,
    ];

    const dynamicBadges = [];

    const langBadgeMap = {
      'JavaScript': { label: 'JavaScript', message: '#323330', color: '#F7DF1E', logo: 'javascript' },
      'Python': { label: 'Python', message: '3670A0', color: 'ffdd54', logo: 'python' },
      'TypeScript': { label: 'TypeScript', message: '#007ACC', color: 'white', logo: 'typescript' },
      'Java': { label: 'Java', message: '#ED8B00', color: 'white', logo: 'openjdk' },
      'Go': { label: 'Go', message: '#00ADD8', color: 'white', logo: 'go' },
      'Rust': { label: 'Rust', message: '#000000', color: 'white', logo: 'rust' },
      'C++': { label: 'C++', message: '#00599C', color: 'white', logo: 'c++' },
      'C#': { label: 'C#', message: '#239120', color: 'white', logo: 'c-sharp' },
    };

    const shieldsIoBadge = (label, message, color, logo, logoColor = 'white', style = 'for-the-badge') => {
        const encodedLabel = encodeURIComponent(label);
        const encodedMessage = encodeURIComponent(message);
        const encodedColor = color.startsWith('#') ? color.substring(1) : color;
        const encodedLogo = logo ? `&logo=${encodeURIComponent(logo)}` : '';
        const encodedLogoColor = logoColor ? `&logoColor=${encodeURIComponent(logoColor)}` : '';
        return `![${label}](https://img.shields.io/badge/${encodedLabel}-${encodedMessage}-${encodedColor}.svg?style=${style}${encodedLogo}${encodedLogoColor})`
    }

    // Add badges based on GitHub languages
    if (githubStats && githubStats.top_languages) {
      const githubLangs = Object.keys(githubStats.top_languages);
      for (const lang of githubLangs) {
        if (langBadgeMap[lang]) {
          const badge = shieldsIoBadge(langBadgeMap[lang].label, langBadgeMap[lang].message, langBadgeMap[lang].color, langBadgeMap[lang].logo);
          if (!baseBadges.includes(badge) && !dynamicBadges.includes(badge)) {
            dynamicBadges.push(badge);
          }
        }
      }
    }

    // Add badges based on Wakatime languages
    if (wakatimeStats && wakatimeStats.languages) {
      const wakatimeLangs = wakatimeStats.languages.map(lang => lang.name);
      for (const lang of wakatimeLangs) {
        if (langBadgeMap[lang]) {
          const badge = shieldsIoBadge(langBadgeMap[lang].label, langBadgeMap[lang].message, langBadgeMap[lang].color, langBadgeMap[lang].logo);
          if (!baseBadges.includes(badge) && !dynamicBadges.includes(badge)) {
            dynamicBadges.push(badge);
          }
        }
      }
    }

    // Combine all badges
    const allBadges = [...baseBadges, ...dynamicBadges];

    // Add framework and tool badges (these could be made dynamic too)
    const frameworkBadges = [
      `![React](https://img.shields.io/badge/react-%2320232a.svg?style=for-the-badge&logo=react&logoColor=%2361DAFB)`,
      `![NodeJS](https://img.shields.io/badge/node.js-6DA55F?style=for-the-badge&logo=node.js&logoColor=white)`,
      `![Next JS](https://img.shields.io/badge/Next-black?style=for-the-badge&logo=next.js&logoColor=white)`,
      `![Express.js](https://img.shields.io/badge/express.js-%23404d59.svg?style=for-the-badge&logo=express&logoColor=%2361DAFB)`,
      `![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)`,
      `![Flask](https://img.shields.io/badge/flask-%23000.svg?style=for-the-badge&logo=flask&logoColor=white)`,
    ];

    const cloudBadges = [
      `![AWS](https://img.shields.io/badge/AWS-%23FF9900.svg?style=for-the-badge&logo=amazon-aws&logoColor=white)`,
      `![Google Cloud](https://img.shields.io/badge/GoogleCloud-%234285F4.svg?style=for-the-badge&logo=google-cloud&logoColor=white)`,
      `![DigitalOcean](https://img.shields.io/badge/DigitalOcean-%230167ff.svg?style=for-the-badge&logo=digitalOcean&logoColor=white)`,
    ];

    const databaseBadges = [
      `![MongoDB](https://img.shields.io/badge/MongoDB-%234ea94b.svg?style=for-the-badge&logo=mongodb&logoColor=white)`,
      `![Redis](https://img.shields.io/badge/redis-%23DD0031.svg?style=for-the-badge&logo=redis&logoColor=white)`,
      `![SQLite](https://img.shields.io/badge/sqlite-%2307405e.svg?style=for-the-badge&logo=sqlite&logoColor=white)`,
    ];

    allBadges.push(...frameworkBadges, ...cloudBadges, ...databaseBadges);

    return allBadges.join(" ");
  }

  generateDynamicGithubStatsUrls(username) {
    const baseParams = new URLSearchParams({
      username: username,
      theme: 'dark',
      hide_border: 'false',
      include_all_commits: 'false',
      count_private: 'false',
    });

    // GitHub stats card
    const statsParams = new URLSearchParams(baseParams);
    statsParams.append('show_icons', 'true');
    statsParams.append('rank_icon', 'github');
    const statsUrl = `https://github-readme-stats.vercel.app/api?${statsParams.toString()}`;

    // GitHub streak stats
    const streakUrl = `https://github-readme-streak-stats.herokuapp.com/?user=${username}&theme=dark&hide_border=false`;

    // Top languages
    const langsParams = new URLSearchParams(baseParams);
    langsParams.append('layout', 'compact');
    langsParams.append('langs_count', '8');
    const langsUrl = `https://github-readme-stats.vercel.app/api/top-langs/?${langsParams.toString()}`;

    // GitHub trophies
    const trophiesUrl = `https://github-profile-trophy.vercel.app/?username=${username}&theme=radical&no-frame=false&no-bg=true&margin-w=4`;

    return {
      stats_card: statsUrl,
      streak_stats: streakUrl,
      top_languages: langsUrl,
      trophies: trophiesUrl,
    };
  }

  generateDynamicSocialLinks(socialData) {
    const socialBadges = {
      'linkedin': '[![LinkedIn](https://img.shields.io/badge/LinkedIn-%230077B5.svg?logo=linkedin&logoColor=white)]({url})',
      'twitter': '[![Twitter](https://img.shields.io/badge/Twitter-%231DA1F2.svg?logo=Twitter&logoColor=white)]({url})',
      'github': '[![GitHub](https://img.shields.io/badge/GitHub-%23121011.svg?logo=github&logoColor=white)]({url})',
      'email': '[![Email](https://img.shields.io/badge/Email-D14836?logo=gmail&logoColor=white)](mailto:{url})',
      'website': '[![Website](https://img.shields.io/badge/Website-000000?logo=About.me&logoColor=white)]({url})',
      'medium': '[![Medium](https://img.shields.io/badge/Medium-12100E?logo=medium&logoColor=white)]({url})',
      'dev': '[![Dev.to](https://img.shields.io/badge/dev.to-0A0A0A?logo=dev.to&logoColor=white)]({url})',
      'stackoverflow': '[![Stack Overflow](https://img.shields.io/badge/-Stackoverflow-FE7A16?logo=stack-overflow&logoColor=white)]({url})',
    };

    const formattedLinks = [];
    for (const platform in socialData) {
      const url = socialData[platform];
      if (socialBadges[platform.toLowerCase()] && url) {
        formattedLinks.push(socialBadges[platform.toLowerCase()].replace('{url}', url));
      }
    }
    return formattedLinks.join(" ");
  }

  generateActivitySummary(githubStats, wakatimeStats) {
    const summaryParts = [];

    // GitHub activity insights
    if (githubStats) {
      if (githubStats.total_contributions > 0) {
        summaryParts.push(`🔥 **${this.formatNumber(githubStats.total_contributions)}** contributions this year`);
      }
      if (githubStats.total_prs > 0) {
        summaryParts.push(`🔀 **${this.formatNumber(githubStats.total_prs)}** pull requests opened`);
      }
      if (githubStats.total_issues > 0) {
        summaryParts.push(`🐛 **${this.formatNumber(githubStats.total_issues)}** issues created`);
      }
    }

    // Wakatime insights
    if (wakatimeStats && wakatimeStats.total_seconds > 0) {
      const totalTime = this.formatTimeDuration(wakatimeStats.total_seconds);
      summaryParts.push(`⏱️ **${totalTime}** coding time this week`);

      if (wakatimeStats.languages && wakatimeStats.languages.length > 0) {
        const topLang = wakatimeStats.languages[0].name;
        summaryParts.push(`💻 **${topLang}** is my current favorite language`);
      }
    }

    if (summaryParts.length === 0) {
      return "🚀 **Building amazing things** - Check back soon for updates!";
    }

    return summaryParts.join("\n");
  }

  async generateDynamicAboutSection(githubStats, wakatimeStats) {
    if (this.llmClient && process.env.LLM_API_KEY) {
      const prompt = `You are a professional software engineer crafting an engaging GitHub profile 'About Me' section.
Given the following key user statistics:
- GitHub Contributions: ${githubStats.total_contributions}
- GitHub Pull Requests: ${githubStats.total_prs}
- GitHub Issues: ${githubStats.total_issues}
- Wakatime Total Coding Seconds (last 7 days): ${wakatimeStats.total_seconds}
- Top Coding Language (Wakatime): ${wakatimeStats.languages[0]?.name || 'Unknown'}

Generate a concise (2-3 sentences), professional, and inspiring 'About Me' section. Start with "Software Engineer @ TNM". Focus on achievements, passion for coding, and current interests based on the data. Avoid redundant phrases and aim for a positive, growth-oriented tone.`;
      try {
        const llmResponse = await this.llmClient.generateText(prompt);
        return llmResponse.trim();
      } catch (error) {
        console.error("LLM generation failed for About Section, falling back:", error);
      }
    }
    
    // Fallback logic (original implementation)
    const aboutParts = ["Software Engineer @ TNM"];

    // Add dynamic insights based on activity
    if (githubStats && githubStats.total_contributions > 100) {
      aboutParts.push("🚀 Passionate about open source");
    }

    if (wakatimeStats && wakatimeStats.total_seconds > 3600) { // More than 1 hour
      aboutParts.push("💻 Coding enthusiast");
    }

    if (githubStats && githubStats.total_prs > 10) {
      aboutParts.push("🔧 Always improving");
    }

    // Add current focus language
    if (wakatimeStats && wakatimeStats.languages && wakatimeStats.languages.length > 0) {
      const topLang = wakatimeStats.languages[0].name;
      aboutParts.push(`🎯 Currently focused on ${topLang}`);
    }

    return aboutParts.join(" | ");
  }

  async generateFunFacts(githubStats, wakatimeStats) {
    if (this.llmClient && process.env.LLM_API_KEY) {
      const prompt = `You are a creative content generator for a GitHub profile README's 'Fun Facts' section.
Given the following key user statistics:
- GitHub Contributions: ${githubStats.total_contributions}
- GitHub Pull Requests: ${githubStats.total_prs}
- GitHub Issues: ${githubStats.total_issues}
- Wakatime Total Coding Seconds (last 7 days): ${wakatimeStats.total_seconds}
- Top Coding Language (Wakatime): ${wakatimeStats.languages[0]?.name || 'Unknown'}

Generate 3-4 short, engaging, and positive fun facts about the user's coding activity. Each fact should start with a relevant emoji and be on a new line. Avoid generic statements and focus on interesting insights derived from the data. If data is low, emphasize potential and growth.`;
      try {
        const llmResponse = await this.llmClient.generateText(prompt);
        return llmResponse.trim();
      } catch (error) {
        console.error("LLM generation failed for Fun Facts, falling back:", error);
      }
    }

    // Fallback logic (original implementation)
    const facts = [];

    if (githubStats) {
      if (githubStats.total_contributions > 365) {
        facts.push("🔥 More than 1 contribution per day this year!");
      }

      if (githubStats.total_prs > 50) {
        facts.push("🚀 Prolific contributor to open source");
      }

      if (githubStats.total_issues > 20) {
        facts.push("🐛 Active bug hunter and problem solver");
      }
    }

    if (wakatimeStats && wakatimeStats.total_seconds > 7200) { // More than 2 hours
      facts.push("⏰ Dedicated coder with consistent activity");

      if (wakatimeStats.languages && wakatimeStats.languages.length > 5) {
        facts.push("🎨 Polyglot programmer");
      }
    }

    if (facts.length === 0) {
      facts.push("🌟 Building the future, one commit at a time");
    }

    return facts.join(" | ");
  }

  async generateMotivationalQuote(githubStats, wakatimeStats) {
    if (this.llmClient && process.env.LLM_API_KEY) {
      const prompt = `You are a motivational speaker providing an inspiring quote for a developer's GitHub profile README.
Given the following key user statistics:
- GitHub Contributions: ${githubStats.total_contributions}
- Wakatime Total Coding Seconds (last 7 days): ${wakatimeStats.total_seconds}

Generate a single, concise (1 sentence) motivational quote about coding or continuous learning. The quote should be uplifting and suitable for a professional profile. Do not include any introductory phrases like "Here's a quote:" or "My quote is:". Just the quote.`;
      try {
        const llmResponse = await this.llmClient.generateText(prompt);
        return llmResponse.trim();
      } catch (error) {
        console.error("LLM generation failed for Motivational Quote, falling back:", error);
      }
    }

    // Fallback logic (original implementation)
    const quotes = [
      "🚀 Code is poetry written in logic",
      "💡 Every bug is a feature waiting to be discovered",
      "⚡ Innovation happens at the intersection of creativity and code",
      "🎯 The best code is the code that solves real problems",
      "🌟 Turning coffee into code, one commit at a time",
      "🔧 Building tomorrow's solutions today",
      "💻 Code never lies, comments sometimes do",
      "🚀 From idea to implementation, one line at a time",
      "⚡ Debugging is like being a detective in a crime movie",
      "🎨 Code is art, and every developer is an artist",
    ];

    // Select quote based on activity patterns
    if (githubStats && githubStats.total_contributions > 500) {
      return quotes[0]; // High activity quote
    } else if (wakatimeStats && wakatimeStats.total_seconds > 10000) { // More than 2.7 hours
      return quotes[1]; // Dedicated coder quote
    } else if (githubStats && githubStats.total_prs > 20) {
      return quotes[2]; // Collaborative quote
    } else {
      return quotes[Math.floor(Math.random() * quotes.length)];
    }
  }

  generateCodingStreakMessage(githubStats) {
    if (!githubStats || githubStats.total_contributions === 0) {
      return "🌟 Ready to start my coding journey!";
    }

    const contributions = githubStats.total_contributions;

    if (contributions > 365) {
      return `🔥 On fire! ${this.formatNumber(contributions)} contributions this year`;
    } else if (contributions > 100) {
      return `🚀 Consistent coder with ${this.formatNumber(contributions)} contributions`;
    } else if (contributions > 50) {
      return `💪 Building momentum with ${this.formatNumber(contributions)} contributions`;
    } else {
      return `🌱 Growing my coding footprint with ${this.formatNumber(contributions)} contributions`;
    }
  }
}

export default DataProcessor;
