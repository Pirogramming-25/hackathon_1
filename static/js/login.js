/* =====================================
   똑디 로그인 페이지
   static/js/login.js
===================================== */


document.addEventListener("DOMContentLoaded", function () {


    const loginForm = document.querySelector(".login-form");

    const usernameInput = document.querySelector("#username");

    const passwordInput = document.querySelector("#password");



    function getCookie(name) {
        const cookies = document.cookie ? document.cookie.split(";") : [];

        for (const cookie of cookies) {
            const trimmedCookie = cookie.trim();

            if (trimmedCookie.startsWith(name + "=")) {
                return decodeURIComponent(trimmedCookie.substring(name.length + 1));
            }
        }

        return "";
    }



    // 로그인 폼 유효성 검사 및 API 요청
    loginForm.addEventListener("submit", async function (event) {

        event.preventDefault();


        const username = usernameInput.value.trim();

        const password = passwordInput.value.trim();



        if (username === "") {

            alert("아이디를 입력해주세요.");

            usernameInput.focus();

            return;

        }



        if (password === "") {

            alert("비밀번호를 입력해주세요.");

            passwordInput.focus();

            return;

        }


        try {
            const response = await fetch("/api/auth/login/", {
                method: "POST",
                credentials: "include",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": getCookie("csrftoken"),
                },
                body: JSON.stringify({
                    username: username,
                    password: password,
                }),
            });

            const result = await response.json();

            if (!response.ok || !result.success) {
                alert(result.message || "로그인에 실패했습니다.");
                return;
            }

            const nextUrl = new URLSearchParams(window.location.search).get("next");
            window.location.href = nextUrl || "/";
        } catch (error) {
            alert("로그인 요청 중 오류가 발생했습니다.");
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
