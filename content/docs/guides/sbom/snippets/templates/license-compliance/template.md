```go-text-template
{{range .artifacts}}
{{- if .licenses}}
{{.name}}: {{range .licenses}}{{.value}} {{end}}{{end}}
{{- end}}

```
