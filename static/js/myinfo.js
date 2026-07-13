/* =====================================
   똑디 나의 정보 페이지
   static/js/myinfo.js
===================================== */

document.addEventListener("DOMContentLoaded", function () {
    const editButtons = document.querySelectorAll(".edit-btn");
    const passwordButton = document.querySelector(".password-edit-btn");

    loadUserInfo();

    editButtons.forEach(function (button) {
        button.addEventListener("click", async function () {
            const input = this.previousElementSibling;

            if (input.disabled) {
                enableEdit(input, this);
                return;
            }

            const success = await updateUserInfo({
                [input.name]: input.value,
            });

            if (success) {
                disableEdit(input, this);
                await loadUserInfo();
            }
        });
    });

    if (passwordButton) {
        passwordButton.addEventListener("click", async function () {
            const passwordInputs = [
                document.querySelector("#current-password"),
                document.querySelector("#new-password"),
                document.querySelector("#new-password-confirm"),
            ].filter(Boolean);

            const isEditing = passwordInputs.some(function (input) {
                return !input.disabled;
            });

            if (!isEditing) {
                passwordInputs.forEach(function (input) {
                    input.disabled = false;
                    input.value = "";
                });
                passwordInputs[0]?.focus();
                this.textContent = "저장";
                this.classList.remove("btn-secondary");
                this.classList.add("btn-primary");
                return;
            }

            const payload = {};
            passwordInputs.forEach(function (input) {
                payload[input.name] = input.value;
            });

            const success = await updateUserInfo(payload);
            if (success) {
                passwordInputs.forEach(function (input) {
                    input.value = "";
                    input.disabled = true;
                });
                this.textContent = "수정";
                this.classList.remove("btn-primary");
                this.classList.add("btn-secondary");
            }
        });
    }
});

function getCookie(name) {
    const cookies = document.cookie ? document.cookie.split(";") : [];

    for (const cookie of cookies) {
        const trimmed = cookie.trim();
        if (trimmed.startsWith(name + "=")) {
            return decodeURIComponent(trimmed.slice(name.length + 1));
        }
    }

    return "";
}

function getCsrfToken() {
    const csrfInput = document.querySelector("[name=csrfmiddlewaretoken]");
    return csrfInput?.value || getCookie("csrftoken");
}

function enableEdit(input, button) {
    input.disabled = false;
    input.focus();
    button.textContent = "저장";
    button.classList.remove("btn-secondary");
    button.classList.add("btn-primary");
}

function disableEdit(input, button) {
    input.disabled = true;
    button.textContent = "수정";
    button.classList.remove("btn-primary");
    button.classList.add("btn-secondary");
}

async function loadUserInfo() {
    try {
        const response = await fetch("/api/users/me/", {
            method: "GET",
            credentials: "include",
        });
        const result = await response.json();

        if (!result.success) {
            alert(result.message);
            return;
        }

        const user = result.data;
        setInputValue("#username", user.username);
        setInputValue("#email", user.email);
        setInputValue("#name", user.name);
        setInputValue("#birth-date", user.birth_date);
    } catch (error) {
        console.error("내 정보 조회 실패:", error);
    }
}

function setInputValue(selector, value) {
    const input = document.querySelector(selector);
    if (input) {
        input.value = value || "";
    }
}

async function updateUserInfo(payload) {
    try {
        const response = await fetch("/api/users/me/", {
            method: "PATCH",
            credentials: "include",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCsrfToken(),
            },
            body: JSON.stringify(payload),
        });
        const result = await response.json();

        if (!result.success) {
            alert(result.message);
            return false;
        }

        alert("정보가 저장되었습니다.");
        return true;
    } catch (error) {
        console.error("정보 수정 실패:", error);
        alert("정보 수정 중 오류가 발생했습니다.");
        return false;
    }
}
