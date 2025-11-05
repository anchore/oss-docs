// pagefind search modal functionality
document.addEventListener('DOMContentLoaded', function() {
  const modal = document.getElementById('pagefind-modal');
  const button = document.getElementById('pagefind-search-button');
  const closeBtn = document.getElementById('pagefind-close');
  let pagefindUI = null;

  if (!modal || !button) return;

  // initialize Pagefind UI when modal first opens
  function initPagefind() {
    if (!pagefindUI) {
      // lazy-load Pagefind CSS on first modal open (performance optimization)
      if (!document.querySelector('link[href="/pagefind/pagefind-ui.css"]')) {
        const link = document.createElement('link');
        link.rel = 'stylesheet';
        link.href = '/pagefind/pagefind-ui.css';
        document.head.appendChild(link);
      }

      pagefindUI = new PagefindUI({
        element: "#pagefind-search-container",
        showSubResults: true,
        showImages: false,
        excerptLength: 15,
        autofocus: true,
        debounceTimeoutMs: 500,
        showEmptyFilters: true,
        filters: {
          section: "Section",
          project: "Tags"
        },
        translations: {
          placeholder: "Search"
        },
        processTerm: (term) => {
          // require at least 2 characters to start searching (e.g. "jq"... which is why we don't have this at 3)
          return term.length >= 2 ? term : "";
        }
      });
    }
  }

  // watch for when filters appear and auto-expand Section filter
  let filtersObserver = null;
  let sectionFilterExpanded = false;

  function setupFiltersObserver() {
    if (filtersObserver) return;

    const searchContainer = modal.querySelector('#pagefind-search-container');
    if (!searchContainer) return;

    filtersObserver = new MutationObserver(() => {
      // only expand Section filter once per modal opening
      if (sectionFilterExpanded) return;

      const filterNames = modal.querySelectorAll('.pagefind-ui__filter-name');
      const sectionFilter = Array.from(filterNames).find(el => el.textContent.trim() === 'Section');

      if (sectionFilter) {
        sectionFilter.click();
        sectionFilterExpanded = true;
      }
    });

    filtersObserver.observe(searchContainer, {
      childList: true,
      subtree: true
    });
  }

  // open modal
  function openModal() {
    modal.showModal();
    sectionFilterExpanded = false; // reset flag for new modal opening

    // initialize Pagefind after dialog is rendered
    requestAnimationFrame(() => {
      initPagefind();
      // focus input after PagefindUI creates it
      setTimeout(() => {
        const input = modal.querySelector('.pagefind-ui__search-input');
        if (input) input.focus();
      }, 50);

      // set up observer to auto-expand Section filter when it appears
      setupFiltersObserver();
    });
  }

  // close modal
  function closeModal() {
    modal.close();
  }

  // event listeners
  button.addEventListener('click', openModal);
  if (closeBtn) closeBtn.addEventListener('click', closeModal);

  // close on backdrop click
  modal.addEventListener('click', (e) => {
    if (e.target === modal) closeModal();
  });

  // keyboard shortcuts (Ctrl/Cmd + K)
  document.addEventListener('keydown', (e) => {
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
      e.preventDefault();
      modal.open ? closeModal() : openModal();
    }
    // Escape to close
    if (e.key === 'Escape' && modal.open) {
      closeModal();
    }
  });
});
