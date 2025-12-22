"""Utility functions for git operations."""

import subprocess
from logging import Logger
from pathlib import Path


def ensure_repo_synced(
    repo_url: str,
    clone_dir: Path,
    ref: str = "main",
    sparse_paths: list[str] | None = None,
    logger: Logger | None = None,
) -> None:
    """
    ensure a git repo is cloned and synced to the specified ref.

    If clone_dir doesn't exist, performs sparse clone.
    If it exists, fetches and checks out the ref.

    Args:
        repo_url: URL of the git repository
        clone_dir: local directory to clone into
        ref: git ref to checkout (branch, tag, or commit)
        sparse_paths: optional list of paths for sparse checkout
        logger: optional logger for status messages
    """
    clone_dir = clone_dir.resolve()

    if not clone_dir.exists():
        # clone with sparse checkout
        if logger:
            logger.info(f"Cloning {repo_url} to {clone_dir} (ref: {ref})")

        clone_dir.parent.mkdir(parents=True, exist_ok=True)

        # clone with minimal data
        _run_git(
            [
                "clone",
                "--filter=blob:none",
                "--no-checkout",
                "--depth=1",
                "--single-branch",
                "-b",
                ref,
                repo_url,
                str(clone_dir),
            ],
            logger=logger,
        )

        # set up sparse checkout if paths specified
        if sparse_paths:
            _run_git(
                ["-C", str(clone_dir), "sparse-checkout", "set", "--no-cone"]
                + sparse_paths,
                logger=logger,
            )

        _run_git(["-C", str(clone_dir), "checkout"], logger=logger)
    else:
        # sync existing clone
        if logger:
            logger.info(f"Syncing {clone_dir} to ref: {ref}")

        _run_git(
            ["-C", str(clone_dir), "fetch", "--depth=1", "origin", ref], logger=logger
        )
        _run_git(["-C", str(clone_dir), "checkout", "FETCH_HEAD"], logger=logger)


def _run_git(args: list[str], logger: Logger | None = None) -> None:
    """Run a git command, raising on failure."""
    cmd = ["git"] + args
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    if result.returncode != 0:
        raise RuntimeError(
            f"Git command failed: {' '.join(cmd)}\nstderr: {result.stderr}"
        )
    if logger:
        logger.debug(f"git {' '.join(args)}")
