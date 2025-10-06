```python
.artifacts[] |
  select(.name | test("^(openssl|ssl|crypto)")) |  # Regex pattern match on package name
  {
    name,
    version,
    type  # Package type (apk, deb, rpm, etc.)
  }

```
