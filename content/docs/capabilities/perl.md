+++
title = "Perl"
description = "Perl package analysis and vulnerability scanning capabilities"
weight = 215
type = "docs"
menu_group = "language"
+++

## Package analysis

{{< readfile file="/content/docs/capabilities/snippets/ecosystem/perl/package.md" >}}

Perl packages are cataloged as CPAN **distributions**, not as modules.
A distribution is the unit that CPAN, MetaCPAN, and CPAN's advisory data all use, so you see `libwww-perl` rather than `LWP`, and `URI` rather than `URI::Escape`.

Every cataloged package has type `cpan` and a purl of the form `pkg:cpan/<distribution>@<version>`.
When the evidence carries the PAUSE author id it is added as an `author` qualifier, for example `pkg:cpan/URI@5.35?author=OALDERS`.

### What is and is not cataloged

Only distribution-level **identity** is emitted, and three kinds of evidence are read to produce it:

- `install.json` under a `.meta` directory, written by `cpanm`, `cpm`, and `carton`
- `.packlist`, paired with `perllocal.pod` for the version, falling back to scraping `$VERSION` from the main `.pm` when `perllocal.pod` is absent
- an unpacked release's own `META.json` or `META.yml`, alongside a sibling `MANIFEST`

Module-level evidence is read where it exists (`install.json` records a `provides` map with per-module versions), but it is used to resolve dependency edges rather than reported as packages of its own.
Both meta file names are read because roughly 43% of current CPAN releases ship no `META.json` at all.
The sibling `MANIFEST` is what gates the unpacked-release case: a built release tarball ships one, a source checkout does not, and without that check every project with a committed meta file would be reported as an installed distribution.

The coverage boundary follows from that:

- **CPAN client installs are cataloged**, wherever they live, including local-lib trees such as an application's `local/lib/perl5`. `cpanm`, `cpm`, and `carton` write `install.json` only when the distribution was resolved from a mirror, so a local directory or tarball install (`cpanm .`, `cpanm ./Foo-1.0.tar.gz`) writes none, and `CPAN.pm` never writes one. Those installs are picked up by the packlist pass instead. This is why the official `perl:5.40-slim` image has no `.meta` directories at all and every Perl package reported from it comes from a packlist.
- **A `.packlist` is written by the `ExtUtils::MakeMaker` and `Module::Build` install targets**, unless it is suppressed with `NO_PACKLIST`, which is what distro packagers set.
- **A packlist-derived name is the installer's `NAME`**, which is usually but not always the distribution name. `libwww-perl` installs to `auto/LWP/.packlist`, so that is the name you see. Resolving those to distributions is left to the vulnerability data, which carries the mapping.
- **Perl modules installed from distro packages are not cataloged here.** They carry no CPAN-native metadata, because packagers suppress it, and they are already reported by the deb, rpm, and apk catalogers. Reporting them twice would be worse than not reporting them here. So `libwww-perl` from apt stays a `deb` package, `perl-URI` from dnf stays an `rpm` package, and `perl-uri` from apk stays an `apk` package.
- **Core and dual-life distributions bundled with the interpreter are not cataloged.** Nothing on disk carries their versions, so there is nothing to read. This is a real gap: 26 of the distributions that carry advisories are dual-life in perl 5.40, including `Encode`, `Storable`, `HTTP-Tiny`, and `Archive-Tar`. The interpreter itself is reported separately and advisories against the `perl` distribution do get matched, so the gap is the distributions bundled inside it rather than perl itself. Installing a newer copy of one from CPAN makes that copy visible.
- **Build leftovers under `~/.cpanm/work` and `~/.cpan/build` are skipped.** They are unpacked release tarballs, `MANIFEST` included, but they describe a copy that is already installed elsewhere on the same image.
- **Vendored `.pm` trees, App::FatPacker output, and PAR archives are invisible.** What they carry is module identity, and there is no offline map from a module to the distribution that shipped it. Fatpacked output does embed the `.pm` sources verbatim, `$VERSION` lines included, so the missing fact is the distribution rather than the version.
- **A `cpanfile` or `cpanfile.snapshot` is not parsed yet.** A snapshot is a resolved lockfile, and in a source checkout or CI workspace, where `local/` does not exist, it is the only evidence there is. This is deferred rather than out of scope.

### The perl interpreter

The perl interpreter binary is reported as `pkg:cpan/perl@<version>`, not `pkg:generic/perl@<version>`.
`perl` is itself a CPAN distribution and carries advisories under that name, so typing it as `cpan` is what makes those advisories reachable.

{{< alert color="primary" title="Note" >}}
This changes an existing purl. Allowlists, policies, and SBOM comparisons keyed on `pkg:generic/perl` need to be updated to `pkg:cpan/perl`.
{{< /alert >}}

## Vulnerability scanning

{{< readfile file="/content/docs/capabilities/snippets/ecosystem/perl/vulnerability.md" >}}

{{< readfile file="/content/docs/capabilities/snippets/ecosystem/perl/grype-app-config.md" >}}

### Version comparison

Perl versions are compared using perl's own `version.pm` semantics rather than semver, because the two disagree on the most common version shape on CPAN.
Under perl's rules a decimal version is a fraction, so `1.2` is greater than `1.10`, and `1.23` is greater than `1.2.3`.
Perl also treats a packed decimal and a dotted version as equal, so `5.008001` and `5.8.1` are the same version.

### Advisory coverage

Perl advisory data comes from CPANSA, the CPAN Security Advisory database.
CPANSA is keyed on **distribution** names, which is the same key Syft reports, so `libwww-perl` is the name that carries advisories and `LWP` is not.

{{< alert color="primary" title="No findings is not the same as no vulnerabilities" >}}
CPANSA coverage is thin and uneven. It carries advisories for 409 distributions out of roughly 42,000 on CPAN, and four Lemonldap-NG distributions alone account for about a third of its 2,035 advisories.
A clean report for a Perl image usually means the distributions you installed are not covered by any advisory data, not that they are known to be safe.
{{< /alert >}}

## Next steps

- [Syft package analysis]({{< ref "docs/guides/sbom/getting-started" >}})
- [Grype vulnerability scanning]({{< ref "docs/guides/vulnerability/getting-started" >}})
- [CPAN Security Advisory database](https://github.com/briandfoy/cpan-security-advisory)
- [MetaCPAN](https://metacpan.org/)
