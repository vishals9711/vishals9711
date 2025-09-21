import { makeBadge } from 'badge-maker';

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
  const format: any = {
    text: [label, message],
    color,
    style,
    ...(logo && { logo }),
    ...(logoColor && { logoColor }),
  };

  const svg = makeBadge(format);
  // Convert SVG to base64 for use in markdown
  const base64 = Buffer.from(svg).toString('base64');
  return `![${label} ${message}](data:image/svg+xml;base64,${base64})`;
}

export function generateTechBadge(techName: string): string {
  // Common technology colors
  const techColors: Record<string, string> = {
    JavaScript: '#f7df1e',
    TypeScript: '#3178c6',
    Python: '#3776ab',
    Java: '#007396',
    'C++': '#00599c',
    'C#': '#239120',
    PHP: '#777bb4',
    Ruby: '#701516',
    Go: '#00add8',
    Rust: '#dea584',
    Swift: '#ffac45',
    Kotlin: '#f18e33',
    React: '#61dafb',
    Vue: '#4fc08d',
    Angular: '#dd0031',
    'Node.js': '#339933',
    'Express.js': '#000000',
    Django: '#092e20',
    Flask: '#000000',
    Spring: '#6db33f',
    Docker: '#2496ed',
    Kubernetes: '#326ce5',
    AWS: '#ff9900',
    MongoDB: '#47a248',
    PostgreSQL: '#336791',
    MySQL: '#4479a1',
    Redis: '#dc382d',
    Git: '#f05032',
    Linux: '#fcc624',
    Windows: '#0078d6',
    macOS: '#000000',
    HTML: '#e34f26',
    CSS: '#1572b6',
    SCSS: '#c6538c',
    Sass: '#cc6699',
    'Tailwind CSS': '#06b6d4',
    'Next.js': '#000000',
    'Nuxt.js': '#00c58e',
    Svelte: '#ff3e00',
    GraphQL: '#e10098',
    'REST APIs': '#009639',
    Jest: '#c21325',
    Mocha: '#8d6748',
    Webpack: '#8dd6f9',
    Vite: '#646cff',
    ESLint: '#4b32c3',
    Prettier: '#f7b93e',
    NPM: '#cb3837',
    Yarn: '#2c8ebb',
    PNPM: '#f69220',
  };

  const color = techColors[techName] || '#007acc';
  const logo = techName
    .toLowerCase()
    .replace(/[^a-z0-9]/g, '')
    .replace('js', 'javascript')
    .replace('nodejs', 'node.js')
    .replace('nextjs', 'next.js')
    .replace('nuxtjs', 'nuxt.js')
    .replace('tailwindcss', 'tailwind-css')
    .replace('postgresql', 'postgresql')
    .replace('mysql', 'mysql')
    .replace('mongodb', 'mongodb');

  return generateBadge({
    label: techName,
    message: '',
    color,
    logo,
    style: 'flat',
  });
}

export function generateCountBadge(
  label: string,
  count: number,
  color = '#007acc'
): string {
  return generateBadge({
    label,
    message: count.toString(),
    color,
    style: 'for-the-badge',
  });
}

export function generatePercentageBadge(
  language: string,
  percentage: string
): string {
  return generateBadge({
    label: language,
    message: `${percentage}%`,
    color: '#007acc',
    style: 'flat-square',
  });
}
