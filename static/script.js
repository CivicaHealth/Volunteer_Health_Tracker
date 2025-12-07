// Example: Add a confirmation before deleting a shot or reminder
document.addEventListener("DOMContentLoaded", function() {
  document.querySelectorAll("button[name='remove_shot']").forEach(function(btn) {
    btn.addEventListener("click", function(e) {
      if (!confirm("Are you sure you want to remove this shot type?")) {
        e.preventDefault();
      }
    });
  });

  // Placeholder for future dashboard interactivity
  // You can add functions here for quick UI feedback!
});
