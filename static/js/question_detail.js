console.log("question_detail.js 파일 실행됨");

document.addEventListener("DOMContentLoaded", () => {
  bindBackButton();
  loadQuestionDetail();
  bindAnswerForm();
  bindAnswerImageDescriptions();
});

function getQuestionId() {
  return window.location.pathname
    .split("/")
    .filter(Boolean)
    .at(-1);
}

/* 설명서 상세와 동일한 '이전' 버튼 동작 */
function bindBackButton() {
  const backButton = document.querySelector("#detailBackBtn");

  if (!backButton) {
    return;
  }

  backButton.addEventListener("click", () => {
    if (window.history.length > 1) {
      window.history.back();
    } else {
      window.location.href = "/questions/";
    }
  });
}

async function loadQuestionDetail() {
  const statusText = document.querySelector("#detailStatus");
  const questionDetail = document.querySelector("#question-detail");
  const answerList = document.querySelector("#answer-list");
  const questionId = getQuestionId();

  if (!questionDetail || !answerList || !statusText) {
    console.error("질문 상세 화면 요소를 찾을 수 없습니다.");
    return;
  }

  if (!questionId || Number.isNaN(Number(questionId))) {
    statusText.textContent = "잘못된 질문 주소입니다.";
    statusText.classList.add("is-error");
    statusText.hidden = false;
    questionDetail.hidden = true;
    answerList.innerHTML = "";
    return;
  }

  try {
    const response = await fetch(`/api/questions/${questionId}/`, {
      method: "GET",
      credentials: "include",
    });

    const result = await parseResponse(response);

    if (!response.ok || result?.success === false) {
      throw new Error(
        getErrorMessage(result) || "질문을 불러오지 못했습니다."
      );
    }

    const question = result?.data;

    if (!question) {
      throw new Error("질문 데이터가 없습니다.");
    }

    document.title = `${question.title} - 똑디`;

    renderQuestion(question);
    renderAnswers(question);
    updateAnswerForm(question);

    statusText.hidden = true;
    questionDetail.hidden = false;
  } catch (error) {
    console.error("질문 상세 조회 오류:", error);

    statusText.textContent = error.message || "질문을 불러오지 못했습니다.";
    statusText.classList.add("is-error");
    statusText.hidden = false;
    questionDetail.hidden = true;

    answerList.innerHTML = "";
  }
}

function renderQuestion(question) {
  const questionDetail = document.querySelector("#question-detail");

  const currentUsername =
    document.querySelector(".question-detail-page")
      ?.dataset.currentUser ?? "";

  const isAuthor =
    Boolean(currentUsername) &&
    question.author === currentUsername;

  const isResolved = question.status === "RESOLVED";

  questionDetail.innerHTML = `
    <div class="detail-header">
      <div>
        <div class="question-detail-labels">
          <span class="question-category">
            ${escapeHtml(getCategoryLabel(question.category))}
          </span>

          <span class="question-status ${isResolved ? "is-resolved" : ""}">
            ${escapeHtml(getStatusLabel(question.status))}
          </span>
        </div>

        <h1 class="detail-title">${escapeHtml(question.title)}</h1>
        <p class="detail-meta">
          ${escapeHtml(question.author)} · ${formatDate(question.created_at)}
        </p>
      </div>

      ${
        isAuthor
          ? `
            <div class="header-actions">
              ${
                question.status !== "RESOLVED"
                  ? `
                    <button type="button" id="question-resolve-btn">
                      <span class="material-symbols-rounded">check_circle</span>
                      해결 완료
                    </button>
                  `
                  : ""
              }

              <button type="button" id="question-delete-btn">
                <span class="material-symbols-rounded">delete</span>
                질문 삭제
              </button>
            </div>
          `
          : ""
      }
    </div>

    <div class="detail-layout">
      <div class="content-area">
        <div class="question-content-card">
          <p class="question-detail-content">${escapeHtml(question.content)}</p>
          ${renderImages(question.images ?? [])}
        </div>
      </div>
    </div>
  `;

  document
    .querySelector("#question-resolve-btn")
    ?.addEventListener("click", () => {
      resolveQuestion(question.id);
    });

  document
    .querySelector("#question-delete-btn")
    ?.addEventListener("click", () => {
      deleteQuestion(question.id);
    });
}

function renderAnswers(question) {
  const answerList = document.querySelector("#answer-list");
  const answers = question.answers ?? [];

  const currentUsername =
    document.querySelector(".question-detail-page")
      ?.dataset.currentUser ?? "";

  const isQuestionAuthor =
    Boolean(currentUsername) &&
    question.author === currentUsername;

  if (!answers.length) {
    answerList.innerHTML = `
      <p class="empty-answer-message">
        아직 등록된 답변이 없습니다.
      </p>
    `;
    return;
  }

  answerList.innerHTML = answers
    .map((answer) => {
      const registerButton = isQuestionAuthor
        ? `
          <button
            type="button"
            class="guide-register-btn"
            data-answer-id="${answer.id}"
          >
            설명서로 등록
          </button>
        `
        : "";
        const isAnswerAuthor =
        Boolean(currentUsername) &&
        answer.author === currentUsername;

        const editDeleteButtons = isAnswerAuthor
        ? `
          <div class="answer-owner-actions">
            <button type="button" class="answer-edit-btn" data-answer-id="${answer.id}">수정</button>
            <button type="button" class="answer-delete-btn" data-answer-id="${answer.id}">삭제</button>
          </div>
        `
        : "";

      return `
        <article class="answer-card" data-answer-id="${answer.id}">
          <div class="answer-card-header">
            <strong>${escapeHtml(answer.author)}</strong>
          </div>

          <p class="answer-content" data-role="answer-content-display">
            ${escapeHtml(answer.content)}
          </p>

          ${renderImages(answer.images ?? [])}

          <div class="answer-card-footer">
            <time datetime="${escapeHtml(answer.created_at ?? "")}">
              ${formatDate(answer.created_at)}
            </time>

            <div class="answer-actions">
              ${editDeleteButtons}
              ${registerButton}
            </div>
          </div>
        </article>
      `;
    })
    .join("");

  answerList
    .querySelectorAll(".guide-register-btn")
    .forEach((button) => {
      button.addEventListener("click", () => {
        registerAnswerAsGuide(
          question,
          button.dataset.answerId,
          button
        );
      });
    });

  answerList
    .querySelectorAll(".answer-edit-btn")
    .forEach((button) => {
      button.addEventListener("click", () => {
        startEditAnswer(button.dataset.answerId);
      });
    });

  answerList
    .querySelectorAll(".answer-delete-btn")
    .forEach((button) => {
      button.addEventListener("click", () => {
        deleteAnswer(button.dataset.answerId);
      });
    });
}

function startEditAnswer(answerId) {
  const card = document.querySelector(
    `.answer-card[data-answer-id="${answerId}"]`
  );
  const contentDisplay = card?.querySelector(
    '[data-role="answer-content-display"]'
  );

  if (!contentDisplay || card.querySelector(".answer-edit-form")) {
    return;
  }

  const originalText = contentDisplay.textContent.trim();

  const editForm = document.createElement("div");
  editForm.className = "answer-edit-form";
  editForm.innerHTML = `
    <textarea class="answer-edit-textarea" rows="5">${escapeHtml(
      originalText
    )}</textarea>
    <div class="answer-edit-actions">
      <button type="button" class="answer-edit-save-btn">저장</button>
      <button type="button" class="answer-edit-cancel-btn">취소</button>
    </div>
  `;

  contentDisplay.hidden = true;
  contentDisplay.insertAdjacentElement("afterend", editForm);

  editForm
    .querySelector(".answer-edit-cancel-btn")
    .addEventListener("click", () => {
      editForm.remove();
      contentDisplay.hidden = false;
    });

  editForm
    .querySelector(".answer-edit-save-btn")
    .addEventListener("click", () => {
      const value = editForm
        .querySelector(".answer-edit-textarea")
        .value.trim();
      saveAnswerEdit(answerId, value, editForm, contentDisplay);
    });
}

async function saveAnswerEdit(answerId, content, editForm, contentDisplay) {
  if (!content) {
    alert("답변 내용을 입력해주세요.");
    return;
  }

  const formData = new FormData();
  formData.append("content", content);

  const response = await fetch(`/api/answers/${answerId}/`, {
    method: "PATCH",
    credentials: "include",
    headers: { "X-CSRFToken": getCookie("csrftoken") },
    body: formData,
  });

  const result = await parseResponse(response);

  if (response.status === 401 || response.status === 403) {
    moveToLogin();
    return;
  }

  if (!response.ok || result?.success === false) {
    alert(getErrorMessage(result) || "답변 수정에 실패했습니다.");
    return;
  }

  await loadQuestionDetail();
}

async function deleteAnswer(answerId) {
  if (!confirm("이 답변을 정말 삭제하시겠습니까?")) {
    return;
  }

  const response = await fetch(`/api/answers/${answerId}/`, {
    method: "DELETE",
    credentials: "include",
    headers: { "X-CSRFToken": getCookie("csrftoken") },
  });

  const result = await parseResponse(response);

  if (response.status === 401 || response.status === 403) {
    moveToLogin();
    return;
  }

  if (!response.ok || result?.success === false) {
    alert(getErrorMessage(result) || "답변 삭제에 실패했습니다.");
    return;
  }

  await loadQuestionDetail();
}

function renderImages(images) {
  if (!images.length) {
    return "";
  }

  const imageItems = images
    .map((image) => {
      const imageUrl =
        image.image_url ??
        image.image ??
        image.url ??
        "";

      if (!imageUrl) {
        return "";
      }

      return `
        <figure class="detail-image-item">
          <img
            src="${escapeHtml(imageUrl)}"
            alt="${escapeHtml(
              image.description ?? "첨부 이미지"
            )}"
            loading="lazy"
          >

          ${
            image.description
              ? `
                <figcaption>
                  ${escapeHtml(image.description)}
                </figcaption>
              `
              : ""
          }
        </figure>
      `;
    })
    .join("");

  if (!imageItems) {
    return "";
  }

  return `
    <div class="detail-image-list">
      ${imageItems}
    </div>
  `;
}

function updateAnswerForm(question) {
  const answerForm = document.querySelector("#answer-form");

  if (!answerForm) {
    return;
  }

  if (question.status === "RESOLVED") {
    answerForm.hidden = true;
    return;
  }

  answerForm.hidden = false;
}
function bindAnswerImageDescriptions() {
  const imageInput = document.querySelector("#answer-images");
  const descriptionList = document.querySelector(
    "#answer-image-description-list"
  );

  if (!imageInput || !descriptionList) {
    return;
  }

  function renderList() {
    const previousDescriptions = Array.from(
      document.querySelectorAll(".answer-image-description")
    ).map((input) => input.value);

    const files = Array.from(imageInput.files);

    descriptionList.innerHTML = files
      .map(
        (file, index) => `
          <div class="answer-image-description-item">
            <p>${escapeHtml(file.name)}</p>

            <div class="answer-image-description-row">
              <input
                type="text"
                class="answer-image-description"
                data-index="${index}"
                placeholder="이미지 설명을 입력하세요. 선택 사항"
                value="${escapeHtml(previousDescriptions[index] ?? "")}"
              >
              <button
                type="button"
                class="answer-image-annotate-btn"
                data-index="${index}"
              >
                <span class="material-symbols-rounded">draw</span>
                그림으로 표시
              </button>
            </div>
          </div>
        `
      )
      .join("");

    descriptionList
      .querySelectorAll(".answer-image-annotate-btn")
      .forEach((button) => {
        button.addEventListener("click", async () => {
          const index = Number(button.dataset.index);
          const currentFiles = Array.from(imageInput.files);
          const targetFile = currentFiles[index];

          if (!targetFile) {
            return;
          }

          const originalHtml = button.innerHTML;
          button.disabled = true;
          button.textContent = "편집 중...";

          const bakedFile = await openImageAnnotator(targetFile);

          button.disabled = false;
          button.innerHTML = originalHtml;

          if (!bakedFile) {
            return;
          }

          const dataTransfer = new DataTransfer();
          currentFiles.forEach((file, i) => {
            dataTransfer.items.add(i === index ? bakedFile : file);
          });
          imageInput.files = dataTransfer.files;

          renderList();
        });
      });
  }

  imageInput.addEventListener("change", () => {
    const files = Array.from(imageInput.files);

    if (files.length > 4) {
      alert("답변 이미지는 최대 4장까지 등록할 수 있습니다.");
      imageInput.value = "";
      descriptionList.innerHTML = "";
      return;
    }

    const oversizedFile = files.find(
      (file) => file.size > 5 * 1024 * 1024
    );

    if (oversizedFile) {
      alert("이미지는 파일당 5MB 이하여야 합니다.");
      imageInput.value = "";
      descriptionList.innerHTML = "";
      return;
    }

    renderList();
  });
}

function bindAnswerForm() {
  const answerForm = document.querySelector("#answer-form");

  if (!answerForm) {
    return;
  }

  answerForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const questionId = getQuestionId();
    const contentInput =
      document.querySelector("#answer-content");
    const imageInput =
      document.querySelector("#answer-images");
    const submitButton =
      answerForm.querySelector('button[type="submit"]');

    if (!contentInput || !submitButton) {
      console.error("답변 입력 요소를 찾을 수 없습니다.");
      return;
    }

    const content = contentInput.value.trim();

    if (!content) {
      alert("답변 내용을 입력해주세요.");
      contentInput.focus();
      return;
    }

    const files = imageInput
      ? Array.from(imageInput.files)
      : [];

    if (files.length > 4) {
      alert("답변 이미지는 최대 4장까지 등록할 수 있습니다.");
      return;
    }

    const oversizedFile = files.find(
      (file) => file.size > 5 * 1024 * 1024
    );

    if (oversizedFile) {
      alert("이미지는 파일당 5MB 이하여야 합니다.");
      return;
    }

    const formData = new FormData();

    formData.append("content", content);

    const descriptionInputs = Array.from(
        document.querySelectorAll(".answer-image-description")
    );

    files.forEach((file, index) => {
        formData.append("images", file);

        const description =
            descriptionInputs[index]?.value.trim() ?? "";

        formData.append("image_descriptions", description);
    });

    const originalButtonText = submitButton.textContent;

    try {
      submitButton.disabled = true;
      submitButton.textContent = "등록 중...";

      const response = await fetch(
        `/api/questions/${questionId}/answers/`,
        {
          method: "POST",
          credentials: "include",
          headers: {
            "X-CSRFToken": getCookie("csrftoken"),
          },
          body: formData,
        }
      );

      const result = await parseResponse(response);

      if (
        response.status === 401 ||
        response.status === 403
      ) {
        moveToLogin();
        return;
      }

      if (!response.ok || result?.success === false) {
        throw new Error(
          getErrorMessage(result) ||
            "답변 등록에 실패했습니다."
        );
      }

      contentInput.value = "";

      if (imageInput) {
        imageInput.value = "";
      }

      const descriptionList = document.querySelector(
        "#answer-image-description-list"
      );

      if (descriptionList) {
        descriptionList.innerHTML = "";
      }

      await loadQuestionDetail();
    } catch (error) {
      console.error("답변 등록 오류:", error);
      alert(error.message);
    } finally {
      submitButton.disabled = false;
      submitButton.textContent = originalButtonText;
    }
  });
}

async function registerAnswerAsGuide(
  question,
  answerId,
  button
) {
  const confirmed = confirm(
    "이 답변을 설명서로 등록하시겠습니까?"
  );

  if (!confirmed) {
    return;
  }

  const originalText = button.textContent;

  try {
    button.disabled = true;
    button.textContent = "등록 중...";

    const formData = new FormData();

    formData.append("title", question.title);
    formData.append("category", question.category);
    formData.append("visibility", "PUBLIC");

    const response = await fetch(
      `/api/guides/answers/${answerId}/promote/`,
      {
        method: "POST",
        credentials: "include",
        headers: {
          "X-CSRFToken": getCookie("csrftoken"),
        },
        body: formData,
      }
    );

    const result = await parseResponse(response);

    if (response.status === 401) {
      moveToLogin();
      return;
    }

    if (!response.ok || result?.success === false) {
      throw new Error(
        getErrorMessage(result) ||
          result?.error ||
          "설명서 생성에 실패했습니다."
      );
    }

    alert("답변이 설명서로 등록되었습니다.");

    button.textContent = "설명서 등록 완료";

    document
      .querySelectorAll(".guide-register-btn")
      .forEach((registerButton) => {
        registerButton.disabled = true;
      });
  } catch (error) {
    console.error("설명서 등록 오류:", error);
    alert(error.message);

    if (button.isConnected) {
      button.disabled = false;
      button.textContent = originalText;
    }
  }
}

async function resolveQuestion(questionId) {
  const confirmed = confirm(
    "이 질문을 해결 완료 상태로 변경하시겠습니까?"
  );

  if (!confirmed) {
    return;
  }

  const resolveButton = document.querySelector(
    "#question-resolve-btn"
  );

  try {
    if (resolveButton) {
      resolveButton.disabled = true;
      resolveButton.textContent = "처리 중...";
    }

    const response = await fetch(
      `/api/questions/${questionId}/status/`,
      {
        method: "PATCH",
        credentials: "include",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": getCookie("csrftoken"),
        },
        body: JSON.stringify({
          status: "RESOLVED",
        }),
      }
    );

    const result = await parseResponse(response);

    if (
      response.status === 401 ||
      response.status === 403
    ) {
      moveToLogin();
      return;
    }

    if (!response.ok || result?.success === false) {
      throw new Error(
        getErrorMessage(result) ||
          "질문 상태 변경에 실패했습니다."
      );
    }

    await loadQuestionDetail();
  } catch (error) {
    console.error("질문 상태 변경 오류:", error);
    alert(error.message);
  } finally {
    if (resolveButton) {
      resolveButton.disabled = false;
      resolveButton.textContent = "해결 완료";
    }
  }
}

async function deleteQuestion(questionId) {
  const confirmed = confirm(
    "이 질문을 정말 삭제하시겠습니까?"
  );

  if (!confirmed) {
    return;
  }

  const deleteButton = document.querySelector(
    "#question-delete-btn"
  );

  try {
    if (deleteButton) {
      deleteButton.disabled = true;
      deleteButton.textContent = "삭제 중...";
    }

    const response = await fetch(
      `/api/questions/${questionId}/`,
      {
        method: "DELETE",
        credentials: "include",
        headers: {
          "X-CSRFToken": getCookie("csrftoken"),
        },
      }
    );

    const result = await parseResponse(response);

    if (
      response.status === 401 ||
      response.status === 403
    ) {
      moveToLogin();
      return;
    }

    if (!response.ok || result?.success === false) {
      throw new Error(
        getErrorMessage(result) ||
          "질문 삭제에 실패했습니다."
      );
    }

    window.location.href = "/questions/";
  } catch (error) {
    console.error("질문 삭제 오류:", error);
    alert(error.message);

    if (deleteButton) {
      deleteButton.disabled = false;
      deleteButton.textContent = "질문 삭제";
    }
  }
}

async function parseResponse(response) {
  if (response.status === 204) {
    return null;
  }

  const contentType =
    response.headers.get("content-type") ?? "";

  if (!contentType.includes("application/json")) {
    return null;
  }

  return response.json();
}

function moveToLogin() {
  const nextPath = encodeURIComponent(
    window.location.pathname
  );

  const loginUrl = window.DDOKDI_LOGIN_URL || "/login/";

  window.location.href = `${loginUrl}?next=${nextPath}`;
}

function getCookie(name) {
  const cookies = document.cookie
    .split(";")
    .map((cookie) => cookie.trim());

  const target = cookies.find((cookie) =>
    cookie.startsWith(`${name}=`)
  );

  return target
    ? decodeURIComponent(
        target.substring(name.length + 1)
      )
    : "";
}

function getErrorMessage(result) {
  if (
    result?.data &&
    typeof result.data === "object"
  ) {
    const values = Object.values(result.data).flat();

    if (values.length) {
      const firstError = values[0];

      if (
        firstError &&
        typeof firstError === "object"
      ) {
        return JSON.stringify(firstError);
      }

      return String(firstError);
    }
  }

  return result?.message ?? null;
}

function getCategoryLabel(category) {
  const labels = {
    GOVERNMENT: "정부",
    FINANCE: "금융",
    MEDICAL: "의료",
    LIFE: "생활",
    ETC: "기타",
  };

  return labels[category] ?? category ?? "";
}

function getStatusLabel(status) {
  const labels = {
    WAITING: "답변 대기",
    RESOLVED: "해결 완료",
  };

  return labels[status] ?? status ?? "";
}

function formatDate(dateString) {
  if (!dateString) {
    return "";
  }

  const date = new Date(dateString);

  if (Number.isNaN(date.getTime())) {
    return "";
  }

  return date.toLocaleDateString("ko-KR", {
    year: "numeric",
    month: "long",
    day: "numeric",
  });
}

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}