+++
title =  "Grype DB"
description = "Developer guidelines when contributing to Grype DB"
weight = 25
categories = ["developer"]
tags = ["grype-db", "vunnel"]
menu_group = "projects"
+++

## Getting started

This codebase is primarily Go, however, there are also Python scripts critical to the daily DB publishing process as
well as acceptance testing. You will require the following:

- Python 3.11+ installed on your system (Python 3.11-3.13 supported). Consider using [pyenv](https://github.com/pyenv/pyenv) if you do not have a
  preference for managing python interpreter installations.
- `zstd` binary utility if you are packaging v6+ DB schemas
- _(optional)_ `xz` binary utility if you have specifically overridden the package command options
- [uv](https://docs.astral.sh/uv/) installed for Python package and virtualenv management

To download Go tooling used for static analysis, dependent Go modules, and Python dependencies run:

```
make bootstrap
```

### Useful commands

Common commands for ongoing development:

- `make help` - List all available commands
- `make lint` - Check code formatting and linting
- `make lint-fix` - Auto-fix formatting issues
- `make unit` - Run unit tests (Go and Python)
- `make cli` - Run CLI tests
- `make db-acceptance schema=<version>` - Run DB acceptance tests for a schema version
- `make snapshot` - Build release snapshot with all binaries and packages
- `make download-all-provider-cache` - Download pre-built vulnerability data cache

## Development workflows

### Getting vulnerability data

In order to build a grype DB you will need a local cache of vulnerability data:

```
make download-all-provider-cache
```

This will populate the `./data` directory locally with everything needed to run `grype-db build` (without needing to run `grype-db pull`).

This data being pulled down is the same data used in the daily DB publishing workflow, so it should be relatively fresh.

### Creating a new DB schema

1. Create a new `v#` schema package in the `grype` repo (within `pkg/db`)
2. Create a new `v#` schema package in the `grype-db` repo (use the `bump-schema.py` helper script) that uses the new changes from `grype-db`
3. Modify the `manager/src/grype_db_manager/data/schema-info.json` to pin the last-latest version to a specific version of grype and add the new schema version pinned to the "main" branch of grype (or a development branch)
4. Update all references in `grype` to use the new schema
5. Use the [Staging DB Publisher](https://github.com/anchore/grype-db/actions/workflows/staging-db-publisher.yaml) workflow to test your DB changes with grype in a flow similar to the daily DB publisher workflow

### Testing with staging databases

While developing a new schema version it may be useful to get a DB built for you by the [Staging DB Publisher](https://github.com/anchore/grype-db/actions/workflows/staging-db-publisher.yaml) GitHub Actions workflow.
This code exercises the same code as the Daily DB Publisher, with the exception that only a single schema is built and is validated against a given development branch of grype.
When these DBs are published you can point grype at the proper listing file like so:

```
GRYPE_DB_UPDATE_URL=https://toolbox-data.anchore.io/grype/staging-databases/listing.json grype centos:8 ...
```

## Testing

### Levels of testing

- `unit` (`make unit`): Unit tests for both Go code in the main codebase and Python scripts in the `manager/` directory.
  These tests focus on correctness of individual functions and components. Coverage metrics track Go test coverage.

- `cli` (`make cli`): CLI tests for both Go and Python components. These validate that command-line interfaces work correctly with various inputs and configurations.

- `db-acceptance` (`make db-acceptance schema=<version>`): Acceptance tests that verify a specific DB schema version works correctly with Grype.
  These tests build a database, run Grype scans, and validate that vulnerability matches are correct and complete.

### Running tests

To run unit tests for Go code and Python scripts:

```
make unit
```

To verify that a specific DB schema version interops with Grype:

```
make db-acceptance schema=<version>
# Note: this may take a while... go make some coffee.
```

## Next Steps

<!-- markdownlint-disable MD036 -->

**Understanding the Codebase**

- [Architecture](/docs/architecture/grype-db) - Learn about the ETL pipeline, schema support, and publishing workflow
- [Vunnel Documentation](https://github.com/anchore/vunnel) - Understand the vulnerability data provider system that feeds Grype DB
  **Contributing Your Work**

- [Pull Requests](/docs/contributing/pull-requests) - Guidelines for submitting PRs and working with reviewers
- [Issues and Discussions](/docs/contributing/issues-and-discussions) - Where to get help and report issues

**Related Projects**

- [Grype Contributing Guide](/docs/contributing/grype) - Understand how Grype uses the database
- [Vunnel Contributing Guide](/docs/contributing/vunnel) - Learn about vulnerability data providers

**Getting Help**

- [Anchore Discourse](https://anchore.com/discourse) - Community discussions and questions
- [Grype DB GitHub Issues](https://github.com/anchore/grype-db/issues) - Report bugs or request features

<!-- markdownlint-enable MD036 -->
