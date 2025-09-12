+++
title = "Using Templates"
description = "SBOM Generation Using Templates"
weight = 60
tags = ["syft", "sbom", "templates"]
url = "docs/userguides/sbom/templates"
+++

## Using templates

Syft lets you define custom output formats, using [Go templates](https://pkg.go.dev/text/template) relative to the Syft JSON output. Here's how it works:

- Define your format as a Go template, and save this template as a file.

- Set the output format to "template" (`-o template`).

- Specify the path to the template file (`-t ./path/to/custom.template`).

- Syft's template processing uses the same data models as the `syft-json` output format — so if you're wondering what data is available as you author a template, you can use the output from `syft <image> -o syft-json` as a reference.

**Example:** You could make Syft output data in CSV format by writing a Go template that renders CSV data and then running `syft <image> -o template -t ~/path/to/csv.tmpl`.

Here's what the `csv.tmpl` file might look like:
```gotemplate
"Package","Version Installed", "Found by"
{{- range .artifacts}}
"{{.name}}","{{.version}}","{{.foundBy}}"
{{- end}}
```

Which would produce output like:
```text
"Package","Version Installed","Found by"
"alpine-baselayout","3.2.0-r20","apkdb-cataloger"
"alpine-baselayout-data","3.2.0-r20","apkdb-cataloger"
"alpine-keys","2.4-r1","apkdb-cataloger"
...
```

Syft also includes a vast array of utility templating functions from [sprig](http://masterminds.github.io/sprig/) apart from the default Golang [text/template](https://pkg.go.dev/text/template#hdr-Functions) to allow users to customize the output format.

Lastly, Syft has custom templating functions defined in `./syft/format/template/encoder.go` to help parse the passed-in JSON structs.

{{% alert title="Note" color="primary" %}}
If you have templates being used before Syft v0.102.0 that are no longer working. This is because templating keys were relative to the internal go structs before this version whereas now the keys are relative to the Syft JSON output. To get the legacy behavior back you can set the `format.template.legacy` option to `true` in your configuration.
{{% /alert %}}