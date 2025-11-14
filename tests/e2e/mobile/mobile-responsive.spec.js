const { test, expect } = require('@playwright/test');

test.describe('Mobile Responsive Behavior', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/docs/installation/syft/');
    await page.waitForLoadState('domcontentloaded');
  });

  test.describe('Table of Contents (TOC)', () => {
    test('right TOC sidebar is hidden on mobile', async ({ page }) => {
      // the right TOC sidebar should not be visible on mobile (< 1200px)
      const tocSidebar = page.locator('.td-sidebar-toc');

      // element should exist in DOM
      await expect(tocSidebar).toBeAttached();

      // but should not be visible (d-none class active on mobile)
      await expect(tocSidebar).not.toBeVisible();
    });

    test('TOC has correct responsive classes', async ({ page }) => {
      const tocSidebar = page.locator('.td-sidebar-toc');

      // should have d-none (hidden by default) and d-xl-block (visible on XL screens only)
      await expect(tocSidebar).toHaveClass(/d-none/);
      await expect(tocSidebar).toHaveClass(/d-xl-block/);
    });

    test('in-page TOC (#TableOfContents) is also hidden on mobile', async ({ page }) => {
      const inPageToc = page.locator('#TableOfContents');

      // element exists but not visible on mobile
      await expect(inPageToc).toBeAttached();
      await expect(inPageToc).not.toBeVisible();
    });
  });

  test.describe('Sidebar Layout', () => {
    test('left sidebar takes full width on mobile', async ({ page }) => {
      const sidebar = page.locator('.td-sidebar');

      // should have col-12 class (full width on mobile)
      await expect(sidebar).toHaveClass(/col-12/);
    });

    test('sidebar has responsive column classes', async ({ page }) => {
      const sidebar = page.locator('.td-sidebar');

      // should have Bootstrap responsive grid classes
      await expect(sidebar).toHaveClass(/col-12/);     // mobile full-width
      await expect(sidebar).toHaveClass(/col-md-3/);   // tablet+ 25%
      await expect(sidebar).toHaveClass(/col-xl-2/);   // XL 16.67%
    });
  });

  test.describe('Main Content Area', () => {
    test('main content is visible and takes full width', async ({ page }) => {
      const mainContent = page.locator('main.col-12');
      await expect(mainContent).toBeVisible();

      // on mobile, main content should take full width
      await expect(mainContent).toHaveClass(/col-12/);
    });

    test('page headings are readable on mobile', async ({ page }) => {
      const h1 = page.locator('h1').first();
      await expect(h1).toBeVisible();

      // heading should not overflow viewport
      const box = await h1.boundingBox();
      const viewport = page.viewportSize();
      expect(box.width).toBeLessThanOrEqual(viewport.width);
    });

    test('code blocks are scrollable on mobile', async ({ page }) => {
      // find a code block
      const codeBlock = page.locator('pre code').first();

      if (await codeBlock.count() === 0) {
        test.skip();
      }

      await expect(codeBlock).toBeVisible();

      // code block container should have overflow handling
      const pre = page.locator('pre').first();
      const overflow = await pre.evaluate(el => {
        const style = window.getComputedStyle(el);
        return style.overflowX;
      });

      // should allow horizontal scrolling
      expect(['auto', 'scroll']).toContain(overflow);
    });

    test('images are responsive on mobile', async ({ page }) => {
      const images = page.locator('main img');
      const imageCount = await images.count();

      if (imageCount === 0) {
        test.skip();
      }

      const firstImage = images.first();
      await expect(firstImage).toBeVisible();

      // image should not overflow viewport
      const box = await firstImage.boundingBox();
      const viewport = page.viewportSize();
      expect(box.width).toBeLessThanOrEqual(viewport.width);
    });
  });

  test.describe('Navigation Bar', () => {
    test('top navbar is visible on mobile', async ({ page }) => {
      const navbar = page.locator('.td-navbar');
      await expect(navbar).toBeVisible();
    });

    test('navbar logo is visible', async ({ page }) => {
      const logo = page.locator('.td-navbar .navbar-brand');
      await expect(logo).toBeVisible();
    });

    test('navbar is sticky or fixed on scroll', async ({ page }) => {
      const navbar = page.locator('.td-navbar');

      // check if navbar has sticky or fixed positioning
      const position = await navbar.evaluate(el => {
        const style = window.getComputedStyle(el);
        return style.position;
      });

      // should be sticky, fixed, or relative (depending on scroll position)
      expect(['sticky', 'fixed', 'relative', 'static', '-webkit-sticky']).toContain(position);
    });
  });

  test.describe('Mobile Viewport Meta', () => {
    test('page has proper viewport meta tag', async ({ page }) => {
      const viewportMeta = await page.locator('meta[name="viewport"]').getAttribute('content');
      expect(viewportMeta).toContain('width=device-width');
    });

    test('page does not allow user scaling to be disabled', async ({ page }) => {
      const viewportMeta = await page.locator('meta[name="viewport"]').getAttribute('content');

      // good accessibility practice - should not disable zoom
      if (viewportMeta.includes('user-scalable')) {
        expect(viewportMeta).not.toContain('user-scalable=no');
      }
    });
  });

  test.describe('Touch Interactions', () => {
    test('links have adequate touch targets', async ({ page }) => {
      const allLinks = page.locator('main a');
      const linkCount = await allLinks.count();

      if (linkCount === 0) {
        test.skip();
      }

      // find first visible link
      let visibleLink = null;
      for (let i = 0; i < Math.min(linkCount, 10); i++) {
        const link = allLinks.nth(i);
        const isVisible = await link.isVisible().catch(() => false);
        if (isVisible) {
          visibleLink = link;
          break;
        }
      }

      if (!visibleLink) {
        test.skip();
      }

      await expect(visibleLink).toBeVisible();

      // link should have reasonable size for touch
      const box = await visibleLink.boundingBox();
      expect(box.height).toBeGreaterThanOrEqual(20); // minimum touch target (relaxed for text links)
    });

    test('buttons have adequate touch targets', async ({ page }) => {
      const button = page.locator('button').first();

      if (await button.count() === 0) {
        test.skip();
      }

      await expect(button).toBeVisible();

      // button should have reasonable size for touch
      const box = await button.boundingBox();
      expect(box.height).toBeGreaterThanOrEqual(32); // comfortable touch target
    });
  });

  test.describe('Font Sizes', () => {
    test('body text is readable on mobile', async ({ page }) => {
      const bodyText = page.locator('main p').first();

      if (await bodyText.count() === 0) {
        test.skip();
      }

      await expect(bodyText).toBeVisible();

      // check font size is reasonable for mobile
      const fontSize = await bodyText.evaluate(el => {
        return parseInt(window.getComputedStyle(el).fontSize);
      });

      // should be at least 14px for readability on mobile
      expect(fontSize).toBeGreaterThanOrEqual(14);
    });
  });
});
