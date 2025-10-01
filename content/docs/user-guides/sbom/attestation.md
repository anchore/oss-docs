+++
title = "Attestation"
linkTitle = "Attestation"
description = "Generate cryptographically signed SBOM attestations using in-toto and Sigstore to create, verify, and attach attestations to container images for supply chain security."
weight = 90
tags = ["syft", "sbom", "attestation"]
url = "docs/user-guides/sbom/attestation"

+++

{{< alert color="warning" title="Experimental Feature" >}}
This feature is experimental and may change in future releases.
{{< /alert >}}

## Overview

An attestation is cryptographic proof that you created a specific SBOM for a container image. When you publish an image, consumers need to trust that the SBOM accurately describes the image contents. Attestations solve this by letting you sign SBOMs and attach them to images, enabling consumers to verify authenticity.

Syft supports two approaches:

- **Keyless attestation**: Uses your identity (GitHub, Google, Microsoft) as trust root via Sigstore. Best for CI/CD and teams.
- **Local key attestation**: Uses cryptographic key pairs you manage. Best for air-gapped environments or specific security requirements.

## Prerequisites

Before creating attestations, ensure you have:

- **Syft** installed
- **Cosign** ≥ v1.12.0 installed ([installation guide](https://docs.sigstore.dev/cosign/installation/))
- **Write access** to the OCI registry where you'll publish attestations
- **Registry authentication** configured (e.g., `docker login` for Docker Hub)

For local key attestations, you'll also need a key pair. Generate one with:

```bash
cosign generate-key-pair
```

This creates `cosign.key` (private key) and `cosign.pub` (public key). Keep the private key secure.

## Keyless attestation

Keyless attestation uses Sigstore to tie your OIDC identity (GitHub, Google, or Microsoft account) to the attestation. This eliminates key management overhead.

### Create a keyless attestation

```bash
syft attest --output cyclonedx-json <IMAGE>
```

Replace `<IMAGE>` with your image reference (e.g., `docker.io/myorg/myimage:latest`). You must have write access to this image.

**What happens:**

1. Syft opens your browser to authenticate via OIDC (GitHub, Google, or Microsoft)
2. After authentication, Syft generates the SBOM
3. Sigstore signs the SBOM using your identity
4. The attestation is uploaded to the OCI registry alongside your image

### Verify a keyless attestation

Anyone can verify the attestation using cosign:

```bash
COSIGN_EXPERIMENTAL=1 cosign verify-attestation <IMAGE>
```

**Successful output shows:**

- Attestation claims are validated
- Claims exist in the Sigstore transparency log
- Certificates verified against Fulcio (Sigstore's certificate authority)
- Certificate subject (your identity email)
- Certificate issuer (identity provider URL)

Example:

```text
Certificate subject:  user@example.com
Certificate issuer URL:  https://accounts.google.com
```

This proves the attestation was created by the specified identity.

## Local key attestation

Local key attestation uses cryptographic key pairs you manage. You sign attestations with your private key, and consumers verify with your public key.

### Create a key-based attestation

Generate the attestation and save it locally:

```bash
syft attest --output spdx-json --key cosign.key docker.io/myorg/myimage:latest > attestation.json
```

The output is a [DSSE envelope](https://github.com/secure-systems-lab/dsse/blob/master/envelope.md#dsse-envelope) containing an in-toto statement with your SBOM as the predicate.

### Attach the attestation to your image

Use cosign to attach the attestation:

```bash
cosign attach attestation --attestation attestation.json docker.io/myorg/myimage:latest
```

You need write access to the image registry for this to succeed.

### Verify a key-based attestation

Consumers verify using your public key:

```bash
cosign verify-attestation --key cosign.pub --type spdxjson docker.io/myorg/myimage:latest
```

**Successful output shows:**

```text
Verification for docker.io/myorg/myimage:latest --
The following checks were performed on each of these signatures:
  - The cosign claims were validated
  - The signatures were verified against the specified public key
  - Any certificates were verified against the Fulcio roots.
```

To extract and view the SBOM:

```bash
cosign verify-attestation --key cosign.pub --type spdxjson docker.io/myorg/myimage:latest | \
  jq '.payload | @base64d | .payload | fromjson | .predicate'
```

### Use with vulnerability scanning

Pipe the verified SBOM directly to Grype for vulnerability analysis:

```bash
cosign verify-attestation --key cosign.pub --type spdxjson docker.io/myorg/myimage:latest | \
  jq '.payload | @base64d | .payload | fromjson | .predicate' | \
  grype
```

This ensures you're scanning a verified, trusted SBOM.

## Troubleshooting

### Authentication failures

- Ensure you're logged into the registry: `docker login <registry>`
- Verify you have write access to the image repository

### Cosign version errors

- Update to cosign ≥ v1.12.0: `cosign version`

### Verification failures

- For keyless: ensure `COSIGN_EXPERIMENTAL=1` is set
- For key-based: verify you're using the correct public key
- Check the attestation type matches (`--type spdxjson` or `--type cyclonedx-json`)

### Permission denied uploading attestations

- Verify write access to the registry
- Check authentication credentials are current
- Ensure the image exists in the registry before attaching attestations
