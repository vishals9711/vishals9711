interface ProfileData {
    header: {
        bio: string;
    };
    stats: {
        stars: number;
        commits: number;
        prs: number;
        issues: number;
        contributedTo: number;
        followers?: number;
        following?: number;
        publicRepos?: number;
        totalContributions?: number;
    };
    languages: Record<string, string>;
    spotlight: {
        name: string;
        description: string;
        stars: number;
        language: string;
        url: string;
    };
    techStack: string[];
    recentActivity: {
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
    };
    wakatimeData: {
        totalHours: number;
        topLanguage: string;
        languages: Array<{
            name: string;
            percent: number;
            hours: number;
        }>;
    } | null;
}
export declare function generateReadme(data: ProfileData): void;
export {};
//# sourceMappingURL=templateService.d.ts.map