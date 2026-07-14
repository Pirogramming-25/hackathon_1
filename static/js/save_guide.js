// save_guide.js

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

    const searchForm = document.querySelector(".guide-search");

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

    const cards = document.querySelectorAll(".guide-card");

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

// static/js/save_guide.js

let currentPage = 1;

document.addEventListener("DOMContentLoaded", () => {
  loadMyScraps(1);
});

async function loadMyScraps(page) {
  const scrapList = document.querySelector("#scrap-list");
  const pagination = document.querySelector("#pagination");

  try {
    // 🎯 백엔드의 '저장한 글(스크랩)' API 호출
    const response = await fetch(`/api/users/me/scraps/?page=${page}`, {
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
        result?.message || "저장한 설명서를 불러오지 못했습니다."
      );
    }

    const scraps = result.data.results || result.data;
    currentPage = page;

    if (scraps.length === 0) {
      scrapList.innerHTML = "<p>저장한 설명서가 없습니다.</p>";
      if (pagination) pagination.innerHTML = "";
      return;
    }

    // 🎯 가져온 데이터를 설명서 카드 HTML로 변환
    scrapList.innerHTML = scraps
      .map(
        (scrap) => {
          // 백엔드 구조에 따라 scrap 안에 guide가 중첩되어 있을 수 있으므로 방어 코드 추가
          const guide = scrap.guide || scrap; 
          
          return `
            <a href="/guides/${guide.id}/" class="guide-card">
              <div class="card-image-placeholder">
                  ${
                    guide.images && guide.images.length > 0
                      ? `<img src="${guide.images[0].image}" alt="설명서 썸네일">`
                      : '<div class="no-image">이미지 없음</div>'
                  }
              </div>
              <div class="guide-card-info">
                <h3 class="card-title">${escapeHtml(guide.title)}</h3>
                <div class="guide-meta">
                  <span>조회수 ${guide.view_count || 0}</span>
                  <span>${formatDate(guide.created_at)}</span>
                </div>
              </div>
            </a>
          `;
        }
      )
      .join("");

    renderPagination(result.data, page, pagination);
  } catch (error) {
    scrapList.innerHTML = `
      <p class="error-message">
        ${escapeHtml(error.message)}
      </p>
    `;
    if (pagination) pagination.innerHTML = "";
  }
}

// ==========================================
// 유틸리티 함수들 (기존에 사용하시던 것 그대로)
// ==========================================

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
        loadMyScraps(targetPage);
        window.scrollTo({ top: 0, behavior: "smooth" });
      }
    });
  });
}

function moveToLogin() {
  const nextPath = encodeURIComponent(window.location.pathname);
  window.location.href = `/login/?next=${nextPath}`;
}

function formatDate(dateString) {
  if (!dateString) return "";
  return new Date(dateString).toLocaleDateString("ko-KR");
}

function escapeHtml(value) {
  return String(value ?? "").replaceAll("&", "&amp;").replaceAll("<", "&lt;").replaceAll(">", "&gt;").replaceAll('"', "&quot;").replaceAll("'", "&#039;");
}