```bash
syft openjdk:11.0.11-jre-slim -o json | \
  jq '.artifacts[] |
  select(.type == "java-archive") |
  {
    package: "\(.name)@\(.version)",
    path: (.locations[] | select(.annotations.evidence == "primary") | .path)
  }'
```
