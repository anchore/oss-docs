"+++
title = "Getting Started"
description = "License Scanning Getting Started"
weight = 10
tags = ["grant", "licenses"]
url = "docs/userguides/license/getstarted"
+++

### Introduction

Grant searches SBOMs for licenses and the packages they belong to.

### Install the latest Grant release

Grant is provided as a single compiled executable. Issue the command for your platform to download the latest release of Grant. The full list of official and community maintained packages can be found on the [installation](/docs/installation/grant) page.

{{% alert title="Note" color="primary" %}}
Grant is not currently available for Windows
{{% /alert %}}

{{< tabpane lang="bash" >}}
{{% tab header="Platform:" disabled=true /%}}
{{% tab header="Linux (and macOS)"  %}}curl -sSfL <https://get.anchore.io/grant> | sudo sh -s -- -b /usr/local/bin{{% /tab %}}
{{% tab header="macOS" %}}brew install grant{{% /tab %}}
{{< /tabpane >}}

1. Scan a container for all the licenses used

```
grant alpine:latest
```

Grant will produce a list of licenses.

```
* alpine:latest
  * license matches for rule: default-deny-all; matched with pattern *
    * Apache-2.0
    * BSD-2-Clause
    * GPL-2.0-only
    * GPL-2.0-or-later
    * MIT
    * MPL-2.0
    * Zlib
```

1. Scan a container for OSI compliant licenses

Now we scan a different container, that contains some software that is distributed under non-OSI-compliant licenses.

{{% alert title="Note" color="primary" %}}
The image used here is quite large (over 3GB) so may take a while to download and analyze
{{% /alert %}}

```
grant check pytorch/pytorch:latest --osi-approved
```

Read more in our [License Auditing User Guide](/docs/userguides/license).

{{% alert title="Next steps" color="primary" %}}

- Try running Syft against other containers, or an application directory on your workstation.
- Find out more about [Supported Sources](/docs/userguides/sbom/sources/) and [Output Formats](/docs/userguides/sbom/formats/).
- Learn about [Vulnerability Scanning](/docs/userguides/vuln/getstarted/) and [License Scanning](/docs/userguides/license/getstarted/) your SBOMs.
  {{% /alert %}}
