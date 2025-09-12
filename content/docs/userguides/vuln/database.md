+++
title = "Vulnerability Database"
description = "Using the Grype Vulnerability Database"
weight = 20
tags = ["grype", "vulnerabilities", "grype-db"]
url = "docs/userguides/vuln/database"
+++

### Introduction

Grype uses a locally cached database of known vulnerabilities when searching a container, directory, or SBOM for security vulnerabilities. Anchore collates vulnerability data from commomn feeds, and publishes that data online, at no cost to users.

{{% alert title="Learn more" color="primary" %}}
Find out more about the vulnerability feeds at [Vulnerability Feeds](/docs/userguides/feeds/).
{{% /alert %}}

### Updating the local database

When Grype is launched, it checks for an existing vulnerability database, and looks for an updated one online. If available, Grype will automatically download the new database.

Users can manage the locally cached database with the `grype db` command:

#### Check and update the database

Manually checking for updates shouldn't be necessary, due to Grype automatically doing this on launch. However, it is possible to force Grype to look for an updated vulnerability database.

```
grype db check
```

A message will indicate if no updates are available since the last download.

```text
Installed DB version v6.0.2 was built on 2025-05-08T04:08:40Z
No update available
```

If the database is outdated, a message such as this will be displayed.

```text
Installed DB version v6.0.2 was built on 2025-05-07T04:08:13Z
Updated DB version v6.0.2 was built on 2025-05-08T04:08:40Z
You can run 'grype db update' to update to the latest db
[0000] ERROR db upgrade available
```

```
grype db update
```

A short animation will show progress of downloading, uncompressing and hydrating (creating indexes on) the database. Then a message reporting the successful update will be displayed.

```text
grype db update
 ✔ Vulnerability DB                [updated]
Vulnerability database updated to latest version!
```

{{% alert title="Next steps" color="primary" %}}
* Learn how the vuln DB is [created](/docs/userguides/database/sources/) and [published](/docs/userguides/database/published/).
* Learn about [SBOM Generation](/docs/userguides/sbom/getstarted/) and [License Scaanning](/docs/userguides/license/getstarted/) your SBOMs.
{{% /alert %}}
