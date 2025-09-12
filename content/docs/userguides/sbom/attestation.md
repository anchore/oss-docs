+++
title = "Attestation (experimental)"
linkTitle = "Attestation"
description = "SBOM Generation Attestation (experimental)"
weight = 90
tags = ["syft", "sbom", "attestation"]
url = "docs/userguides/sbom/attestation"

+++


## Attestation (experimental)

### Keyless support

Syft supports generating attestations using cosign's [keyless](https://github.com/sigstore/cosign/blob/main/KEYLESS.md) signatures.

Note: users need to have >= v1.12.0 of cosign installed for this command to function

To use this feature with a format like CycloneDX json simply run:

```
syft attest --output cyclonedx-json <IMAGE WITH OCI WRITE ACCESS>
```
This command will open a web browser and allow the user to authenticate their OIDC identity as the root of trust for the attestation (Github, Google, Microsoft).

After authenticating, Syft will upload the attestation to the OCI registry specified by the image that the user has write access to.

You will need to make sure your credentials are configured for the OCI registry you are uploading to so that the attestation can write successfully.

Users can then verify the attestation(or any image with attestations) by running:

```
COSIGN_EXPERIMENTAL=1 cosign verify-attestation <IMAGE_WITH_ATTESTATIONS>
```

Users should see that the uploaded attestation claims are validated, the claims exist within the transparency log, and certificates on the attestations were verified against [fulcio](https://github.com/SigStore/fulcio).
There will also be a printout of the certificates subject `<user identity>` and the certificate issuer URL: `<provider of user identity (Github, Google, Microsoft)>`:

```text
Certificate subject:  test.email@testdomain.com
Certificate issuer URL:  https://accounts.google.com
```

### Local private key support

To generate an SBOM attestation for a container image using a local private key:

```
syft attest --output [FORMAT] --key [KEY] [SOURCE] [flags]
```

The above output is in the form of the [DSSE envelope](https://github.com/secure-systems-lab/dsse/blob/master/envelope.md#dsse-envelope).
The payload is a base64 encoded `in-toto` statement with the generated SBOM as the predicate. For details on workflows using this command see [here](#adding-an-sbom-to-an-image-as-an-attestation-using-syft).


### Adding an SBOM to an image as an attestation using Syft

`syft attest --output [FORMAT] --key [KEY] [SOURCE] [flags]`

SBOMs themselves can serve as input to different analysis tools. [Grype](https://github.com/anchore/grype), a vulnerability scanner CLI tool from Anchore, is one such tool. Publishers of container images can use attestations to enable their consumers to trust Syft-generated SBOM descriptions of those container images. To create and provide these attestations, image publishers can run `syft attest` in conjunction with the [cosign](https://github.com/sigstore/cosign) tool to attach SBOM attestations to their images.

### Example attestation

Note for the following example replace `docker.io/image:latest` with an image you own. You should also have push access to
its remote reference. Replace `$MY_PRIVATE_KEY` with a private key you own or have generated with cosign.

```
syft attest --key $MY_PRIVATE_KEY -o spdx-json docker.io/image:latest > image_latest_sbom_attestation.json
cosign attach attestation --attestation image_latest_sbom_attestation.json docker.io/image:latest
```

Verify the new attestation exists on your image.

```
cosign verify-attestation --key $MY_PUBLIC_KEY --type spdxjson docker.io/image:latest | jq '.payload | @base64d | .payload | fromjson | .predicate'
```

You should see this output along with the attached SBOM:

```text
Verification for docker.io/image:latest --
The following checks were performed on each of these signatures:
  - The cosign claims were validated
  - The signatures were verified against the specified public key
  - Any certificates were verified against the Fulcio roots.
```

Consumers of your image can now trust that the SBOM associated with your image is correct and from a trusted source.

The SBOM can be piped to Grype:

```
cosign verify-attestation --key $MY_PUBLIC_KEY --type spdxjson docker.io/image:latest | jq '.payload | @base64d | .payload | fromjson | .predicate' | grype
```