+++
title = "Getting Started"
description = "Get started with Syft to generate your first SBOM from container images, directories, or archives with basic usage and quick commands."
weight = 10
tags = ["syft", "sbom"]
url = "docs/user-guides/sbom/getting-started"
+++

## What is an SBOM?

A Software Bill of Materials (SBOM) is a complete inventory of all the software components in your application. Think of it like an ingredients list on food packaging—it tells you exactly what's inside.

**Why does this matter?**

- **Security**: When a vulnerability is discovered (like the Log4Shell vulnerability in 2021), an SBOM lets you instantly know if you're affected within minutes instead of days
- **Compliance**: Many industries and regulations now require SBOMs for software transparency
- **License management**: Understand what licenses your dependencies use to avoid legal issues
- **Supply chain visibility**: Know exactly what third-party code you're running in production

## What is Syft?

Syft is a command-line tool that automatically generates SBOMs by analyzing your software. Instead of manually tracking every dependency, Syft scans container images, directories, and archives to create comprehensive SBOMs in seconds.

**What Syft detects:**

- Programming language packages (Python, Go, Java, JavaScript, etc.)
- Operating system packages (APK, DEB, RPM)
- Application dependencies and their versions
- File locations and checksums (to verify integrity)

## Prerequisites

Before you begin, you'll need:

- **A container runtime**: Docker, Podman, or similar (for scanning container images)
- **Command-line access**: Basic familiarity with terminal/command prompt
- **Optional**: `jq` for querying JSON output (we'll show you how to use it later)

Don't have Docker installed? Syft can also scan local directories without a container runtime.

## Installation

Choose your platform and install Syft:

{{< tabpane lang="bash">}}
{{% tab header="Platform:" disabled=true /%}}
{{< tab header="Linux (and macOS)" >}}
curl -sSfL https://get.anchore.io/syft | sudo sh -s -- -b /usr/local/bin
{{< /tab >}}
{{% tab header="macOS"%}}brew install syft{{% /tab %}}
{{% tab header="Windows"%}}nuget install Anchore.Syft{{% /tab %}}
{{< /tabpane >}}

See the [installation guide](/docs/installation/syft) for more options including package managers and manual installation.

### Verify installation

Confirm Syft is installed correctly:

```bash
syft version
```

Expected output:

```
Application:    syft
Version:        1.0.0
GitCommit:      abc123def
BuildDate:      2024-01-01T00:00:00Z
```

If you get a "command not found" error, make sure the `syft` binary is in your system's `PATH`.

## Your first SBOM

Let's generate your first SBOM by scanning a small public container image. We'll use Alpine Linux, which is minimal and downloads quickly:

```bash
syft alpine:latest
```

**What's happening:**

1. Syft pulls the Alpine Linux container image from Docker Hub (~3-5 MB download)
2. Analyzes the image contents to find all software packages
3. Displays the results in an easy-to-read table format

### Understanding the output

You'll see progress indicators followed by a summary table:

```
 ✔ Pulled image                                    ← Downloaded from registry
 ✔ Loaded image alpine:latest                      ← Loaded into Syft
 ✔ Parsed image sha256:8d591b0b...                 ← Analyzed image structure
 ✔ Cataloged contents 058c92d86...
   ├── ✔ Packages                        [15 packages]     ← Software packages found
   ├── ✔ File metadata                   [82 locations]    ← Files indexed
   ├── ✔ File digests                    [82 files]        ← Checksums calculated
   └── ✔ Executables                     [17 executables]  ← Programs identified

NAME                    VERSION      TYPE
alpine-baselayout       3.6.8-r1     apk
alpine-baselayout-data  3.6.8-r1     apk
alpine-keys             2.5-r0       apk
...
```

**Understanding the columns:**

- **NAME**: The package name
- **VERSION**: The specific version installed
- **TYPE**: Package format (Alpine uses `apk`, Ubuntu uses `deb`, Red Hat uses `rpm`)

{{% alert title="Success!" color="success" %}}
You've generated your first SBOM! This table shows every software package in the Alpine Linux image. Ready to save it to a file? Continue to the next section.
{{% /alert %}}

### Quick example: Finding a specific package

Let's say you heard about a security issue in the `openssl` package and need to check if Alpine uses it:

```bash
syft alpine:latest | grep openssl
```

You'll immediately see if OpenSSL is present and which version. This takes seconds instead of manually inspecting the entire system.

{{% alert title="Beyond containers" color="primary" %}}
Syft can scan more than just containers. Learn about all [Supported Sources](/docs/user-guides/sbom/sources/) including directories, archives, and more.
{{% /alert %}}

## Saving your SBOM to a file

The table view is great for quick checks, but you'll usually want to save SBOMs as files for:

- Sharing with your security team
- Uploading to vulnerability scanners
- Storing in artifact repositories
- Compliance documentation

Let's save an SBOM in SPDX format (pronounced "S-P-D-X"), an industry-standard format that most security tools understand:

```bash
syft alpine:latest -o spdx-json=alpine-sbom.spdx.json
```

**What this does:**

- `-o spdx-json`: Specifies SPDX JSON format
- `=alpine-sbom.spdx.json`: Names the output file

You can also display the table *and* save to a file simultaneously:

```bash
syft alpine:latest -o table -o spdx-json=alpine-sbom.spdx.json
```

{{% alert title="Multiple formats" color="primary" %}}
Syft supports multiple SBOM formats including SPDX, CycloneDX, and Syft's native JSON. Learn more about [Output Formats](/docs/user-guides/sbom/formats/).
{{% /alert %}}

## Exploring your SBOM

The SPDX JSON file contains detailed package information in a standardized format. You can:

- Open it in any text editor to view the raw data
- Upload it to security scanning tools like Grype
- Query it programmatically using tools like `jq`

{{% alert title="Working with SBOM data" color="primary" %}}
Want to query and filter your SBOM data? Check out the [Working with Syft JSON](/docs/user-guides/sbom/syft-json/) guide for practical examples using `jq` and other tools.
{{% /alert %}}

## Scanning your own projects

Now that you understand the basics, try scanning your own software:

**Scan a container image:**

```bash
syft your-image:tag -o json=sbom.json
```

**Scan a local directory:**

```bash
# Example: scan a Python project
syft dir:~/projects/my-python-app -o json=sbom.json
```

**Scan the current directory:**

```bash
syft . -o json=sbom.json
```

## Advanced: Scanning all image layers

By default, Syft scans only the final container image (what you'd actually run). Container images are built in layers, and sometimes files are added in one layer and removed in another.

If you want to see *everything* that was present at any point during the build process, use `--scope all-layers`:

```bash
syft alpine:latest --scope all-layers
```

**When to use this:**

- Auditing your build process for security compliance
- Finding packages that were installed and later removed
- Investigating how your image was constructed
- Ensuring secrets weren't present in intermediate layers

## Troubleshooting

**"Cannot connect to Docker daemon"**

Make sure Docker is running:

```bash
docker ps
```

If you see an error, start Docker Desktop or the Docker service.

**"Permission denied"**

On Linux, you may need to add your user to the docker group:

```bash
sudo usermod -aG docker $USER
```

Then log out and back in.

**Scan taking a very long time?**

Large images (1GB+) can take several minutes. Use `--quiet` to reduce output:

```bash
syft large-image:latest --quiet -o json=sbom.json
```

## Common questions

**How long does scanning take?**

Small images like Alpine scan in 2-5 seconds. Large production images (1GB+) typically take 30-60 seconds depending on your hardware.

**Does Syft need internet access?**

Only to download container images. Scanning local directories works offline.

**What about private container registries?**

Syft supports authentication for private registries. See [Authentication](/docs/user-guides/sbom/authentication/).

**Can I use Syft in CI/CD pipelines?**

Absolutely! Syft is designed for automation. Generate SBOMs during builds and scan them for vulnerabilities.

**What data does Syft send externally?**

Nothing. Syft runs entirely locally and doesn't send any data to external services.

## Next steps

Now that you've generated your first SBOM, explore what you can do with it:

- **Scan for vulnerabilities**: Use [Grype](/docs/user-guides/vulnerability/getting-started/) to find security issues in your SBOMs
- **Check licenses**: Learn about [License Scanning](/docs/user-guides/license/getting-started/) to understand dependency licenses
- **Customize output**: Explore different [Output Formats](/docs/user-guides/sbom/formats/) for various tools and workflows
- **Scan different sources**: Discover all [Supported Sources](/docs/user-guides/sbom/sources/) Syft can analyze
- **Query SBOM data**: Master [Working with Syft JSON](/docs/user-guides/sbom/syft-json/) for advanced data extraction
