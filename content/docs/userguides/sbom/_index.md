+++
title = "SBOM Generation"
description = "SBOM Generation User Guide"
weight = 21
tags = ["syft", "sbom"]
url = "docs/userguides/sbom"
+++

An SBOM, or Software Bill of Materials, is a detailed list of all the components, libraries, and modules that make up a piece of software. 

For a developer, having an SBOM is crucial for tracking dependencies, quickly identifying known vulnerabilities within those components, and ensuring license compliance. 

For a consumer or organization using the software, an SBOM provides transparency into the software's supply chain, allowing them to assess potential security risks and understand what's "under the hood."   

Syft is an open-source command-line tool and Go library. Its primary function is to scan container images, file systems, and archives to automatically generate a Software Bill of Materials, making it easier to understand the composition of software.

- [Get Started](/docs/userguides/sbom/getstarted) - Install Syft, create an SBOM and examine the contents.
- [Supported Sources](/docs/userguides/sbom/sources) - The variety of sources supported by our tools.
- [File Selection](/docs/userguides/sbom/fileselection) - Specify which files will be cataloged.
- [Output Formats](/docs/userguides/sbom/formats) - The industry-standard supported SBOM formats.
- [Configuration](/docs/userguides/sbom/configuration) - Configuring Syft for your environment and requirements.