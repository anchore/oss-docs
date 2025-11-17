document.addEventListener("DOMContentLoaded", () => {
  [...document.querySelectorAll(".capability-table,.config-table,.binary-details-table")]
    .filter(el => !el.closest(".table-wrapper"))
    .forEach(el => {
      const wrapper = document.createElement("div");
      wrapper.classList.add("table-wrapper");
      el.parentNode.insertBefore(wrapper, el);
      wrapper.appendChild(el);
    });
});
