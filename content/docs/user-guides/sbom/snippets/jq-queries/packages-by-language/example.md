```bash
syft node:18-alpine -o json | \
  jq '[.artifacts[] | select(.language != null and .language != "")] |
  group_by(.language) |
  map({
    language: .[0].language,
    count: length
  }) |
  sort_by(.count) |
  reverse'
```
