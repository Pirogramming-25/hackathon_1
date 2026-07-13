/* =====================================
   똑디 회원가입 페이지
   static/js/signup.js
===================================== */


document.addEventListener("DOMContentLoaded", function () {


    const signupForm = document.querySelector(".signup-form");


    const username = document.querySelector("#username");
    const email = document.querySelector("#email");
    const name = document.querySelector("#name");
    const birth = document.querySelector("#birth");
    const password = document.querySelector("#password");
    const passwordCheck = document.querySelector("#password-check");




    // 회원가입 제출 검사
    signupForm.addEventListener("submit", function (event) {


        // 빈 값 확인
        if (
            username.value.trim() === "" ||
            email.value.trim() === "" ||
            name.value.trim() === "" ||
            birth.value === "" ||
            password.value.trim() === "" ||
            passwordCheck.value.trim() === ""
        ) {

            event.preventDefault();

            alert("모든 정보를 입력해주세요.");

            return;

        }




        // 비밀번호 확인
        if (password.value !== passwordCheck.value) {


            event.preventDefault();


            alert("비밀번호가 일치하지 않습니다.");


            passwordCheck.focus();


            return;

        }



        alert("회원가입을 진행합니다.");

    });






    // 입력창 focus 효과
    const inputs = document.querySelectorAll(".form-group input");


    inputs.forEach(function(input) {


        input.addEventListener("focus", function () {

            this.parentElement.classList.add("is-focus");

        });



        input.addEventListener("blur", function () {

            this.parentElement.classList.remove("is-focus");

        });


    });



});