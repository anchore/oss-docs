+++
tags = ['syft']
title = "Syft"
description = "Installing Syft"
weight = 10
url = "docs/installation/syft"
+++

## Official builds

The Anchore OSS team publish official source archives and binary builds of Syft for Linux, macOS and Windows. There are also numerous community-maintained builds of the tools for different platforms.

### Installer script

Syft binaries are provided for Linux, macOS and Windows.

```
curl -sSfL https://get.anchore.io/syft | sudo sh -s -- -b /usr/local/bin
```

Install script options:

- `-b`: Specify a custom installation directory (defaults to ./bin)
- `-d`: More verbose logging levels (-d for debug, -dd for trace)
- `-v`: Verify the signature of the downloaded artifact before installation (requires [cosign](https://github.com/sigstore/cosign) to be installed)

### Updating Syft

Syft checks for new versions on launch. It will print a message at the end of the output if the version in use is not the latest.

```
A newer version of syft is available for download: 1.20.0 (installed version is 1.19.2)
```

### Docker container

```
docker pull anchore/syft
```

### GitHub releases

- Download the file for your operating system and architecture from the [GitHub releases page](https://github.com/anchore/syft/releases)
- In the case of `.deb` or `.rpm`, install them using your package manager
- For compressed archives, unpack the file, and copy the `syft` binary to a folder in your path such as `/usr/local/bin`

## Community builds of syft

### Alpine Linux

```
apk add syft
```

- [Alpine Linux Syft Page](https://pkgs.alpinelinux.org/packages?name=syft)
- [Alpine Linux packaging for Syft](https://git.alpinelinux.org/aports/tree/community/syft)

Thanks to [Michał Polański](https://pkgs.alpinelinux.org/packages?name=&branch=edge&repo=&arch=&maintainer=Micha%C5%82%20Pola%C5%84ski) for maintaining this package.

### Chocolatey

```
choco install syft -y
```

### Homebrew

```
brew tap anchore/syft
brew install syft
```

- [HomeBrew packaging for Syft](https://github.com/anchore/homebrew-syft)

Thanks to the [Syft community](https://github.com/anchore/homebrew-syft/graphs/contributors) for maintaining this package.

### Kali Linux

```
sudo apt install syft
```

- [Kali Linux Syft page](https://www.kali.org/tools/syft/)
- [Kali Linux packaging for Syft](https://gitlab.com/kalilinux/packages/syft)

Thanks to [Sophie Brun](https://gitlab.com/sophiebrun) for maintaining this package.

### Nix

Syft is available in the [stable channel](https://search.nixos.org/packages?channel=25.05&show=syft&query=syft) since NixOS 22.05.

```
nix-env -i syft
```

Alternatively, just try it out in an ephemeral nix shell.

```
nix-shell -p syft
```

### Scoop

```
scoop install syft
```

### WinGet

```
nuget install Anchore.syft
```

- [WinGet packaging for Syft](https://github.com/microsoft/winget-pkgs/tree/master/manifests/a/Anchore/Syft)

Thanks to [Alan Pope](https://github.com/popey) for maintaining this package.

### Snapcraft

```
snap install syft
```

- [Snapcraft Syft page](https://snapcraft.io/syft)
- [Snapcraft packaging for Syft](https://github.com/popey/syft-snap)

Thanks to [Alan Pope](https://github.com/popey) for maintaining this package.
