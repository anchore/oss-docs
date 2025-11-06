// mermaid-controls.js
// interactive pan/zoom/reset/fullscreen controls for Mermaid diagrams
// uses svg-pan-zoom library (proven compatible with Mermaid)

(function() {
  'use strict';

  // configuration
  const CONFIG = {
    svgPanZoomOptions: {
      // critical: don't interfere with Mermaid's default sizing
      fit: false,
      contain: false,
      center: false,
      // enable zoom and pan
      zoomEnabled: true,
      panEnabled: true,
      // disable built-in controls (we're building custom ones)
      controlIconsEnabled: false,
      dblClickZoomEnabled: false,
      mouseWheelZoomEnabled: false,
      // zoom limits
      minZoom: 0.1,
      maxZoom: 10,
      zoomScaleSensitivity: 0.3
    },
    showToolbarOnHover: true,
    toolbarFadeDelay: 300,
    fullscreenPadding: 60,
    animationDuration: 300
  };

  // store svg-pan-zoom instances
  const panZoomInstances = new WeakMap();

  // store wrapper metadata
  const wrapperMetadata = new WeakMap();

  // intersection observer for lazy initialization
  let intersectionObserver = null;

  /**
   * initialize controls for a mermaid diagram SVG
   * creates wrapper and toolbar but doesn't activate svg-pan-zoom yet
   */
  function initializeControls(svg) {
    if (!svg || wrapperMetadata.has(svg)) {
      return;
    }

    console.log('Mermaid controls: Initializing controls for SVG:', svg);

    // create wrapper and move SVG into it
    const wrapper = createWrapper(svg);

    // create toolbar with control buttons
    const toolbar = createToolbar();
    wrapper.appendChild(toolbar);

    // store metadata
    wrapperMetadata.set(svg, {
      wrapper,
      toolbar,
      initialized: false,
      initialState: null
    });

    // setup event handlers
    setupToolbarHandlers(svg);

    if (CONFIG.showToolbarOnHover) {
      setupHoverBehavior(svg);
    }

    console.log('Mermaid controls: Initialization complete for SVG:', svg);
  }

  /**
   * activate svg-pan-zoom on first user interaction
   */
  function activatePanZoom(svg) {
    const metadata = wrapperMetadata.get(svg);
    if (!metadata) {
      console.error('Mermaid controls: Cannot activate pan/zoom - metadata not found for SVG:', svg);
      return null;
    }

    // return existing instance if already initialized
    if (panZoomInstances.has(svg)) {
      return panZoomInstances.get(svg);
    }

    // capture original dimensions BEFORE svg-pan-zoom modifies the SVG
    // (svg-pan-zoom removes viewBox, which causes height collapse)
    const rect = svg.getBoundingClientRect();
    const originalHeight = rect.height;
    const originalWidth = rect.width;

    // store original dimensions for wrapper sizing and fullscreen restoration
    metadata.originalDimensions = {
      width: originalWidth,
      height: originalHeight
    };

    // set explicit height on wrapper to prevent collapse when viewBox is removed
    metadata.wrapper.style.height = `${originalHeight}px`;

    // initialize svg-pan-zoom
    const panZoom = svgPanZoom(svg, CONFIG.svgPanZoomOptions);
    panZoomInstances.set(svg, panZoom);

    // capture initial state for reset functionality
    metadata.initialState = {
      zoom: panZoom.getZoom(),
      pan: panZoom.getPan()
    };
    metadata.initialized = true;

    // add visual indicator that pan/zoom is active
    metadata.wrapper.classList.add('panzoom-active');

    return panZoom;
  }

  /**
   * create wrapper div around SVG
   */
  function createWrapper(svg) {
    const wrapper = document.createElement('div');
    wrapper.className = 'mermaid-diagram-wrapper';

    // insert wrapper before SVG and move SVG into it
    const parent = svg.parentNode;
    parent.insertBefore(wrapper, svg);
    wrapper.appendChild(svg);

    return wrapper;
  }

  /**
   * create toolbar with control buttons
   */
  function createToolbar() {
    const toolbar = document.createElement('div');
    toolbar.className = 'mermaid-controls-toolbar';
    toolbar.innerHTML = `
      <button class="mermaid-control-btn" data-action="zoom-in" title="Zoom In" aria-label="Zoom In">
        <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
          <path d="M8 4a.5.5 0 0 1 .5.5v3h3a.5.5 0 0 1 0 1h-3v3a.5.5 0 0 1-1 0v-3h-3a.5.5 0 0 1 0-1h3v-3A.5.5 0 0 1 8 4z"/>
        </svg>
      </button>
      <button class="mermaid-control-btn" data-action="zoom-out" title="Zoom Out" aria-label="Zoom Out">
        <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
          <path d="M4 8a.5.5 0 0 1 .5-.5h7a.5.5 0 0 1 0 1h-7A.5.5 0 0 1 4 8z"/>
        </svg>
      </button>
      <button class="mermaid-control-btn" data-action="reset" title="Reset View" aria-label="Reset View">
        <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
          <path d="M8 3a5 5 0 1 0 4.546 2.914.5.5 0 0 1 .908-.417A6 6 0 1 1 8 2v1z"/>
          <path d="M8 4.466V.534a.25.25 0 0 1 .41-.192l2.36 1.966c.12.1.12.284 0 .384L8.41 4.658A.25.25 0 0 1 8 4.466z"/>
        </svg>
      </button>
      <button class="mermaid-control-btn" data-action="fullscreen" title="Fullscreen" aria-label="Toggle Fullscreen">
        <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
          <path d="M1.5 1a.5.5 0 0 0-.5.5v4a.5.5 0 0 1-1 0v-4A1.5 1.5 0 0 1 1.5 0h4a.5.5 0 0 1 0 1h-4zM10 .5a.5.5 0 0 1 .5-.5h4A1.5 1.5 0 0 1 16 1.5v4a.5.5 0 0 1-1 0v-4a.5.5 0 0 0-.5-.5h-4a.5.5 0 0 1-.5-.5zM.5 10a.5.5 0 0 1 .5.5v4a.5.5 0 0 0 .5.5h4a.5.5 0 0 1 0 1h-4A1.5 1.5 0 0 1 0 14.5v-4a.5.5 0 0 1 .5-.5zm15 0a.5.5 0 0 1 .5.5v4a1.5 1.5 0 0 1-1.5 1.5h-4a.5.5 0 0 1 0-1h4a.5.5 0 0 0 .5-.5v-4a.5.5 0 0 1 .5-.5z"/>
        </svg>
      </button>
    `;
    return toolbar;
  }

  /**
   * setup toolbar button handlers
   */
  function setupToolbarHandlers(svg) {
    const metadata = wrapperMetadata.get(svg);
    if (!metadata) {
      console.error('Mermaid controls: Cannot setup toolbar handlers - metadata not found for SVG:', svg);
      return;
    }

    metadata.toolbar.addEventListener('click', (e) => {
      const btn = e.target.closest('.mermaid-control-btn');
      if (!btn) return;

      const action = btn.dataset.action;
      console.log('Mermaid controls: Button clicked - action:', action);

      // fullscreen doesn't require pan/zoom activation
      if (action === 'fullscreen') {
        console.log('Mermaid controls: Fullscreen button clicked, toggling fullscreen for SVG:', svg);
        toggleFullscreen(svg);
        return;
      }

      // activate svg-pan-zoom on first zoom/pan interaction
      const panZoom = activatePanZoom(svg);
      if (!panZoom) return;

      switch (action) {
        case 'zoom-in':
          panZoom.zoomIn();
          break;
        case 'zoom-out':
          panZoom.zoomOut();
          break;
        case 'reset':
          resetView(svg);
          break;
      }
    });
  }

  /**
   * reset view to initial state (normal mode) or fit/center (fullscreen mode)
   */
  function resetView(svg) {
    const metadata = wrapperMetadata.get(svg);
    const panZoom = panZoomInstances.get(svg);

    if (!panZoom) return;

    const isFullscreen = metadata?.wrapper.classList.contains('fullscreen-mode');

    if (isFullscreen) {
      // in fullscreen: fit and center the diagram (maximize view)
      panZoom.resize();
      panZoom.fit();
      panZoom.center();
    } else {
      // not in fullscreen: restore to initial state
      if (!metadata?.initialState) return;
      const { zoom, pan } = metadata.initialState;
      panZoom.zoom(zoom);
      panZoom.pan(pan);
    }
  }

  /**
   * setup hover behavior to show/hide toolbar
   */
  function setupHoverBehavior(svg) {
    const metadata = wrapperMetadata.get(svg);
    if (!metadata) return;

    let hideTimeout;

    metadata.wrapper.addEventListener('mouseenter', () => {
      clearTimeout(hideTimeout);
      metadata.toolbar.classList.add('visible');
    });

    metadata.wrapper.addEventListener('mouseleave', () => {
      // don't hide in fullscreen
      if (metadata.wrapper.classList.contains('fullscreen-mode')) {
        return;
      }
      hideTimeout = setTimeout(() => {
        metadata.toolbar.classList.remove('visible');
      }, CONFIG.toolbarFadeDelay);
    });
  }

  /**
   * toggle fullscreen mode
   */
  function toggleFullscreen(svg) {
    const metadata = wrapperMetadata.get(svg);
    if (!metadata) {
      console.error('Mermaid controls: Cannot toggle fullscreen - metadata not found for SVG:', svg);
      return;
    }

    const isFullscreen = metadata.wrapper.classList.contains('fullscreen-mode');

    if (!isFullscreen) {
      enterFullscreen(svg);
    } else {
      exitFullscreen(svg);
    }
  }

  /**
   * enter fullscreen mode
   */
  function enterFullscreen(svg) {
    const metadata = wrapperMetadata.get(svg);
    if (!metadata) {
      console.error('Mermaid controls: Cannot enter fullscreen - metadata not found for SVG:', svg);
      return;
    }

    console.log('Mermaid controls: Entering fullscreen mode for SVG:', svg);

    // activate pan/zoom if not already active
    const panZoom = activatePanZoom(svg);

    // save original parent for restoration later
    metadata.originalParent = metadata.wrapper.parentNode;

    // save current inline styles and clear them to allow fullscreen sizing
    metadata.savedInlineStyles = {
      wrapper: {
        width: metadata.wrapper.style.width,
        height: metadata.wrapper.style.height
      },
      svg: {
        overflow: svg.style.overflow,
        maxWidth: svg.style.maxWidth,
        width: svg.style.width,
        height: svg.style.height
      }
    };

    // clear wrapper styles
    metadata.wrapper.style.width = '';
    metadata.wrapper.style.height = '';

    // clear SVG inline styles to allow fullscreen sizing
    svg.style.overflow = '';
    svg.style.maxWidth = '';
    svg.style.width = '';
    svg.style.height = '';

    // create backdrop
    const backdrop = document.createElement('div');
    backdrop.className = 'mermaid-fullscreen-backdrop';

    // create modal container
    const modalContainer = document.createElement('div');
    modalContainer.className = 'mermaid-modal-container';

    // create close button
    const closeBtn = document.createElement('button');
    closeBtn.className = 'mermaid-close-btn';
    closeBtn.title = 'Close (Esc)';
    closeBtn.setAttribute('aria-label', 'Close fullscreen');
    closeBtn.innerHTML = `
      <svg width="20" height="20" viewBox="0 0 16 16" fill="currentColor">
        <path d="M2.146 2.854a.5.5 0 1 1 .708-.708L8 7.293l5.146-5.147a.5.5 0 0 1 .708.708L8.707 8l5.147 5.146a.5.5 0 0 1-.708.708L8 8.707l-5.146 5.147a.5.5 0 0 1-.708-.708L7.293 8 2.146 2.854Z"/>
      </svg>
    `;

    // assemble structure: backdrop > modalContainer > wrapper + closeBtn
    document.body.appendChild(backdrop);
    backdrop.appendChild(modalContainer);
    modalContainer.appendChild(metadata.wrapper);
    modalContainer.appendChild(closeBtn);

    // store references
    metadata.backdrop = backdrop;
    metadata.modalContainer = modalContainer;
    metadata.closeBtn = closeBtn;

    // animate in
    requestAnimationFrame(() => {
      backdrop.classList.add('visible');
    });

    // enter fullscreen mode
    metadata.wrapper.classList.add('fullscreen-mode');
    document.body.classList.add('mermaid-fullscreen-active');
    metadata.toolbar.classList.add('visible');

    console.log('Mermaid controls: Fullscreen modal created and displayed');

    // fit diagram to fullscreen modal container
    setTimeout(() => {
      if (panZoom) {
        panZoom.resize(); // update internal dimensions after DOM move
        panZoom.fit();    // fit content to container (handles aspect ratio correctly)
        panZoom.center(); // center content
      }
    }, 100);

    // close on backdrop click (but not modal container click)
    backdrop.addEventListener('click', (e) => {
      if (e.target === backdrop) {
        exitFullscreen(svg);
      }
    });

    // close button handler
    closeBtn.addEventListener('click', () => exitFullscreen(svg));

    // close on ESC key
    const escHandler = (e) => {
      if (e.key === 'Escape') {
        exitFullscreen(svg);
        document.removeEventListener('keydown', escHandler);
      }
    };
    document.addEventListener('keydown', escHandler);
    metadata.escHandler = escHandler;

    // keyboard shortcuts
    const keyHandler = (e) => {
      const panZoom = panZoomInstances.get(svg);
      if (!panZoom) return;

      if (e.key === '+' || e.key === '=') {
        e.preventDefault();
        panZoom.zoomIn();
      } else if (e.key === '-' || e.key === '_') {
        e.preventDefault();
        panZoom.zoomOut();
      } else if (e.key === '0') {
        e.preventDefault();
        resetView(svg);
      } else if (e.key === 'f' || e.key === 'F') {
        e.preventDefault();
        exitFullscreen(svg);
      }
    };
    document.addEventListener('keydown', keyHandler);
    metadata.keyHandler = keyHandler;
  }

  /**
   * exit fullscreen mode
   */
  function exitFullscreen(svg) {
    const metadata = wrapperMetadata.get(svg);
    if (!metadata) return;

    metadata.wrapper.classList.remove('fullscreen-mode');
    document.body.classList.remove('mermaid-fullscreen-active');

    // restore wrapper to original DOM location
    if (metadata.originalParent) {
      metadata.originalParent.appendChild(metadata.wrapper);
      metadata.originalParent = null;
    }

    // restore original inline styles to wrapper and SVG
    if (metadata.savedInlineStyles) {
      // restore wrapper styles
      metadata.wrapper.style.width = metadata.savedInlineStyles.wrapper.width;
      metadata.wrapper.style.height = metadata.savedInlineStyles.wrapper.height;

      // restore SVG inline styles
      svg.style.overflow = metadata.savedInlineStyles.svg.overflow;
      svg.style.maxWidth = metadata.savedInlineStyles.svg.maxWidth;
      svg.style.width = metadata.savedInlineStyles.svg.width;
      svg.style.height = metadata.savedInlineStyles.svg.height;

      metadata.savedInlineStyles = null;
    }

    // animate backdrop out
    if (metadata.backdrop) {
      metadata.backdrop.classList.remove('visible');
      setTimeout(() => {
        metadata.backdrop.remove();
        metadata.backdrop = null;
      }, CONFIG.animationDuration);
    }

    // clean up references
    metadata.modalContainer = null;
    metadata.closeBtn = null;

    // remove event listeners
    if (metadata.escHandler) {
      document.removeEventListener('keydown', metadata.escHandler);
      metadata.escHandler = null;
    }
    if (metadata.keyHandler) {
      document.removeEventListener('keydown', metadata.keyHandler);
      metadata.keyHandler = null;
    }

    // fit diagram to normal container after exiting fullscreen
    setTimeout(() => {
      const panZoom = panZoomInstances.get(svg);
      if (panZoom) {
        panZoom.resize(); // update internal dimensions after DOM move
        panZoom.fit();    // fit content to container
        panZoom.center(); // center content

        // update initialState to this new fitted state
        // makes reset button a no-op when diagram is already correctly fitted
        metadata.initialState = {
          zoom: panZoom.getZoom(),
          pan: panZoom.getPan()
        };
      }
    }, 100);
  }

  /**
   * setup intersection observer for lazy initialization
   */
  function setupIntersectionObserver() {
    intersectionObserver = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          const svg = entry.target;
          if (!wrapperMetadata.has(svg)) {
            initializeControls(svg);
          }
          intersectionObserver.unobserve(svg);
        }
      });
    }, {
      threshold: 0.1,
      rootMargin: '50px'
    });
  }

  /**
   * observe all mermaid diagrams
   */
  function observeAllDiagrams() {
    if (!intersectionObserver) {
      setupIntersectionObserver();
    }

    document.querySelectorAll('.mermaid svg').forEach((svg) => {
      if (!wrapperMetadata.has(svg)) {
        intersectionObserver.observe(svg);
      }
    });
  }

  // expose initialization functions for Mermaid partial
  window.initializeMermaidControls = initializeControls;
  window.observeMermaidDiagrams = observeAllDiagrams;

})();
