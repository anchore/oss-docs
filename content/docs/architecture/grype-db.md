+++
title = "Grype DB"
description = "Architecture and design of the Grype vulnerability database build system"
weight = 30
categories = ["architecture"]
tags = ["grype-db", "vunnel"]
menu_group = "projects"
+++

## Overview

`grype-db` is an orchestration layer that coordinates pulling upstream vulnerability data, delegating transformation and database writing to [grype's build library]({{< relref "/docs/architecture/grype#db-build-utilities" >}}), and packaging the resulting database for distribution.

```mermaid
flowchart LR
    subgraph pull["Pull"]
        A[Pull vuln data<br/>from upstream]
    end

    subgraph build["Build (delegates to grype)"]
        B[Transform entries]
        C[Load entries<br/>into new DB]
    end

    subgraph package["Package"]
        D[Package DB]
    end

    A --> B --> C --> D

    style pull stroke-dasharray: 5 5, fill:none
    style build stroke-dasharray: 5 5, fill:none
    style package stroke-dasharray: 5 5, fill:none
```

## Multi-Schema Support Architecture

What makes `grype-db` unique compared to a typical ETL job is the extra responsibility of needing to transform the most recent vulnerability data shape (defined in the [vunnel repo](https://github.com/anchore/vunnel/tree/main/schema/vulnerability)) to all supported DB schema versions.

From the perspective of the Daily DB Publisher workflow, (abridged) execution looks something like this:

```mermaid
%%{ init: { 'flowchart': { 'curve': 'linear' } } }%%
flowchart LR
    A[Pull vulnerability data]

    B5[Build v5 DB]
    C5[Package v5 DB]
    D5[Publish v5]

    B6[Build v6 DB]
    C6[Package v6 DB]
    D6[Publish v6]

    A --- B5 --> C5 --> D5
    A --- B6 --> C6 --> D6
```

## Core Abstractions

The grype-db CLI retains the **[Provider](https://github.com/anchore/grype-db/blob/main/pkg/provider/provider.go)** abstraction, which is responsible for pulling and caching raw vulnerability data files locally for later processing.

The build-side abstractions (Processor, Transformer, Entry, Writer) now live in the grype repo. See the [Grype DB build utilities]({{< relref "/docs/architecture/grype#db-build-utilities" >}}) section for details on these abstractions and the data flow through the build process.

## Code Organization

After the migration of build logic to grype, grype-db retains orchestration and provider management:

```
grype-db/
├── cmd/                          # CLI entrypoints (pull, build, package commands)
├── pkg/
│   └── provider/                 # provider file/state/workspace management (pulling and caching upstream data)
├── manager/                      # Python scripts driving the daily DB publisher workflow
├── data/                         # local vulnerability data cache (populated by grype-db pull)
└── .grype-db.yaml                # configuration for providers and build settings
```

Build logic (processors, transformers, writers) has moved to the grype repo under `grype/db/`. See the [Grype DB build utilities]({{< relref "/docs/architecture/grype#db-build-utilities" >}}) for the current code organization of those components.

Note: Historical schema versions (v1-v4) have been removed from the codebase.

## DB Structure and Definitions

The definitions of what goes into the database and how to access it (both reads and writes) live in the public [`grype` repo](https://github.com/anchore/grype) under the [`grype/db` package](https://github.com/anchore/grype/tree/main/grype/db). Responsibilities of `grype` (not `grype-db`) include (but are not limited to):

- What tables are in the database
- What columns are in each table
- How each record should be serialized for writing into the database
- How records should be read/written from/to the database
- Providing rich objects for dealing with schema-specific data structures
- The name of the SQLite DB file within an archive
- The definition of a listing file and listing file entries

The purpose of [`grype-db`](https://github.com/anchore/grype-db) is to orchestrate and invoke the [build utilities from `grype/db`]({{< relref "/docs/architecture/grype#db-build-utilities" >}}) with upstream vulnerability data to create DB archives and make them publicly available for consumption via Grype.

## DB Distribution Files

Grype DB currently supports two active schema versions, each with a different distribution mechanism:

- **Schema v5** _(legacy)_: Supports Grype v0.87.0+
- **Schema v6** _(current)_: Supports Grype main branch

Historical schemas (v1-v4) are no longer supported and their code has been removed from the codebase.

### Schema v5: listing.json

The [`listing.json` file](https://github.com/anchore/grype/blob/main/grype/db/v5/distribution/listing.go) is a legacy distribution mechanism used for schema v5 (and historically v1-v4):

- **Location**: `databases/listing.json`
- **Structure**: Contains URLs to DB archives organized by schema version, ordered by latest-date-first
- **Format**: `{ "available": { "1": [...], "2": [...], "5": [...] } }`
- **Update Process**: Re-generated daily by the grype-db publisher workflow through a separate listing update step

### Schema v6+: latest.json

The [`latest.json` file](https://github.com/anchore/grype/blob/main/grype/db/v6/distribution/latest.go) is the modern distribution mechanism used for schema v6 and future versions:

- **Location**: `databases/v{major}/latest.json` (e.g., `v6/latest.json`, `v7/latest.json`)
- **Structure**: Contains metadata and URL for the single latest DB archive for that major schema version
- **Format**: `{ "url": "...", "built": "...", "checksum": "...", "schemaVersion": 6 }`
- **Update Process**: Generated and uploaded atomically with each DB build (no separate update step)

This dual-distribution approach allows Grype to maintain backward compatibility with v5 while providing a more efficient distribution mechanism for v6 and future versions.

**Implementation Notes:**

- Distribution file definitions reside in the [`grype` repo](https://github.com/anchore/grype), while the [`grype-db` repo](https://github.com/anchore/grype-db) is responsible for generating DBs and creating/updating these distribution files
- As long as Grype has been configured to point to the correct distribution file URL, the DBs can be stored separately, replaced with a service returning the distribution file contents, or mirrored for systems behind an air gap

## Daily Workflows

There are two workflows that drive getting a new Grype DB out to OSS users:

1. The [daily data sync workflow](https://github.com/anchore/grype-db/blob/main/.github/workflows/daily-data-sync.yaml), which uses [vunnel](https://github.com/anchore/vunnel) to pull upstream vulnerability data.
2. The [daily DB publisher workflow](https://github.com/anchore/grype-db/blob/main/.github/workflows/daily-db-publisher-r2.yaml), which builds and publishes a Grype DB from the data obtained in the daily data sync workflow.

### Daily Data Sync Workflow

**This workflow takes the upstream vulnerability data (from canonical, redhat, debian, NVD, etc), processes it, and writes the results to OCI repos.**

```mermaid
%%{ init: { 'flowchart': { 'curve': 'linear' } } }%%
flowchart LR
    A1["Pull alpine"] --> B1["Publish to ghcr.io/anchore/grype-db/data/alpine:&lt;date&gt;"]
    A2["Pull amazon"] --> B2["Publish to ghcr.io/anchore/grype-db/data/amazon:&lt;date&gt;"]
    A3["Pull debian"] --> B3["Publish to ghcr.io/anchore/grype-db/data/debian:&lt;date&gt;"]
    A4["Pull github"] --> B4["Publish to ghcr.io/anchore/grype-db/data/github:&lt;date&gt;"]
    A5["Pull nvd"] --> B5["Publish to ghcr.io/anchore/grype-db/data/nvd:&lt;date&gt;"]
    A6["..."] --> B6["... repeat for all upstream providers ..."]

    style A6 fill:none,stroke:none
    style B6 fill:none,stroke:none
```

Once all providers have been updated, a single vulnerability cache OCI repo is updated with all of the latest vulnerability data at `ghcr.io/anchore/grype-db/data:<date>`. This repo is what is used downstream by the DB publisher workflow to create Grype DBs.

The in-repo [`.grype-db.yaml`](https://github.com/anchore/grype-db/blob/main/.grype-db.yaml) and [`.vunnel.yaml`](https://github.com/anchore/grype-db/blob/main/.vunnel.yaml) configurations are used to define the upstream data sources, how to obtain them, and where to put the results locally.

### Daily DB Publishing Workflow

This workflow takes the latest vulnerability data cache, builds a Grype DB, and publishes it for general consumption:

```mermaid
%%{ init: { 'flowchart': { 'curve': 'linear' } } }%%
flowchart LR
    subgraph pull["1. Pull"]
        A["Pull vuln data<br/>(from the daily<br/>sync workflow<br/>output)"]
    end

    subgraph generate["2. Generate Databases"]
        B5["Build v5 DB"]
        C5["Package v5 DB"]
        D5["Upload Archive"]

        B6["Build v6 DB"]
        C6["Package v6 DB<br/>(includes latest.json)"]
        D6["Upload Archive<br/>+ latest.json"]

        B5 --> C5 --> D5
        B6 --> C6 --> D6
    end

    subgraph listing["3. Update Listing (v5 only)"]
        F["Update listing.json"]
    end

    A --- B5
    A --- B6

    D5 --- F
    D6 -.->|"No listing update<br/>needed for v6"| G[Done]

    style pull stroke-dasharray: 5 5, fill:none
    style generate stroke-dasharray: 5 5, fill:none
    style listing stroke-dasharray: 5 5, fill:none
    style G fill:none,stroke:none
```

The [`manager/` directory](https://github.com/anchore/grype-db/tree/main/manager) contains all code responsible for driving the [Daily DB Publisher workflow](https://github.com/anchore/grype-db/blob/main/.github/workflows/daily-db-publisher-r2.yaml), generating DBs for all supported schema versions (currently v5 and v6) and making them available to the public.

#### 1. Pull

Download the latest vulnerability data from various upstream data sources into a local directory. The destination for the provider data is in the [`data/vunnel`](https://github.com/anchore/grype-db/tree/main/data/vunnel) directory.

#### 2. Generate

Build databases for all supported schema versions (using grype's build library) based on the latest vulnerability data and upload them to Cloudflare R2 (S3-compatible storage).

**Supported Schemas** (see [`schema-info.json`](https://github.com/anchore/grype-db/blob/main/manager/src/grype_db_manager/data/schema-info.json)):

- Schema v5 (legacy)
- Schema v6 (current)

**Build and Upload Process:**

Each DB undergoes the following steps:

1. **Build**: Transform vulnerability data into the schema-specific format
2. **Package**: Create a compressed archive (`.tar.zst`)
3. **Validate**: Smoke test with Grype by comparing against the previous release using [vulnerability-match-labels](https://github.com/anchore/vulnerability-match-labels)
4. **Upload**: Only DBs that pass validation are uploaded

**Storage Location:**

- Distribution base URL: `https://grype.anchore.io/databases/...`
- Schema-specific paths:
  - v5: `databases/<archive-name>.tar.zst`
  - v6: `databases/v6/<archive-name>.tar.zst` + `databases/v6/latest.json`

**Key Difference:**

- **v5**: Only the DB archive is uploaded; discoverability happens in the next step
- **v6**: Both the DB archive AND `latest.json` are uploaded atomically, making the DB immediately discoverable

#### 3. Update Listing (v5 Only)

**This step only applies to schema v5.**

Generate and upload a new `listing.json` file to Cloudflare R2 based on the existing listing file and newly discovered DB archives.

The listing file is tested against installations of Grype to ensure scans can successfully discover and download the DB. The scan must have a non-zero count of matches to pass validation.

Once the listing file has been uploaded to `databases/listing.json`, user-facing Grype v5 installations can discover and download the new DB.

**Note:** Schema v6 does not require this step because the `latest.json` file is generated and uploaded atomically with the DB archive in step 2, with a 5-minute cache TTL for fast updates.

## Related Architecture

For more details on:

- How the DB build utilities (processors, transformers, writers) works, see the [Grype DB build utilities](/docs/architecture/grype#db-build-utilities) section
- How Vunnel processes vulnerability data, see the [Vunnel Architecture](/docs/architecture/vunnel) page
- How quality gates validate database builds, see the Quality Gates section
