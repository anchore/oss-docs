```bash
syft alpine:3.9.2 -o json | \
  jq '.files[] |
  select(.executable != null) |
  {
    path: .location.path,
    format: .executable.format,
    importedLibraries: .executable.importedLibraries
  }'
```
