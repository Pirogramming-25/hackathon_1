// static/js/save_guide.js

let currentPage = 1;

document.addEventListener("DOMContentLoaded", () => {
  // 1. 데이터 로드 시작
  loadMyScraps(1);

  // 2. 정렬 버튼 이벤트 연결
  const sortButtons = document.querySelectorAll(".sort-btn");
  sortButtons.forEach((button) => {
    button.addEventListener("click", () => {
      sortButtons.forEach((btn) => {
        btn.classList.remove("active");
      });
      button.classList.add("active");
      // TODO: 정렬 옵션을 적용하여 API 다시 호출 (예: loadMyScraps(1, '조회순'))
    });
  });

  // 3. 검색 폼 이벤트 연결
  const searchForm = document.querySelector(".guide-search");
  if (searchForm) {
    searchForm.addEventListener("submit", (e) => {
      e.preventDefault();
      const keyword = searchForm.querySelector("input").value.trim();
      if (keyword === "") {
        alert("검색어를 입력해주세요.");
        return;
      }
      // TODO: 검색어를 적용하여 API 다시 호출 (예: loadMyScraps(1, keyword))
      console.log("검색어:", keyword);
    });
  }
});

// ==========================
// API 호출 및 화면 렌더링
// ==========================
async function loadMyScraps(page) {
  const scrapList = document.querySelector("#scrap-list");
  const pagination = document.querySelector("#pagination");

  try {
    // 백엔드의 '저장한 글(스크랩)' API 호출
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

    // 가져온 데이터를 설명서 카드 HTML로 변환
    scrapList.innerHTML = scraps
      .map((scrap) => {
        // 백엔드 구조 방어 코드
        const guide = scrap.guide || scrap; 
        
        // 🎯 is_scrapped 상태에 따라 북마크 아이콘 결정
        // (저장한 글 목록이므로 기본적으로 true이겠지만, 명확히 처리)
        const isScrapped = guide.is_scrapped !== false; 
        const bookmarkIcon = isScrapped ? "bookmark" : "bookmark_border"; 

        return `
          <a href="/guides/${guide.id}/" class="guide-card">
            <div class="guide-thumbnail card-image-placeholder">
                ${
                  guide.images && guide.images.length > 0
                    ? `<img src="${guide.images[0].image}" alt="설명서 썸네일">`
                    : `<span class="material-symbols-rounded">${bookmarkIcon}</span>`
                }
            </div>
            
            <div class="guide-info guide-card-info">
              <h3 class="card-title">${escapeHtml(guide.title)}</h3>
              <div class="guide-meta">
                <span>조회수 ${guide.view_count || 0}</span>
                <span>${formatDate(guide.created_at)}</span>
              </div>
            </div>
          </a>
        `;
      })
      .join("");

    // 동적으로 생성된 카드들에 클릭/마우스 효과 적용
    applyCardEffects();
    
    // 페이지네이션 렌더링
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

// ==========================
// 카드 마우스 효과 함수 분리
// ==========================
function applyCardEffects() {
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
}

// ==========================================
// 유틸리티 함수들
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