+++
title = "Data sources"
description = "Complete list of data sources used by Grype for vulnerability scanning"
weight = 30
type = "docs"
menu_group = "grype"
+++

The following are a list of data sources used to directly match packages to vulnerabilities in Grype:

{{< readfile file="/content/docs/reference/grype/snippets/data-source-provenance.md" >}}

## Capabilities

Here are the capabilities of each data source as Grype uses them:

{{< readfile file="/content/docs/reference/grype/snippets/data-source-capabilities.md" >}}

## Auxiliary data

We additionally have auxiliary data sources that are used to enhance vulnerability matching in Grype:

{{< readfile file="/content/docs/reference/grype/snippets/data-source-aux.md" >}}

These sources are cross-cutting in nature and are not tied to a specific distribution or ecosystem
(though, primarily enriching information about CVEs specifically).
