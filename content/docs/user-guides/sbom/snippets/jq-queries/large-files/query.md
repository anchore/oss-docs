```python
[.files[] |
  {
    path: .location.path,
    size: .metadata.size,
    mimeType: .metadata.mimeType
  }] |
  sort_by(.size) |
  reverse |  # Largest first
  .[0:10]  # Top 10 files

```
