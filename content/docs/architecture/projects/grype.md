+++
title = "Grype"
description = "Architecture and design of the Grype vulnerability scanner"
weight = 50
url = "docs/architecture/grype"
categories = ["architecture"]
tags = ["grype"]
menu_group = "projects"
+++

## Overview

Grype is a vulnerability scanner for container images and filesystems. It uses Syft to catalog packages and matches them against vulnerability data stored in a SQLite database.

## Relationship to Syft

Grype uses Syft as a library for all-things related to obtaining and parsing the given scan target:

- Pulling container images
- Parsing container images
- Indexing directories
- Cataloging packages

Releases of Grype should always use released versions of Syft (commits that are tagged and show up in the GitHub releases page). However, continually integrating unreleased Syft changes into Grype incrementally is encouraged (e.g. `go get github.com/anchore/syft@main`) as long as by the time a release is cut the Syft version is updated to a released version (e.g. `go get github.com/anchore/syft@v<semantic-version>`).

For more details on Syft's architecture, see the [Syft Architecture](/docs/architecture/syft) page.

## Database Structure

The currently supported database format is SQLite3. The database contains tables for:

- `id` - vulnerability identifiers
- `vulnerability` - vulnerability records with package matching information
- `vulnerability_metadata` - additional metadata about vulnerabilities

Each vulnerability record includes:

- `record_source` - the source of the vulnerability data
- `package_name` - the name of the affected package
- `namespace` - the ecosystem namespace (e.g. `nvd`, `alpine:3.16`, `debian:11`)
- `version_constraint` - the version range affected by the vulnerability
- `version_format` - the versioning scheme used (e.g. `apk`, `deb`, `rpm`, `semver`)
- `cpes` - Common Platform Enumeration identifiers
- `proxy_vulnerabilities` - related vulnerability identifiers

## Matching Engine

Grype's matching engine takes the package catalog from Syft and matches it against the vulnerability database. The matching process:

1. Receives a package catalog from Syft
2. Queries the vulnerability database for each package
3. Evaluates version constraints to determine if a vulnerability applies
4. Returns a list of vulnerabilities found

The matching engine supports multiple version formats and constraint expressions to accurately match packages against vulnerability records across different ecosystems.

## Database Updates

Grype downloads vulnerability databases from a listing file that points to versioned database archives. The database is updated regularly with new vulnerability data from the [Grype DB](/docs/architecture/grype-db) daily publishing workflow.

For more details on how the database is built and published, see the [Grype DB Architecture](/docs/architecture/grype-db) page.

## Related Architecture

- [Syft Architecture](/docs/architecture/syft) - Package cataloging
- [Grype DB Architecture](/docs/architecture/grype-db) - Database build and publishing
- [Quality Gates](/docs/architecture/quality-gates) - Validation and testing
