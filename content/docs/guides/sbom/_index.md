+++
title = "SBOM Generation"
description = "Learn how to create a Software Bill of Materials (SBOMs) for container images, filesystems, and archives using Syft."
weight = 21
tags = ["syft", "sbom"]
url = "docs/guides/sbom"
+++

An SBOM, or Software Bill of Materials, is a detailed list of all the components, libraries, and modules that make up a piece of software.

For a developer, having an SBOM is crucial for tracking dependencies, quickly identifying known vulnerabilities within those components, and ensuring license compliance.

For a consumer or organization using the software, an SBOM provides transparency into the software's supply chain, allowing them to assess potential security risks and understand what's "under the hood."  

Syft is an open-source command-line tool and Go library. Its primary function is to scan container images, file systems, and archives to automatically generate a Software Bill of Materials, making it easier to understand the composition of software.
