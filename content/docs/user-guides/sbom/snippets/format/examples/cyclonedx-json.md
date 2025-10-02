```json
{
  "$schema": "http://cyclonedx.org/schema/bom-1.6.schema.json",
  "bomFormat": "CycloneDX",
  "specVersion": "1.6",
  "serialNumber": "urn:uuid:aa85cdf7-b49c-4931-9b6a-765984584584",
  "version": 1,
  "metadata": {
    "timestamp": "2025-10-02T01:46:42Z",
    "tools": {
      "components": [
        {
          "type": "application",
          "author": "anchore",
          "name": "syft",
          "version": "1.33.0"
        }
      ]
    },
    "component": {
      "bom-ref": "84d86520b9546322",
      "type": "container",
      "name": "busybox",
      "version": "sha256:cddc8af5547af9de5e6fb66b36d66ef7418561204e1255ae528d0b2c919d09a3"
    }
  },
  "components": [
    {
      "bom-ref": "pkg:generic/busybox@1.37.0?package-id=74d9294c42941b37",
      "type": "application",
      "name": "busybox",
      "version": "1.37.0",
      "cpe": "cpe:2.3:a:busybox:busybox:1.37.0:*:*:*:*:*:*:*",
      "purl": "pkg:generic/busybox@1.37.0",
      "properties": [
        {
          "name": "syft:package:foundBy",
          "value": "binary-classifier-cataloger"
        },
        {
          "name": "syft:package:type",
          "value": "binary"
        },
        {
          "name": "syft:package:metadataType",
          "value": "binary-signature"
        },
        {
          "name": "syft:location:0:layerID",
          "value": "sha256:6aba5e0d32d91e3e923854dcb30588dc4112bfa1dae82b89535ad31d322a7b19"
        },
        {
          "name": "syft:location:0:path",
          "value": "/bin/["
        }
      ]
    },
    {
      "bom-ref": "os:busybox@1.37.0",
      "type": "operating-system",
      "name": "busybox",
      "version": "1.37.0",
      "description": "BusyBox v1.37.0",
      "swid": {
        "tagId": "busybox",
        "name": "busybox",
        "version": "1.37.0"
      },
      "properties": [
        {
          "name": "syft:distro:extendedSupport",
          "value": "false"
        },
        {
          "name": "syft:distro:id",
          "value": "busybox"
        },
        {
          "name": "syft:distro:idLike:0",
          "value": "busybox"
        },
        {
          "name": "syft:distro:prettyName",
          "value": "BusyBox v1.37.0"
        },
        {
          "name": "syft:distro:versionID",
          "value": "1.37.0"
        }
      ]
    }
  ]
}
```
