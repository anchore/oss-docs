+++
title =  "Syft"
description = "Developer guidelines when contributing to Syft"
weight = 10
categories = ["developer"]
tags = ["syft"]
url = "docs/contributing/syft"
menu_group = "projects"
+++

## Getting started

In order to test and develop in the [Syft repo](https://github.com/anchore/syft) you will need the following dependencies installed:

- Golang
- Docker
- Python (>= 3.9)
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
- `make integration` - Run integration tests
- `make cli` - Run CLI tests
- `make snapshot` - Build release snapshot with all binaries and packages

## Testing

### Levels of testing

- `unit` (`make unit`): The default level of test which is distributed throughout the repo are unit tests. Any `_test.go` file that
  does not reside somewhere within the `/test` directory is a unit test. Other forms of testing should be organized in
  the `/test` directory. These tests should focus on the correctness of functionality in depth. % test coverage metrics
  only considers unit tests and no other forms of testing.

- `integration` (`make integration`): located within `cmd/syft/internal/test/integration`, these tests focus on the behavior surfaced by the common library
  entrypoints from the `syft` package and make light assertions about the results surfaced. Additionally, these tests
  tend to make diversity assertions for enum-like objects, ensuring that as enum values are added to a definition
  that integration tests will automatically fail if no test attempts to use that enum value. For more details see
  the "Data diversity and freshness assertions" section below.

- `cli` (`make cli`): located with in `test/cli`, these are tests that test the correctness of application behavior from a
  snapshot build. This should be used in cases where a unit or integration test will not do or if you are looking
  for in-depth testing of code in the `cmd/` package (such as testing the proper behavior of application configuration,
  CLI switches, and glue code before syft library calls).

- `acceptance` (`make install-test`): located within `test/compare` and `test/install`, these are smoke-like tests that ensure that application
  packaging and installation works as expected. For example, during release we provide RPM packages as a download
  artifact. We also have an accompanying RPM acceptance test that installs the RPM from a snapshot build and ensures the
  output of a syft invocation matches canned expected output. New acceptance tests should be added for each release artifact
  and architecture supported (when possible).

### Data diversity and freshness assertions

It is important that tests against the codebase are flexible enough to begin failing when they do not cover "enough"
of the objects under test. "Cover" in this case does not mean that some percentage of the code has been executed
during testing, but instead that there is enough diversity of data input reflected in testing relative to the
definitions available.

For instance, consider an enum-like value like so:

```go
type Language string

const (
  Java            Language = "java"
  JavaScript      Language = "javascript"
  Python          Language = "python"
  Ruby            Language = "ruby"
  Go              Language = "go"
)
```

Say we have a test that exercises all the languages defined today:

```go
func TestCatalogPackages(t *testing.T) {
  testTable := []struct {
    // ... the set of test cases that test all languages
  }
  for _, test := range cases {
    t.Run(test.name, func (t *testing.T) {
      // use inputFixturePath and assert that syft.CatalogPackages() returns the set of expected Package objects
      // ...
    })
  }
}
```

Where each test case has a `inputFixturePath` that would result with packages from each language. This test is
brittle since it does not assert that all languages were exercised directly and future modifications (such as
adding a new language) won't be covered by any test cases.

To address this, the enum-like object should have a definition of all objects that can be used in testing:

```go
type Language string

// const( Java Language = ..., ... )

var AllLanguages = []Language{
 Java,
 JavaScript,
 Python,
 Ruby,
 Go,
 Rust,
}
```

Allowing testing to automatically fail when adding a new language:

```go
func TestCatalogPackages(t *testing.T) {
  testTable := []struct {
   // ... the set of test cases that (hopefully) covers all languages
  }

  // new stuff...
  observedLanguages := strset.New()

  for _, test := range cases {
    t.Run(test.name, func (t *testing.T) {
      // use inputFixturePath and assert that syft.CatalogPackages() returns the set of expected Package objects
     // ...

     // new stuff...
     for _, actualPkg := range actual {
        observedLanguages.Add(string(actualPkg.Language))
     }

    })
  }

   // new stuff...
  for _, expectedLanguage := range pkg.AllLanguages {
    if  !observedLanguages.Contains(expectedLanguage) {
      t.Errorf("failed to test language=%q", expectedLanguage)
    }
  }
}
```

This is a better test since it will fail when someone adds a new language but fails to write a test case that should
exercise that new language. This method is ideal for integration-level testing, where testing correctness in depth
is not needed (that is what unit tests are for) but instead testing in breadth to ensure that units are well integrated.

A similar case can be made for data freshness; if the quality of the results will be diminished if the input data
is not kept up to date then a test should be written (when possible) to assert any input data is not stale.

An example of this is the static list of licenses that is stored in `internal/spdxlicense` for use by the SPDX
presenters. This list is updated and published periodically by an external group and syft can grab and update this
list by running `go generate ./...` from the root of the repo.

An integration test has been written to grabs the latest license list version externally and compares that version
with the version generated in the codebase. If they differ, the test fails, indicating to someone that there is an
action needed to update it.

{{< alert title="Key Takeaway" color="primary" >}}
Try and write tests that fail when data assumptions change and not just when code changes.
{{< /alert >}}

### Snapshot tests

The format objects make a lot of use of "snapshot" testing, where you save the expected output bytes from a call into the
git repository and during testing make a comparison of the actual bytes from the subject under test with the golden
copy saved in the repo. The "golden" files are stored in the `test-fixtures/snapshot` directory relative to the go
package under test and should always be updated by invoking `go test` on the specific test file with a specific CLI
update flag provided.

Many of the `Format` tests make use of this approach, where the raw SBOM report is saved in the repo and the test
compares that SBOM with what is generated from the latest presenter code. The following command can be used to
update the golden files for the various snapshot tests:

```
make update-format-golden-files
```

These flags are defined at the top of the test files that have tests that use the snapshot files.

Snapshot testing is only as good as the manual verification of the golden snapshot file saved to the repo! Be careful
and diligent when updating these files.

### Test fixtures

Syft uses a sophisticated test fixture caching system to speed up test execution. Test fixtures include pre-built test images,
language-specific package manifests, and other test data. Rather than rebuilding fixtures on every checkout, Syft can download
a pre-built cache from GitHub Container Registry.

**Common fixture commands:**

- `make fixtures` - Intelligently download or rebuild fixtures as needed
- `make build-fixtures` - Manually build all fixtures from scratch
- `make clean-cache` - Remove all cached test fixtures
- `make check-docker-cache` - Verify docker cache size is within limits

**When to use each command:**

- **First time setup**: Run `make fixtures` after cloning the repository. This will download the latest fixture cache.
- **Tests failing unexpectedly**: Try `make clean-cache` followed by `make fixtures` to ensure you have fresh fixtures.
- **Working offline**: Set `DOWNLOAD_TEST_FIXTURE_CACHE=false` and run `make build-fixtures` to build fixtures locally without downloading.
- **Modifying test fixtures**: After changing fixture source files, run `make build-fixtures` to rebuild affected fixtures.

The fixture system tracks input fingerprints and only rebuilds fixtures when their source files change. This makes the
development cycle faster while ensuring tests always run against the correct fixture data.

## Code generation

Syft generates several types of code and data files that need to be kept in sync with external sources or internal structures:

**What gets generated:**

- **JSON Schema** - Generated from Go structs to define the Syft JSON output format
- **SPDX License List** - Up-to-date list of license identifiers from the SPDX project
- **CPE Dictionary Index** - Index of Common Platform Enumeration identifiers for vulnerability matching

**When to regenerate:**

Run code generation after:

- Modifying the `pkg.Package` struct or related types (requires JSON schema regeneration)
- SPDX releases a new license list
- CPE dictionary updates are available

**Generation commands:**

- `make generate` - Run all generation tasks
- `make generate-json-schema` - Generate JSON schema from Go types
- `make generate-license-list` - Download and generate latest SPDX license list
- `make generate-cpe-dictionary-index` - Generate CPE dictionary index

After running generation commands, review the changes carefully and commit them as part of your pull request. The CI pipeline
will verify that generated files are up to date.

## Adding a new cataloger

Catalogers must fulfill the [`pkg.Cataloger` interface](https://github.com/anchore/syft/tree/v1.36.0/syft/pkg/cataloger.go) in order to add packages to the SBOM.

All catalogers are registered as tasks in Syft's task-based cataloging system:

- Add your cataloger to [`DefaultPackageTaskFactories()`](https://github.com/anchore/syft/blob/v1.36.0/internal/task/package_tasks.go#L58-L180) using `newSimplePackageTaskFactory` or `newPackageTaskFactory`
- Tag the task appropriately to indicate when it should run:
  - `pkgcataloging.InstalledTag` - for packages positively installed
  - `pkgcataloging.DeclaredTag` - for packages described in manifests (places where we intend to install software, but does not describe installed software)
  - `pkgcataloging.ImageTag` - should run when scanning container images
  - `pkgcataloging.DirectoryTag` - should run when scanning directories/filesystems
  - `pkgcataloging.LanguageTag` - for language-specific packages
  - `pkgcataloging.OSTag` - for OS-specific packages
  - Ecosystem tags like `"java"`, `"python"`, `"alpine"`, etc.
- If your cataloger needs configuration, add it to [`pkgcataloging.Config`](https://github.com/anchore/syft/blob/v1.36.0/syft/cataloging/pkgcataloging/config.go#L14-L23)

The task system orchestrates all catalogers through [`CreateSBOMConfig`](https://github.com/anchore/syft/blob/v1.36.0/syft/create_sbom_config.go#L20-L41),
which manages task execution, parallelism, and configuration.

`generic.NewCataloger` is an abstraction syft used to make writing common components easier (see the [alpine cataloger](https://github.com/anchore/syft/tree/v1.36.0/syft/pkg/cataloger/alpine/cataloger.go) for example usage).
It takes the following information as input:

- A `catalogerName` to identify the cataloger uniquely among all other catalogers.
- Pairs of file globs as well as parser functions to parse those files.
  These parser functions return a slice of [`pkg.Package`](https://github.com/anchore/syft/blob/v1.36.0/syft/pkg/package.go#L19) as well as a slice of [`artifact.Relationship`](https://github.com/anchore/syft/blob/v1.36.0/syft/artifact/relationship.go#L37) to describe how the returned packages are related.
  See this [the alpine cataloger parser function](https://github.com/anchore/syft/tree/v1.36.0/syft/pkg/cataloger/alpine/parse_apk_db.go#L22-L102) as an example.

Identified packages share a common `pkg.Package` struct so be sure that when the new cataloger is constructing a new package it is using the [`Package` struct](https://github.com/anchore/syft/tree/v1.36.0/syft/pkg/package.go#L16-L31).
If you want to return more information than what is available on the `pkg.Package` struct then you can do so in the `pkg.Package.Metadata` field, which accepts any type.
Metadata types tend to be unique for each [`pkg.Type`](https://github.com/anchore/syft/blob/v1.36.0/syft/pkg/type.go) but this is not required.
See [the `pkg` package](https://github.com/anchore/syft/tree/v1.36.0/syft/pkg) for examples of the different metadata types that are supported today.
When encoding to JSON, metadata type names are determined by reflection and mapped according to [`internal/packagemetadata/names.go`](https://github.com/anchore/syft/blob/v1.36.0/internal/packagemetadata/names.go#L64-L126).

Finally, here is an example of where the package construction is done within the alpine cataloger:

- [Calling the APK package constructor from the parser function](https://github.com/anchore/syft/blob/v1.36.0/syft/pkg/cataloger/alpine/parse_apk_db.go#L106)
- [The APK package constructor itself](https://github.com/anchore/syft/tree/v1.36.0/syft/pkg/cataloger/alpine/package.go#L12-L27)

{{< alert color="primary" >}}
**Interested in building a new cataloger?**

Checkout the [list of issues with the `new-cataloger` label](https://github.com/anchore/syft/issues?q=is%3Aopen+is%3Aissue+label%3Anew-cataloger+no%3Aassignee)!

If you have questions about implementing a cataloger, feel free to file an issue or reach out to us [on discourse](https://anchore.com/discourse)!
{{< /alert >}}

## Troubleshooting

### Cannot build test fixtures with Artifactory repositories

Some companies have Artifactory setup internally as a solution for sourcing secure dependencies.
If you're seeing an issue where the unit tests won't run because of the below error then this section might be relevant for your use case.

```
[ERROR] [ERROR] Some problems were encountered while processing the POMs
```

If you're dealing with an issue where the unit tests will not pull/build certain java fixtures check some of these settings:

- a `settings.xml` file should be available to help you communicate with your internal artifactory deployment
- this can be moved to `syft/pkg/cataloger/java/test-fixtures/java-builds/example-jenkins-plugin/` to help build the unit test-fixtures
- you'll also want to modify the `build-example-jenkins-plugin.sh` to use `settings.xml`

For more information on this setup and troubleshooting see [issue 1895](https://github.com/anchore/syft/issues/1895#issuecomment-1610085319)

## Next Steps

<!-- markdownlint-disable MD036 -->

**Understanding the Codebase**

- [Architecture](/docs/architecture/syft) - Learn about package structure, core library flow, cataloger design patterns, and file searching
- [API Reference](https://pkg.go.dev/github.com/anchore/syft) - Explore the public Go API, type definitions, and function signatures

**Contributing Your Work**

- [Pull Requests](/docs/contributing/pull-requests) - Guidelines for submitting PRs and working with reviewers
- [Issues and Discussions](/docs/contributing/issues-and-discussions) - Where to get help and report issues

**Finding Work**

- [New Cataloger Issues](https://github.com/anchore/syft/issues?q=is%3Aopen+is%3Aissue+label%3Anew-cataloger+no%3Aassignee) - Great first contributions for adding ecosystem support
- [Good First Issues](https://github.com/anchore/syft/issues?q=is%3Aopen%20is%3Aissue%20label%3A%22good-first-issue%22) - Beginner-friendly issues

**Getting Help**

- [Anchore Discourse](https://anchore.com/discourse) - Community discussions and questions

<!-- markdownlint-enable MD036 -->
