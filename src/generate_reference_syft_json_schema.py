#!/usr/bin/env python3
"""
Generate JSON schema reference documentation from Syft schema files.

This script parses Syft's JSON schema and generates comprehensive HTML tables
documenting all type definitions, organized into Core Types and Ecosystem Types.

Outputs:
- Reference docs: content/docs/reference/syft/json/{VERSION}.md
  - Core Types section: Document, Package, Location, etc.
  - Ecosystem Types section: AlpmDbEntry, ApkDbEntry, etc.
  - Each type gets a table with: Field Name, Type, Required?, Description

CATEGORIZATION STRATEGY:

The script uses compute_type_categories() as the single chokepoint for all type
categorization decisions. This function can be swapped from heuristic-based to
data-driven categorization without affecting the rest of the script.

Current implementation: heuristic-based (see _categorize_using_heuristics())
  - Examines Package.metadata.anyOf to identify ecosystem types
  - Uses reference patterns to infer core vs. ecosystem-specific types
  - Applies manual heuristics for edge cases

Future implementation: data-driven (NOT YET IMPLEMENTED)
  - Will use golang package metadata from cataloger data
  - Expected data source: data/capabilities/syft-package-catalogers.json
  - Will need to be extended with golang package names for each type
  - See compute_type_categories() docstring for detailed integration plan
"""

import json
import re
import sys
from logging import Logger
from pathlib import Path
from typing import Any

import click

from utils import config, log
from utils.constants import CSSClasses


@click.command()
@click.option(
    "--syft-ref",
    type=str,
    default="main",
    help="Git ref (branch/tag/commit) for Syft repository",
)
@click.option(
    "--update",
    is_flag=True,
    help="Update documentation even if output files already exist",
)
@click.option(
    "-v",
    "--verbose",
    count=True,
    help="Increase verbosity (use -v for info, -vv for debug)",
)
def main(syft_ref: str, update: bool, verbose: int) -> None:
    """Generate JSON schema reference documentation from Syft schema files.

    Processes all schema files in the Syft repository, selecting the latest
    patch version for each major version >= {config.min_schema_major_version}.
    """
    logger = log.setup(verbose, __file__)

    from utils import git

    # ensure syft repo is cloned/synced
    git.ensure_repo_synced(
        repo_url=config.SYFT_REPO_URL,
        clone_dir=config.paths.syft_cache_dir,
        ref=syft_ref,
        sparse_paths=["schema/json"],
        logger=logger,
    )

    schema_dir = config.paths.syft_schema_dir

    # scan directory for schema files
    all_schemas = scan_schema_directory(schema_dir, logger)

    # select schemas to process (latest patch per major version >= min)
    selected = select_schemas_to_process(
        all_schemas, config.min_schema_major_version, logger
    )

    if not selected:
        logger.error("No schemas selected for processing")
        sys.exit(1)

    # determine highest major version for "latest" badge
    highest_major = max(selected.keys())
    logger.info(
        f"Highest major version: v{highest_major} (will receive 'latest' badge)"
    )

    # process each selected schema
    for major, (schema_path, full_version) in sorted(selected.items(), reverse=True):
        output_file = config.paths.json_reference_dir / f"{major}.md"

        # check if output already exists
        if output_file.exists() and not update:
            logger.info(
                f"Output file already exists: {output_file} "
                f"(use --update to regenerate)"
            )
            continue

        # load schema
        schema_data = load_json_schema(schema_path, major, logger)

        # determine if this is the latest version
        is_latest = major == highest_major

        # generate documentation
        generate_schema_documentation(
            schema_data,
            full_version,
            config.paths.json_reference_dir,
            is_latest,
            logger,
        )

    logger.info("Generation complete!")


def parse_schema_filename(filename: str) -> tuple[int, int, int] | None:
    """
    parse schema filename to extract version numbers.

    Args:
        filename: filename like "schema-16.10.0.json"

    Returns:
        tuple of (major, minor, patch) or None if invalid

    Examples:
        >>> parse_schema_filename("schema-16.10.0.json")
        (16, 10, 0)
        >>> parse_schema_filename("schema-latest.json")
        None
        >>> parse_schema_filename("README.md")
        None
    """
    # match pattern: schema-X.Y.Z.json
    match = re.match(r"^schema-(\d+)\.(\d+)\.(\d+)\.json$", filename)
    if not match:
        return None

    try:
        major = int(match.group(1))
        minor = int(match.group(2))
        patch = int(match.group(3))
        return (major, minor, patch)
    except ValueError:
        return None


def scan_schema_directory(
    dir_path: Path, logger: Logger
) -> list[tuple[Path, tuple[int, int, int]]]:
    """
    scan directory for schema files and extract versions.

    Args:
        dir_path: directory containing schema files
        logger: logger instance

    Returns:
        list of (file_path, version_tuple) pairs for valid schemas
    """
    if not dir_path.exists():
        logger.error(f"Schema directory not found: {dir_path}")
        sys.exit(1)

    if not dir_path.is_dir():
        logger.error(f"Path is not a directory: {dir_path}")
        sys.exit(1)

    schemas = []
    for file_path in dir_path.glob("schema-*.json"):
        version = parse_schema_filename(file_path.name)
        if version is None:
            logger.debug(f"Skipping non-versioned schema: {file_path.name}")
            continue

        schemas.append((file_path, version))
        logger.debug(
            f"Found schema {file_path.name}: v{version[0]}.{version[1]}.{version[2]}"
        )

    if not schemas:
        logger.error(f"No valid schema files found in {dir_path}")
        sys.exit(1)

    logger.info(f"Found {len(schemas)} schema files in {dir_path}")
    return schemas


def select_schemas_to_process(
    schemas: list[tuple[Path, tuple[int, int, int]]], min_major: int, logger: Logger
) -> dict[int, tuple[Path, tuple[int, int, int]]]:
    """
    select latest patch version for each major version >= min_major.

    Args:
        schemas: list of (file_path, version_tuple) pairs
        min_major: minimum major version to include
        logger: logger instance

    Returns:
        dict mapping major_version -> (file_path, full_version_tuple)

    Example:
        Given schemas for 16.0.1, 16.1.3, 16.10.0, 17.0.0:
        Returns {16: (path_to_16.10.0, (16, 10, 0)), 17: (path_to_17.0.0, (17, 0, 0))}
    """
    # filter to min major version
    filtered = [(path, ver) for path, ver in schemas if ver[0] >= min_major]

    if not filtered:
        logger.error(
            f"No schemas found with major version >= {min_major}. "
            f"Available versions: {sorted({v[0] for _, v in schemas})}"
        )
        sys.exit(1)

    # group by major version and select highest semver
    by_major: dict[int, list[tuple[Path, tuple[int, int, int]]]] = {}
    for path, ver in filtered:
        major = ver[0]
        if major not in by_major:
            by_major[major] = []
        by_major[major].append((path, ver))

    # select latest patch for each major
    selected = {}
    for major, versions in by_major.items():
        # sort by (major, minor, patch) descending and take first
        latest = max(versions, key=lambda x: x[1])
        selected[major] = latest
        logger.info(
            f"Selected schema v{major}: {latest[1][0]}.{latest[1][1]}.{latest[1][2]} "
            f"from {len(versions)} options"
        )

    return selected


def load_json_schema(schema_path: Path, major_version: int, logger: Logger) -> dict:
    """
    load and parse JSON schema file, validating version matches $id field.

    Args:
        schema_path: path to JSON schema file
        major_version: expected major version number
        logger: logger instance

    Returns:
        schema dict

    Raises:
        SystemExit if schema file not found or version validation fails
    """
    if not schema_path.exists():
        logger.error(f"Schema file not found: {schema_path}")
        sys.exit(1)

    logger.debug(f"Loading schema from {schema_path}")

    with open(schema_path) as f:
        schema = json.load(f)

    # validate $id field contains expected major version
    # example: "anchore.io/schema/syft/json/16.0.40/document"
    schema_id = schema.get("$id", "")
    if not schema_id:
        logger.warning("Schema file missing $id field")
    else:
        # extract version from pattern like "json/16.0.40/document"
        version_match = re.search(r"/json/(\d+)\.\d+\.\d+/", schema_id)
        if version_match:
            id_major_version = int(version_match.group(1))
            if id_major_version != major_version:
                logger.warning(
                    f"Schema $id version mismatch: expected v{major_version}, "
                    f"found v{id_major_version} in $id: {schema_id}"
                )
        else:
            logger.warning(f"Cannot extract version from schema $id: {schema_id}")

    logger.info(f"Loaded schema v{major_version}")
    return schema


def find_referenced_types(
    def_schema: dict, all_defs: dict, visited: set[str] | None = None
) -> set[str]:
    """
    recursively find all types referenced by a definition.

    Args:
        def_schema: definition schema dict
        all_defs: all schema definitions
        visited: set of already visited type names (to avoid circular references)

    Returns:
        set of referenced type names
    """
    if visited is None:
        visited = set()

    referenced = set()

    # helper to extract type name from $ref
    def extract_ref(ref_dict):
        if not isinstance(ref_dict, dict):
            return None
        ref = ref_dict.get("$ref", "")
        if ref.startswith("#/$defs/"):
            return ref.replace("#/$defs/", "")
        return None

    # helper to process a field spec
    def process_field_spec(field_spec) -> None:
        if not isinstance(field_spec, dict):
            return

        # check direct $ref
        ref_name = extract_ref(field_spec)
        if ref_name and ref_name not in visited and ref_name in all_defs:
            referenced.add(ref_name)
            visited.add(ref_name)
            # recurse into referenced type
            referenced.update(
                find_referenced_types(all_defs[ref_name], all_defs, visited)
            )

        # check array items
        if field_spec.get("type") == "array" and "items" in field_spec:
            process_field_spec(field_spec["items"])

        # check anyOf/oneOf unions
        for union_key in ["anyOf", "oneOf"]:
            if union_key in field_spec:
                for option in field_spec[union_key]:
                    process_field_spec(option)

    # process all properties
    for field_spec in def_schema.get("properties", {}).values():
        process_field_spec(field_spec)

    return referenced


def load_ecosystem_types_from_catalogers() -> set[str]:
    """
    load ecosystem type names from cataloger json_schema_types.

    reads data/capabilities/syft-package-catalogers.json and extracts
    all json_schema_types directly (no transformation needed).

    Returns:
        set of type names as they appear in cataloger data (before case normalization)

    Examples:
        cataloger has 'AlpmDbEntry' -> returns 'AlpmDbEntry'
        cataloger has 'ApkDbEntry' -> returns 'ApkDbEntry'
    """
    cataloger_data = json.loads(config.paths.cataloger_cache_file.read_text())

    json_schema_types = set()
    for cataloger in cataloger_data.get("catalogers", []):
        for pattern in cataloger.get("patterns", []):
            for schema_type in pattern.get("json_schema_types", []):
                json_schema_types.add(schema_type)

    return json_schema_types


def extract_type_prefix(type_name: str) -> str:
    """
    extract ecosystem prefix from a type name.

    finds the first camelCase word by looking for the first uppercase letter
    after the initial character. this identifies the ecosystem prefix used for
    grouping related types.

    Args:
        type_name: the type name to extract prefix from

    Returns:
        first camelCase word

    Examples:
        'AlpmDbEntry' -> 'Alpm'
        'ApkFileRecord' -> 'Apk'
        'JavaArchive' -> 'Java'
        'DotnetDepsEntry' -> 'Dotnet'
        'Digest' -> 'Digest' (no second word, returns whole name)
    """
    # start from index 1 to skip the first character
    for i, char in enumerate(type_name[1:], start=1):
        if char.isupper():
            return type_name[:i]
    # no uppercase found after first char, return entire string
    return type_name


def is_single_word_type(type_name: str) -> bool:
    """
    check if type name has only one uppercase letter (single word, likely core type).

    single-word types with one uppercase letter are typically core infrastructure
    types like Digest, File, Location, etc.

    Args:
        type_name: the type name to check

    Returns:
        True if only one uppercase letter in name

    Examples:
        'Digest' -> True (only 'D')
        'File' -> True (only 'F')
        'Location' -> True (only 'L')
        'KeyValues' -> False ('K' and 'V')
        'AlpmFileRecord' -> False (multiple uppercase)
    """
    uppercase_count = sum(1 for c in type_name if c.isupper())
    return uppercase_count == 1


def _categorize_using_cataloger_data(
    all_defs: dict, ecosystem_types_from_schema: set[str], logger: Logger
) -> tuple[set[str], set[str], dict[str, set[str]]]:
    """
    use cataloger metadata to determine ecosystem vs core types.

    this is the DATA-DRIVEN implementation that replaces heuristics.
    loads json_schema_types from cataloger data and uses them to identify
    ecosystem types. for types referenced by ecosystem types, applies
    prefix matching and word count rules to determine categorization.

    Process:
    1. load ecosystem types from cataloger json_schema_types (case-insensitive match)
    2. for each ecosystem type, find all referenced types
    3. for each referenced type:
       a. if it's already an ecosystem type, skip
       b. if it has only 1 uppercase letter → core type
       c. if it shares prefix with referencing ecosystem type → ecosystem type
       d. otherwise → core type

    Args:
        all_defs: all schema definitions
        ecosystem_types_from_schema: ecosystem types from Package.metadata.anyOf (not used, kept for compatibility)
        logger: logger instance

    Returns:
        tuple of (truly_core_types, ecosystem_types, ecosystem_refs) where:
        - truly_core_types: set of type names that should be in core section
        - ecosystem_types: set of ecosystem type names identified from cataloger data
        - ecosystem_refs: dict mapping ecosystem type -> set of types it references
    """
    # load ecosystem types from cataloger metadata
    cataloger_ecosystem_types = load_ecosystem_types_from_catalogers()
    logger.debug(
        f"Loaded {len(cataloger_ecosystem_types)} json_schema_types from cataloger data"
    )

    # match cataloger types against schema types (case-insensitive)
    # cataloger has: AlpmDbEntry, schema has: AlpmDbEntry
    schema_type_names_lower = {name.lower(): name for name in all_defs.keys()}

    ecosystem_types = set()
    matched_count = 0
    for cataloger_type in cataloger_ecosystem_types:
        cataloger_type_lower = cataloger_type.lower()
        if cataloger_type_lower in schema_type_names_lower:
            # found a match - use the schema's actual type name
            schema_type_name = schema_type_names_lower[cataloger_type_lower]
            ecosystem_types.add(schema_type_name)
            matched_count += 1
            logger.debug(
                f"  Matched cataloger type '{cataloger_type}' to schema type '{schema_type_name}'"
            )

    logger.debug(
        f"Matched {matched_count}/{len(cataloger_ecosystem_types)} cataloger types to schema types"
    )
    logger.debug(f"Final ecosystem types count: {len(ecosystem_types)}")

    # find all types referenced by each ecosystem type
    ecosystem_refs = {}
    ecosystem_related_types = (
        set()
    )  # types that are referenced by ecosystems and share prefix

    for eco_type in ecosystem_types:
        if eco_type not in all_defs:
            continue

        refs = find_referenced_types(all_defs[eco_type], all_defs)
        ecosystem_refs[eco_type] = refs

        # get prefix of this ecosystem type
        eco_prefix = extract_type_prefix(eco_type)

        # examine each referenced type
        for ref_type in refs:
            # skip if already identified as ecosystem type
            if ref_type in ecosystem_types:
                continue

            # check if it's a single-word core type (e.g., Digest, File, Location)
            if is_single_word_type(ref_type):
                logger.debug(f"  Type '{ref_type}' is single-word → core type")
                continue

            # check if it shares prefix with the ecosystem type
            ref_prefix = extract_type_prefix(ref_type)
            if ref_prefix == eco_prefix:
                # shares prefix, so it's also an ecosystem type
                ecosystem_related_types.add(ref_type)
                logger.debug(
                    f"  Type '{ref_type}' shares prefix '{ref_prefix}' with '{eco_type}' → ecosystem type"
                )

    # add prefix-matched types to ecosystem_types
    ecosystem_types.update(ecosystem_related_types)
    logger.debug(
        f"Added {len(ecosystem_related_types)} prefix-matched types to ecosystem types"
    )

    # truly_core_types = everything that's not an ecosystem type or Document
    truly_core_types = set()
    for type_name in all_defs.keys():
        if type_name == "Document":
            continue
        if type_name not in ecosystem_types:
            truly_core_types.add(type_name)

    logger.debug(
        f"Total ecosystem types (including prefix-matched): {len(ecosystem_types)}"
    )
    logger.debug(f"Total truly_core_types: {len(truly_core_types)}")
    logger.debug(f"Ecosystem types sample: {sorted(ecosystem_types)[:10]}...")
    logger.debug(f"Core types sample: {sorted(truly_core_types)[:10]}...")

    return truly_core_types, ecosystem_types, ecosystem_refs


def _build_categorization_from_core_types(
    truly_core_types: set[str],
    ecosystem_types: set[str],
    ecosystem_refs: dict[str, set[str]],
    all_defs: dict,
    logger: Logger,
) -> dict[str, Any]:
    """
    build categorization structure from truly core types.

    this is pure computation that organizes types into sections based on
    the provided core types set. no heuristics here - just data organization.

    Args:
        truly_core_types: set of type names that should be in core section
        ecosystem_types: set of ecosystem type names
        ecosystem_refs: dict mapping ecosystem type -> set of types it references
        all_defs: all schema definitions
        logger: logger instance

    Returns:
        dict with categorization:
        {
            "core_only": [type names that should be in core],
            "ecosystem_related": {ecosystem_type: [non-core types it references]},
            "shared": []  # always empty, kept for compatibility
        }
    """
    # build ecosystem_related dict, excluding truly core types
    ecosystem_related = {}
    for eco_type, refs in ecosystem_refs.items():
        # filter out truly core types from ecosystem-related types
        ecosystem_specific_refs = [ref for ref in refs if ref not in truly_core_types]
        if ecosystem_specific_refs:
            ecosystem_related[eco_type] = sorted(ecosystem_specific_refs)

    # log sample ecosystem_related mappings
    sample_ecosystems = list(ecosystem_related.keys())[:3]
    for eco_type in sample_ecosystems:
        related = ecosystem_related.get(eco_type, [])
        logger.debug(
            f"Ecosystem {eco_type} has {len(related)} related types: {related[:5]}..."
        )

    # core types include truly core types AND types not referenced by any ecosystem
    all_ecosystem_specific_refs = set()
    for refs in ecosystem_related.values():
        all_ecosystem_specific_refs.update(refs)

    core_only = [
        name
        for name in all_defs.keys()
        if (
            name in truly_core_types  # truly core types always included
            or (
                name not in ecosystem_types  # not an ecosystem type itself
                and name not in all_ecosystem_specific_refs  # not ecosystem-specific
            )
        )
    ]

    return {
        "core_only": sorted(core_only),
        "ecosystem_related": ecosystem_related,
        "shared": [],  # empty - we show everything under ecosystem types
    }


# ==============================================================================
# DATA-DRIVEN CATEGORIZATION - IMPLEMENTATION NOTES
# ==============================================================================
#
# This code now uses DATA-DRIVEN categorization based on cataloger json_schema_types.
#
# HOW IT WORKS:
#
# 1. Loads json_schema_types from data/capabilities/syft-package-catalogers.json
#    - Each cataloger pattern has json_schema_types field (e.g., "AlpmDbEntry")
#    - These identify ecosystem-specific metadata types
#
# 2. Matches cataloger types to JSON schema types (case-insensitive)
#    - Cataloger: "AlpmDbEntry" → matches schema: "AlpmDbEntry"
#    - Case-insensitive matching provides robustness
#
# 3. For types referenced by ecosystem types, applies categorization rules:
#    a. Single uppercase letter only? → core type (e.g., Digest, File, Location)
#    b. Shares prefix with ecosystem type? → ecosystem type (e.g., AlpmFileRecord)
#    c. Otherwise → core type (default)
#
# ADVANTAGES OVER HEURISTICS:
#
# - Authoritative source: cataloger data explicitly defines ecosystem types
# - Maintainable: new ecosystem types automatically categorized when added to catalogers
# - Accurate: prefix matching ensures related types stay together
# - Simple: no arbitrary thresholds or reference counting
#
# IMPLEMENTATION:
#
# - load_ecosystem_types_from_catalogers(): loads json_schema_types directly
# - extract_type_prefix(): finds common prefix for related type matching
# - is_single_word_type(): identifies single-word core types
# - _categorize_using_cataloger_data(): main categorization logic
# - compute_type_categories(): chokepoint that calls cataloger-based logic
#
# ==============================================================================


def compute_type_categories(
    all_defs: dict, ecosystem_types: set[str], logger: Logger
) -> dict[str, Any]:
    """
    **CATEGORIZATION CHOKEPOINT** - single function that decides which types go where.

    this is the ONLY function responsible for type categorization. to switch from
    heuristic-based to data-driven categorization, modify only this function.

    current implementation: DATA-DRIVEN using cataloger metadata_types
    - loads metadata_types from data/capabilities/syft-package-catalogers.json
    - matches them against JSON schema types (case-insensitive)
    - applies prefix matching for related types
    - uses word count heuristic for edge cases

    categorization approach:
    1. load metadata_types from cataloger data
    2. match against JSON schema types (case-insensitive)
    3. for types referenced by ecosystem types:
       - single uppercase letter only? → core type
       - shares prefix with ecosystem type? → ecosystem type
       - otherwise → core type (default)
    4. everything else not categorized as ecosystem → core type

    Args:
        all_defs: all schema definitions
        ecosystem_types: set of ecosystem type names (from Package.metadata.anyOf, for compatibility)
        logger: logger instance

    Returns:
        dict with categorization:
        {
            "core_only": [type names for core section],
            "ecosystem_related": {ecosystem_type: [related types]},
            "shared": []  # always empty, kept for compatibility
        }
    """
    # use data-driven categorization from cataloger metadata
    truly_core_types, cataloger_ecosystem_types, ecosystem_refs = (
        _categorize_using_cataloger_data(all_defs, ecosystem_types, logger)
    )

    # build categorization structure from core types
    # use ecosystem types from cataloger data, not from Package.metadata.anyOf
    return _build_categorization_from_core_types(
        truly_core_types, cataloger_ecosystem_types, ecosystem_refs, all_defs, logger
    )


def categorize_definitions(schema: dict, logger: Logger) -> dict[str, Any]:
    """
    categorize schema definitions into Core Types, Ecosystem Types, and related types.

    ecosystem types are identified by examining Package.metadata.anyOf union.
    related types are types ONLY referenced by ecosystem types.
    core types are everything else (including shared types used by both).

    filters out types in config.excluded_schema_types from all categories.

    Args:
        schema: parsed JSON schema dict
        logger: logger instance

    Returns:
        dict with keys:
        - "core": list of core type names (includes shared types)
        - "ecosystem": list of ecosystem type names
        - "ecosystem_related": dict mapping ecosystem type -> list of related types
    """
    all_defs = schema.get("$defs", {})
    ecosystem_types = set()

    # find Package definition
    package_def = all_defs.get("Package")
    if not package_def:
        logger.warning("Package definition not found in schema")
        return {
            "core": list(all_defs.keys()),
            "ecosystem": [],
            "ecosystem_related": {},
        }

    # find metadata field's anyOf union
    metadata_field = package_def.get("properties", {}).get("metadata", {})
    any_of = metadata_field.get("anyOf", [])

    # extract ecosystem type names from anyOf (excluding "null" type)
    for option in any_of:
        if option.get("type") == "null":
            continue

        ref = option.get("$ref", "")
        # extract type name from "#/$defs/TypeName"
        if ref.startswith("#/$defs/"):
            type_name = ref.replace("#/$defs/", "")
            ecosystem_types.add(type_name)

    # use categorization chokepoint to determine type categories
    categories = compute_type_categories(all_defs, ecosystem_types, logger)

    # core types = types not in ecosystem + shared types (excluding Document and excluded types)
    core_types = [
        t
        for t in (categories["core_only"] + categories["shared"])
        if t != "Document" and t not in config.excluded_schema_types
    ]

    # filter excluded types from ecosystem types
    filtered_ecosystem_types = [
        t for t in ecosystem_types if t not in config.excluded_schema_types
    ]

    # filter excluded types from ecosystem_related (both keys and values)
    filtered_ecosystem_related = {}
    for eco_type, related_types in categories["ecosystem_related"].items():
        if eco_type not in config.excluded_schema_types:
            filtered_related = [
                t for t in related_types if t not in config.excluded_schema_types
            ]
            if filtered_related:
                filtered_ecosystem_related[eco_type] = filtered_related

    logger.debug(
        f"Categorized {len(core_types)} core types, "
        f"{len(filtered_ecosystem_types)} ecosystem types, "
        f"{sum(len(v) for v in filtered_ecosystem_related.values())} ecosystem-related types"
    )

    return {
        "document": ["Document"],  # Document gets its own section
        "core": sorted(core_types),
        "ecosystem": sorted(filtered_ecosystem_types),
        "ecosystem_related": filtered_ecosystem_related,
    }


def get_documented_types(categories: dict[str, Any], all_defs: dict) -> set[str]:
    """
    collect all type names that will be documented on the page.

    only includes types that have fields (types without fields are skipped in HTML generation).

    Args:
        categories: categorization dict from categorize_definitions()
        all_defs: all schema definitions

    Returns:
        set of type names that have documentation sections
    """
    documented = set()

    def has_fields(type_name: str) -> bool:
        """check if type has any fields"""
        type_def = all_defs.get(type_name)
        if not type_def:
            return False
        properties = type_def.get("properties", {})
        return len(properties) > 0

    # add Document (if it has fields)
    for type_name in categories.get("document", []):
        if has_fields(type_name):
            documented.add(type_name)

    # add core types (if they have fields)
    for type_name in categories.get("core", []):
        if has_fields(type_name):
            documented.add(type_name)

    # add ecosystem types (if they have fields)
    for type_name in categories.get("ecosystem", []):
        if has_fields(type_name):
            documented.add(type_name)

    # add ecosystem-related types (if they have fields)
    ecosystem_related = categories.get("ecosystem_related", {})
    for related_types in ecosystem_related.values():
        for type_name in related_types:
            if has_fields(type_name):
                documented.add(type_name)

    return documented


def expand_type_reference(type_spec: Any, all_defs: dict) -> str:
    """
    expand type specification to human-readable type string.

    handles:
    - primitives: "string", "integer", "boolean"
    - references: {"$ref": "#/$defs/Foo"} -> "Foo"
    - arrays: {"type": "array", "items": {...}} -> "Array<Type>"
    - unions: {"anyOf": [...]} or {"oneOf": [...]}

    Args:
        type_spec: type specification (dict or string)
        all_defs: all schema definitions for resolving references

    Returns:
        human-readable type string
    """
    # handle string type specifications
    if isinstance(type_spec, str):
        return type_spec

    # handle dict type specifications
    if isinstance(type_spec, dict):
        # handle $ref
        if "$ref" in type_spec:
            ref = type_spec["$ref"]
            if ref.startswith("#/$defs/"):
                return ref.replace("#/$defs/", "")
            return ref

        # handle primitive types
        if "type" in type_spec:
            type_value = type_spec["type"]

            # handle arrays
            if type_value == "array":
                items = type_spec.get("items", {})
                item_type = expand_type_reference(items, all_defs)
                return f"Array&lt;{item_type}&gt;"

            # handle primitives
            return type_value

        # handle anyOf unions
        if "anyOf" in type_spec:
            options = type_spec["anyOf"]
            # filter out null types for cleaner display
            non_null_options = [
                opt
                for opt in options
                if not (isinstance(opt, dict) and opt.get("type") == "null")
            ]
            if len(non_null_options) == 1:
                return expand_type_reference(non_null_options[0], all_defs)
            elif non_null_options:
                option_types = [
                    expand_type_reference(opt, all_defs) for opt in non_null_options
                ]
                return " | ".join(option_types)

        # handle oneOf unions
        if "oneOf" in type_spec:
            options = type_spec["oneOf"]
            option_types = [expand_type_reference(opt, all_defs) for opt in options]
            return " | ".join(option_types)

    return "unknown"


def clean_type_description(type_name: str, description: str) -> str:
    """
    clean type-level description by removing redundant type name prefix.

    if description starts with the type name, removes it and capitalizes
    the first letter of the remaining text.

    Args:
        type_name: name of the type definition
        description: original description text

    Returns:
        cleaned description text

    Examples:
        >>> clean_type_description("PhpComposerAuthors", "PhpComposerAuthors represents author info...")
        "Represents author info..."
        >>> clean_type_description("Package", "represents a package")
        "represents a package"
    """
    if not description:
        return description

    # split description into words
    words = description.split(None, 1)  # split on first whitespace only
    if not words:
        return description

    first_word = words[0]

    # check if first word matches type name (case-insensitive)
    if first_word.lower() == type_name.lower():
        # remove type name and capitalize remainder
        if len(words) > 1:
            remainder = words[1]
            # capitalize first letter
            if remainder:
                return remainder[0].upper() + remainder[1:]
            return remainder
        # description was just the type name
        return ""

    # no match, return original
    return description


def linkify_type_string(type_str: str, documented_types: set[str]) -> str:
    """
    add hyperlinks to type references that are documented on the page.

    handles simple types, arrays, and unions. Preserves HTML entities.
    primitives and undocumented types are left as plain text.

    Args:
        type_str: type string from expand_type_reference (may contain HTML entities)
        documented_types: set of type names that have documentation sections

    Returns:
        type string with documented types wrapped in anchor links

    Examples:
        >>> linkify_type_string("Package", {"Package"})
        '<a href="#package">Package</a>'
        >>> linkify_type_string("Array&lt;Location&gt;", {"Location"})
        'Array&lt;<a href="#location">Location</a>&gt;'
        >>> linkify_type_string("string | Package", {"Package"})
        'string | <a href="#package">Package</a>'
    """
    # primitive types that should never be linked
    primitives = {"string", "integer", "boolean", "object", "null", "number", "array"}

    # helper to linkify a single type name
    def linkify_single(name: str) -> str:
        name = name.strip()
        if not name or name in primitives or name not in documented_types:
            return name
        return f'<a href="#{name.lower()}">{name}</a>'

    # handle union types (split by " | ")
    if " | " in type_str:
        parts = type_str.split(" | ")
        linked_parts = []
        for part in parts:
            # each part might be an array or simple type
            if part.startswith("Array&lt;") and part.endswith("&gt;"):
                # extract inner type from Array&lt;Type&gt;
                inner = part[9:-4]  # remove "Array&lt;" and "&gt;"
                linked_inner = linkify_single(inner)
                linked_parts.append(f"Array&lt;{linked_inner}&gt;")
            else:
                linked_parts.append(linkify_single(part))
        return shorten_type_string(" | ".join(linked_parts))

    # handle array types
    if type_str.startswith("Array&lt;") and type_str.endswith("&gt;"):
        inner = type_str[9:-4]  # remove "Array&lt;" and "&gt;"
        # inner might itself be a union
        if " | " in inner:
            parts = inner.split(" | ")
            linked_parts = [linkify_single(p) for p in parts]
            return shorten_type_string(f"Array&lt;{' | '.join(linked_parts)}&gt;")
        else:
            linked_inner = linkify_single(inner)
            return shorten_type_string(f"Array&lt;{linked_inner}&gt;")

    # simple type
    return shorten_type_string(linkify_single(type_str))


def shorten_type_string(type_str: str) -> str:
    """
    shorten primitive type names to save horizontal space.

    replaces verbose primitive types with shorter equivalents while preserving
    custom type names, HTML entities, and complex type structures.

    Args:
        type_str: type string (may contain HTML entities and links)

    Returns:
        type string with shortened primitive types

    Examples:
        >>> shorten_type_string("string")
        "str"
        >>> shorten_type_string("Array&lt;integer&gt;")
        "Array&lt;int&gt;"
        >>> shorten_type_string("string | boolean")
        "str | bool"
    """
    # primitive type mappings
    replacements = {
        "string": "str",
        "integer": "int",
        "boolean": "bool",
        "object": "obj",
    }

    # apply replacements as whole-word substitutions
    # use word boundaries to avoid replacing parts of custom type names
    import re

    result = type_str
    for long_name, short_name in replacements.items():
        # match whole word (not part of another word)
        # negative lookbehind/lookahead to ensure not part of a type name
        pattern = r"\b" + re.escape(long_name) + r"\b"
        result = re.sub(pattern, short_name, result)

    return result


def should_replace_field_with_link(
    def_name: str, field_name: str, field_spec: dict
) -> bool:
    """
    determine if a field should be replaced with a link to Ecosystem Types section.

    specifically checks for Package.metadata field which has a large anyOf union.

    Args:
        def_name: name of the type definition
        field_name: name of the field
        field_spec: field specification dict

    Returns:
        True if field should show link instead of full type
    """
    # check if this is the Package.metadata field
    if def_name == "Package" and field_name == "metadata":
        # check if it has anyOf with multiple options (ecosystem types)
        any_of = field_spec.get("anyOf", [])
        # if there are many options (more than just null), this is the ecosystem union
        non_null_options = [
            opt
            for opt in any_of
            if not (isinstance(opt, dict) and opt.get("type") == "null")
        ]
        return len(non_null_options) > 5  # arbitrary threshold
    return False


def parse_definition(def_name: str, def_schema: dict, all_defs: dict) -> dict[str, Any]:
    """
    parse a schema definition to extract structured information.

    Args:
        def_name: name of the definition
        def_schema: definition schema dict
        all_defs: all schema definitions for resolving references

    Returns:
        dict with:
        - name: definition name
        - description: type-level description (if exists)
        - fields: list of field dicts with name, type, required, description
    """
    result = {
        "name": def_name,
        "description": clean_type_description(
            def_name, def_schema.get("description", "")
        ),
        "fields": [],
    }

    properties = def_schema.get("properties", {})
    required_fields = set(def_schema.get("required", []))

    for field_name, field_spec in properties.items():
        # handle edge case where field_spec might be a boolean or other primitive
        if not isinstance(field_spec, dict):
            # skip non-dict field specs (shouldn't happen in well-formed schemas)
            continue

        # check if this field should be replaced with a link
        if should_replace_field_with_link(def_name, field_name, field_spec):
            field_type = "ECOSYSTEM_TYPES_LINK"  # special marker
            field_desc = ""  # clear description for this special field
        else:
            field_type = expand_type_reference(field_spec, all_defs)
            field_desc = field_spec.get("description", "")

        is_required = field_name in required_fields

        result["fields"].append(
            {
                "name": field_name,
                "type": field_type,
                "required": is_required,
                "description": field_desc,
            }
        )

    return result


def has_field_descriptions(fields: list[dict]) -> bool:
    """
    check if any field has a non-empty description.

    Args:
        fields: list of field dicts with 'description' key

    Returns:
        true if at least one field has a non-empty description
    """
    return any(field.get("description", "").strip() for field in fields)


def generate_type_section_html(
    type_names: list[str],
    all_defs: dict,
    section_title: str,
    logger: Logger,
    documented_types: set[str],
    related_types_map: dict[str, list[str]] | None = None,
) -> list[str]:
    """
    generate HTML for a section of type definitions.

    Args:
        type_names: list of type names to include
        all_defs: all schema definitions
        section_title: section heading (e.g., "Core Types", "Ecosystem Types")
        logger: logger instance
        documented_types: set of type names that have documentation sections
        related_types_map: optional dict mapping type names to their related types
                          (used for ecosystem types to show related types with h4)

    Returns:
        list of HTML lines
    """
    html_lines = []

    # generate markdown h2 header with custom anchor ID
    anchor_id = section_title.lower().replace(" ", "-")
    html_lines.append(f"## {section_title} {{#{anchor_id}}}\n")

    for type_name in type_names:
        type_def = all_defs.get(type_name)
        if not type_def:
            logger.warning(f"Definition not found: {type_name}")
            continue

        parsed = parse_definition(type_name, type_def, all_defs)

        # skip types with no fields entirely
        if not parsed["fields"]:
            continue

        # type heading with anchor (markdown h3)
        html_lines.append(f"### `{type_name}` {{#{type_name.lower()}}}\n")

        # type description (if exists)
        if parsed["description"]:
            html_lines.append(f"<p>{parsed['description']}</p>\n")

        # table header
        show_descriptions = has_field_descriptions(parsed["fields"])

        html_lines.append(f'<table class="{CSSClasses.SCHEMA_TABLE}">')
        html_lines.append("  <thead>")
        html_lines.append("    <tr>")
        html_lines.append(
            f'      <th class="{CSSClasses.COL_FIELD_NAME}">Field Name</th>'
        )
        html_lines.append(f'      <th class="{CSSClasses.COL_TYPE}">Type</th>')
        if show_descriptions:
            html_lines.append(
                f'      <th class="{CSSClasses.COL_DESCRIPTION}">Description</th>'
            )
        html_lines.append("    </tr>")
        html_lines.append("  </thead>")
        html_lines.append("  <tbody>")

        # table rows
        for field in parsed["fields"]:
            html_lines.append("    <tr>")
            # add required icon outside code block for required fields
            field_name_html = f"<code>{field['name']}</code>"
            if field["required"]:
                field_name_html += f'<svg class="{CSSClasses.REQUIRED_ICON}"><use xlink:href="#icon-required"></use></svg>'
            html_lines.append(
                f'      <td class="{CSSClasses.COL_FIELD_NAME}">{field_name_html}</td>'
            )

            # handle special ecosystem types link
            if field["type"] == "ECOSYSTEM_TYPES_LINK":
                html_lines.append(
                    f'      <td class="{CSSClasses.COL_TYPE}"><em><a href="#ecosystem-specific-types">see the Ecosystem Specific Types section</a></em></td>'
                )
            else:
                # linkify type references and wrap in code tags
                linked_type = linkify_type_string(field["type"], documented_types)
                html_lines.append(
                    f'      <td class="{CSSClasses.COL_TYPE}"><code>{linked_type}</code></td>'
                )

            if show_descriptions:
                html_lines.append(
                    f'      <td class="{CSSClasses.COL_DESCRIPTION}">{field["description"]}</td>'
                )
            html_lines.append("    </tr>")

        # close table
        html_lines.append("  </tbody>")
        html_lines.append("</table>\n")

        # if this is an ecosystem type with related types, show them with h4
        if related_types_map and type_name in related_types_map:
            related_types = related_types_map[type_name]
            for related_type_name in related_types:
                related_def = all_defs.get(related_type_name)
                if not related_def:
                    logger.warning(f"Related type not found: {related_type_name}")
                    continue

                related_parsed = parse_definition(
                    related_type_name, related_def, all_defs
                )

                # skip related types with no fields entirely
                if not related_parsed["fields"]:
                    continue

                # related type heading with markdown h4
                html_lines.append(
                    f"#### `{related_type_name}` {{#{related_type_name.lower()}}}\n"
                )

                # type description (if exists)
                if related_parsed["description"]:
                    html_lines.append(f"<p>{related_parsed['description']}</p>\n")

                # table (same structure as main types)
                related_show_descriptions = has_field_descriptions(
                    related_parsed["fields"]
                )

                html_lines.append(f'<table class="{CSSClasses.SCHEMA_TABLE}">')
                html_lines.append("  <thead>")
                html_lines.append("    <tr>")
                html_lines.append(
                    f'      <th class="{CSSClasses.COL_FIELD_NAME}">Field Name</th>'
                )
                html_lines.append(f'      <th class="{CSSClasses.COL_TYPE}">Type</th>')
                if related_show_descriptions:
                    html_lines.append(
                        f'      <th class="{CSSClasses.COL_DESCRIPTION}">Description</th>'
                    )
                html_lines.append("    </tr>")
                html_lines.append("  </thead>")
                html_lines.append("  <tbody>")

                for field in related_parsed["fields"]:
                    html_lines.append("    <tr>")
                    # add required icon outside code block for required fields
                    field_name_html = f"<code>{field['name']}</code>"
                    if field["required"]:
                        field_name_html += f'<svg class="{CSSClasses.REQUIRED_ICON}"><use xlink:href="#icon-required"></use></svg>'
                    html_lines.append(
                        f'      <td class="{CSSClasses.COL_FIELD_NAME}">{field_name_html}</td>'
                    )
                    # linkify type references
                    linked_type = linkify_type_string(field["type"], documented_types)
                    html_lines.append(
                        f'      <td class="{CSSClasses.COL_TYPE}"><code>{linked_type}</code></td>'
                    )

                    if related_show_descriptions:
                        html_lines.append(
                            f'      <td class="{CSSClasses.COL_DESCRIPTION}">{field["description"]}</td>'
                        )
                    html_lines.append("    </tr>")

                html_lines.append("  </tbody>")
                html_lines.append("</table>\n")

    return html_lines


def generate_schema_documentation(
    schema: dict,
    full_version: tuple[int, int, int],
    output_dir: Path,
    is_latest: bool,
    logger: Logger,
) -> None:
    """
    generate complete schema reference documentation.

    Args:
        schema: parsed JSON schema dict
        full_version: version tuple (major, minor, patch)
        output_dir: output directory for generated file
        is_latest: whether to add /latest alias and sidebar badge
        logger: logger instance
    """
    major, minor, patch = full_version
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / f"{major}.md"

    logger.info(f"Generating documentation for schema v{major}.{minor}.{patch}")

    # categorize definitions
    categories = categorize_definitions(schema, logger)
    all_defs = schema.get("$defs", {})

    # collect all documented types for linkification
    documented_types = get_documented_types(categories, all_defs)

    # calculate weight (newest first: v17=183, v16=184, v15=185)
    weight = 200 - major

    # generate front matter (must be first - no comments before it)
    front_matter_lines = [
        "+++",
        f'title = "Syft v{major} JSON Schema Reference"',
        f'linkTitle = "v{major}"',
        f'description = "Complete reference for Syft JSON schema version `{major}.{minor}.{patch}`"',
        f"weight = {weight}",
        'type = "docs"',
        'menu_group = "syft"',
        f'url = "/docs/reference/syft/json/{major}"',
    ]

    if is_latest:
        front_matter_lines.append('aliases = ["/docs/reference/syft/json/latest"]')
        front_matter_lines.append("")
        front_matter_lines.append("[params]")
        front_matter_lines.append('sidebar_badge = "latest"')

    front_matter_lines.append("+++")

    # generate comment (after front matter)
    comment = config.get_generated_comment(__file__, "html")
    comment += "<!-- markdownlint-disable MD013 MD033 -->\n"

    # generate content sections
    content_lines = []

    # document section (single type, no h3 to avoid redundant "Document" heading)
    doc_html = []
    doc_html.append("## Document {#document}\n")

    # get and parse Document definition
    doc_def = all_defs.get("Document")
    if doc_def:
        parsed = parse_definition("Document", doc_def, all_defs)

        # type description (if exists)
        if parsed["description"]:
            doc_html.append(f"<p>{parsed['description']}</p>\n")

        # generate table (same structure as in generate_type_section_html)
        if parsed["fields"]:
            show_descriptions = has_field_descriptions(parsed["fields"])

            doc_html.append(f'<table class="{CSSClasses.SCHEMA_TABLE}">')
            doc_html.append("  <thead>")
            doc_html.append("    <tr>")
            doc_html.append(
                f'      <th class="{CSSClasses.COL_FIELD_NAME}">Field Name</th>'
            )
            doc_html.append(f'      <th class="{CSSClasses.COL_TYPE}">Type</th>')
            if show_descriptions:
                doc_html.append(
                    f'      <th class="{CSSClasses.COL_DESCRIPTION}">Description</th>'
                )
            doc_html.append("    </tr>")
            doc_html.append("  </thead>")
            doc_html.append("  <tbody>")

            for field in parsed["fields"]:
                doc_html.append("    <tr>")
                # add required icon outside code block for required fields
                field_name_html = f"<code>{field['name']}</code>"
                if field["required"]:
                    field_name_html += f'<svg class="{CSSClasses.REQUIRED_ICON}"><use xlink:href="#icon-required"></use></svg>'
                doc_html.append(
                    f'      <td class="{CSSClasses.COL_FIELD_NAME}">{field_name_html}</td>'
                )
                # linkify type references
                linked_type = linkify_type_string(field["type"], documented_types)
                doc_html.append(
                    f'      <td class="{CSSClasses.COL_TYPE}"><code>{linked_type}</code></td>'
                )

                if show_descriptions:
                    doc_html.append(
                        f'      <td class="{CSSClasses.COL_DESCRIPTION}">{field["description"]}</td>'
                    )
                doc_html.append("    </tr>")

            doc_html.append("  </tbody>")
            doc_html.append("</table>\n")
        else:
            doc_html.append("<p><em>No fields defined</em></p>\n")
    else:
        logger.warning("Document definition not found")

    content_lines.extend(doc_html)

    # core types section
    content_lines.extend(
        generate_type_section_html(
            categories["core"], all_defs, "Core Types", logger, documented_types
        )
    )

    # ecosystem types section (with related types)
    content_lines.extend(
        generate_type_section_html(
            categories["ecosystem"],
            all_defs,
            "Ecosystem Specific Types",
            logger,
            documented_types,
            related_types_map=categories["ecosystem_related"],
        )
    )

    # write file (front matter must be first)
    with open(output_file, "w") as f:
        f.write("\n".join(front_matter_lines) + "\n\n")
        f.write(comment)
        f.write("\n".join(content_lines))

    logger.info(f"Generated {output_file}")


if __name__ == "__main__":
    main()
