# 👋 Hi there! I'm @vishals9711

<div align="center">

## 🚀 About Me
<%= header.bio %>

### 📊 GitHub Statistics
![GitHub Stats](https://github-readme-stats.vercel.app/api?username=vishals9711&show_icons=true&theme=radical&include_all_commits=true&count_private=false)
![Top Languages](https://github-readme-stats.vercel.app/api/top-langs/?username=vishals9711&layout=compact&theme=radical&langs_count=6)
![GitHub Streak](https://github-readme-streak-stats.herokuapp.com/?user=vishals9711&theme=radical)

</div>

## 🛠️ Tech Stack
<% techStack.forEach(t => { %>
![<%= t %>](https://img.shields.io/badge/<%= t.replace(/ /g, '%20') %>-informational?style=flat&logo=<%= t.toLowerCase().replace(/[^a-z0-9]/g, '') %>) <% }) %>

## 📈 GitHub Analytics
| Metric | Value |
|--------|-------|
| 🌟 **Total Stars** | <%= stats.stars %> |
| 💻 **Total Commits** | <%= stats.commits %> |
| 🔀 **Pull Requests** | <%= stats.prs %> |
| 🐛 **Issues Created** | <%= stats.issues %> |
| 📁 **Repositories** | <%= stats.publicRepos %> |
| 👥 **Followers** | <%= stats.followers %> |
| 🎯 **Following** | <%= stats.following %> |
| 📊 **Total Contributions** | <%= stats.totalContributions %> |

<% if (wakatimeData) { %>
## ⚡ Recent Coding Activity (WakaTime)
⏰ **<%= wakatimeData.totalHours %> hours** of coding in the last 7 days

**Top Languages:**
<% wakatimeData.languages.forEach(lang => { %>
- **<%= lang.name %>**: <%= lang.percent %>% (<%= lang.hours %> hrs)
<% }) %>
<% } %>

## 🚀 Featured Project
### **[<%= spotlight.name %>](<%= spotlight.url %>)**
<%= spotlight.description %>

![<%= spotlight.language %>](https://img.shields.io/badge/<%= spotlight.language %>-informational?style=flat&logo=<%= spotlight.language.toLowerCase() %>)
![Stars](https://img.shields.io/badge/Stars-<%= spotlight.stars %>-yellow?style=flat)

## 📝 Recent Activity
<% if (recentActivity.recentRepos && recentActivity.recentRepos.length > 0) { %>
**Recently Updated Repositories:**
<% recentActivity.recentRepos.forEach(repo => { %>
- **[<%= repo.name %>](https://github.com/vishals9711/<%= repo.name %>)** - <%= repo.language || 'Multiple Languages' %>
<% }) %>
<% } %>

## 💻 Language Breakdown
| Language | Usage |
|----------|-------|
<% Object.entries(languages).slice(0, 8).forEach(([lang, percentage]) => { %>
| <%= lang %> | <%= percentage %>% |
<% }) %>

## 🌐 Connect With Me
[![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=flat&logo=linkedin&logoColor=white)](https://linkedin.com/in/vishals9711)
[![GitHub](https://img.shields.io/badge/GitHub-100000?style=flat&logo=github&logoColor=white)](https://github.com/vishals9711)

---

<div align="center">

**Profile Views:** ![Visitor Count](https://komarev.com/ghpvc/?username=vishals9711&color=blue)

*Last updated: <%= new Date().toLocaleString('en-US', { timeZone: 'UTC', year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' }) %> UTC*

> This profile README is automatically generated using [Profile Dynamo](https://github.com/vishals9711/profile-dynamo)

</div>

<!-- Proudly created with Profile Dynamo -->
