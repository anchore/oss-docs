```python
.artifacts[] |
  select(.purl != null and .purl != "") |  # Filter packages with PURLs
  {
    name,
    version,
    purl  # Package URL for cross-tool compatibility
  }

```
