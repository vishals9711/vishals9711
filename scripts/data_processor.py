"""
Data processing and formatting utilities for Profile Dynamo.

This module contains the DataProcessor class that transforms raw API data
into formatted, human-readable content for the README template.
"""

from typing import Dict, List, Any
from datetime import datetime
from scripts.models import GitHubStats, WakatimeStats, ProcessedData, LanguageTime


class DataProcessor:
    """Processes and formats raw API data into display-ready content."""
    
    def __init__(self):
        """Initialize the DataProcessor."""
        pass
    
    def format_time_duration(self, seconds: int) -> str:
        """
        Convert seconds into "X hrs Y mins" format.
        
        Args:
            seconds: Total seconds to convert
            
        Returns:
            Formatted time string (e.g., "5 hrs 30 mins", "45 mins", "2 hrs")
        """
        if seconds <= 0:
            return "0 mins"
        
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        
        if hours > 0 and minutes > 0:
            return f"{hours} hrs {minutes} mins"
        elif hours > 0:
            return f"{hours} hrs"
        else:
            return f"{minutes} mins"
    
    def format_number(self, number: int) -> str:
        """
        Add commas to numbers for readability.
        
        Args:
            number: Integer to format
            
        Returns:
            Formatted number string (e.g., "1,234", "567,890")
        """
        return f"{number:,}"
    
    def generate_language_bar_chart(self, languages: List[LanguageTime], max_languages: int = 5) -> str:
        """
        Generate text-based bar charts for programming languages.
        
        Args:
            languages: List of LanguageTime objects
            max_languages: Maximum number of languages to display
            
        Returns:
            Formatted bar chart as markdown string
        """
        if not languages:
            return "No language data available"
        
        # Sort languages by time spent (descending) and take top N
        sorted_languages = sorted(languages, key=lambda x: x.total_seconds, reverse=True)
        top_languages = sorted_languages[:max_languages]
        
        if not top_languages:
            return "No language data available"
        
        # Calculate the maximum time for scaling bars
        max_time = top_languages[0].total_seconds
        bar_width = 20  # Maximum bar width in characters
        
        chart_lines = []
        for lang in top_languages:
            # Calculate bar length proportional to time spent
            if max_time > 0:
                bar_length = int((lang.total_seconds / max_time) * bar_width)
            else:
                bar_length = 0
            
            # Create the bar using block characters
            filled_bar = "█" * bar_length
            empty_bar = "░" * (bar_width - bar_length)
            bar = filled_bar + empty_bar
            
            # Format the time duration
            time_str = self.format_time_duration(lang.total_seconds)
            
            # Create the line with language name, bar, percentage, and time
            line = f"{lang.name:<12} {bar} {lang.percentage:5.1f}% ({time_str})"
            chart_lines.append(line)
        
        return "\n".join(chart_lines)
    
    def process_github_data(self, github_stats: GitHubStats) -> Dict[str, str]:
        """
        Process GitHub statistics into formatted display content.
        
        Args:
            github_stats: GitHubStats object with raw GitHub data
            
        Returns:
            Dictionary with formatted GitHub content
        """
        processed = {}
        
        # Format contribution statistics
        contributions = self.format_number(github_stats.total_contributions)
        prs = self.format_number(github_stats.total_prs)
        issues = self.format_number(github_stats.total_issues)
        
        processed["contribution_stats"] = (
            f"📈 **{contributions}** contributions this year\n"
            f"🔀 **{prs}** pull requests opened\n"
            f"🐛 **{issues}** issues created"
        )
        
        # Format pinned repositories
        if github_stats.pinned_repos:
            repo_lines = []
            for repo in github_stats.pinned_repos:
                stars = self.format_number(repo.stars)
                line = (
                    f"- **[{repo.name}]({repo.url})** - {repo.description} "
                    f"({repo.primary_language}) ⭐ {stars}"
                )
                repo_lines.append(line)
            processed["pinned_repos"] = "\n".join(repo_lines)
        else:
            processed["pinned_repos"] = "No pinned repositories available"
        
        # Format top languages (convert dict to LanguageTime objects for consistency)
        if github_stats.top_languages:
            total_bytes = sum(github_stats.top_languages.values())
            language_times = []
            
            for lang, bytes_count in github_stats.top_languages.items():
                percentage = (bytes_count / total_bytes * 100) if total_bytes > 0 else 0
                # Convert bytes to a time-like representation for bar chart
                # This is a simplified approach - in reality, we'd use actual coding time
                lang_time = LanguageTime(
                    name=lang,
                    total_seconds=bytes_count,  # Using bytes as proxy for time
                    percentage=percentage
                )
                language_times.append(lang_time)
            
            processed["github_languages"] = self.generate_language_bar_chart(language_times)
        else:
            processed["github_languages"] = "No language data available"
        
        return processed
    
    def process_wakatime_data(self, wakatime_stats: WakatimeStats) -> Dict[str, str]:
        """
        Process Wakatime statistics into formatted display content.
        
        Args:
            wakatime_stats: WakatimeStats object with raw Wakatime data
            
        Returns:
            Dictionary with formatted Wakatime content
        """
        processed = {}
        
        # Format total coding time
        total_time = self.format_time_duration(wakatime_stats.total_seconds)
        processed["total_coding_time"] = f"⏱️ **{total_time}** coding time this week"
        
        # Format language statistics with bar chart
        if wakatime_stats.languages:
            processed["wakatime_languages"] = self.generate_language_bar_chart(wakatime_stats.languages)
        else:
            processed["wakatime_languages"] = "No language data available"
        
        # Format editor statistics
        if wakatime_stats.editors:
            editor_lines = []
            for editor in wakatime_stats.editors[:3]:  # Top 3 editors
                name = editor.get('name', 'Unknown')
                percentage = editor.get('percent', 0)
                time_seconds = editor.get('total_seconds', 0)
                time_str = self.format_time_duration(time_seconds)
                editor_lines.append(f"- **{name}**: {percentage:.1f}% ({time_str})")
            processed["editors"] = "\n".join(editor_lines)
        else:
            processed["editors"] = "No editor data available"
        
        # Format operating system statistics
        if wakatime_stats.operating_systems:
            os_lines = []
            for os_data in wakatime_stats.operating_systems[:3]:  # Top 3 OS
                name = os_data.get('name', 'Unknown')
                percentage = os_data.get('percent', 0)
                time_seconds = os_data.get('total_seconds', 0)
                time_str = self.format_time_duration(time_seconds)
                os_lines.append(f"- **{name}**: {percentage:.1f}% ({time_str})")
            processed["operating_systems"] = "\n".join(os_lines)
        else:
            processed["operating_systems"] = "No operating system data available"
        
        return processed
    
    def generate_comprehensive_wakatime_summary(self, wakatime_stats: WakatimeStats) -> str:
        """
        Generate a comprehensive Wakatime summary for the main section.
        
        Args:
            wakatime_stats: WakatimeStats object with raw Wakatime data
            
        Returns:
            Formatted comprehensive summary string
        """
        processed = self.process_wakatime_data(wakatime_stats)
        
        summary_lines = [
            f"📊 **Coding Activity (Last 7 Days)**",
            "",
            processed["total_coding_time"],
            "",
            "**Top Languages:**",
            "```",
            processed["wakatime_languages"],
            "```",
            "",
            "**Editors:**",
            processed["editors"],
            "",
            "**Operating Systems:**",
            processed["operating_systems"]
        ]
        
        return "\n".join(summary_lines)
    
    def generate_dynamic_tech_stack(self, github_stats: GitHubStats, wakatime_stats: WakatimeStats) -> str:
        """
        Generate a dynamic tech stack based on actual usage data.
        
        Args:
            github_stats: GitHubStats object with GitHub data
            wakatime_stats: WakatimeStats object with Wakatime data
            
        Returns:
            Formatted tech stack badges string
        """
        # Base tech stack badges (always included)
        base_badges = [
            "![JavaScript](https://img.shields.io/badge/javascript-%23323330.svg?style=for-the-badge&logo=javascript&logoColor=%23F7DF1E)",
            "![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)",
            "![TypeScript](https://img.shields.io/badge/typescript-%23007ACC.svg?style=for-the-badge&logo=typescript&logoColor=white)",
            "![HTML5](https://img.shields.io/badge/html5-%23E34F26.svg?style=for-the-badge&logo=html5&logoColor=white)"
        ]
        
        # Dynamic badges based on actual usage
        dynamic_badges = []
        
        # Add badges based on GitHub languages
        if github_stats and github_stats.top_languages:
            github_langs = github_stats.top_languages.keys()
            lang_badge_map = {
                'JavaScript': "![JavaScript](https://img.shields.io/badge/javascript-%23323330.svg?style=for-the-badge&logo=javascript&logoColor=%23F7DF1E)",
                'Python': "![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)",
                'TypeScript': "![TypeScript](https://img.shields.io/badge/typescript-%23007ACC.svg?style=for-the-badge&logo=typescript&logoColor=white)",
                'Java': "![Java](https://img.shields.io/badge/java-%23ED8B00.svg?style=for-the-badge&logo=openjdk&logoColor=white)",
                'Go': "![Go](https://img.shields.io/badge/go-%2300ADD8.svg?style=for-the-badge&logo=go&logoColor=white)",
                'Rust': "![Rust](https://img.shields.io/badge/rust-%23000000.svg?style=for-the-badge&logo=rust&logoColor=white)",
                'C++': "![C++](https://img.shields.io/badge/c++-%2300599C.svg?style=for-the-badge&logo=c%2B%2B&logoColor=white)",
                'C#': "![C#](https://img.shields.io/badge/c%23-%23239120.svg?style=for-the-badge&logo=c-sharp&logoColor=white)"
            }
            
            for lang in github_langs:
                if lang in lang_badge_map and lang_badge_map[lang] not in base_badges:
                    dynamic_badges.append(lang_badge_map[lang])
        
        # Add badges based on Wakatime languages
        if wakatime_stats and wakatime_stats.languages:
            wakatime_langs = [lang.name for lang in wakatime_stats.languages]
            for lang in wakatime_langs:
                if lang in lang_badge_map and lang_badge_map[lang] not in base_badges:
                    if lang_badge_map[lang] not in dynamic_badges:
                        dynamic_badges.append(lang_badge_map[lang])
        
        # Combine all badges
        all_badges = base_badges + dynamic_badges
        
        # Add framework and tool badges (these could be made dynamic too)
        framework_badges = [
            "![React](https://img.shields.io/badge/react-%2320232a.svg?style=for-the-badge&logo=react&logoColor=%2361DAFB)",
            "![NodeJS](https://img.shields.io/badge/node.js-6DA55F?style=for-the-badge&logo=node.js&logoColor=white)",
            "![Next JS](https://img.shields.io/badge/Next-black?style=for-the-badge&logo=next.js&logoColor=white)",
            "![Express.js](https://img.shields.io/badge/express.js-%23404d59.svg?style=for-the-badge&logo=express&logoColor=%2361DAFB)",
            "![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)",
            "![Flask](https://img.shields.io/badge/flask-%23000.svg?style=for-the-badge&logo=flask&logoColor=white)"
        ]
        
        cloud_badges = [
            "![AWS](https://img.shields.io/badge/AWS-%23FF9900.svg?style=for-the-badge&logo=amazon-aws&logoColor=white)",
            "![Google Cloud](https://img.shields.io/badge/GoogleCloud-%234285F4.svg?style=for-the-badge&logo=google-cloud&logoColor=white)",
            "![DigitalOcean](https://img.shields.io/badge/DigitalOcean-%230167ff.svg?style=for-the-badge&logo=digitalOcean&logoColor=white)"
        ]
        
        database_badges = [
            "![MongoDB](https://img.shields.io/badge/MongoDB-%234ea94b.svg?style=for-the-badge&logo=mongodb&logoColor=white)",
            "![Redis](https://img.shields.io/badge/redis-%23DD0031.svg?style=for-the-badge&logo=redis&logoColor=white)",
            "![SQLite](https://img.shields.io/badge/sqlite-%2307405e.svg?style=for-the-badge&logo=sqlite&logoColor=white)"
        ]
        
        all_badges.extend(framework_badges)
        all_badges.extend(cloud_badges)
        all_badges.extend(database_badges)
        
        return " ".join(all_badges)
    
    def generate_dynamic_github_stats_urls(self, username: str) -> Dict[str, str]:
        """
        Generate dynamic GitHub stats URLs with customizable parameters.
        
        Args:
            username: GitHub username
            
        Returns:
            Dictionary with different types of GitHub stats URLs
        """
        base_params = {
            'username': username,
            'theme': 'dark',
            'hide_border': 'false',
            'include_all_commits': 'false',
            'count_private': 'false'
        }
        
        # GitHub stats card
        stats_params = base_params.copy()
        stats_params.update({
            'show_icons': 'true',
            'rank_icon': 'github'
        })
        stats_url = f"https://github-readme-stats.vercel.app/api?{'&'.join([f'{k}={v}' for k, v in stats_params.items()])}"
        
        # GitHub streak stats
        streak_url = f"https://github-readme-streak-stats.herokuapp.com/?user={username}&theme=dark&hide_border=false"
        
        # Top languages
        langs_params = base_params.copy()
        langs_params.update({
            'layout': 'compact',
            'langs_count': '8'
        })
        langs_url = f"https://github-readme-stats.vercel.app/api/top-langs/?{'&'.join([f'{k}={v}' for k, v in langs_params.items()])}"
        
        # GitHub trophies
        trophies_url = f"https://github-profile-trophy.vercel.app/?username={username}&theme=radical&no-frame=false&no-bg=true&margin-w=4"
        
        return {
            'stats_card': stats_url,
            'streak_stats': streak_url,
            'top_languages': langs_url,
            'trophies': trophies_url
        }
    
    def generate_dynamic_social_links(self, social_data: Dict[str, str]) -> str:
        """
        Generate dynamic social media links based on provided data.
        
        Args:
            social_data: Dictionary with social platform names and URLs
            
        Returns:
            Formatted social links string
        """
        social_badges = {
            'linkedin': '[![LinkedIn](https://img.shields.io/badge/LinkedIn-%230077B5.svg?logo=linkedin&logoColor=white)]({url})',
            'twitter': '[![Twitter](https://img.shields.io/badge/Twitter-%231DA1F2.svg?logo=Twitter&logoColor=white)]({url})',
            'github': '[![GitHub](https://img.shields.io/badge/GitHub-%23121011.svg?logo=github&logoColor=white)]({url})',
            'email': '[![Email](https://img.shields.io/badge/Email-D14836?logo=gmail&logoColor=white)](mailto:{url})',
            'website': '[![Website](https://img.shields.io/badge/Website-000000?logo=About.me&logoColor=white)]({url})',
            'medium': '[![Medium](https://img.shields.io/badge/Medium-12100E?logo=medium&logoColor=white)]({url})',
            'dev': '[![Dev.to](https://img.shields.io/badge/dev.to-0A0A0A?logo=dev.to&logoColor=white)]({url})',
            'stackoverflow': '[![Stack Overflow](https://img.shields.io/badge/-Stackoverflow-FE7A16?logo=stack-overflow&logoColor=white)]({url})'
        }
        
        formatted_links = []
        for platform, url in social_data.items():
            if platform.lower() in social_badges and url:
                formatted_links.append(social_badges[platform.lower()].format(url=url))
        
        return " ".join(formatted_links)
    
    def generate_activity_summary(self, github_stats: GitHubStats, wakatime_stats: WakatimeStats) -> str:
        """
        Generate a creative activity summary combining GitHub and Wakatime data.
        
        Args:
            github_stats: GitHubStats object with GitHub data
            wakatime_stats: WakatimeStats object with Wakatime data
            
        Returns:
            Formatted activity summary string
        """
        summary_parts = []
        
        # GitHub activity insights
        if github_stats:
            if github_stats.total_contributions > 0:
                summary_parts.append(f"🔥 **{self.format_number(github_stats.total_contributions)}** contributions this year")
            
            if github_stats.total_prs > 0:
                summary_parts.append(f"🔀 **{self.format_number(github_stats.total_prs)}** pull requests opened")
            
            if github_stats.total_issues > 0:
                summary_parts.append(f"🐛 **{self.format_number(github_stats.total_issues)}** issues created")
        
        # Wakatime insights
        if wakatime_stats and wakatime_stats.total_seconds > 0:
            total_time = self.format_time_duration(wakatime_stats.total_seconds)
            summary_parts.append(f"⏱️ **{total_time}** coding time this week")
            
            if wakatime_stats.languages:
                top_lang = wakatime_stats.languages[0].name if wakatime_stats.languages else "Unknown"
                summary_parts.append(f"💻 **{top_lang}** is my current favorite language")
        
        if not summary_parts:
            return "🚀 **Building amazing things** - Check back soon for updates!"
        
        return "\n".join(summary_parts)
    
    def generate_dynamic_about_section(self, github_stats: GitHubStats, wakatime_stats: WakatimeStats) -> str:
        """
        Generate a dynamic about section based on actual coding activity.
        
        Args:
            github_stats: GitHubStats object with GitHub data
            wakatime_stats: WakatimeStats object with Wakatime data
            
        Returns:
            Formatted about section string
        """
        about_parts = ["Software Engineer @ TNM"]
        
        # Add dynamic insights based on activity
        if github_stats and github_stats.total_contributions > 100:
            about_parts.append("🚀 Passionate about open source")
        
        if wakatime_stats and wakatime_stats.total_seconds > 3600:  # More than 1 hour
            about_parts.append("💻 Coding enthusiast")
        
        if github_stats and github_stats.total_prs > 10:
            about_parts.append("🔧 Always improving")
        
        # Add current focus language
        if wakatime_stats and wakatime_stats.languages:
            top_lang = wakatime_stats.languages[0].name
            about_parts.append(f"🎯 Currently focused on {top_lang}")
        
        return " | ".join(about_parts)
    
    def generate_fun_facts(self, github_stats: GitHubStats, wakatime_stats: WakatimeStats) -> str:
        """
        Generate fun facts about coding activity.
        
        Args:
            github_stats: GitHubStats object with GitHub data
            wakatime_stats: WakatimeStats object with Wakatime data
            
        Returns:
            Formatted fun facts string
        """
        facts = []
        
        if github_stats:
            if github_stats.total_contributions > 365:
                facts.append("🔥 More than 1 contribution per day this year!")
            
            if github_stats.total_prs > 50:
                facts.append("🚀 Prolific contributor to open source")
            
            if github_stats.total_issues > 20:
                facts.append("🐛 Active bug hunter and problem solver")
        
        if wakatime_stats and wakatime_stats.total_seconds > 7200:  # More than 2 hours
            facts.append("⏰ Dedicated coder with consistent activity")
            
            if wakatime_stats.languages and len(wakatime_stats.languages) > 5:
                facts.append("🎨 Polyglot programmer")
        
        if not facts:
            facts.append("🌟 Building the future, one commit at a time")
        
        return " | ".join(facts)
    
    def generate_motivational_quote(self, github_stats: GitHubStats, wakatime_stats: WakatimeStats) -> str:
        """
        Generate motivational quotes based on coding activity.
        
        Args:
            github_stats: GitHubStats object with GitHub data
            wakatime_stats: WakatimeStats object with Wakatime data
            
        Returns:
            Motivational quote string
        """
        quotes = [
            "🚀 Code is poetry written in logic",
            "💡 Every bug is a feature waiting to be discovered",
            "⚡ Innovation happens at the intersection of creativity and code",
            "🎯 The best code is the code that solves real problems",
            "🌟 Turning coffee into code, one commit at a time",
            "🔧 Building tomorrow's solutions today",
            "💻 Code never lies, comments sometimes do",
            "🚀 From idea to implementation, one line at a time",
            "⚡ Debugging is like being a detective in a crime movie",
            "🎨 Code is art, and every developer is an artist"
        ]
        
        # Select quote based on activity patterns
        if github_stats and github_stats.total_contributions > 500:
            return quotes[0]  # High activity quote
        elif wakatime_stats and wakatime_stats.total_seconds > 10000:  # More than 2.7 hours
            return quotes[1]  # Dedicated coder quote
        elif github_stats and github_stats.total_prs > 20:
            return quotes[2]  # Collaborative quote
        else:
            import random
            return random.choice(quotes)
    
    def generate_coding_streak_message(self, github_stats: GitHubStats) -> str:
        """
        Generate a message about coding streaks and consistency.
        
        Args:
            github_stats: GitHubStats object with GitHub data
            
        Returns:
            Streak message string
        """
        if not github_stats or github_stats.total_contributions == 0:
            return "🌟 Ready to start my coding journey!"
        
        contributions = github_stats.total_contributions
        
        if contributions > 365:
            return f"🔥 On fire! {self.format_number(contributions)} contributions this year"
        elif contributions > 100:
            return f"🚀 Consistent coder with {self.format_number(contributions)} contributions"
        elif contributions > 50:
            return f"💪 Building momentum with {self.format_number(contributions)} contributions"
        else:
            return f"🌱 Growing my coding footprint with {self.format_number(contributions)} contributions"
    
    def create_processed_data(self, github_stats: GitHubStats, wakatime_stats: WakatimeStats) -> ProcessedData:
        """
        Create a ProcessedData object with all formatted content.
        
        Args:
            github_stats: GitHubStats object with raw GitHub data
            wakatime_stats: WakatimeStats object with raw Wakatime data
            
        Returns:
            ProcessedData object with all formatted content
        """
        github_processed = self.process_github_data(github_stats)
        wakatime_processed = self.process_wakatime_data(wakatime_stats)
        
        # Create comprehensive Wakatime summary using the new method
        wakatime_summary = self.generate_comprehensive_wakatime_summary(wakatime_stats)
        
        # Use Wakatime languages for the main language chart, fallback to GitHub
        language_chart = wakatime_processed.get('wakatime_languages', github_processed['github_languages'])
        
        return ProcessedData(
            wakatime_summary=wakatime_summary,
            language_chart=language_chart,
            contribution_summary=github_processed['contribution_stats'],
            pinned_repos_list=github_processed['pinned_repos'],
            last_updated=datetime.now().strftime("%B %d, %Y at %H:%M UTC")
        )
