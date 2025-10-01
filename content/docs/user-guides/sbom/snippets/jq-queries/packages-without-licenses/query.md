```python
.artifacts[] |
  select(.licenses == null or (.licenses | length) == 0) |  # Packages without license info
  {
    name,
    version,
    type,
    locations: [.locations[].path]  # Where package is installed
  }

```
