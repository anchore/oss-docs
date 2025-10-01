```python
.files[] |
  select(.executable != null) |  # Filter for executable files
  {
    path: .location.path,
    digests: [.digests[] | {algorithm, value}]  # All available hash algorithms
  }

```
