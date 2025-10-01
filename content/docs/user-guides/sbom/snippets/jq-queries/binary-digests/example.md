```bash
syft alpine:3.9.2 -o json | \
  jq '.files[] |
  select(.executable != null) |
  {
    path: .location.path,
    digests: [.digests[] | {algorithm, value}]
  }'
```
