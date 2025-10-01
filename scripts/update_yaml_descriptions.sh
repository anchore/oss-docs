#!/bin/bash

# Update remaining YAML files with better descriptions and query format

cd "$(dirname "$0")/../data/sbom/jq-query-examples" || exit 1

# Function to update a YAML file
update_yaml() {
    local file=$1
    local desc=$2

    # Extract current query (everything after 'query: |')
    query=$(awk '/query: \|/{flag=1;next}/^[a-z]/{flag=0}flag' "$file" | sed 's/^  jq /  /' | sed 's/ \\$//' | sed "s/' *\$//" | sed '/sbom\.json/d' | sed "s/^  '/  /" | sed "/^  $/d")

    # Write new format
    cat > "$file" << EOF
description: "$desc"
image: $(grep '^image:' "$file" | cut -d'"' -f2)
config: null
query: |
$query
EOF
}

# Update each file
update_yaml "packages-by-type.yaml" "Filters packages by ecosystem type with their license information"
update_yaml "all-purls.yaml" "Extracts Package URLs for cross-tool SBOM correlation and vulnerability matching"
update_yaml "packages-by-language.yaml" "Groups and counts packages by programming language"
update_yaml "count-packages-by-type.yaml" "Provides a summary count of packages per ecosystem"
update_yaml "go-modules.yaml" "Shows Go module dependencies with content-addressable hashes"
update_yaml "python-packages.yaml" "Lists Python packages with author metadata"
update_yaml "npm-packages.yaml" "Shows npm packages with integrity hashes for supply chain verification"
update_yaml "package-locations.yaml" "Maps packages to their filesystem locations"
update_yaml "files-by-mime-type.yaml" "Filters files by MIME type, useful for finding specific file types"
update_yaml "dependency-relationships.yaml" "Traverses package dependency graph using relationships"
update_yaml "files-without-packages.yaml" "Finds orphaned files not associated with any package"
update_yaml "file-licenses.yaml" "Extracts license information embedded in source files"
update_yaml "large-files.yaml" "Identifies the top 10 largest files by size"
update_yaml "all-cpes.yaml" "Lists Common Platform Enumeration identifiers for vulnerability scanning"
update_yaml "package-digests.yaml" "Extracts package verification hashes"
update_yaml "packages-without-licenses.yaml" "Identifies packages missing license information for compliance audits"
update_yaml "packages-with-cves.yaml" "Lists packages with CPE identifiers indicating potential CVE matches"
update_yaml "source-metadata.yaml" "Shows what was scanned and image provenance information"
update_yaml "os-distro-info.yaml" "Extracts operating system distribution details"

echo "Updated all YAML files"
