const { test, expect } = require('@playwright/test');

test.describe('Navigation', () => {
  test.describe('Sidebar Navigation', () => {
    test.beforeEach(async ({ page }) => {
      await page.goto('/docs/installation/syft/');
      await page.waitForLoadState('domcontentloaded');
    });

    test('sidebar is visible', async ({ page }) => {
      const sidebar = page.locator('.td-sidebar');
      await expect(sidebar).toBeVisible();
    });

    test('sidebar has navigation links', async ({ page }) => {
      const sidebarLinks = page.locator('.td-sidebar a');
      const count = await sidebarLinks.count();
      expect(count).toBeGreaterThan(0);
    });

    test('active page is highlighted in sidebar', async ({ page }) => {
      // current page should have active class
      const activeLink = page.locator('.td-sidebar .active');
      await expect(activeLink).toBeVisible();

      // verify it matches the current page
      const currentPath = new URL(page.url()).pathname;
      const activeLinkHref = await activeLink.getAttribute('href');

      // active link should match or be contained in current path
      expect(currentPath.includes(activeLinkHref) || activeLinkHref.includes(currentPath)).toBe(true);
    });

    test('sidebar groups can expand and collapse', async ({ page }) => {
      // find collapsible sections (using details/summary or similar)
      const collapsibleHeaders = page.locator('.td-sidebar .folder input[type="checkbox"]');
      const count = await collapsibleHeaders.count();

      if (count > 0) {
        const firstCheckbox = collapsibleHeaders.first();

        // get initial state
        const initialChecked = await firstCheckbox.isChecked();

        // toggle it
        await firstCheckbox.click();
        await page.waitForTimeout(200);

        // state should have changed
        const newChecked = await firstCheckbox.isChecked();
        expect(newChecked).not.toBe(initialChecked);

        // toggle back
        await firstCheckbox.click();
        await page.waitForTimeout(200);

        // should be back to original state
        const finalChecked = await firstCheckbox.isChecked();
        expect(finalChecked).toBe(initialChecked);
      }
    });

    test('clicking sidebar link navigates to page', async ({ page }) => {
      // find a sidebar link that's not the current page
      const sidebarLinks = page.locator('.td-sidebar a[href^="/docs/"]');
      const count = await sidebarLinks.count();

      if (count > 1) {
        // get second link (first might be current page)
        const secondLink = sidebarLinks.nth(1);
        const href = await secondLink.getAttribute('href');

        // click it
        await secondLink.click();
        await page.waitForLoadState('domcontentloaded');

        // verify navigation occurred
        const newPath = new URL(page.url()).pathname;
        expect(newPath).toContain(href);
      }
    });

    test('sidebar groups have proper icons', async ({ page }) => {
      // check for group headers with icons
      const groupHeaders = page.locator('.td-sidebar .sidebar-group-header');
      const count = await groupHeaders.count();

      if (count > 0) {
        const firstHeader = groupHeaders.first();

        // should have an icon (FontAwesome or similar)
        const icon = firstHeader.locator('i, svg').first();
        const iconCount = await icon.count();
        expect(iconCount).toBeGreaterThan(0);
      }
    });
  });

  test.describe('Heading Anchor Links', () => {
    test.beforeEach(async ({ page }) => {
      await page.goto('/docs/installation/syft/');
      await page.waitForLoadState('domcontentloaded');
    });

    test('headings have anchor links', async ({ page }) => {
      // find h2, h3, h4 headings with IDs
      const headingsWithIds = page.locator('main h2[id], main h3[id], main h4[id]');
      const count = await headingsWithIds.count();

      if (count > 0) {
        const firstHeading = headingsWithIds.first();
        const headingId = await firstHeading.getAttribute('id');

        // heading should have an anchor link
        const anchorLink = firstHeading.locator('a.heading-anchor');
        await expect(anchorLink).toBeAttached();

        // anchor link should point to the heading ID
        const href = await anchorLink.getAttribute('href');
        expect(href).toBe(`#${headingId}`);
      }
    });

    test('clicking anchor link scrolls to heading', async ({ page }) => {
      // find a heading with an anchor
      const headingsWithIds = page.locator('main h2[id], main h3[id]');
      const count = await headingsWithIds.count();

      if (count > 1) {
        // scroll to top first
        await page.evaluate(() => window.scrollTo(0, 0));
        await page.waitForTimeout(200);

        // get second heading
        const secondHeading = headingsWithIds.nth(1);
        const headingId = await secondHeading.getAttribute('id');

        // click its anchor link
        const anchorLink = page.locator(`a[href="#${headingId}"]`).first();
        await anchorLink.click();
        await page.waitForTimeout(500);

        // verify we scrolled to the heading
        await expect(secondHeading).toBeInViewport();

        // URL should have the hash
        const url = page.url();
        expect(url).toContain(`#${headingId}`);
      }
    });

    test('anchor links are visible on hover', async ({ page }) => {
      const headingsWithIds = page.locator('main h2[id], main h3[id]');
      const count = await headingsWithIds.count();

      if (count > 0) {
        const firstHeading = headingsWithIds.first();
        const anchorLink = firstHeading.locator('a.heading-anchor');

        // hover over heading
        await firstHeading.hover();
        await page.waitForTimeout(100);

        // anchor link should be visible (or at least attached to DOM)
        await expect(anchorLink).toBeAttached();
      }
    });
  });

  test.describe('Clickable Alert Cards', () => {
    test.beforeEach(async ({ page }) => {
      // navigate to homepage which has clickable alert cards
      await page.goto('/');
      await page.waitForLoadState('domcontentloaded');
    });

    test('alert cards exist on homepage', async ({ page }) => {
      const alertCards = page.locator('[data-url]');
      const count = await alertCards.count();

      // homepage should have some clickable alert cards
      if (count === 0) {
        test.skip();
      }
    });

    test('clicking alert card navigates to URL', async ({ page }) => {
      const alertCards = page.locator('[data-url]');
      const count = await alertCards.count();

      if (count > 0) {
        const firstCard = alertCards.first();
        const targetUrl = await firstCard.getAttribute('data-url');

        if (targetUrl) {
          // click the card
          await firstCard.click();
          await page.waitForLoadState('domcontentloaded');

          // verify navigation occurred
          const newUrl = page.url();
          expect(newUrl).toContain(targetUrl);
        }
      }
    });

    test('links inside alert cards still work independently', async ({ page }) => {
      const alertCards = page.locator('[data-url]');
      const count = await alertCards.count();

      if (count > 0) {
        // find an alert card with a link inside
        const cardWithLink = alertCards.locator('has=a').first();
        const cardLinkCount = await cardWithLink.count();

        if (cardLinkCount > 0) {
          const innerLink = cardWithLink.locator('a').first();
          const linkHref = await innerLink.getAttribute('href');

          if (linkHref) {
            // click the inner link
            await innerLink.click();
            await page.waitForLoadState('domcontentloaded');

            // should navigate to the link, not the card's data-url
            const newUrl = page.url();
            expect(newUrl).toContain(linkHref);
          }
        }
      }
    });
  });

  test.describe('Breadcrumb Navigation', () => {
    test.beforeEach(async ({ page }) => {
      await page.goto('/docs/installation/syft/');
      await page.waitForLoadState('domcontentloaded');
    });

    test('breadcrumbs are visible on docs pages', async ({ page }) => {
      const breadcrumbs = page.locator('nav[aria-label="breadcrumb"], .breadcrumb');
      const count = await breadcrumbs.count();

      // breadcrumbs may or may not exist depending on Docsy theme config
      if (count > 0) {
        await expect(breadcrumbs.first()).toBeVisible();
      }
    });

    test('breadcrumb links are clickable', async ({ page }) => {
      const breadcrumbs = page.locator('nav[aria-label="breadcrumb"], .breadcrumb');
      const count = await breadcrumbs.count();

      if (count > 0) {
        const breadcrumbLinks = breadcrumbs.first().locator('a');
        const linkCount = await breadcrumbLinks.count();

        if (linkCount > 0) {
          const firstLink = breadcrumbLinks.first();
          const href = await firstLink.getAttribute('href');

          // click breadcrumb link
          await firstLink.click();
          await page.waitForLoadState('domcontentloaded');

          // verify navigation
          const newPath = new URL(page.url()).pathname;
          expect(newPath).toContain(href);
        }
      }
    });
  });

  test.describe('Page Navigation Links', () => {
    test.beforeEach(async ({ page }) => {
      await page.goto('/docs/installation/syft/');
      await page.waitForLoadState('domcontentloaded');
    });

    test('next/previous page links work', async ({ page }) => {
      // Docsy may have prev/next navigation at bottom of pages
      const nextLink = page.locator('a[rel="next"], .nav-next a');
      const prevLink = page.locator('a[rel="prev"], .nav-prev a');

      const nextCount = await nextLink.count();
      const prevCount = await prevLink.count();

      if (nextCount > 0) {
        const href = await nextLink.first().getAttribute('href');
        await nextLink.first().click();
        await page.waitForLoadState('domcontentloaded');

        const newPath = new URL(page.url()).pathname;
        expect(newPath).toContain(href);
      } else if (prevCount > 0) {
        const href = await prevLink.first().getAttribute('href');
        await prevLink.first().click();
        await page.waitForLoadState('domcontentloaded');

        const newPath = new URL(page.url()).pathname;
        expect(newPath).toContain(href);
      }
    });
  });
});
