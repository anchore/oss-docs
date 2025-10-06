```bash
syft alpine:3.9.2 -o json | \
  jq '.artifacts[] |
  select(.name | test("^(openssl|ssl|crypto)")) |
  {
    name,
    version,
    type
  }'
```
