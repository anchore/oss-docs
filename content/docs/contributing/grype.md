+++
title = "Grype"
description = "Developer guidelines when contributing to Grype"
weight = 20
categories = ["developer"]
tags = ["grype"]
menu_group = "projects"
icon_image = "/images/logos/grype/favicon-48x48.png"
+++

## Getting started

In order to test and develop in the [Grype repo](https://github.com/anchore/grype) you will need the following dependencies installed:

- Golang
- Docker
- Python (>= 3.9)
- make
- SQLite3 (optional -- for database inspection)

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
- `make format` - Auto-format source code
- `make unit` - Run unit tests
- `make integration` - Run integration tests
- `make cli` - Run CLI tests
- `make quality` - Run vulnerability matching quality tests
- `make snapshot` - Build release snapshot with all binaries and packages

## Testing

### Levels of testing

- `unit` (`make unit`): The default level of test which is distributed throughout the repo are unit tests.
  Any `_test.go` file that does not reside somewhere within the `/test` directory is a unit test.
  Other forms of testing should be organized in the `/test` directory.
  These tests should focus on the correctness of functionality in depth.
  % test coverage metrics only considers unit tests and no other forms of testing.

- `integration` (`make integration`): located within `test/integration`, these tests focus on the behavior surfaced by the Grype library entrypoints and make
  assertions about vulnerability matching results.
  The integration tests also update the vulnerability database and run with the race detector enabled to catch concurrency issues.

- `cli` (`make cli`): located within `test/cli`, these are tests that test the correctness of application behavior from a snapshot build.
  This should be used in cases where a unit or integration test will not do or if you are looking for in-depth testing of code in the `cmd/` package (such as
  testing the proper behavior of application configuration, CLI switches, and glue code before grype library calls).

- `quality` (`make quality`): located within `test/quality`, these are tests that verify vulnerability matching quality by comparing Grype's results against known-good results (quality gates).
  These tests help ensure that changes to vulnerability matching logic don't introduce regressions in match quality. The quality tests use a pinned database version to ensure consistent results.
  See the quality gate architecture documentation for how the system works and the [test/quality README](https://github.com/anchore/grype/tree/main/test/quality) for practical development workflows.

- `install` (part of acceptance testing): located within `test/install`, these are smoke-like tests that ensure that application packaging and installation works as expected.
  For example, during release we provide RPM packages as a download artifact.
  We also have an accompanying RPM acceptance test that installs the RPM from a snapshot build and ensures the output of a grype invocation matches canned expected output.

### Quality Gates

Quality gates validate that code changes don't cause performance regressions in vulnerability matching. The system compares your PR's matching results against a baseline using a pinned database to isolate code changes from database volatility.

**What quality gates validate:**

- F1 score (combination of true positives, false positives, and false negatives)
- False negative count (should not increase)
- Indeterminate matches (should remain below 10%)

**Common development workflows:**

- `make capture` - Download SBOMs and generate match results
- `make validate` - Analyze output and evaluate pass/fail
- `yardstick label explore [UUID]` - Interactive TUI for labeling matches
- `./gate.py --image [digest]` - Test specific images

**Learn more:**

- [test/quality README](https://github.com/anchore/grype/tree/main/test/quality) - Detailed setup and workflows

## Relationship to Syft

Grype uses Syft as a library for all-things related to obtaining and parsing the given scan target (pulling container images, parsing container images,
indexing directories, cataloging packages, etc). Releases of Grype should always use released versions of Syft (commits that are tagged and show up in the GitHub releases page).
However, continually integrating unreleased Syft changes into Grype incrementally is encouraged (e.g. `go get github.com/anchore/syft@main`) as long as by the time
a release is cut the Syft version is updated to a released version (e.g. `go get github.com/anchore/syft@v<semantic-version>`).

## Inspecting the database

The v6 database is a highly normalized database with JSON data, making queries more difficult than the previous version.
The easiest way to understand what's in the database is using the [`grype db search` subcommand]({{< relref "/docs/reference/grype/cli/#grype-db-search" >}}), e.g.:

```
go run ./cmd/grype db search CVE-2025-1234 -o json
```

If you need to inspect the database directly, the current database format is Sqlite3. Install `sqlite3` in your system and ensure that the `sqlite3` executable is available in your path.
Ask `grype` about the location of the database, which will be different depending on the operating system:

```bash
$ go run ./cmd/grype db status
Path:      /Users/kzantow/Library/Caches/grype/db/6/vulnerability.db
Schema:    v6.1.3
Built:     2025-12-01T16:28:25Z
From:      https://grype.anchore.io/databases/v6/vulnerability-db_v6.1.3_2025-12-01T11:57:14Z_1764606505.tar.zst?checksum=sha256%3A8d34ad53aebced159559e767e1ccedddc41dfeb3f70492bdbb1b94df629def05
Status:    valid
```

Next, open the `vulnerability.db` with `sqlite3`:

```bash
sqlite3 /Users/kzantow/Library/Caches/grype/db/6/vulnerability.db
```

To make the reporting from Sqlite3 easier to read, enable the following:

```sql
sqlite> .mode column
sqlite> .headers on
```

List the tables:

```sql
sqlite> .tables
affected_cpe_handles                   operating_systems                    affected_package_handles               package_cpes
...
```

To retrieve basic information for a specific vulnerability, join the `vulnerability_handles` table with `blobs`, for example:

```sql
sqlite> select * from blobs b join vulnerability_handles h on b.id = h.blob_id where h.name = 'CVE-2025-1234';
id       value                                                         id      name           status    published_date                 modified_date                  withdrawn_date  provider_id  blob_id
-------  ------------------------------------------------------------  ------  -------------  --------  -----------------------------  -----------------------------  --------------  -----------  -------
1016723  {"id":"CVE-2025-1234","assigner":["cve@gitlab.com"],"descrip  287704  CVE-2025-1234  rejected  2025-07-05 23:15:24.613+00:00  2025-07-05 23:15:24.613+00:00                  nvd          1016723
         tion":"Rejected reason: This CVE ID has been rejected or wit
         hdrawn by its CVE Numbering Authority.","refs":[{"url":"http
         s://nvd.nist.gov/vuln/detail/CVE-2025-1234"}]}
```

## Next Steps

<!-- markdownlint-disable MD036 -->

**Understanding the Codebase**

- [Architecture](/docs/architecture/grype) - Learn about package structure, core library flow, and matchers
- [API Reference](https://pkg.go.dev/github.com/anchore/grype) - Explore the public Go API, type definitions, and function signatures
  **Contributing Your Work**

- [Pull Requests](/docs/contributing/pull-requests) - Guidelines for submitting PRs and working with reviewers
- [Issues and Discussions](/docs/contributing/issues-and-discussions) - Where to get help and report issues

**Finding Work**

- [Good First Issues](https://github.com/anchore/grype/issues?q=is%3Aopen%20is%3Aissue%20label%3A%22good-first-issue%22) - Beginner-friendly issues
- [Help Wanted](https://github.com/anchore/grype/issues?q=is%3Aopen%20is%3Aissue%20label%3A%22help-wanted%22) - Issues where contributions are especially welcome

**Getting Help**

- [Anchore Discourse](https://anchore.com/discourse) - Community discussions and questions

<!-- markdownlint-enable MD036 -->
