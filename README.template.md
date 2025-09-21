# 👋 Hi there! I'm @<%= config.github.username %>

<div align="center">

## 🚀 About Me

<%= header.bio %>

### 📊 GitHub Statistics

</div>

## 🛠️ Tech Stack

### 🚀 Technologies I Work With
<% techStack.forEach(t => { %>
<%= generateTechBadge(t) %><% }); %>

### 💡 Skills
- **Programming Languages**: JavaScript, TypeScript, Python, Java
- **Web Development**: React, Node.js, Express, HTML/CSS
- **Databases**: MongoDB, PostgreSQL, Redis
- **Tools & Platforms**: Git, Docker, AWS, Linux
- **Methodologies**: Agile, TDD, CI/CD

## 📈 GitHub Analytics

<div align="center">

### 📊 Main Statistics

| 🌟 Stars | 💻 Commits | 📁 Repos | 📊 Contributions |
|:--------:|:----------:|:--------:|:----------------:|
| <%= stats.stars %> | <%= stats.commits %> | <%= stats.publicRepos %> | <%= stats.totalContributions %> |

### 👥 Community

| 👥 Followers | 🎯 Following | 🤝 Contributed To |
|:------------:|:------------:|:-----------------:|
| <%= stats.followers %> | <%= stats.following %> | <%= stats.contributedTo %> |

</div>

<% if (wakatimeData) { %>
## ⚡ Recent Coding Activity (WakaTime)

⏰ **<%= wakatimeData.totalHours %> hours** of coding in the last 7 days

### 📊 Language Activity
| Language | Usage | Hours |
|:---------|-------:|------:|
<% wakatimeData.languages.slice(0, 5).forEach(lang => { %>| `<%= lang.name %>` | <%= lang.percent %>% | <%= lang.hours %> |
<% }); %>
<% } %>

## 🚀 Featured Project
### **[<%= spotlight.name %>](<%= spotlight.url %>)**
<%= spotlight.description %>

![<%= spotlight.language %>](https://img.shields.io/badge/<%= spotlight.language %>-informational?style=flat&logo=<%= spotlight.language.toLowerCase() %>)
![Stars](https://img.shields.io/badge/Stars-<%= spotlight.stars %>-yellow?style=flat)

## 📝 Recent Activity

<% if (recentActivity.recentRepos && recentActivity.recentRepos.length > 0) { %>
### 🔄 Recently Updated Repositories

<% recentActivity.recentRepos.forEach(repo => { %>
- **[<%= repo.name %>](https://github.com/<%= config.github.username %>/<%= repo.name %>)** - `<%= repo.language || 'Multiple Languages' %>`
<% }) %>

### 📊 Recent Contributions
- **<%= recentActivity.totalCommits %>** total commits across all repositories
- **<%= recentActivity.recentCommits.length %>** commits in the last 30 days
<% } %>

## 💻 Language Breakdown

### 📊 Most Used Languages

<% const sortedLanguages = Object.entries(languages).slice(0, 8).sort(([,a], [,b]) => parseFloat(b) - parseFloat(a)); %>
<% sortedLanguages.forEach(([lang, percentage]) => { %>
<%= generateTechBadge(lang) %> <%= generatePercentageBadge(lang, percentage) %>
<% }) %>

### 📈 Language Usage Stats

| Language | Percentage | Usage |
|:---------|-----------:|-------|
<% sortedLanguages.forEach(([lang, percentage]) => { %>| `<%= lang %>` | <%= percentage %>% | Primary language for <%= lang %> projects |
<% }); %>

## 🌐 Connect With Me

<% if (config.social.linkedin) { %>
[![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=flat&logo=linkedin&logoColor=white)](<%= config.social.linkedin %>)
<% } %>
<% if (config.social.github) { %>
[![GitHub](https://img.shields.io/badge/GitHub-100000?style=flat&logo=github&logoColor=white)](<%= config.social.github %>)
<% } %>
<% if (config.social.twitter) { %>
[![Twitter](https://img.shields.io/badge/Twitter-1DA1F2?style=flat&logo=twitter&logoColor=white)](<%= config.social.twitter %>)
<% } %>
<% if (config.social.website) { %>
[![Website](https://img.shields.io/badge/Website-000000?style=flat&logo=globe&logoColor=white)](<%= config.social.website %>)
<% } %>

---

<div align="center">

**Profile Views:** ![Visitor Count](https://komarev.com/ghpvc/?username=<%= config.github.username %>&color=blue)

*Last updated: <%= new Date().toLocaleString('en-US', { timeZone: 'UTC', year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' }) %> UTC*

> This profile README is automatically generated using [Profile Dynamo](https://github.com/vishals9711/profile-dynamo)

</div>

<!-- Proudly created with Profile Dynamo -->
