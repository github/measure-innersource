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

Example format of `org-data.json`:
```json
{
  "username1": {
    "manager": "manager1",
  },
  "username2": {
    "manager": "manager1",
  },
  "username3": {
    "manager": "manager2",
  }
}
```

## Sample Report

Below is an example of the generated InnerSource report:

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

## Support

If you need support using this project or have questions about it, please [open up an issue in this repository](https://github.com/github/measure-innersource/issues). Requests made directly to GitHub staff or support team will be redirected here to open an issue. GitHub SLA's and support/services contracts do not apply to this repository.

### OSPO GitHub Actions as a Whole

All feedback regarding our GitHub Actions, as a whole, should be communicated through [issues on our github-ospo repository](https://github.com/github/github-ospo/issues/new).

## Use as a GitHub Action

1. Create a repository to host this GitHub Action or select an existing repository. This is easiest with regards to permissions if it is the same repository as the one you want to measure innersource collaboration on.
2. **Create an org-data.json file** in the root of your repository with your organization structure as described above.
4. Copy the example below (in the next section) into your repository (from step 1) and into the proper directory for GitHub Actions: `.github/workflows/` directory with the file extension `.yml` (ie. `.github/workflows/measure-innersource.yml`)
5. Update the workflow file with the appropriate configuration options as described below. The required configuration options are `REPOSITORY`, `GH_APP_ID`, `GH_APP_INSTALLATION_ID`, and `GH_APP_PRIVATE_KEY` for GitHub App Installation authentication, or `REPOSITORY` and `GH_TOKEN` for Personal Access Token (PAT) authentication. The other configuration options are optional.
6. Commit the workflow file to the default branch (often `master` or `main`)
7. Wait for the action to trigger based on the `schedule` entry or manually trigger the workflow as shown in the [documentation](https://docs.github.com/en/actions/using-workflows/manually-running-a-workflow).

### Basic Workflow Example

Here's a simple example workflow file to get you started:

```yaml
name: Measure InnerSource Collaboration

on:
  schedule:
    - cron: '0 0 * * 0'  # Run weekly on Sundays at midnight
  workflow_dispatch:     # Allow manual triggers

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

## Limitations

- Requires accurate organization data in the org-data.json file
- Cannot detect team relationships beyond what's specified in the org-data.json file
- Historical team changes are not accounted for (uses current team structure only)
- Bot accounts should have "[bot]" in their username to be excluded from calculations

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
- Run tests
  `make test`
- Run linter
  `make lint`

## License

[MIT](LICENSE)

## More OSPO Tools

Looking for more resources for your open source program office (OSPO)? Check out the [`github-ospo`](https://github.com/github/github-ospo) repository for a variety of tools designed to support your needs.
