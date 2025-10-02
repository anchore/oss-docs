```json
{
  "spdxVersion": "SPDX-2.3",
  "dataLicense": "CC0-1.0",
  "SPDXID": "SPDXRef-DOCUMENT",
  "name": "busybox",
  "documentNamespace": "https://anchore.com/syft/image/busybox-03efca37-5574-462a-9838-bbbca8c4cf5c",
  "creationInfo": {
    "licenseListVersion": "3.27",
    "creators": ["Organization: Anchore, Inc", "Tool: syft-1.33.0"],
    "created": "2025-10-02T01:46:48Z"
  },
  "packages": [
    {
      "name": "busybox",
      "SPDXID": "SPDXRef-Package-binary-busybox-74d9294c42941b37",
      "versionInfo": "1.37.0",
      "supplier": "NOASSERTION",
      "downloadLocation": "NOASSERTION",
      "filesAnalyzed": false,
      "sourceInfo": "acquired package info from the following paths: /bin/[",
      "licenseConcluded": "NOASSERTION",
      "licenseDeclared": "NOASSERTION",
      "copyrightText": "NOASSERTION",
      "externalRefs": [
        {
          "referenceCategory": "SECURITY",
          "referenceType": "cpe23Type",
          "referenceLocator": "cpe:2.3:a:busybox:busybox:1.37.0:*:*:*:*:*:*:*"
        },
        {
          "referenceCategory": "PACKAGE-MANAGER",
          "referenceType": "purl",
          "referenceLocator": "pkg:generic/busybox@1.37.0"
        }
      ]
    },
    {
      "name": "busybox",
      "SPDXID": "SPDXRef-DocumentRoot-Image-busybox",
      "versionInfo": "sha256:cddc8af5547af9de5e6fb66b36d66ef7418561204e1255ae528d0b2c919d09a3",
      "supplier": "NOASSERTION",
      "downloadLocation": "NOASSERTION",
      "filesAnalyzed": false,
      "checksums": [
        {
          "algorithm": "SHA256",
          "checksumValue": "cddc8af5547af9de5e6fb66b36d66ef7418561204e1255ae528d0b2c919d09a3"
        }
      ],
      "licenseConcluded": "NOASSERTION",
      "licenseDeclared": "NOASSERTION",
      "copyrightText": "NOASSERTION",
      "externalRefs": [
        {
          "referenceCategory": "PACKAGE-MANAGER",
          "referenceType": "purl",
          "referenceLocator": "pkg:oci/busybox@sha256%3Acddc8af5547af9de5e6fb66b36d66ef7418561204e1255ae528d0b2c919d09a3?arch=arm64&tag=latest"
        }
      ],
      "primaryPackagePurpose": "CONTAINER"
    }
  ],
  "files": [
    {
      "fileName": "bin/[",
      "SPDXID": "SPDXRef-File-bin---de0bf36b25443562",
      "checksums": [
        {
          "algorithm": "SHA1",
          "checksumValue": "0000000000000000000000000000000000000000"
        }
      ],
      "licenseConcluded": "NOASSERTION",
      "licenseInfoInFiles": ["NOASSERTION"],
      "copyrightText": "NOASSERTION",
      "comment": "layerID: sha256:6aba5e0d32d91e3e923854dcb30588dc4112bfa1dae82b89535ad31d322a7b19"
    }
  ],
  "relationships": [
    {
      "spdxElementId": "SPDXRef-Package-binary-busybox-74d9294c42941b37",
      "relatedSpdxElement": "SPDXRef-File-bin---de0bf36b25443562",
      "relationshipType": "OTHER",
      "comment": "evident-by: indicates the package's existence is evident by the given file"
    },
    {
      "spdxElementId": "SPDXRef-DocumentRoot-Image-busybox",
      "relatedSpdxElement": "SPDXRef-Package-binary-busybox-74d9294c42941b37",
      "relationshipType": "CONTAINS"
    },
    {
      "spdxElementId": "SPDXRef-DOCUMENT",
      "relatedSpdxElement": "SPDXRef-DocumentRoot-Image-busybox",
      "relationshipType": "DESCRIBES"
    }
  ]
}
```
