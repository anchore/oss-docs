```bash
syft alpine:3.9.2 -o json | \
  jq '. as $root |
  [.files[].id] as $allFiles |
  [.artifactRelationships[] | select(.type == "contains") | .child] as $ownedFiles |
  ($allFiles - $ownedFiles) as $orphans |
  $root.files[] |
  select(.id as $id | $orphans | index($id)) |
  .location.path'
```
