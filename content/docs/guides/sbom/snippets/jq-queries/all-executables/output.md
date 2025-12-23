```json
{
  "path": "/bin/busybox",
  "format": "elf",
  "importedLibraries": [
    "libc.musl-x86_64.so.1"
  ]
}
{
  "path": "/lib/ld-musl-x86_64.so.1",
  "format": "elf",
  "importedLibraries": []
}
{
  "path": "/lib/libcrypto.so.1.1",
  "format": "elf",
  "importedLibraries": [
    "libc.musl-x86_64.so.1"
  ]
}
{
  "path": "/lib/libssl.so.1.1",
  "format": "elf",
  "importedLibraries": [
    "libcrypto.so.1.1",
    "libc.musl-x86_64.so.1"
  ]
}
{
  "path": "/lib/libz.so.1.2.11",
  "format": "elf",
  "importedLibraries": [
    "libc.musl-x86_64.so.1"
  ]
}
{
  "path": "/sbin/apk",
  "format": "elf",
  "importedLibraries": [
    "libssl.so.1.1",
    "libcrypto.so.1.1",
    "libz.so.1",
    "libc.musl-x86_64.so.1"
  ]
}
{
  "path": "/sbin/mkmntdirs",
  "format": "elf",
  "importedLibraries": [
    "libc.musl-x86_64.so.1"
  ]
}
{
  "path": "/usr/bin/getconf",
  "format": "elf",
  "importedLibraries": [
    "libc.musl-x86_64.so.1"
  ]
}
{
  "path": "/usr/bin/getent",
  "format": "elf",
  "importedLibraries": [
    "libc.musl-x86_64.so.1"
  ]
}
{
  "path": "/usr/bin/iconv",
  "format": "elf",
  "importedLibraries": [
    "libc.musl-x86_64.so.1"
  ]
}
{
  "path": "/usr/bin/scanelf",
  "format": "elf",
  "importedLibraries": [
    "libc.musl-x86_64.so.1"
  ]
}
{
  "path": "/usr/bin/ssl_client",
  "format": "elf",
  "importedLibraries": [
    "libtls-standalone.so.1",
    "libc.musl-x86_64.so.1"
  ]
}
{
  "path": "/usr/lib/engines-1.1/afalg.so",
  "format": "elf",
  "importedLibraries": [
    "libcrypto.so.1.1",
    "libc.musl-x86_64.so.1"
  ]
}
{
  "path": "/usr/lib/engines-1.1/capi.so",
  "format": "elf",
  "importedLibraries": [
    "libc.musl-x86_64.so.1"
  ]
}
{
  "path": "/usr/lib/engines-1.1/padlock.so",
  "format": "elf",
  "importedLibraries": [
    "libc.musl-x86_64.so.1"
  ]
}
{
  "path": "/usr/lib/libtls-standalone.so.1.0.0",
  "format": "elf",
  "importedLibraries": [
    "libssl.so.1.1",
    "libcrypto.so.1.1",
    "libc.musl-x86_64.so.1"
  ]
}
```
