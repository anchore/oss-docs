+++
title =  "Grant"
description = "Developer guidelines when contributing to Grant"
weight = 30
categories = ["developer"]
tags = ["grant"]
type = "docs"
url = "docs/contributing/grant"
menu_group = "projects"
+++

## Getting started

In order to test and develop in the [Grant repo](https://github.com/anchore/grant) you will need the following dependencies installed:

- Golang
- Docker
- make

### Initial setup

Run once after cloning to install development tools:

```bash
make bootstrap
```

{{< alert color="primary" >}}
Make sure you've updated your docker settings so the default docker socket path is available.

1. Go to `docker → settings → advanced` and ensure **"Allow the default Docker socket to be used"** is checked.

2. Use the **default docker context**, run: `docker context use default`

{{< /alert >}}

### Useful commands

Common commands for ongoing development:

- `make help` - List all available commands
- `make lint` - Check code formatting and linting
- `make lint-fix` - Auto-fix formatting issues
- `make unit` - Run unit tests
- `make test` - Run all tests
- `make snapshot` - Build release snapshot with all binaries and packages (also available as `make build`)
- `make generate` - Generate SPDX license index and license patterns

## Testing

### Levels of testing

- `unit` (`make unit`): The default level of test which is distributed throughout the repo are unit tests.
  Any `_test.go` file that does not reside somewhere within the `/tests` directory is a unit test.
  These tests focus on the correctness of functionality in depth. % test coverage metrics only consider unit tests and no other forms of testing.

- `integration` (`make test`): located in `tests/integration_test.go`, these tests focus on policy loading, license evaluation, and core library behavior.
  They test the interaction between different components like policy parsing, license matching with glob patterns, and package evaluation logic.

- `cli` (part of `make test`): located in `tests/cli/`, these are tests that test the correctness of application behavior from a snapshot build.
  These tests execute the actual Grant binary and verify command output, exit codes, and behavior of commands like `check`, `list`, and `version`.

### Testing conventions

- Unit tests should focus on correctness of individual functions and components
- Integration tests validate that core library components work together correctly (policy evaluation, license matching, etc.)
- CLI tests ensure user-facing commands produce expected output and behavior
- Current coverage threshold is 8% (see `Taskfile.yaml`)
- Use table-driven tests where appropriate to test multiple scenarios

### Linting

You can run the linter for the project by running:

```bash
make lint
```

This checks code formatting with `gofmt` and runs `golangci-lint` checks.

To automatically fix linting issues:

```bash
make lint-fix
```

## Code generation

Grant generates code and data files that need to be kept in sync with external sources:

**What gets generated:**

- **SPDX License Index** - Up-to-date list of license identifiers from the SPDX project for license identification and validation
- **License File Patterns** - Generated patterns to identify license files in scanned directories

**When to regenerate:**

Run code generation after:

- The SPDX license list has been updated
- Adding new license file naming patterns
- Contributing changes to license detection logic

**Generation commands:**

- `make generate` - Run all generation tasks
- `make generate-spdx-licenses` - Download and generate latest SPDX license list
- `make generate-license-patterns` - Generate license file patterns (depends on SPDX license index)

After running generation commands, review the changes carefully and commit them as part of your pull request.

## Package structure

Grant is organized into two main areas: the public library API and the CLI application. For detailed API documentation, see the [Grant Go package reference](https://pkg.go.dev/github.com/anchore/grant).

### `grant/` - Public Library API

The top-level `grant/` package is the public library that other projects can import and use. This is what you'd reference with `import "github.com/anchore/grant/grant"`.

This package contains the core functionality:

- License evaluation and matching
- Policy loading and validation
- Package analysis and filtering

Most contributions to core Grant functionality belong in this package.

### `cmd/grant/` - CLI Application

The CLI application is built on top of the `grant/` library and contains application-specific code:

```
cmd/grant/
├── cli/            # Command wiring and application setup
│   ├── command/    # CLI command implementations (list, check, etc.)
│   ├── internal/   # Internal command implementations
│   ├── option/     # Command flags and configuration options
│   └── tui/        # Terminal UI and event handlers
└── main.go         # Application entrypoint
```

Contributions to CLI features, command behavior, or user interface improvements belong in this package.

## Next Steps

<!-- markdownlint-disable MD036 -->

**Understanding the Codebase**

- [Grant API Reference](https://pkg.go.dev/github.com/anchore/grant) - Explore the public Go API, type definitions, and function signatures

**Contributing Your Work**

- [Pull Requests](/docs/contributing/pull-requests) - Guidelines for submitting PRs and working with reviewers
- [Issues and Discussions](/docs/contributing/issues-and-discussions) - Where to get help and report issues

**Finding Work**

- [Good First Issues](https://github.com/anchore/grant/issues?q=is%3Aopen%20is%3Aissue%20label%3A%22good%20first%20issue%22) - Beginner-friendly issues

**Getting Help**

- [Anchore Discourse](https://anchore.com/discourse) - Community discussions and questions

<!-- markdownlint-enable MD036 -->
