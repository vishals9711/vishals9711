"""
Unit tests for the DataProcessor class.

Tests all formatting methods and data processing functionality.
"""

import pytest
from datetime import datetime
from scripts.data_processor import DataProcessor
from scripts.models import GitHubStats, WakatimeStats, LanguageTime, PinnedRepository


class TestDataProcessor:
    """Test cases for DataProcessor class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.processor = DataProcessor()
    
    def test_format_time_duration_hours_and_minutes(self):
        """Test formatting time with both hours and minutes."""
        result = self.processor.format_time_duration(7830)  # 2 hours 10 minutes 30 seconds
        assert result == "2 hrs 10 mins"
    
    def test_format_time_duration_hours_only(self):
        """Test formatting time with only hours."""
        result = self.processor.format_time_duration(7200)  # 2 hours exactly
        assert result == "2 hrs"
    
    def test_format_time_duration_minutes_only(self):
        """Test formatting time with only minutes."""
        result = self.processor.format_time_duration(1800)  # 30 minutes
        assert result == "30 mins"
    
    def test_format_time_duration_zero(self):
        """Test formatting zero time."""
        result = self.processor.format_time_duration(0)
        assert result == "0 mins"
    
    def test_format_time_duration_negative(self):
        """Test formatting negative time."""
        result = self.processor.format_time_duration(-100)
        assert result == "0 mins"
    
    def test_format_number_with_commas(self):
        """Test number formatting with commas."""
        assert self.processor.format_number(1234) == "1,234"
        assert self.processor.format_number(1234567) == "1,234,567"
        assert self.processor.format_number(123) == "123"
        assert self.processor.format_number(0) == "0"
    
    def test_generate_language_bar_chart_normal(self):
        """Test generating language bar chart with normal data."""
        languages = [
            LanguageTime("Python", 7200, 40.0),
            LanguageTime("JavaScript", 5400, 30.0),
            LanguageTime("TypeScript", 3600, 20.0),
            LanguageTime("Go", 1800, 10.0)
        ]
        
        result = self.processor.generate_language_bar_chart(languages)
        
        # Check that all languages are included
        assert "Python" in result
        assert "JavaScript" in result
        assert "TypeScript" in result
        assert "Go" in result
        
        # Check that percentages are included
        assert "40.0%" in result
        assert "30.0%" in result
        assert "20.0%" in result
        assert "10.0%" in result
        
        # Check that time durations are included
        assert "2 hrs" in result
        assert "1 hrs 30 mins" in result
        assert "1 hrs" in result
        assert "30 mins" in result
        
        # Check that bars are present (using block characters)
        assert "█" in result
        assert "░" in result
    
    def test_generate_language_bar_chart_empty(self):
        """Test generating language bar chart with empty data."""
        result = self.processor.generate_language_bar_chart([])
        assert result == "No language data available"
    
    def test_generate_language_bar_chart_max_languages(self):
        """Test that bar chart respects max_languages parameter."""
        languages = [
            LanguageTime(f"Lang{i}", 1000 - i*100, 10.0) for i in range(10)
        ]
        
        result = self.processor.generate_language_bar_chart(languages, max_languages=3)
        lines = result.split('\n')
        assert len(lines) == 3
        assert "Lang0" in result
        assert "Lang1" in result
        assert "Lang2" in result
        assert "Lang3" not in result
    
    def test_process_github_data(self):
        """Test processing GitHub statistics."""
        pinned_repos = [
            PinnedRepository("repo1", "Description 1", "https://github.com/user/repo1", "Python", 100),
            PinnedRepository("repo2", "Description 2", "https://github.com/user/repo2", "JavaScript", 50)
        ]
        
        github_stats = GitHubStats(
            total_contributions=1234,
            total_prs=56,
            total_issues=78,
            pinned_repos=pinned_repos,
            top_languages={"Python": 5000, "JavaScript": 3000, "Go": 2000}
        )
        
        result = self.processor.process_github_data(github_stats)
        
        # Check contribution stats
        assert "1,234" in result["contribution_stats"]
        assert "56" in result["contribution_stats"]
        assert "78" in result["contribution_stats"]
        
        # Check pinned repos
        assert "repo1" in result["pinned_repos"]
        assert "repo2" in result["pinned_repos"]
        assert "Description 1" in result["pinned_repos"]
        assert "100" in result["pinned_repos"]
        
        # Check languages
        assert "Python" in result["github_languages"]
        assert "JavaScript" in result["github_languages"]
        assert "Go" in result["github_languages"]
    
    def test_process_github_data_empty_repos(self):
        """Test processing GitHub data with no pinned repositories."""
        github_stats = GitHubStats(
            total_contributions=100,
            total_prs=5,
            total_issues=3,
            pinned_repos=[],
            top_languages={"Python": 1000}
        )
        
        result = self.processor.process_github_data(github_stats)
        assert result["pinned_repos"] == "No pinned repositories available"
    
    def test_process_wakatime_data(self):
        """Test processing Wakatime statistics."""
        languages = [
            LanguageTime("Python", 7200, 60.0),
            LanguageTime("JavaScript", 4800, 40.0)
        ]
        
        editors = [
            {"name": "VS Code", "percent": 80.0, "total_seconds": 9600},
            {"name": "PyCharm", "percent": 20.0, "total_seconds": 2400}
        ]
        
        operating_systems = [
            {"name": "macOS", "percent": 100.0, "total_seconds": 12000}
        ]
        
        wakatime_stats = WakatimeStats(
            total_seconds=12000,
            languages=languages,
            editors=editors,
            operating_systems=operating_systems
        )
        
        result = self.processor.process_wakatime_data(wakatime_stats)
        
        # Check total coding time
        assert "3 hrs 20 mins" in result["total_coding_time"]
        
        # Check languages
        assert "Python" in result["wakatime_languages"]
        assert "JavaScript" in result["wakatime_languages"]
        
        # Check editors
        assert "VS Code" in result["editors"]
        assert "PyCharm" in result["editors"]
        assert "80.0%" in result["editors"]
        
        # Check operating systems
        assert "macOS" in result["operating_systems"]
        assert "100.0%" in result["operating_systems"]
    
    def test_process_wakatime_data_empty(self):
        """Test processing empty Wakatime data."""
        wakatime_stats = WakatimeStats(
            total_seconds=0,
            languages=[],
            editors=[],
            operating_systems=[]
        )
        
        result = self.processor.process_wakatime_data(wakatime_stats)
        
        assert result["wakatime_languages"] == "No language data available"
        assert result["editors"] == "No editor data available"
        assert result["operating_systems"] == "No operating system data available"
    
    def test_create_processed_data(self):
        """Test creating complete ProcessedData object."""
        # Create sample data
        pinned_repos = [
            PinnedRepository("test-repo", "Test description", "https://github.com/user/test-repo", "Python", 10)
        ]
        
        github_stats = GitHubStats(
            total_contributions=500,
            total_prs=25,
            total_issues=15,
            pinned_repos=pinned_repos,
            top_languages={"Python": 3000}
        )
        
        languages = [LanguageTime("Python", 3600, 100.0)]
        editors = [{"name": "VS Code", "percent": 100.0, "total_seconds": 3600}]
        operating_systems = [{"name": "macOS", "percent": 100.0, "total_seconds": 3600}]
        
        wakatime_stats = WakatimeStats(
            total_seconds=3600,
            languages=languages,
            editors=editors,
            operating_systems=operating_systems
        )
        
        result = self.processor.create_processed_data(github_stats, wakatime_stats)
        
        # Check that all fields are populated
        assert result.wakatime_summary
        assert result.language_chart
        assert result.contribution_summary
        assert result.pinned_repos_list
        assert result.last_updated
        
        # Check specific content
        assert "1 hrs" in result.wakatime_summary
        assert "Python" in result.language_chart
        assert "500" in result.contribution_summary
        assert "test-repo" in result.pinned_repos_list
        
        # Check that last_updated is a valid date string
        assert "2024" in result.last_updated or "2025" in result.last_updated
        assert "UTC" in result.last_updated
    
    def test_bar_chart_scaling(self):
        """Test that bar chart scales correctly."""
        languages = [
            LanguageTime("Python", 10000, 50.0),  # Should get full bar
            LanguageTime("JavaScript", 5000, 25.0),  # Should get half bar
            LanguageTime("Go", 2000, 10.0)  # Should get smaller bar
        ]
        
        result = self.processor.generate_language_bar_chart(languages)
        lines = result.split('\n')
        
        # Python should have the most filled blocks
        python_line = [line for line in lines if "Python" in line][0]
        js_line = [line for line in lines if "JavaScript" in line][0]
        go_line = [line for line in lines if "Go" in line][0]
        
        # Count filled blocks (█) in each line
        python_blocks = python_line.count("█")
        js_blocks = js_line.count("█")
        go_blocks = go_line.count("█")
        
        # Python should have more blocks than JavaScript, which should have more than Go
        assert python_blocks >= js_blocks >= go_blocks
        assert python_blocks > 0  # Should have at least some filled blocks