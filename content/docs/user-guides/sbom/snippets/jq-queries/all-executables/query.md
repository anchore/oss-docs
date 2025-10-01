```python
.files[] |
  select(.executable != null) |  # Filter for executable files
  {
    path: .location.path,
    format: .executable.format,  # ELF, Mach-O, PE, etc.
    importedLibraries: .executable.importedLibraries  # Shared library dependencies
  }

```
