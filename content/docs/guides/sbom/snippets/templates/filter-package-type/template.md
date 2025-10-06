```go-text-template
{{range .artifacts}}
{{- if eq .type "apk"}}
{{.name}}@{{.version}}{{end}}
{{- end}}

```
