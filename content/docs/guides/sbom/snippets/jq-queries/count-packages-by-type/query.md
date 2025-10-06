```python
[.artifacts[]] |
  group_by(.type) |  # Group packages by ecosystem type
  map({
    type: .[0].type,
    count: length  # Count packages in each group
  }) |
  sort_by(.count) |
  reverse  # Highest count first

```
