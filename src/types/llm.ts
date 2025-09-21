export interface BioData {
  topLanguage: string;
  latestRepo: string;
  totalHours: number;
  username: string;
}

export interface BioResponse {
  bio: string;
}

export interface ProjectData {
  repoName: string;
  language: string | null | undefined;
  stars: number;
  hasReadme: boolean;
  fileCount: number;
}

export interface ProjectResponse {
  description: string;
}

export interface TechStackData {
  languages: string[];
}

export interface TechStackResponse {
  techStack: string[];
}
