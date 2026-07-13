document.addEventListener("DOMContentLoaded", () => {
  bindImageDescriptions();
  bindQuestionCreateForm();
});

function bindImageDescriptions() {
  const imageInput = document.querySelector("#question-images");
  const descriptionList = document.querySelector(
    "#image-description-list"
  );

  imageInput.addEventListener("change", () => {
    const files = Array.from(imageInput.files);

    if (files.length > 5) {
      alert("이미지는 최대 5장까지 등록할 수 있습니다.");
      imageInput.value = "";
      descriptionList.innerHTML = "";
      return;
    }

    const invalidFile = files.find(
      (file) => file.size > 5 * 1024 * 1024
    );

    if (invalidFile) {
      alert("이미지는 파일당 5MB 이하여야 합니다.");
      imageInput.value = "";
      descriptionList.innerHTML = "";
      return;
    }

    descriptionList.innerHTML = files
      .map(
        (file, index) => `
          <div class="image-description-item">
            <p>${escapeHtml(file.name)}</p>

            <input
              type="text"
              class="image-description"
              data-index="${index}"
              placeholder="이미지 설명을 입력하세요. 선택 사항"
            >
          </div>
        `
      )
      .join("");
  });
}

function bindQuestionCreateForm() {
  const form = document.querySelector("#question-create-form");

  form.addEventListener("submit", async (event) => {
    event.preventDefault();

    const titleInput = document.querySelector("#question-title");
    const categoryInput = document.querySelector("#question-category");
    const contentInput = document.querySelector("#question-content");
    const imageInput = document.querySelector("#question-images");
    const submitButton = document.querySelector(
      "#question-submit-button"
    );
    const errorElement = document.querySelector(
      "#question-form-error"
    );

    const title = titleInput.value.trim();
    const category = categoryInput.value;
    const content = contentInput.value.trim();

    errorElement.textContent = "";

    if (!title || !category || !content) {
      errorElement.textContent =
        "제목, 카테고리, 질문 내용을 모두 입력해주세요.";
      return;
    }

    const formData = new FormData();

    formData.append("title", title);
    formData.append("category", category);
    formData.append("content", content);

    const files = Array.from(imageInput.files);
    const descriptionInputs = Array.from(
      document.querySelectorAll(".image-description")
    );

    files.forEach((file, index) => {
      formData.append("images", file);

      const description =
        descriptionInputs[index]?.value.trim() ?? "";

      formData.append("image_descriptions", description);
    });

    try {
      submitButton.disabled = true;
      submitButton.textContent = "등록 중...";

      const response = await fetch("/api/questions/", {
        method: "POST",
        credentials: "include",
        headers: {
          "X-CSRFToken": getCookie("csrftoken"),
        },
        body: formData,
      });

      const contentType =
        response.headers.get("content-type") || "";

      const result = contentType.includes("application/json")
        ? await response.json()
        : null;

      if (response.status === 401 || response.status === 403) {
        window.location.href =
          `/login/?next=${encodeURIComponent(
            window.location.pathname
          )}`;
        return;
      }

      if (!response.ok || !result?.success) {
        throw new Error(
          getErrorMessage(result) ||
            "질문 등록에 실패했습니다."
        );
      }

      const questionId = result.data?.id;

      if (questionId) {
        window.location.href = `/questions/${questionId}/`;
      } else {
        window.location.href = "/questions/";
      }
    } catch (error) {
      console.error("질문 등록 오류:", error);
      errorElement.textContent = error.message;
    } finally {
      submitButton.disabled = false;
      submitButton.textContent = "질문 등록";
    }
  });
}

function getCookie(name) {
  const cookies = document.cookie
    .split(";")
    .map((cookie) => cookie.trim());

  const target = cookies.find((cookie) =>
    cookie.startsWith(`${name}=`)
  );

  return target
    ? decodeURIComponent(target.substring(name.length + 1))
    : "";
}

function getErrorMessage(result) {
  if (result?.data && typeof result.data === "object") {
    const values = Object.values(result.data).flat();

    if (values.length > 0) {
      return String(values[0]);
    }
  }

  return result?.message ?? null;
}

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}