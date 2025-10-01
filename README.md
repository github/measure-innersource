# Measure InnerSource tool

This tool measures InnerSource collaboration in a given repository by analyzing issues, pull requests, and code contributions. It helps organizations track and improve their InnerSource adoption by quantifying the collaboration between different teams and departments.

## What is InnerSource?

InnerSource applies open source principles and practices to internal development. It involves teams contributing to projects owned by other teams within the same organization, fostering collaboration, knowledge sharing, and code reuse across organizational boundaries. See [the InnerSource Commons Foundation's site](https://innersourcecommons.org) for more details.

## How This Tool Works

The measure-innersource tool:

1. Identifies the original repository owner(s) and their organizational structure
2. Analyzes all contributors to the repository
3. Classifies contributors as either team members or InnerSource contributors (from outside the team responsible for the repository)
4. Counts contributions (commits, PRs, issues) from both groups
5. Calculates an InnerSource collaboration ratio
6. Generates a detailed Markdown report

### Organization Data

This tool requires an `org-data.json` file in the root of the repository that contains organizational hierarchy information. This file maps GitHub usernames to their managers, allowing the tool to determine team boundaries.

#### Basic org-data.json Schema

<details>
<summary>View basic org-data.json example</summary>

```json
{
  "username1": {
    "manager": "manager1"
  },
  "username2": {
    "manager": "manager1"
  },
  "username3": {
    "manager": "manager2"
  }
}
```

</details>

#### Schema Definition

The `org-data.json` file must follow this structure:

<details>
<summary>View schema definition</summary>

```typescript
interface OrgData {
  [username: string]: {
    manager: string;
  };
}
```

</details>

**Field Descriptions:**

- `username` (string): The GitHub username of the employee (case-sensitive)
- `manager` (string): The GitHub username of the employee's direct manager

#### Comprehensive org-data.json Examples

##### Small Team Structure

<details>
<summary>View Small Team Structure Example</summary>

```json
{
  "alice": {
    "manager": "teamlead1"
  },
  "bob": {
    "manager": "teamlead1"
  },
  "charlie": {
    "manager": "teamlead1"
  },
  "teamlead1": {
    "manager": "director1"
  },
  "director1": {
    "manager": "vp-engineering"
  }
}
```

</details>

##### Multi-Team Department Structure

<details>
<summary>View Multi-Team Department Structure Example</summary>

```json
{
  "frontend-dev1": {
    "manager": "frontend-lead"
  },
  "frontend-dev2": {
    "manager": "frontend-lead"
  },
  "backend-dev1": {
    "manager": "backend-lead"
  },
  "backend-dev2": {
    "manager": "backend-lead"
  },
  "backend-dev3": {
    "manager": "backend-lead"
  },
  "frontend-lead": {
    "manager": "engineering-manager"
  },
  "backend-lead": {
    "manager": "engineering-manager"
  },
  "engineering-manager": {
    "manager": "director-engineering"
  },
  "devops-engineer": {
    "manager": "infrastructure-lead"
  },
  "infrastructure-lead": {
    "manager": "director-engineering"
  },
  "director-engineering": {
    "manager": "vp-engineering"
  }
}
```

</details>

##### Matrix Organization Structure

<details>
<summary>View Matrix Organization Structure Example</summary>

```json
{
  "product-owner": {
    "manager": "product-director"
  },
  "ux-designer": {
    "manager": "design-lead"
  },
  "mobile-dev1": {
    "manager": "mobile-lead"
  },
  "mobile-dev2": {
    "manager": "mobile-lead"
  },
  "qa-engineer": {
    "manager": "qa-lead"
  },
  "mobile-lead": {
    "manager": "engineering-manager"
  },
  "qa-lead": {
    "manager": "engineering-manager"
  },
  "design-lead": {
    "manager": "design-director"
  },
  "engineering-manager": {
    "manager": "director-engineering"
  },
  "product-director": {
    "manager": "vp-product"
  },
  "design-director": {
    "manager": "vp-product"
  },
  "director-engineering": {
    "manager": "vp-engineering"
  }
}
```

</details>

#### Important Requirements

1. **All Contributors Must Be Included**: Every GitHub username that appears in the repository's contributor list must have an entry in org-data.json
2. **Manager Chain**: Managers should also be included in the org-data.json file with their own manager relationships
3. **Case Sensitivity**: GitHub usernames are case-sensitive and must match exactly
4. **JSON Validity**: The file must be valid JSON format
5. **UTF-8 Encoding**: The file should be saved with UTF-8 encoding

#### Validation Rules

- Each username key must be a valid GitHub username
- Each manager value must correspond to a GitHub username
- Circular management relationships are not recommended but won't break the tool
- Missing manager entries will be treated as top-level managers
- Bot accounts (containing "[bot]" in the username) are automatically excluded

#### Team Boundary Determination Algorithm

The tool determines team boundaries using this algorithm:

1. **Find Original Author**: Identify the author of the repository's first commit
2. **Identify Manager**: Look up the original author's manager in org-data.json
3. **Build Team List**: Include all users who:
   - Report directly to the same manager as the original author
   - Report to anyone already in the team (recursive relationship)
   - Are managers of anyone in the team
4. **Classify Contributors**: Any contributor not in the team list is considered an InnerSource contributor

**Overriding Team Determination**: You can override this algorithm by setting the `OWNING_TEAM` environment variable with a comma-separated list of GitHub usernames. When set, these users will be considered the owning team, and the algorithm above will be bypassed. This is useful when:
- The first commit author doesn't accurately represent the current owning team
- The org chart doesn't align with actual repository ownership
- You want to explicitly define team boundaries

Example:
```yaml
env:
  OWNING_TEAM: "alice,bob,charlie"
```

#### Example Team Boundary Calculation

<details>
<summary>View team boundary calculation example</summary>

Given this org-data.json:

```json
{
  "alice": { "manager": "teamlead" },
  "bob": { "manager": "teamlead" },
  "charlie": { "manager": "alice" },
  "teamlead": { "manager": "director" },
  "dave": { "manager": "otherlead" },
  "otherlead": { "manager": "director" }
}
```

If Alice created the repository:

- **Team Members**: alice, bob, charlie, teamlead (alice's manager), director (teamlead's manager)
- **InnerSource Contributors**: dave, otherlead (from different team branch)
</details>

#### Troubleshooting org-data.json

**Common Issues:**

1. **Username Mismatch**: Ensure GitHub usernames match exactly (case-sensitive)
2. **Missing Contributors**: All repository contributors must be in org-data.json
3. **Invalid JSON**: Validate JSON syntax using online validators
4. **Manager Loops**: Avoid circular manager relationships
5. **File Location**: Ensure org-data.json is in the repository root directory

## Architecture and Design

The InnerSource measurement tool follows a modular architecture designed for scalability, maintainability, and efficient processing of large repositories. For detailed architectural information, see [ARCHITECTURE.md](ARCHITECTURE.md).

### High-Level Architecture

```bash
┌─────────────────────────────────────────────────────────────────┐
│                    measure-innersource                           │
│                                                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────┐ │
│  │   config    │  │    auth     │  │ markdown_   │  │markdown_│ │
│  │             │  │             │  │  writer     │  │helpers  │ │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────┘ │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │           measure_innersource (Main Module)                 │ │
│  └─────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────┐
│                      GitHub API                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────┐ │
│  │ Repository  │  │   Commits   │  │Pull Requests│  │ Issues  │ │
│  │  Metadata   │  │             │  │             │  │         │ │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

### Key Design Principles

1. **Modular Architecture**: Separate concerns into distinct modules for better maintainability
2. **Chunked Processing**: Process large datasets in configurable chunks to prevent memory issues
3. **Multiple Authentication**: Support both PAT and GitHub App authentication for flexibility
4. **Graceful Error Handling**: Provide informative error messages and degrade gracefully
5. **Memory Efficiency**: Use lazy evaluation and streaming to handle large repositories

### Data Processing Pipeline

1. **Initialization**: Load configuration and authenticate to GitHub
2. **Repository Analysis**: Fetch metadata and organizational data
3. **Team Boundary Detection**: Determine repository ownership using org-data.json
4. **Contribution Analysis**: Process commits, PRs, and issues in chunks
5. **Metric Calculation**: Calculate InnerSource ratios and statistics
6. **Report Generation**: Create comprehensive Markdown reports

Below is an example of the generated InnerSource report:

<details>
<summary>View example InnerSource report</summary>

```markdown
# InnerSource Report

## Repository: octocat/hello-world

### InnerSource Ratio: 35.67%

### Original Commit Author: octocat (Manager: octoboss)

## Team Members that Own the Repo:

- octocat
- octoboss
- octodev1
- octodev2

## All Contributors:

- octocat
- octodev1
- octodev2
- contributor1
- contributor2

## Innersource Contributors:

- contributor1
- contributor2

## Innersource Contribution Counts:

- contributor1: 15 contributions
- contributor2: 8 contributions

## Team Member Contribution Counts:

- octocat: 25 contributions
- octodev1: 12 contributions
- octodev2: 5 contributions
```

</details>

## Support

If you need support using this project or have questions about it, please [open up an issue in this repository](https://github.com/github/measure-innersource/issues). Requests made directly to GitHub staff or support team will be redirected here to open an issue. GitHub SLA's and support/services contracts do not apply to this repository.

### OSPO GitHub Actions as a Whole

All feedback regarding our GitHub Actions, as a whole, should be communicated through [issues on our github-ospo repository](https://github.com/github/github-ospo/issues/new).

## Use as a GitHub Action

1. Create a repository to host this GitHub Action or select an existing repository. This is easiest with regards to permissions if it is the same repository as the one you want to measure innersource collaboration on.
2. **Create an org-data.json file** in the root of your repository with your organization structure as described above.
3. Copy the example below (in the next section) into your repository (from step 1) and into the proper directory for GitHub Actions: `.github/workflows/` directory with the file extension `.yml` (ie. `.github/workflows/measure-innersource.yml`)
4. Update the workflow file with the appropriate configuration options as described below. The required configuration options are `REPOSITORY`, `GH_APP_ID`, `GH_APP_INSTALLATION_ID`, and `GH_APP_PRIVATE_KEY` for GitHub App Installation authentication, or `REPOSITORY` and `GH_TOKEN` for Personal Access Token (PAT) authentication. The other configuration options are optional.
5. Commit the workflow file to the default branch (often `master` or `main`)
6. Wait for the action to trigger based on the `schedule` entry or manually trigger the workflow as shown in the [documentation](https://docs.github.com/en/actions/using-workflows/manually-running-a-workflow).

### Basic Workflow Example

Here's a simple example workflow file to get you started:

```yaml
name: Measure InnerSource Collaboration

on:
  schedule:
    - cron: "0 0 * * 0" # Run weekly on Sundays at midnight
  workflow_dispatch: # Allow manual triggers

jobs:
  measure-innersource:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Measure InnerSource
        uses: github/measure-innersource@v1
        env:
          REPOSITORY: "owner/repo"
          GH_TOKEN: ${{ secrets.GH_TOKEN }}
          REPORT_TITLE: "Weekly InnerSource Report"
          OUTPUT_FILE: "innersource_report.md"
```

### Advanced Workflow Examples

#### Using GitHub App Authentication

For enhanced security and higher rate limits, you can use GitHub App authentication:

```yaml
name: Measure InnerSource with GitHub App

on:
  schedule:
    - cron: "0 0 * * 0"
  workflow_dispatch:

jobs:
  measure-innersource:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Measure InnerSource
        uses: github/measure-innersource@v1
        env:
          REPOSITORY: "owner/repo"
          GH_APP_ID: ${{ secrets.APP_ID }}
          GH_APP_INSTALLATION_ID: ${{ secrets.APP_INSTALLATION_ID }}
          GH_APP_PRIVATE_KEY: ${{ secrets.APP_PRIVATE_KEY }}
          REPORT_TITLE: "Monthly InnerSource Analysis"
          OUTPUT_FILE: "monthly_innersource_report.md"
          CHUNK_SIZE: "200"
```

#### GitHub Enterprise Server Configuration

For GitHub Enterprise Server installations:

```yaml
name: Measure InnerSource on GitHub Enterprise

on:
  schedule:
    - cron: "0 8 * * 1" # Run Monday mornings
  workflow_dispatch:

jobs:
  measure-innersource:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Measure InnerSource
        uses: github/measure-innersource@v1
        env:
          REPOSITORY: "internal-org/critical-service"
          GH_TOKEN: ${{ secrets.GHE_TOKEN }}
          GH_ENTERPRISE_URL: "https://github.company.com"
          REPORT_TITLE: "Internal Service InnerSource Report"
          OUTPUT_FILE: "internal_service_report.md"
          CHUNK_SIZE: "150"
```

#### High-Volume Repository Configuration

For large repositories with many contributors:

```yaml
name: Measure InnerSource for Large Repository

on:
  schedule:
    - cron: "0 2 * * 6" # Run Saturday nights to avoid peak hours
  workflow_dispatch:

jobs:
  measure-innersource:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Measure InnerSource
        uses: github/measure-innersource@v1
        env:
          REPOSITORY: "bigcorp/massive-monorepo"
          GH_TOKEN: ${{ secrets.GH_TOKEN }}
          REPORT_TITLE: "Large Repository InnerSource Analysis"
          OUTPUT_FILE: "large_repo_analysis.md"
          CHUNK_SIZE: "500" # Process more items at once for efficiency
          RATE_LIMIT_BYPASS: "false" # Respect rate limits for large repos
```

#### Multiple Repository Analysis

To analyze multiple repositories, create separate workflow files or use a matrix strategy:

```yaml
name: Multi-Repository InnerSource Analysis

on:
  schedule:
    - cron: "0 0 * * 0"
  workflow_dispatch:

jobs:
  measure-innersource:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        repository:
          - "org/frontend-app"
          - "org/backend-service"
          - "org/mobile-app"
          - "org/data-pipeline"
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Measure InnerSource for ${{ matrix.repository }}
        uses: github/measure-innersource@v1
        env:
          REPOSITORY: ${{ matrix.repository }}
          GH_TOKEN: ${{ secrets.GH_TOKEN }}
          REPORT_TITLE: "InnerSource Report for ${{ matrix.repository }}"
          OUTPUT_FILE: "report_${{ matrix.repository }}.md"
          CHUNK_SIZE: "100"
```

#### Using Custom Team Ownership

To override the automatic team determination and explicitly specify the owning team:

```yaml
name: InnerSource with Custom Team

on:
  schedule:
    - cron: "0 0 * * 0"
  workflow_dispatch:

jobs:
  measure-innersource:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Measure InnerSource
        uses: github/measure-innersource@v1
        env:
          REPOSITORY: "org/repository"
          GH_TOKEN: ${{ secrets.GH_TOKEN }}
          OWNING_TEAM: "alice,bob,charlie,david"
          REPORT_TITLE: "InnerSource Report with Custom Team"
```

This is useful when:
- The first commit author doesn't represent the current team
- The org chart doesn't align with actual ownership
- You want to explicitly define team boundaries


### Configuration

Below are the allowed configuration options:

#### Authentication

This action can be configured to authenticate with GitHub App Installation or Personal Access Token (PAT). If all configuration options are provided, the GitHub App Installation configuration has precedence. You can choose one of the following methods to authenticate:

##### GitHub App Installation

| field                        | required | default | description                                                                                                                                                                                             |
| ---------------------------- | -------- | ------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `GH_APP_ID`                  | True     | `""`    | GitHub Application ID. See [documentation](https://docs.github.com/en/apps/creating-github-apps/authenticating-with-a-github-app/about-authentication-with-a-github-app) for more details.              |
| `GH_APP_INSTALLATION_ID`     | True     | `""`    | GitHub Application Installation ID. See [documentation](https://docs.github.com/en/apps/creating-github-apps/authenticating-with-a-github-app/about-authentication-with-a-github-app) for more details. |
| `GH_APP_PRIVATE_KEY`         | True     | `""`    | GitHub Application Private Key. See [documentation](https://docs.github.com/en/apps/creating-github-apps/authenticating-with-a-github-app/about-authentication-with-a-github-app) for more details.     |
| `GITHUB_APP_ENTERPRISE_ONLY` | False    | false   | Set this input to `true` if your app is created in GHE and communicates with GHE.                                                                                                                       |

##### Personal Access Token (PAT)

| field      | required | default | description                                                                                                       |
| ---------- | -------- | ------- | ----------------------------------------------------------------------------------------------------------------- |
| `GH_TOKEN` | True     | `""`    | The GitHub Token used to run the action. Must have read access to the repository you are interested in measuring. |

#### Other Configuration Options

| field               | required | default                 | description                                                                                                                           |
| ------------------- | -------- | ----------------------- | ------------------------------------------------------------------------------------------------------------------------------------- |
| `GH_ENTERPRISE_URL` | False    | `""`                    | URL of GitHub Enterprise instance to use for auth instead of github.com                                                               |
| `RATE_LIMIT_BYPASS` | False    | `false`                 | If set to `true`, the rate limit will be bypassed. This is useful if being run on an local GitHub server with rate limiting disabled. |
| `OUTPUT_FILE`       | False    | `innersource_report.md` | Output filename.                                                                                                                      |
| `REPORT_TITLE`      | False    | `"InnerSource Report"`  | Title to have on the report issue.                                                                                                    |
| `REPOSITORY`        | True     | `""`                    | The name of the repository you are trying to measure. Format `owner/repo` ie. `github/measure-innersource`                            |
| `CHUNK_SIZE`        | False    | `100`                   | Number of items to process at once when fetching data. Increasing can improve performance but uses more memory. Minimum value is 10.  |
| `OWNING_TEAM`       | False    | `""`                    | Comma-separated list of GitHub usernames that own the repository. Overrides the built-in team determination algorithm. Example: `alice,bob,charlie` |

## Understanding the Results

The generated report includes several key metrics:

### InnerSource Ratio

This is calculated as:

```markdown
InnerSource Ratio = (Total InnerSource Contributions) / (Total Contributions)
```

Where:

- Total InnerSource Contributions = Sum of all contributions from users outside the repository's owning team
- Total Contributions = Sum of all contributions to the repository

A higher ratio indicates more cross-team collaboration.

### Team Ownership Determination

The tool determines team ownership by:

1. Identifying the original commit author
2. Finding the original author's manager from org-data.json
3. Including all users who report to the same manager in the team
4. Including all users who report to anyone in the team

### Use Cases

- **Track InnerSource adoption over time**: Run this action on a schedule to see if your InnerSource initiative is gaining traction
- **Compare InnerSource collaboration across repositories**: Run on multiple repositories to identify which ones have the most cross-team collaboration
- **Identify key InnerSource contributors**: Recognize individuals who contribute across team boundaries
- **Measure the impact of InnerSource initiatives**: Track the change in metrics before and after implementing InnerSource practices

## Troubleshooting

### Common Issues and Solutions

#### Authentication Problems

**Issue**: `GH_TOKEN or the set of [GH_APP_ID, GH_APP_INSTALLATION_ID, GH_APP_PRIVATE_KEY] environment variables are not set`

**Solution**:

1. Verify you have set one of the authentication methods:
   - For PAT: Set `GH_TOKEN` environment variable
   - For GitHub App: Set all three app-related variables
2. Check that your token has the necessary permissions:
   - `repo` scope for private repositories
   - `public_repo` scope for public repositories
3. Ensure the token hasn't expired

**Issue**: `Unable to authenticate to GitHub`

**Solution**:

1. Verify your GitHub token is valid: `curl -H "Authorization: token YOUR_TOKEN" https://api.github.com/user` #gitleaks:allow
2. For GitHub Enterprise, ensure `GH_ENTERPRISE_URL` is set correctly
3. Check network connectivity to GitHub/GHE instance

#### Repository Access Issues

**Issue**: `Unable to fetch repository owner/repo specified`

**Solution**:

1. Verify the repository exists and is accessible
2. Check the `REPOSITORY` format is correct: `owner/repo`
3. Ensure your token has access to the repository
4. For private repositories, confirm you have the necessary permissions

#### Organization Data Issues

**Issue**: `No org data found. InnerSource collaboration cannot be measured`

**Solution**:

1. Create an `org-data.json` file in your repository root
2. Verify the file is valid JSON
3. Ensure all contributors are included in the org-data.json
4. Check file encoding is UTF-8

**Issue**: Contributors missing from org-data.json

**Solution**:

1. Add missing contributors to org-data.json:
   ```json
   {
     "missing-username": {
       "manager": "appropriate-manager"
     }
   }
   ```
2. Verify GitHub usernames are spelled correctly (case-sensitive)
3. Include bot accounts if needed (they're auto-excluded if containing "[bot]")

#### Memory and Performance Issues

**Issue**: Action runs out of memory or times out

**Solution**:

1. Reduce `CHUNK_SIZE` environment variable (default: 100)
2. For very large repositories, consider:
   ```yaml
   env:
     CHUNK_SIZE: "50" # Process fewer items at once
   ```
3. Run during off-peak hours to reduce API latency

**Issue**: API rate limit exceeded

**Solution**:

1. Use GitHub App authentication for higher rate limits
2. Reduce `CHUNK_SIZE` to make fewer concurrent requests
3. Set `RATE_LIMIT_BYPASS: "false"` (default) to respect rate limits
4. Consider running less frequently

#### Report Generation Issues

**Issue**: Empty or incomplete reports

**Solution**:

1. Check that contributors have activity (commits, PRs, issues)
2. Verify org-data.json includes all active contributors
3. Ensure the repository has commits, PRs, or issues to analyze
4. Check for network issues during data collection

**Issue**: Report files are too large

**Solution**:
The tool automatically splits large files, but you can:

1. Reduce the scope of analysis
2. Use the split files feature (automatic for files >65,535 characters)
3. Process reports programmatically rather than viewing in GitHub issues

### Configuration Validation

#### Environment Variable Checklist

**Required Variables**:

- [ ] `REPOSITORY` (format: `owner/repo`)
- [ ] Authentication: `GH_TOKEN` OR (`GH_APP_ID` + `GH_APP_INSTALLATION_ID` + `GH_APP_PRIVATE_KEY`)

**Optional Variables**:

- [ ] `GH_ENTERPRISE_URL` (for GitHub Enterprise)
- [ ] `GITHUB_APP_ENTERPRISE_ONLY` (for GHE GitHub Apps)
- [ ] `REPORT_TITLE` (default: "InnerSource Report")
- [ ] `OUTPUT_FILE` (default: "innersource_report.md")
- [ ] `CHUNK_SIZE` (default: 100, minimum: 10)
- [ ] `RATE_LIMIT_BYPASS` (default: false)
- [ ] `OWNING_TEAM` (comma-separated usernames to override team determination)

#### File Requirements Checklist

- [ ] `org-data.json` exists in repository root
- [ ] `org-data.json` is valid JSON
- [ ] All repository contributors are included in org-data.json
- [ ] GitHub usernames match exactly (case-sensitive)
- [ ] Manager relationships are defined for all users

### Debugging Steps

1. **Enable Verbose Logging**: The tool prints progress messages. Monitor the logs for:
   - Successful authentication
   - Repository access confirmation
   - Org data loading
   - Progress updates during processing

2. **Validate Configuration**:

   ```bash
   # Test GitHub authentication
   curl -H "Authorization: token $GH_TOKEN" https://api.github.com/user

   # Validate org-data.json
   python -m json.tool org-data.json

   # Check repository access
   curl -H "Authorization: token $GH_TOKEN" https://api.github.com/repos/owner/repo
   ```

3. **Test with Smaller Repositories**: Start with a smaller repository to isolate issues

4. **Check GitHub API Status**: Visit [https://www.githubstatus.com/](https://www.githubstatus.com/) for API availability

### Performance Optimization

#### For Large Repositories

1. **Optimize Chunk Size**:

   ```yaml
   env:
     CHUNK_SIZE: "200" # Increase for better performance
   ```

2. **Use GitHub App Authentication**:
   - Higher rate limits (5,000 requests/hour vs 1,000)
   - More reliable for large-scale operations

3. **Schedule During Off-Peak Hours**:
   ```yaml
   on:
     schedule:
       - cron: "0 2 * * 0" # 2 AM on Sundays
   ```

#### For High-Frequency Analysis

1. **Use Incremental Processing**: Consider analyzing only recent changes
2. **Cache Results**: Store intermediate results to avoid reprocessing
3. **Distribute Load**: Run analysis on multiple repositories in parallel

### Getting Help

If you continue to experience issues:

1. **Check Existing Issues**: Search the [GitHub Issues](https://github.com/github/measure-innersource/issues) for similar problems
2. **Create a New Issue**: Include:
   - Error messages (sanitized of sensitive information)
   - Configuration details (without secrets)
   - Steps to reproduce
   - Expected vs. actual behavior
3. **Provide Context**: Include repository size, org structure complexity, and environment details

## Sample Report

```markdown
# InnerSource Report

## Repository: octocat/hello-world

### InnerSource Ratio: 35.67%

### Original Commit Author: octocat (Manager: octoboss)

## Team Members that Own the Repo:

- octocat
- octoboss
- octodev1
- octodev2

## All Contributors:

- octocat
- octodev1
- octodev2
- contributor1
- contributor2

## Innersource Contributors:

- contributor1
- contributor2

## Innersource Contribution Counts:

- contributor1: 15 contributions
- contributor2: 8 contributions

## Team Member Contribution Counts:

- octocat: 25 contributions
- octodev1: 12 contributions
- octodev2: 5 contributions
```

## Limitations

- Requires accurate organization data in the org-data.json file
- Cannot detect team relationships beyond what's specified in the org-data.json file
- Historical team changes are not accounted for (uses current team structure only)
- Bot accounts should have "[bot]" in their username to be excluded from calculations
- Analysis is based on current repository state, not historical team memberships
- Large repositories may require longer processing times and higher memory usage
- API rate limits may affect processing speed for very large repositories

## Contributions

We would ❤️ contributions to improve this action. Please see [CONTRIBUTING.md](./CONTRIBUTING.md) for how to get involved.

### Development Setup

- Ensure you have python `3.10+` installed
- Clone this repository and cd into `measure-innersource`
- Create python virtual env
  `python3 -m venv .venv`
- Activate virtual env
  `source .venv/bin/activate`
- Install dependencies
  `pip install -r requirements.txt -r requirements-test.txt`
- Run linter
  `make lint`
- Run tests
  `make test`

## License

[MIT](LICENSE)

## More OSPO Tools

Looking for more resources for your open source program office (OSPO)? Check out the [`github-ospo`](https://github.com/github/github-ospo) repository for a variety of tools designed to support your needs.
