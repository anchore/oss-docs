```python
.artifacts[] |
  select(.type == "java-archive") |  # Filter for JAR packages
  {
    package: "\(.name)@\(.version)",
    path: (.locations[] | select(.annotations.evidence == "primary") | .path)  # Primary installation path
  }

```
