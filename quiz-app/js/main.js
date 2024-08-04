// Add home icon to the first nav item
document.addEventListener("DOMContentLoaded", function () {
  const firstNavItem = document.querySelector("#main-nav ul li:first-child a");
  if (firstNavItem) {
    firstNavItem.innerHTML = '<i class="fas fa-home"></i>';
    firstNavItem.title = "Home";
  }
});

// Dark mode toggle
function toggleDarkMode() {
  document.body.classList.toggle("dark-mode");
  localStorage.setItem(
    "darkMode",
    document.body.classList.contains("dark-mode")
  );
}

// Check for saved dark mode preference
if (localStorage.getItem("darkMode") === "true") {
  document.body.classList.add("dark-mode");
}

// Sidebar toggle (you'll need to implement the sidebar HTML)
function toggleSidebar() {
  const sidebar = document.getElementById("sidebar");
  if (sidebar) {
    sidebar.classList.toggle("open");
  } else {
    console.log("Sidebar not implemented yet");
  }
}

// You can add more global functionality here
