# Measure InnerSource tool

## Sample Report

## Support

If you need support using this project or have questions about it, please [open up an issue in this repository](https://github.com/github/measure-innersource/issues). Requests made directly to GitHub staff or support team will be redirected here to open an issue. GitHub SLA's and support/services contracts do not apply to this repository.

### OSPO GitHub Actions as a Whole

All feedback regarding our GitHub Actions, as a whole, should be communicated through [issues on our github-ospo repository](https://github.com/github/github-ospo/issues/new).

## Use as a GitHub Action

1. Create a repository to host this GitHub Action or select an existing repository. This is easiest with regards to permissions if it is the same repository as the one you want to measure innersource collaboration on.
2. Select a best fit workflow file from the [examples directory](./docs/example-workflows.md) for your use case.
3. Copy that example into your repository (from step 1) and into the proper directory for GitHub Actions: `.github/workflows/` directory with the file extension `.yml` (ie. `.github/workflows/measure-innersource.yml`)
4. Commit the workflow file to the default branch (often `master` or `main`)
5. Wait for the action to trigger based on the `schedule` entry or manually trigger the workflow as shown in the [documentation](https://docs.github.com/en/actions/using-workflows/manually-running-a-workflow).

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
| `REPOSITORY`        | True    | `""`                     | The name of the repository you are trying to measure. Format `owner/repo` ie. `github/measure-innersource`         |

                                                      
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
