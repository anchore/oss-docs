+++
tags = ['grant']
title = "Grant"
description = "Installing Grant"
weight = 30
url = "docs/installation/grant"
+++

## Official builds

The Anchore OSS team publish official source archives and binary builds for Linux and macOS. There are also some community-maintained builds of the tools for different platforms.

### Installer script

Grant binaries are provided for Linux and macOS.

```
curl -sSfL https://get.anchore.io/grant | sudo sh -s -- -b /usr/local/bin
```

Install script options:

- `-b`: Specify a custom installation directory (defaults to ./bin)
- `-d`: More verbose logging levels (-d for debug, -dd for trace)
- `-v`: Verify the signature of the downloaded artifact before installation (requires [cosign](https://github.com/sigstore/cosign) to be installed)

### GitHub releases

- Download the file for your operating system and architecture from the [GitHub releases page](https://github.com/anchore/grant/releases)
- In the case of `.deb` or `.rpm`, install them using your package manager
- For compressed archives, unpack the file, and copy the `grant` binary to a folder in your path such as `/usr/local/bin`

## Community builds of grant

### Homebrew

```
brew tap anchore/grant
brew install grant
```
