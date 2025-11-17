document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll('abbr[title],[data-tooltip]').forEach(e => {
    const content = e.getAttribute("title") || e.getAttribute("data-tooltip")
    e.setAttribute("title", content)
    new bootstrap.Tooltip(e, {
      // trigger: 'click', // for debugging
      html: content.includes("<"),
      container: "body",
      popperConfig: cfg => {
        cfg.placement = "top-start"
        cfg.modifiers = cfg.modifiers.map(e => {
          if (e.name === "flip") {
            e.options.fallbackPlacements = ["top-end", ...e.options.fallbackPlacements]
          }
          return e
        })
        return cfg
      }
    })
  })
})
