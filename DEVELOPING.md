# Developing

This guide helps documentation authors and contributors create documentation for Anchore's open source tools in a consistent manner (Syft, Grype, Grant, etc.).

## Getting Started

To start the local development server, run:

```bash
make dev
```

After you make changes you can fix / check linting with:

```bash
make lint-fix
```

Or if you want to run all validations:

```bash
make validate
```

If you want to make a new doc page, you can use claude with the `/doc:new` command to generate a first draft.
This requires the syft/grype/grype-db/vunnel/grant repos to be checked out as siblings to the current repo dir.

Any intermediate work from agents when using the slash commands is stored in `drafts/` in a session directory.

## Data

Python scripts in `./src` populate JSON and TXT data in `./data`, which are then used by those same scripts to
generate `*.md` snippets throughout `content/docs/`.
YAML files in `./data` are manually curated; all other files (JSON, TXT) are generated.

To generate snippets from existing `./data` files:

```bash
make generate
```

To generate snippets after running the latest docker container syft/grype/grant to update the `./data` files:

```bash
make generate:update
```

## AI Tooling

Use these slash commands with claude code:

| Command            | Purpose                  | Agent Used                                             |
| ------------------ | ------------------------ | ------------------------------------------------------ |
| `/doc:new`         | Create new documentation | doc-writer                                             |
| `/doc:refine`      | Improve existing docs    | doc-style-checker, accuracy-validator, structure-guide |
| `/doc:fact-check`  | Verify accuracy          | accuracy-validator                                     |
| `/doc:style-check` | Check style compliance   | doc-style-checker                                      |

### Agent Definitions

| Agent                  | Purpose                         | When to Use                                               |
| ---------------------- | ------------------------------- | --------------------------------------------------------- |
| **doc-writer**         | Create new content from scratch | Starting a new documentation page                         |
| **accuracy-validator** | Verify technical claims         | Want to ensure documentation matches actual tool behavior |
| **snippet-generator**  | Generate real code examples     | Need working CLI outputs, jq queries, or config examples  |
| **doc-style-checker**  | Check style guide compliance    | Want consistent tone, voice, and formatting               |
| **structure-guide**    | Validate document organization  | Need help with heading hierarchy, links, and sections     |

All agents are located in `.claude/agents/` and work as Claude Code subagents via the Task tool.

## Testing

**Unit Tests** (pytest) - Tests `src/utils/` modules:

```bash
pytest              # run all unit tests
task unit           # same as above
pytest --cov        # with coverage
```

**E2E Tests** (Playwright) - Tests Hugo site (search, navigation, theme, mermaid, responsive):

```bash
npm test            # run all e2e tests
task e2e            # same as above
npm run test:ui     # interactive mode
```

**All Tests**:

```bash
task test           # unit + e2e
task validate       # linting + unit + e2e + hugo build
```
