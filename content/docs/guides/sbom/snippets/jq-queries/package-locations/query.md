```python
.artifacts[] |
  {
    name,
    version,
    type,
    locations: [.locations[] | .path]  # All filesystem locations
  }

```
