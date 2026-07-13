// guid_list.js

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

            // TODO : Django 연결 시 fetch로 정렬 요청
            console.log(button.textContent.trim());

        });

    });


    // ==========================
    // 검색
    // ==========================

    const searchForm = document.querySelector(".guide-search");

    searchForm.addEventListener("submit", (e) => {

        e.preventDefault();

        const keyword = searchForm.querySelector("input").value.trim();

        if(keyword === ""){

            alert("검색어를 입력해주세요.");

            return;

        }

        // TODO : Django 검색 URL 연결

        console.log(keyword);

        // 예시
        // window.location.href = `/guides/?q=${encodeURIComponent(keyword)}`;

    });


    // ==========================
    // 카드 Hover
    // ==========================

    const cards = document.querySelectorAll(".guide-card");

    cards.forEach((card) => {

        card.addEventListener("mouseenter", () => {

            card.style.cursor = "pointer";

        });

    });

});