document.addEventListener("DOMContentLoaded", () => {

    // ==========================
    // 저장하기 버튼
    // ==========================

    const saveBtn = document.querySelector(".save-btn");

    if(saveBtn){

        saveBtn.addEventListener("click", () => {

            saveBtn.classList.toggle("active");

            if(saveBtn.classList.contains("active")){

                saveBtn.innerHTML = `
                    <span class="material-symbols-rounded">
                        bookmark
                    </span>
                    저장 완료
                `;

            }else{

                saveBtn.innerHTML = `
                    <span class="material-symbols-rounded">
                        bookmark
                    </span>
                    저장하기
                `;

            }

        });

    }


    // ==========================
    // 도움이 됐어요 버튼
    // ==========================

    const likeBtn = document.querySelector(".like-btn");

    if(likeBtn){

        likeBtn.addEventListener("click",()=>{

            likeBtn.classList.toggle("active");

            if(likeBtn.classList.contains("active")){

                likeBtn.innerHTML=`
                    <span class="material-symbols-rounded">
                        thumb_up
                    </span>
                    감사합니다!
                `;

            }else{

                likeBtn.innerHTML=`
                    <span class="material-symbols-rounded">
                        thumb_up
                    </span>
                    도움이 됐어요
                `;

            }

        });

    }


    // ==========================
    // STEP 이동 부드럽게
    // ==========================

    const stepLinks = document.querySelectorAll(".step-nav a");

    stepLinks.forEach(link=>{

        link.addEventListener("click",(e)=>{

            e.preventDefault();

            const target = document.querySelector(link.getAttribute("href"));

            if(target){

                target.scrollIntoView({

                    behavior:"smooth",
                    block:"start"

                });

            }

        });

    });

});