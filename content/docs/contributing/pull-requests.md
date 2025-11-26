+++
title = "Pull Requests"
description = "Guidelines for submitting pull requests and working with reviewers"
weight = 20
type = "docs"
menu_group = "general"
+++

If you've made changes and the tests are passing, it's time to submit a pull request (PR). This guide will help you through the process.

## Quick Checklist

Before submitting your PR, make sure you have:

- ✓ Run the test suite and confirmed tests pass
- ✓ Signed off all commits (see [Sign-off Requirements]({{< ref "/docs/contributing/sign-off" >}}))
- ✓ Updated in-repo documentation if your changes affect user-facing behavior
- ✓ Written a clear PR title that describes the user-facing impact
- ✓ Followed existing code style and patterns in the project

Each of these items helps maintainers review your contribution more effectively and merge it faster.

## PR Title

Your PR title is important—**it becomes the changelog entry in release notes**. Write titles that are meaningful to end users, not just developers.

### Guidelines

- **Start with an action verb**: "Add", "Fix", "Update", "Remove"
- **Be specific**: "Add support for Alpine 3.19" rather than "Update Alpine"
- **Keep it concise**: Under 72 characters when possible
- **Focus on user impact**: What changed for users, not implementation details

### Examples

**Good titles:**

- `Add support for Python 3.12 package detection`
- `Fix crash when parsing malformed RPM databases`
- `Update documentation for custom template usage`

**Poor titles:**

- `Updates` (too vague—updates to what?)
- `Fixed bug` (which bug?)
- `WIP: trying some things` (not ready for review)
- `Refactor parseRPM function` (implementation detail, not a user-facing change)

{{< alert title="Note" color="primary" >}}
We use [chronicle](https://github.com/anchore/chronicle) to automatically generate changelogs from issue and PR titles, so a well-written title goes a long way.
{{< /alert >}}

## PR Description

A clear description helps reviewers understand your changes quickly. Include these key sections:

### What to include

1. **Summary**: Briefly describe what changed
2. **Motivation**: Explain why this change is needed or what problem it solves
3. **Approach**: If your solution isn't obvious, explain your approach
4. **Testing**: Describe how you tested the changes
5. **Related issues**: Link to issues or discussions that provide context

### Template

```markdown
## Summary

Brief description of the change.

## Motivation

Why is this change needed? What problem does it solve?

## Changes

- Bullet point list of key changes
- Include any breaking changes or migration steps

## Type of change

<!-- Delete any that are not relevant -->

- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (please discuss with the team first; Syft is 1.0 software and we won't accept breaking changes without going to 2.0)
- [ ] Documentation (updates the documentation)
- [ ] Chore (improve the developer experience, fix a test flake, etc, without changing the visible behavior of Syft)
- [ ] Performance (make Syft run faster or use less memory, without changing visible behavior much)

## Checklist

- [ ] I have added unit tests that cover changed behavior
- [ ] I have tested my code in common scenarios and confirmed there are no regressions
- [ ] I have added comments to my code, particularly in hard-to-understand sections

Closes #123
```

## Commit History

We use **squash merging** for all pull requests, which means:

- Your entire PR becomes a single commit on the main branch
- You don't need to maintain a clean commit history in your PR
- Merge commits in your feature branch are perfectly fine
- You can commit as frequently as you like during development
- The PR title (not individual commit messages) becomes the changelog entry

This approach keeps the main branch clean and linear while reducing friction for contributors. Focus on code quality rather than commit structure—reviewers care about the changes, not how you got there.

## Size Matters

**Small PRs get reviewed faster.** Here's how to make your PR easier to review:

- **Keep changes focused**: Try to address one concern per PR
- **Avoid mixing unrelated changes**: Don't combine bug fixes with new features
- **Split large PRs when possible**: If a PR is unavoidably large, provide extra context in the description

Consider breaking work into multiple PRs if you're making both refactoring changes and feature additions. Reviewers can process smaller, focused changes more quickly.

## What to Expect

### Review Feedback

It's normal and expected for reviewers to have questions and suggestions:

- **Questions about your approach**: Be prepared to explain your decisions
- **Code style adjustments**: You may be asked to match existing project patterns
- **Additional tests**: Reviewers might request more test coverage
- **Scope changes**: You might be asked to split or narrow the PR

### How to respond to feedback

- **Address feedback promptly**: Respond when you can, even if just to acknowledge
- **Ask for clarification**: If something isn't clear, ask questions
- **Explain your reasoning**: It's okay to discuss alternatives respectfully
- **Make changes in new commits**: This makes incremental review easier
- **Mark conversations as resolved**: When you've addressed a comment

Remember that review feedback is about the code, not about you. Reviewers want to help make the contribution successful.

### After Approval

Once approved, a maintainer will merge your PR. Depending on the project, you might be asked to:

- Rebase on the latest main branch if there are conflicts
- Update the PR title or description for clarity
- Make final adjustments based on last-minute feedback

## Common Issues

Watch out for these common pitfalls:

- **Missing sign-off**: All commits must be signed off (see [Sign-off Requirements]({{< ref "/docs/contributing/sign-off" >}}))
- **Failing CI checks**: Make sure all tests and checks pass before requesting review
- **Merge conflicts**: Keep your branch up to date with main to avoid conflicts
- **Formatting-only changes**: Submit formatting and refactoring in separate PRs from features
- **Missing documentation**: User-facing changes need corresponding documentation updates

## Need Help?

If you're stuck or have questions about the PR process:

- Ask in the PR comments—maintainers are happy to help
- Reach out on the project's [Discourse](https://anchore.com/discourse)
- Check the project-specific contributing guide for any additional requirements

Contributing to open source can feel intimidating at first, but the community is here to support you. Don't hesitate to ask questions.
