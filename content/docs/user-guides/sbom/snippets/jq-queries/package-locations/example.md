```bash
syft alpine:3.9.2 -o json | \
  jq '.artifacts[] |
  {
    name,
    version,
    type,
    locations: [.locations[] | .path]
  }'
```
