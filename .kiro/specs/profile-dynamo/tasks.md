# Implementation Plan

- [x] 1. Set up project structure and core configuration files
  - Create directory structure for scripts, tests, and configuration
  - Create pyproject.toml with UV configuration and necessary Python dependencies
  - Create README.template.md with placeholder structure
  - _Requirements: 1.1, 1.2_

- [x] 2. Implement GitHub Actions workflow
  - Create .github/workflows/profile-update.yml with cron schedule
  - Configure workflow to install UV and set up Python environment
  - Add steps to install dependencies with UV and execute main script
  - Implement git auto-commit functionality for README updates
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6_

- [x] 3. Create core data models and interfaces
  - Implement GitHubStats, PinnedRepository, WakatimeStats, and LanguageTime dataclasses
  - Create ProcessedData dataclass for formatted content
  - Define APIError and RateLimitError exception classes
  - _Requirements: 3.1, 3.2, 7.3_

- [x] 4. Implement basic GitHub API client
  - Create GitHubClient class with GraphQL query functionality
  - Implement fetch_profile_stats method to get contributions, PRs, and issues
  - Implement fetch_pinned_repositories method to get top 5 pinned repos
  - Implement fetch_language_stats method to aggregate language usage
  - Add basic authentication and simple error handling
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6_

- [x] 5. Implement basic Wakatime API client
  - Create WakatimeClient class with REST API functionality
  - Implement fetch_coding_stats method for last 7 days activity
  - Add authentication using API key and basic error handling
  - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5_

- [x] 6. Create data processing and formatting utilities
  - Implement DataProcessor class with formatting methods
  - Create format_time_duration method to convert seconds to "X hrs Y mins"
  - Implement generate_language_bar_chart method with text-based progress bars
  - Create format_number method to add commas for readability
  - Add methods to process GitHub and Wakatime data into display format
  - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6_

- [x] 7. Implement template engine
  - Create TemplateEngine class for template loading and processing
  - Implement load_template method to read README.template.md
  - Create populate_template method to replace placeholders with processed data
  - Implement save_readme method to write final README.md
  - Add error handling for file operations and missing placeholders
  - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 6.6_

- [x] 8. Create main profile updater script
  - Implement ProfileUpdater class as central coordinator
  - Create run method that orchestrates the entire update process
  - Implement _fetch_all_data method to collect data from all APIs
  - Create _process_data method to transform raw data into formatted content
  - Implement _generate_readme method to create final README file
  - Add basic error handling to prevent crashes
  - _Requirements: 6.1, 6.2, 6.3, 6.4_

- [x] 9. Test and validate basic functionality
  - Create simple test script to verify API connections work
  - Test template processing with sample data
  - Validate that README generation works end-to-end
  - Test GitHub Actions workflow in repository
  - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 6.6_

- [-] 10. Add robust error handling and retry logic
  - Create with_retry decorator for API calls with exponential backoff
  - Implement fallback content dictionary for when APIs fail
  - Add comprehensive logging for debugging and monitoring
  - Create error handling that preserves existing README on failures
  - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5, 7.6_

- [ ] 11. Write comprehensive unit tests
  - Create test files for GitHubClient with mocked API responses
  - Implement tests for WakatimeClient with various response scenarios
  - Write tests for DataProcessor formatting methods with edge cases
  - Create tests for TemplateEngine with different template scenarios
  - Add tests for error handling and retry logic
  - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5, 7.6_

- [ ] 12. Add configuration and documentation
  - Create configuration file for customizable settings (API endpoints, timeouts)
  - Add comprehensive docstrings to all classes and methods
  - Create setup instructions for repository secrets configuration
  - Add troubleshooting guide for common issues
  - Document template placeholder format and customization options
  - _Requirements: 1.3, 1.4, 1.5, 7.3_