+++
title = "Getting Started"
description = "Use Grant to discover and analyze software licenses in your container images, directories, or SBOMs."
weight = 10
tags = ["grant", "licenses"]
+++

## What is License Scanning?

**License scanning** is the process of **automatically identifying and analyzing the licenses** associated with software components in your projects.

- **For developers**, it helps ensure license compliance early in development and understand the legal obligations of dependencies.

- **For organizations**, it's essential for managing legal risk, meeting compliance requirements, and avoiding license violations.

**[Grant](https://github.com/anchore/grant)** is a CLI tool for discovering and analyzing software licenses in container images, SBOM documents, and filesystems. It categorizes licenses by risk level and helps verify compliance against your policies.

## Installation

Grant is provided as a single compiled executable and requires no external dependencies to run.
Run the command for your platform to download the latest release.

{{< tabpane lang="bash">}}
{{% tab header="Platform:" disabled=true /%}}
{{< tab header="Linux (and macOS)" >}}
curl -sSfL https://get.anchore.io/grant | sudo sh -s -- -b /usr/local/bin
{{< /tab >}}
{{% tab header="macOS"%}}brew install grant{{% /tab %}}
{{< /tabpane >}}

Check out [installation guide]({{< relref "/docs/installation/grant" >}}) for full list of official and community-maintained packaging options.

{{% alert title="Note" color="primary" %}}
Grant is not currently available for Windows
{{% /alert %}}

## Discover licenses in a container image

Run `grant list` against a container image. Grant will analyze the image and display a summary table of all licenses found, categorized by risk level:

```bash
grant list alpine:latest
```

```text
 LICENSE              PACKAGES  RISK
 GPL-2.0-only                8  High
 MIT                         5  Low
 Apache-2.0                  2  Low
 BSD-2-Clause                1  Low
 GPL-2.0-or-later            1  High
 MPL-2.0                     1  Medium
 Zlib                        1  Low
```

You can also get more information with the `-o json` flag to output the full details in JSON format:

```bash
grant list alpine:latest -o json
```

Grant categorizes licenses into three risk levels:

- **High**: Strong copyleft licenses that may require source code disclosure
- **Medium**: Weak copyleft licenses with more limited obligations
- **Low**: Permissive licenses with minimal restrictions

## License detection modes

Grant performs two types of license detection:

1. **SBOM-based detection**: Analyzes package manifests and metadata to identify licenses associated with specific packages
2. **File-based detection**: Searches the filesystem for standalone license files (LICENSE, COPYING, etc.) that may not be associated with any specific package

Use `--disable-file-search` to skip file-based detection when you only want licenses that are directly associated with packages:

```bash
grant check dir:. --disable-file-search
```

This can be useful for faster scanning or when you only care about package-level license data.

## Group licenses by risk

Use `--group-by risk` to see an aggregated summary of licenses by risk category:

```bash
grant list alpine:latest --group-by risk
```

```text
 RISK CATEGORY    LICENSES  PACKAGES
 Strong Copyleft         2         9
 Weak Copyleft           1         1
 Permissive              4         8
```

This view helps you quickly assess the overall risk profile of your dependencies.

{{< alert title="Learn more" color="primary" >}}
Grant supports more than just containers. You can scan SBOM files, directories, and archives.

The target types are the same as [those supported by Syft]({{< relref "/docs/guides/sbom/scan-targets" >}}).
{{< /alert >}}

## View packages with specific licenses

To see which packages use a particular license, add the license name (or list of names) as an argument:

```bash
grant list alpine:latest MIT
```

```text
 NAME                    VERSION      LICENSE    RISK
 alpine-keys             2.5-r0       MIT        Low
 alpine-release          3.22.2-r0    MIT        Low
 ca-certificates-bundle  20250911-r0  MIT, ...   Medium (+1 more)
 musl                    1.2.5-r10    MIT        Low
 musl-utils              1.2.5-r10    BSD-2-C... High (+2 more)
```

This view shows the package-level detail, including package names, versions, and all licenses associated with each package.

### Get detailed package information

Use `--pkg` with a license filter to see detailed information about a specific package:

```bash
grant list dir:. MIT --pkg "github.com/BurntSushi/toml"
```

```text
Name:     github.com/BurntSushi/toml
Version:  v1.5.0
Type:     go-module
ID:       go-module:github.com/BurntSushi/toml@v1.5.0
Licenses (1):

• MIT
  OSI Approved: true | Deprecated: false
```

## Scan an existing SBOM for licenses

Grant can also scan an SBOM instead of a container image. The simplest approach is to pipe Syft's output directly:

```bash
syft alpine:latest -o json | grant list
```

Alternatively, scan an SBOM file you've already generated:

```bash
grant list alpine.spdx.json
```

## Check license compliance

Use `grant check` to verify that licenses comply with your organization's policies. By default, Grant uses a "deny-all" policy, flagging any licenses found:

```bash
grant check alpine:latest
```

This command exits with:

- **Exit code 0**: All licenses are compliant
- **Exit code 1**: Non-compliant licenses detected or an error occurred

{{< alert title="Learn more" color="primary" >}}
You can customize Grant's behavior by specifying a policy file. Learn more about [creating policies]({{< relref "/docs/guides/license/policies/" >}}).
{{< /alert >}}

## Find unlicensed packages

Use `--unlicensed` to identify packages that have no detected license:

```bash
grant list alpine:latest --unlicensed
```

Packages without licenses may indicate missing metadata or need manual investigation to determine their licensing terms.

## FAQ

**Does Grant need internet access?**

Only for downloading container images if you're scanning containers directly. Scanning SBOM files or local directories works completely offline.

**What license data does Grant use?**

Grant uses [SPDX (Software Package Data Exchange) license identifiers](https://spdx.org/licenses/) and categorizes them based on copyleft strength and common usage patterns.

**Can I use Grant in CI/CD pipelines?**

Absolutely! Grant is designed for automation. Use `grant check` to fail builds when non-compliant licenses are detected.

**What data does Grant send externally?**

Nothing. Grant runs entirely locally and doesn't send any data to external services.

## Next steps

{{< alert title="Continue the guide" color="success" url="/docs/guides/license/policies/" >}}
**Next**: Learn about how to enforce licnes compliance with [Policies]({{< relref "/docs/guides/license/policies/" >}}).
{{< /alert >}}

Now that you've scanned for licenses, here are additional resources:

- **Configure policies**: Run `grant config` to generate a sample configuration file with allowed licenses and packages to ignore
- **Scan for vulnerabilities**: Use [Grype]({{< relref "/docs/guides/vulnerability/getting-started/" >}}) to find security issues in your containers
- **Generate SBOMs**: Learn about [SBOM generation with Syft]({{< relref "/docs/guides/sbom/getting-started/" >}}) for comprehensive software analysis
