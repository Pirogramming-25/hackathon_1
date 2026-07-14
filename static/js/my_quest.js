// my_quest.js

document.addEventListener("DOMContentLoaded", () => {

    // ==========================
    // 정렬 버튼
    // ==========================

    const sortButtons = document.querySelectorAll(".sort-btn");

    sortButtons.forEach((button) => {

        button.addEventListener("click", () => {

            sortButtons.forEach((btn) => {
                btn.classList.remove("active");
            });

            button.classList.add("active");

            // TODO : Django 정렬 연결

        });

    });


    // ==========================
    // 검색
    // ==========================

    const searchForm = document.querySelector(".question-search");

    if(searchForm){

        searchForm.addEventListener("submit", (e) => {

            e.preventDefault();

            const keyword = searchForm.querySelector("input").value.trim();

            if(keyword === ""){

                alert("검색어를 입력해주세요.");

                return;

            }

            // TODO : Django 검색 연결
            console.log(keyword);

        });

    }


    // ==========================
    // 카드 클릭 효과
    // ==========================

    const cards = document.querySelectorAll(".question-card");

    cards.forEach((card) => {

        card.addEventListener("mousedown", () => {

            card.style.transform = "scale(0.98)";

        });

        card.addEventListener("mouseup", () => {

            card.style.transform = "";

        });

        card.addEventListener("mouseleave", () => {

            card.style.transform = "";

        });

    });

});

let currentPage = 1;

document.addEventListener("DOMContentLoaded", () => {
  loadMyQuestions(1);
});

async function loadMyQuestions(page) {
  const questionList = document.querySelector("#question-list");
  const pagination = document.querySelector("#pagination");

  try {
    // 🎯 백엔드의 '내가 등록한 질문' API 호출
    const response = await fetch(`/api/users/me/questions/?page=${page}`, {
      method: "GET",
      credentials: "include",
    });

    const result = await response.json().catch(() => null);

    if (response.status === 401 || response.status === 403) {
      moveToLogin();
      return;
    }

    if (!response.ok || !result?.success) {
      throw new Error(
        result?.message || "질문 목록을 불러오지 못했습니다."
      );
    }

    const questions = result.data.results || result.data; // 페이징 구조에 맞게 접근
    currentPage = page;

    if (questions.length === 0) {
      questionList.innerHTML = "<p>등록한 질문이 없습니다.</p>";
      if (pagination) pagination.innerHTML = "";
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
                <span>답변 ${question.answer_count || 0}개</span>
                <span>${formatDate(question.created_at)}</span>
              </div>
            </div>
          </article>
        `
      )
      .join("");

    // 상세 페이지 이동 이벤트 연결
    document.querySelectorAll(".question-card").forEach((card) => {
      card.addEventListener("click", () => {
        const questionId = card.dataset.questionId;
        window.location.href = `/questions/${questionId}/`; // 상세 페이지 URL
      });
    });

    renderPagination(result.data, page, pagination);
  } catch (error) {
    questionList.innerHTML = `
      <p class="error-message">
        ${escapeHtml(error.message)}
      </p>
    `;
    if (pagination) pagination.innerHTML = "";
  }
}

// ---------------------------------------------------------
// 아래는 기존에 사용하시던 유틸리티 함수들 (동일하게 유지)
// ---------------------------------------------------------

function renderPagination(pageData, page, pagination) {
  if (!pagination) return;
  const pageSize = 10;
  const totalCount = pageData.count ?? 0;
  const totalPages = Math.max(1, Math.ceil(totalCount / pageSize));

  if (totalPages <= 1) {
    pagination.innerHTML = "";
    return;
  }

  const buttons = [];
  buttons.push(`
    <button type="button" class="pagination-btn" data-page="${page - 1}" ${!pageData.previous ? "disabled" : ""}>이전</button>
  `);

  for (let i = 1; i <= totalPages; i += 1) {
    buttons.push(`
      <button type="button" class="pagination-btn ${i === page ? "pagination-btn--active" : ""}" data-page="${i}" ${i === page ? "disabled" : ""}>
        ${i}
      </button>
    `);
  }

  buttons.push(`
    <button type="button" class="pagination-btn" data-page="${page + 1}" ${!pageData.next ? "disabled" : ""}>다음</button>
  `);

  pagination.innerHTML = buttons.join("");

  pagination.querySelectorAll(".pagination-btn").forEach((button) => {
    button.addEventListener("click", () => {
      const targetPage = Number(button.dataset.page);
      if (!Number.isNaN(targetPage) && targetPage >= 1) {
        loadMyQuestions(targetPage);
        window.scrollTo({ top: 0, behavior: "smooth" });
      }
    });
  });
}

function moveToLogin() {
  const nextPath = encodeURIComponent(window.location.pathname);
  window.location.href = `/login/?next=${nextPath}`;
}

function getCategoryLabel(category) {
  const labels = { GOVERNMENT: "정부", FINANCE: "금융", MEDICAL: "의료", LIFE: "생활", ETC: "기타" };
  return labels[category] ?? category;
}

function getStatusLabel(status) {
  const labels = { WAITING: "답변 대기", RESOLVED: "해결 완료" };
  return labels[status] ?? status;
}

function formatDate(dateString) {
  if (!dateString) return "";
  return new Date(dateString).toLocaleDateString("ko-KR");
}

function escapeHtml(value) {
  return String(value ?? "").replaceAll("&", "&amp;").replaceAll("<", "&lt;").replaceAll(">", "&gt;").replaceAll('"', "&quot;").replaceAll("'", "&#039;");
}