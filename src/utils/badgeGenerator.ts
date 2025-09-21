import { Format, makeBadge } from 'badge-maker';

interface BadgeOptions {
  label: string;
  message: string;
  color?: string;
  style?: 'plastic' | 'flat' | 'flat-square' | 'for-the-badge' | 'social';
  logo?: string;
  logoColor?: string;
}

export function generateBadge({
  label,
  message,
  color = '#007acc',
  style = 'for-the-badge',
  logo,
  logoColor = 'white',
}: BadgeOptions): string {
  const encodedLabel = encodeURIComponent(label);
  const encodedMessage = encodeURIComponent(message);
  const encodedColor = encodeURIComponent(color.replace('#', ''));

  let badgeUrl = `https://img.shields.io/badge/${encodedLabel}-${encodedMessage}-${encodedColor}?style=${style}`;

  if (logo) {
    badgeUrl += `&logo=${encodeURIComponent(logo)}`;
    if (logoColor) {
      badgeUrl += `&logoColor=${encodeURIComponent(logoColor)}`;
    }
  }

  return `![${label}](` + badgeUrl + ')';
}

export function generateTechBadge(techName: string): string {
  // Technology colors and Simple Icons slugs with high contrast
  const techInfo: Record<string, { color: string; logo?: string }> = {
    JavaScript: { color: '#000000', logo: 'javascript' }, // Changed from yellow to black for max contrast
    TypeScript: { color: '#005a9c', logo: 'typescript' }, // Darkened for better contrast
    Python: { color: '#2b5b84', logo: 'python' }, // Darkened for better contrast
    Java: { color: '#005e7c', logo: 'java' }, // Darkened for better contrast
    'C++': { color: '#00599c', logo: 'cplusplus' },
    'C#': { color: '#1a6e17', logo: 'csharp' }, // Darkened for better contrast
    PHP: { color: '#4F5B93', logo: 'php' }, // Darkened for better contrast
    Ruby: { color: '#701516', logo: 'ruby' },
    Go: { color: '#006782', logo: 'go' }, // Darkened for better contrast
    Rust: { color: '#000000', logo: 'rust' }, // Changed from tan to black for max contrast
    Swift: { color: '#c66700', logo: 'swift' }, // Darkened for better contrast
    Kotlin: { color: '#6a40d9', logo: 'kotlin' }, // Darkened for better contrast
    React: { color: '#20232a', logo: 'react' }, // Changed from light blue to a common dark theme color
    Vue: { color: '#34495e', logo: 'vue.js' }, // Using the darker brand color
    Angular: { color: '#c3002b', logo: 'angular' }, // Slightly darkened for better contrast
    'Node.js': { color: '#2d6a2b', logo: 'nodedotjs' }, // Darkened for better contrast
    'Express.js': { color: '#000000', logo: 'express' },
    Django: { color: '#092e20', logo: 'django' },
    Flask: { color: '#000000', logo: 'flask' },
    Spring: { color: '#428b1e', logo: 'spring' }, // Darkened for better contrast
    Docker: { color: '#1d76bb', logo: 'docker' }, // Darkened for better contrast
    Kubernetes: { color: '#2555b0', logo: 'kubernetes' }, // Darkened for better contrast
    AWS: { color: '#232f3e', logo: 'amazonaws' }, // Changed from orange to official dark theme color
    MongoDB: { color: '#348335', logo: 'mongodb' }, // Darkened for better contrast
    PostgreSQL: { color: '#2a5578', logo: 'postgresql' }, // Darkened for better contrast
    MySQL: { color: '#005C84', logo: 'mysql' }, // Using a darker official color
    Redis: { color: '#c73228', logo: 'redis' }, // Slightly darkened for better contrast
    Git: { color: '#c43a20', logo: 'git' }, // Darkened for better contrast
    Linux: { color: '#000000', logo: 'linux' }, // Changed from yellow to black for max contrast
    Windows: { color: '#005da6', logo: 'windows' }, // Darkened for better contrast
    macOS: { color: '#000000', logo: 'apple' },
    HTML: { color: '#ca421c', logo: 'html5' }, // Darkened for better contrast
    CSS: { color: '#105a96', logo: 'css3' }, // Darkened for better contrast
    SCSS: { color: '#a53d6d', logo: 'sass' }, // Darkened for better contrast
    Sass: { color: '#a53d6d', logo: 'sass' }, // Darkened for better contrast
    'Tailwind CSS': { color: '#03697c', logo: 'tailwindcss' }, // Darkened for better contrast
    'Next.js': { color: '#000000', logo: 'nextdotjs' },
    'Nuxt.js': { color: '#007a58', logo: 'nuxtdotjs' }, // Darkened for better contrast
    Svelte: { color: '#e03700', logo: 'svelte' }, // Slightly darkened for better contrast
    GraphQL: { color: '#b30078', logo: 'graphql' }, // Darkened for better contrast
    'REST APIs': { color: '#00732c', logo: 'openapi' }, // Darkened for better contrast
    Jest: { color: '#c21325', logo: 'jest' },
    Mocha: { color: '#735032', logo: 'mocha' }, // Darkened for better contrast
    Webpack: { color: '#1563a0', logo: 'webpack' }, // Changed from light blue to a darker brand color
    Vite: { color: '#4a50d6', logo: 'vite' }, // Darkened for better contrast
    ESLint: { color: '#4b32c3', logo: 'eslint' },
    Prettier: { color: '#1a1a1a', logo: 'prettier' },
    NPM: { color: '#cb3837', logo: 'npm' },
    Yarn: { color: '#23739a', logo: 'yarn' }, // Darkened for better contrast
    PNPM: { color: '#c56c00', logo: 'pnpm' }, // Darkened for better contrast
  };
  const info = techInfo[techName] || { color: '#007acc' };
  const encodedTechName = encodeURIComponent(techName);
  const encodedColor = encodeURIComponent(info.color.replace('#', ''));

  let badgeUrl = `https://img.shields.io/badge/${encodedTechName}-${encodedColor}?style=flat`;

  if (info.logo) {
    badgeUrl += `&logo=${info.logo}`;
  }

  return `![${techName}](` + badgeUrl + ')';
}

export function generateCountBadge(
  label: string,
  count: number,
  color = '#007acc'
): string {
  const encodedLabel = encodeURIComponent(label);
  const encodedCount = encodeURIComponent(count.toString());

  return `![${label}](https://img.shields.io/badge/${encodedLabel}-${encodedCount}-${color}?style=for-the-badge)`;
}

export function generatePercentageBadge(
  language: string,
  percentage: string
): string {
  const encodedLanguage = encodeURIComponent(language);
  const encodedPercentage = encodeURIComponent(`${percentage}%`);

  return `![${language}](https://img.shields.io/badge/${encodedLanguage}-${encodedPercentage}-007acc?style=flat-square)`;
}
