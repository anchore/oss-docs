# Developing

This guide helps documentation authors and contributors create documentation for Anchore's open source tools in a consistent manner (Syft, Grype, Grant, etc.).

## AI Tooling

Use these slash commands with claude code:

| Command            | Purpose                  | Agent Used                                             |
| ------------------ | ------------------------ | ------------------------------------------------------ |
| `/doc:new`         | Create new documentation | doc-writer                                             |
| `/doc:refine`      | Improve existing docs    | doc-style-checker, accuracy-validator, structure-guide |
| `/doc:add-snippet` | Generate code examples   | snippet-generator                                      |
| `/doc:fact-check`  | Verify accuracy          | accuracy-validator                                     |
| `/doc:style-check` | Check style compliance   | doc-style-checker                                      |

### Agent Definitions

| Agent                  | Purpose                         | When to Use                                               |
| ---------------------- | ------------------------------- | --------------------------------------------------------- |
| **doc-writer**         | Create new content from scratch | Starting a new documentation page                         |
| **snippet-generator**  | Generate real code examples     | Need working CLI outputs, jq queries, or config examples  |
| **accuracy-validator** | Verify technical claims         | Want to ensure documentation matches actual tool behavior |
| **doc-style-checker**  | Check style guide compliance    | Want consistent tone, voice, and formatting               |
| **structure-guide**    | Validate document organization  | Need help with heading hierarchy, links, and sections     |

All agents are located in `.claude/agents/` and work as Claude Code subagents via the Task tool.

## Common Workflows

### Creating a New User Guide

1. **Start the workflow:**

   ```
   /doc:new
   ```

2. **Answer discovery questions:**
   - What feature/topic to document?
   - Who's the audience (beginners, advanced)?
   - Any specific use case?

3. **Review proposed structure:**
   - Agent proposes file location
   - Agent suggests document outline
   - Agent generates front matter

4. **Review initial draft:**
   - Agent generates content following style guide
   - Agent includes working examples
   - Agent suggests internal links

5. **Validate accuracy:**
   - Agent checks claims against source code
   - Agent identifies snippet opportunities

6. **Refine if needed:**
   - Use `/doc:refine` for improvements
   - Use `/doc:style-check` for final polish

### Improving Existing Documentation

1. **Run refinement:**

   ```
   /doc:refine
   ```

2. **Specify the file:**

   ```
   content/docs/guides/sbom/catalogers.md
   ```

3. **Review suggestions:**
   - Style issues (voice, tone, formatting)
   - Accuracy problems (outdated flags, wrong counts)
   - Structure improvements (missing sections, links)
   - Readability enhancements (sentence length, clarity)

4. **Apply changes:**
   - Review each suggestion critically
   - Apply what makes sense
   - Use your judgment for edge cases

### Generating Code Examples

1. **Request snippet generation:**

   ```
   /doc:add-snippet
   ```

2. **Describe what you need:**

   ```
   I need an example showing how to filter SBOM packages by type using jq.
   ```

3. **Agent determines approach:**
   - Checks if existing script can generate it
   - If yes: creates/updates YAML definition and runs script
   - If no: runs tool via Docker and captures output

4. **Agent provides:**
   - Generated snippet files
   - Hugo inclusion syntax
   - Command to regenerate

5. **Include in documentation:**

   ```markdown
   {{< readfile "guides/sbom/snippets/jq-queries/filter-by-type/query.md" >}}
   ```

### Validating Technical Accuracy

1. **Run validation:**

   ```
   /doc:fact-check
   ```

2. **Agent extracts claims:**
   - CLI flags and commands
   - Configuration options
   - Feature descriptions
   - Counts and numbers

3. **Agent cross-references source code:**
   - Checks ../syft, ../grype, ../grant repositories
   - Verifies cobra definitions, struct fields, implementations
   - Counts actual catalogers, matchers, etc.

4. **Review findings:**

   ```
   ✓ --output flag verified (cmd/syft/cli/commands/packages.go:45)
   ✗ catalog.filter not found in source - may be incorrect
   ✓ Count: 47 catalogers (claim "40+" is accurate)
   ```

5. **Update documentation based on findings**
