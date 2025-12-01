+++
title = "License Scanning"
description = "Learn how to scan container images and filesystems for software licenses covering detection, compliance checking, and managing license obligations."
weight = 41
tags = ["syft", "grant", "licenses"]
manualLinkRelref = "/docs/guides/license/getting-started"
icon_image = "/images/logos/grant/favicon-48x48.png"
+++

License scanning is the automated process of identifying and analyzing the licenses associated with software components in your projects.
This is important because most software relies on third-party and open-source components, each with its own licensing terms that dictate how the software can be used, modified, and distributed, and failing to comply can lead to legal issues.

Grant is an open-source command-line tool designed to discover and report on the software licenses present in container images, SBOM documents, or filesystems. It helps users understand the licenses of their software dependencies and can check them against user-defined policies to ensure compliance.
