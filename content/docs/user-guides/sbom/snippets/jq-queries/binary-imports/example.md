```bash
syft alpine:3.9.2 -o json | \
  jq '.files[] |
  select(.executable != null and .executable.importedLibraries != null) |
  select(.executable.importedLibraries[] | contains("libcrypto")) |
  {
    path: .location.path,
    imports: .executable.importedLibraries
  }'
```
