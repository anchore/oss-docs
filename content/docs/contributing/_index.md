+++ 
title = "Contributing" 
tags = ["syft", "grype", "grant", "grype-db", "vunnel", "stereoscope"]
description = "Guidelines for developing & contributing to Anchore Open Source projects" 
weight = 20 
url = "docs/contributing"
+++

## Anchore OSS Contribution Guidelines

Each tool has their own slightly different guide, linked below. However, some of the guidelines are common across all tools, and are shown in the next section, [General Guidelines](#general-guidelines).

## Tool-Specific Guides

### User facing tools

* [Syft](/docs/contributing/syft) - SBOM generation tool and library
* [Grype](/docs/contributing/grype) - Vulnerability scanner
* [Grant](/docs/contributing/grant) - License search

### Automation tools

* [SBOM-Action](/docs/contributing/sbom-action) - SBOM generating GitHub Action
* [Scan-Action](/docs/contributing/scan-action) - Vulnerability scanning GitHub Action

### Backend tools & libraries

* [Grype-DB](/docs/contributing/grype-db) - Vulnerability database creation
* [Vunnel](/docs/contributing/vunnel) - Collect vulnerability data from sources
* [Stereoscope](/docs/contributing/stereoscope) - Container image processing library

## General Guidelines

This document is the single source of truth for how to contribute to the code base. We'd love to accept your patches and contributions to this project. There are just a few small guidelines you need to follow.

### Sign off your work

The `sign-off` is an added line at the end of the explanation for the commit, certifying that you wrote it or otherwise have the right to submit it as an open-source patch. By submitting a contribution, you agree to be bound by the terms of the DCO Version 1.1 and Apache License Version 2.0.

Signing off a commit certifies the below Developer's Certificate of Origin (DCO):

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

All contributions to this project are licensed under the [Apache License Version 2.0, January 2004](http://www.apache.org/licenses/).

When committing your change, you can add the required line manually so that it looks like this:

```text
Signed-off-by: John Doe <john.doe@example.com>
```

Creating a signed-off commit is then possible with `-s` or `--signoff`:

```text
$ git commit -s -m "this is a commit message"
```

To double-check that the commit was signed-off, look at the log output:

```text
$ git log -1
commit 37ceh170e4hb283bb73d958f2036ee5k07e7fde7 (HEAD -> issue-35, origin/main, main)
Author: John Doe <john.doe@example.com>
Date:   Mon Aug 1 11:27:13 2020 -0400

    this is a commit message

    Signed-off-by: John Doe <john.doe@example.com>
```


### Test your changes

This project has a `Makefile` which includes many helpers running both unit and integration tests. You can run `make help` to see all the options. Although PRs will have automatic checks for these, it is useful to run them locally, ensuring they pass before submitting changes. Ensure you've bootstrapped once before running tests:

```text
$ make bootstrap
```

You only need to bootstrap once. After the bootstrap process, you can run the tests as many times as needed:

```text
$ make unit
$ make integration
```

You can also run `make all` to run a more extensive test suite, but there is additional configuration that will be needed for those tests to run correctly. We will not cover the extra steps here.

### Pull Request

If you made it this far and all the tests are passing, it's time to submit a Pull Request (PR) for the project. Submitting a PR is always a scary moment as what happens next can be an unknown. The projects strive to be easy to work with, we appreciate all contributions. Nobody is going to yell at you or try to make you feel bad. We love contributions and know how scary that first PR can be.

#### PR Title and Description

Just like the commit title and description mentioned above, the PR title and description is very important for letting others know what's happening. Please include any details you think a reviewer will need to more properly review your PR.

A PR that is very large or poorly described has a higher likelihood of being pushed to the end of the list. Reviewers like PRs they can understand and quickly review.

#### What to expect next

Please be patient with the project. We try to review PRs in a timely manner, but this is highly dependent on all the other tasks we have going on. It's OK to ask for a status update every week or two, it's not OK to ask for a status update every day.

It's very likely the reviewer will have questions and suggestions for changes to your PR. If your changes don't match the current style and flow of the other code, expect a request to change what you've done.

### Document your changes

And lastly, when proposed changes are modifying user-facing functionality or output, it is expected the PR will include updates to the documentation as well. Our projects are not heavy on documentation. This will mostly be updating the README and help for the tool.

If nobody knows new features exist, they can't use them!