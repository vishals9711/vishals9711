interface HeaderData {
    bio: string;
}
export declare function getHeaderAndBio(): Promise<HeaderData>;
interface LanguagesData {
    [language: string]: string;
}
export declare function getLanguages(): Promise<LanguagesData>;
interface GithubStats {
    stars: number;
    commits: number;
    prs: number;
    issues: number;
    contributedTo: number;
    followers?: number;
    following?: number;
    publicRepos?: number;
    totalContributions?: number;
}
export declare function getTechStack(): Promise<string[]>;
export declare function getGithubStats(): Promise<GithubStats>;
interface ProjectSpotlight {
    name: string;
    description: string;
    stars: number;
    language: string;
    url: string;
}
interface RecentActivity {
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
interface WakaTimeData {
    totalHours: number;
    topLanguage: string;
    languages: Array<{
        name: string;
        percent: number;
        hours: number;
    }>;
}
export declare function getProjectSpotlight(): Promise<ProjectSpotlight>;
export declare function getRecentActivity(): Promise<RecentActivity>;
export declare function getWakaTimeData(): Promise<WakaTimeData | null>;
export {};
//# sourceMappingURL=dataService.d.ts.map