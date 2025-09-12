+++
tags = ['grype']
title = "Grype"
description = "Installing Grype"
weight = 20
url = "docs/installation/grype"
+++

## Official builds

The Anchore OSS team publish official source archives and binary builds of Grype for Linux, macOS and Windows. There are also numerous community-maintained builds of the tools for different platforms.

### Installer script

Grype binaries are provided for Linux, macOS and Windows.

```
curl -sSfL https://get.anchore.io/grype | sudo sh -s -- -b /usr/local/bin
```

Install script options:

- `-b`: Specify a custom installation directory (defaults to ./bin)
- `-d`: More verbose logging levels (-d for debug, -dd for trace)
- `-v`: Verify the signature of the downloaded artifact before installation (requires [cosign](https://github.com/sigstore/cosign) to be installed)

### Updating Grype

Grype checks for new versions on launch. It will print a message at the end of the output if the version in use is not the latest.

```
A newer version of grype is available for download: 0.92.0 (installed version is 0.91.2)
```


### Docker container

```
docker pull anchore/grype
```

### GitHub releases

- Download the file for your operating system and architecture from the [GitHub releases page](https://github.com/anchore/grype/releases)
- In the case of `.deb` or `.rpm`, install them using your package manager
- For compressed archives, unpack the file, and copy the `grype` binary to a folder in your path such as `/usr/local/bin`

## Community builds of Grype

### Arch Linux

```
sudo pacman -S grype-bin
```

### Homebrew

```
brew tap anchore/grype
brew install grype
```

### MacPorts

```
sudo port install grype
```

### NuGet

```powershell
nuget install Anchore.Grype
```

### Snapcraft

```
snap install grype
```

