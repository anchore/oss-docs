+++
title = "Getting Started"
description = "Vulnerability Scanning Getting Started"
weight = 10
tags = ["grype", "vulnerabilities"]
url = "docs/userguides/vuln/getstarted"
+++

### Introduction

Grype is an easy-to-integrate open source vulnerability scanning tool for container images and filesystems.

### Install the latest Grype release

Grype is provided as a single compiled executable. Issue the command for your platform to download the latest release of Grype. The full list of official and community maintained packages can be found on the [installation](/docs/installation/grype) page.

{{< tabpane lang="bash">}}
{{% tab header="Platform:" disabled=true /%}}
{{% tab header="Linux (and macOS)" %}}curl -sSfL <https://get.anchore.io/grype> | sudo sh -s -- -b /usr/local/bin{{% /tab %}}
{{% tab header="macOS"%}}brew install grype{{% /tab %}}
{{% tab header="Windows"%}}nuget install Anchore.Grype{{% /tab %}}
{{< /tabpane >}}

Once installed, ensure the `grype` binary is in the `PATH` for your system.

### Scan a container for vulnerabilities

```
grype <image>
```

### Scan a public container image for vulnerabilities

Run `grype` with default options against a small container, which will be pulled from DockerHub. Grype will also download the latest vulnerability database. The output will be a simple human-readable table.

```
grype alpine:latest
```

```text
 ✔ Loaded image alpine:latest
 ✔ Parsed image sha256:8d591b0b7dea080ea3be9e12ae563eebf9…
 ✔ Cataloged contents 058c92d86112aa6f641b01ed238a07a3885…
   ├── ✔ Packages                        [15 packages]
   ├── ✔ File metadata                   [82 locations]
   ├── ✔ File digests                    [82 files]
   └── ✔ Executables                     [17 executables]
 ✔ Scanned for vulnerabilities     [6 vulnerability matches]
   ├── by severity: 0 critical, 0 high, 0 medium, 6 low, 0 negligible
   └── by status:   0 fixed, 6 not-fixed, 0 ignored
NAME           INSTALLED   FIXED-IN  TYPE  VULNERABILITY   SEVERITY
busybox        1.37.0-r12            apk   CVE-2024-58251  Low
busybox        1.37.0-r12            apk   CVE-2025-46394  Low
busybox-binsh  1.37.0-r12            apk   CVE-2024-58251  Low
busybox-binsh  1.37.0-r12            apk   CVE-2025-46394  Low
ssl_client     1.37.0-r12            apk   CVE-2024-58251  Low
ssl_client     1.37.0-r12            apk   CVE-2025-46394  Low
```

### Scan an existing SBOM for vulnerabilities

Grype can scan containers directly, but it can also scan an existing SBOM document.

{{% alert title="Note" color="primary" %}}
This presumes you already created `alpine_latest-spdx.json` using Syft, or some other tool. If not, go to [SBOM Generation Getting Started](/docs/userguides/sbom/getstarted) and create it now.
{{% /alert %}}

```
grype alpine_latest-spdx.json
```

Grype should give similar output to the previous table.

### Create a vulnerability report in JSON format

The JSON-formatted output from Grype may be processed or visualized by other tools.

Create the vulnerability report using the `--output`, and via `jq` to make it prettier.

```
grype alpine:latest --output json | jq . > vuln_report.json
```

Example:

```
 ✔ Pulled image
 ✔ Loaded image alpine:latest
 ✔ Parsed image sha256:8d591b0b7dea080ea3be9e12ae563eebf9869168ffced1cb25b2470a3d9fe15e
 ✔ Cataloged contents 058c92d86112aa6f641b01ed238a07a3885b8c0815de3e423e5c5f789c398b45
   ├── ✔ Packages                        [15 packages]
   ├── ✔ File digests                    [82 files]
   ├── ✔ Executables                     [17 executables]
   └── ✔ File metadata                   [82 locations]
 ✔ Scanned for vulnerabilities     [6 vulnerability matches]
   ├── by severity: 0 critical, 0 high, 0 medium, 6 low, 0 negligible
   └── by status:   0 fixed, 6 not-fixed, 0 ignored
```

### Create an HTML Vulnerability Report

{{% alert title="Next steps" color="primary" %}}

- Try searching for vulnerabilities in an older container!
- Find out more about [TODO](/docs/userguides/vuln/todo/) and [)TODO(/docs/userguides/vuln/todo/)
- Learn about [SBOM Generation](/docs/userguides/sbom/getstarted/) and [License Scanning](/docs/userguides/license/getstarted/) your SBOMs.
  {{% /alert %}}
