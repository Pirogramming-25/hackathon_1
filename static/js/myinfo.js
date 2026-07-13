/* =====================================
   똑디 나의 정보 페이지
   static/js/myinfo.js
===================================== */


document.addEventListener("DOMContentLoaded", function () {


    const editButtons = document.querySelectorAll(".edit-btn");


    // 페이지 접속 시 내 정보 불러오기
    loadUserInfo();



    // 수정 버튼 이벤트
    editButtons.forEach(function (button) {


        button.addEventListener("click", async function () {


            const input = this.previousElementSibling;



            // 수정 모드
            if (input.disabled) {


                input.disabled = false;

                input.focus();

                this.textContent = "저장";

                this.classList.remove("btn-secondary");

                this.classList.add("btn-primary");


            }


            // 저장 모드
            else {


                input.disabled = true;


                this.textContent = "수정";

                this.classList.remove("btn-primary");

                this.classList.add("btn-secondary");



                // API 수정 요청
                await updateUserInfo(input);


            }


        });


    });


});





// =========================
// 내 정보 가져오기
// =========================

async function loadUserInfo() {


    try {


        const response = await fetch(
            "/api/users/me/",
            {
                method: "GET",
                credentials: "include",
            }
        );



        const result = await response.json();



        console.log(
            "내 정보:",
            result
        );



        if (!result.success) {

            alert(result.message);

            return;

        }



        const user = result.data;



        const usernameInput = document.querySelector("#username");
        const emailInput = document.querySelector("#email");
        const nameInput = document.querySelector("#name");
        const birthInput = document.querySelector("#birth-date");



        if (usernameInput) {

            usernameInput.value = user.username || "";

        }


        if (emailInput) {

            emailInput.value = user.email || "";

        }


        if (nameInput) {

            nameInput.value = user.name || "";

        }


        if (birthInput) {

            birthInput.value = user.birth_date || "";

        }



    } catch (error) {


        console.error(
            "내 정보 조회 실패:",
            error
        );


    }


}







// =========================
// 내 정보 수정
// =========================

async function updateUserInfo(input) {


    try {


        const response = await fetch(
            "/api/users/me/",
            {

                method: "PATCH",

                credentials: "include",


                headers: {
                    "Content-Type": "application/json",
                },


                body: JSON.stringify({

                    // name 속성 기준으로 전송
                    [input.name]: input.value

                }),

            }
        );



        const result = await response.json();



        console.log(
            "수정 결과:",
            result
        );



        if (!result.success) {


            alert(result.message);

            return;


        }



        alert("정보가 저장되었습니다.");



    } catch (error) {


        console.error(
            "정보 수정 실패:",
            error
        );


    }


}