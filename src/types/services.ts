export interface HeaderData {
  bio: string;
}

export interface LanguagesData {
  [language: string]: string; // language -> percentage
}

export interface GithubStats {
  stars: number;
  commits: number;
  contributedTo: number;
  followers?: number;
  following?: number;
  publicRepos?: number;
  totalContributions?: number;
}

export interface ProjectSpotlight {
  name: string;
  description: string;
  stars: number;
  language: string;
  url: string;
}

export interface RecentActivity {
  totalCommits: number;
  recentCommits: Array<{
    date: string;
    count: number;
  }>;
  recentRepos: Array<{
    name: string;
    pushed_at: string;
    language: string;
  }>;
}

export interface WakaTimeData {
  totalHours: number;
  topLanguage: string;
  languages: import('../types/wakatime.js').WakaTimeLanguage[];
}

export interface ProfileData {
  header: HeaderData;
  stats: GithubStats;
  languages: LanguagesData;
  spotlight: ProjectSpotlight;
  techStack: string[];
  recentActivity: RecentActivity;
  wakatimeData: WakaTimeData | null;
}
