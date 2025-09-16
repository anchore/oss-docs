+++
tags = ['syft', 'grype', 'grant']
title = "Verifying Downloads"
description = "Verifying release assets after downloading"
weight = 50
url = "docs/installation/verification"
+++

## Verifying the artifacts

Checksums are applied to all artifacts, and the resulting checksum file is signed using cosign.

You need the following tool to verify signature:

- [Cosign](https://docs.sigstore.dev/cosign/system_config/installation/)

Verification steps are as follow:

1. Download the files you want, and the checksums.txt, checksums.txt.pem and checksums.txt.sig files from the appropriate GitHub:

- [Syft](https://github.com/anchore/syft/releases)
- [Grype](https://github.com/anchore/grype/releases)
- [Grant](https://github.com/anchore/grant/releases)

1. Verify the signature:

Use `cosign` to verify.

```
cosign verify-blob <path to checksum.txt> \
--certificate <path to checksums.txt.pem> \
--signature <path to checksums.txt.sig> \
--certificate-identity-regexp 'https://github\.com/anchore/<name of tool>/\.github/workflows/.+' \
--certificate-oidc-issuer "https://token.actions.githubusercontent.com"
```

Here's an example of verifying the macOS arm64 Syft v1.23.1 tarball in the current directory:

First, we download the Syft tarball directly from the [GitHub releases](https://github.com/anchore/syft/releases/tag/v1.23.1) page for Syft v1.23.1:

```
wget https://github.com/anchore/syft/releases/download/v1.23.1/syft_1.23.1_darwin_arm64.tar.gz
```

Then we grab the files required to verify the download:

```
wget https://github.com/anchore/syft/releases/download/v1.23.1/syft_1.23.1_checksums.txt
wget https://github.com/anchore/syft/releases/download/v1.23.1/syft_1.23.1_checksums.txt.pem
wget https://github.com/anchore/syft/releases/download/v1.23.1/syft_1.23.1_checksums.txt.sig
```

The `cosign` command will look a bit like this:

```
cosign verify-blob ./syft_1.23.1_checksums.txt \
--certificate ./syft_1.23.1_checksums.txt.pem \
--signature ./syft_1.23.1_checksums.txt.sig \
--certificate-identity-regexp 'https://github\.com/anchore/syft/\.github/workflows/.+' \
--certificate-oidc-issuer "https://token.actions.githubusercontent.com"
```

The resulting output, if successful, looks like this:

```
Verified OK
```

1. Once the signature is confirmed as valid, you can proceed to validate that the SHA256 sums align with the downloaded artifact:

```
sha256sum --ignore-missing -c checksums.txt
```

In our example above, that command looks like this:

```
sha256sum --ignore-missing -c syft_1.23.1_checksums.txt
```

If successful, we will get this output:

```
syft_1.23.1_darwin_arm64.tar.gz: OK
```
