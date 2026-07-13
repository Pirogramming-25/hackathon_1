// save_guid.js

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