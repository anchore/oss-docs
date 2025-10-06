```bash
syft alpine:3.9.2 -o json | \
  jq '.files[] |
  select(.metadata.mimeType == "application/x-sharedlib") |
  {
    path: .location.path,
    mimeType: .metadata.mimeType,
    size: .metadata.size
  }'
```
