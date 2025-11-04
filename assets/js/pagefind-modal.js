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
      pagefindUI = new PagefindUI({
        element: "#pagefind-search-container",
        showSubResults: true,
        showImages: false,
        excerptLength: 15,
        autofocus: true,
        debounceTimeoutMs: 500,
        processTerm: (term) => {
          // require at least 2 characters to start searching (e.g. "jq"... which is why we don't have this at 3)
          return term.length >= 2 ? term : "";
        }
      });
    }
  }

  // open modal
  function openModal() {
    modal.showModal();

    // initialize Pagefind after dialog is rendered
    requestAnimationFrame(() => {
      initPagefind();
      // focus input after PagefindUI creates it
      setTimeout(() => {
        const input = modal.querySelector('.pagefind-ui__search-input');
        if (input) input.focus();
      }, 50);
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
