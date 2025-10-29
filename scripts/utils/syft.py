#!/usr/bin/env python3
"""
Utility functions for running Syft in Docker containers.

Provides common functionality for scripts that need to run Syft,
including template execution, format generation, and config-based scanning.
"""

import subprocess
from pathlib import Path

from .config import docker_images, timeouts


def run(
    syft_image: str = docker_images.syft,
    args: list[str] | None = None,
    timeout: int = timeouts.syft_scan_default,
    env_vars: dict[str, str] | None = None,
    volumes: dict[str, str] | None = None,
) -> tuple[str, str, int]:
    """
    run Syft command in a Docker container with flexible configuration.

    This is the base function that can run any Syft command (scan, version, config, etc).

    Args:
        syft_image: Syft Docker image to use (default: from config)
        args: command line arguments to pass to Syft (e.g., ["alpine:3.9.2", "-o", "json"])
        timeout: command timeout in seconds (default: from config)
        env_vars: environment variables to pass to container
        volumes: volume mounts as {host_path: container_path}

    Returns:
        Tuple of (stdout, stderr, returncode)

    Raises:
        subprocess.TimeoutExpired: if command times out

    Examples:
        >>> # Scan an image
        >>> stdout, stderr, code = syft.run(args=["alpine:3.9.2", "-o", "json"])
        >>>
        >>> # Get version
        >>> stdout, stderr, code = syft.run(args=["version"])
        >>>
        >>> # Get config
        >>> stdout, stderr, code = syft.run(args=["config"])
    """
    docker_cmd = ["docker", "run", "--rm"]

    # add environment variables
    if env_vars:
        for key, value in env_vars.items():
            docker_cmd.extend(["-e", f"{key}={value}"])

    # add volume mounts
    if volumes:
        for host_path, container_path in volumes.items():
            docker_cmd.extend(["-v", f"{host_path}:{container_path}"])

    # add syft image
    docker_cmd.append(syft_image)

    # add syft arguments
    if args:
        docker_cmd.extend(args)

    try:
        result = subprocess.run(
            docker_cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
        )

        return result.stdout, result.stderr, result.returncode

    except subprocess.TimeoutExpired:
        raise


def scan(
    target_image: str,
    syft_image: str = docker_images.syft,
    output_format: str = "syft-json",
    timeout: int = timeouts.syft_scan_default,
    env_vars: dict[str, str] | None = None,
    volumes: dict[str, str] | None = None,
    extra_args: list[str] | None = None,
) -> str:
    """
    run Syft to scan an image with flexible configuration.

    Args:
        target_image: container image to scan (e.g., "alpine:3.9.2")
        syft_image: Syft Docker image to use (default: from config)
        output_format: output format (default: "syft-json")
        timeout: command timeout in seconds (default: from config)
        env_vars: environment variables to pass to container
        volumes: volume mounts as {host_path: container_path}
        extra_args: additional arguments to pass to Syft

    Returns:
        Syft stdout output as string

    Raises:
        RuntimeError: if Syft command fails or times out
    """
    args = [target_image, "-o", output_format]

    # add any extra arguments
    if extra_args:
        args.extend(extra_args)

    try:
        stdout, stderr, returncode = run(
            syft_image=syft_image,
            args=args,
            timeout=timeout,
            env_vars=env_vars,
            volumes=volumes,
        )

        if returncode != 0:
            raise RuntimeError(f"Syft command failed: {stderr or stdout}")

        return stdout.strip()

    except subprocess.TimeoutExpired as e:
        raise RuntimeError(f"Syft command timed out after {timeout} seconds") from e
    except Exception as e:
        raise RuntimeError(f"Failed to run Syft: {e}") from e


def scan_with_template(
    template_file: Path,
    target_image: str,
    syft_image: str = docker_images.syft,
    timeout: int = timeouts.syft_scan_default,
) -> str:
    """
    run Syft with a custom template file.

    Args:
        template_file: path to template file on host
        target_image: container image to scan
        syft_image: Syft Docker image to use (default: from config)
        timeout: command timeout in seconds (default: from config)

    Returns:
        Syft template output as string

    Raises:
        RuntimeError: if Syft command fails or times out
    """
    # get absolute path for the template file
    template_path = template_file.resolve()

    # mount the template file as read-only
    volumes = {f"{template_path}": "/template.tmpl:ro"}

    # use template output format with path to mounted template
    extra_args = ["-t", "/template.tmpl"]

    return scan(
        target_image=target_image,
        syft_image=syft_image,
        output_format="template",
        timeout=timeout,
        volumes=volumes,
        extra_args=extra_args,
    )


def scan_with_config(
    target_image: str,
    config_file: Path,
    syft_image: str = docker_images.syft,
    output_format: str = "syft-json",
    timeout: int = timeouts.syft_scan_with_config,
) -> str:
    """
    run Syft with a custom configuration file.

    Args:
        target_image: container image to scan
        config_file: path to Syft config file on host
        syft_image: Syft Docker image to use (default: from config)
        output_format: output format (default: "syft-json")
        timeout: command timeout in seconds (default: from config)

    Returns:
        Syft output as string

    Raises:
        RuntimeError: if Syft command fails or times out
        ValueError: if config file doesn't exist
    """
    # get absolute path and validate existence
    config_path = config_file.resolve()
    if not config_path.exists():
        raise ValueError(f"Config file not found: {config_path}")

    # mount config file as read-only
    volumes = {f"{config_path}": "/config.yaml:ro"}

    # specify config file path
    extra_args = ["-c", "/config.yaml"]

    return scan(
        target_image=target_image,
        syft_image=syft_image,
        output_format=output_format,
        timeout=timeout,
        volumes=volumes,
        extra_args=extra_args,
    )


def convert(
    sbom_file: Path,
    template_file: Path,
    syft_image: str = docker_images.syft,
    timeout: int = timeouts.syft_scan_default,
) -> str:
    """
    run Syft convert to apply a template to an existing SBOM.

    Args:
        sbom_file: path to SBOM file on host (syft-json format)
        template_file: path to template file on host
        syft_image: Syft Docker image to use (default: from config)
        timeout: command timeout in seconds (default: from config)

    Returns:
        Syft template output as string

    Raises:
        RuntimeError: if Syft command fails or times out
        ValueError: if sbom_file or template_file doesn't exist
    """
    # get absolute paths and validate existence
    sbom_path = sbom_file.resolve()
    template_path = template_file.resolve()

    if not sbom_path.exists():
        raise ValueError(f"SBOM file not found: {sbom_path}")
    if not template_path.exists():
        raise ValueError(f"Template file not found: {template_path}")

    # mount both files as read-only
    volumes = {
        f"{sbom_path}": "/sbom.json:ro",
        f"{template_path}": "/template.tmpl:ro",
    }

    # use convert command with template output format
    args = ["convert", "/sbom.json", "-o", "template", "-t", "/template.tmpl"]

    try:
        stdout, stderr, returncode = run(
            syft_image=syft_image,
            args=args,
            timeout=timeout,
            volumes=volumes,
        )

        if returncode != 0:
            raise RuntimeError(f"Syft convert command failed: {stderr or stdout}")

        return stdout.strip()

    except subprocess.TimeoutExpired as e:
        raise RuntimeError(
            f"Syft convert command timed out after {timeout} seconds"
        ) from e
    except Exception as e:
        raise RuntimeError(f"Failed to run Syft convert: {e}") from e


def convert_format(
    sbom_file: Path,
    output_format: str,
    syft_image: str = docker_images.syft,
    timeout: int = timeouts.syft_scan_default,
    env_vars: dict[str, str] | None = None,
) -> str:
    """
    run Syft convert to convert an SBOM to a different output format.

    Args:
        sbom_file: path to SBOM file on host (syft-json format)
        output_format: output format (e.g., "json", "cyclonedx-json", "spdx-json")
        syft_image: Syft Docker image to use (default: from config)
        timeout: command timeout in seconds (default: from config)
        env_vars: environment variables to pass to container (e.g., {"SYFT_FORMAT_PRETTY": "true"})

    Returns:
        Syft output as string in the requested format

    Raises:
        RuntimeError: if Syft command fails or times out
        ValueError: if sbom_file doesn't exist
    """
    # get absolute path and validate existence
    sbom_path = sbom_file.resolve()

    if not sbom_path.exists():
        raise ValueError(f"SBOM file not found: {sbom_path}")

    # mount SBOM file as read-only
    volumes = {f"{sbom_path}": "/sbom.json:ro"}

    # use convert command with specified output format
    args = ["convert", "/sbom.json", "-o", output_format]

    try:
        stdout, stderr, returncode = run(
            syft_image=syft_image,
            args=args,
            timeout=timeout,
            env_vars=env_vars,
            volumes=volumes,
        )

        if returncode != 0:
            raise RuntimeError(f"Syft convert command failed: {stderr or stdout}")

        return stdout.strip()

    except subprocess.TimeoutExpired as e:
        raise RuntimeError(
            f"Syft convert command timed out after {timeout} seconds"
        ) from e
    except Exception as e:
        raise RuntimeError(f"Failed to run Syft convert: {e}") from e


def scan_with_format(
    target_image: str,
    syft_image: str = docker_images.syft,
    output_format: str = "json",
    timeout: int = timeouts.syft_scan_default,
    pretty: bool = True,
    file_metadata_selection: str = "none",
) -> str:
    """
    run Syft with specific output format and common environment variables.

    Args:
        target_image: container image to scan
        syft_image: Syft Docker image to use (default: from config)
        output_format: output format (default: "json")
        timeout: command timeout in seconds (default: from config)
        pretty: enable pretty printing (default: True)
        file_metadata_selection: file metadata selection mode (default: "none")

    Returns:
        Syft output as string

    Raises:
        RuntimeError: if Syft command fails or times out
    """
    env_vars = {}

    if pretty:
        env_vars["SYFT_FORMAT_PRETTY"] = "true"

    if file_metadata_selection:
        env_vars["SYFT_FILE_METADATA_SELECTION"] = file_metadata_selection

    return scan(
        target_image=target_image,
        syft_image=syft_image,
        output_format=output_format,
        timeout=timeout,
        env_vars=env_vars,
    )
