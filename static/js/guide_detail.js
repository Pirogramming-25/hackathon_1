/* static/js/guide_detail.js */

document.addEventListener("DOMContentLoaded", () => {

    // ==========================
    // 1. 저장하기 버튼 토글
    // ==========================
    const saveBtn = document.querySelector(".save-btn");

    if (saveBtn) {
        saveBtn.addEventListener("click", () => {
            saveBtn.classList.toggle("active");

            if (saveBtn.classList.contains("active")) {
                saveBtn.innerHTML = `
                    <span class="material-symbols-rounded">bookmark</span>
                    저장 완료
                `;
            } else {
                saveBtn.innerHTML = `
                    <span class="material-symbols-rounded">bookmark</span>
                    저장하기
                `;
            }
        });
    }

    // ==========================
    // 2. 도움이 됐어요 버튼 토글
    // ==========================
    const likeBtn = document.querySelector(".like-btn");

    if (likeBtn) {
        likeBtn.addEventListener("click", () => {
            likeBtn.classList.toggle("active");

            if (likeBtn.classList.contains("active")) {
                likeBtn.innerHTML = `
                    <span class="material-symbols-rounded">thumb_up</span>
                    감사합니다!
                `;
            } else {
                likeBtn.innerHTML = `
                    <span class="material-symbols-rounded">thumb_up</span>
                    도움이 됐어요
                `;
            }
        });
    }

    // ==========================
    // 3. 우측 STEP 네비게이션 부드러운 스크롤 + 현재 스텝 활성화 효과
    // ==========================
    const stepLinks = document.querySelectorAll(".step-nav a");

    stepLinks.forEach(link => {
        link.addEventListener("click", (e) => {
            const hrefAttr = link.getAttribute("href");
            
            // 빈 링크(#) 처리 방지
            if (hrefAttr === "#" || !hrefAttr.startsWith("#")) return;
            
            e.preventDefault();
            const target = document.querySelector(hrefAttr);

            if (target) {
                // 오른쪽 번호 버튼들의 active 표시 순체 전환
                stepLinks.forEach(l => l.classList.remove("active"));
                link.classList.add("active");

                // 목표 구역으로 부드럽게 스크롤링
                target.scrollIntoView({
                    behavior: "smooth",
                    block: "start"
                });
            }
        });
    });
});