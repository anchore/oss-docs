```python
.files[] |
  select(.executable != null and .executable.importedLibraries != null) |
  select(.executable.importedLibraries[] | contains("libcrypto")) |  # Find binaries using libcrypto
  {
    path: .location.path,
    imports: .executable.importedLibraries  # Shared library dependencies
  }

```
