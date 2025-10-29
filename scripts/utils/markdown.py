"""Markdown generation utilities for documentation scripts."""

from typing import Any


def create_code_fence(content: str, language: str = "") -> str:
    """
    Create markdown code fence with optional language specifier.

    Args:
        content: Code/text content to wrap in code fence
        language: Language for syntax highlighting (empty string for plain text)

    Returns:
        Formatted markdown code fence with content

    Examples:
        >>> create_code_fence("print('hello')", "python")
        "```python\\nprint('hello')\\n```\\n"

        >>> create_code_fence("plain text")
        "```\\nplain text\\n```\\n"
    """
    fence_start = f"```{language}" if language else "```"
    return f"{fence_start}\n{content}\n```\n"


def generate_front_matter(
    title: str,
    link_title: str | None = None,
    weight: int | None = None,
    tags: list[str] | None = None,
    categories: list[str] | None = None,
    url: str | None = None,
    description: str | None = None,
    aliases: list[str] | None = None,
    params: dict[str, Any] | None = None,
) -> str:
    """
    Generate Hugo front matter in TOML format.

    Args:
        title: Page title
        link_title: Sidebar link title (defaults to title)
        weight: Menu ordering weight
        tags: List of tags
        categories: List of categories
        url: Custom URL path
        description: Page description for SEO
        aliases: List of URL aliases
        params: Additional parameters dict

    Returns:
        Formatted TOML front matter with +++ delimiters

    Example:
        >>> generate_front_matter(
        ...     title="Syft CLI",
        ...     link_title="Syft CLI",
        ...     weight=10,
        ...     tags=["syft"],
        ...     categories=["reference"],
        ...     url="docs/reference/syft/cli"
        ... )
        '+++\\ntitle = "Syft CLI"\\nlinkTitle = "Syft CLI"\\nweight = 10\\ntags = [\\'syft\\']\\ncategories = [\\'reference\\']\\nurl = "docs/reference/syft/cli"\\n+++\\n\\n'
    """
    lines = ["+++"]

    # required field
    lines.append(f'title = "{title}"')

    # optional fields
    if link_title is not None:
        lines.append(f'linkTitle = "{link_title}"')

    if weight is not None:
        lines.append(f"weight = {weight}")

    if tags is not None:
        tags_str = ", ".join(f"'{tag}'" for tag in tags)
        lines.append(f"tags = [{tags_str}]")

    if categories is not None:
        categories_str = ", ".join(f"'{cat}'" for cat in categories)
        lines.append(f"categories = [{categories_str}]")

    if url is not None:
        lines.append(f'url = "{url}"')

    if description is not None:
        lines.append(f'description = "{description}"')

    if aliases is not None:
        aliases_str = ", ".join(f'"{alias}"' for alias in aliases)
        lines.append(f"aliases = [{aliases_str}]")

    if params is not None:
        for key, value in params.items():
            if isinstance(value, str):
                lines.append(f'{key} = "{value}"')
            elif isinstance(value, bool):
                lines.append(f"{key} = {str(value).lower()}")
            elif isinstance(value, (int, float)):
                lines.append(f"{key} = {value}")
            else:
                # for complex types, convert to string
                lines.append(f'{key} = "{value}"')

    lines.append("+++")
    lines.append("")  # blank line after front matter

    return "\n".join(lines) + "\n"


def detect_format(content: str) -> str:
    """
    Detect output format for syntax highlighting.

    Analyzes content to determine the best syntax highlighting language identifier.

    Args:
        content: Output content to analyze

    Returns:
        Format string: "json", "csv", "text", "yaml", "xml", etc.

    Examples:
        >>> markdown.detect_format('{"foo": "bar"}')
        'json'

        >>> markdown.detect_format('name,value\\nfoo,bar')
        'csv'

        >>> markdown.detect_format('plain text output')
        'text'

        >>> markdown.detect_format('(no results)')
        'text'
    """
    # handle empty or special cases
    if not content or content == "(no results)":
        return "text"

    # try to detect JSON (starts with { or [)
    # note: we can't parse it since it might be truncated
    if content.startswith("{") or content.startswith("["):
        return "json"

    # check if it looks like CSV (multiple lines with commas)
    lines = content.split("\n")
    if len(lines) > 1 and all("," in line for line in lines[:3] if line.strip()):
        return "csv"

    # check for YAML indicators
    if ":" in content and any(
        line.strip().startswith("-") for line in lines if line.strip()
    ):
        return "yaml"

    # check for XML
    if content.strip().startswith("<?xml") or content.strip().startswith("<"):
        return "xml"

    # default to plain text
    return "text"
