```bash
syft alpine:3.9.2 -o json | \
  jq '.artifacts[] |
  select(.cpes != null and (.cpes | length) > 0) |
  {
    name,
    version,
    cpes: [.cpes[].cpe]
  }'
```
