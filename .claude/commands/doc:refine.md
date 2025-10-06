---
description: Refine existing documentation using multiple specialized agents (project)
---

You are orchestrating the refinement of existing documentation for Anchore OSS tools using a multi-agent workflow.

## Workflow Overview

This slash command coordinates specialized agents through a 6-step process:
1. Session setup + file selection (you)
2. Parallel analysis: structure + accuracy (structure-guide + accuracy-validator)
3. Snippet refresh (snippet-generator, conditional)
4. Apply improvements (doc-writer)
5. Style check (doc-style-checker)
6. Finalization (you)

All artifacts are saved to `draft/<session-id>/` for transparency.

## Step-by-Step Instructions

### Step 1: User Prompt - Which Document

**Check if file is open in editor:**
If a file is currently open and it's a markdown file in `content/docs/`:

```
Refine the currently open file?
content/docs/<path>/<filename>.md

(y/n):
```

**If no file open, or user says 'n':**

```
Which document should I refine?

Enter path (relative to repo root):
```

**Capture:** `<file-path>`

**Validate:** File exists and is markdown

### Step 2: Refinement Scope

**Prompt user:**
```
What should I focus on?

1. Everything (structure, facts, snippets, style)
2. Only fact-checking and accuracy
3. Only style and readability
4. Only code examples/snippets
5. Structure and organization only

Enter choice (1/2/3/4/5):
```

**Capture:** `<scope>`

**Map to agents:**
- 1 → all agents
- 2 → accuracy-validator only
- 3 → doc-style-checker only
- 4 → snippet-generator only
- 5 → structure-guide only

### Step 3: Session Setup

**Create session directory:**
```bash
session_id=$(date +%Y%m%d-%H%M%S)-refine-<filename>
mkdir -p draft/$session_id
```

**Copy original file:**
```bash
cp <file-path> draft/$session_id/00-original.md
```

**Write session info:**
```markdown
---
session: <session-id>
created: <ISO-8601 timestamp>
---

# Documentation Refinement: <filename>

## Request Details

**Original file:** <file-path>

**Scope:** <scope description>

**Agents to run:**
<list based on scope>

## Session Directory

This directory contains artifacts from each refinement step.

### Artifacts
- `00-original.md` - Original document
- `01-structure-check.md` - Structure validation (structure-guide)
- `02-fact-check.md` - Accuracy validation (accuracy-validator)
- `03-snippet-refresh.md` - Updated examples (snippet-generator)
- `04-improved-draft.md` - Document with improvements (doc-writer)
- `05-style-report.md` - Style compliance check (doc-style-checker)
- `06-final-draft.md` - Ready to replace original
```

**Save to:** `draft/<session-id>/00-session-info.md`

### Step 4: Parallel Analysis (structure-guide + accuracy-validator)

**Launch both agents in parallel using a single message with multiple Task tool calls:**

**Note:** Only launch agents included in the user's scope choice.

**Agent 1: structure-guide** (if scope includes structure)
- Prompt:
  ```
  Validate document structure.

  Session: <session-id>

  Read documentation from: draft/<session-id>/00-original.md

  Check:
  - Heading hierarchy (H1 → H2 → H3)
  - Section organization and flow
  - Content placement
  - Missing essential sections
  - Logical ordering

  Write validation report to: draft/<session-id>/01-structure-check.md

  Follow the structure validation report format specified in your instructions.
  ```

**Agent 2: accuracy-validator** (if scope includes accuracy)
- Prompt:
  ```
  Validate documentation accuracy.

  Session: <session-id>

  Read documentation from: draft/<session-id>/00-original.md

  Detect tool from content (Syft/Grype/Grant) and search source code in:
  - ../syft/
  - ../grype/
  - ../grant/

  Verify:
  - CLI flags, descriptions, defaults
  - Configuration fields
  - Behavior claims
  - Version requirements
  - Code examples

  Write fact-check report to: draft/<session-id>/02-fact-check.md

  Follow the fact-check report format specified in your instructions.
  ```

**Wait for both agents to complete.**

### Step 5: Review Analysis (user prompt)

**Show combined summary:**

Read both reports (if they exist based on scope) and extract summaries.

**Prompt user:**
```
## Analysis Complete

Structure Issues:
- Critical: <count> 🔴
- Important: <count> 🟡
- Minor: <count> 🔵

Accuracy Issues:
- Inaccurate: <count> ❌
- Partially accurate: <count> ⚠️
- Unverifiable: <count> ❓

Reports:
- draft/<session-id>/01-structure-check.md
- draft/<session-id>/02-fact-check.md

Review detailed reports? (y/n/skip)
```

**If 'y':** Display full reports (or open in editor)

### Step 6: Snippet Refresh (snippet-generator)

**Determine if snippets need refresh:**

From fact-check report, identify:
- Outdated command examples
- Incorrect output formats
- Missing examples

**If snippets need refresh (or scope=4):**

**Launch snippet-generator:**

Use the Task tool with:
- Agent: `snippet-generator`
- Prompt:
  ```
  Refresh code snippets and examples.

  Session: <session-id>

  Read documentation from: draft/<session-id>/00-original.md
  Read fact-check report from: draft/<session-id>/02-fact-check.md (if exists)

  Generate fresh examples by:
  - Running actual tools via Docker
  - Executing scripts (generate-jq-examples.sh, etc.)
  - Capturing real, current output

  Update or create examples for:
  - Commands with outdated output
  - Missing examples identified
  - Incorrect format examples

  Write examples to: draft/<session-id>/03-snippet-refresh.md

  Follow the snippet artifact format specified in your instructions.
  ```

**Wait for agent to complete.**

**If no snippet refresh needed:**
```
Snippet refresh: Not needed (all examples current)
```

### Step 7: Apply Improvements (doc-writer)

**Launch doc-writer in revision mode:**

Use the Task tool with:
- Agent: `doc-writer`
- Prompt:
  ```
  Apply improvements to documentation.

  Session: <session-id>

  Read inputs from:
  - draft/<session-id>/00-original.md (current document)
  - draft/<session-id>/01-structure-check.md (structure issues) [if exists]
  - draft/<session-id>/02-fact-check.md (accuracy issues) [if exists]
  - draft/<session-id>/03-snippet-refresh.md (updated examples) [if exists]

  Apply improvements:
  - Fix structure issues (reorder sections, fix headings)
  - Correct factual errors
  - Integrate updated snippets
  - Maintain overall content and meaning
  - Preserve front matter

  Write improved document to: draft/<session-id>/04-improved-draft.md

  Follow the revision artifact format specified in your instructions.
  ```

**Wait for agent to complete.**

### Step 8: Style Check (doc-style-checker)

**Launch doc-style-checker:**

Use the Task tool with:
- Agent: `doc-style-checker`
- Prompt:
  ```
  Check documentation for style guide compliance.

  Session: <session-id>

  Read documentation from: draft/<session-id>/04-improved-draft.md
  Read style guide from: content/docs/about/style-guide.md

  Check for:
  - Voice: Active not passive
  - Tense: Present not future
  - Audience: "you" not "we"/"the user"
  - Formatting: code, bold, placeholders
  - Capitalization: sentence case for headings
  - Brand names: correct capitalization

  Write style report to: draft/<session-id>/05-style-report.md

  Follow the style report format specified in your instructions.
  ```

**Wait for agent to complete.**

### Step 9: Finalization

**Apply style fixes:**

Read both:
- `draft/<session-id>/04-improved-draft.md`
- `draft/<session-id>/05-style-report.md`

Apply critical style fixes (🔴) automatically. For important/minor fixes, apply if straightforward.

**Write final draft:**

Save to `draft/<session-id>/06-final-draft.md` with all corrections applied.

### Step 10: Show Diff and Confirm (user prompt)

**Generate diff:**
```bash
diff -u <original-file-path> draft/<session-id>/06-final-draft.md > draft/<session-id>/changes.diff
```

**Show summary of changes:**
```
## Refinement Complete!

Changes made:
- Lines added: <count>
- Lines removed: <count>
- Lines modified: <count>

Key improvements:
- <summary of structure fixes>
- <summary of accuracy fixes>
- <summary of snippet updates>
- <summary of style fixes>

View diff: draft/<session-id>/changes.diff
Final version: draft/<session-id>/06-final-draft.md
```

**Show preview of diff** (first 50 lines or so)

**Prompt user:**
```
Apply these changes?

1. Replace original file (<file-path>)
2. Save as new file (specify path)
3. Keep in draft/ for manual review

Enter choice (1/2/3):
```

**If 1:**
```bash
cp draft/<session-id>/06-final-draft.md <original-file-path>
```
```
✅ Original file updated!

Updated: <file-path>
Session artifacts: draft/<session-id>/

Next steps:
- Review changes: git diff <file-path>
- Run linter: npm run lint
- Commit when ready
```

**If 2:**
```
Enter new file path (relative to repo root):
```
Then copy to specified path.

**If 3:**
```
✅ Refinement complete!

Final version: draft/<session-id>/06-final-draft.md
Original preserved: <file-path>
Session artifacts: draft/<session-id>/

You can manually apply changes:
cp draft/<session-id>/06-final-draft.md <file-path>
```

## Scope-Specific Workflows

### Scope 2: Fact-checking only

**Steps:**
1. Session setup
2. Launch accuracy-validator only
3. Review fact-check report
4. Launch doc-writer to apply fact corrections
5. Finalize and show diff

**Skip:** structure-guide, snippet-generator, doc-style-checker

### Scope 3: Style only

**Steps:**
1. Session setup
2. Launch doc-style-checker only
3. Apply style fixes
4. Finalize and show diff

**Skip:** structure-guide, accuracy-validator, snippet-generator, doc-writer

### Scope 4: Snippets only

**Steps:**
1. Session setup
2. Launch snippet-generator only
3. Launch doc-writer to integrate snippets
4. Finalize and show diff

**Skip:** structure-guide, accuracy-validator, doc-style-checker

### Scope 5: Structure only

**Steps:**
1. Session setup
2. Launch structure-guide only
3. Review structure report
4. Launch doc-writer to fix structure
5. Finalize and show diff

**Skip:** accuracy-validator, snippet-generator, doc-style-checker

## Implementation Notes

### Session ID Format
```
YYYYMMDD-HHMMSS-refine-<filename>

Example: 20250103-143022-refine-installation
```

### Filename Extraction
```javascript
// From path: content/docs/guides/syft/installation.md
filename = path.split('/').pop().replace('.md', '')
// Result: installation
```

### Parallel Execution

Step 4 MUST execute agents in parallel when scope=1:
- Use single message with two Task tool calls
- Don't wait for first to finish before launching second
- Both agents read same input (00-original.md)
- They write to different outputs (01, 02)

### Diff Display

Show meaningful context:
```diff
--- original
+++ improved
@@ -10,7 +10,7 @@
 ## Installation

-The user can install Syft using Homebrew.
+Install Syft using Homebrew:

 ```bash
-$ brew install syft
+brew install syft
 ```
```

### Error Handling

**If no changes needed:**
```
✅ No improvements needed!

This documentation already meets quality standards:
- Structure: ✅ Good
- Accuracy: ✅ Verified
- Snippets: ✅ Current
- Style: ✅ Compliant

Session artifacts: draft/<session-id>/ (for reference)
```

**If agent fails:**
1. Show error, preserve partial work
2. Offer to skip that agent
3. Continue with other agents
4. Final draft includes what was possible

## Tips for Success

1. **Choose scope wisely:** Full refinement takes longer but is thorough
2. **Review reports:** Understanding issues helps with future docs
3. **Check diff carefully:** Ensure changes preserve meaning
4. **Keep original safe:** Always have backup (in draft/)
5. **Iterate if needed:** Can run again with different scope

The goal is to improve documentation by:
- ✅ Fixing structural issues (better flow)
- ✅ Correcting factual errors (source truth)
- ✅ Updating examples (current, working)
- ✅ Enforcing style (consistency)
- ✅ Preserving author's intent (not rewriting)