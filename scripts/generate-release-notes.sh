#!/bin/bash

# Array of repos and their weights
# Format: "repo_name:weight:output_subdir"
REPOS=(
    "syft:10:syft"
    "grype:20:grype"
    "grant:30:grant"
    "grype-db:40:grype-db"
    "vunnel:50:vunnel"
    "sbom-action:60:sbom-action"
    "scan-action:70:scan-action"
    "stereoscope:80:stereoscope"
)

# Base output directory for Hugo content
BASE_OUTPUT_DIR="content/docs/releases"

# Iterate through the repos array
for repo_info in "${REPOS[@]}"; do
    # Split the repo_info string by colon
    IFS=':' read -r repo_name weight output_subdir <<< "$repo_info"
    
    # Construct the output directory
    output_dir="${BASE_OUTPUT_DIR}/${output_subdir}"
    
    echo "Processing ${repo_name} with weight ${weight}..."
    
    # Call the Python script with the appropriate arguments
    python scripts/release-to-hugo.py --repo "$repo_name" --output-dir "$output_dir" --weight "$weight"
    
    # Check if the previous command was successful
    if [ $? -eq 0 ]; then
        echo "✅ Successfully generated release notes for ${repo_name}"
    else
        echo "❌ Failed to generate release notes for ${repo_name}"
    fi
    
    echo "-----------------------------------"
done

echo "All release notes have been generated!"