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


    function getFirstError(errors) {
        if (!errors || typeof errors !== "object") {
            return "";
        }

        const firstKey = Object.keys(errors)[0];
        const firstValue = errors[firstKey];

        if (Array.isArray(firstValue)) {
            return firstValue[0];
        }

        if (typeof firstValue === "string") {
            return firstValue;
        }

        return "";
    }



    // 회원가입 제출 검사 및 API 요청
    signupForm.addEventListener("submit", async function (event) {

        event.preventDefault();


        // 빈 값 확인
        if (
            username.value.trim() === "" ||
            email.value.trim() === "" ||
            name.value.trim() === "" ||
            birth.value === "" ||
            password.value.trim() === "" ||
            passwordCheck.value.trim() === ""
        ) {

            alert("모든 정보를 입력해주세요.");

            return;

        }




        // 비밀번호 확인
        if (password.value !== passwordCheck.value) {


            alert("비밀번호가 일치하지 않습니다.");


            passwordCheck.focus();


            return;

        }



        try {
            const response = await fetch("/api/auth/signup/", {
                method: "POST",
                credentials: "include",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": getCookie("csrftoken"),
                },
                body: JSON.stringify({
                    username: username.value.trim(),
                    email: email.value.trim(),
                    name: name.value.trim(),
                    birth_date: birth.value,
                    password: password.value,
                    password_confirm: passwordCheck.value,
                }),
            });

            const result = await response.json();

            if (!response.ok || !result.success) {
                const errorMessage = getFirstError(result.data);
                alert(errorMessage || result.message || "회원가입에 실패했습니다.");
                return;
            }

            alert("회원가입이 완료되었습니다.");
            window.location.href = "/login/";
        } catch (error) {
            alert("회원가입 요청 중 오류가 발생했습니다.");
        }

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
