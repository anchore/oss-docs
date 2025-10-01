+++
title = "Configuration Reference"
description = "Configuration patterns and options used across all Anchore OSS tools"
weight = 100
tags = ["syft", "grype", "grant"]
url = "docs/reference/configuration"
+++

All Anchore open source tools (Syft, Grype, Grant) share the same configuration system. This guide explains how to configure these tools using command-line flags, environment variables, and configuration files.

## Configuration precedence

When you configure a tool, settings are applied in a specific order. If the same setting is specified in multiple places, the tool uses the value from the highest-priority source:

1. **Command-line arguments** _(highest priority)_
2. **Environment variables**
3. **Configuration file**
4. **Default values** _(lowest priority)_

For example, if you set the log level using all three methods, the command-line flag overrides the environment variable, which overrides the config file value.

{{% alert title="Tip" %}}
Running a tool with `--verbose` or `-vv` log level prints the entire active configuration at startup, showing you exactly which values are being used.
{{% /alert %}}

## Viewing your configuration

To see available configuration options and current settings:

- `syft --help` — shows all command-line flags
- `syft config` — prints a complete sample configuration file
- `syft config --load` — displays your current active configuration

Replace `syft` with the tool you're using (`grype`, `grant`, etc.).

## Using environment variables

Every configuration option can be set via environment variable. The variable name follows the path to the setting in the configuration file.

**Example:** To enable pretty-printed JSON output, the config file setting is:

```yaml
format:
  json:
    pretty: true
```

The path from root to this value is `format` → `json` → `pretty`, so the environment variable is:

```bash
export SYFT_FORMAT_JSON_PRETTY=true
```

The pattern is: `<TOOL>_<PATH>_<TO>_<SETTING>` where:

- `<TOOL>` is the uppercase tool name (`SYFT`, `GRYPE`, `GRANT`)
- Path segments are joined with underscores
- All letters are uppercase

**More examples:**

```bash
# Set log level to debug
export SYFT_LOG_LEVEL=debug

# Configure output format
export GRYPE_OUTPUT=json

# Set registry credentials
export SYFT_REGISTRY_AUTH_USERNAME=myuser
```

## Using a configuration file

Configuration files use YAML format. The tool searches these locations in order and uses the first file it finds:

1. `.syft.yaml` (in current directory)
2. `.syft/config.yaml` (in current directory)
3. `~/.syft.yaml` (in home directory)
4. `<XDG_CONFIG_HOME>/syft/config.yaml` (typically `~/.config/syft/config.yaml`)

Replace `syft` with your tool name (`grype`, `grant`, etc.).

{{% alert title="Note" %}}
Only the first config file found is used — configuration files are not merged together.
{{% /alert %}}
