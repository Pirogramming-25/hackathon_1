/* =====================================
   똑디 가족 연동 페이지
   static/js/family_connect.js
===================================== */

document.addEventListener("DOMContentLoaded", function () {
    const searchInput = document.querySelector("#family-search-input");
    const searchBtn = document.querySelector("#search-btn");
    const searchResult = document.querySelector("#search-result");
    const receivedList = document.querySelector(".received-list");
    const sentList = document.querySelector(".sent-list");
    const familyList = document.querySelector(".family-list");

    searchBtn?.addEventListener("click", searchUsers);
    searchInput?.addEventListener("keydown", function (event) {
        if (event.key === "Enter") {
            searchUsers();
        }
    });

    searchResult?.addEventListener("click", async function (event) {
        const button = event.target.closest(".request-btn");
        if (!button) {
            return;
        }

        const success = await apiRequest("/api/families/requests/", {
            method: "POST",
            body: JSON.stringify({
                target_user_id: Number(button.dataset.userId),
            }),
        });

        if (success) {
            alert("가족 연동 요청을 보냈습니다.");
            await refreshFamilyPage();
        }
    });

    receivedList?.addEventListener("click", async function (event) {
        const button = event.target.closest("[data-action]");
        if (!button) {
            return;
        }

        const relationId = button.dataset.relationId;
        const action = button.dataset.action;
        const success = await apiRequest(
            `/api/families/requests/${relationId}/${action}/`,
            {
                method: "PATCH",
            }
        );

        if (success) {
            await refreshFamilyPage();
        }
    });

    familyList?.addEventListener("click", async function (event) {
        const button = event.target.closest(".disconnect-btn");
        if (!button) {
            return;
        }

        if (!confirm("가족 연동을 해제할까요?")) {
            return;
        }

        const success = await apiRequest(`/api/families/${button.dataset.relationId}/`, {
            method: "DELETE",
        });

        if (success) {
            await refreshFamilyPage();
        }
    });

    refreshFamilyPage();

    async function searchUsers() {
        const username = searchInput.value.trim();

        if (!username) {
            alert("검색할 아이디를 입력해주세요.");
            searchInput.focus();
            return;
        }

        const result = await apiRequest(
            `/api/families/users/?username=${encodeURIComponent(username)}`,
            {
                method: "GET",
            },
            true
        );

        if (!result || !result.success || result.data.length === 0) {
            searchResult.innerHTML = `<p class="empty-message">사용자를 찾을 수 없습니다.</p>`;
            return;
        }

        searchResult.innerHTML = result.data
            .map(function (user) {
                return `
                    <div class="result-card">
                        <p>
                            <strong>${escapeHtml(user.username)}</strong>
                            <span>${escapeHtml(user.name || "")}</span>
                        </p>
                        <button
                            class="btn btn-secondary request-btn"
                            type="button"
                            data-user-id="${user.id}"
                        >
                            가족 연동 요청 보내기
                        </button>
                    </div>
                `;
            })
            .join("");
    }

    async function refreshFamilyPage() {
        await Promise.all([
            renderRelationList(
                "/api/families/requests/received/",
                receivedList,
                renderReceivedRequest,
                "받은 가족 요청이 없습니다."
            ),
            renderRelationList(
                "/api/families/requests/sent/",
                sentList,
                renderSentRequest,
                "보낸 가족 요청이 없습니다."
            ),
            renderRelationList(
                "/api/families/",
                familyList,
                renderFamily,
                "연동된 가족이 없습니다."
            ),
        ]);
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

async function apiRequest(url, options = {}, returnRawResult = false) {
    try {
        const method = options.method || "GET";
        const headers = {
            ...(options.headers || {}),
        };

        if (method !== "GET" && method !== "HEAD") {
            headers["Content-Type"] = headers["Content-Type"] || "application/json";
            headers["X-CSRFToken"] = getCsrfToken();
        }

        const response = await fetch(url, {
            credentials: "include",
            ...options,
            headers,
        });
        const result = await response.json();

        if (!result.success) {
            alert(result.message);
            return returnRawResult ? result : false;
        }

        return returnRawResult ? result : true;
    } catch (error) {
        console.error("가족 연동 API 오류:", error);
        alert("가족 연동 처리 중 오류가 발생했습니다.");
        return returnRawResult ? null : false;
    }
}

async function renderRelationList(url, container, renderItem, emptyMessage) {
    if (!container) {
        return;
    }

    const result = await apiRequest(url, { method: "GET" }, true);
    if (!result || !result.success || result.data.length === 0) {
        container.innerHTML = `<p class="empty-message">${emptyMessage}</p>`;
        return;
    }

    container.innerHTML = result.data.map(renderItem).join("");
}

function renderReceivedRequest(relation) {
    const user = relation.user;

    return `
        <div class="request-item">
            <p>
                <strong>${escapeHtml(user.username)}</strong>
                <span>${escapeHtml(user.name || "")}</span>
            </p>
            <div class="button-group">
                <button
                    type="button"
                    class="btn btn-primary"
                    data-action="accept"
                    data-relation-id="${relation.id}"
                >
                    수락
                </button>
                <button
                    type="button"
                    class="btn btn-secondary"
                    data-action="reject"
                    data-relation-id="${relation.id}"
                >
                    거절
                </button>
            </div>
        </div>
    `;
}

function renderSentRequest(relation) {
    const user = relation.user;

    return `
        <div class="request-item">
            <p>
                <strong>${escapeHtml(user.username)}</strong>
                <span>${escapeHtml(user.name || "")}</span>
            </p>
            <span class="status-badge">${escapeHtml(relation.status)}</span>
        </div>
    `;
}

function renderFamily(relation) {
    const user = relation.user;

    return `
        <div class="family-item">
            <p>
                <strong>${escapeHtml(user.username)}</strong>
                <span>${escapeHtml(user.name || "")}</span>
            </p>
            <button
                type="button"
                class="btn btn-secondary disconnect-btn"
                data-relation-id="${relation.id}"
            >
                연동 해제
            </button>
        </div>
    `;
}

function escapeHtml(value) {
    return String(value)
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
}
