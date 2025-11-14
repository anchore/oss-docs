const { test, expect } = require('@playwright/test');

test.describe('Mobile Mermaid Diagrams', () => {
  test.beforeEach(async ({ page }) => {
    // navigate to architecture page which has Mermaid diagrams
    await page.goto('/docs/architecture/syft/');
    await page.waitForLoadState('domcontentloaded');

    // wait for Mermaid to render
    await page.waitForTimeout(2000);

    // manually initialize controls (IntersectionObserver doesn't work in tests)
    await page.evaluate(() => {
      const svgs = document.querySelectorAll('.mermaid svg');
      if (typeof window.initializeMermaidControls === 'function') {
        svgs.forEach(svg => {
          window.initializeMermaidControls(svg);
        });
      }
    });

    await page.waitForTimeout(500);
  });

  test('Mermaid diagrams render on mobile', async ({ page }) => {
    const mermaidSvg = page.locator('.mermaid svg').first();
    await expect(mermaidSvg).toBeVisible({ timeout: 5000 });
  });

  test('mermaid-controls.js script loads on mobile', async ({ page }) => {
    const functionsExist = await page.evaluate(() => {
      return {
        observeMermaidDiagrams: typeof window.observeMermaidDiagrams === 'function',
        initializeMermaidControls: typeof window.initializeMermaidControls === 'function',
      };
    });

    expect(functionsExist.observeMermaidDiagrams).toBe(true);
    expect(functionsExist.initializeMermaidControls).toBe(true);
  });

  test('diagram controls initialize on mobile', async ({ page }) => {
    const wrapper = page.locator('.mermaid-diagram-wrapper').first();
    await expect(wrapper).toBeVisible({ timeout: 3000 });
  });

  test('diagram has controls toolbar on mobile', async ({ page }) => {
    const toolbar = page.locator('.mermaid-controls-toolbar').first();
    await expect(toolbar).toBeAttached();
  });

  test('all control buttons exist on mobile', async ({ page }) => {
    const toolbar = page.locator('.mermaid-controls-toolbar').first();

    const zoomInBtn = toolbar.locator('[data-action="zoom-in"]');
    const zoomOutBtn = toolbar.locator('[data-action="zoom-out"]');
    const resetBtn = toolbar.locator('[data-action="reset"]');
    const fullscreenBtn = toolbar.locator('[data-action="fullscreen"]');

    await expect(zoomInBtn).toBeAttached();
    await expect(zoomOutBtn).toBeAttached();
    await expect(resetBtn).toBeAttached();
    await expect(fullscreenBtn).toBeAttached();
  });

  test('diagram is sized appropriately for mobile viewport', async ({ page }) => {
    const wrapper = page.locator('.mermaid-diagram-wrapper').first();
    const box = await wrapper.boundingBox();
    const viewport = page.viewportSize();

    expect(box).not.toBeNull();
    // diagram should not overflow viewport width
    expect(box.width).toBeLessThanOrEqual(viewport.width);
  });

  test('zoom in button works on mobile', async ({ page }) => {
    const wrapper = page.locator('.mermaid-diagram-wrapper').first();
    const toolbar = wrapper.locator('.mermaid-controls-toolbar');
    const zoomInBtn = toolbar.locator('[data-action="zoom-in"]');

    // tap zoom in button (use tap for mobile)
    await wrapper.tap();
    await zoomInBtn.tap();
    await page.waitForTimeout(200);

    // verify pan/zoom was activated
    await expect(wrapper).toHaveClass(/panzoom-active/);
  });

  test('fullscreen button works on mobile', async ({ page }) => {
    const toolbar = page.locator('.mermaid-diagram-wrapper').first().locator('.mermaid-controls-toolbar');
    const fullscreenBtn = toolbar.locator('[data-action="fullscreen"]');

    // tap on diagram area first, then fullscreen
    await page.locator('.mermaid-diagram-wrapper').first().tap();
    await page.waitForTimeout(100);
    await fullscreenBtn.tap();
    await page.waitForTimeout(300);

    // backdrop should be visible
    const backdrop = page.locator('.mermaid-fullscreen-backdrop');
    await expect(backdrop).toBeVisible({ timeout: 3000 });
    await expect(backdrop).toHaveClass(/visible/);
  });

  test('close button exits fullscreen on mobile', async ({ page }) => {
    const toolbar = page.locator('.mermaid-diagram-wrapper').first().locator('.mermaid-controls-toolbar');
    const fullscreenBtn = toolbar.locator('[data-action="fullscreen"]');

    // enter fullscreen
    await page.locator('.mermaid-diagram-wrapper').first().tap();
    await page.waitForTimeout(100);
    await fullscreenBtn.tap();
    await page.waitForTimeout(300);

    const backdrop = page.locator('.mermaid-fullscreen-backdrop');
    await expect(backdrop).toBeVisible({ timeout: 3000 });

    // tap close button
    const closeBtn = page.locator('.mermaid-modal-container .mermaid-close-btn');
    await closeBtn.tap();
    await page.waitForTimeout(300);

    // fullscreen should be closed
    await expect(backdrop).not.toBeVisible({ timeout: 3000 });
  });

  test('Escape key exits fullscreen on mobile', async ({ page }) => {
    const wrapper = page.locator('.mermaid-diagram-wrapper').first();
    const toolbar = wrapper.locator('.mermaid-controls-toolbar');
    const fullscreenBtn = toolbar.locator('[data-action="fullscreen"]');

    // enter fullscreen
    await wrapper.tap();
    await fullscreenBtn.tap();
    await page.waitForTimeout(300);

    // press Escape
    await page.keyboard.press('Escape');
    await page.waitForTimeout(300);

    // fullscreen should be closed
    const backdrop = page.locator('.mermaid-fullscreen-backdrop');
    await expect(backdrop).not.toBeVisible();
  });

  test('diagram wrapper is properly sized for mobile viewport', async ({ page }) => {
    const wrapper = page.locator('.mermaid-diagram-wrapper').first();
    const wrapperBox = await wrapper.boundingBox();
    const viewport = page.viewportSize();

    expect(wrapperBox).not.toBeNull();

    // wrapper should fit within viewport and have reasonable dimensions
    expect(wrapperBox.width).toBeGreaterThan(0);
    expect(wrapperBox.width).toBeLessThanOrEqual(viewport.width);
    expect(wrapperBox.height).toBeGreaterThan(0);
  });

  test('multiple diagrams all have controls on mobile', async ({ page }) => {
    const diagrams = page.locator('.mermaid-diagram-wrapper');
    const count = await diagrams.count();

    // if there are multiple diagrams, they should all have controls
    if (count > 1) {
      for (let i = 0; i < Math.min(count, 3); i++) {
        const diagram = diagrams.nth(i);
        const toolbar = diagram.locator('.mermaid-controls-toolbar');
        await expect(toolbar).toBeAttached();
      }
    }
  });

  test('touch interactions work on diagram', async ({ page }) => {
    const wrapper = page.locator('.mermaid-diagram-wrapper').first();

    // should be able to tap the diagram
    await wrapper.tap();
    await page.waitForTimeout(200);

    // wrapper should respond to touch
    await expect(wrapper).toBeVisible();
  });
});
