+++
title = "Architecture"
description = "How all the projects and datasets fit together"
weight = 60
menu_group = "general"
+++

Anchore's open source security tooling consists of several interconnected tools that work together to detect vulnerabilities and ensure license compliance in software packages. This page explains how these tools interact and how data flows through the system.

The Anchore OSS ecosystem includes five main tools that, at the 30,000 ft view, work together as follows:

```mermaid
---
config:
  layout: dagre
  look: handDrawn
  theme: default
  flowchart:
    curve: linear
---
flowchart TD
    vunnel["***Vunnel***<br><small>Downloads and normalizes<br>security feeds</small>"]:::Ash
    grypedb["***Grype DB***<br><small>Converts feeds to<br>SQLite database</small>"]:::Ash
    grype["***Grype***<br><small>Matches vulnerabilities<br>from SBOM + database</small>"]:::Ash
    syft["***Syft***<br><small>Generates SBOMs from<br>scan targets</small>"]:::Ash
    grant["***Grant***<br><small>Analyzes licenses<br>from SBOM</small>"]:::Ash

    vunnel --> grypedb --> grype
    syft --> grype & grant

    vunnel@{ shape: event}
    grypedb@{ shape: event}
    grype@{ shape: event}
    syft@{ shape: event}
    grant@{ shape: event}

    classDef Ash stroke-width:1px, stroke-dasharray:none, stroke:#424242, fill:#e1ffe1, color:#000000

```

Zooming in to the 20,000 ft view, here's how data flows through the same system:

```mermaid
---
config:
  layout: dagre
  look: handDrawn
  theme: default
  flowchart:
    curve: linear
---
flowchart TB

  feed1["NVD Feed"]
  feed2["Alpine Feed"]
  feed3["... (20+ feeds)"]

  subgraph anchore["<b>Anchore Infrastructure</b>"]
    vunnel["Vunnel"]
    grypedb["Grype DB"]
    cache["Daily DB"]
    vunnel --> grypedb --> cache
  end


  subgraph user["<b>User Environment</b>"]
    targets["Image, filesystem,<br>PURLs, directory, ..."]
    local["DB Cache"]

    syft["Syft"]
    sbom["SBOM"]

    targets --> syft --> sbom

    grype["Grype"]
    vulns["Vulnerability+Package<br>Matches"]
    grant["Grant"]
    licenses["License Compliance<br>Report"]

    grype --> vulns
    grant --> licenses

    sbom --> grype
    sbom --> grant
    local --> grype
  end

  feed1 --> vunnel
  feed2 --> vunnel
  feed3 -.-> vunnel

  cache -. "<i>download</i>" .-> local

  feed1:::ExternalSource@{ shape: cloud}
  feed2:::ExternalSource@{ shape: cloud}
  feed3:::ExternalSource@{ shape: cloud}
  vunnel:::Application@{ shape: event}
  grypedb:::Application@{ shape: event}
  grype:::Application@{ shape: event}
  syft:::Application@{ shape: event}
  grant:::Application@{ shape: event}

  targets:::AnalysisInput
  cache:::Database@{ shape: db}
  local:::Database@{ shape: db}
  sbom:::Document@{ shape: doc}
  vulns:::Document@{ shape: doc}
  licenses:::Document@{ shape: doc}

  style anchore fill:none, stroke:#333333, stroke-width:2px, stroke-dasharray:5 5
  style user fill:none, stroke:#333333, stroke-width:2px, stroke-dasharray:5 5

  classDef AnalysisInput stroke-width:1px, stroke-dasharray:none, stroke:#424242, fill:#f0f8ff, color:#000000
  classDef ExternalSource stroke-width:1px, stroke-dasharray:none, stroke:#424242, fill:#f0f8ff, color:#000000
  classDef Application stroke-width:1px, stroke-dasharray:none, stroke:#424242, fill:#e1ffe1, color:#000000
  classDef Document stroke-width:1px, stroke-dasharray:none, stroke:#424242, fill:#fff9c4, color:#000000
  classDef Database stroke-width:1px, stroke-dasharray:none, stroke:#424242, fill:#fff9c4, color:#000000
```
