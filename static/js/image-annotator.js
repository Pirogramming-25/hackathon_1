/* static/js/image-annotator.js
 *
 * 이미지에 빨간 동그라미 / 화살표 / 텍스트를 그려서 "구운"(baked) 결과 파일을 만드는 도구.
 * 좌표 데이터는 서버에 저장하지 않고, 캔버스에 그린 결과를 합성한 이미지 파일 자체를
 * 업로드하는 방식 (베이크드 이미지 방식).
 *
 * 사용법:
 *   const bakedFile = await openImageAnnotator(originalFile);
 *   // bakedFile === null 이면 사용자가 취소한 것 (원본 그대로 유지)
 *   // bakedFile 이 있으면 원본 대신 이 파일을 업로드용 FileList에 넣으면 됨
 */

function openImageAnnotator(file) {
  return new Promise((resolve) => {
    const imageUrl = URL.createObjectURL(file);
    const img = new Image();

    img.onload = () => {
      const overlay = buildOverlay(img, file, resolve, imageUrl);
      document.body.appendChild(overlay);
    };

    img.onerror = () => {
      URL.revokeObjectURL(imageUrl);
      alert("이미지를 불러오지 못했습니다.");
      resolve(null);
    };

    img.src = imageUrl;
  });
}

function buildOverlay(img, originalFile, resolve, imageUrl) {
  // ---------- 캔버스 크기 계산 (너무 크면 성능 문제라 최대 1600px로 축소) ----------
  const MAX_DIMENSION = 1600;
  let canvasWidth = img.naturalWidth;
  let canvasHeight = img.naturalHeight;

  if (canvasWidth > MAX_DIMENSION || canvasHeight > MAX_DIMENSION) {
    const scale = MAX_DIMENSION / Math.max(canvasWidth, canvasHeight);
    canvasWidth = Math.round(canvasWidth * scale);
    canvasHeight = Math.round(canvasHeight * scale);
  }

  const shapes = []; // { type: 'circle'|'arrow'|'text', ... }
  let currentTool = "circle";
  let drawing = null; // 그리는 중인 도형 { x1, y1, x2, y2 }

  // ---------- 오버레이 뼈대 (전부 인라인 스타일 — 공유 CSS 파일 안 건드림) ----------
  const overlay = document.createElement("div");
  overlay.style.cssText = `
    position: fixed; inset: 0; background: rgba(0,0,0,0.75);
    z-index: 9999; display: flex; align-items: center; justify-content: center;
    padding: 20px;
  `;

  const panel = document.createElement("div");
  panel.style.cssText = `
    background: #ffffff; border-radius: 16px; padding: 20px;
    max-width: 95vw; max-height: 95vh; display: flex; flex-direction: column; gap: 12px;
  `;

  const title = document.createElement("p");
  title.textContent = "동그라미/화살표는 드래그로 그리고, 텍스트는 원하는 위치를 클릭해서 입력하세요.";
  title.style.cssText = "margin:0; font-weight:700; font-size:15px; color:#111827;";

  const toolbar = document.createElement("div");
  toolbar.style.cssText = "display:flex; gap:8px; align-items:center; flex-wrap:wrap;";

  const circleBtn = makeToolButton("⭕ 동그라미", true);
  const arrowBtn = makeToolButton("➡️ 화살표", false);
  const textBtn = makeToolButton("🔤 텍스트", false);
  const undoBtn = makeToolButton("↩️ 되돌리기", false);
  const clearBtn = makeToolButton("🗑️ 전체 지우기", false);

  toolbar.appendChild(circleBtn);
  toolbar.appendChild(arrowBtn);
  toolbar.appendChild(textBtn);
  toolbar.appendChild(undoBtn);
  toolbar.appendChild(clearBtn);

  const canvasWrap = document.createElement("div");
  canvasWrap.style.cssText =
    "overflow:auto; max-width:90vw; max-height:65vh; border:1px solid #e5e7eb; border-radius:8px;";

  const canvas = document.createElement("canvas");
  canvas.width = canvasWidth;
  canvas.height = canvasHeight;
  canvas.style.cssText = "display:block; touch-action:none; cursor:crosshair;";
  canvasWrap.appendChild(canvas);

  const actions = document.createElement("div");
  actions.style.cssText = "display:flex; justify-content:flex-end; gap:8px;";

  const cancelBtn = document.createElement("button");
  cancelBtn.type = "button";
  cancelBtn.textContent = "취소";
  cancelBtn.style.cssText =
    "padding:10px 18px; border:1px solid #e5e7eb; border-radius:8px; background:#fff; cursor:pointer; font-size:14px;";

  const completeBtn = document.createElement("button");
  completeBtn.type = "button";
  completeBtn.textContent = "완료";
  completeBtn.style.cssText =
    "padding:10px 18px; border:0; border-radius:8px; background:#2563eb; color:#fff; font-weight:700; cursor:pointer; font-size:14px;";

  actions.appendChild(cancelBtn);
  actions.appendChild(completeBtn);

  panel.appendChild(title);
  panel.appendChild(toolbar);
  panel.appendChild(canvasWrap);
  panel.appendChild(actions);
  overlay.appendChild(panel);

  // ---------- 그리기 로직 ----------
  const ctx = canvas.getContext("2d");

  function redraw() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.drawImage(img, 0, 0, canvas.width, canvas.height);

    shapes.forEach((shape) => drawShape(ctx, shape));

    if (drawing && currentTool !== "text") {
      drawShape(ctx, { ...drawing, type: currentTool });
    }
  }

  function drawShape(context, shape) {
    if (shape.type === "text") {
      drawText(context, shape);
      return;
    }

    context.strokeStyle = "#ef4444";
    context.lineWidth = Math.max(3, canvas.width * 0.004);
    context.lineCap = "round";
    context.lineJoin = "round";

    if (shape.type === "circle") {
      const cx = (shape.x1 + shape.x2) / 2;
      const cy = (shape.y1 + shape.y2) / 2;
      const rx = Math.abs(shape.x2 - shape.x1) / 2;
      const ry = Math.abs(shape.y2 - shape.y1) / 2;

      context.beginPath();
      context.ellipse(cx, cy, rx, ry, 0, 0, Math.PI * 2);
      context.stroke();
    } else if (shape.type === "arrow") {
      drawArrow(context, shape.x1, shape.y1, shape.x2, shape.y2);
    }
  }

  function drawText(context, shape) {
    const fontSize = Math.max(20, Math.round(canvas.width * 0.024));
    context.font = `bold ${fontSize}px sans-serif`;
    context.textBaseline = "top";

    const paddingX = 8;
    const paddingY = 5;
    const textWidth = context.measureText(shape.text).width;

    context.fillStyle = "rgba(255, 255, 255, 0.85)";
    context.fillRect(
      shape.x - paddingX,
      shape.y - paddingY,
      textWidth + paddingX * 2,
      fontSize + paddingY * 2
    );

    context.fillStyle = "#ef4444";
    context.fillText(shape.text, shape.x, shape.y);
  }

  function drawArrow(context, x1, y1, x2, y2) {
    const headLength = Math.max(14, canvas.width * 0.018);
    const angle = Math.atan2(y2 - y1, x2 - x1);

    context.beginPath();
    context.moveTo(x1, y1);
    context.lineTo(x2, y2);
    context.stroke();

    context.beginPath();
    context.moveTo(x2, y2);
    context.lineTo(
      x2 - headLength * Math.cos(angle - Math.PI / 6),
      y2 - headLength * Math.sin(angle - Math.PI / 6)
    );
    context.moveTo(x2, y2);
    context.lineTo(
      x2 - headLength * Math.cos(angle + Math.PI / 6),
      y2 - headLength * Math.sin(angle + Math.PI / 6)
    );
    context.stroke();
  }

  function getCanvasPoint(event) {
    const rect = canvas.getBoundingClientRect();
    const clientX = event.touches ? event.touches[0].clientX : event.clientX;
    const clientY = event.touches ? event.touches[0].clientY : event.clientY;

    return {
      x: ((clientX - rect.left) / rect.width) * canvas.width,
      y: ((clientY - rect.top) / rect.height) * canvas.height,
    };
  }

  canvas.addEventListener("pointerdown", (event) => {
    const point = getCanvasPoint(event);
    drawing = { x1: point.x, y1: point.y, x2: point.x, y2: point.y };
    canvas.setPointerCapture(event.pointerId);
  });

  canvas.addEventListener("pointermove", (event) => {
    if (!drawing) return;
    const point = getCanvasPoint(event);
    drawing.x2 = point.x;
    drawing.y2 = point.y;
    redraw();
  });

  canvas.addEventListener("pointerup", () => {
    if (!drawing) return;

    const distance = Math.hypot(
      drawing.x2 - drawing.x1,
      drawing.y2 - drawing.y1
    );

    // 너무 작게(실수로 클릭만) 그린 건 무시
    if (distance > 6 && currentTool !== "text") {
      shapes.push({ ...drawing, type: currentTool });
    }

    drawing = null;
    redraw();
  });

  canvas.addEventListener("click", (event) => {
    if (currentTool !== "text") {
      return;
    }

    const point = getCanvasPoint(event);
    const text = window.prompt("표시할 텍스트를 입력하세요.", "");

    if (text && text.trim()) {
      shapes.push({ type: "text", x: point.x, y: point.y, text: text.trim() });
      redraw();
    }
  });

  circleBtn.addEventListener("click", () => setTool("circle"));
  arrowBtn.addEventListener("click", () => setTool("arrow"));
  textBtn.addEventListener("click", () => setTool("text"));

  function setTool(tool) {
    currentTool = tool;
    canvas.style.cursor = tool === "text" ? "text" : "crosshair";

    circleBtn.style.background = tool === "circle" ? "#2563eb" : "#fff";
    circleBtn.style.color = tool === "circle" ? "#fff" : "#374151";
    arrowBtn.style.background = tool === "arrow" ? "#2563eb" : "#fff";
    arrowBtn.style.color = tool === "arrow" ? "#fff" : "#374151";
    textBtn.style.background = tool === "text" ? "#2563eb" : "#fff";
    textBtn.style.color = tool === "text" ? "#fff" : "#374151";
  }

  undoBtn.addEventListener("click", () => {
    shapes.pop();
    redraw();
  });

  clearBtn.addEventListener("click", () => {
    shapes.length = 0;
    redraw();
  });

  cancelBtn.addEventListener("click", () => {
    cleanup();
    resolve(null);
  });

  completeBtn.addEventListener("click", () => {
    canvas.toBlob(
      (blob) => {
        if (!blob) {
          alert("이미지 합성에 실패했습니다.");
          return;
        }

        const bakedName = renameToPng(originalFile.name);
        const bakedFile = new File([blob], bakedName, {
          type: "image/png",
        });

        cleanup();
        resolve(bakedFile);
      },
      "image/png",
      0.92
    );
  });

  function cleanup() {
    URL.revokeObjectURL(imageUrl);
    overlay.remove();
  }

  setTool("circle");
  redraw();

  return overlay;
}

function makeToolButton(label, active) {
  const button = document.createElement("button");
  button.type = "button";
  button.textContent = label;
  button.style.cssText = `
    padding: 8px 14px; border-radius: 8px; font-size: 13px; cursor: pointer;
    border: 1px solid #e5e7eb;
    background: ${active ? "#2563eb" : "#fff"};
    color: ${active ? "#fff" : "#374151"};
  `;
  return button;
}

function renameToPng(originalName) {
  const withoutExt = originalName.replace(/\.[^/.]+$/, "");
  return `${withoutExt}_baked.png`;
}