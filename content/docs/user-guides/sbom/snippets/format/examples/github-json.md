```json
{
  "version": 0,
  "job": {},
  "detector": {
    "name": "syft",
    "url": "https://github.com/anchore/syft",
    "version": "1.33.0"
  },
  "metadata": {
    "syft:distro": "pkg:generic/busybox@1.37.0?like=busybox"
  },
  "manifests": {
    "busybox:latest:/bin/busybox": {
      "name": "busybox:latest:/bin/busybox",
      "file": {
        "source_location": "busybox:latest:/bin/busybox"
      },
      "metadata": {
        "syft:filesystem": "sha256:6aba5e0d32d91e3e923854dcb30588dc4112bfa1dae82b89535ad31d322a7b19"
      },
      "resolved": {
        "pkg:generic/busybox@1.37.0": {
          "package_url": "pkg:generic/busybox@1.37.0",
          "relationship": "direct",
          "scope": "runtime"
        }
      }
    }
  },
  "scanned": "2025-10-02T20:50:39Z"
}
```
