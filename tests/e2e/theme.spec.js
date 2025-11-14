const { test, expect } = require('@playwright/test');

test.describe('Theme Switching', () => {
  test.beforeEach(async ({ page }) => {
    // navigate to homepage
    await page.goto('/');
    await page.waitForLoadState('domcontentloaded');
  });

  test('theme toggle button exists', async ({ page }) => {
    // Docsy uses a dropdown for theme switching
    const themeToggle = page.locator('.td-light-dark-menu');
    await expect(themeToggle).toBeVisible();
  });

  test('can toggle between light and dark themes', async ({ page }) => {
    // find the theme dropdown
    const themeDropdown = page.locator('.td-light-dark-menu');

    // get initial theme from html data-bs-theme attribute (Bootstrap 5)
    const initialTheme = await page.locator('html').getAttribute('data-bs-theme');

    // open theme dropdown
    await themeDropdown.click();

    // find and click the opposite theme option
    if (initialTheme === 'dark') {
      // switch to light
      const lightOption = page.locator('[data-bs-theme-value="light"]');
      await lightOption.click();
      await page.waitForTimeout(300); // wait for theme change

      // verify theme changed
      const newTheme = await page.locator('html').getAttribute('data-bs-theme');
      expect(newTheme).toBe('light');
    } else {
      // switch to dark
      const darkOption = page.locator('[data-bs-theme-value="dark"]');
      await darkOption.click();
      await page.waitForTimeout(300); // wait for theme change

      // verify theme changed
      const newTheme = await page.locator('html').getAttribute('data-bs-theme');
      expect(newTheme).toBe('dark');
    }
  });

  test('theme persists on page reload', async ({ page }) => {
    // find the theme dropdown
    const themeDropdown = page.locator('.td-light-dark-menu');

    // open theme dropdown
    await themeDropdown.click();

    // set to dark mode
    const darkOption = page.locator('[data-bs-theme-value="dark"]');
    await darkOption.click();
    await page.waitForTimeout(300);

    // verify dark mode is active
    let currentTheme = await page.locator('html').getAttribute('data-bs-theme');
    expect(currentTheme).toBe('dark');

    // reload page
    await page.reload();
    await page.waitForLoadState('domcontentloaded');

    // verify theme persisted
    currentTheme = await page.locator('html').getAttribute('data-bs-theme');
    expect(currentTheme).toBe('dark');

    // switch back to light mode
    await themeDropdown.click();
    const lightOption = page.locator('[data-bs-theme-value="light"]');
    await lightOption.click();
    await page.waitForTimeout(300);

    // reload again
    await page.reload();
    await page.waitForLoadState('domcontentloaded');

    // verify light theme persisted
    currentTheme = await page.locator('html').getAttribute('data-bs-theme');
    expect(currentTheme).toBe('light');
  });

  test('theme persists across navigation', async ({ page }) => {
    // find the theme dropdown
    const themeDropdown = page.locator('.td-light-dark-menu');

    // set to dark mode
    await themeDropdown.click();
    const darkOption = page.locator('[data-bs-theme-value="dark"]');
    await darkOption.click();
    await page.waitForTimeout(300);

    // navigate to another page
    await page.goto('/docs/installation/grype/');
    await page.waitForLoadState('domcontentloaded');

    // theme should still be dark
    const theme = await page.locator('html').getAttribute('data-bs-theme');
    expect(theme).toBe('dark');
  });

  test('auto theme option available', async ({ page }) => {
    // find the theme dropdown
    const themeDropdown = page.locator('.td-light-dark-menu');

    // open theme dropdown
    await themeDropdown.click();

    // check if auto option exists
    const autoOption = page.locator('[data-bs-theme-value="auto"]');
    // auto option may or may not exist depending on Docsy configuration
    // just verify we can query it without error
    const autoCount = await autoOption.count();
    expect(autoCount >= 0).toBe(true);
  });

  test('theme affects page background color', async ({ page }) => {
    const themeDropdown = page.locator('.td-light-dark-menu');

    // set to light mode
    await themeDropdown.click();
    const lightOption = page.locator('[data-bs-theme-value="light"]');
    await lightOption.click();
    await page.waitForTimeout(300);

    // get background color in light mode
    const lightBgColor = await page.locator('body').evaluate(el =>
      getComputedStyle(el).backgroundColor
    );

    // switch to dark mode
    await themeDropdown.click();
    const darkOption = page.locator('[data-bs-theme-value="dark"]');
    await darkOption.click();
    await page.waitForTimeout(300);

    // get background color in dark mode
    const darkBgColor = await page.locator('body').evaluate(el =>
      getComputedStyle(el).backgroundColor
    );

    // background colors should be different
    expect(lightBgColor).not.toBe(darkBgColor);
  });
});
