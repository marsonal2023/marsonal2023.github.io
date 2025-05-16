(() => {
  let currentImage = null;
  let isDragging = false;
  let lastX = 0;
  let lastY = 0;
  let translateX = 0;
  let translateY = 0;
  let scale = 1;
  const minScale = 0.5;
  const maxScale = 3;
  let animationFrameId = null;

  const resetState = () => {
    translateX = 0;
    translateY = 0;
    scale = 1;
    isDragging = false;
    applyTransform();
  };

  const applyTransform = () => {
    if (currentImage) {
      currentImage.style.transform = `translate3d(${translateX}px, ${translateY}px, 0) scale(${scale})`;
    }
  };

  const updatePosition = (deltaX, deltaY) => {
    translateX += deltaX / scale;
    translateY += deltaY / scale;

    if (animationFrameId) {
      cancelAnimationFrame(animationFrameId);
    }
    animationFrameId = requestAnimationFrame(applyTransform);
  };

  const startDragging = (clientX, clientY) => {
    isDragging = true;
    lastX = clientX;
    lastY = clientY;
    if (currentImage) {
      currentImage.style.cursor = "grabbing";
      currentImage.style.transition = "none";
    }
  };

  const stopDragging = () => {
    isDragging = false;
    if (currentImage) {
      currentImage.style.cursor = "grab";
      currentImage.style.transition = "transform 0.3s ease-out";
    }
  };

  const handleStart = (e) => {
    e.preventDefault();
    if (e.type === "mousedown") {
      startDragging(e.clientX, e.clientY);
    } else if (e.type === "touchstart" && e.touches.length === 1) {
      const touch = e.touches[0];
      startDragging(touch.clientX, touch.clientY);
    }
  };

  const handleMove = (e) => {
    if (!isDragging) return;
    e.preventDefault();
    let clientX, clientY;
    if (e.type === "mousemove") {
      clientX = e.clientX;
      clientY = e.clientY;
    } else if (e.type === "touchmove" && e.touches.length === 1) {
      const touch = e.touches[0];
      clientX = touch.clientX;
      clientY = touch.clientY;
    }
    if (clientX !== undefined && clientY !== undefined) {
      const deltaX = clientX - lastX;
      const deltaY = clientY - lastY;
      updatePosition(deltaX, deltaY);
      lastX = clientX;
      lastY = clientY;
    }
  };

  const handleEnd = () => {
    stopDragging();
  };

  const zoomImage = (zoomIn = true) => {
    const zoomFactor = 0.1;
    const newScale = zoomIn
      ? scale * (1 + zoomFactor)
      : scale * (1 - zoomFactor);
    scale = Math.min(maxScale, Math.max(minScale, newScale));
    applyTransform();
  };

  const handleWheel = (e) => {
    e.preventDefault();
    const zoomIn = e.deltaY < 0;
    zoomImage(zoomIn);
  };

  const handlePinchZoom = (e) => {
    if (e.touches.length !== 2) return;
    e.preventDefault();
    const touch1 = e.touches[0];
    const touch2 = e.touches[1];
    const currentDistance = Math.hypot(
      touch2.clientX - touch1.clientX,
      touch2.clientY - touch1.clientY
    );

    if (handlePinchZoom.lastDistance) {
      const delta = currentDistance - handlePinchZoom.lastDistance;
      const zoomDirection = delta > 0 ? 1 : -1;
      const zoomIn = zoomDirection > 0;
      const zoomAmount = Math.abs(delta) / 200; // Adjust sensitivity
      const newScale = zoomIn
        ? scale * (1 + zoomAmount)
        : scale * (1 - zoomAmount);
      scale = Math.min(maxScale, Math.max(minScale, newScale));
      applyTransform();
    }

    handlePinchZoom.lastDistance = currentDistance;
  };

  const resetPinch = () => {
    handlePinchZoom.lastDistance = null;
  };

  const addListeners = () => {
    if (!currentImage) return;
    currentImage.addEventListener("mousedown", handleStart);
    currentImage.addEventListener("touchstart", handleStart, {
      passive: false,
    });
    window.addEventListener("mousemove", handleMove);
    window.addEventListener("touchmove", handleMove, { passive: false });
    window.addEventListener("mouseup", handleEnd);
    window.addEventListener("touchend", handleEnd);
    window.addEventListener("touchcancel", handleEnd);
    currentImage.addEventListener("wheel", handleWheel, { passive: false });
    currentImage.addEventListener("touchmove", handlePinchZoom, {
      passive: false,
    });
    currentImage.addEventListener("touchend", resetPinch);
    currentImage.addEventListener("touchcancel", resetPinch);
  };

  const removeListeners = () => {
    if (!currentImage) return;
    currentImage.removeEventListener("mousedown", handleStart);
    currentImage.removeEventListener("touchstart", handleStart);
    window.removeEventListener("mousemove", handleMove);
    window.removeEventListener("touchmove", handleMove);
    window.removeEventListener("mouseup", handleEnd);
    window.removeEventListener("touchend", handleEnd);
    window.removeEventListener("touchcancel", handleEnd);
    currentImage.removeEventListener("wheel", handleWheel);
    currentImage.removeEventListener("touchmove", handlePinchZoom);
    currentImage.removeEventListener("touchend", resetPinch);
    currentImage.removeEventListener("touchcancel", resetPinch);
  };

  const closeFullscreenImage = () => {
    const fullscreenDiv = document.querySelector(".fullscreen-image");
    if (fullscreenDiv) {
      removeListeners();
      fullscreenDiv.remove();
      resetState();
      if (animationFrameId) {
        cancelAnimationFrame(animationFrameId);
      }
    }
  };

  window.closeFullscreenImage = closeFullscreenImage;

  window.showFullscreenImage = (src) => {
    // Preload image for faster display
    const img = new Image();
    img.src = src;
    img.onload = () => {
      // Create fullscreen container
      const fullscreenDiv = document.createElement("div");
      fullscreenDiv.className = "fullscreen-image";
      fullscreenDiv.innerHTML = `
          <img src="${src}" alt="Fullscreen image" draggable="false">
          <div class="fullscreen-controls">
            <button id="zoomInBtn" aria-label="Zoom In"><i class="fas fa-search-plus"></i></button>
            <button id="zoomOutBtn" aria-label="Zoom Out"><i class="fas fa-search-minus"></i></button>
            <button id="closeFullscreenBtn" aria-label="Close"><i class="fas fa-times"></i></button>
          </div>
        `;
      document.body.appendChild(fullscreenDiv);

      currentImage = fullscreenDiv.querySelector("img");
      resetState();
      addListeners();

      // Add button event listeners
      const centerX = window.innerWidth / 2;
      const centerY = window.innerHeight / 2;

      fullscreenDiv
        .querySelector("#zoomInBtn")
        .addEventListener("click", () => zoomImage(true));
      fullscreenDiv
        .querySelector("#zoomOutBtn")
        .addEventListener("click", () => zoomImage(false));
      fullscreenDiv
        .querySelector("#closeFullscreenBtn")
        .addEventListener("click", closeFullscreenImage);

      // Close when clicking outside the image
      fullscreenDiv.addEventListener("click", (e) => {
        if (e.target === fullscreenDiv) closeFullscreenImage();
      });
    };

    img.onerror = () => {
      console.error("Failed to load image:", src);
    };
  };
})();
