```python
.artifacts[] |
  select(.cpes != null and (.cpes | length) > 0) |  # Filter packages with CPEs
  {
    name,
    version,
    cpes: [.cpes[].cpe]  # Extract CPE strings
  }

```
