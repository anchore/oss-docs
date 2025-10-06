---
description: Validate documentation accuracy using the accuracy-validator agent (project)
---

You are running a standalone fact-check on documentation for Anchore OSS tools.

## Purpose

Quickly validate that documentation makes accurate technical claims by cross-referencing against source code in `../syft`, `../grype`, and `../grant`.

## Workflow

This is a lightweight wrapper around the `accuracy-validator` agent with user prompts for input and output preferences.

## Step-by-Step Instructions

### Step 1: User Prompt - Which Document

**Check if file is open in editor:**
If a file is currently open and it's a markdown file in `content/docs/`:

```
Fact-check the currently open file?
content/docs/<path>/<filename>.md

(y/n):
```

**If no file open, or user says 'n':**

```
Which document should I fact-check?

Enter path (relative to repo root):
```

**Capture:** `<file-path>`

**Validate:** File exists and is markdown

### Step 2: User Prompt - Scope (Optional)

**Prompt user:**
```
Check specific claims only? (Enter patterns or 'all')

Examples:
- "all" - check everything (default)
- "CLI flags" - only check flag descriptions
- "default values" - only check defaults
- "configuration" - only check config options

Enter scope (or press Enter for 'all'):
```

**Capture:** `<scope>` (default to 'all' if empty)

### Step 3: User Prompt - Output Format

**Prompt user:**
```
How should I present results?

1. Summary only (counts + critical issues)
2. Detailed report (all findings + source references)
3. Interactive (prompt for each issue)

Enter choice (1/2/3):
```

**Capture:** `<output-format>`

### Step 4: Run Fact Check

**Detect tool from file path or content:**
- Path contains "syft" → Syft
- Path contains "grype" → Grype
- Path contains "grant" → Grant
- Otherwise, scan content for tool keywords

**Launch accuracy-validator:**

Use the Task tool with:
- Agent: `accuracy-validator`
- Prompt:
  ```
  Fact-check documentation against source code.

  File to check: <file-path>
  Tool: <detected-tool>
  Scope: <scope>

  Read documentation from: <file-path>

  Search source code in:
  - ../syft/ (if Syft)
  - ../grype/ (if Grype)
  - ../grant/ (if Grant)

  Verify all technical claims:
  - CLI flags (names, descriptions, defaults)
  - Configuration options (fields, types, defaults)
  - Behavior descriptions
  - Feature availability
  - Code examples and outputs

  <If scope != 'all'>
  Focus only on claims related to: <scope>
  </If>

  Report findings with:
  - Source code references (file:line)
  - Exact quotes from documentation
  - Corrections needed
  - Classification (accurate/inaccurate/unverifiable)

  Return your complete fact-check report.
  ```

**Wait for agent to complete.**

### Step 5: Present Results

**Parse the agent's report** to extract:
- Summary counts
- Critical issues (❌ inaccurate)
- Important issues (⚠️ partially accurate)
- Unverifiable claims (❓)

**Output based on format choice:**

#### Format 1: Summary Only

```
## Fact-Check Summary: <filename>

✅ Accurate: <count>
❌ Inaccurate: <count>
⚠️ Partially accurate: <count>
❓ Unverifiable: <count>

<If any inaccurate or partially accurate:>
Critical Issues:

### ❌ <Issue description>
Line <N>: <Quoted claim>
Should be: <Correction>
Source: <file:line>

<Repeat for each critical issue>

<If output-format==1 and there are more issues:>
For full details, run with option 2 (detailed report)
```

#### Format 2: Detailed Report

Show the complete report from the agent, including:
- All findings (accurate, inaccurate, unverifiable)
- Full source code references
- All corrections and suggestions

```
<Full agent report>

---

Next steps:
- Review findings above
- Apply corrections to: <file-path>
- Re-run fact-check to verify fixes
```

#### Format 3: Interactive

For each issue found, prompt user:

```
Issue <N> of <total>:

❌ [Line <N>] <Issue description>

Documentation states:
> <exact quote>

Source code shows:
<source code snippet from file:line>

Correction needed:
<what should be written>

Action:
1. Fix now (I'll update the file)
2. Skip (fix manually later)
3. Dismiss (not actually wrong)
4. Stop (exit interactive mode)

Enter choice (1/2/3/4):
```

**If user chooses 1:** Apply fix immediately using Edit tool

**If user chooses 2:** Continue to next issue

**If user chooses 3:** Mark as dismissed, continue

**If user chooses 4:** Exit, show summary of what was done

**After all issues:**
```
Interactive fact-check complete!

Fixed: <count>
Skipped: <count>
Dismissed: <count>

<If any fixed:>
Updated file: <file-path>
Review changes: git diff <file-path>
```

## Special Cases

### No Issues Found

```
✅ Fact-check passed!

All technical claims in <filename> are accurate and verified against source code.

Checked:
- <summary of what was verified>

Source verification:
- <tool> source: <repo path>
- Last verified: <timestamp>
```

### Unverifiable Claims

If many claims are unverifiable:

```
⚠️ Warning: <count> claims could not be verified

This may indicate:
- Feature documentation ahead of implementation
- Source code not available locally
- Claims about external systems/behavior

Unverifiable claims should be manually reviewed:
<List unverifiable claims>

Consider:
- Adding source code references
- Clarifying scope (what's documented vs implemented)
- Removing claims that can't be verified
```

### File Not Found or Invalid

```
❌ Error: Cannot fact-check this file

Reason: <specific issue>

Valid files for fact-checking:
- Markdown files (.md) in content/docs/
- Files documenting Syft, Grype, or Grant features
- Files with technical claims (CLI, config, behavior)

Try:
/doc:fact-check <path-to-valid-file>
```

## Implementation Notes

### Tool Detection

**From file path:**
```javascript
if (file_path.includes('/syft/')) return 'Syft'
if (file_path.includes('/grype/')) return 'Grype'
if (file_path.includes('/grant/')) return 'Grant'
```

**From content (if path doesn't reveal tool):**
```javascript
content = read(file_path)
if (/syft|SBOM|cataloger/i.test(content)) return 'Syft'
if (/grype|vulnerabilit|CVE/i.test(content)) return 'Grype'
if (/grant|attestation|policy/i.test(content)) return 'Grant'
```

### Scope Filtering

Pass scope to agent as guidance:
```
Focus only on claims related to: <scope>

For example, if scope is "CLI flags":
- Check flag names, descriptions, defaults
- Skip configuration, behavior, other claims
```

Agent should filter its analysis accordingly.

### Interactive Mode Edits

When applying fixes in interactive mode:

1. Find exact line in file
2. Use Edit tool to replace with correction
3. Confirm change to user
4. Continue to next issue

```bash
# Pseudo-code for fix
original_line = extract_line(file_path, line_number)
corrected_line = apply_correction(original_line, correction)

Edit(
  file_path=file_path,
  old_string=original_line,
  new_string=corrected_line
)
```

## Usage Examples

**Quick summary check:**
```
User: /doc:fact-check
      [Prompted for file]
      content/docs/guides/grype/scanning.md
      [Prompted for scope]
      all
      [Prompted for format]
      1

Output: Summary with critical issues only
```

**Detailed review:**
```
User: /doc:fact-check
      [File auto-detected from editor]
      y
      [Scope]
      CLI flags
      [Format]
      2

Output: Full report of all CLI flag claims
```

**Interactive fixing:**
```
User: /doc:fact-check
      [File]
      content/docs/reference/syft/config.md
      [Scope]
      all
      [Format]
      3

Output: Interactive prompts for each issue, fixes applied
```

## Output Examples

**Summary format (option 1):**
```
## Fact-Check Summary: scanning.md

✅ Accurate: 12
❌ Inaccurate: 2
⚠️ Partially accurate: 1
❓ Unverifiable: 0

Critical Issues:

### ❌ Default value incorrect
Line 45: States default is "high", actually "medium"
Should be: Default severity threshold is "medium"
Source: ../grype/cmd/root.go:145

### ❌ Flag name wrong
Line 67: References --fail-severity, actual flag is --fail-on
Should be: Use the --fail-on flag to set severity threshold
Source: ../grype/cmd/root.go:145
```

**Interactive format (option 3):**
```
Issue 1 of 3:

❌ [Line 45] Default severity value incorrect

Documentation states:
> The default severity threshold is "high"

Source code shows:
// ../grype/cmd/root.go:145
rootCmd.Flags().StringP("fail-on", "", "medium", "set minimum severity")

Correction needed:
The default severity threshold is "medium"

Action:
1. Fix now (I'll update the file)
2. Skip (fix manually later)
3. Dismiss (not actually wrong)
4. Stop (exit interactive mode)

Enter choice (1/2/3/4):
```

## Tips for Users

1. **Run regularly:** Fact-check docs when source code changes
2. **Use scope:** Focus on specific areas for faster checks
3. **Interactive mode:** Best for fixing issues immediately
4. **Summary mode:** Best for quick health checks
5. **Detailed mode:** Best for comprehensive review before release

The goal is to ensure every technical claim in documentation is backed by source code evidence.