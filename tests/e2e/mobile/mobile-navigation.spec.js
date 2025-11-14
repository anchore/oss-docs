const { test, expect } = require('@playwright/test');

test.describe('Mobile Navigation', () => {
  test.beforeEach(async ({ page }) => {
    // navigate to a docs page
    await page.goto('/docs/installation/syft/');
    await page.waitForLoadState('domcontentloaded');
  });

  test.describe('Sidebar Toggle', () => {
    test('sidebar toggle button is visible on mobile', async ({ page }) => {
      // on mobile, there should be a toggle button to expand the sidebar
      const toggleButton = page.locator('.td-sidebar__toggle');
      await expect(toggleButton).toBeVisible();
    });

    test('sidebar navigation is collapsed by default', async ({ page }) => {
      // sidebar nav should have "collapse" class and not be shown
      const sidebarNav = page.locator('#td-section-nav');
      await expect(sidebarNav).toHaveClass(/collapse/);

      // should not have "show" class initially
      const hasShowClass = await sidebarNav.evaluate(el => el.classList.contains('show'));
      expect(hasShowClass).toBe(false);
    });

    test('clicking toggle button expands sidebar navigation', async ({ page }) => {
      const toggleButton = page.locator('.td-sidebar__toggle');
      const sidebarNav = page.locator('#td-section-nav');

      // initially collapsed
      await expect(sidebarNav).not.toHaveClass(/show/);

      // click toggle
      await toggleButton.click();
      await page.waitForTimeout(400); // wait for Bootstrap collapse animation

      // should now have "show" class
      await expect(sidebarNav).toHaveClass(/show/);
    });

    test('navigation links accessible after expanding', async ({ page }) => {
      const toggleButton = page.locator('.td-sidebar__toggle');
      const sidebarNav = page.locator('#td-section-nav');

      // expand sidebar
      await toggleButton.click();
      await page.waitForTimeout(400);

      // navigation links should now be visible
      const navLinks = sidebarNav.locator('.td-sidebar-link');
      const firstLink = navLinks.first();
      await expect(firstLink).toBeVisible();
    });

    test('active page has active class in collapsed sidebar', async ({ page }) => {
      // even when collapsed, the active link should have the active class
      const activeLink = page.locator('.td-sidebar .active');
      await expect(activeLink).toBeAttached();
      await expect(activeLink).toHaveClass(/active/);
    });

    test('clicking sidebar link navigates to page', async ({ page }) => {
      const toggleButton = page.locator('.td-sidebar__toggle');

      // expand sidebar
      await toggleButton.click();
      await page.waitForTimeout(400);

      // find a different link to click
      const links = page.locator('.td-sidebar a[href^="/docs/"]');
      const secondLink = links.nth(1);
      const targetHref = await secondLink.getAttribute('href');

      // click it
      await secondLink.click();
      await page.waitForLoadState('domcontentloaded');

      // verify navigation occurred
      const currentPath = new URL(page.url()).pathname;
      expect(currentPath).toBe(targetHref);
    });
  });

  test.describe('Heading Anchor Links', () => {
    test('heading anchor links exist but may not be visible', async ({ page }) => {
      // on mobile, content may be scrolled/hidden, but anchors should exist
      const anchors = page.locator('.heading-anchor');
      const count = await anchors.count();
      expect(count).toBeGreaterThan(0);
    });

    test('clicking visible anchor link scrolls to heading', async ({ page }) => {
      // find a heading with an ID
      const headings = page.locator('h2[id], h3[id]');
      const count = await headings.count();

      if (count === 0) {
        test.skip();
      }

      const firstHeading = headings.first();
      const headingId = await firstHeading.getAttribute('id');

      if (!headingId) {
        test.skip();
      }

      // find anchor link to this heading (might be in TOC or inline)
      const anchorLink = page.locator(`a[href="#${headingId}"]`).first();
      const anchorCount = await page.locator(`a[href="#${headingId}"]`).count();

      if (anchorCount === 0) {
        test.skip();
      }

      // check if anchor is visible before trying to interact
      const isVisible = await anchorLink.isVisible().catch(() => false);
      if (!isVisible) {
        test.skip();
      }

      // scroll anchor into view first (it might be off-screen)
      await anchorLink.scrollIntoViewIfNeeded();

      // click it
      await anchorLink.click();
      await page.waitForTimeout(500);

      // verify the heading is now in viewport
      const headingBox = await firstHeading.boundingBox();
      expect(headingBox).not.toBeNull();
      expect(headingBox.y).toBeLessThan(1000); // should be near top of viewport
    });
  });

  test.describe('Mobile Layout', () => {
    test('main content is visible on mobile', async ({ page }) => {
      const mainContent = page.locator('main');
      await expect(mainContent).toBeVisible();
    });

    test('page has correct responsive meta tag', async ({ page }) => {
      const viewport = page.locator('meta[name="viewport"]');
      await expect(viewport).toHaveAttribute('content', /width=device-width/);
    });
  });
});
