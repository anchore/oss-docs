const { defineConfig, devices } = require('@playwright/test');

/**
 * Playwright configuration for Hugo documentation site e2e tests
 * @see https://playwright.dev/docs/test-configuration
 */
module.exports = defineConfig({
  // test directory
  testDir: './tests/e2e',

  // maximum time one test can run
  timeout: 12 * 1000,

  // run tests in parallel
  fullyParallel: true,

  // fail the build on CI if you accidentally left test.only in the source code
  forbidOnly: !!process.env.CI,

  // retry on CI only
  retries: process.env.CI ? 2 : 0,

  // reporter configuration
  reporter: process.env.CI ? 'github' : 'list',

  // shared settings for all projects
  use: {
    // base URL for tests - uses local Hugo server
    baseURL: process.env.BASE_URL || 'http://localhost:1313',

    // collect trace when retrying the failed test
    trace: 'on-first-retry',

    // screenshot on failure
    screenshot: 'only-on-failure',
  },

  // configure projects for different browsers
  projects: [
    // Desktop browsers - run all tests except mobile-specific ones
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
      testIgnore: '**/mobile/**',
    },
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
      testIgnore: '**/mobile/**',
    },
    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] },
      testIgnore: '**/mobile/**',
    },
    // Mobile browsers - only run mobile-specific tests
    {
      name: 'mobile-chrome',
      use: { ...devices['Pixel 5'] },
      testMatch: '**/mobile/**',
    },
    {
      name: 'mobile-safari',
      use: { ...devices['iPhone 12'] },
      testMatch: '**/mobile/**',
    },
  ],

  // run local dev server before starting tests
  webServer: {
    command: process.env.CI
      // CI: build static site with Pagefind index, then serve
      ? 'npm run build:dev && npx -y pagefind --site public && npx -y serve public -l 1313'
      // Local: use live Hugo server (better for Mermaid controls initialization)
      : 'npm run serve:with-search',
    url: 'http://localhost:1313',
    reuseExistingServer: !process.env.CI,
    timeout: 120 * 1000,
  },
});
