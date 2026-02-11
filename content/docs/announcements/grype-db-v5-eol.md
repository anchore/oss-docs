+++
title = "Grype DB v5 schema EOL"
description = "Users running Grype versions older than v0.88.0 will stop receiving vulnerability database updates on March 6, 2026."
date = 2026-01-08
weight = 10
tags = ["grype", "grype-db", "eol", "announcement"]
banner = "Grype DB v5 schema reaches EOL on March 6, 2026"
+++

On **March 6, 2026**, Grype will stop publishing vulnerability database updates for **DB schema v5**. After this date, older Grype versions that depend on schema v5 will no longer receive new vulnerability data.

## Who is affected

You are affected if you are running **Grype older than v0.88.0**. These versions use DB schema v5 and will stop getting database updates after the EOL date.

To check your version, run:

```shell
grype version
```

If the output shows a version lower than `v0.88.0`, you need to upgrade.

## What to do

Upgrade to **Grype v0.88.0 or later**, which uses DB schema v6. This is the only action required.

You can upgrade using the install script:

```shell
curl -sSfL https://get.anchore.io/grype | sudo sh -s -- -b /usr/local/bin
```

Or see the [Grype installation page](/docs/installation/grype/) for other installation methods.

## Why this is happening

Maintaining multiple database schemas in parallel has significant operational overhead. Retiring schema v5 allows the team to focus on improving the current schema and delivering better vulnerability data.

## Questions or issues

If you run into problems or have questions, reach out through:

- [Anchore Community Discourse](https://anchorecommunity.discourse.group/)
- [Grype GitHub Issues](https://github.com/anchore/grype/issues)
