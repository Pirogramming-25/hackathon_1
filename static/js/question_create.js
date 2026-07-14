/* static/js/question_create.js */

const QUESTION_MAX_IMAGES = 5;
const QUESTION_MAX_FILE_SIZE = 5 * 1024 * 1024;

const QUESTION_ALLOWED_TYPES = new Set([
  "image/jpeg",
  "image/png",
  "image/webp",
]);

const QUESTION_ALLOWED_EXTENSIONS = new Set([
  "jpg",
  "jpeg",
  "png",
  "webp",
]);

/*
 * 각 이미지 데이터 구조
 *
 * {
 *   originalFile: 최초 업로드 파일,
 *   file: 실제 서버에 전송할 파일,
 *   description: 이미지 설명,
 *   isBaked: 주석 적용 여부,
 *   previewUrl: 화면 표시용 blob URL
 * }
 */
let questionImages = [];
let selectedImageIndex = -1;

let questionCreateForm;
let imageInput;
let uploadBox;
let imageEditorSection;
let thumbnailList;
let imageCount;
let mainPreviewImage;
let selectedImageTitle;
let selectedImageStatus;
let annotateImageBtn;
let annotateButtonText;
let restoreOriginalBtn;
let imageDescription;
let saveQuestionBtn;
let questionCreateError;

document.addEventListener("DOMContentLoaded", () => {
  questionCreateForm =
    document.getElementById("questionCreateForm");

  imageInput =
    document.getElementById("imageInput");

  uploadBox =
    document.getElementById("uploadBox");

  imageEditorSection =
    document.getElementById("imageEditorSection");

  thumbnailList =
    document.getElementById("thumbnailList");

  imageCount =
    document.getElementById("imageCount");

  mainPreviewImage =
    document.getElementById("mainPreviewImage");

  selectedImageTitle =
    document.getElementById("selectedImageTitle");

  selectedImageStatus =
    document.getElementById("selectedImageStatus");

  annotateImageBtn =
    document.getElementById("annotateImageBtn");

  annotateButtonText =
    document.getElementById("annotateButtonText");

  restoreOriginalBtn =
    document.getElementById("restoreOriginalBtn");

  imageDescription =
    document.getElementById("imageDescription");

  saveQuestionBtn =
    document.getElementById("saveQuestionBtn");

  questionCreateError =
    document.getElementById("questionCreateError");

  imageInput.addEventListener(
    "change",
    handleFileInputChange
  );

  uploadBox.addEventListener(
    "dragover",
    handleDragOver
  );

  uploadBox.addEventListener(
    "dragleave",
    handleDragLeave
  );

  uploadBox.addEventListener(
    "drop",
    handleDrop
  );

  imageDescription.addEventListener(
    "input",
    handleDescriptionInput
  );

  annotateImageBtn.addEventListener(
    "click",
    annotateSelectedImage
  );

  restoreOriginalBtn.addEventListener(
    "click",
    restoreSelectedImage
  );

  questionCreateForm.addEventListener(
    "submit",
    submitQuestion
  );

  window.addEventListener(
    "beforeunload",
    revokeAllPreviewUrls
  );
});


/* =====================================================
   이미지 추가
===================================================== */

function handleFileInputChange(event) {
  const files =
    Array.from(event.target.files);

  addImages(files);

  /*
   * 같은 파일을 다시 선택해도 change 이벤트가
   * 발생할 수 있도록 input을 비운다.
   *
   * 실제 파일 데이터는 questionImages 배열에 들어 있으므로
   * input을 비워도 이미지가 사라지지 않는다.
   */
  imageInput.value = "";
}

function handleDragOver(event) {
  event.preventDefault();

  uploadBox.classList.add("is-dragging");
}

function handleDragLeave(event) {
  event.preventDefault();

  uploadBox.classList.remove("is-dragging");
}

function handleDrop(event) {
  event.preventDefault();

  uploadBox.classList.remove("is-dragging");

  const files =
    Array.from(event.dataTransfer.files);

  addImages(files);
}

function addImages(files) {
  if (!files.length) {
    return;
  }

  const validationMessage =
    validateIncomingFiles(files);

  if (validationMessage) {
    showError(validationMessage);
    return;
  }

  const existingFileKeys = new Set(
    questionImages.map((item) =>
      getFileKey(item.originalFile)
    )
  );

  const uniqueFiles = files.filter((file) => {
    const key = getFileKey(file);

    if (existingFileKeys.has(key)) {
      return false;
    }

    existingFileKeys.add(key);
    return true;
  });

  if (!uniqueFiles.length) {
    showError(
      "이미 등록된 사진입니다."
    );

    return;
  }

  if (
    questionImages.length + uniqueFiles.length >
    QUESTION_MAX_IMAGES
  ) {
    const remainingCount =
      QUESTION_MAX_IMAGES - questionImages.length;

    showError(
      `사진은 최대 ${QUESTION_MAX_IMAGES}장까지 등록할 수 있습니다. ` +
      `현재 ${questionImages.length}장이 등록되어 있어 ` +
      `${remainingCount}장만 더 추가할 수 있습니다.`
    );

    return;
  }

  uniqueFiles.forEach((file) => {
    questionImages.push({
      originalFile: file,
      file,
      description: "",
      isBaked: false,
      previewUrl: URL.createObjectURL(file),
    });
  });

  if (selectedImageIndex === -1) {
    selectedImageIndex = 0;
  }

  showError("");
  renderImageEditor();
}

function validateIncomingFiles(files) {
  for (const file of files) {
    const extension =
      getFileExtension(file.name);

    if (
      !QUESTION_ALLOWED_TYPES.has(file.type) ||
      !QUESTION_ALLOWED_EXTENSIONS.has(extension)
    ) {
      return (
        `${file.name}: ` +
        "JPG, JPEG, PNG, WEBP 파일만 등록할 수 있습니다."
      );
    }

    if (file.size > QUESTION_MAX_FILE_SIZE) {
      return (
        `${file.name}: ` +
        "이미지 크기는 파일당 최대 5MB입니다."
      );
    }
  }

  return "";
}

function getFileExtension(filename) {
  const parts = filename
    .toLowerCase()
    .split(".");

  return parts.length > 1
    ? parts.pop()
    : "";
}

function getFileKey(file) {
  return [
    file.name,
    file.size,
    file.lastModified,
  ].join(":");
}


/* =====================================================
   이미지 화면 렌더링
===================================================== */

function renderImageEditor() {
  const hasImages =
    questionImages.length > 0;

  imageEditorSection.hidden =
    !hasImages;

  imageCount.textContent =
    String(questionImages.length);

  if (!hasImages) {
    selectedImageIndex = -1;
    thumbnailList.innerHTML = "";
    mainPreviewImage.removeAttribute("src");
    imageDescription.value = "";
    return;
  }

  if (
    selectedImageIndex < 0 ||
    selectedImageIndex >= questionImages.length
  ) {
    selectedImageIndex = 0;
  }

  renderThumbnails();
  renderSelectedImage();
}

function renderThumbnails() {
  thumbnailList.innerHTML = "";

  questionImages.forEach((item, index) => {
    const card =
      document.createElement("div");

    card.className =
      "thumbnail-card";

    if (index === selectedImageIndex) {
      card.classList.add("is-selected");
    }

    const selectButton =
      document.createElement("button");

    selectButton.type = "button";
    selectButton.className =
      "thumbnail-select-button";

    selectButton.setAttribute(
      "aria-label",
      `${index + 1}번째 화면 선택`
    );

    if (index === selectedImageIndex) {
      selectButton.setAttribute(
        "aria-current",
        "true"
      );
    }

    selectButton.addEventListener(
      "click",
      () => {
        selectImage(index);
      }
    );

    const thumbnailImage =
      document.createElement("img");

    thumbnailImage.src =
      item.previewUrl;

    thumbnailImage.alt =
      `${index + 1}번째 화면 미리보기`;

    const orderBadge =
      document.createElement("span");

    orderBadge.className =
      "thumbnail-order-badge";

    orderBadge.textContent =
      String(index + 1);

    selectButton.append(
      thumbnailImage,
      orderBadge
    );

    if (item.isBaked) {
      const editedBadge =
        document.createElement("span");

      editedBadge.className =
        "thumbnail-edited-badge";

      editedBadge.textContent =
        "표시 완료";

      selectButton.appendChild(
        editedBadge
      );
    }

    const deleteButton =
      document.createElement("button");

    deleteButton.type = "button";
    deleteButton.className =
      "thumbnail-delete-button";

    deleteButton.setAttribute(
      "aria-label",
      `${index + 1}번째 화면 삭제`
    );

    deleteButton.innerHTML = `
      <span class="material-symbols-rounded">
        close
      </span>
    `;

    deleteButton.addEventListener(
      "click",
      (event) => {
        event.stopPropagation();
        deleteImage(index);
      }
    );

    card.append(
      selectButton,
      deleteButton
    );

    thumbnailList.appendChild(card);
  });
}

function renderSelectedImage() {
  const currentItem =
    questionImages[selectedImageIndex];

  if (!currentItem) {
    return;
  }

  mainPreviewImage.src =
    currentItem.previewUrl;

  mainPreviewImage.alt =
    `${selectedImageIndex + 1}번째 화면`;

  selectedImageTitle.textContent =
    `화면 ${selectedImageIndex + 1}`;

  imageDescription.value =
    currentItem.description;

  if (currentItem.isBaked) {
    selectedImageStatus.textContent =
      "그림 표시 적용됨";

    selectedImageStatus.classList.add(
      "is-edited"
    );

    annotateButtonText.textContent =
      "표시 수정";

    restoreOriginalBtn.hidden = false;
  } else {
    selectedImageStatus.textContent =
      "원본 이미지";

    selectedImageStatus.classList.remove(
      "is-edited"
    );

    annotateButtonText.textContent =
      "그림으로 표시";

    restoreOriginalBtn.hidden = true;
  }
}

function selectImage(index) {
  if (
    index < 0 ||
    index >= questionImages.length
  ) {
    return;
  }

  selectedImageIndex = index;

  showError("");
  renderThumbnails();
  renderSelectedImage();
}

function deleteImage(index) {
  const imageItem =
    questionImages[index];

  if (!imageItem) {
    return;
  }

  URL.revokeObjectURL(
    imageItem.previewUrl
  );

  questionImages.splice(index, 1);

  if (!questionImages.length) {
    selectedImageIndex = -1;
  } else if (
    index < selectedImageIndex
  ) {
    selectedImageIndex -= 1;
  } else if (
    selectedImageIndex >= questionImages.length
  ) {
    selectedImageIndex =
      questionImages.length - 1;
  }

  renderImageEditor();
}


/* =====================================================
   이미지별 설명
===================================================== */

function handleDescriptionInput() {
  const currentItem =
    questionImages[selectedImageIndex];

  if (!currentItem) {
    return;
  }

  /*
   * 입력하는 순간 현재 이미지 데이터에 저장한다.
   * 따라서 다른 썸네일로 이동해도 설명이 유지된다.
   */
  currentItem.description =
    imageDescription.value;
}


/* =====================================================
   이미지 주석 편집
===================================================== */

async function annotateSelectedImage() {
  const currentItem =
    questionImages[selectedImageIndex];

  if (!currentItem) {
    showError(
      "먼저 편집할 화면을 선택해주세요."
    );

    return;
  }

  const originalButtonText =
    annotateButtonText.textContent;

  try {
    annotateImageBtn.disabled = true;
    restoreOriginalBtn.disabled = true;

    annotateButtonText.textContent =
      "편집기 여는 중...";

    showError("");

    /*
     * 현재 선택된 이미지 파일만 편집기에 전달한다.
     * 편집 결과는 다른 이미지가 아니라 현재 항목에만 저장된다.
     */
    const bakedFile =
      await openImageAnnotator(
        currentItem.file
      );

    if (!bakedFile) {
      return;
    }

    /*
     * image-annotator.js는 결과를 PNG로 만든다.
     * PNG 변환 후 5MB를 넘을 수 있으므로 다시 검사한다.
     */
    if (
      bakedFile.size >
      QUESTION_MAX_FILE_SIZE
    ) {
      showError(
        "그림 표시 후 이미지 크기가 5MB를 초과했습니다. " +
        "더 작은 원본 이미지를 사용해주세요."
      );

      return;
    }

    URL.revokeObjectURL(
      currentItem.previewUrl
    );

    currentItem.file = bakedFile;
    currentItem.isBaked = true;
    currentItem.previewUrl =
      URL.createObjectURL(bakedFile);

    renderThumbnails();
    renderSelectedImage();
  } catch (error) {
    console.error(
      "이미지 표시 편집 오류:",
      error
    );

    showError(
      "이미지 편집에 실패했습니다. 다시 시도해주세요."
    );
  } finally {
    annotateImageBtn.disabled = false;
    restoreOriginalBtn.disabled = false;

    const latestItem =
      questionImages[selectedImageIndex];

    annotateButtonText.textContent =
      latestItem?.isBaked
        ? "표시 수정"
        : originalButtonText;
  }
}

function restoreSelectedImage() {
  const currentItem =
    questionImages[selectedImageIndex];

  if (!currentItem) {
    return;
  }

  URL.revokeObjectURL(
    currentItem.previewUrl
  );

  currentItem.file =
    currentItem.originalFile;

  currentItem.isBaked = false;

  currentItem.previewUrl =
    URL.createObjectURL(
      currentItem.originalFile
    );

  showError("");
  renderThumbnails();
  renderSelectedImage();
}


/* =====================================================
   질문 최종 등록
   (설명서 작성과 다른 점: 공개범위(visibility) 필드가 없고,
    /api/questions/ 로 전송한 뒤 질문 목록으로 이동한다)
===================================================== */

async function submitQuestion(event) {
  event.preventDefault();

  const title =
    document
      .getElementById("title")
      .value
      .trim();

  const category =
    document
      .getElementById("category")
      .value;

  if (!title) {
    showError(
      "질문 제목을 입력해주세요."
    );

    document
      .getElementById("title")
      .focus();

    return;
  }

  if (!category) {
    showError(
      "분류를 선택해주세요."
    );

    document
      .getElementById("category")
      .focus();

    return;
  }

  if (!questionImages.length) {
    showError(
      "최소 1장 이상의 화면 사진을 추가해주세요."
    );

    return;
  }

  const content = questionImages
    .map((item) => item.description.trim())
    .filter(Boolean)
    .join("\n");

  if (!content) {
    showError(
      "등록한 화면에 궁금한 내용을 입력해주세요."
    );

    imageDescription.focus();
    return;
  }

  for (const item of questionImages) {
    if (
      item.file.size >
      QUESTION_MAX_FILE_SIZE
    ) {
      showError(
        `${item.file.name}: 이미지 크기는 파일당 최대 5MB입니다.`
      );

      return;
    }
  }

  const formData =
    new FormData();

  formData.append(
    "title",
    title
  );

  formData.append(
    "category",
    category
  );

  formData.append(
    "content",
    content
  );

  questionImages.forEach((item) => {
    formData.append(
      "images",
      item.file
    );

    formData.append(
      "image_descriptions",
      item.description.trim()
    );
  });

  const originalButtonText =
    saveQuestionBtn.textContent;

  try {
    saveQuestionBtn.disabled = true;
    annotateImageBtn.disabled = true;
    restoreOriginalBtn.disabled = true;

    saveQuestionBtn.textContent =
      "질문 등록 중...";

    showError("");

    const response =
      await fetch("/api/questions/", {
        method: "POST",
        credentials: "include",
        headers: {
          "X-CSRFToken":
            getCsrfToken(),
        },
        body: formData,
      });

    const contentType =
      response.headers.get(
        "content-type"
      ) || "";

    const result =
      contentType.includes(
        "application/json"
      )
        ? await response.json()
        : null;

    if (
      response.status === 401 ||
      response.status === 403
    ) {
      window.location.href =
        `/login/?next=${encodeURIComponent(
          window.location.pathname
        )}`;

      return;
    }

    if (
      !response.ok ||
      result?.success === false
    ) {
      throw new Error(
        getResponseErrorMessage(result) ||
        "질문 등록에 실패했습니다."
      );
    }

    alert(
      result?.message ||
      "질문이 등록되었습니다."
    );

    /*
     * 현재 동적 질문 상세 페이지가 없으므로
     * 일단 질문 목록으로 이동한다.
     */
    window.location.href = "/questions/";
  } catch (error) {
    console.error(
      "질문 등록 오류:",
      error
    );

    showError(
      error.message ||
      "질문 등록에 실패했습니다."
    );
  } finally {
    saveQuestionBtn.disabled = false;
    annotateImageBtn.disabled = false;
    restoreOriginalBtn.disabled = false;

    saveQuestionBtn.textContent =
      originalButtonText;
  }
}


/* =====================================================
   공통 함수
===================================================== */

function getCsrfToken() {
  const tokenInput =
    document.querySelector(
      '[name="csrfmiddlewaretoken"]'
    );

  if (tokenInput?.value) {
    return tokenInput.value;
  }

  const csrfCookie =
    document.cookie
      .split(";")
      .map((item) => item.trim())
      .find((item) =>
        item.startsWith("csrftoken=")
      );

  if (!csrfCookie) {
    return "";
  }

  return decodeURIComponent(
    csrfCookie.split("=")[1]
  );
}

function getResponseErrorMessage(result) {
  if (!result) {
    return "";
  }

  if (
    result.message &&
    result.message !==
      "잘못된 입력값입니다."
  ) {
    return result.message;
  }

  const firstDetail =
    findFirstString(result.data);

  if (firstDetail) {
    return firstDetail;
  }

  return result.message || "";
}

function findFirstString(value) {
  if (typeof value === "string") {
    return value;
  }

  if (Array.isArray(value)) {
    for (const item of value) {
      const found =
        findFirstString(item);

      if (found) {
        return found;
      }
    }

    return "";
  }

  if (
    value &&
    typeof value === "object"
  ) {
    for (
      const item of
      Object.values(value)
    ) {
      const found =
        findFirstString(item);

      if (found) {
        return found;
      }
    }
  }

  return "";
}

function showError(message) {
  questionCreateError.textContent =
    message;
}

function revokeAllPreviewUrls() {
  questionImages.forEach((item) => {
    URL.revokeObjectURL(
      item.previewUrl
    );
  });
}
