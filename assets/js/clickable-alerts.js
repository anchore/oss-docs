// clickable alert cards functionality
document.addEventListener('DOMContentLoaded', function() {
  document.querySelectorAll('.alert-clickable').forEach(function(alert) {
    alert.addEventListener('click', function(e) {
      // don't navigate if clicking on a link or interactive element
      if (e.target.tagName === 'A' || e.target.closest('a')) {
        return;
      }

      const url = this.getAttribute('data-url');
      if (url) {
        window.location.href = url;
      }
    });
  });
});
