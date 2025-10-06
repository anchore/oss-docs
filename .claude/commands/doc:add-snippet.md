---
description: Generate real code snippets using the snippet-generator agent (project)
---

You are generating real, working code snippets for Anchore OSS documentation.

## Purpose

Quickly create authentic code examples by executing actual tools (Syft, Grype, Grant) and capturing real output.

## Workflow

This is a wrapper around the `snippet-generator` agent with user prompts for specifying what example is needed and where to place it.

## Step-by-Step Instructions

### Step 1: User Prompt - What Example

**Prompt user:**
```
What code example do you need?

Examples:
- "Scan Alpine image with Syft showing JSON output"
- "Grype scanning with --fail-on critical"
- "Using jq to filter SBOM by package type"
- "Custom Syft template for package listing"

Describe the example:
```

**Capture:** `<description>`

### Step 2: Tool Detection

**Auto-detect tool from description:**
- Keywords: "syft", "sbom", "cataloger" → Syft
- Keywords: "grype", "vulnerability", "scan", "cve" → Grype
- Keywords: "grant", "attestation", "policy" → Grant
- Keywords: "jq", "filter", "query", "parse" → jq (requires SBOM from Syft first)

**Prompt for confirmation:**
```
This requires running [<detected-tool>]. Correct? (y/n)
```

If user says no:
```
Which tool? (syft/grype/grant/jq/other)
```

**Capture:** `<tool>`

### Step 3: User Prompt - Output Format

**Prompt user:**
```
What format for the output?

1. Command + output (full example)
2. Command only (no output)
3. Output only (no command)
4. Custom (specify)

Enter choice (1/2/3/4):
```

**If choice is 4:**
```
Describe custom format:
```

**Capture:** `<output-format>` and optional `<custom-format-description>`

### Step 4: User Prompt - Placement

**Prompt user:**
```
Where should I put this snippet?

1. Print to console (copy/paste)
2. Insert at cursor (if file open in editor)
3. Save to file (specify path)
4. Add to snippet library (data/*/examples/)

Enter choice (1/2/3/4):
```

**If choice is 3:**
```
Enter file path (relative to repo root):
```

**If choice is 4:**
```
Snippet library detected: data/<tool>/examples/

Enter filename (will add .yaml/.json):
```

**Capture:** `<placement>` and optional `<placement-path>`

### Step 5: Generate Snippet

**Launch snippet-generator:**

Use the Task tool with:
- Agent: `snippet-generator`
- Prompt:
  ```
  Generate a real, working code snippet.

  Description: <description>
  Tool: <tool>
  Output format: <output-format>
  <If custom format:>
  Custom format: <custom-format-description>
  <End if>

  Execute the actual tool to generate authentic examples:

  <If tool is Syft:>
  - Run: docker run --rm anchore/syft:latest <image> -o <format>
  - Use images like: alpine:3.18, node:18-alpine, python:3.11-slim
  - Capture real output
  <End if>

  <If tool is Grype:>
  - Run: docker run --rm anchore/grype:latest <image> -o <format>
  - Use images like: alpine:3.10, ubuntu:18.04 (for known CVEs)
  - Capture real vulnerability output
  <End if>

  <If tool is Grant:>
  - Run: docker run --rm anchore/grant:latest <command>
  - Capture real attestation/policy output
  <End if>

  <If tool is jq:>
  - First generate SBOM: syft <image> -o json
  - Then apply jq query: cat sbom.json | jq '<query>'
  - Show both steps
  <End if>

  Format the snippet according to: <output-format>

  <If format is "Command + output" (1):>
  Show:
  \`\`\`bash
  $ <command>
  <output>
  \`\`\`
  <End if>

  <If format is "Command only" (2):>
  Show:
  \`\`\`bash
  <command>
  \`\`\`
  <End if>

  <If format is "Output only" (3):>
  Show:
  \`\`\`<format>
  <output>
  \`\`\`
  <End if>

  Return the complete, formatted snippet ready to use in documentation.
  ```

**Wait for agent to complete.**

### Step 6: Process Snippet Based on Placement

**Extract the generated snippet from agent response.**

#### Placement 1: Print to Console

**Display snippet:**
```
## Generated Snippet

<Show the complete snippet>

---

Copy the snippet above and paste it into your documentation.

<If the snippet includes commands:>
To verify, you can run:
<command to execute>
<End if>
```

#### Placement 2: Insert at Cursor

**Check if file is open in editor and cursor position is available.**

**If yes:**
```
Inserting snippet at cursor position in <filename>...

<Use Edit tool to insert snippet at cursor location>

✅ Snippet inserted!

Location: <filename>:<line>
Review: git diff <filename>
```

**If no file open:**
```
No file currently open in editor.

The snippet has been generated:

<Show snippet>

Options:
- Copy and paste manually
- Or specify file with /doc:add-snippet option 3
```

#### Placement 3: Save to File

**Append or insert snippet into specified file:**

```
Adding snippet to: <placement-path>

<Read file, determine best insertion point, use Edit or Write tool>

✅ Snippet saved!

Location: <placement-path>
Preview:
<Show snippet in context>

Review: git diff <placement-path>
```

#### Placement 4: Add to Snippet Library

**Determine library path:**
- Syft → `data/syft/examples/`
- Grype → `data/grype/examples/`
- Grant → `data/grant/examples/`

**Create library file:**
```yaml
---
description: <description>
tool: <tool>
created: <timestamp>
---

command: |
  <command>

output: |
  <output>

notes: |
  <Any notes about the example>
```

**Save and confirm:**
```
✅ Snippet added to library!

Location: data/<tool>/examples/<filename>.yaml

This snippet can now be referenced in documentation:
{{< snippet "<tool>/<filename>" >}}

Or included directly:
<Show how to use the library file>
```

## Special Cases

### Tool Not Available

If Docker or the tool isn't available:

```
⚠️ Warning: Cannot execute <tool>

Reason: <specific issue>

Options:
1. Install/start Docker and retry
2. Use existing script (if available): scripts/generate-<type>-examples.sh
3. Generate example from source code (without real execution)

What would you like to do? (1/2/3)
```

### Command Fails

If the tool execution fails:

```
❌ Command failed: <command>

Error:
<error output>

This might be because:
- Image not available
- Invalid flags/options
- Tool version issue

Suggestions:
- Try different image: <alternative>
- Adjust command: <suggested fix>
- Check tool version

Retry with suggested fix? (y/n)
```

### Output Too Large

If output is very long:

```
⚠️ Output is large (<size> lines)

Options:
1. Truncate to first N lines with "..."
2. Show summary only
3. Save full output to file
4. Keep full output (might be hard to read in docs)

Enter choice (1/2/3/4):
```

## Implementation Notes

### Tool Execution

**Use Docker for consistency:**
```bash
# Syft
docker run --rm anchore/syft:latest <image> -o <format>

# Grype
docker run --rm anchore/grype:latest <image> -o <format>

# Grant
docker run --rm anchore/grant:latest <command>
```

**Fallback to existing scripts:**
```bash
# jq examples
./scripts/generate-jq-examples.sh

# Template examples
python scripts/generate-template-examples.py --template <template>
```

### Image Selection

**Choose appropriate images:**
- **Small/fast:** alpine:3.18, alpine:latest
- **Common packages:** node:18-alpine, python:3.11-slim
- **Known vulnerabilities:** alpine:3.10, ubuntu:18.04
- **Specific use case:** nginx:alpine, postgres:14-alpine

### Output Formatting

**Command + output (format 1):**
```markdown
\`\`\`bash
$ syft alpine:3.18 -o json | jq '.artifacts | length'
14
\`\`\`
```

**Command only (format 2):**
```markdown
\`\`\`bash
syft alpine:3.18 -o spdx-json > sbom.spdx.json
\`\`\`
```

**Output only (format 3):**
```markdown
\`\`\`json
{
  "artifacts": [
    {
      "name": "alpine-baselayout",
      "version": "3.4.3-r1",
      "type": "apk"
    }
  ]
}
\`\`\`
```

### Insertion Point Detection

**When inserting at cursor:**
1. Get current file and cursor position
2. Read surrounding context
3. Determine if snippet should be:
   - Inline (in existing paragraph)
   - New section (after current heading)
   - Code block (replace or insert)

**When saving to file:**
1. Read file content
2. Find best section for snippet:
   - Look for "Examples" section
   - Look for related content
   - Append to end if no good spot
3. Insert with appropriate context

### Library File Format

**YAML template for snippet library:**
```yaml
---
description: <one-line description>
tool: <syft|grype|grant>
category: <basic|intermediate|advanced>
tags: [<tag1>, <tag2>]
created: <ISO-8601 timestamp>
---

# <Title>

<Optional explanation>

## Command

\`\`\`bash
<command>
\`\`\`

## Output

\`\`\`<format>
<output>
\`\`\`

## Notes

- <Note 1>
- <Note 2>
```

## Usage Examples

**Quick console snippet:**
```
User: /doc:add-snippet
      [Description]
      Scan Alpine image with Syft JSON output
      [Tool]
      y (Syft)
      [Format]
      1 (Command + output)
      [Placement]
      1 (Console)

Output: Formatted snippet printed to console
```

**Insert at cursor:**
```
User: /doc:add-snippet
      [Description]
      Grype scan with severity threshold
      [Tool]
      y (Grype)
      [Format]
      1 (Command + output)
      [Placement]
      2 (Insert at cursor)

Output: Snippet inserted into open file at cursor
```

**Save to snippet library:**
```
User: /doc:add-snippet
      [Description]
      jq query to filter packages by type
      [Tool]
      n → jq
      [Format]
      1 (Command + output)
      [Placement]
      4 (Snippet library)
      [Filename]
      filter-by-type

Output: Saved to data/syft/examples/filter-by-type.yaml
```

## Output Examples

**Console output (placement 1):**
```
## Generated Snippet

\`\`\`bash
$ syft alpine:3.18 -o json | jq '.artifacts | length'
14
\`\`\`

---

Copy the snippet above and paste it into your documentation.

To verify, you can run:
docker run --rm anchore/syft:latest alpine:3.18 -o json | jq '.artifacts | length'
```

**File insertion (placement 2):**
```
Inserting snippet at cursor position in guides/syft/jq-queries.md...

✅ Snippet inserted!

Location: content/docs/guides/syft/jq-queries.md:45
Review: git diff content/docs/guides/syft/jq-queries.md
```

**Library addition (placement 4):**
```
✅ Snippet added to library!

Location: data/syft/examples/filter-by-type.yaml

This snippet can now be referenced in documentation:
{{< snippet "syft/filter-by-type" >}}

Or view the file:
cat data/syft/examples/filter-by-type.yaml
```

## Tips for Users

1. **Be specific:** Clear descriptions get better examples
2. **Verify output:** Always check that generated examples are current
3. **Use library:** Build reusable snippet collection for common examples
4. **Real execution:** Snippets from actual tool runs are always accurate
5. **Update regularly:** Re-run snippet generation when tools are updated

The goal is to provide users with real, working examples they can copy, paste, and run immediately.