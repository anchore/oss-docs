```bash
syft alpine:3.9.2 -o json | \
  jq '.files[] |
  select(.executable != null and .executable.format == "elf") |
  {
    path: .location.path,
    pie: .executable.elfSecurityFeatures.pie,
    stackCanary: .executable.elfSecurityFeatures.stackCanary,
    nx: .executable.elfSecurityFeatures.nx
  }'
```
