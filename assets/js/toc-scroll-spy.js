// minimal TOC scroll spy using IntersectionObserver
(function() {
  'use strict';

  function init() {
    const toc = document.getElementById('TableOfContents');
    if (!toc) return;

    const links = toc.querySelectorAll('a');
    const headings = Array.from(links).map(link => {
      const id = link.getAttribute('href').slice(1);
      return document.getElementById(id);
    }).filter(Boolean);

    if (headings.length === 0) return;

    let currentActiveId = headings[0].id; // start with first section active
    let isScrollingFromClick = false;

    // function to update active link and gliding marker position
    function setActiveLink(id) {
      currentActiveId = id;
      let activeLink = null;

      links.forEach(link => {
        const href = link.getAttribute('href').slice(1);
        if (href === currentActiveId) {
          link.classList.add('active');
          activeLink = link;
        } else {
          link.classList.remove('active');
        }
      });

      // update gliding marker position
      if (activeLink) {
        const linkRect = activeLink.getBoundingClientRect();
        const tocRect = toc.getBoundingClientRect();

        // calculate marker position relative to TOC container
        // center the marker vertically on the link
        const markerTop = linkRect.top - tocRect.top + (linkRect.height / 2) - 9;

        // update CSS custom properties to move the marker
        toc.style.setProperty('--toc-marker-top', `${markerTop}px`);
        toc.style.setProperty('--toc-marker-opacity', '1');
      }
    }

    // handle TOC link clicks
    links.forEach(link => {
      link.addEventListener('click', (e) => {
        const targetId = link.getAttribute('href').slice(1);
        setActiveLink(targetId);
        isScrollingFromClick = true;

        // reset flag after scroll completes
        setTimeout(() => {
          isScrollingFromClick = false;
        }, 1000);
      });
    });

    const observer = new IntersectionObserver(entries => {
      // skip observer updates if we just clicked a link
      if (isScrollingFromClick) return;

      // find the heading that's closest to the top of the viewport
      let closestHeading = null;
      let closestDistance = Infinity;

      headings.forEach(heading => {
        const rect = heading.getBoundingClientRect();
        const distance = Math.abs(rect.top);

        // if heading is above viewport or just entered, consider it
        if (rect.top <= window.innerHeight * 0.3 && distance < closestDistance) {
          closestDistance = distance;
          closestHeading = heading;
        }
      });

      // update active ID if we found a closest heading
      if (closestHeading) {
        setActiveLink(closestHeading.id);
      }
    }, {
      threshold: [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
    });

    headings.forEach(heading => observer.observe(heading));

    // set initial active state
    setActiveLink(currentActiveId);
  }

  // wait for DOM to be ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
