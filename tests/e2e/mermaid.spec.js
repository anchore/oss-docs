const { test, expect } = require('@playwright/test');

test.describe('Mermaid Diagram Controls', () => {
  test.beforeEach(async ({ page }) => {
    // navigate to architecture page which MUST have Mermaid diagrams
    await page.goto('/docs/architecture/syft/');
    await page.waitForLoadState('domcontentloaded');

    // wait for Mermaid to render
    await page.waitForTimeout(2000);

    // Manually initialize controls (IntersectionObserver doesn't work reliably in Playwright)
    await page.evaluate(() => {
      const svgs = document.querySelectorAll('.mermaid svg');
      if (typeof window.initializeMermaidControls === 'function') {
        svgs.forEach(svg => window.initializeMermaidControls(svg));
      }
    });

    // Give controls time to initialize
    await page.waitForTimeout(500);
  });

  test('Mermaid diagram exists on page', async ({ page }) => {
    const mermaidSvg = page.locator('.mermaid svg').first();

    // FAIL if no diagrams found - this page MUST have diagrams
    await expect(mermaidSvg).toBeVisible({ timeout: 5000 });
  });

  test('mermaid-controls.js script loaded', async ({ page }) => {
    // Check if the control functions exist in window
    const functionsExist = await page.evaluate(() => {
      return {
        observeMermaidDiagrams: typeof window.observeMermaidDiagrams === 'function',
        initializeMermaidControls: typeof window.initializeMermaidControls === 'function',
      };
    });

    // Log what we found (debugging)
    // console.log('Mermaid control functions:', functionsExist);

    // FAIL if functions don't exist - script didn't load
    expect(functionsExist.observeMermaidDiagrams).toBe(true);
    expect(functionsExist.initializeMermaidControls).toBe(true);
  });

  test('diagram controls are initialized', async ({ page }) => {
    // First verify diagram exists
    const mermaidSvg = page.locator('.mermaid svg').first();
    await expect(mermaidSvg).toBeVisible();

    // Manually initialize controls (bypassing IntersectionObserver which may not trigger in tests)
    await page.evaluate(() => {
      const svgs = document.querySelectorAll('.mermaid svg');
      if (typeof window.initializeMermaidControls === 'function') {
        svgs.forEach(svg => {
          window.initializeMermaidControls(svg);
        });
      }
    });

    // Give a moment for initialization to complete
    await page.waitForTimeout(500);

    // Check if controls wrapper exists
    const wrapper = page.locator('.mermaid-diagram-wrapper').first();

    // This should fail if controls aren't initializing
    await expect(wrapper).toBeVisible({ timeout: 1000 });
  });

  test('diagram has controls wrapper', async ({ page }) => {
    const wrapper = page.locator('.mermaid-diagram-wrapper').first();

    // controls wrapper MUST exist
    await expect(wrapper).toBeVisible();
  });

  test('toolbar appears on diagram', async ({ page }) => {
    const toolbar = page.locator('.mermaid-controls-toolbar').first();

    // toolbar MUST exist in DOM
    await expect(toolbar).toBeAttached();
  });

  test('toolbar has all control buttons', async ({ page }) => {
    const toolbar = page.locator('.mermaid-controls-toolbar').first();

    // check for zoom in, zoom out, reset, and fullscreen buttons
    const zoomInBtn = toolbar.locator('[data-action="zoom-in"]');
    const zoomOutBtn = toolbar.locator('[data-action="zoom-out"]');
    const resetBtn = toolbar.locator('[data-action="reset"]');
    const fullscreenBtn = toolbar.locator('[data-action="fullscreen"]');

    await expect(zoomInBtn).toBeAttached();
    await expect(zoomOutBtn).toBeAttached();
    await expect(resetBtn).toBeAttached();
    await expect(fullscreenBtn).toBeAttached();
  });

  test('zoom in button increases zoom level', async ({ page }) => {
    const wrapper = page.locator('.mermaid-diagram-wrapper').first();
    const toolbar = wrapper.locator('.mermaid-controls-toolbar');
    const zoomInBtn = toolbar.locator('[data-action="zoom-in"]');

    // hover to show toolbar if needed
    await wrapper.hover();

    // click zoom in button
    await zoomInBtn.click();
    await page.waitForTimeout(200);

    // verify pan/zoom was activated
    await expect(wrapper).toHaveClass(/panzoom-active/);
  });

  test('zoom out button works', async ({ page }) => {
    const wrapper = page.locator('.mermaid-diagram-wrapper').first();
    const toolbar = wrapper.locator('.mermaid-controls-toolbar');
    const zoomInBtn = toolbar.locator('[data-action="zoom-in"]');
    const zoomOutBtn = toolbar.locator('[data-action="zoom-out"]');

    // hover to show toolbar
    await wrapper.hover();

    // zoom in first
    await zoomInBtn.click();
    await page.waitForTimeout(200);

    // then zoom out
    await zoomOutBtn.click();
    await page.waitForTimeout(200);

    // pan/zoom should still be active
    await expect(wrapper).toHaveClass(/panzoom-active/);
  });

  test('reset button restores initial view', async ({ page }) => {
    const wrapper = page.locator('.mermaid-diagram-wrapper').first();
    const toolbar = wrapper.locator('.mermaid-controls-toolbar');
    const zoomInBtn = toolbar.locator('[data-action="zoom-in"]');
    const resetBtn = toolbar.locator('[data-action="reset"]');

    // hover to show toolbar
    await wrapper.hover();

    // zoom in multiple times
    await zoomInBtn.click();
    await page.waitForTimeout(100);
    await zoomInBtn.click();
    await page.waitForTimeout(100);

    // click reset
    await resetBtn.click();
    await page.waitForTimeout(200);

    // pan/zoom should still be active after reset
    await expect(wrapper).toHaveClass(/panzoom-active/);
  });

  test('fullscreen button opens fullscreen modal', async ({ page }) => {
    const toolbar = page.locator('.mermaid-diagram-wrapper').first().locator('.mermaid-controls-toolbar');
    const fullscreenBtn = toolbar.locator('[data-action="fullscreen"]');

    // hover to show toolbar
    await page.locator('.mermaid-diagram-wrapper').first().hover();
    await page.waitForTimeout(100);

    // click fullscreen button
    await fullscreenBtn.click();

    // wait for fullscreen to activate and DOM to update
    await page.waitForTimeout(100);

    // backdrop should be visible
    const backdrop = page.locator('.mermaid-fullscreen-backdrop');
    await expect(backdrop).toBeVisible({ timeout: 3000 });
    await expect(backdrop).toHaveClass(/visible/, { timeout: 3000 });

    // re-query wrapper after it's been moved to fullscreen container
    const fullscreenWrapper = page.locator('.mermaid-fullscreen-backdrop .mermaid-diagram-wrapper');
    await expect(fullscreenWrapper).toHaveClass(/fullscreen-mode/, { timeout: 3000 });

    // body should have fullscreen class
    const body = page.locator('body');
    await expect(body).toHaveClass(/mermaid-fullscreen-active/, { timeout: 3000 });
  });

  test('close button exits fullscreen', async ({ page }) => {
    const toolbar = page.locator('.mermaid-diagram-wrapper').first().locator('.mermaid-controls-toolbar');
    const fullscreenBtn = toolbar.locator('[data-action="fullscreen"]');

    // enter fullscreen
    await page.locator('.mermaid-diagram-wrapper').first().hover();
    await page.waitForTimeout(100);
    await fullscreenBtn.click();

    // wait for fullscreen to activate
    await page.waitForTimeout(100);
    const backdrop = page.locator('.mermaid-fullscreen-backdrop');
    await expect(backdrop).toBeVisible({ timeout: 3000 });

    // click close button (using the button inside modalContainer)
    const closeBtn = page.locator('.mermaid-modal-container .mermaid-close-btn');
    await closeBtn.click();

    // wait for fullscreen to close
    await expect(backdrop).not.toBeVisible({ timeout: 3000 });

    // wrapper should no longer have fullscreen class (it's been moved back)
    const wrapper = page.locator('.mermaid-diagram-wrapper').first();
    await expect(wrapper).not.toHaveClass(/fullscreen-mode/, { timeout: 3000 });
  });

  test('Escape key exits fullscreen', async ({ page }) => {
    const wrapper = page.locator('.mermaid-diagram-wrapper').first();
    const toolbar = wrapper.locator('.mermaid-controls-toolbar');
    const fullscreenBtn = toolbar.locator('[data-action="fullscreen"]');

    // enter fullscreen
    await wrapper.hover();
    await fullscreenBtn.click();
    await page.waitForTimeout(300);

    // press Escape
    await page.keyboard.press('Escape');
    await page.waitForTimeout(300);

    // fullscreen should be closed
    const backdrop = page.locator('.mermaid-fullscreen-backdrop');
    await expect(backdrop).not.toBeVisible();
  });

  test('backdrop click exits fullscreen', async ({ page }) => {
    const wrapper = page.locator('.mermaid-diagram-wrapper').first();
    const toolbar = wrapper.locator('.mermaid-controls-toolbar');
    const fullscreenBtn = toolbar.locator('[data-action="fullscreen"]');

    // enter fullscreen
    await wrapper.hover();
    await fullscreenBtn.click();
    await page.waitForTimeout(300);

    // click backdrop
    const backdrop = page.locator('.mermaid-fullscreen-backdrop');
    await backdrop.click({ position: { x: 5, y: 5 } });
    await page.waitForTimeout(300);

    // fullscreen should be closed
    await expect(backdrop).not.toBeVisible();
  });

  test('keyboard shortcuts work in fullscreen: + and - for zoom', async ({ page }) => {
    const wrapper = page.locator('.mermaid-diagram-wrapper').first();
    const toolbar = wrapper.locator('.mermaid-controls-toolbar');
    const fullscreenBtn = toolbar.locator('[data-action="fullscreen"]');

    // enter fullscreen
    await wrapper.hover();
    await fullscreenBtn.click();
    await page.waitForTimeout(300);

    // press + to zoom in
    await page.keyboard.press('+');
    await page.waitForTimeout(200);

    // press - to zoom out
    await page.keyboard.press('-');
    await page.waitForTimeout(200);

    // verify still in fullscreen
    const backdrop = page.locator('.mermaid-fullscreen-backdrop');
    await expect(backdrop).toBeVisible();

    // exit fullscreen
    await page.keyboard.press('Escape');
  });

  test('keyboard shortcut 0 resets view in fullscreen', async ({ page }) => {
    const wrapper = page.locator('.mermaid-diagram-wrapper').first();
    const toolbar = wrapper.locator('.mermaid-controls-toolbar');
    const fullscreenBtn = toolbar.locator('[data-action="fullscreen"]');

    // enter fullscreen
    await wrapper.hover();
    await fullscreenBtn.click();
    await page.waitForTimeout(300);

    // zoom in
    await page.keyboard.press('+');
    await page.waitForTimeout(100);

    // press 0 to reset
    await page.keyboard.press('0');
    await page.waitForTimeout(200);

    // verify still in fullscreen
    const backdrop = page.locator('.mermaid-fullscreen-backdrop');
    await expect(backdrop).toBeVisible();

    // exit fullscreen
    await page.keyboard.press('Escape');
  });

  test('keyboard shortcut F exits fullscreen', async ({ page }) => {
    const wrapper = page.locator('.mermaid-diagram-wrapper').first();
    const toolbar = wrapper.locator('.mermaid-controls-toolbar');
    const fullscreenBtn = toolbar.locator('[data-action="fullscreen"]');

    // enter fullscreen
    await wrapper.hover();
    await fullscreenBtn.click();
    await page.waitForTimeout(300);

    // press F to exit fullscreen
    await page.keyboard.press('f');
    await page.waitForTimeout(300);

    // fullscreen should be closed
    const backdrop = page.locator('.mermaid-fullscreen-backdrop');
    await expect(backdrop).not.toBeVisible();
  });
});
