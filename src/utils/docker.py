#!/usr/bin/env python3
"""
Utility functions for running Docker containers.

Provides common functionality for scripts that need to run commands
inside Docker containers.
"""

import subprocess

from .config import timeouts


def run_docker_command(
    image: str,
    cmd_parts: list[str],
    timeout: int = timeouts.docker_command,
) -> tuple[str, str, int]:
    """
    run a command inside a Docker container.

    Args:
        image: Docker image to use (e.g., "anchore/syft:latest")
        cmd_parts: command and arguments to run inside the container
        timeout: command timeout in seconds (default: from config)

    Returns:
        Tuple of (stdout, stderr, returncode)

    Examples:
        >>> stdout, stderr, code = run_docker_command("anchore/syft:latest", ["version"])
        >>> if code == 0:
        ...     print(f"Version: {stdout}")
    """
    docker_cmd = ["docker", "run", "--rm", image] + cmd_parts

    try:
        result = subprocess.run(
            docker_cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return result.stdout, result.stderr, result.returncode

    except subprocess.TimeoutExpired:
        return "", "Command timed out", 1
    except Exception as e:
        return "", str(e), 1
