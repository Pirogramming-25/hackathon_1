document.addEventListener("DOMContentLoaded", loadQuestions);

async function loadQuestions() {
  const questionList = document.querySelector("#question-list");

  try {
    const response = await fetch("/api/questions/", {
      method: "GET",
      credentials: "include",
    });

    const result = await response.json();

    if (!response.ok || !result.success) {
      throw new Error(
        result.message || "질문 목록을 불러오지 못했습니다."
      );
    }

    const questions = result.data.results;

    if (questions.length === 0) {
      questionList.innerHTML = "<p>등록된 질문이 없습니다.</p>";
      return;
    }

    questionList.innerHTML = questions
      .map(
        (question) => `
          <article
            class="question-card"
            data-question-id="${question.id}"
          >
            ${
              question.thumbnail
                ? `
                  <img
                    src="${question.thumbnail}"
                    alt="질문 이미지"
                    class="question-thumbnail"
                  >
                `
                : ""
            }

            <div class="question-card-info">
              <div class="question-labels">
                <span class="question-category">
                  ${getCategoryLabel(question.category)}
                </span>

                <span class="question-status">
                  ${getStatusLabel(question.status)}
                </span>
              </div>

              <h2>${escapeHtml(question.title)}</h2>

              <div class="question-meta">
                <span>${escapeHtml(question.author)}</span>
                <span>답변 ${question.answer_count}개</span>
                <span>${formatDate(question.created_at)}</span>
              </div>
            </div>
          </article>
        `
      )
      .join("");

    document.querySelectorAll(".question-card").forEach((card) => {
      card.addEventListener("click", () => {
        const questionId = card.dataset.questionId;
        window.location.href = `/questions/${questionId}/`;
      });
    });
  } catch (error) {
    questionList.innerHTML = `
      <p class="error-message">
        ${escapeHtml(error.message)}
      </p>
    `;
  }
}

function getCategoryLabel(category) {
  const labels = {
    GOVERNMENT: "정부",
    FINANCE: "금융",
    MEDICAL: "의료",
    LIFE: "생활",
    ETC: "기타",
  };

  return labels[category] ?? category;
}

function getStatusLabel(status) {
  const labels = {
    WAITING: "답변 대기",
    RESOLVED: "해결 완료",
  };

  return labels[status] ?? status;
}

function formatDate(dateString) {
  if (!dateString) return "";

  return new Date(dateString).toLocaleDateString("ko-KR");
}

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}