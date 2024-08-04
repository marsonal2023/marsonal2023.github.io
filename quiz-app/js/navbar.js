const appStructure = {
  Home: "index.html",
  Surgery: { "Quiz 1": "surgery/quiz1.html", "Quiz 2": "surgery/quiz2.html" },
  Women: { "Quiz 1": "women/quiz1.html", "Quiz 2": "women/quiz2.html" },
};

function createNavbar() {
  const nav = document.getElementById("main-nav");
  if (!nav) return;

  nav.innerHTML = `
    <a href="${appStructure.Home}" class="nav-link home-link"><i class="fas fa-home"></i></a>
    <div class="dropdown">
      <button class="dropbtn" id="category-btn">Categories</button>
      <div class="dropdown-content" id="dropdown-content"></div>
    </div>
    <div class="navbar-actions">
      <button onclick="location.reload();" class="icon-button"><i class="fas fa-sync-alt"></i></button>
      <button onclick="toggleDarkMode()" class="icon-button"><i class="fas fa-moon"></i></button>
      <button class="icon-button" id="menu-toggle"><i class="fas fa-bars"></i></button>
    </div>
  `;

  const dropdownContent = document.getElementById("dropdown-content");
  Object.entries(appStructure).forEach(([category, content]) => {
    if (typeof content === "object") {
      const subcontent = Object.entries(content)
        .map(([name, link]) => `<a href="${link}" class="nav-link">${name}</a>`)
        .join("");
      dropdownContent.innerHTML += `
        <div class="category">
          <span class="category-link">
            ${category}
            <i class="fas fa-chevron-right category-icon"></i>
          </span>
          <div class="subcategory-content">${subcontent}</div>
        </div>
      `;
    }
  });

  document.querySelectorAll(".category-link").forEach((category) => {
    category.addEventListener("click", (e) => {
      e.preventDefault();
      const subcategory = category.nextElementSibling;
      const icon = category.querySelector(".category-icon");
      subcategory.style.display =
        subcategory.style.display === "block" ? "none" : "block";
      icon.style.transform =
        subcategory.style.display === "block"
          ? "rotate(90deg)"
          : "rotate(0deg)";
    });
  });

  document
    .getElementById("category-btn")
    .addEventListener("click", toggleDropdown);
}
function getRelativePath(href) {
  const currentPath = window.location.pathname.split("/");
  const projectRootIndex = currentPath.indexOf("quiz-app");
  if (projectRootIndex === -1) return href;
  const depth = currentPath.length - projectRootIndex - 2;
  return depth > 0 ? "../".repeat(depth) + href : href;
}

function updateLinks() {
  document.querySelectorAll(".nav-link").forEach((link) => {
    const href = link.getAttribute("href");
    if (href && href !== "#") link.setAttribute("href", getRelativePath(href));
  });
}

function updateCategoryButton() {
  const categoryBtn = document.getElementById("category-btn");
  const currentPath = window.location.pathname;
  for (const [category, content] of Object.entries(appStructure)) {
    if (typeof content === "object") {
      for (const [name, link] of Object.entries(content)) {
        if (currentPath.includes(link)) {
          categoryBtn.textContent = `${category}: ${name}`;
          return;
        }
      }
    }
  }
  categoryBtn.textContent = "Categories";
}

function toggleDropdown() {
  const dropdown = document.getElementById("dropdown-content");
  dropdown.style.display =
    dropdown.style.display === "block" ? "none" : "block";
}

function toggleDarkMode() {
  document.body.classList.toggle("dark-mode");
}

document.addEventListener("DOMContentLoaded", () => {
  createNavbar();
  updateLinks();
  updateCategoryButton();
});
