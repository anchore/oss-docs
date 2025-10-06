```go-text-template
"Package","Version","Type","Found by"
{{- range .artifacts}}
"{{.name}}","{{.version}}","{{.type}}","{{.foundBy}}"
{{- end}}

```
