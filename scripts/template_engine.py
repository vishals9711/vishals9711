"""
Template engine for processing README templates with dynamic content.

This module provides the TemplateEngine class for loading README templates,
replacing placeholders with processed data, and generating the final README file.
"""

import os
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class TemplateEngine:
    """
    Handles template loading and placeholder replacement for README generation.
    
    The TemplateEngine reads a template file, replaces placeholders with processed
    data, and writes the final README.md file. It includes error handling for
    file operations and missing placeholders.
    """
    
    def __init__(self, template_path: str = "README.template.md"):
        """
        Initialize the TemplateEngine with a template file path.
        
        Args:
            template_path: Path to the template file (default: README.template.md)
        """
        self.template_path = template_path
        
    def load_template(self) -> str:
        """
        Load the template file content.
        
        Returns:
            str: The template file content
            
        Raises:
            FileNotFoundError: If the template file doesn't exist
            IOError: If there's an error reading the template file
        """
        try:
            if not os.path.exists(self.template_path):
                raise FileNotFoundError(f"Template file not found: {self.template_path}")
                
            with open(self.template_path, 'r', encoding='utf-8') as file:
                template_content = file.read()
                
            logger.info(f"Successfully loaded template from {self.template_path}")
            return template_content
            
        except FileNotFoundError:
            logger.error(f"Template file not found: {self.template_path}")
            raise
        except IOError as e:
            logger.error(f"Error reading template file {self.template_path}: {e}")
            raise IOError(f"Error reading template file {self.template_path}: {e}")
        except Exception as e:
            logger.error(f"Unexpected error loading template: {e}")
            raise IOError(f"Failed to load template: {e}")
    
    def populate_template(self, template: str, data: Dict[str, str]) -> str:
        """
        Replace placeholders in the template with processed data.
        
        Placeholders are expected to be in the format {PLACEHOLDER_NAME}.
        Missing placeholders are handled gracefully by leaving them unchanged
        and logging a warning.
        
        Args:
            template: The template string with placeholders
            data: Dictionary mapping placeholder names to replacement values
            
        Returns:
            str: The populated template with placeholders replaced
        """
        if not template:
            logger.warning("Empty template provided")
            return ""
            
        if not data:
            logger.warning("No data provided for template population")
            return template
            
        populated_content = template
        replaced_count = 0
        
        # Replace each placeholder with corresponding data
        for placeholder, value in data.items():
            placeholder_pattern = f"{{{placeholder}}}"
            if placeholder_pattern in populated_content:
                populated_content = populated_content.replace(placeholder_pattern, str(value))
                replaced_count += 1
                logger.debug(f"Replaced placeholder {placeholder_pattern}")
            else:
                logger.debug(f"Placeholder {placeholder_pattern} not found in template")
        
        # Check for any remaining unreplaced placeholders
        import re
        remaining_placeholders = re.findall(r'\{([^}]+)\}', populated_content)
        if remaining_placeholders:
            logger.warning(f"Unreplaced placeholders found: {remaining_placeholders}")
        
        logger.info(f"Template population completed. Replaced {replaced_count} placeholders")
        return populated_content
    
    def save_readme(self, content: str, output_path: str = "README.md") -> None:
        """
        Write the populated content to the README file.
        
        Args:
            content: The final README content to write
            output_path: Path where to save the README (default: README.md)
            
        Raises:
            IOError: If there's an error writing the file
        """
        if not content:
            logger.warning("Empty content provided for README generation")
            
        try:
            # Create backup of existing README if it exists
            if os.path.exists(output_path):
                backup_path = f"{output_path}.backup"
                try:
                    with open(output_path, 'r', encoding='utf-8') as existing:
                        existing_content = existing.read()
                    with open(backup_path, 'w', encoding='utf-8') as backup:
                        backup.write(existing_content)
                    logger.info(f"Created backup at {backup_path}")
                except Exception as e:
                    logger.warning(f"Could not create backup: {e}")
            
            # Write the new README content
            with open(output_path, 'w', encoding='utf-8') as file:
                file.write(content)
                
            logger.info(f"Successfully saved README to {output_path}")
            
        except IOError as e:
            logger.error(f"Error writing README file {output_path}: {e}")
            raise IOError(f"Error writing README file {output_path}: {e}")
        except Exception as e:
            logger.error(f"Unexpected error saving README: {e}")
            raise IOError(f"Failed to save README: {e}")
    
    def process_template(self, data: Dict[str, str], output_path: str = "README.md") -> None:
        """
        Complete template processing workflow: load, populate, and save.
        
        This is a convenience method that combines all template operations
        with comprehensive error handling.
        
        Args:
            data: Dictionary mapping placeholder names to replacement values
            output_path: Path where to save the final README (default: README.md)
            
        Raises:
            FileNotFoundError: If template file doesn't exist
            IOError: If there's an error with file operations
        """
        try:
            # Load template
            template_content = self.load_template()
            
            # Populate with data
            populated_content = self.populate_template(template_content, data)
            
            # Save final README
            self.save_readme(populated_content, output_path)
            
            logger.info("Template processing completed successfully")
            
        except Exception as e:
            logger.error(f"Template processing failed: {e}")
            raise