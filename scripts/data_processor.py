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
        
        # Create comprehensive Wakatime summary
        wakatime_summary = (
            f"{wakatime_processed['total_coding_time']}\n\n"
            f"**Top Languages:**\n```\n{wakatime_processed['wakatime_languages']}\n```\n\n"
            f"**Editors:**\n{wakatime_processed['editors']}\n\n"
            f"**Operating Systems:**\n{wakatime_processed['operating_systems']}"
        )
        
        # Use Wakatime languages for the main language chart, fallback to GitHub
        language_chart = wakatime_processed.get('wakatime_languages', github_processed['github_languages'])
        
        return ProcessedData(
            wakatime_summary=wakatime_summary,
            language_chart=language_chart,
            contribution_summary=github_processed['contribution_stats'],
            pinned_repos_list=github_processed['pinned_repos'],
            last_updated=datetime.now().strftime("%B %d, %Y at %H:%M UTC")
        )