+++
title = "Types of Licenses"
description = "Understand the different categories of software licenses, from permissive to copyleft, and their implications for your projects."
weight = 20
tags = ["grant", "licenses"]
+++

Understanding software license types is essential for managing legal risk and ensuring compliance. This guide covers the main categories of licenses you encounter when scanning software with Grant.

## Why licenses matter

By default, creative works, including code, are protected by exclusive copyright. The author has sole control over use, copying, distribution, and modification. Open source licenses explicitly grant permissions that the legal default would otherwise restrict.

Making a repository public is **not** the same as licensing it. Without an explicit license, contributors retain full copyright to their contributions, potentially preventing even the project maintainer from using that code.

## Permissive licenses

Permissive licenses have minimal restrictions on how you can modify or redistribute software. They typically only require you to retain copyright notices and attribution.

**Examples:** MIT, Apache-2.0, BSD-2-Clause, BSD-3-Clause, ISC

**Obligations:**

- Retain copyright information when distributing
- Include the license text with distributions
- Some (like Apache-2.0) include explicit patent grants

**Risk level in Grant:** Low

Permissive licenses are popular for projects seeking wide adoption. They allow relicensing to other licenses and integration into proprietary software.

## Weak copyleft licenses

Weak copyleft licenses balance permissive and restrictive terms. They allow linking to open source libraries with limited obligations, making them practical for library code.

**Examples:** LGPL-2.1-only, LGPL-3.0-only, MPL-2.0, EPL-2.0, CDDL-1.0

**Obligations:**

- Dynamic linking typically permits proprietary distribution with minimal requirements
- Static linking and modifications to the library itself require source disclosure
- Changes to the licensed component must be shared under the same license

**Risk level in Grant:** Medium

These licenses are common for libraries where the authors want modifications shared back while still allowing proprietary applications to use the library.

## Strong copyleft licenses

Strong copyleft (also called "reciprocal" or "restrictive") licenses require that derivative works are distributed under the same license. Any modifications or software that incorporates the code must have its source code made available.

**Examples:** GPL-2.0-only, GPL-3.0-only, AGPL-3.0-only

**Obligations:**

- Distribute source code with any distribution of the software
- Derivative works must use the same (or compatible) license
- AGPL extends these requirements to software accessed over a network

**Risk level in Grant:** High

Organizations often flag these licenses for review because they can require disclosure of proprietary source code if not properly isolated.

## Commercial and proprietary licenses

Commercial or proprietary licenses assert specific conditions on usage rights. They typically prohibit sharing, reverse-engineering, modification, redistribution, or resale without explicit permission.

**Risk level in Grant:** These may appear as "Unknown" if not in the SPDX license list.

## Dual licenses

Some software is offered under multiple licenses simultaneously. This approach often combines an open source license with a commercial option.

**Common patterns:**

- AGPL for open source use, commercial license for proprietary integration
- Weak copyleft for community, proprietary for enterprise features

Dual licensing enables developer adoption while requiring commercial licenses for certain commercial uses.

## Public domain and unlicensed code

**Public domain:** Software explicitly released without copyright restrictions. Examples include CC0-1.0 and Unlicense. These have minimal obligations but definitions vary by jurisdiction.

**Unlicensed:** Code without any explicit license is **not** public domain. Using it typically violates copyright law because no permissions have been granted. Grant flags these packages so you can investigate.

## EU regulatory context

Recent EU legislation (AI Act, Cyber Resilience Act, Product Liability Directive, Interoperable Europe Act) defines compliant open source software as having:

- Source code openly shared and accessible
- Rights to freely use, modify, and redistribute
- Licensing that ensures these rights remain available

The European Union Public Licence (EUPL) version 1.2 is recognized as a standard compliant open-source license.

## How Grant categorizes risk

Grant assigns risk levels based on the strength of copyleft requirements:

| Risk Level | License Type | Implication |
|------------|--------------|-------------|
| **High** | Strong copyleft | May require source code disclosure |
| **Medium** | Weak copyleft | Limited obligations, typically for modifications |
| **Low** | Permissive | Minimal restrictions, attribution required |

Use `grant list --group-by risk` to organize scan results by risk level.

## Choosing licenses for your projects

Consider these factors when selecting a license:

- **Dependencies:** Ensure compatibility with licenses of included libraries
- **Community norms:** MIT dominates npm; Apache-2.0 appeals to enterprises
- **Contributor preferences:** GPL/AGPL appeal to those opposing closed-source derivatives
- **Company policies:** Verify corporate IP agreements and licensing requirements

## Next steps

{{< alert title="Continue the guide" color="success" url="/docs/guides/license/grant-policies/" >}}
**Next**: Learn how to [configure license policies]({{< relref "grant-policies" >}}) to enforce compliance in your organization.
{{< /alert >}}

- [Getting Started]({{< relref "getting-started" >}}) - Scan for licenses with Grant
- [Configuration Reference]({{< relref "/docs/reference/grant/configuration" >}}) - Full Grant configuration options
