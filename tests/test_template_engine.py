"""
Unit tests for the TemplateEngine class.

Tests cover template loading, placeholder replacement, file operations,
and error handling scenarios.
"""

import os
import tempfile
import pytest
from unittest.mock import patch, mock_open
from scripts.template_engine import TemplateEngine


class TestTemplateEngine:
    """Test cases for TemplateEngine class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.template_engine = TemplateEngine()
        
    def test_init_default_template_path(self):
        """Test TemplateEngine initialization with default template path."""
        engine = TemplateEngine()
        assert engine.template_path == "README.template.md"
        
    def test_init_custom_template_path(self):
        """Test TemplateEngine initialization with custom template path."""
        custom_path = "custom_template.md"
        engine = TemplateEngine(custom_path)
        assert engine.template_path == custom_path
    
    def test_load_template_success(self):
        """Test successful template loading."""
        template_content = "# My Profile\n\nStats: {GITHUB_STATS}\nTime: {WAKATIME_STATS}"
        
        with patch("builtins.open", mock_open(read_data=template_content)):
            with patch("os.path.exists", return_value=True):
                result = self.template_engine.load_template()
                
        assert result == template_content
    
    def test_load_template_file_not_found(self):
        """Test template loading when file doesn't exist."""
        with patch("os.path.exists", return_value=False):
            with pytest.raises(FileNotFoundError, match="Template file not found"):
                self.template_engine.load_template()
    
    def test_load_template_io_error(self):
        """Test template loading with IO error."""
        with patch("os.path.exists", return_value=True):
            with patch("builtins.open", side_effect=IOError("Permission denied")):
                with pytest.raises(IOError, match="Error reading template file"):
                    self.template_engine.load_template()
    
    def test_populate_template_success(self):
        """Test successful template population with all placeholders."""
        template = "Hello {NAME}! You have {COUNT} repositories and {HOURS} coding hours."
        data = {
            "NAME": "John",
            "COUNT": "42",
            "HOURS": "120"
        }
        
        result = self.template_engine.populate_template(template, data)
        expected = "Hello John! You have 42 repositories and 120 coding hours."
        
        assert result == expected
    
    def test_populate_template_partial_data(self):
        """Test template population with missing placeholders."""
        template = "Stats: {GITHUB_STATS} and {WAKATIME_STATS} and {MISSING_DATA}"
        data = {
            "GITHUB_STATS": "100 contributions",
            "WAKATIME_STATS": "50 hours"
        }
        
        result = self.template_engine.populate_template(template, data)
        expected = "Stats: 100 contributions and 50 hours and {MISSING_DATA}"
        
        assert result == expected
    
    def test_populate_template_empty_template(self):
        """Test template population with empty template."""
        result = self.template_engine.populate_template("", {"KEY": "value"})
        assert result == ""
    
    def test_populate_template_empty_data(self):
        """Test template population with empty data."""
        template = "Hello {NAME}!"
        result = self.template_engine.populate_template(template, {})
        assert result == template
    
    def test_populate_template_no_placeholders(self):
        """Test template population with no placeholders in template."""
        template = "This is a plain template with no placeholders."
        data = {"KEY": "value"}
        
        result = self.template_engine.populate_template(template, data)
        assert result == template
    
    def test_save_readme_success(self):
        """Test successful README saving."""
        content = "# My Profile\n\nThis is my updated profile."
        
        with patch("builtins.open", mock_open()) as mock_file:
            with patch("os.path.exists", return_value=False):
                self.template_engine.save_readme(content)
                
        mock_file.assert_called_once_with("README.md", 'w', encoding='utf-8')
        mock_file().write.assert_called_once_with(content)
    
    def test_save_readme_custom_path(self):
        """Test README saving with custom output path."""
        content = "# Custom Profile"
        custom_path = "custom_readme.md"
        
        with patch("builtins.open", mock_open()) as mock_file:
            with patch("os.path.exists", return_value=False):
                self.template_engine.save_readme(content, custom_path)
                
        mock_file.assert_called_once_with(custom_path, 'w', encoding='utf-8')
    
    def test_save_readme_with_backup(self):
        """Test README saving creates backup of existing file."""
        content = "# New Profile"
        existing_content = "# Old Profile"
        
        with patch("builtins.open", mock_open(read_data=existing_content)) as mock_file:
            with patch("os.path.exists", return_value=True):
                self.template_engine.save_readme(content)
        
        # Should open files for reading existing, writing backup, and writing new
        assert mock_file.call_count >= 2
    
    def test_save_readme_io_error(self):
        """Test README saving with IO error."""
        content = "# Profile"
        
        with patch("os.path.exists", return_value=False):
            with patch("builtins.open", side_effect=IOError("Permission denied")):
                with pytest.raises(IOError, match="Error writing README file"):
                    self.template_engine.save_readme(content)
    
    def test_save_readme_empty_content(self):
        """Test README saving with empty content."""
        with patch("builtins.open", mock_open()) as mock_file:
            with patch("os.path.exists", return_value=False):
                self.template_engine.save_readme("")
                
        mock_file().write.assert_called_once_with("")
    
    def test_process_template_success(self):
        """Test complete template processing workflow."""
        template_content = "Profile: {NAME}\nStats: {STATS}"
        data = {"NAME": "John", "STATS": "Active"}
        expected_content = "Profile: John\nStats: Active"
        
        with patch.object(self.template_engine, 'load_template', return_value=template_content):
            with patch.object(self.template_engine, 'save_readme') as mock_save:
                self.template_engine.process_template(data)
                
        mock_save.assert_called_once_with(expected_content, "README.md")
    
    def test_process_template_with_custom_output(self):
        """Test complete template processing with custom output path."""
        template_content = "Profile: {NAME}"
        data = {"NAME": "John"}
        custom_output = "custom_output.md"
        
        with patch.object(self.template_engine, 'load_template', return_value=template_content):
            with patch.object(self.template_engine, 'save_readme') as mock_save:
                self.template_engine.process_template(data, custom_output)
                
        mock_save.assert_called_once_with("Profile: John", custom_output)
    
    def test_process_template_load_error(self):
        """Test template processing when loading fails."""
        data = {"KEY": "value"}
        
        with patch.object(self.template_engine, 'load_template', side_effect=FileNotFoundError("Template not found")):
            with pytest.raises(FileNotFoundError):
                self.template_engine.process_template(data)
    
    def test_process_template_save_error(self):
        """Test template processing when saving fails."""
        template_content = "Profile: {NAME}"
        data = {"NAME": "John"}
        
        with patch.object(self.template_engine, 'load_template', return_value=template_content):
            with patch.object(self.template_engine, 'save_readme', side_effect=IOError("Write failed")):
                with pytest.raises(IOError):
                    self.template_engine.process_template(data)


class TestTemplateEngineIntegration:
    """Integration tests using real files."""
    
    def test_real_file_operations(self):
        """Test template engine with real file operations."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create template file
            template_path = os.path.join(temp_dir, "test_template.md")
            template_content = "# {TITLE}\n\nStats: {STATS}\nTime: {TIME}"
            
            with open(template_path, 'w', encoding='utf-8') as f:
                f.write(template_content)
            
            # Create template engine
            engine = TemplateEngine(template_path)
            
            # Process template
            data = {
                "TITLE": "My Profile",
                "STATS": "100 contributions",
                "TIME": "50 hours"
            }
            
            output_path = os.path.join(temp_dir, "output.md")
            engine.process_template(data, output_path)
            
            # Verify output
            with open(output_path, 'r', encoding='utf-8') as f:
                result = f.read()
            
            expected = "# My Profile\n\nStats: 100 contributions\nTime: 50 hours"
            assert result == expected
    
    def test_backup_creation(self):
        """Test that backup is created when overwriting existing file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create template
            template_path = os.path.join(temp_dir, "template.md")
            with open(template_path, 'w') as f:
                f.write("New content: {DATA}")
            
            # Create existing README
            readme_path = os.path.join(temp_dir, "README.md")
            original_content = "Original README content"
            with open(readme_path, 'w') as f:
                f.write(original_content)
            
            # Process template
            engine = TemplateEngine(template_path)
            engine.process_template({"DATA": "updated"}, readme_path)
            
            # Check backup was created
            backup_path = f"{readme_path}.backup"
            assert os.path.exists(backup_path)
            
            with open(backup_path, 'r') as f:
                backup_content = f.read()
            assert backup_content == original_content
            
            # Check new content
            with open(readme_path, 'r') as f:
                new_content = f.read()
            assert new_content == "New content: updated"