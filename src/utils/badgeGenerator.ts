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
  const techInfo: Record<string, { color: string; logo?: string }> = {
    JavaScript: { color: '#000000', logo: 'javascript' },
    TypeScript: { color: '#005a9c', logo: 'typescript' },
    Python: { color: '#2b5b84', logo: 'python' },
    Java: { color: '#005e7c', logo: 'java' },
    'C++': { color: '#00599c', logo: 'cplusplus' },
    'C#': { color: '#1a6e17', logo: 'csharp' },
    PHP: { color: '#4F5B93', logo: 'php' },
    Ruby: { color: '#701516', logo: 'ruby' },
    Go: { color: '#006782', logo: 'go' },
    Rust: { color: '#000000', logo: 'rust' },
    Swift: { color: '#c66700', logo: 'swift' },
    Kotlin: { color: '#6a40d9', logo: 'kotlin' },
    React: { color: '#20232a', logo: 'react' },
    Vue: { color: '#34495e', logo: 'vue.js' },
    Angular: { color: '#c3002b', logo: 'angular' },
    'Node.js': { color: '#2d6a2b', logo: 'nodedotjs' },
    'Express.js': { color: '#000000', logo: 'express' },
    Django: { color: '#092e20', logo: 'django' },
    Flask: { color: '#000000', logo: 'flask' },
    Spring: { color: '#428b1e', logo: 'spring' },
    Docker: { color: '#1d76bb', logo: 'docker' },
    Kubernetes: { color: '#2555b0', logo: 'kubernetes' },
    AWS: { color: '#232f3e', logo: 'amazonaws' },
    MongoDB: { color: '#348335', logo: 'mongodb' },
    PostgreSQL: { color: '#2a5578', logo: 'postgresql' },
    MySQL: { color: '#005C84', logo: 'mysql' },
    Redis: { color: '#c73228', logo: 'redis' },
    Git: { color: '#c43a20', logo: 'git' },
    Linux: { color: '#000000', logo: 'linux' },
    Windows: { color: '#005da6', logo: 'windows' },
    macOS: { color: '#000000', logo: 'apple' },
    HTML: { color: '#ca421c', logo: 'html5' },
    CSS: { color: '#105a96', logo: 'css3' },
    SCSS: { color: '#a53d6d', logo: 'sass' }, 
    Sass: { color: '#a53d6d', logo: 'sass' }, 
    'Tailwind CSS': { color: '#03697c', logo: 'tailwindcss' },
    'Next.js': { color: '#000000', logo: 'nextdotjs' },
    'Nuxt.js': { color: '#007a58', logo: 'nuxtdotjs' },
    Svelte: { color: '#e03700', logo: 'svelte' },
    GraphQL: { color: '#b30078', logo: 'graphql' }, 
    'REST APIs': { color: '#00732c', logo: 'openapi' }, 
    Jest: { color: '#c21325', logo: 'jest' },
    Mocha: { color: '#735032', logo: 'mocha' }, 
    Webpack: { color: '#1563a0', logo: 'webpack' },
    Vite: { color: '#4a50d6', logo: 'vite' }, 
    ESLint: { color: '#4b32c3', logo: 'eslint' },
    Prettier: { color: '#1a1a1a', logo: 'prettier' },
    NPM: { color: '#cb3837', logo: 'npm' },
    Yarn: { color: '#23739a', logo: 'yarn' }, 
    PNPM: { color: '#c56c00', logo: 'pnpm' }, 
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
