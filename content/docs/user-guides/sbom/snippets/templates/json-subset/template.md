```go-text-template
{
  "scanned": "{{.source.metadata.userInput}}",
  "packages": [
    {{- $last := sub (len .artifacts) 1}}
    {{- range $i, $pkg := .artifacts}}
    {"name": "{{$pkg.name}}", "version": "{{$pkg.version}}"}{{if ne $i $last}},{{end}}
    {{- end}}
  ]
}

```
