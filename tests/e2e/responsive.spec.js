const { test, expect } = require('@playwright/test');

test.describe('Responsive Layouts', () => {
  test.describe('Mobile viewport', () => {
    test.use({ viewport: { width: 375, height: 667 } }); // iPhone SE size

    test.beforeEach(async ({ page }) => {
      await page.goto('/docs/installation/syft/');
      await page.waitForLoadState('domcontentloaded');
    });

    test('navbar is visible on mobile', async ({ page }) => {
      // navbar should be visible (this site doesn't use hamburger menu)
      const navbar = page.locator('.td-navbar');
      await expect(navbar).toBeVisible();
    });

    test('layout adapts for mobile viewport', async ({ page }) => {
      // on mobile, layout should adapt (may hide or reposition sidebar)
      const mainContent = page.locator('main[role="main"]');
      await expect(mainContent).toBeVisible();

      // main content should be accessible and readable
      const contentWidth = await mainContent.evaluate(el => el.offsetWidth);
      expect(contentWidth).toBeGreaterThan(300); // at least 300px wide
    });

    test('main navigation menu adapts to mobile', async ({ page }) => {
      const navbar = page.locator('#main_navbar');
      // navigation should exist (layout changes but menu is always present)
      await expect(navbar).toBeAttached();
    });

    test('content is accessible on mobile', async ({ page }) => {
      // main content should be visible on mobile
      const mainContent = page.locator('main[role="main"]');
      await expect(mainContent).toBeVisible();
    });

    test('content is readable without horizontal scroll', async ({ page }) => {
      await page.goto('/docs/installation/syft/');

      // page should not require horizontal scrolling
      const hasHorizontalScroll = await page.evaluate(() => {
        return document.documentElement.scrollWidth > document.documentElement.clientWidth;
      });

      expect(hasHorizontalScroll).toBe(false);
    });
  });

  test.describe('Tablet viewport', () => {
    test.use({ viewport: { width: 768, height: 1024 } }); // iPad size

    test.beforeEach(async ({ page }) => {
      await page.goto('/docs/installation/syft/');
      await page.waitForLoadState('domcontentloaded');
    });

    test('sidebar is visible on tablet', async ({ page }) => {
      const sidebar = page.locator('.td-sidebar');

      // sidebar should be visible on tablet and larger
      const isVisible = await sidebar.isVisible();
      expect(isVisible).toBe(true);
    });

    test('navbar items are visible on tablet', async ({ page }) => {
      const mainNavbar = page.locator('#main_navbar');
      await expect(mainNavbar).toBeVisible();
    });

    test('content width is constrained appropriately', async ({ page }) => {
      const content = page.locator('main .td-content');

      // content should exist and be visible
      await expect(content).toBeVisible();

      // content should not be full viewport width (should have margins)
      const contentWidth = await content.evaluate(el => el.offsetWidth);
      const viewportWidth = await page.evaluate(() => window.innerWidth);

      expect(contentWidth).toBeLessThan(viewportWidth);
    });
  });

  test.describe('Desktop viewport', () => {
    test.use({ viewport: { width: 1920, height: 1080 } }); // Full HD

    test.beforeEach(async ({ page }) => {
      await page.goto('/docs/installation/syft/');
      await page.waitForLoadState('domcontentloaded');
    });

    test('sidebar is fully visible on desktop', async ({ page }) => {
      const sidebar = page.locator('.td-sidebar');
      await expect(sidebar).toBeVisible();
    });

    test('table of contents is visible on desktop', async ({ page }) => {
      const toc = page.locator('#TableOfContents');

      // TOC might not exist on all pages, so check count
      const tocCount = await toc.count();
      if (tocCount > 0) {
        await expect(toc).toBeVisible();
      }
    });

    test('navbar items are accessible', async ({ page }) => {
      const navbarNav = page.locator('.navbar-nav');
      await expect(navbarNav).toBeVisible();

      // main navbar should be visible
      const mainNavbar = page.locator('#main_navbar');
      await expect(mainNavbar).toBeVisible();
    });

    test('content has appropriate max-width on desktop', async ({ page }) => {
      const content = page.locator('main .td-content');
      await expect(content).toBeVisible();

      // on desktop, content should be readable width, not full viewport
      const contentWidth = await content.evaluate(el => el.offsetWidth);
      const viewportWidth = await page.evaluate(() => window.innerWidth);

      // content should be significantly less than viewport (has sidebars, margins)
      expect(contentWidth).toBeLessThan(viewportWidth * 0.9);
    });

    test('all navigation elements visible simultaneously', async ({ page }) => {
      // main navbar
      const navbar = page.locator('#main_navbar');
      await expect(navbar).toBeVisible();

      // theme toggle
      const themeToggle = page.locator('.td-light-dark-menu');
      await expect(themeToggle).toBeVisible();

      // sidebar should be visible on docs pages on desktop
      const sidebar = page.locator('.td-sidebar');
      await expect(sidebar).toBeVisible();
    });
  });

  test.describe('Landing page responsive design', () => {
    test.beforeEach(async ({ page }) => {
      await page.goto('/');
      await page.waitForLoadState('domcontentloaded');
    });

    test('project cards stack on mobile', async ({ page }) => {
      await page.setViewportSize({ width: 375, height: 667 });

      // find project cards
      const cards = page.locator('.landing-card');
      const cardCount = await cards.count();

      if (cardCount > 0) {
        // on mobile, cards should stack vertically
        // check that cards don't appear side-by-side
        const firstCard = cards.first();
        const firstCardWidth = await firstCard.evaluate(el => el.offsetWidth);
        const viewportWidth = await page.evaluate(() => window.innerWidth);

        // card should take most of viewport width on mobile
        expect(firstCardWidth).toBeGreaterThan(viewportWidth * 0.8);
      }
    });

    test('project cards are in grid on desktop', async ({ page }) => {
      await page.setViewportSize({ width: 1920, height: 1080 });

      const cards = page.locator('.landing-card');
      const cardCount = await cards.count();

      if (cardCount > 1) {
        // on desktop, cards should be in a grid (not full width)
        const firstCard = cards.first();
        const firstCardWidth = await firstCard.evaluate(el => el.offsetWidth);
        const viewportWidth = await page.evaluate(() => window.innerWidth);

        // card should be less than half viewport width (multiple columns)
        expect(firstCardWidth).toBeLessThan(viewportWidth * 0.5);
      }
    });
  });
});
