```bash
syft alpine:3.9.2 -o json | \
  jq '[.files[] |
  {
    path: .location.path,
    size: .metadata.size,
    mimeType: .metadata.mimeType
  }] |
  sort_by(.size) |
  reverse |
  .[0:10]'
```
