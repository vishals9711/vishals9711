# Requirements Document

## Introduction

Profile Dynamo is a fully automated system that generates a dynamic and up-to-date GitHub profile README. The system uses a custom script orchestrated by GitHub Actions workflow to fetch data from various APIs (GitHub, Wakatime), process it into formatted content, and automatically update the profile README with current statistics and activity summaries.

## Requirements

### Requirement 1: Repository Structure and Environment Setup

**User Story:** As a developer, I want to set up a secure and organized foundation for the automation system, so that I can manage templates, scripts, and sensitive data properly.

#### Acceptance Criteria

1. WHEN the system is initialized THEN it SHALL create a README.template.md file in the repository root
2. WHEN the system is initialized THEN it SHALL create a scripts/ directory for automation scripts
3. WHEN secrets are configured THEN the system SHALL store WAKATIME_API_KEY securely in GitHub repository secrets
4. WHEN secrets are configured THEN the system SHALL store GH_TOKEN with repo and user scopes in GitHub repository secrets
5. WHEN the template is created THEN it SHALL contain unique placeholders for dynamic content (e.g., {WAKATIME_STATS}, {GITHUB_LANGUAGES})

### Requirement 2: Automated Workflow Orchestration

**User Story:** As a developer, I want the profile update to run automatically on a schedule, so that my README stays current without manual intervention.

#### Acceptance Criteria

1. WHEN the workflow is configured THEN it SHALL trigger every Sunday at 05:00 UTC using cron schedule
2. WHEN the workflow runs THEN it SHALL check out the repository code successfully
3. WHEN the workflow runs THEN it SHALL set up the Python 3.10 environment
4. WHEN the script executes THEN it SHALL receive API keys as secure environment variables
5. WHEN README.md changes THEN the workflow SHALL automatically commit the updated file to main branch
6. IF the script fails THEN the workflow SHALL handle errors gracefully without breaking the repository

### Requirement 3: GitHub Data Integration

**User Story:** As a profile viewer, I want to see accurate and current GitHub statistics, so that I can understand the developer's recent activity and technical focus areas.

#### Acceptance Criteria

1. WHEN the script runs THEN it SHALL authenticate with GitHub GraphQL API using the GH_TOKEN
2. WHEN fetching GitHub data THEN it SHALL retrieve total contributions, pull requests, and issues for the current year
3. WHEN fetching repository data THEN it SHALL get details for the user's top 5 pinned repositories
4. WHEN analyzing languages THEN it SHALL fetch and aggregate the top programming languages used across repositories
5. WHEN GitHub API is unavailable THEN it SHALL handle failures gracefully with fallback content
6. WHEN rate limits are encountered THEN it SHALL respect GitHub API rate limiting

### Requirement 4: Wakatime Activity Integration

**User Story:** As a profile viewer, I want to see a summary of the developer's recent coding activity, so that I know what technologies they are actively using.

#### Acceptance Criteria

1. WHEN the script runs THEN it SHALL authenticate with Wakatime API using the WAKATIME_API_KEY
2. WHEN fetching coding stats THEN it SHALL retrieve the user's activity summary for the last 7 days
3. WHEN processing Wakatime data THEN it SHALL include time spent per programming language
4. WHEN processing Wakatime data THEN it SHALL include editor and operating system usage statistics
5. WHEN Wakatime API is unavailable THEN it SHALL handle failures gracefully with fallback content

### Requirement 5: Data Processing and Visualization

**User Story:** As a developer, I want the raw API data transformed into engaging visual content, so that the README is clear, readable, and visually appealing.

#### Acceptance Criteria

1. WHEN processing time data THEN it SHALL convert seconds into "X hrs Y mins" format
2. WHEN displaying language statistics THEN it SHALL generate text-based bar charts for top 5 languages
3. WHEN formatting numbers THEN it SHALL add commas for readability (e.g., 1,234 contributions)
4. WHEN processing repository data THEN it SHALL format pinned repositories into clean Markdown lists
5. WHEN creating visualizations THEN it SHALL include percentages and visual progress bars using block characters
6. WHEN generating content THEN it SHALL ensure all output is valid Markdown syntax

### Requirement 6: Template Processing and README Generation

**User Story:** As a script, I want to populate the template with processed data and generate the final README, so that the profile displays current, formatted information.

#### Acceptance Criteria

1. WHEN generating README THEN it SHALL read the entire content of README.template.md successfully
2. WHEN populating template THEN it SHALL replace all placeholders with corresponding generated content
3. WHEN creating output THEN it SHALL write or overwrite README.md with the final populated content
4. WHEN API calls fail THEN it SHALL use fallback content instead of breaking the README
5. WHEN template placeholders are missing THEN it SHALL handle gracefully without corrupting the output
6. WHEN file operations fail THEN it SHALL log errors appropriately and maintain system stability

### Requirement 7: Error Handling and Reliability

**User Story:** As a developer, I want the system to be resilient to failures, so that temporary API issues don't break my profile or the automation workflow.

#### Acceptance Criteria

1. WHEN any API is unavailable THEN the system SHALL continue processing with fallback content
2. WHEN network timeouts occur THEN the system SHALL retry requests with exponential backoff
3. WHEN authentication fails THEN the system SHALL log clear error messages for debugging
4. WHEN file operations fail THEN the system SHALL preserve the existing README.md
5. WHEN the workflow encounters errors THEN it SHALL not commit broken or incomplete content
6. WHEN rate limits are hit THEN the system SHALL respect API limits and handle gracefully