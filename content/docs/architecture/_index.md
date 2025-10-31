+++
title = "Architecture"
description = "How all the projects and datasets fit together"
weight = 60
url = "architecture"
menu_group = "general"
+++

Anchore's open source security tooling consists of several interconnected tools that work together to detect vulnerabilities and ensure license compliance in software packages. This page explains how these tools interact and how data flows through the system.

The Anchore OSS ecosystem includes five main tools that, at the 30,000 ft view, work together as follows:

```mermaid
flowchart TD
    vunnel[[***Vunnel***<br/>Downloads and normalizes<br/>security feeds]]
    grypedb[[***Grype DB***<br/>Converts feeds to<br/>SQLite database]]
    syft[[***Syft***<br/>Generates SBOMs from<br/>scan targets]]
    grype[[***Grype***<br/>Matches vulnerabilities<br/>from SBOM + database]]
    grant[[***Grant***<br/>Analyzes licenses<br/>from SBOM]]

    vunnel --> grypedb
    grypedb --> grype
    syft --> grype
    syft --> grant

    style vunnel fill:#e0e0e0
    style grypedb fill:#e0e0e0
    style syft fill:#e0e0e0
    style grype fill:#e0e0e0
    style grant fill:#e0e0e0
```

Zooming in to the 20,000 ft view, here's how data flows through the same system:

```mermaid
---
config:
  layout: dagre
---
flowchart LR
 subgraph anchore["Anchore Infrastructure"]
        feed1["NVD Feed"]
        feed2["Alpine Feed"]
        feed3["... (20+ feeds)"]
        vunnel[["Vunnel"]]
        grypedb[["Grype DB"]]
        cache["Daily<br>Database"]
  end
 subgraph user["User Environment"]
        download["grype db update<br>or auto-update"]
        local["Local DB<br>Cache"]
        targets["Image, filesystem,<br>PURLs, directory,<br>..."]
        syft[["Syft"]]
        sbom["SBOM"]
        grype[["Grype"]]
        vulns["Vulnerability+Package<br>Matches"]
        grant[["Grant"]]
        licenses["License Compliance<br>Report"]
  end
    feed1 --> vunnel
    feed2 --> vunnel
    feed3 -.-> vunnel
    vunnel --> grypedb
    grypedb --> cache
    cache -. Download .-> download
    download --> local
    targets --> syft
    syft --> sbom
    local --> grype
    sbom --> grype
    grype --> vulns
    sbom --> grant
    grant --> licenses
    cache@{ shape: db}
    local@{ shape: db}
    sbom@{ shape: doc}
    vulns@{ shape: doc}
    licenses@{ shape: doc}
    style anchore fill:#e1f5ff
    style user fill:#f0f0f0
    style vunnel fill:#e1ffe1
    style grypedb fill:#e1ffe1
    style syft fill:#e1ffe1
    style grype fill:#e1ffe1
    style grant fill:#e1ffe1
    style sbom fill:#fff9c4
    style vulns fill:#fff9c4
    style licenses fill:#fff9c4
```
