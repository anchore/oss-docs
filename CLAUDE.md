# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Architecture Overview

This is a Hugo-based documentation site for Anchore's open source tools (Syft, Grype, Grant, etc.) built with the Docsy theme. The site generates static documentation from Markdown files and includes automated release notes generation.

**Key Components:**

- **Hugo Configuration**: `hugo.toml` - defines site structure, theme settings, and deployment configuration
- **Content Structure**: `content/docs/` - organized into sections (installation, contributing, releases, reference)
- **Theme**: Uses Docsy theme with custom CSS (`static/css/custom.css`)
- **Release Management**: Automated scripts in `src/` for generating release notes from GitHub
- **PostCSS Pipeline**: Uses Autoprefixer for CSS processing

**Content Organization:**

- `content/docs/installation/` - Installation guides for each tool
- `content/docs/contributing/` - Contribution guides per project
- `content/docs/releases/` - Auto-generated release notes organized by project
- `content/docs/reference/` - Command reference documentation
- `content/docs/about/` - General information, adopters, team info

## Development Commands

**Build and Serve:**

```bash
hugo server          # Start development server with live reload
hugo                 # Build static site to public/
hugo --minify        # Build production-ready minified site
```

**CSS Processing:**

```bash
npx postcss --use autoprefixer --dir css/ --ext css css/*.css  # Process CSS files
```

**Release Notes Generation:**

```bash
./src/generate-release-notes.sh                           # Generate all release notes
python src/release-to-hugo.py --repo <repo> --output-dir content/docs/releases/<repo> --weight <num>
```

**Adopters Info Update:**

```bash
pip install requests packaging
./src/generate-adopters-info.sh                          # Update adopters page
```

## Documentation Authoring with AI Agents

This repository uses AI agents to assist with creating high-quality documentation.
See `AGENTS.md` for a quick overview or `DEVELOPING.md` for detailed workflows.

**Slash Commands:**

- `/doc:new` - Create new documentation with agent assistance
- `/doc:refine` - Improve existing documentation for style and accuracy
- `/doc:add-snippet` - Generate real code examples from tool execution
- `/doc:fact-check` - Validate technical claims against source code
- `/doc:style-check` - Check style guide compliance

All agents are defined in `.claude/agents/` and work as Claude Code subagents via the Task tool.

## Content Creation Guidelines

Follow the style guide in `content/docs/about/style-guide.md`:

- Use American spelling and sentence case for headings
- Address readers directly with "you" rather than "we" or "the user"
- Use active voice and simple present tense
- Keep sentences short and clear
- Use `code style` for filenames, commands, and field names
- Use **bold** for UI elements
- Use angle brackets for placeholders: `<your-value>`

**Front Matter Template:**

```yaml
+++
title = "Page Title"
description = "Brief description for SEO"
weight = 10          # Controls menu ordering
type = "docs"
url = "docs/section/page"  # Optional custom URL
+++
```

## File Structure Notes

- `archetypes/` contains content templates
- `static/` contains assets (images, CSS, etc.)
- `themes/docsy/` is the Hugo theme (Git submodule)
- `public/` is the generated site output (not tracked)
- Release note files follow naming: `content/docs/releases/<tool>/v<version>.md`

## Hugo Configuration Details

- **Base URL**: <https://oss.anchore.com/>
- **Theme**: Docsy with custom configurations
- **Features**: GitInfo enabled, sidebar search, dark mode toggle
- **Menu Structure**: Defined in `hugo.toml` with FontAwesome icons
- **Sitemap**: Auto-generated as `sitemap.xml`
