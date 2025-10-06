```python
[.artifacts[] | select(.language != null and .language != "")] |
  group_by(.language) |  # Group by programming language
  map({
    language: .[0].language,
    count: length  # Count packages per language
  }) |
  sort_by(.count) |
  reverse  # Highest count first

```
