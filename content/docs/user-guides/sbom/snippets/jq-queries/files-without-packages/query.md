```python
. as $root |
  [.files[].id] as $allFiles |  # All file IDs
  [.artifactRelationships[] | select(.type == "contains") | .child] as $ownedFiles |  # Package-owned files
  ($allFiles - $ownedFiles) as $orphans |  # Set subtraction for unowned files
  $root.files[] |
  select(.id as $id | $orphans | index($id)) |  # Filter to orphaned files
  .location.path

```
