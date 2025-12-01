+++
title = "Issues and Discussions"
description = "When to use GitHub Issues versus Discourse Discussions"
weight = 10
type = "docs"
menu_group = "general"
+++

Understanding where to post helps you get faster, more relevant responses.

## GitHub Issues

Use GitHub issues for:

- **Bug reports**: Something isn't working as documented
- **Feature requests**: Proposals for new functionality
- **Enhancement requests**: Improvements to existing features
- **Security vulnerabilities**: Please follow our [Security Policy]({{< ref "security" >}}) (reported privately)

### Creating a good issue

- **Write a clear title**: Issue titles become changelog entries in release notes, so make them descriptive and user-focused
- **Search existing issues first**: This helps avoid duplicates and keeps discussions in one place
- **Use issue templates**: Templates guide you through providing the right information
- **Include version information**: Specify which version you're using
- **Provide reproduction steps**: For bugs, describe how to recreate the issue
- **Describe expected vs actual behavior**: Explain what you expected to happen and what actually happened
- **Add supporting details**: Include relevant logs, error messages, or screenshots

{{< alert title="Note" color="primary" >}}
We use [chronicle](https://github.com/anchore/chronicle) to automatically generate changelogs from issue and PR titles, so a well-written title goes a long way.
{{< /alert >}}

## Discourse Discussions

Use the [Anchore Discourse](https://anchore.com/discourse) for:

- **Questions**: "How do I...?" or "Why does...?"
- **Clarifications**: Understanding how features work
- **General discussion**: Ideas, use cases, and community chat
- **Help requests**: Troubleshooting your specific setup
- **Best practices**: Sharing knowledge and experiences

### Why separate channels?

GitHub issues track work items that require code changes.
Each issue represents a potential task for the development team.
Discourse provides a better format for conversations, questions, and community support without cluttering the issue tracker.

If you're unsure which to use, start with Discourse. The community can help identify if an issue should be created.

## Security Issues

If you discover a security vulnerability, please report it privately rather than creating a public issue.
See our [Security Policy]({{< ref "security" >}}) for details on how to report security issues responsibly. This gives us time to fix the problem and protect users before details become public.
