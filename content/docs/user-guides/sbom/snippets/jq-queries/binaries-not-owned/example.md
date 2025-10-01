```bash
syft httpd:2.4.65 -o json | \
  jq '. as $root |
  [.files[] | select(.executable != null) | .id] as $binaries |
  [.artifactRelationships[] | select(.type == "contains") | .child] as $owned |
  ($binaries - $owned) as $unowned |
  $root.files[] |
  select(.id as $id | $unowned | index($id)) |
  {
    path: .location.path,
    sha256: .digests[] | select(.algorithm == "sha256") | .value
  }'
```
