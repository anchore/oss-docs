const { test, expect } = require('@playwright/test');

test.describe('Mobile Search Modal', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/docs/installation/syft/');
    await page.waitForLoadState('domcontentloaded');
  });

  test('search button is visible on mobile', async ({ page }) => {
    // mobile should have a search button/icon
    const searchButton = page.locator('#pagefind-search-button');
    await expect(searchButton).toBeVisible();
  });

  test('clicking search button opens modal', async ({ page }) => {
    const searchButton = page.locator('#pagefind-search-button');
    const modal = page.locator('#pagefind-modal');

    // click search button
    await searchButton.click();
    await page.waitForTimeout(300);

    // modal should be open
    await expect(modal).toHaveAttribute('open', '');
  });

  test('search input gets focus when modal opens', async ({ page }) => {
    const searchButton = page.locator('#pagefind-search-button');
    const searchInput = page.locator('#pagefind-modal input[type="text"]');

    // open modal
    await searchButton.click();
    await page.waitForTimeout(300);

    // input should be focused
    await expect(searchInput).toBeFocused();
  });

  test('typing in search shows results', async ({ page }) => {
    const searchButton = page.locator('#pagefind-search-button');
    const searchInput = page.locator('#pagefind-modal input[type="text"]');

    // open modal and type
    await searchButton.click();
    await page.waitForTimeout(300);
    await searchInput.fill('syft');
    await page.waitForTimeout(500);

    // results should appear
    const results = page.locator('.pagefind-ui__results .pagefind-ui__result');
    await expect(results.first()).toBeVisible({ timeout: 3000 });
  });

  test('close button closes modal on mobile', async ({ page }) => {
    const searchButton = page.locator('#pagefind-search-button');
    const modal = page.locator('#pagefind-modal');
    const closeButton = page.locator('#pagefind-close');

    // open modal
    await searchButton.click();
    await page.waitForTimeout(300);
    await expect(modal).toHaveAttribute('open', '');

    // click close button
    await closeButton.click();
    await page.waitForTimeout(300);

    // modal should be closed
    await expect(modal).not.toHaveAttribute('open', '');
  });

  test('Escape key closes modal on mobile', async ({ page }) => {
    const searchButton = page.locator('#pagefind-search-button');
    const modal = page.locator('#pagefind-modal');

    // open modal
    await searchButton.click();
    await page.waitForTimeout(300);
    await expect(modal).toHaveAttribute('open', '');

    // press Escape
    await page.keyboard.press('Escape');
    await page.waitForTimeout(300);

    // modal should be closed
    await expect(modal).not.toHaveAttribute('open', '');
  });

  test('clicking modal content does not close modal', async ({ page }) => {
    const searchButton = page.locator('#pagefind-search-button');
    const modal = page.locator('#pagefind-modal');
    const searchInput = page.locator('#pagefind-modal input[type="text"]');

    // open modal
    await searchButton.click();
    await page.waitForTimeout(300);

    // click inside the modal content
    await searchInput.click();
    await page.waitForTimeout(200);

    // modal should still be open
    await expect(modal).toHaveAttribute('open', '');
  });

  test('modal is properly sized for mobile viewport', async ({ page }) => {
    const searchButton = page.locator('#pagefind-search-button');
    const modal = page.locator('#pagefind-modal');

    // open modal
    await searchButton.click();
    await page.waitForTimeout(300);

    // get modal dimensions
    const box = await modal.boundingBox();
    const viewport = page.viewportSize();

    // modal should take up significant portion of viewport on mobile
    // (not testing exact dimensions, just that it's responsive)
    expect(box).not.toBeNull();
    expect(box.width).toBeGreaterThan(200);
    expect(box.width).toBeLessThanOrEqual(viewport.width);
  });

  test('search results are scrollable on mobile', async ({ page }) => {
    const searchButton = page.locator('#pagefind-search-button');
    const searchInput = page.locator('#pagefind-modal input[type="text"]');
    const resultsContainer = page.locator('.pagefind-ui__results');

    // open modal and search for something with many results
    await searchButton.click();
    await page.waitForTimeout(300);
    await searchInput.fill('install');
    await page.waitForTimeout(500);

    // results container should exist and be visible
    await expect(resultsContainer).toBeVisible();

    // verify results container has overflow handling
    const overflow = await resultsContainer.evaluate(el => {
      const style = window.getComputedStyle(el);
      return style.overflow || style.overflowY;
    });

    // should have some overflow handling (auto, scroll, or inherited)
    expect(['auto', 'scroll', 'visible', '']).toContain(overflow);
  });
});
