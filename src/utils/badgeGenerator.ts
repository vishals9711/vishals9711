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
    JavaScript: { color: '#f7df1e', logo: 'javascript' },
    TypeScript: { color: '#007acc', logo: 'typescript' }, // Darker blue for better contrast
    Python: { color: '#3776ab', logo: 'python' },
    Java: { color: '#007396', logo: 'java' },
    'C++': { color: '#00599c', logo: 'cplusplus' },
    'C#': { color: '#239120', logo: 'csharp' },
    PHP: { color: '#777bb4', logo: 'php' },
    Ruby: { color: '#701516', logo: 'ruby' },
    Go: { color: '#00add8', logo: 'go' },
    Rust: { color: '#dea584', logo: 'rust' },
    Swift: { color: '#ffac45', logo: 'swift' },
    Kotlin: { color: '#7f52ff', logo: 'kotlin' }, // Purple for better contrast
    React: { color: '#61dafb', logo: 'react' },
    Vue: { color: '#4fc08d', logo: 'vue.js' },
    Angular: { color: '#dd0031', logo: 'angular' },
    'Node.js': { color: '#68a063', logo: 'nodedotjs' }, // Darker green
    'Express.js': { color: '#000000', logo: 'express' },
    Django: { color: '#092e20', logo: 'django' },
    Flask: { color: '#000000', logo: 'flask' },
    Spring: { color: '#6db33f', logo: 'spring' },
    Docker: { color: '#2496ed', logo: 'docker' },
    Kubernetes: { color: '#326ce5', logo: 'kubernetes' },
    AWS: { color: '#ff9900', logo: 'amazonaws' },
    MongoDB: { color: '#47a248', logo: 'mongodb' },
    PostgreSQL: { color: '#336791', logo: 'postgresql' },
    MySQL: { color: '#4479a1', logo: 'mysql' },
    Redis: { color: '#dc382d', logo: 'redis' },
    Git: { color: '#f05032', logo: 'git' },
    Linux: { color: '#fcc624', logo: 'linux' },
    Windows: { color: '#0078d6', logo: 'windows' },
    macOS: { color: '#000000', logo: 'apple' },
    HTML: { color: '#e34f26', logo: 'html5' },
    CSS: { color: '#1572b6', logo: 'css3' },
    SCSS: { color: '#c6538c', logo: 'sass' },
    Sass: { color: '#cc6699', logo: 'sass' },
    'Tailwind CSS': { color: '#06b6d4', logo: 'tailwindcss' },
    'Next.js': { color: '#000000', logo: 'nextdotjs' },
    'Nuxt.js': { color: '#00c58e', logo: 'nuxtdotjs' },
    Svelte: { color: '#ff3e00', logo: 'svelte' },
    GraphQL: { color: '#e10098', logo: 'graphql' },
    'REST APIs': { color: '#009639', logo: 'openapi' },
    Jest: { color: '#c21325', logo: 'jest' },
    Mocha: { color: '#8d6748', logo: 'mocha' },
    Webpack: { color: '#8dd6f9', logo: 'webpack' },
    Vite: { color: '#646cff', logo: 'vite' },
    ESLint: { color: '#4b32c3', logo: 'eslint' },
    Prettier: { color: '#1a1a1a', logo: 'prettier' }, // Dark gray for better contrast
    NPM: { color: '#cb3837', logo: 'npm' },
    Yarn: { color: '#2c8ebb', logo: 'yarn' },
    PNPM: { color: '#f69220', logo: 'pnpm' },
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
