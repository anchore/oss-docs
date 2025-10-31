+++
title = "Sign-off Commits"
description = "How to sign-off commits with the Developer's Certificate of Origin"
weight = 30
type = "docs"
menu_group = "general"
+++

## Sign off your work

All commits require a simple sign-off line to confirm you have the right to contribute your code.
This is a standard practice in open source called the Developer Certificate of Origin (DCO).

### How to sign off

The easiest way is to use the `-s` or `--signoff` flag when committing:

```bash
git commit -s -m "your commit message"
```

This automatically adds a sign-off line to your commit message:

```text
Signed-off-by: Your Name <your.email@example.com>
```

**Tip:** You can configure Git to always sign off commits automatically:

```bash
git config --global format.signoff true
```

### Verify your sign-off

To check that your commit includes the sign-off, look at the log output:

```bash
git log -1
```

You should see the `Signed-off-by:` line at the end of your commit message:

```text
commit 37ceh170e4hb283bb73d958f2036ee5k07e7fde7
Author: Your Name <your.email@example.com>
Date:   Mon Aug 1 11:27:13 2020 -0400

    your commit message

    Signed-off-by: Your Name <your.email@example.com>
```

### Why we require sign-off

**In plain English:** By adding a sign-off line, you're confirming that:

- You wrote the code yourself, OR
- You have permission to submit it, AND
- You're okay with it being released under the project's open source license

This protects both you and the project. It's a simple legal formality that takes just a few seconds to add to each commit.

All contributions to this project are licensed under the [Apache License Version 2.0](http://www.apache.org/licenses/).

### Adding sign-off to existing commits

If you've already committed without a sign-off (easy to do!), you can add it retroactively.

#### For your most recent commit

```bash
git commit --amend --signoff
```

This updates your last commit to include the sign-off line.

#### For older commits

If you need to add sign-off to commits further back in your history:

```bash
git rebase --signoff HEAD~N
```

Replace `N` with the number of commits you need to sign. For example, `HEAD~3` signs off the last 3 commits.

**Note:** If you've already pushed these commits, you'll need to force-push after rebasing:

```bash
git push --force-with-lease
```

#### If you're new to rebasing

Rebasing rewrites commit history, which can be tricky if you're not familiar with it. If you run into issues:

1. Ask for help in the PR comments
2. Or, create a fresh branch from the latest main and cherry-pick your changes
3. The maintainers can also help you fix sign-off issues during the review process

### What the DCO means (technical details)

The Developer Certificate of Origin (DCO) is a legal attestation that you have the right to submit your contribution under the project's license.
Here's the full text:

```text
Developer's Certificate of Origin 1.1

By making a contribution to this project, I certify that:

   (a) The contribution was created in whole or in part by me and I
       have the right to submit it under the open source license
       indicated in the file; or

   (b) The contribution is based upon previous work that, to the best
       of my knowledge, is covered under an appropriate open source
       license and I have the right under that license to submit that
       work with modifications, whether created in whole or in part
       by me, under the same open source license (unless I am
       permitted to submit under a different license), as indicated
       in the file; or

   (c) The contribution was provided directly to me by some other
       person who certified (a), (b) or (c) and I have not modified
       it.

   (d) I understand and agree that this project and the contribution
       are public and that a record of the contribution (including all
       personal information I submit with it, including my sign-off) is
       maintained indefinitely and may be redistributed consistent with
       this project or the open source license(s) involved.
```

The DCO protects both contributors and the project by creating a clear record of contribution rights and licensing terms.
