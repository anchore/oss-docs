```bash
syft node:18-alpine -o json | \
  jq '[.artifacts[]] |
  group_by(.type) |
  map({
    type: .[0].type,
    count: length
  }) |
  sort_by(.count) |
  reverse'
```
