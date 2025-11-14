# Testing

Automated tests for the Anchore OSS documentation site.

## Test Structure

- **`unit/`** - Python unit tests for documentation generation scripts (pytest)
- **`e2e/`** - End-to-end browser tests for the live site (Playwright)

## Unit Tests

```bash
# run all unit tests
pytest

# or with uv
uv run pytest

# run with coverage report
pytest --cov

# run specific test file
pytest tests/unit/test_cli_ref.py

# run with verbose output
pytest -v
```

To update snapshots run `pytest --snapshot-update` after intentional changes.

Tests use:
- **pytest** as the test framework
- **pytest-snapshot** for snapshot testing (comparing generated output against known-good examples)
- **fixtures/** directory for test input files
- **snapshots/** directory for expected output snapshots

## E2E Tests

End-to-end tests validate the live documentation site using Playwright browser automation.

```bash
# run all e2e tests
npm test

# run in headed mode (see browser)
npm run test:headed

# run with UI mode (interactive debugging)
npm run test:ui

# run specific browser
npm run test:chromium
npm run test:firefox
npm run test:webkit
npm run test:mobile

# run specific test file
npx playwright test tests/e2e/search.spec.js

# run in debug mode
npx playwright test --debug
```

### Prerequisites

- Node.js 20+ installed
- All npm dependencies installed (`npm install`)
- Playwright browsers installed (`npx playwright install`)

### Architecture

- **Config**: `playwright.config.js` defines browsers, timeout, base URL
- **Auto-start server**: Tests automatically start Hugo dev server before running
- **Multiple browsers**: Tests run on Chromium, Firefox, WebKit, and mobile browsers
- **Screenshots**: Captured automatically on test failure
- **Traces**: Recorded on first retry for debugging

### Debugging

- Use `npm run test:headed` to watch tests in a real browser
- Use `npm run test:ui` for interactive debugging with time travel
- Add `await page.pause()` to pause execution at a specific point
- Check `test-results/` for screenshots and traces from failed tests
- Use `--debug` flag to step through tests line by line
