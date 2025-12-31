```json
{
  "path": "/lib/libssl.so.1.1",
  "imports": [
    "libcrypto.so.1.1",
    "libc.musl-x86_64.so.1"
  ]
}
{
  "path": "/sbin/apk",
  "imports": [
    "libssl.so.1.1",
    "libcrypto.so.1.1",
    "libz.so.1",
    "libc.musl-x86_64.so.1"
  ]
}
{
  "path": "/usr/lib/engines-1.1/afalg.so",
  "imports": [
    "libcrypto.so.1.1",
    "libc.musl-x86_64.so.1"
  ]
}
{
  "path": "/usr/lib/libtls-standalone.so.1.0.0",
  "imports": [
    "libssl.so.1.1",
    "libcrypto.so.1.1",
    "libc.musl-x86_64.so.1"
  ]
}
```
