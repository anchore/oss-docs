---
description: Check documentation for style guide compliance using the doc-style-checker agent (project)
---

You are running a standalone style check on documentation for Anchore OSS tools.

## Purpose

Quickly validate that documentation follows the Anchore OSS style guide for voice, tone, formatting, and conventions.

## Workflow

This is a lightweight wrapper around the `doc-style-checker` agent with user prompts for input and output preferences.

## Step-by-Step Instructions

### Step 1: User Prompt - Which Document

**Check if file is open in editor:**
If a file is currently open and it's a markdown file in `content/docs/`:

```
Style-check the currently open file?
content/docs/<path>/<filename>.md

(y/n):
```

**If no file open, or user says 'n':**

```
Which document should I style-check?

Enter path (relative to repo root):
```

**Capture:** `<file-path>`

**Validate:** File exists and is markdown

### Step 2: User Prompt - Style Scope (Optional)

**Prompt user:**
```
Check for specific style issues? (Enter numbers or 'all')

1. Voice/tense (active voice, present tense)
2. Audience (use of 'you' vs 'we')
3. Formatting (code style, bold, placeholders)
4. Capitalization
5. Sentence complexity
all. Everything (default)

Enter scope (comma-separated numbers, 'all', or press Enter for 'all'):
```

**Capture:** `<scope>` (default to 'all' if empty)

**Parse scope:**
- "all" or empty → check everything
- "1,3,5" → check voice/tense, formatting, sentence complexity
- Single number → check that category only

### Step 3: User Prompt - Fix Mode

**Prompt user:**
```
How should I handle violations?

1. Report only (show issues, no changes)
2. Auto-fix safe issues (apply obvious fixes)
3. Interactive fix (prompt for each issue)

Enter choice (1/2/3):
```

**Capture:** `<fix-mode>`

### Step 4: Run Style Check

**Launch doc-style-checker:**

Use the Task tool with:
- Agent: `doc-style-checker`
- Prompt:
  ```
  Check documentation for style guide compliance.

  File to check: <file-path>
  Scope: <scope>

  Read documentation from: <file-path>
  Read style guide from: content/docs/about/style-guide.md

  Check for:
  <If scope includes voice/tense (1) or 'all':>
  - Voice: Active not passive
  - Tense: Present not future/conditional
  <End if>

  <If scope includes audience (2) or 'all':>
  - Audience: "you" not "we"/"the user"
  <End if>

  <If scope includes formatting (3) or 'all':>
  - Formatting: `code style` for filenames/commands, **bold** for UI
  - Placeholders: Use <angle-brackets>
  <End if>

  <If scope includes capitalization (4) or 'all':>
  - Capitalization: Sentence case for H2+ headings
  - Brand names: Correct capitalization (Syft, Grype, GitHub, Kubernetes)
  <End if>

  <If scope includes sentence complexity (5) or 'all':>
  - Sentence complexity: Short, simple sentences
  - Split complex sentences, use lists
  <End if>

  Report violations with:
  - Line numbers
  - Exact quotes
  - Specific corrections
  - Severity (🔴 critical / 🟡 important / 🔵 minor)

  Return your complete style report.
  ```

**Wait for agent to complete.**

### Step 5: Process Results Based on Fix Mode

**Parse the agent's report** to extract:
- Violation counts by severity
- Specific issues with line numbers
- Suggested fixes

#### Mode 1: Report Only

**Display full report:**

```
## Style Report: <filename>

Summary:
🔴 Critical: <count> (voice/tense/audience)
🟡 Important: <count> (formatting/brand names)
🔵 Minor: <count> (punctuation/capitalization)

Critical Issues (Fix Required) 🔴

### [Line <N>] Passive voice

**Current:**
> <exact quote>

**Should be:**
> <corrected version>

**Rule:** Use active voice rather than passive voice

---

<Repeat for all issues by severity>

---

Next steps:
- Fix issues manually in: <file-path>
- Or run with mode 2/3 to apply fixes automatically
```

#### Mode 2: Auto-fix Safe Issues

**Determine which fixes are "safe":**
- 🔴 Critical passive voice → Safe if simple transformation
- 🔴 Future tense → Safe ("will X" → "X")
- 🟡 Code formatting → Safe (add backticks)
- 🟡 Brand names → Safe (correct capitalization)
- 🔵 Minor issues → Safe if mechanical

**Not safe (need review):**
- Complex sentence restructuring
- Ambiguous "we" removal (might change meaning)
- Major rewording

**Apply safe fixes:**

For each safe fix:
1. Use Edit tool to apply correction
2. Track what was changed

**Show summary:**

```
## Auto-fix Complete: <filename>

Fixed automatically:
✅ <count> passive voice → active voice
✅ <count> future tense → present tense
✅ <count> missing code formatting
✅ <count> brand name capitalization

Manual review needed:
⚠️ <count> complex sentence restructuring
⚠️ <count> ambiguous audience references

Changes applied to: <file-path>

Review changes: git diff <file-path>

Remaining issues require manual attention:
<List non-safe issues>
```

#### Mode 3: Interactive Fix

**For each violation, prompt user:**

```
Issue <N> of <total>:

🔴 [Line <N>] <Issue type>

**Current:**
> <exact quote from documentation>

**Suggested fix:**
> <corrected version>

**Rule:** <style guide rule>

Action:
1. Apply this fix
2. Let me edit it differently
3. Skip (fix manually later)
4. Dismiss (not actually wrong)
5. Stop (exit interactive mode)

Enter choice (1/2/3/4/5):
```

**If user chooses 1:** Apply suggested fix using Edit tool

**If user chooses 2:**
```
Enter your preferred wording:
```
Then apply user's version using Edit tool

**If user chooses 3:** Continue to next issue

**If user chooses 4:** Mark as dismissed, continue

**If user chooses 5:** Exit, show summary

**After all issues:**

```
Interactive style check complete!

Applied: <count>
Edited: <count> (with custom wording)
Skipped: <count>
Dismissed: <count>

<If any changes:>
Updated file: <file-path>
Review changes: git diff <file-path>

<If any skipped:>
Skipped issues (fix manually):
- Line <N>: <issue type>
<Repeat>
```

## Special Cases

### No Violations Found

```
✅ Style check passed!

<filename> follows the Anchore OSS style guide perfectly.

Checked:
- Voice: Active ✅
- Tense: Present ✅
- Audience: Addresses reader directly ✅
- Formatting: Correct ✅
- Capitalization: Sentence case ✅
- Sentence complexity: Simple and clear ✅

Style guide: content/docs/about/style-guide.md
```

### Only Minor Issues

```
✅ Style check: Good!

<filename> has only minor style issues.

🔵 Minor Issues (<count>):
- Line <N>: <minor issue>

These don't affect readability significantly.
Fix when convenient or run mode 2/3 to auto-fix.
```

### File Not Found or Invalid

```
❌ Error: Cannot style-check this file

Reason: <specific issue>

Valid files for style-checking:
- Markdown files (.md) in content/docs/
- Documentation pages (not data files)

Try:
/doc:style-check <path-to-valid-file>
```

## Implementation Notes

### Safe Fix Detection

**Safe transformations:**

```javascript
// Passive to active
"can be configured" → "you can configure"
"is provided" → "provides" (if subject clear)

// Future to present
"will scan" → "scans"
"will generate" → "generates"

// Code formatting
"config.yaml" → "`config.yaml`"
"--flag" → "`--flag`"

// Brand names
"kubernetes" → "Kubernetes"
"github" → "GitHub"
```

**Not safe (need review):**

```javascript
// Ambiguous subject
"the user must..." → Could be "you must" or "configure" (imperative)

// Complex restructuring
"Because X, Y happens" → "X. Y happens." (might change meaning)

// Multiple issues in one sentence
Needs human judgment on best fix
```

### Scope Filtering

**Map scope numbers to checks:**
- 1 → Check voice (passive/active) and tense (present/future)
- 2 → Check audience ("you", "we", "the user")
- 3 → Check formatting (code, bold, placeholders)
- 4 → Check capitalization (headings, brand names)
- 5 → Check sentence complexity (length, lists)

Pass to agent:
```
Focus on: <list of checks based on scope>
Skip: <list of checks not in scope>
```

### Interactive Mode Edits

**Applying suggested fix:**
```javascript
line_content = extract_line(file_path, line_number)

// Find the exact text to replace (might be partial line)
old_text = find_matching_quote(line_content, current_quote)
new_text = suggested_fix

Edit(
  file_path=file_path,
  old_string=old_text,
  new_string=new_text
)
```

**Applying custom fix:**
```javascript
old_text = find_matching_quote(line_content, current_quote)
new_text = user_input

Edit(
  file_path=file_path,
  old_string=old_text,
  new_string=new_text
)
```

## Usage Examples

**Quick report:**
```
User: /doc:style-check
      [File auto-detected]
      y
      [Scope]
      all
      [Mode]
      1

Output: Full report, no changes
```

**Auto-fix voice/tense only:**
```
User: /doc:style-check
      [File]
      content/docs/guides/grype/scanning.md
      [Scope]
      1,2  (voice/tense and audience)
      [Mode]
      2

Output: Automatically fixes safe voice/tense/audience issues
```

**Interactive fixing everything:**
```
User: /doc:style-check
      [File from editor]
      y
      [Scope]
      all
      [Mode]
      3

Output: Interactive prompts for each issue, apply or customize
```

## Output Examples

**Report mode (option 1):**
```
## Style Report: installation.md

Summary:
🔴 Critical: 5 (voice/tense/audience)
🟡 Important: 3 (formatting/brand names)
🔵 Minor: 2 (punctuation)

Critical Issues (Fix Required) 🔴

### [Line 23] Passive voice

**Current:**
> The configuration can be changed by editing the file

**Should be:**
> Change the configuration by editing the file

**Rule:** Use active voice rather than passive voice

---

### [Line 45] Future tense

**Current:**
> The command will scan the image

**Should be:**
> The command scans the image

**Rule:** Use simple present tense

---
```

**Auto-fix mode (option 2):**
```
## Auto-fix Complete: installation.md

Fixed automatically:
✅ 3 passive voice → active voice
✅ 2 future tense → present tense
✅ 2 missing code formatting (`config.yaml`)
✅ 1 brand name (kubernetes → Kubernetes)

Changes applied to: content/docs/guides/syft/installation.md

Review changes: git diff content/docs/guides/syft/installation.md

Manual review needed:
⚠️ Line 67: Complex sentence restructuring
⚠️ Line 89: Ambiguous "we" reference

Run interactive mode (option 3) to fix these.
```

**Interactive mode (option 3):**
```
Issue 1 of 5:

🔴 [Line 23] Passive voice

**Current:**
> The configuration can be changed by editing the file

**Suggested fix:**
> Change the configuration by editing the file

**Rule:** Use active voice rather than passive voice

Action:
1. Apply this fix
2. Let me edit it differently
3. Skip (fix manually later)
4. Dismiss (not actually wrong)
5. Stop (exit interactive mode)

Enter choice (1/2/3/4/5): 2

Enter your preferred wording: Edit the file to change the configuration

✅ Applied custom fix

[Continues to next issue...]
```

## Tips for Users

1. **Start with report mode:** Understand issues before fixing
2. **Auto-fix is fast:** Good for obvious mechanical fixes
3. **Interactive for quality:** Best for important docs that need care
4. **Use scope:** Focus on specific issues (voice/tense often most critical)
5. **Review changes:** Always git diff after auto-fix or interactive mode

The goal is to ensure documentation follows consistent style, making it easier to read and understand for all users.