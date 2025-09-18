+++
title = "Projects"
description = "Overview of Anchore Open Source tools."
weight = 10
tags = ["syft", "grype", "grant"]
url = "docs/projects"
+++

### Anchore Open Source Tools

We maintain three popular command-line tools, some libraries, and supporting utilities. Most are written in Go, with a few in Python. They are all released under the Apache-2.0 license. For the full list, see our [GitHub org](https://github.com/orgs/anchore/repositories).

#### <img src="/images/logos/syft/apple-touch-icon-60x60.png" alt="Syft logo" class="m4-3 h1" style="max-height: 50px;"/> Syft

{{< card  title="SBOM Generator and library" footer="<a href=<https://github.com/anchore/syft>Syft</a> GitHub Repo</a> | <a href=/docs/userguides/sbom/getstarted>SBOM Generation Guide</a>" >}}
<b>Syft</b> (pronounced like <i>sift</i>) is an open-source command-line tool and Go library. Its primary function is to scan container images, file systems, and archives to automatically generate a Software Bill of Materials, making it easier to understand the composition of software.  
{{< /card >}}

#### <img src="/images/logos/grype/apple-touch-icon-60x60.png" alt="Grype logo" class="m4-3 h1" style="max-height: 50px;"/> Grype

{{< card title="Vulnerability Scanner" footer="<a href=<https://github.com/anchore/grype>Grype</a> GitHub Repo</a> | <a href=/docs/userguides/vuln/getstarted>Vulnerability Scanning Guide</a>" >}}
<b>Grype</b> (pronounced like <i>hype</i>) is an open-source vulnerability scanner specifically designed to analyze container images and filesystems. It works by comparing the software components it finds against a database of known vulnerabilities, providing a report of potential risks so they can be addressed.
{{< /card >}}

#### <img src="/images/logos/grant/apple-touch-icon-60x60.png" alt="Grant logo" class="m4-3 h1" style="max-height: 50px;"/> Grant

{{< card title="License Scanner" footer="<a href=<https://github.com/anchore/grant>Grant</a> GitHub Repo</a> | <a href=/docs/userguides/license/getstarted>License Scanning Guide</a>">}}
<b>Grant</b> is an open-source command-line tool designed to discover and report on the software licenses present in container images, SBOM documents, or filesystems. It helps users understand the licenses of their software dependencies and can check them against user-defined policies to ensure compliance.
{{< /card >}}

### Installing the Tools

The tools are available in many common distribution channels. The full list of official and community maintained packages can be found on the [installation](/docs/installation) page.

### Using the Tools

We have "Getting Started" user guides for [SBOM Generation](/docs/userguides/sbom/getstarted) with Syft, [Vulnerability Scanning](/docs/userguides/sbom/getstarted) with Grype, and [License Scanning](/docs/userguides/license/getstarted).

### Developing

Developers also have [Contribution Guides](/docs/contributing/) for all of our open source tools and libraries.
