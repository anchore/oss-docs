+++
title = "Scan Action"
description = "Developer guidelines when contributing to scan-action"
weight = 50
categories = ["developer"]
tags = ["scan-action"]
menu_group = "projects"
+++

## Getting started

In order to test and develop in the [scan-action repo](https://github.com/anchore/scan-action) you will need the following dependencies installed:

- Node.js (>= 20.11.0)
- npm
- Docker

### Initial setup

Run once after cloning to install dependencies and development tools:

```bash
npm install
```

This command installs all dependencies and sets up [Husky](https://typicard.github.io/husky/) git hooks that automatically format code and rebuild the distribution files before commits.

### Useful commands

Common commands for ongoing development:

- `npm run build` - Bundle with ncc and normalize line endings
- `npm run lint` - Check code with ESLint
- `npm run prettier` - Auto-format code with Prettier
- `npm test` - Complete test suite (lint + install Grype + build + run tests)
- `npm run run-tests` - Run Jest tests only
- `npm run test:update-snapshots` - Update test expectations (lint + install Grype + run tests with snapshot updates)
- `npm run audit` - Run security audit on production dependencies
- `npm run update-deps` - Update dependencies with npm-check-updates

## Testing

Tests require Grype to be installed locally and a Docker registry for integration tests. Set up your test environment:

**Install Grype locally:**

```bash
npm run install-and-update-grype
```

**Start local Docker registry:**

```bash
docker run -d -p 5000:5000 --name registry registry:2
```

Tests automatically disable Grype database auto-update and validation to ensure consistent test results.

**CI environment:**

The GitHub Actions test workflow automatically:

- Starts a Docker registry service on port 5000
- Tests on Ubuntu, Windows, and macOS
- Validates across multiple configurations (image/path/sbom sources, output formats)

### Test types

The scan-action uses [Jest](https://jestjs.io/) for testing with several categories:

- **Unit tests** (e.g., `tests/action.test.js`, `tests/grype_command.test.js`): Test individual functions in isolation by mocking GitHub Actions context and external dependencies.

- **Integration tests**: Execute the full action workflow with real Grype invocations. These tests validate end-to-end functionality including downloading Grype, running scans, and generating output files.

- **SARIF validation tests** (`tests/sarif_output.test.js`): Validate SARIF report structure and content using the `@microsoft/jest-sarif` library to ensure consistent output format and compliance with the SARIF specification.

- **Distribution tests** (`tests/dist.test.js`): Verify that the committed `dist/` directory is up-to-date with the source code.

**Test fixtures:**

The `tests/fixtures/` directory contains sample projects and files for testing:

- `npm-project/` - Sample npm project for directory scanning
- `yarn-project/` - Sample yarn project for directory scanning
- `test_sbom.spdx.json` - Sample SBOM file for SBOM scanning tests

### SARIF output testing

The SARIF output tests validate report structure using the `@microsoft/jest-sarif` library. Tests normalize dynamic values (versions, fully qualified names) before validation to ensure consistent results across test runs.

The tests validate that:

- Generated SARIF reports are valid according to the SARIF specification
- Expected vulnerabilities are detected in test fixtures
- Output structure remains consistent across runs

If you need to update test expectations, run:

```bash
npm run test:update-snapshots
```

{{< alert color="warning" >}}
**Important:** Always manually review test changes before committing. Tests capture expected behavior, so changes should be intentional and correct.
{{< /alert >}}

## Development workflow

### Pre-commit hooks

The scan-action uses Husky to run automated checks before each commit:

1. **Code formatting** - lint-staged runs Prettier on staged JavaScript files
2. **Distribution rebuild** - Runs `npm run precommit` to rebuild `dist/` directory
3. **Auto-staging** - Automatically stages updated `dist/` files

The hook is defined in `.husky/pre-commit` and ensures that distribution files are always synchronized with source code.

{{< alert color="primary" >}}
**Why commit dist/?**

GitHub Actions can't install dependencies or compile code at runtime. The action must include pre-built JavaScript files in the `dist/` directory. The ncc compiler bundles all source code and dependencies into standalone JavaScript files.
{{< /alert >}}

### Code organization

The scan-action has a straightforward single-file architecture:

**Main action** (`action.yml`):

- Entry point: `index.js`
- Compiled to: `dist/index.js`
- Downloads Grype, runs vulnerability scans, generates reports

**Download Grype sub-action** (`download-grype/action.yml`):

- Entry point: Reuses `dist/index.js` with `run: "download-grype"` input
- Provides standalone Grype download and caching
- Returns `cmd` output with path to Grype binary

**Key functions in index.js:**

- `downloadGrype()` - Downloads Grype using install script
- `downloadGrypeWindowsWorkaround()` - Windows-specific download logic
- `installGrype()` - Installs and caches Grype binary
- `sourceInput()` - Validates mutually exclusive inputs (image/path/sbom)
- `run()` - Main action execution flow
- Command construction and output handling

## GitHub Actions specifics

### Debugging Actions

Enable detailed debug logging by setting a repository secret:

1. Go to your repository Settings → Secrets and variables → Actions
2. Add a new secret: `ACTIONS_STEP_DEBUG` = `true`

This enables debug logging from the [@actions/toolkit](https://github.com/actions/toolkit) libraries used throughout the action.

See the [GitHub documentation](https://github.com/actions/toolkit/blob/master/docs/action-debugging.md) for more details.

### Testing Actions locally

**CI validation:**

The repository includes comprehensive CI workflows in `.github/workflows/test.yml` that:

- Test on Ubuntu, Windows, and macOS
- Validate distribution files are up-to-date
- Test scanning images, directories, and SBOM files
- Verify all output formats (SARIF, JSON, CycloneDX, table)
- Test download-grype sub-action

**Manual testing:**

Test changes in your own workflows using the repository name and branch:

```yaml
- uses: <your-username>/scan-action@<your-branch>
  with:
    image: "alpine:latest"
```

Or test locally using [act](https://github.com/nektos/act) if you have it installed.

### Action runtime

The scan-action uses the Node.js 20 runtime (`runs.using: node20` in action.yml). This runtime is provided by GitHub Actions and doesn't require separate installation in workflows.

## Next Steps

<!-- markdownlint-disable MD036 -->

**Understanding the Codebase**

- [Scan Action Repository](https://github.com/anchore/scan-action) - Source code and issue tracker
- [Grype Documentation]({{< relref "/docs/installation/grype" >}}) - Learn about the underlying vulnerability scanner that scan-action uses

**Contributing Your Work**

- [Pull Requests]({{< relref "/docs/contributing/pull-requests" >}}) - Guidelines for submitting PRs and working with reviewers
- [Issues and Discussions]({{< relref "/docs/contributing/issues-and-discussions" >}}) - Where to get help and report issues

**Finding Work**

- [Good First Issues](https://github.com/anchore/scan-action/issues?q=is%3Aopen+is%3Aissue+label%3A%22good+first+issue%22) - Beginner-friendly issues

**Getting Help**

- [Anchore Discourse](https://anchore.com/discourse) - Community discussions and questions

<!-- markdownlint-enable MD036 -->
