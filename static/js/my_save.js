// my_save.js

document.addEventListener("DOMContentLoaded", () => {

    // ==========================
    // 카드 Hover 효과
    // ==========================

    const cards = document.querySelectorAll(".save-card");

    cards.forEach((card) => {

        card.addEventListener("mouseenter", () => {

            card.style.cursor = "pointer";

        });

    });


    // ==========================
    // 클릭 애니메이션
    // ==========================

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