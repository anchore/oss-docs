+++
title = "Package Catalogers"
description = "SBOM Generation Package Catalogers"
weight = 50
tags = ["syft", "sbom", "catalogers"]
url = "docs/userguides/sbom/catalogers"

+++

## Package cataloger selection

### Concepts

{{% alert title="Note" color="primary" %}}
Syft uses a different set of catalogers by default when scanning files directly than it does when scanning images.
{{% /alert %}}

The catalogers for an image scan assumes that package installation steps have already been completed. For example, Syft will identify Python packages that have egg or wheel metadata files under a `site-packages` directory, since this is how the canonical tooling `pip` installs python packages.

The catalogers for a directory scan will look for installed software as well as declared dependencies that are not necessarily installed. For example, dependencies listed in a Python `requirements.txt`.

This default set of catalogers being dynamic is critical as this allows Syft to be used in a variety of contexts while still generating accurate SBOMs.
Overriding the set of default catalogers is not recommended for most purposes, however, is possible if needed.

Catalogers can be referenced in two different ways:
- *by name*: the exact cataloger name (e.g. `java-pom-cataloger` or `java-archive-cataloger`)
- *by tag*: a tag that is associated with a cataloger (e.g. `java`)

Syft can take lists of references on the CLI or in the application configuration to define which catalogers to use.

You can **set** the list of catalogers explicitly to use with the `--override-default-catalogers` CLI flag, accepting a comma-separated list of cataloger names or tags.

You can also **add** to, **remove** from, or **sub-select** catalogers to use within the default set of catalogers by using the `--select-catalogers` CLI flag.
  - To **sub-select** catalogers simply provide a tag (e.g. `--select-catalogers TAG`). Catalogers will always be selected from the default set of catalogers (e.g. `--select-catalogers java,go` will select all the `java` catalogers in the default set and all the `go` catalogers in the default set).
  - To **add** a cataloger prefix the cataloger name with `+` (e.g. `--select-catalogers +NAME`). Added catalogers will _always be added_ regardless of removals, filtering, or other defaults.
  - To **remove** a cataloger prefix the cataloger name or tag with `-` (e.g. `--select-catalogers -NAME_OR_TAG`). Catalogers are removed from the set of default catalogers after processing any sub-selections.

These rules and the dynamic default cataloger sets approximates to the following logic:

```text
image_catalogers = all_catalogers AND catalogers_tagged("image")

directory_catalogers = all_catalogers AND catalogers_tagged("directory")

default_catalogers = image_catalogers OR directory_catalogers

sub_selected_catalogers = default_catalogers INTERSECT catalogers_tagged(TAG) [ UNION sub_selected_catalogers ... ]

base_catalogers = default_catalogers OR sub_selected_catalogers

final_set = (base_catalogers SUBTRACT removed_catalogers) UNION added_catalogers
```

### Examples

Only scan for python related packages with catalogers appropriate for the source type (image or directory):

```
syft <some container image> --select-catalogers "python"
# results in the following catalogers being used:
# - python-installed-package-cataloger
```

Same command, but the set of catalogers changes based on what is being analyzed (in this case a directory):

```
syft <a directory> --select-catalogers "python"
# results in the following catalogers being used:
# - python-installed-package-cataloger
# - python-package-cataloger
```

Use the default set of catalogers and add a cataloger to the set:

```
syft ... --select-catalogers "+sbom-cataloger"
```

Use the default set of catalogers but remove any catalogers that deal with RPMs:

```
syft ... --select-catalogers "-rpm"
```

Only scan with catalogers that:
- are tagged with "go"
- always use the sbom-cataloger
- are appropriate for the source type (image or directory)

```
syft <some container image> --select-catalogers "go,+sbom-cataloger"
# results in the following catalogers being used:
# - go-module-binary-cataloger
# - sbom-cataloger
```

Scan with all catalogers that deal with binary analysis, regardless of the source type:

```
syft ... --override-default-catalogers "binary"
# results in the following catalogers being used:
# - binary-cataloger
# - cargo-auditable-binary-cataloger
# - dotnet-portable-executable-cataloger
# - go-module-binary-cataloger
```

Only scan with the specific `go-module-binary-cataloger` and `go-module-file-cataloger` catalogers:

```
syft ... --override-default-catalogers "go-module-binary-cataloger,go-module-file-cataloger"
```
