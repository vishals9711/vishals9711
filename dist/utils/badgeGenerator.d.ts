interface BadgeOptions {
    label: string;
    message: string;
    color?: string;
    style?: 'plastic' | 'flat' | 'flat-square' | 'for-the-badge' | 'social';
    logo?: string;
    logoColor?: string;
}
export declare function generateBadge({ label, message, color, style, logo, logoColor }: BadgeOptions): string;
export declare function generateTechBadge(techName: string): string;
export declare function generateCountBadge(label: string, count: number, color?: string): string;
export declare function generatePercentageBadge(language: string, percentage: string): string;
export {};
//# sourceMappingURL=badgeGenerator.d.ts.map