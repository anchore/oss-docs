const { test, expect } = require('@playwright/test');

test.describe('Pagefind Search Modal', () => {
  test.beforeEach(async ({ page }) => {
    // navigate to docs page (search modal only exists on docs pages)
    await page.goto('/docs/installation/syft/');
    await page.waitForLoadState('domcontentloaded');
  });

  test('opens modal when clicking search button', async ({ page }) => {
    const searchButton = page.locator('#pagefind-search-button');
    const modal = page.locator('#pagefind-modal');

    // modal should be closed initially
    await expect(modal).not.toHaveAttribute('open', '');

    // click search button
    await searchButton.click();

    // modal should now be open
    await expect(modal).toHaveAttribute('open', '');
  });

  test('opens modal with Cmd/Ctrl+K keyboard shortcut', async ({ page }) => {
    const modal = page.locator('#pagefind-modal');

    // modal should be closed initially
    await expect(modal).not.toHaveAttribute('open', '');

    // press Cmd+K (Mac) or Ctrl+K (Windows/Linux)
    await page.keyboard.press('Meta+KeyK');

    // modal should now be open
    await expect(modal).toHaveAttribute('open', '');
  });

  test('search input receives focus when modal opens', async ({ page }) => {
    const searchButton = page.locator('#pagefind-search-button');

    // open modal
    await searchButton.click();

    // wait for PagefindUI to initialize and create the input
    const searchInput = page.locator('.pagefind-ui__search-input');
    await searchInput.waitFor({ timeout: 2000 });

    // input should be focused
    await expect(searchInput).toBeFocused();
  });

  test('closes modal with close button', async ({ page }) => {
    const searchButton = page.locator('#pagefind-search-button');
    const modal = page.locator('#pagefind-modal');
    const closeButton = page.locator('#pagefind-close');

    // open modal
    await searchButton.click();
    await expect(modal).toHaveAttribute('open', '');

    // click close button
    await closeButton.click();

    // modal should be closed
    await expect(modal).not.toHaveAttribute('open', '');
  });

  test('closes modal with Escape key', async ({ page }) => {
    const searchButton = page.locator('#pagefind-search-button');
    const modal = page.locator('#pagefind-modal');

    // open modal
    await searchButton.click();
    await expect(modal).toHaveAttribute('open', '');

    // press Escape
    await page.keyboard.press('Escape');

    // modal should be closed
    await expect(modal).not.toHaveAttribute('open', '');
  });

  test('closes modal when clicking backdrop', async ({ page }) => {
    const searchButton = page.locator('#pagefind-search-button');
    const modal = page.locator('#pagefind-modal');

    // open modal
    await searchButton.click();
    await expect(modal).toHaveAttribute('open', '');

    // click outside the modal content to hit the backdrop
    // use force: true to click on the dialog backdrop even if covered
    await page.mouse.click(10, 10);
    await page.waitForTimeout(100);

    // modal should be closed
    await expect(modal).not.toHaveAttribute('open', '');
  });

  test('toggling with Cmd/Ctrl+K closes open modal', async ({ page }) => {
    const modal = page.locator('#pagefind-modal');

    // open modal with keyboard shortcut
    await page.keyboard.press('Meta+KeyK');
    await expect(modal).toHaveAttribute('open', '');

    // press Cmd+K again to close
    await page.keyboard.press('Meta+KeyK');
    await expect(modal).not.toHaveAttribute('open', '');
  });

  test('search results appear when typing query', async ({ page }) => {
    const searchButton = page.locator('#pagefind-search-button');
    const searchInput = page.locator('.pagefind-ui__search-input');

    // open modal
    await searchButton.click();
    await searchInput.waitFor({ timeout: 2000 });

    // type a search query (at least 2 characters based on processTerm)
    await searchInput.fill('syft');

    // wait for results to appear
    const results = page.locator('.pagefind-ui__results');
    await results.waitFor({ timeout: 3000 });

    // results container should be visible
    await expect(results).toBeVisible();
  });

  test('Section filter auto-expands when filters appear', async ({ page }) => {
    const searchButton = page.locator('#pagefind-search-button');
    const searchInput = page.locator('.pagefind-ui__search-input');

    // open modal
    await searchButton.click();
    await searchInput.waitFor({ timeout: 2000 });

    // type a search query to trigger filters
    await searchInput.fill('installation');

    // wait for Section filter to appear
    const sectionFilter = page.locator('.pagefind-ui__filter-name', { hasText: 'Section' });
    await sectionFilter.waitFor({ timeout: 3000 });

    // check if filter is expanded (has .pagefind-ui__filter-group--open or similar)
    const filterBlock = sectionFilter.locator('xpath=ancestor::details');
    await expect(filterBlock).toHaveAttribute('open', '');
  });
});
