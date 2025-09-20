# 💫 About Me:
<%= header.bio %>

## 🌐 Socials:
[![LinkedIn](https://img.shields.io/badge/LinkedIn-%230077B5.svg?logo=linkedin&logoColor=white)](https://linkedin.com/in/vishals9711) 

# 💻 Tech Stack:
<% Object.keys(languages).forEach(t => { %>![<%= t %>](https://img.shields.io/badge/<%= t.replace(/ /g, '%20') %>-%23<%= Math.floor(Math.random()*16777215).toString(16) %>.svg?style=for-the-badge&logo=<%= t.toLowerCase().replace(/ /g, '') %>&logoColor=white) <% }) %>

# 📊 GitHub Stats:
| Key                | Value                |
| ------------------ | -------------------- |
| ⭐ Total Stars     | <%= stats.stars %>   |
| Commits            | <%= stats.commits %> |
| Pull Requests      | <%= stats.prs %>     |
| Issues             | <%= stats.issues %>  |
| Contributed to     | <%= stats.contributedTo %> |

## 🏆 GitHub Trophies
![Trophies](https://github-profile-trophy.vercel.app/?username=vishals9711&theme=radical&no-frame=false&no-bg=true&margin-w=4)

---

### 🚀 Project Spotlight

**[<%= spotlight.name %>](https://github.com/vishals9711/<%= spotlight.name %>)**

<%= spotlight.description || "An amazing project showcasing modern development practices and innovative solutions." %>

⭐ **<%= spotlight.stars %>** stars | 💻 **<%= spotlight.language %>** | 🔗 **[View Project](https://github.com/vishals9711/<%= spotlight.name %>)**

---

## 💻 Most Used Languages
| Language           | Percentage           |
| ------------------ | -------------------- |
<% for(let lang in languages) { %>
| <%= lang %>        | <%= languages[lang] %>% |
<% } %>

---

*Last updated: <%= new Date().toUTCString() %>*

> This profile README is automatically generated using [Profile Dynamo](https://github.com/vishals9711/profile-dynamo)

---
[![](https://visitcount.itsvg.in/api?id=vishals9711&icon=0&color=9)](https://visitcount.itsvg.in)

<!-- Proudly created with Profile Dynamo -->
