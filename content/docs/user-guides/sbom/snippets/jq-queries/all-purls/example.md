```bash
syft alpine:3.9.2 -o json | \
  jq '.artifacts[] |
  select(.purl != null and .purl != "") |
  {
    name,
    version,
    purl
  }'
```
