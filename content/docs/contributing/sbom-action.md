+++
title =  "SBOM Action"
description = "Developer guidelines when contributing to sbom-action"
weight = 40
categories = ["developer"]
tags = ["sbom-action"]
menu_group = "projects"
+++

## Getting started

In order to test and develop in the [sbom-action repo](https://github.com/anchore/sbom-action) you will need the following dependencies installed:

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

- `npm run build` - Check TypeScript compilation (no output files)
- `npm run lint` - Check code with ESLint
- `npm run format` - Auto-format code with Prettier
- `npm run format-check` - Check code formatting without changes
- `npm run package` - Build distribution files with ncc (outputs to `dist/`)
- `npm test` - Run Jest tests
- `npm run all` - Complete validation suite (build + format + lint + package + test)

## Testing

The sbom-action uses [Jest](https://jestjs.io/) for testing. To run the test suite:

```bash
npm test
```

The CI workflow handles any additional setup automatically (like Docker registries). For local development, you just need to install dependencies and run tests.

### Test types

The test suite includes two main categories:

- **Unit tests** (e.g., `tests/GithubClient.test.ts`, `tests/SyftGithubAction.test.ts`): Test individual components in isolation by mocking GitHub Actions context and external dependencies.

- **Integration tests** (`tests/integration/`): Execute the full action workflow with real Syft invocations against test fixtures in `tests/fixtures/` (npm-project, yarn-project). These tests use snapshot testing to validate SBOM output and GitHub dependency snapshot uploads.

### Snapshot testing

Integration tests extensively use Jest's snapshot testing to validate SBOM output. When you run integration tests, Jest compares the generated SBOMs against saved snapshots in `tests/integration/__snapshots__/`.

The tests normalize dynamic values (timestamps, hashes, IDs) before comparison to ensure consistent snapshots across runs.

**Updating snapshots:**

When you intentionally change SBOM output format or content, update the snapshots:

```bash
npm run test:update-snapshots
```

{{< alert color="warning" >}}
**Important:** Always manually review snapshot changes before committing. Snapshots capture expected behavior, so changes should be intentional and correct.
{{< /alert >}}

## Development workflow

### Pre-commit hooks

The sbom-action uses Husky to run automated checks before each commit:

1. **Code formatting** - Prettier formats staged TypeScript files
2. **Distribution rebuild** - Runs `npm run package` to rebuild `dist/` directory
3. **Auto-staging** - Automatically stages updated `dist/` files

The hook is defined in `.husky/pre-commit` and runs the `precommit` npm script.

{{< alert color="primary" >}}
**Why commit dist/?**

GitHub Actions can't install dependencies or compile code at runtime. The action must include pre-built JavaScript files in the `dist/` directory. The ncc compiler bundles all TypeScript source and dependencies into standalone JavaScript files.
{{< /alert >}}

### Code organization

The sbom-action consists of three GitHub Actions, each with its own entry point:

**Main action** (`action.yml`):

- Entry point: `src/runSyftAction.ts`
- Compiled to: `dist/runSyftAction/index.js`
- Generates SBOMs and uploads as workflow artifacts and release assets

**Publish SBOM sub-action** (`publish-sbom/action.yml`):

- Entry point: `src/attachReleaseAssets.ts`
- Compiled to: `dist/attachReleaseAssets/index.js`
- Uploads existing SBOMs to GitHub releases

**Download Syft sub-action** (`download-syft/action.yml`):

- Entry point: `src/downloadSyft.ts`
- Compiled to: `dist/downloadSyft/index.js`
- Downloads and caches Syft binary

**Key modules:**

- `src/Syft.ts` - Wraps Syft execution and configuration
- `src/SyftVersion.ts` - Manages Syft version resolution
- `src/github/SyftDownloader.ts` - Handles Syft binary downloads
- `src/github/SyftGithubAction.ts` - Core action orchestration logic
- `src/github/GithubClient.ts` - GitHub API interactions
- `src/github/Executor.ts` - Command execution wrapper

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

- Test on Ubuntu and Windows
- Validate distribution files are up-to-date
- Test scanning directories and container images
- Verify all SBOM formats
- Test sub-actions (download-syft, publish-sbom)

**Manual testing:**

Test changes in your own workflows using the repository name and branch:

```yaml
- uses: your-username/sbom-action@your-branch
  with:
    path: ./
```

Or test locally using [act](https://github.com/nektos/act) if you have it installed.

### Action runtime

The sbom-action uses the Node.js 20 runtime (`runs.using: node20` in action.yml). This runtime is provided by GitHub Actions and doesn't require separate installation in workflows.

## Next Steps

<!-- markdownlint-disable MD036 -->

**Understanding the Codebase**

- [SBOM Action Repository](https://github.com/anchore/sbom-action) - Source code and issue tracker
- [Syft Documentation]({{< relref "/docs/installation/syft" >}}) - The underlying SBOM generation tool that sbom-action uses

**Contributing Your Work**

- [Pull Requests]({{< relref "/docs/contributing/pull-requests" >}}) - Guidelines for submitting PRs and working with reviewers
- [Issues and Discussions]({{< relref "/docs/contributing/issues-and-discussions" >}}) - Where to get help and report issues

**Finding Work**

- [Good First Issues](https://github.com/anchore/sbom-action/issues?q=is%3Aopen+is%3Aissue+label%3A%22good+first+issue%22) - Beginner-friendly issues

**Getting Help**

- [Anchore Discourse](https://anchore.com/discourse) - Community discussions and questions

<!-- markdownlint-enable MD036 -->
