#!/usr/bin/env python3
"""
Simple GitHub Release Notes to Hugo Converter

This script fetches release notes from a GitHub repository and converts them
to Hugo markdown files with minimal processing, preserving the original format
and converting GitHub usernames to links.
"""

import os
import requests
from datetime import datetime
import argparse
import re

# GitHub API configuration
HEADERS = {"Accept": "application/vnd.github.v3+json"}

def fetch_releases(repo, token=None, limit=None):
    """Fetch releases from GitHub API for the given repository"""
    if token:
        HEADERS["Authorization"] = f"token {token}"
    
    all_releases = []
    page = 1
    per_page = 100
    base_url = f"https://api.github.com/repos/{repo}/releases"
    
    while True:
        response = requests.get(
            f"{base_url}?page={page}&per_page={per_page}", 
            headers=HEADERS
        )
        response.raise_for_status()
        releases = response.json()
        
        if not releases:
            break
            
        all_releases.extend(releases)
        
        if limit and len(all_releases) >= limit:
            all_releases = all_releases[:limit]
            break
            
        page += 1
    
    return all_releases

def link_github_users(text):
    """Replace @username with [@username](https://github.com/username), but only if not already a link"""
    return re.sub(r'(?<!\[)@(\w+)', r'[@\1](https://github.com/\1)', text)

def generate_hugo_content(release, repo_name):
    """Generate Hugo markdown content for a release with minimal processing"""
    # Format release date
    release_date = datetime.strptime(release['published_at'], "%Y-%m-%dT%H:%M:%SZ")
    formatted_date = release_date.strftime("%Y-%m-%dT%H:%M:%SZ")

    # Extract version number
    version = release['tag_name']

    # Create the Hugo front matter
    content = f"""+++
tags = ['{repo_name}']
categories = ['release']
title = "{version}"
date = "{formatted_date}"
url = "docs/releases/{repo_name}/{version}/"
description = "Release notes for {repo_name} {version}"
+++

## Release Notes

Version [{version}]({release['html_url']})

"""

    # Add the release body with minimal processing
    body = release['body'] if release['body'] else ""

    # Clean up the body text
    # Remove any ref to 'Release Notes:' or '# Release Notes:' since we add that ourselves
    body = re.sub(r'^#+\s*Release Notes:.*?\n', '', body, flags=re.IGNORECASE | re.MULTILINE)

    # Remove duplicate version headings (h1) since version is already in front matter title
    body = re.sub(r'^#+\s*' + re.escape(version) + r'\s*\n', '', body, flags=re.MULTILINE)

    # Remove "Changelog" headings (any level) with following newlines
    body = re.sub(r'^#+\s*Changelog\s*\n+', '', body, flags=re.IGNORECASE | re.MULTILINE)

    # Remove auto-generated changelog footers
    body = re.sub(r'\n*\\\?\*\s*\*?This\s+Changelog.*generated.*\*.*$', '', body, flags=re.IGNORECASE | re.MULTILINE)

    # Convert h3 headings to h2 to fix heading increment issues (h1 in title -> h2 next)
    body = re.sub(r'^### ', '## ', body, flags=re.MULTILINE)

    # Link GitHub usernames
    body = link_github_users(body)

    # Add the cleaned body
    content += body.strip() + "\n"

    return content

def main():
    parser = argparse.ArgumentParser(description='Generate Hugo markdown files from GitHub releases with minimal processing')
    parser.add_argument('--repo', required=True, help='Repository name (e.g., syft, grype). Always uses anchore/<repo>')
    parser.add_argument('--token', help='GitHub API token for authentication')
    parser.add_argument('--output-dir', required=True, help='Directory to save the Hugo markdown files')
    parser.add_argument('--limit', type=int, help='Limit the number of releases to process')
    parser.add_argument('--weight', type=int, default=10, help='Weight for the _index.md front matter (default: 10)')
    args = parser.parse_args()

    repo_name = args.repo
    repo_full = f"anchore/{repo_name}"

    # Create output directory if it doesn't exist
    os.makedirs(args.output_dir, exist_ok=True)

    # Fetch releases
    print(f"Fetching releases from {repo_full} on GitHub...")
    releases = fetch_releases(repo_full, token=args.token, limit=args.limit)
    print(f"Found {len(releases)} releases")

    # Process each release
    for release in releases:
        if release.get('draft'):
            print(f"Skipping draft release: {release['tag_name']}")
            continue

        # Create filename
        filename = f"{release['tag_name']}.md"
        filepath = os.path.join(args.output_dir, filename)

        if os.path.exists(filepath):
            print(f"Skipping existing release: {release['tag_name']} (already exists)")
            continue

        print(f"Processing release: {release['tag_name']}")

        # Generate Hugo content
        content = generate_hugo_content(release, repo_name)

        # Write the file
        with open(filepath, 'w') as f:
            f.write(content)

        print(f"Created {filepath}")

    # After processing releases, update _index.md in the output directory
    # List the most recent 10 releases (sorted by version tag, descending)
    try:
        from packaging.version import parse as parse_version
        
        release_tags = [release['tag_name'] for release in releases if not release.get('draft')]
        # Only include releases that were not skipped due to existing file
        release_tags = [tag for tag in release_tags if os.path.exists(os.path.join(args.output_dir, f"{tag}.md"))]
        # Sort tags by semantic version (if possible), otherwise by string
        release_tags_sorted = sorted(release_tags, key=lambda v: parse_version(v), reverse=True)
        latest_10 = release_tags_sorted[:10]
        
        # Compose _index.md front matter and list
        repo_tag = repo_name
        repo_title = repo_name.capitalize()
        index_md = f"""+++
tags = ['{repo_tag}']
categories = ['release']
title = \"{repo_title} Release Notes\" 
linkTitle = \"{repo_title}\"
url = \"docs/releases/{repo_name}\"
description = \"Anchore {repo_title} Release Notes\"
weight = {args.weight}
+++
\n"""
        for tag in latest_10:
            index_md += f"- [{tag}](./{tag}/)\n"
        # Write _index.md
        with open(os.path.join(args.output_dir, '_index.md'), 'w') as f:
            f.write(index_md)
    except ImportError:
        print("Warning: packaging.version not available. Skipping _index.md generation.")

    print("Done!")

if __name__ == "__main__":
    main()
