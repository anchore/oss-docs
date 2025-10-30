+++
title = "Projects"
description = "Overview of Anchore Open Source tools."
weight = 5
tags = ["syft", "grype", "grant"]
url = "docs/projects"
+++

We maintain three popular command-line tools, some libraries, and supporting utilities. Most are written in Go, with a few in Python. They are all released under the Apache-2.0 license. For the full list, see our [GitHub org](https://github.com/orgs/anchore/repositories).

Anchore's tools follow a simple workflow: search and raise up evidence in the form of a Software Bill of Materials (SBOM) using **Syft**,
then analyze that SBOM with **Grype** for security vulnerabilities and **Grant** for open source license compliance.

```mermaid
%%{init: {'theme':'base', 'themeVariables': { 'primaryColor':'#f8fafc','primaryTextColor':'#1e293b','primaryBorderColor':'#cbd5e1','lineColor':'#94a3b8','secondaryColor':'#f8fafc','tertiaryColor':'#f8fafc'}}}%%
graph LR
    software["📦 Your Software<br/><small>Container Images<br/>Filesystems<br/>Archives</small>"]
    syft["🔍 Syft<br/><small>SBOM Generator</small>"]
    sbom@{ shape: doc, label: "📋 SBOM<br/><small>Software Bill<br/>of Materials</small>"}
    grype["🛡️ Grype<br/><small>Vulnerability<br/>Scanner</small>"]
    grant["⚖️ Grant<br/><small>License<br/>Scanner</small>"]
    vulns@{ shape: doc, label: "Security Report<br/><small>CVE findings</small>"}
    licenses@{ shape: doc, label: "License Report<br/><small>Compliance info</small>"}

    software -.->|scan| syft
    syft -->|generates| sbom
    sbom -->|analyze| grype
    sbom -->|analyze| grant
    grype -->|produces| vulns
    grant -->|produces| licenses

    classDef inputStyle fill:#f8fafc,stroke:#cbd5e1,stroke-width:2px,stroke-dasharray: 5 5,color:#64748b
    classDef syftStyle fill:#fdf4ff,stroke:#e879f9,stroke-width:2px,color:#6b21a8
    classDef grypleStyle fill:#eff6ff,stroke:#3b82f6,stroke-width:2px,color:#1e3a8a
    classDef grantStyle fill:#f0fdf4,stroke:#00b388,stroke-width:2px,color:#065f46
    classDef docStyle fill:#ffffff,stroke:#cbd5e1,stroke-width:1px,color:#475569

    class software inputStyle
    class syft syftStyle
    class grype grypleStyle
    class grant grantStyle
    class sbom,vulns,licenses docStyle
```

This modular approach lets you generate the SBOM once with Syft, then use Grype and Grant independently to scan for different types of risk.

#### <img src="/images/logos/syft/apple-touch-icon-60x60.png" alt="Syft logo" class="m4-3 h1" style="max-height: 50px;"/> Syft

{{< card  title="SBOM Generator and library" footer="<a href='https://github.com/anchore/syft'>Syft GitHub Repo</a> | <a href=/docs/guides/sbom/getting-started>SBOM Generation Guide</a>" >}}
<b>Syft</b> (pronounced like <i>sift</i>) is an open-source command-line tool and Go library. Its primary function is to scan container images, file systems, and archives to automatically generate a Software Bill of Materials, making it easier to understand the composition of software.  
{{< /card >}}

#### <img src="/images/logos/grype/apple-touch-icon-60x60.png" alt="Grype logo" class="m4-3 h1" style="max-height: 50px;"/> Grype

{{< card title="Vulnerability Scanner" footer="<a href='https://github.com/anchore/grype'>Grype GitHub Repo</a> | <a href=/docs/guides/vulnerability/getting-started>Vulnerability Scanning Guide</a>" >}}
<b>Grype</b> (pronounced like <i>hype</i>) is an open-source vulnerability scanner specifically designed to analyze container images and filesystems. It works by comparing the software components it finds against a database of known vulnerabilities, providing a report of potential risks so they can be addressed.
{{< /card >}}

#### <img src="/images/logos/grant/apple-touch-icon-60x60.png" alt="Grant logo" class="m4-3 h1" style="max-height: 50px;"/> Grant

{{< card title="License Scanner" footer="<a href='https://github.com/anchore/grant'>Grant GitHub Repo</a> | <a href=/docs/guides/license/getting-started>License Scanning Guide</a>">}}
<b>Grant</b> is an open-source command-line tool designed to discover and report on the software licenses present in container images, SBOM documents, or filesystems. It helps users understand the licenses of their software dependencies and can check them against user-defined policies to ensure compliance.
{{< /card >}}

### Installing the Tools

The tools are available in many common distribution channels. The full list of official and community maintained packages can be found on the [installation](/docs/installation) page.

### Using the Tools

We have "Getting Started" user guides for [SBOM Generation](/docs/guides/sbom/getting-started) with Syft, [Vulnerability Scanning](/docs/guides/sbom/getting-started) with Grype, and [License Scanning](/docs/guides/license/getting-started).

### Developing

Developers also have [Contribution Guides](/docs/contributing/) for all of our open source tools and libraries.
