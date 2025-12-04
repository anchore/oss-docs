+++
title = "Vunnel"
description = "Developer guidelines when contributing to Vunnel"
weight = 28
categories = ["developer"]
tags = ["vunnel"]
menu_group = "projects"
+++

## Getting started

This project requires:

- python (>= 3.11)
- pip (>= 22.2)
- uv
- docker
- go (>= 1.20)
- posix shell (bash, zsh, etc... needed for the `make dev` "development shell")

Once you have python and uv installed, get the project bootstrapped by cloning grype, grype-db, and vunnel next to each other:

```sh
# clone grype and grype-db, which is needed for provider development
git clone git@github.com:anchore/grype.git
git clone git@github.com:anchore/grype-db.git
# note: if you already have these repos cloned, you can skip this step. However, if they
# reside in a different directory than where the vunnel repo is, then you will need to
# set the `GRYPE_PATH` and/or `GRYPE_DB_PATH` environment variables for the development
# shell to function. You can add these to a local .env file in the vunnel repo root.

# clone the vunnel repo
git clone git@github.com:anchore/vunnel.git
cd vunnel

# get basic project tooling
make bootstrap

# install project dependencies
uv sync --all-extras --dev
```

[Pre-commit](https://pre-commit.com/) is used to help enforce static analysis checks with git hooks:

```sh
uv run pre-commit install --hook-type pre-push
```

## Development environment

### Development shell

The easiest way to develop providers is to use the development shell, selecting the specific provider(s) you'd like to focus your development workflow on:

```sh
# Specify one or more providers you want to develop on.
# Any provider from the output of "vunnel list" is valid.
# Specify multiple as a space-delimited list:
# make dev providers="oracle wolfi nvd"
$ make dev provider="oracle"

Entering vunnel development shell...
• Configuring with providers: oracle ...
• Writing grype config: /Users/wagoodman/code/vunnel/.grype.yaml ...
• Writing grype-db config: /Users/wagoodman/code/vunnel/.grype-db.yaml ...
• Activating virtual env: /Users/wagoodman/code/vunnel/.venv ...
• Installing editable version of vunnel ...
• Building grype ...
• Building grype-db ...

Note: development builds grype and grype-db are now available in your path.
To update these builds run 'make build-grype' and 'make build-grype-db' respectively.
To run your provider and update the grype database run 'make update-db'.
Type 'exit' to exit the development shell.
```

The development shell provides local builds of grype and grype-db from adjacent directories. You can configure custom paths using environment variables:

```sh
# example .env file in the root of the vunnel repo
GRYPE_PATH=~/somewhere/else/grype
GRYPE_DB_PATH=~/also/somewhere/else/grype-db
```

### Example: Running make update-db

You can run the provider you specified in the `make dev` command, build an isolated grype DB, and import the DB into grype:

```
$ make update-db
• Updating vunnel providers ...
[0000]  INFO grype-db version: ede464c2def9c085325e18ed319b36424d71180d-adhoc-build
...
[0000]  INFO configured providers parallelism=1 providers=1
[0000] DEBUG   └── oracle
[0000] DEBUG all providers started, waiting for graceful completion...
[0000]  INFO running vulnerability provider provider=oracle
[0000] DEBUG oracle:  2023-03-07 15:44:13 [INFO] running oracle provider
[0000] DEBUG oracle:  2023-03-07 15:44:13 [INFO] downloading ELSA from https://linux.oracle.com/security/oval/com.oracle.elsa-all.xml.bz2
[0019] DEBUG oracle:  2023-03-07 15:44:31 [INFO] wrote 6298 entries
[0019] DEBUG oracle:  2023-03-07 15:44:31 [INFO] recording workspace state
• Building grype-db ...
[0000]  INFO grype-db version: ede464c2def9c085325e18ed319b36424d71180d-adhoc-build
[0000]  INFO reading all provider state
[0000]  INFO building DB build-directory=./build providers=[oracle] schema=5
• Packaging grype-db ...
[0000]  INFO grype-db version: ede464c2def9c085325e18ed319b36424d71180d-adhoc-build
[0000]  INFO packaging DB from="./build" for="https://toolbox-data.anchore.io/grype/databases"
[0000]  INFO created DB archive path=build/vulnerability-db_v5_2023-03-07T20:44:13Z_405ae93d52ac4cde6606.tar.gz
• Importing DB into grype ...
Vulnerability database imported
```

### Example: Scanning with the dev database

You can now run grype that uses the newly created DB:

```sh
$ grype oraclelinux:8.4
 ✔ Pulled image
 ✔ Loaded image
 ✔ Parsed image
 ✔ Cataloged packages      [195 packages]
 ✔ Scanning image...       [193 vulnerabilities]
   ├── 0 critical, 25 high, 146 medium, 22 low, 0 negligible
   └── 193 fixed

NAME                        INSTALLED                FIXED-IN                    TYPE  VULNERABILITY   SEVERITY
bind-export-libs            32:9.11.26-4.el8_4       32:9.11.26-6.el8            rpm   ELSA-2021-4384  Medium
bind-export-libs            32:9.11.26-4.el8_4       32:9.11.36-3.el8            rpm   ELSA-2022-2092  Medium
bind-export-libs            32:9.11.26-4.el8_4       32:9.11.36-3.el8_6.1        rpm   ELSA-2022-6778  High
bind-export-libs            32:9.11.26-4.el8_4       32:9.11.36-5.el8            rpm   ELSA-2022-7790  Medium

# note that we're using the database we just built...
$ grype db status
Location:  /Users/wagoodman/code/vunnel/.cache/grype/6  # <--- this is the local DB we just built
...

# also note that we're using a development build of grype
$ which grype
/Users/wagoodman/code/vunnel/bin/grype
```

### Rebuilding development tools

To rebuild the grype and grype-db binaries from local source, run:

```sh
make build-grype
make build-grype-db
```

### Recommended development workflow

For most provider development, follow this iterative workflow:

1. **Clone all three repos side-by-side**: vunnel, grype, and grype-db
2. **Enter the development shell**: `make dev provider="<your-provider>"`
3. **Make changes** to your provider code in vunnel
4. **Build and test**: Run `make update-db` to build a database with your provider's data. Run `make build-grype` or `make build-grype-db` if these tools have code changes.
5. **Validate with grype**: Scan test images to verify matching works correctly
6. **Iterate**: Adjust code and repeat steps 4-5

If you need to make changes to grype or grype-db during development, use `make build-grype` or `make build-grype-db` to rebuild with your changes.

### Common commands

This project uses Make for running common development tasks:

```sh
make                  # run static analysis and unit testing
make static-analysis  # run static analysis
make unit             # run unit tests
make format           # format the codebase
make lint-fix         # attempt to automatically fix linting errors
```

To see all available commands:

```sh
make help
```

### Snapshot tests

Many providers have snapshot tests, which assert that a fixed set of inputs will always produce the expected outputs. These tests provide end-to-end validation of the transformation logic within the vunnel provider.

Snapshot tests run as part of `make unit`.

To update snapshots, pass `--snapshot-update` to pytest:

```sh
uv run pytest ./tests/unit/providers/debian/test_debian.py -k test_provider_via_snapshot --snapshot-update
```

### Quality gate tests

All vunnel providers are protected by a quality gate. A quality gate essentially does the following:

1. Use vunnel and grype-db to build a vulnerability database
2. Use Syft to create an SBOM
3. Use grype to scan the SBOM with the vulnerability database
4. Compare the results to [known vulnerability labels](https://github.com/anchore/vulnerability-match-labels) using [yardstick](https://github.com/anchore/yardstick)

## Understanding Vunnel and Grype architecture

### Key concepts for provider authors

Before implementing a provider, understand how the pieces fit together:

#### Vulnerability matching overview

- **[Syft](https://github.com/anchore/syft)**: Catalogs packages from images/filesystems with metadata (type, name, version, distro, etc.)
- **[Vunnel](https://github.com/anchore/vunnel)**: Provides vulnerability data from various sources
- **[Grype DB](https://github.com/anchore/grype-db)**: Transforms and stores vulnerability data with ecosystem metadata
- **[Grype](https://github.com/anchore/grype)**: Matches packages against vulnerabilities in the database built by grype-db

#### Affected vs. unaffected package handles

Grype uses two types of package records:

- **Affected**: "If a package meets this version constraint, it IS vulnerable"
- **Unaffected**: "If a package meets this version constraint, it is NOT vulnerable"

Most providers emit affected package records. Some providers (like AlmaLinux) emit unaffected records to filter matches from other sources (Red Hat in AlmaLinux's case).

**Examples in code:**

- Affected packages: Most distro providers (Red Hat, Debian, Ubuntu, etc.)
- Unaffected packages: [AlmaLinux matcher](https://github.com/anchore/grype/blob/main/grype/matcher/rpm/almalinux.go), [OSV transformer](https://github.com/anchore/grype-db/blob/main/pkg/process/v6/transformers/osv/transform.go#L61-L71)

#### Schemas

Vulnerability data must conform to a structured schema. Vunnel supports several schemas including OSV, OpenVEX, NVD, and GitHub Security Advisory. Schema selection is covered in detail below.

### Architecture details

For detailed information about Vunnel's internal architecture, including provider abstraction, workspace conventions, and integration with Grype DB, see the [Vunnel Architecture](/docs/architecture/vunnel) page.

## Adding a new provider

### Before you start: Understanding requirements

#### Schema selection

{{< alert color="primary" >}}
**Choosing the right schema**

Legacy Vunnel providers emit vulnerabilities in the OS schema, but generally, new providers should use an externally specified schema like OSV or OpenVEX.
{{< /alert >}}

**Schema preference hierarchy for new providers:**

1. **OSV** (strongly preferred) - Use for most vulnerability data
2. **Other externally specified schemas** - OpenVEX, CSAF VEX, etc.
3. **Existing internal schemas** - NVD, GitHub Security Advisory, OS (only if data naturally fits)
4. **Custom schemas** - Requires discussion with maintainers

**Why we prefer externally specified schemas:**

- Based on open standards (OSV, OpenVEX, CSAF)
- Better interoperability with other tools
- Reduced maintenance burden
- Broader ecosystem support

The OS schema is an internal format that exists primarily to support legacy providers. While it's still supported, we encourage new providers to use externally specified schemas when possible.

**Decision tree: What schema should my provider use?**

- Source already provides OSV format? → **Use OSV**
- Easy to transform to OSV without data loss? → **Use OSV**
- Source already uses an externally specified format (OpenVEX, CSAF VEX, etc.)? → **Probably use that format** (may need to add a transformer to grype-db; check with maintainers in an issue)
- Not already in an external format and not easy to make into OSV? → **Check with maintainers in an issue**

**Schema resources:**

- [OSV Schema Documentation](https://ossf.github.io/osv-schema/)
- [OpenVEX Specification](https://github.com/openvex/spec)
- [CSAF VEX](https://docs.oasis-open.org/csaf/csaf/v2.0/csaf-v2.0.html)
- OSV examples in Vunnel: See providers in [src/vunnel/providers](https://github.com/anchore/vunnel/tree/main/src/vunnel/providers)

#### Key questions before implementing

Before implementing a provider, answer these questions to understand what changes will be needed:

**1. Can Syft identify which packages should be matched against your data?**

This is critical—Grype needs to know when to use your vulnerability data. Examples:

- **New Linux distro**: Does the distro have something distinctive in `/etc/os-release` that Syft can detect? (Concretely, does `syft -o json my-test-image | jq .distro` produce something correct and specific to your vulnerability feed?)
- **Vendor-specific patches**: Do patched packages have a distinctive version pattern (e.g., `.<vendor_name>` in dpkg versions)?
- **Language ecosystem**: Does your data apply to all packages from a specific package manager?

If Syft can't distinguish your packages, you may need changes to Syft first. See [contributing to Syft](/docs/contributing/syft).

**2. Do you have public test artifacts?**

You **must** have publicly accessible test images or artifacts that:

- Contain packages your provider has data for
- Can be scanned by Syft
- Can be used in CI/CD for ongoing validation

Without test artifacts, we cannot validate that your provider works correctly.

**3. Is your vulnerability feed comprehensive or supplementary?**

- **Comprehensive**: Contains both vulnerability disclosures AND fixes (e.g., most Linux distro security advisories, GHSA)
- **Supplementary**: Contains only fixes that layer over another source (e.g., AlmaLinux provides fixes on top of Red Hat data; Alpine SecDB provides fixes on top of NVD CVE data)

Supplementary feeds typically require additional Grype changes to filter existing matches.

**4. What schema is your vulnerability data available in?**

- **Already OSV?** Great—minimal work needed
- **Already in another external format (OpenVEX, CSAF, etc.)?** May need to add a transformer to grype-db
- **Custom format?** You'll need to transform it to an external schema (preferably OSV)

See the schema selection section above for guidance.

**5. How should Vunnel retrieve your data?**

**Important**: Vunnel must be able to enumerate and fetch the entire vulnerability feed. APIs that only provide individual vulnerability lookups (e.g., `GET /vuln-id` without a `GET /all-vulns` endpoint) are very difficult to integrate.

Common patterns:

- **Downloadable archive** (tar.gz, zip, etc. with vulnerability data)—provide the URL
- **Public HTTP API** with enumeration support—provide the endpoint
- **Public Git repository** (with JSON/YAML/XML files)—provide the repo URL
- **Requires authentication or special access?** Discuss with maintainers in an issue

**What these answers tell you:**

- **Syft changes needed?** Question 1
- **Grype changes needed?** Questions 1 and 3
- **Grype DB changes needed?** Question 4
- **Feasibility?** Question 2 is a hard requirement
- **Complexity?** All questions together determine overall complexity

If you're unsure about any of these, open an issue to discuss with maintainers before starting implementation.

#### Initial prerequisites

"Vulnerability matching" is the process of taking a list of vulnerabilities and matching them against a list of packages. A provider in this repo is responsible for the "vulnerability" side of this process. The "package" side is handled by [Syft](https://github.com/anchore/syft). A prerequisite for adding a new provider is that Syft can catalog the package types that the provider is feeding vulnerability data for, so [Grype](https://github.com/anchore/grype) can perform the matching from these two sources.

For a detailed example on the implementation details of a provider, see the ["example" provider](https://github.com/anchore/vunnel/blob/main/example/README.md).

### Understanding multi-repository coordination

{{< alert color="primary" >}}
**Adding a new provider often requires PRs in multiple repositories.**

Depending on your answers to the key questions above, you may need PRs in vunnel, grype-db, and grype. This is normal and expected.
{{< /alert >}}

**Recommended approach:**

1. **Set up all three repos as siblings**: Clone vunnel, grype, and grype-db in the same parent directory
2. **Make changes across all needed repos**: Create branches in each repo that needs changes
3. **Test locally with the dev shell**: Use `make dev provider=<your-new-provider>` in vunnel, which will use your local grype and grype-db branches
4. **Validate end-to-end**: Run `make update-db` and then `grype <your-test-artifacts>` to verify matching works correctly
5. **Open PRs in all repos**: When your local branches work together correctly, open PRs. If possible, make sure maintainers have permission to edit your PRs.
6. **Add quality gate tests**: Add a block to [`tests/quality/config.yaml`](https://github.com/anchore/vunnel/blob/main/tests/quality/config.yaml) that exercises your provider. You may need to temporarily make `config.yaml` point to your branches of Grype or Grype-DB in order for the validation to pass.
7. **Maintainers coordinate merging**: Once all PRs are approved, maintainers will coordinate getting them merged and update version references

**Which PRs do you need?**

- **Vunnel PR**: Always needed—implements the provider and emits vulnerability data
- **Grype DB PR**: Needed if adding a new schema transformer (may not be needed for OSV, OpenVEX, etc.)
- **Grype PR**: Needed if adding new matching logic, distro types, or filtering behavior

Don't be discouraged by the multi-repo requirement—this is a well-established workflow. Open draft PRs early and maintainers can help guide you through the process.

### Step-by-step: Implementing your provider

#### Step 1: Prove Syft can find your artifacts

Before implementing anything, verify that Syft can catalog the packages you want to provide vulnerability data for:

```sh
syft -q <your-test-image> | grep <expected-pattern>
# You should see packages that your provider will have data for
```

For distro-specific providers, verify Syft detects the distro correctly:

```sh
syft -o json <your-test-image> | jq .distro
# Should show the correct distro name and version
```

If Syft can't find your packages or detect your distro, you may need Syft changes before proceeding. Generally, we are happy for Syft to learn to parse new distros and package types. See [contributing to Syft](/docs/contributing/syft).

#### Step 2: Find or create test artifacts showing incorrect matching

Identify concrete test cases that your provider will fix. Run Grype on your test artifact:

```sh
grype <your-test-artifact>
```

Document what's wrong:

- **Missing vulnerabilities**: Grype should report CVE-X for package Y but doesn't
- **False positives**: Grype reports CVE-X for package Y but shouldn't (e.g., the package is patched)

These incorrect matches are what you'll use to validate your provider works correctly.

#### Step 3: Set up the three-repo workspace

Clone vunnel, grype, and grype-db as siblings in the same parent directory:

```sh
# Fork the repos on GitHub first, then:
git clone git@github.com:your-username/vunnel.git
git clone git@github.com:your-username/grype.git
git clone git@github.com:your-username/grype-db.git

# Or clone from upstream and add forks as remotes:
cd vunnel
git remote add fork git@github.com:your-username/vunnel.git
# (repeat for grype and grype-db)
```

Create branches in each repo where you'll make changes:

```sh
cd vunnel
git checkout -b add-my-provider

cd ../grype
git checkout -b support-my-provider

cd ../grype-db
git checkout -b transform-my-provider-data
```

#### Step 4: Implement the Vunnel provider

Take a look at the example provider in the `example` directory. You are encouraged to copy it as a starting point:

```sh
# from the root of the vunnel repo
cp -a example/awesome src/vunnel/providers/YOURPROVIDERNAME
```

See the ["example" provider README](https://github.com/anchore/vunnel/blob/main/example/README.md) for detailed guidance.

**Core implementation requirements:**

Create a provider class under `/src/vunnel/providers/<name>` that inherits from `provider.Provider` and implements:

- `name()`: A unique and semantically-useful name for the provider
- `update()`: Downloads and processes raw data, writing all results with `self.results_writer()`

**Wire up your provider:**

- Add an entry to the dispatch table in `src/vunnel/providers/__init__.py` mapping your provider name to the class
- Add provider configuration to `src/vunnel/cli/config.py` (specifically the `Providers` dataclass)

**Validation:**

```sh
vunnel list  # Should show your provider
vunnel run <your-provider-name>  # Should execute successfully
```

{{< alert color="primary" >}}
**Need help with your provider?**

At this point you can open a draft Vunnel PR and ask maintainers for guidance on the next steps.
{{< /alert >}}

#### Step 5: Implement Grype DB changes (if needed)

**When needed:**

If your provider uses a schema that doesn't already have a transformer, add one in grype-db:

- Add unmarshaling logic in `pkg/provider/unmarshal`
- Add processing/transformation logic in `pkg/process/v6` (the v5 data is only consumed by old versions of Grype, and new providers generally should not change v5 or older code in Grype DB)

**Note:** For OSV and OpenVEX, transformers already exist—check [grype-db transformers](https://github.com/anchore/grype-db/tree/main/pkg/process/v6/transformers).

**Test the data flow:**

Use the dev shell to test that your vulnerability data flows into Grype's database:

```sh
cd vunnel
make dev provider="<your-provider-name>"

# This enters a shell with local builds of grype and grype-db
make update-db

# Check that data was imported (you can inspect the SQLite database if needed)
```

#### Step 6: Determine if Grype changes are needed

Test whether Grype automatically picks up your new data:

```sh
# In the dev shell from step 5
grype <your-test-artifact>
```

Compare against the incorrect matches you documented in step 2. If Grype now correctly reports previously missing vulnerabilities or filters out false positives, you're done with Grype changes—skip to step 7.

**Common reasons for needing Grype changes:**

- Grype does not support the distro type and it needs to be added. See the [grype/distro/type.go](https://github.com/anchore/grype/blob/main/grype/distro/type.go) file to add the new distro.
- Grype supports the distro already, but matching is disabled. See the [grype/distro/distro.go](https://github.com/anchore/grype/blob/main/grype/distro/distro.go) file to enable the distro explicitly.
- Supplementary fixes require filtering logic. See the [AlmaLinux matcher example](https://github.com/anchore/grype/blob/main/grype/matcher/rpm/almalinux.go).

**Implement and test:**

If you're using the developer shell (`make dev ...`) then you can run `make build-grype` to get a build of grype with your changes, then test again with `grype <your-test-artifact>`.

**Note:** Steps 5 and 6 are iterative—you may go back and forth between provider implementation, grype-db transformers, and grype matchers until everything works correctly.

#### Step 7: Add test configuration

Add your provider and test images to `tests/quality/config.yaml`:

```yaml
- provider: your-provider-name
  images:
    - docker.io/yourorg/test:tag@sha256:digest
```

These images are used to test the provider on PRs and nightly builds to verify the provider is working. Always use both the image tag and digest for all container image entries. Pick an image that has a good representation of the package types that your new provider is adding vulnerability data for.

**Before continuing, validate your test images:**

```sh
syft -q <your-test-image> | grep <expected-pattern>
# You should see packages that your provider has vulnerability data for
```

**Common mistake:** Test images that don't contain relevant packages. Always verify before proceeding!

#### Step 8: Update quality gate configuration for your branches

If you have Grype or Grype DB changes, update the `yardstick.tools[*]` entries in `tests/quality/config.yaml` to use versions that point to your fork:

```yaml
yardstick:
  tools:
    - name: grype
      version: your-username/grype@your-branch-name
      # ...
  # (similar for grype-db if needed)
```

If you don't have any grype or grype-db changes, you can skip this step.

#### Step 9: Add vulnerability match labels

In order to evaluate the quality of the new provider, we need to know what the expected results are. This is done by annotating Grype results with "True Positive" labels (good results) and "False Positive" labels (bad results). We'll use [Yardstick](https://github.com/anchore/yardstick) to do this:

```sh
cd tests/quality

# Capture results with the development version of grype (from your fork)
make capture provider=<your-provider-name>

# List your results
uv run yardstick result list | grep grype

d415064e-2bf3-4a1d-bda6-9c3957f2f71a  docker.io/anc...  grype@v0.58.0             2023-03...
75d1fe75-0890-4d89-a497-b1050826d9f6  docker.io/anc...  grype[custom-db]@bdcefd2  2023-03...

# Use the "grype[custom-db]" result UUID and explore the results and add labels to each entry
uv run yardstick label explore 75d1fe75-0890-4d89-a497-b1050826d9f6
```

**In the Yardstick TUI:**

- Press `T` to label a row as a True Positive (correct match)
- Press `F` to label a row as a False Positive (incorrect match)
- Press `Ctrl-Z` to undo a label
- Press `Ctrl-S` to save your labels
- Press `Ctrl-C` to quit when you are done

Later we'll open a PR in the [vulnerability-match-labels repo](https://github.com/anchore/vulnerability-match-labels) to persist these labels. For the meantime we can iterate locally with the labels we've added.

#### Step 10: Run the quality gate

```sh
cd tests/quality

# Runs your specific provider to gather vulnerability data, builds a DB, and runs grype with the new DB
make capture provider=<your-provider-name>

# Evaluate the quality gate
make validate
```

This uses the latest Grype DB release to build a DB and the specified Grype version with a DB containing only data from the new provider.

You are looking for a passing run before continuing further.

**Troubleshooting:**

- **Quality gate failing?** Check that labels are correctly applied
- **Matches not appearing?** Verify your provider is writing data correctly
- **Images not scanning?** Verify test image accessibility and digests

#### Step 11: Persist labels to vulnerability-match-labels repo

Vunnel uses the labels in the [vulnerability-match-labels repo](https://github.com/anchore/vulnerability-match-labels) via a git submodule. We've already added labels locally within this submodule in an earlier step. To persist these labels we need to push them to a fork and open a PR:

```sh
# Fork the github.com/anchore/vulnerability-match-labels repo, but you do not need to clone it...

# From the Vunnel repo...
cd tests/quality/vulnerability-match-labels

git remote add fork git@github.com:your-fork-name/vulnerability-match-labels.git
git checkout -b 'add-labels-for-<your-provider-name>'
git status

# You should see changes from the labels/ directory for your provider that you added
git add .
git commit -m 'add labels for <your-provider-name>'
git push fork add-labels-for-<your-provider-name>
```

At this point you can open a PR in the [vulnerability-match-labels repo](https://github.com/anchore/vulnerability-match-labels).

**Note:** You will not be able to open a Vunnel PR that passes PR checks until the labels are merged into the vulnerability-match-labels repo.

Once the PR is merged in the vulnerability-match-labels repo you can update the submodule in Vunnel to point to the latest commit in the vulnerability-match-labels repo:

```sh
cd tests/quality
git submodule update --remote vulnerability-match-labels
```

#### Step 12: Open PRs in all repos

**Open PRs in all repos where you made changes:**

- **Vunnel PR**: Always needed
- **Grype DB PR**: If you added transformer logic
- **Grype PR**: If you added matching logic

The PR will also run all of the same quality gate checks that you ran locally.

**In your PR descriptions:**

- Link to the related PRs in other repos
- Describe what incorrect matching behavior this fixes
- Reference your test artifacts
- Note the test images you added to config.yaml

**Before the Vunnel PR can merge:**

- Grype DB PR must be merged (if you have one)
- Grype PR must be merged (if you have one)
- Vulnerability-match-labels PR must be merged
- Update `tests/quality/config.yaml` to point back to the `latest` versions (not branch names)

**Getting help:**

Open draft PRs early and ask maintainers for guidance. Maintainers are experienced with multi-repo coordination and can help you navigate the process. Maintainers may take over coordination and merge the PRs.

### Adding a provider with a new schema

If you're adding a provider that uses a completely new schema (not OSV, OpenVEX, etc.), follow the steps above with these additional requirements:

1. You will need to add the new schema to the Vunnel repo in the `schemas` directory
2. Grype DB will need to be updated to support the new schema in the `pkg/provider/unmarshal` and `pkg/process/v*` directories
3. The Vunnel `tests/quality/config.yaml` file will need to be updated to use development `grype-db.version`, pointing to your fork
4. The final Vunnel PR will not be able to be merged until the Grype DB PR is merged and the `tests/quality/config.yaml` file is updated to point back to the `latest` Grype DB version

**Consider carefully:** Adding a new schema is complex and increases maintenance burden. Prefer externally specified schemas like OSV whenever possible.

## Troubleshooting

### My test image doesn't show any packages

```sh
# Verify the image contains expected packages
syft -q <image> | grep <pattern>

# Check the package type
syft -q <image> -o json | jq '.artifacts[] | select(.name=="<pkg>") | .type'

# Verify the image is accessible
docker pull <image>
```

If packages aren't appearing, the image may not contain what you expect. Review your test image selection.

### Quality gate is failing

- Verify labels are correctly applied (T for true positive, F for false positive)
- Check that test images are accessible and have correct digests
- Ensure grype and grype-db versions in `config.yaml` are correct
- Run `make capture` and manually inspect the results with `uv run yardstick result list`

### Grype isn't matching my vulnerabilities

- **Check your provider's output**: Use `vunnel run <name>` and inspect the generated data
- **Verify schema conformance**: Ensure your data matches the schema you've chosen
- **Check Grype DB transformation**: Inspect the generated SQLite database to see if data was transformed correctly
- **Add debug logging**: Use the dev shell and add logging to Grype matchers to understand why matches aren't happening
- **Verify package metadata**: Ensure Syft is cataloging packages with the metadata your matcher needs

### I'm not sure if I need Grype changes

- Try running end-to-end in the dev shell first (`make update-db`, then scan an image)
- If matching doesn't work as expected, you likely need Grype changes
- Look for similar providers and see what Grype changes they required
- Ask a maintainer in a draft PR—they can help you determine what's needed

### Getting help

- **Open a draft PR** with your progress so far
- **Include specific questions or blockers** you're encountering
- **Share test images** so maintainers can reproduce issues
- Maintainers are happy to help guide you through the process
- Expect response within a few business days

## Next Steps

<!-- markdownlint-disable MD036 -->

**Understanding the Codebase**

- [Vunnel Architecture](/docs/architecture/vunnel) - Learn about provider abstraction, workspace conventions, and vulnerability schemas
- [Example Provider](https://github.com/anchore/vunnel/blob/main/example/README.md) - Detailed walkthrough of creating a new provider

**Contributing Your Work**

- [Pull Requests](/docs/contributing/pull-requests) - Guidelines for submitting PRs and working with reviewers
- [Issues and Discussions](/docs/contributing/issues-and-discussions) - Where to get help and report issues

**Finding Work**

- [New Provider Issues](https://github.com/anchore/vunnel/issues?q=is%3Aopen+is%3Aissue+label%3Anew-provider) - Add support for new vulnerability data sources
- [Refactoring Issues](https://github.com/anchore/vunnel/issues?q=is%3Aissue+is%3Aopen+label%3Arefactor) - Help improve code quality
- [Good First Issues](https://github.com/anchore/vunnel/issues?q=is%3Aopen%20is%3Aissue%20label%3A%22good-first-issue%22) - Beginner-friendly issues

**Getting Help**

- [Anchore Discourse](https://anchore.com/discourse) - Community discussions and questions

<!-- markdownlint-enable MD036 -->
