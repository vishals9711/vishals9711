export interface Config {
  github: {
    username: string;
    personalAccessToken?: string;
  };
  header: {
    image?: string;
  };
  wakatime: {
    apiKey?: string;
    enabled: boolean;
  };
  llm: {
    apiKey?: string;
    model: string;
    provider: 'gemini' | 'openai';
  };
  output: {
    readmePath: string;
    templatePath: string;
  };
  features: {
    wakatimeStats: boolean;
    githubStats: boolean;
    recentActivity: boolean;
    techStack: boolean;
    projectSpotlight: boolean;
  };
  social: {
    linkedin?: string;
    github?: string;
    twitter?: string;
    instagram?: string;
    stackoverflow?: string;
    website?: string;
    blog?: string;
  };
}

export const defaultConfig: Config = {
  github: {
    username: 'vishals9711',
    personalAccessToken: process.env.GH_PAT_TOKEN,
  },
  header: {
    image: '',
  },
  wakatime: {
    apiKey: process.env.WAKATIME_API_KEY,
    enabled: !!process.env.WAKATIME_API_KEY,
  },
  llm: {
    apiKey: process.env.LLM_API_KEY || process.env.GOOGLE_API_KEY,
    model: 'gemini-2.5-flash',
    provider: 'gemini',
  },
  output: {
    readmePath: './README.md',
    templatePath: './README.template.md',
  },
  features: {
    wakatimeStats: true,
    githubStats: true,
    recentActivity: true,
    techStack: true,
    projectSpotlight: true,
  },
  social: {
    linkedin: 'https://linkedin.com/in/vishals9711',
    github: 'https://github.com/vishals9711',
    twitter: 'https://x.com/vishals1197',
    instagram: '',
    stackoverflow: '',
    website: 'https://www.vishalrsharma.dev/',
    blog: '',
  },
};

export function getConfig(): Config {
  return {
    ...defaultConfig,
    github: {
      ...defaultConfig.github,
      personalAccessToken:
        process.env.GH_PAT_TOKEN || defaultConfig.github.personalAccessToken,
    },
    header: {
      ...defaultConfig.header,
      image: process.env.HEADER_IMAGE_URL || defaultConfig.header.image,
    },
    wakatime: {
      ...defaultConfig.wakatime,
      apiKey: process.env.WAKATIME_API_KEY || defaultConfig.wakatime.apiKey,
      enabled: !!process.env.WAKATIME_API_KEY && defaultConfig.wakatime.enabled,
    },
    llm: {
      ...defaultConfig.llm,
      apiKey:
        process.env.LLM_API_KEY ||
        process.env.GOOGLE_API_KEY ||
        defaultConfig.llm.apiKey,
    },
    social: {
      ...defaultConfig.social,
      linkedin: process.env.LINKEDIN_URL || defaultConfig.social.linkedin,
      github: process.env.GITHUB_URL || defaultConfig.social.github,
      twitter: process.env.TWITTER_URL || defaultConfig.social.twitter,
      instagram: process.env.INSTAGRAM_URL || defaultConfig.social.instagram,
      stackoverflow:
        process.env.STACKOVERFLOW_URL || defaultConfig.social.stackoverflow,
      website: process.env.WEBSITE_URL || defaultConfig.social.website,
      blog: process.env.BLOG_URL || defaultConfig.social.blog,
    },
  };
}
