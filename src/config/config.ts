export interface Config {
  github: {
    username: string;
    personalAccessToken?: string;
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
    twitter?: string;
    website?: string;
  };
}

export const defaultConfig: Config = {
  github: {
    username: 'vishals9711',
    personalAccessToken: process.env.GH_PAT_TOKEN,
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
    twitter: 'https://x.com/vishals1197',
    website: 'https://www.vishalrsharma.dev/',
  },
};

export function getConfig(): Config {
  return {
    ...defaultConfig,
    github: {
      ...defaultConfig.github,
      personalAccessToken: process.env.GH_PAT_TOKEN || defaultConfig.github.personalAccessToken,
    },
    wakatime: {
      ...defaultConfig.wakatime,
      apiKey: process.env.WAKATIME_API_KEY || defaultConfig.wakatime.apiKey,
      enabled: !!process.env.WAKATIME_API_KEY && defaultConfig.wakatime.enabled,
    },
    llm: {
      ...defaultConfig.llm,
      apiKey: process.env.LLM_API_KEY || process.env.GOOGLE_API_KEY || defaultConfig.llm.apiKey,
    },
  };
}
