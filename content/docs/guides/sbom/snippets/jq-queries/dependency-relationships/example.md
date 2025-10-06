```bash
syft node:18-alpine -o json | \
  jq '. as $root |
  .artifactRelationships[] |
  select(.type == "dependency-of") |
  .parent as $parent |
  .child as $child |
  {
    parent: ($root.artifacts[] | select(.id == $parent).name),
    child: ($root.artifacts[] | select(.id == $child).name)
  }'
```
