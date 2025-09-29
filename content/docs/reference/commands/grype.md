+++
title = "Grype Command Line Reference"
linkTitle = "Grype CLI"
weight = 20
tags = ['grype']
categories = ['reference']
url = "docs/reference/commands/grype"
+++

### `grype version`

```
Application:         grype
Version:             0.100.0
BuildDate:           2025-09-15T21:51:57Z
GitCommit:           088112b26e638c139a513f387f7a6e51f1a8b76d
GitDescription:      v0.100.0
Platform:            linux/arm64
GoVersion:           go1.24.7
Compiler:            gc
Syft Version:        v1.33.0
Supported DB Schema: 6
```

### `grype help`

```
A vulnerability scanner for container images, filesystems, and SBOMs.

Supports the following image sources:
    grype yourrepo/yourimage:tag             defaults to using images from a Docker daemon
    grype path/to/yourproject                a Docker tar, OCI tar, OCI directory, SIF container, or generic filesystem directory

You can also explicitly specify the scheme to use:
    grype podman:yourrepo/yourimage:tag          explicitly use the Podman daemon
    grype docker:yourrepo/yourimage:tag          explicitly use the Docker daemon
    grype docker-archive:path/to/yourimage.tar   use a tarball from disk for archives created from "docker save"
    grype oci-archive:path/to/yourimage.tar      use a tarball from disk for OCI archives (from Podman or otherwise)
    grype oci-dir:path/to/yourimage              read directly from a path on disk for OCI layout directories (from Skopeo or otherwise)
    grype singularity:path/to/yourimage.sif      read directly from a Singularity Image Format (SIF) container on disk
    grype dir:path/to/yourproject                read directly from a path on disk (any directory)
    grype file:path/to/yourfile                  read directly from a file on disk
    grype sbom:path/to/syft.json                 read Syft JSON from path on disk
    grype registry:yourrepo/yourimage:tag        pull image directly from a registry (no container runtime required)
    grype purl:path/to/purl/file                 read a newline separated file of package URLs from a path on disk
    grype PURL                                   read a single package PURL directly (e.g. pkg:apk/openssl@3.2.1?distro=alpine-3.20.3)
    grype CPE                                    read a single CPE directly (e.g. cpe:2.3:a:openssl:openssl:3.0.14:*:*:*:*:*)

You can also pipe in Syft JSON directly:
 syft yourimage:tag -o json | grype

Usage:
  grype [IMAGE] [flags]
  grype [command]

Available Commands:
  completion  Generate a shell completion for Grype (listing local docker images)
  config      show the grype configuration
  db          vulnerability database operations
  explain     Ask grype to explain a set of findings
  help        Help about any command
  version     show version information

Flags:
      --add-cpes-if-none       generate CPEs for packages with no CPE data
      --by-cve                 orient results by CVE instead of the original vulnerability ID when possible
  -c, --config stringArray     grype configuration file(s) to use
      --distro string          distro to match against in the format: <distro>:<version>
      --exclude stringArray    exclude paths from being scanned using a glob expression
  -f, --fail-on string         set the return code to 1 if a vulnerability is found with a severity >= the given severity, options=[negligible low medium high critical]
      --file string            file to write the default report output to (default is STDOUT)
  -h, --help                   help for grype
      --ignore-states string   ignore matches for vulnerabilities with specified comma separated fix states, options=[fixed not-fixed unknown wont-fix]
      --name string            set the name of the target being analyzed
      --only-fixed             ignore matches for vulnerabilities that are not fixed
      --only-notfixed          ignore matches for vulnerabilities that are fixed
  -o, --output stringArray     report output formatter, formats=[json table cyclonedx cyclonedx-json sarif template], deprecated formats=[embedded-cyclonedx-vex-json embedded-cyclonedx-vex-xml]
      --platform string        an optional platform specifier for container image sources (e.g. 'linux/arm64', 'linux/arm64/v8', 'arm64', 'linux')
      --profile stringArray    configuration profiles to use
  -q, --quiet                  suppress all logging output
  -s, --scope string           selection of layers to analyze, options=[squashed all-layers deep-squashed] (default "squashed")
      --show-suppressed        show suppressed/ignored vulnerabilities in the output (only supported with table output format)
      --sort-by string         sort the match results with the given strategy, options=[package severity epss risk kev vulnerability] (default "risk")
  -t, --template string        specify the path to a Go template file (requires 'template' output to be selected)
  -v, --verbose count          increase verbosity (-v = info, -vv = debug)
      --version                version for grype
      --vex stringArray        a list of VEX documents to consider when producing scanning results

Use "grype [command] --help" for more information about a command.
```

### `grype config`

```
log:
  # suppress all logging output (env: GRYPE_LOG_QUIET)
  quiet: false

  # explicitly set the logging level (available: [error warn info debug trace]) (env: GRYPE_LOG_LEVEL)
  level: 'warn'

  # file path to write logs to (env: GRYPE_LOG_FILE)
  file: ''

dev:
  # capture resource profiling data (available: [cpu, mem]) (env: GRYPE_DEV_PROFILE)
  profile: ''

  db:
    # (env: GRYPE_DEV_DB_DEBUG)
    debug: false

# the output format of the vulnerability report (options: table, template, json, cyclonedx)
# when using template as the output type, you must also provide a value for 'output-template-file' (env: GRYPE_OUTPUT)
output: []

# if using template output, you must provide a path to a Go template file
# see https://github.com/anchore/grype#using-templates for more information on template output
# the default path to the template file is the current working directory
# output-template-file: .grype/html.tmpl
#
# write output report to a file (default is to write to stdout) (env: GRYPE_FILE)
file: ''

# pretty-print output (env: GRYPE_PRETTY)
pretty: false

# distro to match against in the format: <distro>:<version> (env: GRYPE_DISTRO)
distro: ''

# generate CPEs for packages with no CPE data (env: GRYPE_ADD_CPES_IF_NONE)
add-cpes-if-none: false

# specify the path to a Go template file (requires 'template' output to be selected) (env: GRYPE_OUTPUT_TEMPLATE_FILE)
output-template-file: ''

# enable/disable checking for application updates on startup (env: GRYPE_CHECK_FOR_APP_UPDATE)
check-for-app-update: true

# ignore matches for vulnerabilities that are not fixed (env: GRYPE_ONLY_FIXED)
only-fixed: false

# ignore matches for vulnerabilities that are fixed (env: GRYPE_ONLY_NOTFIXED)
only-notfixed: false

# ignore matches for vulnerabilities with specified comma separated fix states, options=[fixed not-fixed unknown wont-fix] (env: GRYPE_IGNORE_WONTFIX)
ignore-wontfix: ''

# an optional platform specifier for container image sources (e.g. 'linux/arm64', 'linux/arm64/v8', 'arm64', 'linux') (env: GRYPE_PLATFORM)
platform: ''

search:
  # selection of layers to analyze, options=[squashed all-layers deep-squashed] (env: GRYPE_SEARCH_SCOPE)
  scope: 'squashed'

  # search within archives that do not contain a file index to search against (tar, tar.gz, tar.bz2, etc)
  # note: enabling this may result in a performance impact since all discovered compressed tars will be decompressed
  # note: for now this only applies to the java package cataloger (env: GRYPE_SEARCH_UNINDEXED_ARCHIVES)
  unindexed-archives: false

  # search within archives that do contain a file index to search against (zip)
  # note: for now this only applies to the java package cataloger (env: GRYPE_SEARCH_INDEXED_ARCHIVES)
  indexed-archives: true

# A list of vulnerability ignore rules, one or more property may be specified and all matching vulnerabilities will be ignored.
# This is the full set of supported rule fields:
#   - vulnerability: CVE-2008-4318
#     fix-state: unknown
#     package:
#       name: libcurl
#       version: 1.5.1
#       type: npm
#       location: "/usr/local/lib/node_modules/**"
#
# VEX fields apply when Grype reads vex data:
#   - vex-status: not_affected
#     vex-justification: vulnerable_code_not_present
ignore: []

# a list of globs to exclude from scanning, for example:
#   - '/etc/**'
#   - './out/**/*.json'
# same as --exclude (env: GRYPE_EXCLUDE)
exclude: []

external-sources:
  # enable Grype searching network source for additional information (env: GRYPE_EXTERNAL_SOURCES_ENABLE)
  enable: false

  maven:
    # search for Maven artifacts by SHA1 (env: GRYPE_EXTERNAL_SOURCES_MAVEN_SEARCH_MAVEN_UPSTREAM)
    search-maven-upstream: true

    # base URL of the Maven repository to search (env: GRYPE_EXTERNAL_SOURCES_MAVEN_BASE_URL)
    base-url: 'https://search.maven.org/solrsearch/select'

    # (env: GRYPE_EXTERNAL_SOURCES_MAVEN_RATE_LIMIT)
    rate-limit: 300ms

match:
  java:
    # use CPE matching to find vulnerabilities (env: GRYPE_MATCH_JAVA_USING_CPES)
    using-cpes: false

  jvm:
    # (env: GRYPE_MATCH_JVM_USING_CPES)
    using-cpes: true

  dotnet:
    # use CPE matching to find vulnerabilities (env: GRYPE_MATCH_DOTNET_USING_CPES)
    using-cpes: false

  golang:
    # use CPE matching to find vulnerabilities (env: GRYPE_MATCH_GOLANG_USING_CPES)
    using-cpes: false

    # use CPE matching to find vulnerabilities for the Go standard library (env: GRYPE_MATCH_GOLANG_ALWAYS_USE_CPE_FOR_STDLIB)
    always-use-cpe-for-stdlib: true

    # allow comparison between main module pseudo-versions (e.g. v0.0.0-20240413-2b432cf643...) (env: GRYPE_MATCH_GOLANG_ALLOW_MAIN_MODULE_PSEUDO_VERSION_COMPARISON)
    allow-main-module-pseudo-version-comparison: false

  javascript:
    # use CPE matching to find vulnerabilities (env: GRYPE_MATCH_JAVASCRIPT_USING_CPES)
    using-cpes: false

  python:
    # use CPE matching to find vulnerabilities (env: GRYPE_MATCH_PYTHON_USING_CPES)
    using-cpes: false

  ruby:
    # use CPE matching to find vulnerabilities (env: GRYPE_MATCH_RUBY_USING_CPES)
    using-cpes: false

  rust:
    # use CPE matching to find vulnerabilities (env: GRYPE_MATCH_RUST_USING_CPES)
    using-cpes: false

  stock:
    # use CPE matching to find vulnerabilities (env: GRYPE_MATCH_STOCK_USING_CPES)
    using-cpes: true

# upon scanning, if a severity is found at or above the given severity then the return code will be 1
# default is unset which will skip this validation (options: negligible, low, medium, high, critical) (env: GRYPE_FAIL_ON_SEVERITY)
fail-on-severity: ''

registry:
  # skip TLS verification when communicating with the registry (env: GRYPE_REGISTRY_INSECURE_SKIP_TLS_VERIFY)
  insecure-skip-tls-verify: false

  # use http instead of https when connecting to the registry (env: GRYPE_REGISTRY_INSECURE_USE_HTTP)
  insecure-use-http: false

  # Authentication credentials for specific registries. Each entry describes authentication for a specific authority:
  # - authority: the registry authority URL the URL to the registry (e.g. "docker.io", "localhost:5000", etc.) (env: SYFT_REGISTRY_AUTH_AUTHORITY)
  #  username: a username if using basic credentials (env: SYFT_REGISTRY_AUTH_USERNAME)
  #  password: a corresponding password (env: SYFT_REGISTRY_AUTH_PASSWORD)
  #  token: a token if using token-based authentication, mutually exclusive with username/password (env: SYFT_REGISTRY_AUTH_TOKEN)
  #  tls-cert: filepath to the client certificate used for TLS authentication to the registry (env: SYFT_REGISTRY_AUTH_TLS_CERT)
  #  tls-key: filepath to the client key used for TLS authentication to the registry (env: SYFT_REGISTRY_AUTH_TLS_KEY)
  auth: []

  # filepath to a CA certificate (or directory containing *.crt, *.cert, *.pem) used to generate the client certificate (env: GRYPE_REGISTRY_CA_CERT)
  ca-cert: ''

# show suppressed/ignored vulnerabilities in the output (only supported with table output format) (env: GRYPE_SHOW_SUPPRESSED)
show-suppressed: false

# orient results by CVE instead of the original vulnerability ID when possible (env: GRYPE_BY_CVE)
by-cve: false

# sort the match results with the given strategy, options=[package severity epss risk kev vulnerability] (env: GRYPE_SORT_BY)
sort-by: 'risk'

# same as --name; set the name of the target being analyzed (env: GRYPE_NAME)
name: ''

# allows users to specify which image source should be used to generate the sbom
# valid values are: registry, docker, podman (env: GRYPE_DEFAULT_IMAGE_PULL_SOURCE)
default-image-pull-source: ''

# a list of VEX documents to consider when producing scanning results (env: GRYPE_VEX_DOCUMENTS)
vex-documents: []

# VEX statuses to consider as ignored rules (env: GRYPE_VEX_ADD)
vex-add: []

# match kernel-header packages with upstream kernel as kernel vulnerabilities (env: GRYPE_MATCH_UPSTREAM_KERNEL_HEADERS)
match-upstream-kernel-headers: false

fix-channel:
  redhat-eus:
    # whether fixes from this channel should be considered, options are "never", "always", or "auto" (conditionally applied based on SBOM data) (env: GRYPE_FIX_CHANNEL_REDHAT_EUS_APPLY)
    apply: 'auto'

    # (env: GRYPE_FIX_CHANNEL_REDHAT_EUS_VERSIONS)
    versions: '>= 8.0'

# (env: GRYPE_TIMESTAMP)
timestamp: true

db:
  # location to write the vulnerability database cache (env: GRYPE_DB_CACHE_DIR)
  cache-dir: '~.cache~grype~db'

  # URL of the vulnerability database (env: GRYPE_DB_UPDATE_URL)
  update-url: 'https://grype.anchore.io/databases'

  # certificate to trust download the database and listing file (env: GRYPE_DB_CA_CERT)
  ca-cert: ''

  # check for database updates on execution (env: GRYPE_DB_AUTO_UPDATE)
  auto-update: true

  # validate the database matches the known hash each execution (env: GRYPE_DB_VALIDATE_BY_HASH_ON_START)
  validate-by-hash-on-start: true

  # ensure db build is no older than the max-allowed-built-age (env: GRYPE_DB_VALIDATE_AGE)
  validate-age: true

  # Max allowed age for vulnerability database,
  # age being the time since it was built
  # Default max age is 120h (or five days) (env: GRYPE_DB_MAX_ALLOWED_BUILT_AGE)
  max-allowed-built-age: 120h0m0s

  # fail the scan if unable to check for database updates (env: GRYPE_DB_REQUIRE_UPDATE_CHECK)
  require-update-check: false

  # Timeout for downloading GRYPE_DB_UPDATE_URL to see if the database needs to be downloaded
  # This file is ~156KiB as of 2024-04-17 so the download should be quick; adjust as needed (env: GRYPE_DB_UPDATE_AVAILABLE_TIMEOUT)
  update-available-timeout: 30s

  # Timeout for downloading actual vulnerability DB
  # The DB is ~156MB as of 2024-04-17 so slower connections may exceed the default timeout; adjust as needed (env: GRYPE_DB_UPDATE_DOWNLOAD_TIMEOUT)
  update-download-timeout: 5m0s

  # Maximum frequency to check for vulnerability database updates (env: GRYPE_DB_MAX_UPDATE_CHECK_FREQUENCY)
  max-update-check-frequency: 2h0m0s

exp:
```

### `grype db`

```
vulnerability database operations

Usage:
  grype db [command]

Available Commands:
  check       Check to see if there is a database update available
  delete      Delete the vulnerability database
  import      Import a vulnerability database or archive from a local file or URL
  list        List all DBs available according to the listing URL
  providers   List vulnerability providers that are in the database
  search      Search the DB for vulnerabilities or affected packages
  status      Display database status and metadata
  update      Download and install the latest vulnerability database

Flags:
  -h, --help   help for db

Global Flags:
  -c, --config stringArray    grype configuration file(s) to use
      --profile stringArray   configuration profiles to use
  -q, --quiet                 suppress all logging output
  -v, --verbose count         increase verbosity (-v = info, -vv = debug)

Use "grype db [command] --help" for more information about a command.
```

### `grype db check`

```
Check to see if there is a database update available

Usage:
  grype db check [flags]

Flags:
  -h, --help            help for check
  -o, --output string   format to display results (available=[text, json]) (default "text")

Global Flags:
  -c, --config stringArray    grype configuration file(s) to use
      --profile stringArray   configuration profiles to use
  -q, --quiet                 suppress all logging output
  -v, --verbose count         increase verbosity (-v = info, -vv = debug)
```

### `grype db delete`

```
Delete the vulnerability database

Usage:
  grype db delete [flags]

Flags:
  -h, --help   help for delete

Global Flags:
  -c, --config stringArray    grype configuration file(s) to use
      --profile stringArray   configuration profiles to use
  -q, --quiet                 suppress all logging output
  -v, --verbose count         increase verbosity (-v = info, -vv = debug)
```

### `grype db import`

```
import a vulnerability database archive from a local FILE or URL.
DB archives can be obtained from "https://grype.anchore.io/databases" (or running `db list`). If the URL has a `checksum` query parameter with a fully qualified digest (e.g. 'sha256:abc728...') then the archive/DB will be verified against this value.

Usage:
  grype db import FILE | URL [flags]

Flags:
  -h, --help   help for import

Global Flags:
  -c, --config stringArray    grype configuration file(s) to use
      --profile stringArray   configuration profiles to use
  -q, --quiet                 suppress all logging output
  -v, --verbose count         increase verbosity (-v = info, -vv = debug)
```

### `grype db list`

```
List all DBs available according to the listing URL

Usage:
  grype db list [flags]

Flags:
  -h, --help            help for list
  -o, --output string   format to display results (available=[text, raw, json]) (default "text")

Global Flags:
  -c, --config stringArray    grype configuration file(s) to use
      --profile stringArray   configuration profiles to use
  -q, --quiet                 suppress all logging output
  -v, --verbose count         increase verbosity (-v = info, -vv = debug)
```

### `grype db providers`

```
List vulnerability providers that are in the database

Usage:
  grype db providers [flags]

Flags:
  -h, --help            help for providers
  -o, --output string   format to display results (available=[table, json]) (default "table")

Global Flags:
  -c, --config stringArray    grype configuration file(s) to use
      --profile stringArray   configuration profiles to use
  -q, --quiet                 suppress all logging output
  -v, --verbose count         increase verbosity (-v = info, -vv = debug)
```

### `grype db search`

```
Search the DB for vulnerabilities or affected packages

Usage:
  grype db search [flags]
  grype db search [command]

Examples:

  Search for affected packages by vulnerability ID:

    $ grype db search --vuln ELSA-2023-12205

  Search for affected packages by package name:

    $ grype db search --pkg log4j

  Search for affected packages by package name, filtering down to a specific vulnerability:

    $ grype db search --pkg log4j --vuln CVE-2021-44228

  Search for affected packages by PURL (note: version is not considered):

    $ grype db search --pkg 'pkg:rpm/redhat/openssl' # or: '--ecosystem rpm --pkg openssl

  Search for affected packages by CPE (note: version/update is not considered):

    $ grype db search --pkg 'cpe:2.3:a:jetty:jetty_http_server:*:*:*:*:*:*:*:*'
    $ grype db search --pkg 'cpe:/a:jetty:jetty_http_server'

Available Commands:
  vuln        Search for vulnerabilities within the DB (supports DB schema v6+ only)

Flags:
      --broad-cpe-matching       allow for specific package CPE attributes to match with '*' values on the vulnerability
      --distro stringArray       refine to results with the given operating system (format: 'name', 'name@version', 'name@maj.min', 'name@codename')
      --ecosystem string         ecosystem of the package to search within
  -h, --help                     help for search
      --limit int                limit the number of results returned, use 0 for no limit (default 5000)
      --modified-after string    only show vulnerabilities originally published or modified since the given date (format: YYYY-MM-DD)
  -o, --output string            format to display results (available=[table, json]) (default "table")
      --pkg stringArray          package name/CPE/PURL to search for
      --provider stringArray     only show vulnerabilities from the given provider
      --published-after string   only show vulnerabilities originally published after the given date (format: YYYY-MM-DD)
      --vuln stringArray         only show results for the given vulnerability ID

Global Flags:
  -c, --config stringArray    grype configuration file(s) to use
      --profile stringArray   configuration profiles to use
  -q, --quiet                 suppress all logging output
  -v, --verbose count         increase verbosity (-v = info, -vv = debug)

Use "grype db search [command] --help" for more information about a command.
```

### `grype db status`

```
Display database status and metadata

Usage:
  grype db status [flags]

Flags:
  -h, --help            help for status
  -o, --output string   format to display results (available=[text, json]) (default "text")

Global Flags:
  -c, --config stringArray    grype configuration file(s) to use
      --profile stringArray   configuration profiles to use
  -q, --quiet                 suppress all logging output
  -v, --verbose count         increase verbosity (-v = info, -vv = debug)
```

### `grype db update`

```
Download and install the latest vulnerability database

Usage:
  grype db update [flags]

Flags:
  -h, --help   help for update

Global Flags:
  -c, --config stringArray    grype configuration file(s) to use
      --profile stringArray   configuration profiles to use
  -q, --quiet                 suppress all logging output
  -v, --verbose count         increase verbosity (-v = info, -vv = debug)
```

### `grype explain`

```
Ask grype to explain a set of findings

Usage:
  grype explain --id [VULNERABILITY ID] [flags]

Flags:
  -h, --help             help for explain
      --id stringArray   CVE IDs to explain

Global Flags:
  -c, --config stringArray    grype configuration file(s) to use
      --profile stringArray   configuration profiles to use
  -q, --quiet                 suppress all logging output
  -v, --verbose count         increase verbosity (-v = info, -vv = debug)
```
