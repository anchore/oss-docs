+++
title = "Distribution Support Reference"
description = "Complete list of Linux distributions supported by Grype for vulnerability scanning"
weight = 10
type = "docs"
+++

This reference lists all Linux distributions that Grype recognizes and scans for vulnerabilities.

## All supported distributions

<div class="table-responsive">
  <table class="table table-bordered">
    <thead class="thead-light">
      <tr>
        <th>Distribution</th>
        <th>Support Level</th>
        <th>Data Source</th>
        <th>Comprehensive Feed</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td>AlmaLinux</td>
        <td>Direct</td>
        <td>alma</td>
        <td>No</td>
      </tr>
      <tr>
        <td>Alpine</td>
        <td>Direct</td>
        <td>alpine</td>
        <td>No</td>
      </tr>
      <tr>
        <td>Amazon Linux</td>
        <td>Direct</td>
        <td>amazon</td>
        <td>No</td>
      </tr>
      <tr>
        <td>Arch Linux</td>
        <td>CPE fallback</td>
        <td>nvd</td>
        <td>No</td>
      </tr>
      <tr>
        <td>Azure Linux</td>
        <td>Direct</td>
        <td>mariner</td>
        <td>Yes</td>
      </tr>
      <tr>
        <td>Busybox</td>
        <td>CPE fallback</td>
        <td>nvd</td>
        <td>No</td>
      </tr>
      <tr>
        <td>CentOS</td>
        <td>Via rhel</td>
        <td>rhel</td>
        <td>No</td>
      </tr>
      <tr>
        <td>Chainguard</td>
        <td>Direct</td>
        <td>chainguard</td>
        <td>No</td>
      </tr>
      <tr>
        <td>Debian</td>
        <td>Direct</td>
        <td>debian</td>
        <td>Yes</td>
      </tr>
      <tr>
        <td>Echo</td>
        <td>Direct</td>
        <td>echo</td>
        <td>No</td>
      </tr>
      <tr>
        <td>Fedora</td>
        <td>CPE fallback</td>
        <td>nvd</td>
        <td>No</td>
      </tr>
      <tr>
        <td>Gentoo</td>
        <td>CPE fallback</td>
        <td>nvd</td>
        <td>No</td>
      </tr>
      <tr>
        <td>Mariner</td>
        <td>Direct</td>
        <td>mariner</td>
        <td>Yes</td>
      </tr>
      <tr>
        <td>MinimOS</td>
        <td>Direct</td>
        <td>minimos</td>
        <td>No</td>
      </tr>
      <tr>
        <td>OpenSUSE Leap</td>
        <td>CPE fallback</td>
        <td>nvd</td>
        <td>No</td>
      </tr>
      <tr>
        <td>Oracle Linux</td>
        <td>Direct</td>
        <td>oracle</td>
        <td>No</td>
      </tr>
      <tr>
        <td>Photon OS</td>
        <td>CPE fallback</td>
        <td>nvd</td>
        <td>No</td>
      </tr>
      <tr>
        <td>Raspbian</td>
        <td>Via debian</td>
        <td>debian</td>
        <td>No</td>
      </tr>
      <tr>
        <td>Red Hat Enterprise Linux</td>
        <td>Direct</td>
        <td>rhel</td>
        <td>Yes</td>
      </tr>
      <tr>
        <td>Rocky Linux</td>
        <td>Direct</td>
        <td>rocky</td>
        <td>No</td>
      </tr>
      <tr>
        <td>SLES</td>
        <td>Direct</td>
        <td>sles</td>
        <td>No</td>
      </tr>
      <tr>
        <td>Ubuntu</td>
        <td>Direct</td>
        <td>ubuntu</td>
        <td>Yes</td>
      </tr>
      <tr>
        <td>Windows</td>
        <td>Direct</td>
        <td>MSRC</td>
        <td>No</td>
      </tr>
      <tr>
        <td>Wolfi</td>
        <td>Direct</td>
        <td>wolfi</td>
        <td>No</td>
      </tr>
    </tbody>
  </table>
</div>

## Support level definitions

**Direct support** - Grype has a dedicated vulnerability data feed from Vunnel for these distributions. This provides the most accurate and comprehensive vulnerability detection.

**ID-like support** - Grype recognizes these distributions and uses vulnerability data from a compatible distribution through the `ID_LIKE` field in `/etc/os-release`.

**CPE fallback** - Grype recognizes these distributions but lacks a dedicated vulnerability feed. It uses CPE-based matching against the National Vulnerability Database (NVD) to detect vulnerabilities.

## Comprehensive feeds

Distributions marked "Yes" in the Comprehensive Feed column provide both fixed and unfixed vulnerability data. These distributions are:

- Azure Linux
- Debian
- Mariner
- Red Hat Enterprise Linux
- Ubuntu

For comprehensive distributions, Grype deduplicates vulnerabilities more aggressively by excluding non-OS packages (binaries, language packages) when they are owned by OS packages via file overlap.

## Notes

**Azure Linux / Mariner:** Azure Linux is the current product name for Microsoft's Linux distribution. Mariner (CBL-Mariner) was the original name. Both refer to the same distribution and use the same vulnerability data.
