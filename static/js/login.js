/* =====================================
   똑디 로그인 페이지
   static/js/login.js
===================================== */


document.addEventListener("DOMContentLoaded", function () {


    const loginForm = document.querySelector(".login-form");

    const usernameInput = document.querySelector("#username");

    const passwordInput = document.querySelector("#password");



    // 로그인 폼 유효성 검사
    loginForm.addEventListener("submit", function (event) {


        const username = usernameInput.value.trim();

        const password = passwordInput.value.trim();



        if (username === "") {

            event.preventDefault();

            alert("아이디를 입력해주세요.");

            usernameInput.focus();

            return;

        }



        if (password === "") {

            event.preventDefault();

            alert("비밀번호를 입력해주세요.");

            passwordInput.focus();

            return;

        }


    });



    // 입력창 클릭 시 강조 효과
    const inputs = document.querySelectorAll(".input-box input");


    inputs.forEach(function(input) {


        input.addEventListener("focus", function() {

            this.parentElement.classList.add("is-focus");

        });



        input.addEventListener("blur", function() {

            this.parentElement.classList.remove("is-focus");

        });


    });


});