```xml
<?xml version="1.0" encoding="UTF-8"?>
<bom xmlns="http://cyclonedx.org/schema/bom/1.6" serialNumber="urn:uuid:2fcb8236-e891-40b4-9e98-84ed1c776664" version="1">
  <metadata>
    <timestamp>2025-10-02T01:46:44Z</timestamp>
    <tools>
      <components>
        <component type="application">
          <author>anchore</author>
          <name>syft</name>
          <version>1.33.0</version>
        </component>
      </components>
    </tools>
    <component bom-ref="84d86520b9546322" type="container">
      <name>busybox</name>
      <version>sha256:cddc8af5547af9de5e6fb66b36d66ef7418561204e1255ae528d0b2c919d09a3</version>
    </component>
  </metadata>
  <components>
    <component bom-ref="pkg:generic/busybox@1.37.0?package-id=74d9294c42941b37" type="application">
      <name>busybox</name>
      <version>1.37.0</version>
      <cpe>cpe:2.3:a:busybox:busybox:1.37.0:*:*:*:*:*:*:*</cpe>
      <purl>pkg:generic/busybox@1.37.0</purl>
      <properties>
        <property name="syft:package:foundBy">binary-classifier-cataloger</property>
        <property name="syft:package:type">binary</property>
        <property name="syft:package:metadataType">binary-signature</property>
        <property name="syft:location:0:layerID">sha256:6aba5e0d32d91e3e923854dcb30588dc4112bfa1dae82b89535ad31d322a7b19</property>
        <property name="syft:location:0:path">/bin/[</property>
      </properties>
    </component>
    <component bom-ref="os:busybox@1.37.0" type="operating-system">
      <name>busybox</name>
      <version>1.37.0</version>
      <description>BusyBox v1.37.0</description>
      <swid tagId="busybox" name="busybox" version="1.37.0"></swid>
      <properties>
        <property name="syft:distro:extendedSupport">false</property>
        <property name="syft:distro:id">busybox</property>
        <property name="syft:distro:idLike:0">busybox</property>
        <property name="syft:distro:prettyName">BusyBox v1.37.0</property>
        <property name="syft:distro:versionID">1.37.0</property>
      </properties>
    </component>
  </components>
</bom>
```
