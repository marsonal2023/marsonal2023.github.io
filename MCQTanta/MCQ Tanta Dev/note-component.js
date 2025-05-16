class NoteComponent extends HTMLElement {
  constructor() {
    super();
    this.expanded = false;
    this.isLongNote = false;
    this.isSlider = false;
  }

  connectedCallback() {
    this.render();
    this.addEventListeners();
  }

  render() {
    const noteContentRaw = decodeURIComponent(
      this.getAttribute("data-note") || ""
    );

    const noteContentProcessed = this.processContent(noteContentRaw);

    this.innerHTML = `
      <style>
        .note {
          background: rgba(253, 245, 230, 0.95);
          padding: 0;
          border-radius: 0.5rem;
          position: relative;
          overflow: hidden;
          box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
          transition: all 0.3s ease;
        }
        .note.clickable {
          cursor: pointer;
        }
        .note:hover {
          box-shadow: 0 6px 8px rgba(0, 0, 0, 0.15);
          transform: translateY(-2px);
        }
        .note-text {
          color: rgba(0, 0, 0, 0.8);
          line-height: normal;
          max-height: 100px;
          overflow: hidden;
          transition: max-height 0.3s ease;
          padding: 5px 10px 20px;
          white-space: normal;
        }
        .note-text p,
        .note-text h1,
        .note-text h2,
        .note-text h3,
        .note-text h4,
        .note-text h5,
        .note-text h6 {
          margin: 0;
          padding: 0;
        }
        .note-text[data-direction="rtl"] {
          direction: rtl;
        }
        .note-text[data-direction="ltr"] {
          direction: ltr;
        }
        .note.expanded .note-text {
          max-height: none;
        }
        .note.slider .note-text {
          overflow-y: auto;
          max-height: 75vh;
        }
        .note.slider .note-text::-webkit-scrollbar {
          width: 5px;
        }
        .note.slider .note-text::-webkit-scrollbar-thumb {
          background: rgba(0,0,0,0.25);
          border-radius: 5px;
        }
        .note.slider .note-text::-webkit-scrollbar-thumb:hover {
          background: rgba(0,0,0,0.5);
        }
        .note.slider .note-text::-webkit-scrollbar-button {
          display: none;
        }
        .note.slider .note-text {
          scrollbar-width: thin;
          scrollbar-color: rgba(0,0,0,0.25) transparent;
        }
        .note.slider .note-text:hover {
          scrollbar-color: rgba(0,0,0,0.5) transparent;
        }

        .expand-icon {
          position: absolute;
          bottom: 2px;
          left: 50%;
          transform: translateX(-50%);
          width: 20px;
          height: 20px;
          fill: rgba(0, 0, 0, 0.5);
          transition: transform 0.3s ease;
        }
        img.thumbnail {
          max-width: 100%;
          cursor: pointer;
          border-radius: 5px;
          transition: transform 0.2s;
        }
        img.thumbnail:hover {
          transform: scale(1.05);
        }
      </style>
      <div class="note">
        <div class="note-text">${
          noteContentProcessed || "No note available."
        }</div>
        <svg class="expand-icon" viewBox="0 0 24 24">
          <path d="M7 10l5 5 5-5z"/>
        </svg>
      </div>
    `;

    this.setTextDirection(noteContentRaw);
    this.addEventListenersToImages();
    this.adjustNoteDisplay();
  }

  processContent(content) {
    let processedContent = content
      .replace(/\$\$IMG\$\$(.*?)\$\$\/IMG\$\$/g, (match, p1) => {
        const imagePath = p1.replace(/\\/g, "/");
        return `<img src="file://${imagePath}" class="thumbnail">`;
      })
      .replace(/\n+/g, '\n') // Replace multiple line breaks with one
      .replace(/\n/g, '<br>'); // Replace line breaks with <br>
    return processedContent;
  }

  setTextDirection(content) {
    const hasArabic = /[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF]/.test(content);
    const noteText = this.querySelector(".note-text");
    if (noteText) {
      noteText.setAttribute("data-direction", hasArabic ? "rtl" : "ltr");
    }
  }

  addEventListeners() {
    const noteElement = this.querySelector(".note");
    noteElement.addEventListener("click", (event) => {
      if (this.isLongNote) {
        this.toggleNoteExpansion();
      }
    });
  }

  addEventListenersToImages() {
    const images = this.querySelectorAll("img.thumbnail");
    images.forEach((img) => {
      img.addEventListener("click", (e) => {
        e.stopPropagation();
        const src = img.getAttribute("src");
        window.showFullscreenImage(src);
      });
    });
  }

  adjustNoteDisplay() {
    const noteElement = this.querySelector(".note");
    const noteText = noteElement.querySelector(".note-text");
    const expandIcon = noteElement.querySelector(".expand-icon");

    if (noteText) {
      const scrollHeight = noteText.scrollHeight;
      const viewportHeight = window.innerHeight;

      if (scrollHeight > 100) {
        this.isLongNote = true;
        noteElement.classList.add("clickable");
        expandIcon.style.display = "block";

        if (scrollHeight > viewportHeight * 0.75) {
          this.isSlider = true;
          noteElement.classList.add("slider");
        }

        if (!this.expanded) {
          noteText.style.maxHeight = "100px";
        }
      } else {
        this.isLongNote = false;
        expandIcon.style.display = "none";
        noteElement.classList.remove("clickable");
      }
    }
  }

  toggleNoteExpansion() {
    const noteElement = this.querySelector(".note");
    const noteText = noteElement.querySelector(".note-text");
    const expandIcon = noteElement.querySelector(".expand-icon");

    this.expanded = !this.expanded;

    if (this.expanded) {
      if (this.isSlider) {
        noteText.style.maxHeight = "75vh";
      } else {
        noteText.style.maxHeight = "none";
      }
      noteElement.classList.add("expanded");
      expandIcon.innerHTML = '<path d="M7 14l5-5 5 5z"/>';
    } else {
      noteText.style.maxHeight = "100px";
      noteElement.classList.remove("expanded");
      expandIcon.innerHTML = '<path d="M7 10l5 5 5-5z"/>';
    }
  }

  resetAndAdjustNote() {
    this.expanded = false;
    this.isLongNote = false;
    this.isSlider = false;
    this.adjustNoteDisplay();
  }
}

customElements.define("note-component", NoteComponent);