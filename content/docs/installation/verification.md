+++
tags = ['syft', 'grype', 'grant']
title = "Verifying Downloads"
description = "Verifying release assets after downloading"
weight = 50
+++

## Why verify downloads?

Verifying your downloads ensures that:

- The files haven't been tampered with during transit
- You're installing authentic Anchore software
- Your supply chain is secure from the start

All release artifacts include checksums, and the checksum file itself is cryptographically signed using cosign for verification.

{{< alert color="primary" title="Note" >}}
Installation scripts support automatic verification using the `-v` flag if you have cosign installed. This performs the same verification steps outlined below.
{{< /alert >}}

## Prerequisites

Before verifying downloads, you need:

- The binary you want to verify (see [Installation]({{< relref "/docs/installation/" >}}))
- [Cosign](https://docs.sigstore.dev/cosign/system_config/installation/) installed (for signature verification)

**Note**: Checksum verification doesn't require additional tools beyond your operating system's built-in utilities.

## Cosign signature verification

This method verifies that your download is both authentic (from Anchore) and hasn't been tampered with.

### Step 1: Download the files

Download your tool binary and the verification files from the appropriate GitHub releases page:

- [Syft releases](https://github.com/anchore/syft/releases)
- [Grype releases](https://github.com/anchore/grype/releases)
- [Grant releases](https://github.com/anchore/grant/releases)

You'll need:

- The binary file (e.g., `syft_1.23.1_darwin_arm64.tar.gz`)
- `checksums.txt`
- `checksums.txt.pem`
- `checksums.txt.sig`

### Step 2: Verify the signature

Use cosign to verify the checksum file's signature:

```bash
cosign verify-blob <path to checksums.txt> \
  --certificate <path to checksums.txt.pem> \
  --signature <path to checksums.txt.sig> \
  --certificate-identity-regexp 'https://github\.com/anchore/<tool-name>/\.github/workflows/.+' \
  --certificate-oidc-issuer "https://token.actions.githubusercontent.com"
```

Replace `<tool-name>` with `syft`, `grype`, or `grant` depending on which tool you're verifying.

**Expected output on success:**

```
Verified OK
```

### Step 3: Verify the checksum

Once the signature is confirmed as valid, verify that the SHA256 checksum matches your downloaded file:

```bash
sha256sum --ignore-missing -c checksums.txt
```

**Expected output on success:**

```
<your-binary-file>: OK
```

### Complete example

Here's a complete example verifying Syft v1.23.1 for macOS ARM64:

**Download the files:**

```bash
# Download the binary
wget https://github.com/anchore/syft/releases/download/v1.23.1/syft_1.23.1_darwin_arm64.tar.gz

# Download verification files
wget https://github.com/anchore/syft/releases/download/v1.23.1/syft_1.23.1_checksums.txt
wget https://github.com/anchore/syft/releases/download/v1.23.1/syft_1.23.1_checksums.txt.pem
wget https://github.com/anchore/syft/releases/download/v1.23.1/syft_1.23.1_checksums.txt.sig
```

**Verify the signature:**

```bash
cosign verify-blob ./syft_1.23.1_checksums.txt \
  --certificate ./syft_1.23.1_checksums.txt.pem \
  --signature ./syft_1.23.1_checksums.txt.sig \
  --certificate-identity-regexp 'https://github\.com/anchore/syft/\.github/workflows/.+' \
  --certificate-oidc-issuer "https://token.actions.githubusercontent.com"
```

**Output:**

```
Verified OK
```

**Verify the checksum:**

```bash
sha256sum --ignore-missing -c syft_1.23.1_checksums.txt
```

**Output:**

```
syft_1.23.1_darwin_arm64.tar.gz: OK
```

## Checksum verification

If you can't use cosign, you can verify checksums manually. This verifies file integrity but not authenticity.

{{< alert color="warning" title="Security Note" >}}
Checksum verification only confirms the file hasn't been corrupted. It doesn't verify that the file is authentic. Use cosign verification when possible for better security.
{{< /alert >}}

### Step 1: Download the files

Download your tool binary and the checksums file:

```bash
# Example for Syft v1.23.1
wget https://github.com/anchore/syft/releases/download/v1.23.1/syft_1.23.1_darwin_arm64.tar.gz
wget https://github.com/anchore/syft/releases/download/v1.23.1/syft_1.23.1_checksums.txt
```

### Step 2: Verify the checksum

```bash
sha256sum --ignore-missing -c syft_1.23.1_checksums.txt
```

**Expected output:**

```
syft_1.23.1_darwin_arm64.tar.gz: OK
```

## Troubleshooting

### Verification failed

If cosign verification fails, check these common issues:

- **Mismatched certificate identity**: Ensure you're using the correct tool name (`syft`, `grype`, or `grant`) in the certificate identity pattern
- **Outdated cosign**: Update to the latest version of cosign
- **Network connectivity**: Cosign requires internet access to verify against transparency logs
- **Corrupted download**: Try downloading the verification files again

### Checksum doesn't match

If the checksum verification fails:

- **Download again**: The file may have been corrupted during download
- **Check the filename**: Ensure you're comparing the checksum for the correct file (right version, architecture, and tool)
- **Do not proceed**: A mismatched checksum indicates a potential security issue or corruption

{{< alert color="danger" title="Security Warning" >}}
If verification fails repeatedly with newly downloaded files, do not use the binary. Report the issue on the appropriate GitHub repository.
{{< /alert >}}

### Platform-specific issues

**macOS:**

- If you get a "command not found" error for `sha256sum`, use `shasum -a 256` instead
- Example: `shasum -a 256 syft_1.23.1_darwin_arm64.tar.gz`

**Windows:**

- Use PowerShell's `Get-FileHash` command:

  ```powershell
  Get-FileHash .\syft_1.23.1_windows_amd64.zip -Algorithm SHA256
  ```

### Need help?

If you're still having issues:

- Check the [GitHub Discussions](https://github.com/anchore/syft/discussions) for your tool
- Review the [Cosign documentation](https://docs.sigstore.dev/cosign/overview/)
- Open an issue on the appropriate repository
