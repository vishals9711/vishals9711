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
export declare const defaultConfig: Config;
export declare function getConfig(): Config;
//# sourceMappingURL=config.d.ts.map