# Profile Dynamo - Refactored

An automated GitHub profile README generator that dynamically updates your profile with real-time data from GitHub, Wakatime, and AI-generated content.

## 🏗️ Architecture

The application has been completely refactored with a modern, modular architecture:

```
src/
├── clients/           # API client modules
│   ├── githubClient.js    # GitHub API interactions
│   ├── wakatimeClient.js  # Wakatime API interactions
│   └── llmClient.js       # Google Gemini AI interactions
├── services/          # Business logic services
│   ├── dataService.js     # Data fetching and processing
│   └── templateService.js # README template rendering
└── index.js          # Main application entry point
```

## 🚀 Features

- **Dynamic Bio Generation**: AI-powered bio based on your recent coding activity
- **Real-time Stats**: Live GitHub contributions, repos, followers, and coding hours
- **Tech Arsenal**: Automatically detected technologies from your recent repositories
- **Project Spotlight**: Features your most recently updated project
- **Achievement System**: Unlocks badges based on coding patterns and contributions

## 📋 Prerequisites

- Node.js 18+ 
- pnpm package manager
- GitHub Personal Access Token
- Wakatime API Key
- Google Gemini API Key

## ⚙️ Setup

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd profile-dynamo
   ```

2. **Install dependencies**
   ```bash
   pnpm install
   ```

3. **Configure environment variables**
   ```bash
   cp env.example .env
   ```
   
   Edit `.env` with your actual API keys:
   ```
   GH_PAT_TOKEN=your_github_personal_access_token
   WAKATIME_API_KEY=your_wakatime_api_key
   LLM_API_KEY=your_google_gemini_api_key
   ```

4. **Run the application**
   ```bash
   pnpm start
   ```

## 🔧 API Keys Setup

### GitHub Personal Access Token
1. Go to [GitHub Settings > Developer settings > Personal access tokens](https://github.com/settings/tokens)
2. Generate a new token with `repo` and `user` scopes
3. Copy the token to your `.env` file

### Wakatime API Key
1. Visit [Wakatime Settings > API Key](https://wakatime.com/settings/api-key)
2. Copy your API key to the `.env` file

### Google Gemini API Key
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Add it to your `.env` file

## 🤖 GitHub Actions

The application is designed to run automatically via GitHub Actions. The workflow:

1. Runs every Sunday at 05:00 UTC
2. Can be triggered manually via `workflow_dispatch`
3. Automatically commits updated README.md to the repository

## 📊 Data Sources

- **GitHub API**: User data, repositories, contributions, activity
- **Wakatime API**: Coding statistics, language usage, time tracking
- **Google Gemini**: AI-generated bio content

## 🛠️ Development

The refactored codebase uses:
- **ES Modules** for modern JavaScript
- **Separation of Concerns** with dedicated client and service layers
- **Error Handling** with proper environment variable validation
- **Type Safety** with comprehensive input validation

## 📝 Template Customization

Edit `README.template.md` to customize your profile layout. The template uses EJS syntax:

```html
<%= header.bio %>
<%= stats.contributions %>
<% tech.forEach(t => { %>
  <img src="https://img.shields.io/badge/-<%= t %>-black" />
<% }) %>
```

## 🔍 Troubleshooting

- **Environment Variables**: Ensure all required API keys are set in `.env`
- **API Limits**: Check GitHub and Wakatime API rate limits
- **Permissions**: Verify GitHub token has required scopes
- **Dependencies**: Run `pnpm install` to ensure all packages are installed
- **Network Issues**: If you get `ENOTFOUND` errors, check your internet connection
- **JSON Parsing**: The LLM client now handles markdown-formatted responses automatically

## 🧪 Testing

The application has been tested with mock data and works correctly. To test with real data:

1. Set up your `.env` file with valid API keys
2. Run `pnpm start`
3. Check the generated `README.md` file

The template system is fully functional and will generate a beautiful profile README with your real data.

## 📄 License

ISC License - see LICENSE file for details.
