document.addEventListener("DOMContentLoaded", function () {
  // Function to get correct path based on current location
  function getCorrectPath() {
    const currentPath = window.location.pathname;
    const isInSubfolder =
      currentPath.includes("/med/") ||
      currentPath.includes("/dental/") ||
      currentPath.includes("/pharmacy/") ||
      currentPath.includes("/physio/") ||
      currentPath.includes("/nursing/") ||
      currentPath.includes("/vet/");
    return isInSubfolder ? "../" : "./";
  }

  const basePath = getCorrectPath();

  const menuItems = [
    {
      name: "الرئيسية",
      link: basePath + "index.html",
      icon: "fas fa-home",
    },
    {
      name: "Surgery",
      subItems: [
        { name: "معلومات عن الامتحان", link: basePath + "med/info.html" },
        { name: "أداء الامتحانات والتدريب", link: basePath + "med/exam.html0",
          subItems: [
            { name: "امتحان 1", link: basePath + "med/exam1.html" },
            { name: "امتحان 2", link: basePath + "med/exam2.html" },
            { name: "امتحان 3", link: basePath + "med/exam3.html" },
            { name: "امتحان 4", link: basePath + "med/exam4.html" },
            { name: "امتحان 5", link: basePath + "med/exam5.html" },
            { name: "امتحان 6", link: basePath + "med/exam6.html" },
            { name: "امتحان 7", link: basePath + "med/exam7.html" },
            { name: "امتحان 8", link: basePath + "med/exam8.html" },
            { name: "امتحان 9", link: basePath + "med/exam9.html" },
            { name: "امتحان 10", link: basePath + "med/exam10.html" },
          ]
         },
        { name: "بنك الأسئلة", link: basePath + "med/qb.html" },
      ],
    },
    {
      name: "OBGYN",
      subItems: [
        { name: "معلومات عن الامتحان", link: basePath + "dental/info.html" },
        {
          name: "أداء الامتحانات والتدريب",
          link: basePath + "dental/exam.html",
        },
        { name: "بنك الأسئلة", link: basePath + "dental/questions.html" },
      ],
    },
    {
      name: "الصيدلة",
      subItems: [
        { name: "معلومات عن الامتحان", link: basePath + "pharmacy/info.html" },
        {
          name: "أداء الامتحانات والتدريب",
          link: basePath + "pharmacy/exam.html",
        },
        { name: "بنك الأسئلة", link: basePath + "pharmacy/questions.html" },
      ],
    },
    {
      name: "العلاج الطبيعى",
      subItems: [
        { name: "معلومات عن الامتحان", link: basePath + "physio/info.html" },
        {
          name: "أداء الامتحانات والتدريب",
          link: basePath + "physio/exam.html",
        },
        { name: "بنك الأسئلة", link: basePath + "physio/questions.html" },
      ],
    },
    {
      name: "التمريض",
      subItems: [
        { name: "معلومات عن الامتحان", link: basePath + "nursing/info.html" },
        {
          name: "أداء الامتحانات والتدريب",
          link: basePath + "nursing/exam.html",
        },
        { name: "بنك الأسئلة", link: basePath + "nursing/questions.html" },
      ],
    },
    {
      name: "الطب البيطرى",
      subItems: [
        { name: "معلومات عن الامتحان", link: basePath + "vet/info.html" },
        { name: "أداء الامتحانات والتدريب", link: basePath + "vet/exam.html" },
        { name: "بنك الأسئلة", link: basePath + "vet/questions.html" },
      ],
    },
  ];

  function generateMenuHTML(items) {
    return (
      '<ul class="dropdown-menu">' +
      items
        .map(
          (item) => `
      <li class="dropdown-item ${item.subItems ? "has-submenu" : ""}">
        <a href="${item.link || "#"}">${item.name}</a>
        ${
          item.subItems
            ? `<ul class="submenu">${generateMenuHTML(item.subItems)}</ul>`
            : ""
        }
      </li>`
        )
        .join("") +
      "</ul>"
    );
  }

  function getCurrentPageName() {
    const currentPath = window.location.pathname;
    const currentFile = currentPath.split("/").pop();

    if (currentFile === "index.html") {
      return "الرئيسية";
    }

    const findPageName = (items) => {
      for (const item of items) {
        if (item.link && item.link.split("/").pop() === currentFile) {
          return item.name;
        }
        if (item.subItems) {
          const subItem = item.subItems.find(
            (sub) => sub.link.split("/").pop() === currentFile
          );
          if (subItem) return subItem.name;
        }
      }
      return "القائمة";
    };
    return findPageName(menuItems);
  }

  const navbarHTML = `
    <div class="navbar">
      <div class="navbar-left">
        <a href="${menuItems[0].link}" class="nav-icon" title="الرئيسية">
          <i class="${menuItems[0].icon}"></i>
        </a>
        <div class="dropdown">
          <button class="dropbtn">${getCurrentPageName()} <i class="fas fa-caret-down"></i></button>
          <div class="dropdown-content">${generateMenuHTML(menuItems)}</div>
        </div>
      </div>
      <div class="navbar-right">
        <button id="refreshPage" class="nav-icon" title="تحديث">
          <i class="fas fa-sync-alt"></i>
        </button>
      </div>
    </div>
  `;

  const headerElement = document.querySelector(".header");
  if (headerElement) {
    headerElement.insertAdjacentHTML("afterbegin", navbarHTML);
  }

  document.getElementById("refreshPage").addEventListener("click", () => {
    location.reload();
  });

  document.querySelector(".dropbtn").addEventListener("click", function (e) {
    e.stopPropagation();
    document.querySelector(".dropdown-content").classList.toggle("show");
  });

  document.addEventListener("click", function (e) {
    if (!e.target.closest(".dropdown")) {
      document.querySelector(".dropdown-content").classList.remove("show");
    }
  });
});

