# Hi there, I'm Vishal 👋

<%= header.bio %>

---

### 📊 Dynamic Stats

| Contributions | Public Repos | Followers | Hours Coded |
|---|---|---|---|
| <%= stats.contributions %> | <%= stats.repos %> | <%= stats.followers %> | <%= Math.round(stats.codedHours) %> |

---

### 💻 My Tech Arsenal

<% tech.forEach(t => { %>
  <img src="https://img.shields.io/badge/-<%= t %>-black?style=flat-square&logo=<%= t.toLowerCase().replace(/ /g, '') %>" />
<% }) %>

---

### 🚀 Project Spotlight

**[<%= spotlight.name %>](https://github.com/vishals9711/<%= spotlight.name %>)**

<%= spotlight.description %>

⭐ <%= spotlight.stars %> | 💻 <%= spotlight.language %>

---

### 🏆 Achievements Unlocked

<% if (achievements.nightOwl) { %>🌙 Night Owl<% } %>
<% if (achievements.polyglot) { %>🗣️ Polyglot<% } %>
<% if (achievements.onFire) { %>🔥 On Fire<% } %>
<% if (achievements.ossChampion) { %>🎖️ Open Source Champion<% } %>

---
*Last updated: <%= new Date().toUTCString() %>*
