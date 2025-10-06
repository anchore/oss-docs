---
description: Create new documentation with agent assistance
---

You are orchestrating the creation of new documentation for Anchore OSS tools using a multi-agent workflow.

## Workflow Overview

This slash command coordinates multiple specialized agents through a 9-step process:
1. Session setup (you)
2. Discovery (doc-writer agent)
3. Structure proposal (structure-guide agent)
4. Initial draft (doc-writer agent)
5. Parallel validation (accuracy-validator + snippet-generator agents)
6. Revision (doc-writer agent)
7. Style check (doc-style-checker agent)
8. Finalization (you)

All artifacts are saved to `draft/<session-id>/` for transparency and manual intervention.

## Step-by-Step Instructions

### Step 1: User Prompt - What to Document

**Prompt the user:**
```
What would you like to document?

Examples:
- "The --fail-on severity flag in Grype"
- "How to use SBOM attestations with Syft"
- "Grype's database update command"
- "Filtering packages by type with jq"

Enter description:
```

**Capture:** `<description>` from user

### Step 2: Tool Detection

**Auto-detect tool from description:**
- Keywords "syft", "sbom", "cataloger" → Syft
- Keywords "grype", "vulnerability", "cve", "scan" → Grype
- Keywords "grant", "attestation", "policy" → Grant
- Keywords "jq", "filter", "query" → jq/SBOM manipulation

**Prompt for confirmation:**
```
I detected this relates to [<detected-tool>]. Is that correct? (y/n)
```

If user says no:
```
Which tool? (syft/grype/grant/other)
```

**Capture:** `<tool>` name

### Step 3: Document Type

**Prompt the user:**
```
What type of documentation?

1. User guide (how-to, tutorials)
2. Reference (CLI commands, config options)
3. Conceptual (architecture, explanations)

Enter choice (1/2/3):
```

**Map choice to type:**
- 1 → "user-guide"
- 2 → "reference"
- 3 → "conceptual"

**Capture:** `<doc-type>`

### Step 4: Session Setup

**Create session directory:**
```bash
session_id=$(date +%Y%m%d-%H%M%S)-<topic-slug>
mkdir -p draft/$session_id
```

Where `<topic-slug>` is a URL-safe version of the description (lowercase, hyphens, max 30 chars).

**Write session info:**
```markdown
---
session: <session-id>
created: <ISO-8601 timestamp>
---

# Documentation Session: <description>

## Request Details

**User request:** <description>

**Tool:** <tool>

**Document type:** <doc-type>

## Session Directory

This directory contains artifacts from each step of the documentation creation process.

### Artifacts
- `00-session-info.md` - This file
- `01-discovery.md` - Source code findings (doc-writer)
- `02-structure-proposal.md` - Proposed outline (structure-guide)
- `03-initial-draft.md` - First content draft (doc-writer)
- `04-fact-check-report.md` - Accuracy validation (accuracy-validator)
- `05-updated-draft.md` - Revised content (doc-writer)
- `06-snippet-examples.md` - Real code examples (snippet-generator)
- `07-style-report.md` - Style compliance check (doc-style-checker)
- `08-final-draft.md` - Ready for placement
```

**Save to:** `draft/<session-id>/00-session-info.md`

### Step 5: Discovery (doc-writer agent)

**Launch doc-writer in discovery mode:**

Use the Task tool with:
- Agent: `doc-writer`
- Prompt:
  ```
  Perform discovery for new documentation.

  Session: <session-id>
  Topic: <description>
  Tool: <tool>
  Document type: <doc-type>

  Search source code in:
  - ../syft/ (if tool is Syft)
  - ../grype/ (if tool is Grype)
  - ../grant/ (if tool is Grant)

  Find and document:
  - CLI flags, configuration options
  - Implementation details
  - Test examples
  - Default values
  - Related code locations

  Write your findings to: draft/<session-id>/01-discovery.md

  Follow the discovery artifact format specified in your instructions.
  ```

**Wait for agent to complete.**

### Step 6: Review Discovery (user prompt)

**Show discovery summary to user:**

Read `draft/<session-id>/01-discovery.md` and extract key findings.

**Prompt user:**
```
## Discovery Complete

Found the following items:
- <summary of key findings>
- <source locations>
- <implementation details>

Full findings in: draft/<session-id>/01-discovery.md

Continue with this discovery? (y/n/edit)
```

**If user chooses 'edit':**
```
Opening discovery file for manual editing...
[Open draft/<session-id>/01-discovery.md in editor]

Press Enter when you're done editing...
```

**If user says 'n':** Ask what's missing, re-run discovery with updated instructions.

### Step 7: Structure Proposal (structure-guide agent)

**Launch structure-guide:**

Use the Task tool with:
- Agent: `structure-guide`
- Prompt:
  ```
  Propose a structure for new documentation.

  Session: <session-id>
  Document type: <doc-type>

  Read discovery findings from: draft/<session-id>/01-discovery.md

  Based on the findings and document type, propose:
  - Heading hierarchy (H1, H2, H3)
  - Section organization
  - Content placement
  - Recommended flow

  Write your proposal to: draft/<session-id>/02-structure-proposal.md

  Follow the structure proposal artifact format specified in your instructions.
  ```

**Wait for agent to complete.**

### Step 8: Review Structure (user prompt)

**Show structure outline to user:**

Read `draft/<session-id>/02-structure-proposal.md` and extract proposed outline.

**Prompt user:**
```
## Proposed Structure

<Show outline/heading hierarchy>

Full proposal in: draft/<session-id>/02-structure-proposal.md

Approve this structure? (y/n/edit)
```

**Handle user choice same as Step 6.**

### Step 9: Initial Draft (doc-writer agent)

**Launch doc-writer in drafting mode:**

Use the Task tool with:
- Agent: `doc-writer`
- Prompt:
  ```
  Write initial documentation draft.

  Session: <session-id>

  Read inputs from:
  - draft/<session-id>/01-discovery.md (source findings)
  - draft/<session-id>/02-structure-proposal.md (structure to follow)

  Write documentation following:
  - The proposed structure exactly
  - Style guide at content/docs/about/style-guide.md
  - Active voice, present tense, "you" not "we"
  - Code examples from discovery

  Write your draft to: draft/<session-id>/03-initial-draft.md

  Include proper front matter:
  +++
  title = "<Title>"
  description = "<Brief description>"
  weight = <number>
  type = "docs"
  +++

  Follow the drafting artifact format specified in your instructions.
  ```

**Wait for agent to complete.**

### Step 10: Parallel Validation (accuracy-validator + snippet-generator)

**Launch both agents in parallel using a single message with multiple Task tool calls:**

**Agent 1: accuracy-validator**
- Prompt:
  ```
  Validate documentation accuracy against source code.

  Session: <session-id>
  Tool: <tool>

  Read documentation from: draft/<session-id>/03-initial-draft.md

  Cross-reference all technical claims against source code in:
  - ../syft/ (if Syft)
  - ../grype/ (if Grype)
  - ../grant/ (if Grant)

  Check:
  - CLI flag names, descriptions, defaults
  - Configuration fields
  - Behavior claims
  - Examples and output

  Write fact-check report to: draft/<session-id>/04-fact-check-report.md

  Follow the fact-check report format specified in your instructions.
  ```

**Agent 2: snippet-generator**
- Prompt:
  ```
  Generate real code snippets and examples.

  Session: <session-id>
  Tool: <tool>

  Read documentation from: draft/<session-id>/03-initial-draft.md

  Generate working examples by:
  - Running actual tools via Docker (syft, grype, grant)
  - Using existing scripts (scripts/generate-jq-examples.sh)
  - Capturing real output

  Create examples for:
  - Commands shown in documentation
  - Expected outputs
  - Configuration snippets

  Write examples to: draft/<session-id>/06-snippet-examples.md

  Follow the snippet artifact format specified in your instructions.
  ```

**Wait for both agents to complete.**

### Step 11: Review Fact Check (user prompt)

**Show fact-check summary:**

Read `draft/<session-id>/04-fact-check-report.md` and extract summary.

**Prompt user:**
```
## Fact-Check Complete

Summary:
- Accurate: <count> ✅
- Issues found: <count> ❌
- Unverifiable: <count> ❓

Full report in: draft/<session-id>/04-fact-check-report.md

Review full report? (y/n/skip)
```

**If 'y':** Display full report

Then ask:
```
Continue with automated corrections? (y/n)
```

**If 'n':** User can manually edit the draft.

### Step 12: Revision (doc-writer agent)

**Launch doc-writer in revision mode:**

Use the Task tool with:
- Agent: `doc-writer`
- Prompt:
  ```
  Revise documentation based on fact-check and snippets.

  Session: <session-id>

  Read inputs from:
  - draft/<session-id>/03-initial-draft.md (original draft)
  - draft/<session-id>/04-fact-check-report.md (corrections needed)
  - draft/<session-id>/06-snippet-examples.md (real examples to integrate)

  Apply:
  - All fact-check corrections
  - Integrate real code snippets
  - Maintain structure and flow
  - Keep style guide compliance

  Write revised draft to: draft/<session-id>/05-updated-draft.md

  Follow the revision artifact format specified in your instructions.
  ```

**Wait for agent to complete.**

### Step 13: Style Check (doc-style-checker agent)

**Launch doc-style-checker:**

Use the Task tool with:
- Agent: `doc-style-checker`
- Prompt:
  ```
  Check documentation for style guide compliance.

  Session: <session-id>

  Read documentation from: draft/<session-id>/05-updated-draft.md
  Read style guide from: content/docs/about/style-guide.md

  Check for:
  - Voice: Active not passive
  - Tense: Present not future
  - Audience: "you" not "we"/"the user"
  - Formatting: code, bold, placeholders
  - Capitalization: sentence case
  - Brand names: correct capitalization

  Write style report to: draft/<session-id>/07-style-report.md

  Follow the style report format specified in your instructions.
  ```

**Wait for agent to complete.**

### Step 14: Finalization

**Apply style fixes:**

Read both:
- `draft/<session-id>/05-updated-draft.md`
- `draft/<session-id>/07-style-report.md`

Apply critical style fixes (🔴) automatically. For important/minor fixes, apply if straightforward.

**Write final draft:**

Save to `draft/<session-id>/08-final-draft.md` with all corrections applied.

### Step 15: Placement (user prompt)

**Show preview and suggest placement:**

```
## Documentation Complete!

Preview: draft/<session-id>/08-final-draft.md

Suggested placement:
content/docs/<section>/<tool>/<inferred-filename>.md

Where:
- <section> = guides | reference | concepts
- <tool> = syft | grype | grant
- <filename> = <URL-safe topic>

Options:
1. Use suggested path
2. Specify custom path
3. Leave in draft/ for manual placement

Enter choice (1/2/3):
```

**If 1:** Copy `08-final-draft.md` to suggested path
**If 2:** Prompt for path, then copy
**If 3:** Leave in draft, inform user

**Finally:**
```
✅ Documentation created!

Location: <final-path> (or draft/<session-id>/)
Session artifacts: draft/<session-id>/

Next steps:
- Review the final documentation
- Run: npm run lint to check for issues
- Commit when ready
```

## Implementation Notes

### Session ID Format
```
YYYYMMDD-HHMMSS-<topic-slug>

Example: 20250103-143022-grype-fail-on-flag
```

### Topic Slug Generation
```javascript
// Pseudo-code
topic_slug = description
  .toLowerCase()
  .replace(/[^a-z0-9]+/g, '-')
  .substring(0, 30)
  .replace(/^-|-$/g, '')
```

### Error Handling

**If agent fails:**
1. Show error message
2. Preserve partial artifacts
3. Offer to retry or skip step
4. Allow manual intervention

**If user interrupts:**
1. Save current state
2. Allow resume from any step
3. Session artifacts remain for later use

### User Intervention Points

Users can manually edit artifacts at:
- After discovery (01-discovery.md)
- After structure (02-structure-proposal.md)
- After fact-check (can skip auto-correction)
- Before final placement

### Parallel Execution

Step 10 MUST execute agents in parallel:
- Use single message with two Task tool calls
- Don't wait for first to finish before launching second
- Both agents read same input (03-initial-draft.md)
- They write to different outputs (04, 06)

## Tips for Success

1. **Be patient:** 9 steps take time, but ensure quality
2. **Review artifacts:** Check each step's output before proceeding
3. **Intervene when needed:** Edit artifacts if agents miss something
4. **Trust the process:** Each step builds on previous ones
5. **Keep session organized:** All artifacts in one directory

The goal is to produce documentation that is:
- ✅ Factually accurate (validated against source)
- ✅ Well-structured (logical flow)
- ✅ Style-compliant (consistent voice/tone)
- ✅ Example-rich (real, working code)
- ✅ Ready to publish (minimal editing needed)