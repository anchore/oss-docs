+++
title = "Binary"
description = "Binary package analysis and vulnerability scanning capabilities"
weight = 30
type = "docs"
menu_group = "other"
+++

## File analysis

Within the `.files[].executable` sections of the Syft JSON there is an analysis of what features and claims were found within a binary file.

This includes:

- Imported libraries (shared libraries)
- Exported symbols
- Security features (like NX, PIE, RELRO, etc)

Security features that can be detected include:

- if debugging symbols have been stripped
- presence of _Stack Canaries_ to protect against stack smashing (which lead to buffer overflows)
- _NoExecute_ (NX) bit support to prevent execution of code on the stack or heap
- _Relocation Read-Only_ (RelRO) to protect the Global Offset Table (GOT) from being overwritten (can be "partial" or "full")
- _Position Independent Executable_ (PIE) support such that offsets are used instead of absolute addresses
- if it is a _Dynamic Shared Object_ (DSO) (not a security feature, but important for analysis)
- [LLVM SafeStack](https://clang.llvm.org/docs/SafeStack.html) partitioning is in use, which separates unsafe stack objects from safe stack objects to mitigate stack-based memory corruption vulnerabilities
- [LLVM Control Flow Integrity](https://clang.llvm.org/docs/ControlFlowIntegrity.html) (CFI) is in use, which adds runtime checks to ensure that indirect function calls only target valid functions, helping to prevent control-flow hijacking attacks
- [Clang Fortified Builds](https://clang.llvm.org/docs/ClangFortifyBuild.html) is enabled, which adds additional runtime checks for certain standard library functions to detect buffer overflows and other memory errors

When it comes to shared library requirement claims and exported symbol claims, these are used by Syft to:

- associate file-to-file relationships (in the case of executables/shared libraries being distributed without a package manager)
- associate file-to-package relationships (when an executable imports a shared library that is managed by a package manager)

Say that all package manager information has been stripped from a container image, leaving behind a collection of binary files (some of which may be executables or shared libraries).
In this case Syft can still synthesize a dependency graph from the imported libraries and exported symbols found within the binaries, allowing for a more complete SBOM to be generated.
In a mixed case, where there are some packages managed by package managers and some binaries without package manager metadata, Syft can still use the binary analysis to fill in the gaps.
Package-level relationships are preferred over file-level relationships when both are available, which simplifies the dependency graph.

## Package analysis

{{< readfile file="/content/docs/capabilities/snippets/ecosystem/binary/package.md" >}}

{{< readfile file="/content/docs/capabilities/snippets/ecosystem/binary/binary-package-details.md" >}}

### ELF package notes

Syft is capable of looking at ELF formatted binaries, specifically the `.note.package` note, that are formatted using the [convention established by the systemd project](https://systemd.io/PACKAGE_METADATA_FOR_EXECUTABLE_FILES/).
This spec requires a PE/COFF section that wraps a json payload describing the package metadata for the binary, however, syft does not require the PE/COFF wrapping and can extract the json payload directly from the ELF note.

Here's an example of what the json payload looks like:

```json
{
  "name": "my-application",
  "version": "1.2.3",
  "purl": "pkg:deb/debian/my-application@1.2.3?arch=amd64&distro=debian-12",
  "cpe": "cpe:2.3:a:vendor:my-application:1.2.3:*:*:*:*:*:*:*",
  "license": "Apache-2.0",
  "type": "deb"
}
```

Which, if stored in `payload.json`, can be injected into an existing ELF binary using the following command:

```bash
objcopy --add-section .note.package=payload.json --set-section-flags .note.package=noload,readonly
```

## Vulnerability scanning

{{< readfile file="/content/docs/capabilities/snippets/ecosystem/binary/vulnerability.md" >}}

{{< readfile file="/content/docs/capabilities/snippets/ecosystem/binary/grype-app-config.md" >}}

## Next steps

- [Syft package analysis]({{< ref "docs/guides/sbom" >}})
- [Grype vulnerability scanning]({{< ref "docs/guides/vulnerability" >}})
