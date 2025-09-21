interface BioData {
    topLanguage: string;
    latestRepo: string;
    totalHours: number;
    username: string;
}
interface BioResponse {
    bio: string;
}
interface ProjectData {
    repoName: string;
    language: string;
    stars: number;
    hasReadme: boolean;
    fileCount: number;
}
interface ProjectResponse {
    description: string;
}
interface TechStackData {
    languages: string[];
}
interface TechStackResponse {
    techStack: string[];
}
export declare function generateBio(data: BioData): Promise<BioResponse>;
export declare function generateProjectDescription(data: ProjectData): Promise<ProjectResponse>;
export declare function generateTechStack(data: TechStackData): Promise<TechStackResponse>;
export {};
//# sourceMappingURL=llmClient.d.ts.map