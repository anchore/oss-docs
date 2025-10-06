```python
.artifacts[] |
  select(.cpes != null and (.cpes | length) > 0) |  # Packages with CPE identifiers
  {
    name,
    version,
    type,
    cpeCount: (.cpes | length)  # Number of CPE matches
  }

```
