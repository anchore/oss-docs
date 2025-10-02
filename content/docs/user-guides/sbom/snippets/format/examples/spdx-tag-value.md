```
SPDXVersion: SPDX-2.3
DataLicense: CC0-1.0
SPDXID: SPDXRef-DOCUMENT
DocumentName: busybox
DocumentNamespace: https://anchore.com/syft/image/busybox-b39723f8-5c34-49d7-b928-aeac1021603c
LicenseListVersion: 3.27
Creator: Organization: Anchore, Inc
Creator: Tool: syft-1.33.0
Created: 2025-10-02T01:46:51Z

##### Unpackaged files

FileName: bin/[
SPDXID: SPDXRef-File-bin---de0bf36b25443562
FileChecksum: SHA1: 0000000000000000000000000000000000000000
LicenseConcluded: NOASSERTION
LicenseInfoInFile: NOASSERTION
FileCopyrightText: NOASSERTION
FileComment: layerID: sha256:6aba5e0d32d91e3e923854dcb30588dc4112bfa1dae82b89535ad31d322a7b19

##### Package: busybox

PackageName: busybox
SPDXID: SPDXRef-DocumentRoot-Image-busybox
PackageVersion: sha256:cddc8af5547af9de5e6fb66b36d66ef7418561204e1255ae528d0b2c919d09a3
PackageSupplier: NOASSERTION
PackageDownloadLocation: NOASSERTION
PrimaryPackagePurpose: CONTAINER
FilesAnalyzed: false
PackageChecksum: SHA256: cddc8af5547af9de5e6fb66b36d66ef7418561204e1255ae528d0b2c919d09a3
PackageLicenseConcluded: NOASSERTION
PackageLicenseDeclared: NOASSERTION
PackageCopyrightText: NOASSERTION
ExternalRef: PACKAGE-MANAGER purl pkg:oci/busybox@sha256%3Acddc8af5547af9de5e6fb66b36d66ef7418561204e1255ae528d0b2c919d09a3?arch=arm64&tag=latest

##### Package: busybox

PackageName: busybox
SPDXID: SPDXRef-Package-binary-busybox-74d9294c42941b37
PackageVersion: 1.37.0
PackageSupplier: NOASSERTION
PackageDownloadLocation: NOASSERTION
FilesAnalyzed: false
PackageSourceInfo: acquired package info from the following paths: /bin/[
PackageLicenseConcluded: NOASSERTION
PackageLicenseDeclared: NOASSERTION
PackageCopyrightText: NOASSERTION
ExternalRef: SECURITY cpe23Type cpe:2.3:a:busybox:busybox:1.37.0:*:*:*:*:*:*:*
ExternalRef: PACKAGE-MANAGER purl pkg:generic/busybox@1.37.0

##### Relationships

Relationship: SPDXRef-Package-binary-busybox-74d9294c42941b37 OTHER SPDXRef-File-bin---de0bf36b25443562
RelationshipComment: evident-by: indicates the package's existence is evident by the given file
Relationship: SPDXRef-DocumentRoot-Image-busybox CONTAINS SPDXRef-Package-binary-busybox-74d9294c42941b37
Relationship: SPDXRef-DOCUMENT DESCRIBES SPDXRef-DocumentRoot-Image-busybox
```
