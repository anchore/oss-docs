+++
title = "Syft Default Configuration"
linkTitle = "Syft Default Config"
weight = 15
tags = ['syft']
categories = ['reference']
url = "reference/commands/syft-config"
+++

### Syft default configuration

```
log:
  # suppress all logging output (env: SYFT_LOG_QUIET)
  quiet: false

  # increase verbosity (-v = info, -vv = debug) (env: SYFT_LOG_VERBOSITY)
  verbosity: 0

  # explicitly set the logging level (available: [error warn info debug trace]) (env: SYFT_LOG_LEVEL)
  level: 'warn'

  # file path to write logs to (env: SYFT_LOG_FILE)
  file: ''

dev:
  # capture resource profiling data (available: [cpu, mem]) (env: SYFT_DEV_PROFILE)
  profile: ''

# the configuration file(s) used to load application configuration (env: SYFT_CONFIG)
config: ''

# the output format(s) of the SBOM report (options: syft-table, syft-text, syft-json, spdx-json, ...)
# to specify multiple output files in differing formats, use a list:
# output:
#   - "syft-json=<syft-json-output-file>"
#   - "spdx-json=<spdx-json-output-file>" (env: SYFT_OUTPUT)
output:
  - 'syft-table'

# file to write the default report output to (default is STDOUT) (env: SYFT_LEGACYFILE)
legacyFile: ''

format:
  # default value for all formats that support the "pretty" option (default is unset) (env: SYFT_FORMAT_PRETTY)
  pretty:

  template:
    # path to the template file to use when rendering the output with the template output format.
    # Note that all template paths are based on the current syft-json schema (env: SYFT_FORMAT_TEMPLATE_PATH)
    path: ''

    # if true, uses the go structs for the syft-json format for templating.
    # if false, uses the syft-json output for templating (which follows the syft JSON schema exactly).
    #
    # Note: long term support for this option is not guaranteed (it may change or break at any time) (env: SYFT_FORMAT_TEMPLATE_LEGACY)
    legacy: false

  json:
    # transform any syft-json output to conform to an approximation of the v11.0.1 schema. This includes:
    # - using the package metadata type names from before v12 of the JSON schema (changed in https://github.com/anchore/syft/pull/1983)
    #
    # Note: this will still include package types and fields that were added at or after json schema v12. This means
    # that output might not strictly be json schema v11 compliant, however, for consumers that require time to port
    # over to the final syft 1.0 json output this option can be used to ease the transition.
    #
    # Note: long term support for this option is not guaranteed (it may change or break at any time) (env: SYFT_FORMAT_JSON_LEGACY)
    legacy: false

    # include space indentation and newlines
    # note: inherits default value from 'format.pretty' or 'false' if parent is unset (env: SYFT_FORMAT_JSON_PRETTY)
    pretty:

  spdx-json:
    # include space indentation and newlines
    # note: inherits default value from 'format.pretty' or 'false' if parent is unset (env: SYFT_FORMAT_SPDX_JSON_PRETTY)
    pretty:

  cyclonedx-json:
    # include space indentation and newlines
    # note: inherits default value from 'format.pretty' or 'false' if parent is unset (env: SYFT_FORMAT_CYCLONEDX_JSON_PRETTY)
    pretty:

  cyclonedx-xml:
    # include space indentation and newlines
    # note: inherits default value from 'format.pretty' or 'false' if parent is unset (env: SYFT_FORMAT_CYCLONEDX_XML_PRETTY)
    pretty:

# whether to check for an application update on start up or not (env: SYFT_CHECK_FOR_APP_UPDATE)
check-for-app-update: true

# enable one or more package catalogers (env: SYFT_CATALOGERS)
catalogers: []

# set the base set of catalogers to use (defaults to 'image' or 'directory' depending on the scan source) (env: SYFT_DEFAULT_CATALOGERS)
default-catalogers: []

# add, remove, and filter the catalogers to be used (env: SYFT_SELECT_CATALOGERS)
select-catalogers: []

package:
  # search within archives that do not contain a file index to search against (tar, tar.gz, tar.bz2, etc)
  # note: enabling this may result in a performance impact since all discovered compressed tars will be decompressed
  # note: for now this only applies to the java package cataloger (env: SYFT_PACKAGE_SEARCH_UNINDEXED_ARCHIVES)
  search-unindexed-archives: false

  # search within archives that do contain a file index to search against (zip)
  # note: for now this only applies to the java package cataloger (env: SYFT_PACKAGE_SEARCH_INDEXED_ARCHIVES)
  search-indexed-archives: true

  # allows users to exclude synthetic binary packages from the sbom
  # these packages are removed if an overlap with a non-synthetic package is found (env: SYFT_PACKAGE_EXCLUDE_BINARY_OVERLAP_BY_OWNERSHIP)
  exclude-binary-overlap-by-ownership: true

license:
  # include the content of licenses in the SBOM for a given syft scan; valid values are: [all unknown none] (env: SYFT_LICENSE_CONTENT)
  content: 'none'

  # deprecated: please use 'license-content' instead (env: SYFT_LICENSE_INCLUDE_UNKNOWN_LICENSE_CONTENT)
  include-unknown-license-content:

  # adjust the percent as a fraction of the total text, in normalized words, that
  # matches any valid license for the given inputs, expressed as a percentage across all of the licenses matched. (env: SYFT_LICENSE_COVERAGE)
  coverage: 75

  # deprecated: please use 'coverage' instead (env: SYFT_LICENSE_LICENSE_COVERAGE)
  license-coverage:

file:
  metadata:
    # select which files should be captured by the file-metadata cataloger and included in the SBOM.
    # Options include:
    #  - "all": capture all files from the search space
    #  - "owned-by-package": capture only files owned by packages
    #  - "none", "": do not capture any files (env: SYFT_FILE_METADATA_SELECTION)
    selection: 'owned-by-package'

    # the file digest algorithms to use when cataloging files (options: "md5", "sha1", "sha224", "sha256", "sha384", "sha512") (env: SYFT_FILE_METADATA_DIGESTS)
    digests:
      - 'sha1'
      - 'sha256'

  content:
    # skip searching a file entirely if it is above the given size (default = 1MB; unit = bytes) (env: SYFT_FILE_CONTENT_SKIP_FILES_ABOVE_SIZE)
    skip-files-above-size: 256000

    # file globs for the cataloger to match on (env: SYFT_FILE_CONTENT_GLOBS)
    globs: []

  executable:
    # file globs for the cataloger to match on (env: SYFT_FILE_EXECUTABLE_GLOBS)
    globs: []

# selection of layers to catalog, options=[squashed all-layers deep-squashed] (env: SYFT_SCOPE)
scope: 'squashed'

# number of cataloger workers to run in parallel
# by default, when set to 0: this will be based on runtime.NumCPU * 4, if set to less than 0 it will be unbounded (env: SYFT_PARALLELISM)
parallelism: 0

relationships:
  # include package-to-file relationships that indicate which files are owned by which packages (env: SYFT_RELATIONSHIPS_PACKAGE_FILE_OWNERSHIP)
  package-file-ownership: true

  # include package-to-package relationships that indicate one package is owned by another due to files claimed to be owned by one package are also evidence of another package's existence (env: SYFT_RELATIONSHIPS_PACKAGE_FILE_OWNERSHIP_OVERLAP)
  package-file-ownership-overlap: true

compliance:
  # action to take when a package is missing a name (env: SYFT_COMPLIANCE_MISSING_NAME)
  missing-name: 'drop'

  # action to take when a package is missing a version (env: SYFT_COMPLIANCE_MISSING_VERSION)
  missing-version: 'stub'

# Enable data enrichment operations, which can utilize services such as Maven Central and NPM.
# By default all enrichment is disabled, use: all to enable everything.
# Available options are: all, golang, java, javascript (env: SYFT_ENRICH)
enrich: []

dotnet:
  # only keep dep.json packages which an executable on disk is found. The package is also included if a DLL is found for any child package, even if the package itself does not have a DLL. (env: SYFT_DOTNET_DEP_PACKAGES_MUST_HAVE_DLL)
  dep-packages-must-have-dll: false

  # only keep dep.json packages which have a runtime/resource DLL claimed in the deps.json targets section (but not necessarily found on disk). The package is also included if any child package claims a DLL, even if the package itself does not claim a DLL. (env: SYFT_DOTNET_DEP_PACKAGES_MUST_CLAIM_DLL)
  dep-packages-must-claim-dll: true

  # treat DLL claims or on-disk evidence for child packages as DLL claims or on-disk evidence for any parent package (env: SYFT_DOTNET_PROPAGATE_DLL_CLAIMS_TO_PARENTS)
  propagate-dll-claims-to-parents: true

  # show all packages from the deps.json if bundling tooling is present as a dependency (e.g. ILRepack) (env: SYFT_DOTNET_RELAX_DLL_CLAIMS_WHEN_BUNDLING_DETECTED)
  relax-dll-claims-when-bundling-detected: true

golang:
  # search for go package licences in the GOPATH of the system running Syft, note that this is outside the
  # container filesystem and potentially outside the root of a local directory scan (env: SYFT_GOLANG_SEARCH_LOCAL_MOD_CACHE_LICENSES)
  search-local-mod-cache-licenses:

  # specify an explicit go mod cache directory, if unset this defaults to $GOPATH/pkg/mod or $HOME/go/pkg/mod (env: SYFT_GOLANG_LOCAL_MOD_CACHE_DIR)
  local-mod-cache-dir: '~/go/pkg/mod'

  # search for go package licences in the vendor folder on the system running Syft, note that this is outside the
  # container filesystem and potentially outside the root of a local directory scan (env: SYFT_GOLANG_SEARCH_LOCAL_VENDOR_LICENSES)
  search-local-vendor-licenses:

  # specify an explicit go vendor directory, if unset this defaults to ./vendor (env: SYFT_GOLANG_LOCAL_VENDOR_DIR)
  local-vendor-dir: ''

  # search for go package licences by retrieving the package from a network proxy (env: SYFT_GOLANG_SEARCH_REMOTE_LICENSES)
  search-remote-licenses:

  # remote proxy to use when retrieving go packages from the network,
  # if unset this defaults to $GOPROXY followed by https://proxy.golang.org (env: SYFT_GOLANG_PROXY)
  proxy: 'https://proxy.golang.org,direct'

  # specifies packages which should not be fetched by proxy
  # if unset this defaults to $GONOPROXY (env: SYFT_GOLANG_NO_PROXY)
  no-proxy: ''

  main-module-version:
    # look for LD flags that appear to be setting a version (e.g. -X main.version=1.0.0) (env: SYFT_GOLANG_MAIN_MODULE_VERSION_FROM_LD_FLAGS)
    from-ld-flags: true

    # search for semver-like strings in the binary contents (env: SYFT_GOLANG_MAIN_MODULE_VERSION_FROM_CONTENTS)
    from-contents: false

    # use the build settings (e.g. vcs.version & vcs.time) to craft a v0 pseudo version
    # (e.g. v0.0.0-20220308212642-53e6d0aaf6fb) when a more accurate version cannot be found otherwise (env: SYFT_GOLANG_MAIN_MODULE_VERSION_FROM_BUILD_SETTINGS)
    from-build-settings: true

java:
  # enables Syft to use the network to fetch version and license information for packages when
  # a parent or imported pom file is not found in the local maven repository.
  # the pom files are downloaded from the remote Maven repository at 'maven-url' (env: SYFT_JAVA_USE_NETWORK)
  use-network:

  # use the local Maven repository to retrieve pom files. When Maven is installed and was previously used
  # for building the software that is being scanned, then most pom files will be available in this
  # repository on the local file system. this greatly speeds up scans. when all pom files are available
  # in the local repository, then 'use-network' is not needed.
  # TIP: If you want to download all required pom files to the local repository without running a full
  # build, run 'mvn help:effective-pom' before performing the scan with syft. (env: SYFT_JAVA_USE_MAVEN_LOCAL_REPOSITORY)
  use-maven-local-repository:

  # override the default location of the local Maven repository.
  # the default is the subdirectory '.m2/repository' in your home directory (env: SYFT_JAVA_MAVEN_LOCAL_REPOSITORY_DIR)
  maven-local-repository-dir: '~/.m2/repository'

  # maven repository to use, defaults to Maven central (env: SYFT_JAVA_MAVEN_URL)
  maven-url: 'https://repo1.maven.org/maven2'

  # depth to recursively resolve parent POMs, no limit if <= 0 (env: SYFT_JAVA_MAX_PARENT_RECURSIVE_DEPTH)
  max-parent-recursive-depth: 0

  # resolve transient dependencies such as those defined in a dependency's POM on Maven central (env: SYFT_JAVA_RESOLVE_TRANSITIVE_DEPENDENCIES)
  resolve-transitive-dependencies: false

javascript:
  # enables Syft to use the network to fill in more detailed license information (env: SYFT_JAVASCRIPT_SEARCH_REMOTE_LICENSES)
  search-remote-licenses:

  # base NPM url to use (env: SYFT_JAVASCRIPT_NPM_BASE_URL)
  npm-base-url: ''

  # include development-scoped dependencies (env: SYFT_JAVASCRIPT_INCLUDE_DEV_DEPENDENCIES)
  include-dev-dependencies:

linux-kernel:
  # whether to catalog linux kernel modules found within lib/modules/** directories (env: SYFT_LINUX_KERNEL_CATALOG_MODULES)
  catalog-modules: true

nix:
  # enumerate all files owned by packages found within Nix store paths (env: SYFT_NIX_CAPTURE_OWNED_FILES)
  capture-owned-files: false

python:
  # when running across entries in requirements.txt that do not specify a specific version
  # (e.g. "sqlalchemy >= 1.0.0, <= 2.0.0, != 3.0.0, <= 3.0.0"), attempt to guess what the version could
  # be based on the version requirements specified (e.g. "1.0.0"). When enabled the lowest expressible version
  # when given an arbitrary constraint will be used (even if that version may not be available/published). (env: SYFT_PYTHON_GUESS_UNPINNED_REQUIREMENTS)
  guess-unpinned-requirements: false

registry:
  # skip TLS verification when communicating with the registry (env: SYFT_REGISTRY_INSECURE_SKIP_TLS_VERIFY)
  insecure-skip-tls-verify: false

  # use http instead of https when connecting to the registry (env: SYFT_REGISTRY_INSECURE_USE_HTTP)
  insecure-use-http: false

  # Authentication credentials for specific registries. Each entry describes authentication for a specific authority:
  # - authority: the registry authority URL the URL to the registry (e.g. "docker.io", "localhost:5000", etc.) (env: SYFT_REGISTRY_AUTH_AUTHORITY)
  #  username: a username if using basic credentials (env: SYFT_REGISTRY_AUTH_USERNAME)
  #  password: a corresponding password (env: SYFT_REGISTRY_AUTH_PASSWORD)
  #  token: a token if using token-based authentication, mutually exclusive with username/password (env: SYFT_REGISTRY_AUTH_TOKEN)
  #  tls-cert: filepath to the client certificate used for TLS authentication to the registry (env: SYFT_REGISTRY_AUTH_TLS_CERT)
  #  tls-key: filepath to the client key used for TLS authentication to the registry (env: SYFT_REGISTRY_AUTH_TLS_KEY)
  auth: []

  # filepath to a CA certificate (or directory containing *.crt, *.cert, *.pem) used to generate the client certificate (env: SYFT_REGISTRY_CA_CERT)
  ca-cert: ''

# specify the source behavior to use (e.g. docker, registry, oci-dir, ...) (env: SYFT_FROM)
from: []

# an optional platform specifier for container image sources (e.g. 'linux/arm64', 'linux/arm64/v8', 'arm64', 'linux') (env: SYFT_PLATFORM)
platform: ''

source:
  # set the name of the target being analyzed (env: SYFT_SOURCE_NAME)
  name: ''

  # set the version of the target being analyzed (env: SYFT_SOURCE_VERSION)
  version: ''

  # base directory for scanning, no links will be followed above this directory, and all paths will be reported relative to this directory (env: SYFT_SOURCE_BASE_PATH)
  base-path: ''

  file:
    # the file digest algorithms to use on the scanned file (options: "md5", "sha1", "sha224", "sha256", "sha384", "sha512") (env: SYFT_SOURCE_FILE_DIGESTS)
    digests:
      - 'SHA-256'

  image:
    # allows users to specify which image source should be used to generate the sbom
    # valid values are: registry, docker, podman (env: SYFT_SOURCE_IMAGE_DEFAULT_PULL_SOURCE)
    default-pull-source: ''

    # (env: SYFT_SOURCE_IMAGE_MAX_LAYER_SIZE)
    max-layer-size: ''

# exclude paths from being scanned using a glob expression (env: SYFT_EXCLUDE)
exclude: []

unknowns:
  # remove unknown errors on files with discovered packages (env: SYFT_UNKNOWNS_REMOVE_WHEN_PACKAGES_DEFINED)
  remove-when-packages-defined: true

  # include executables without any identified packages (env: SYFT_UNKNOWNS_EXECUTABLES_WITHOUT_PACKAGES)
  executables-without-packages: true

  # include archives which were not expanded and searched (env: SYFT_UNKNOWNS_UNEXPANDED_ARCHIVES)
  unexpanded-archives: true

cache:
  # root directory to cache any downloaded content; empty string will use an in-memory cache (env: SYFT_CACHE_DIR)
  dir: '~/Library/Caches/syft'

  # time to live for cached data; setting this to 0 will disable caching entirely (env: SYFT_CACHE_TTL)
  ttl: '7d'

# show catalogers that have been de-selected (env: SYFT_SHOW_HIDDEN)
show-hidden: false

attest:
  # the key to use for the attestation (env: SYFT_ATTEST_KEY)
  key: ''

  # password to decrypt to given private key
  # additionally responds to COSIGN_PASSWORD env var (env: SYFT_ATTEST_PASSWORD)
  password: ''
```
