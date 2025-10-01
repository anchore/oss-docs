```bash
syft httpd:2.4.65 -o json | \
  jq '.artifacts[] |
  select(.licenses == null or (.licenses | length) == 0) |
  {
    name,
    version,
    type,
    locations: [.locations[].path]
  }'
```
