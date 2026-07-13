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



    // =========================
    // 가족 아이디 검색
    // =========================

    searchBtn.addEventListener("click", async function () {


        const username = searchInput.value.trim();



        if (username === "") {

            alert("검색할 아이디를 입력해주세요.");

            searchInput.focus();

            return;

        }



        try {

            const response = await fetch(
                `/api/families/users/?username=${username}`,
                {
                    method: "GET",
                    credentials: "include",
                }
            );


            const result = await response.json();



            if (!result.success || result.data.length === 0) {

                searchResult.innerHTML = `
                    <p>
                        사용자를 찾을 수 없습니다.
                    </p>
                `;

                return;

            }



            const user = result.data[0];



            // 검색 결과 출력
            searchResult.innerHTML = `

                <div class="result-card">

                    <p>
                        <strong>${user.username}</strong>님을 찾았습니다.
                    </p>


                    <button 
                        class="btn btn-secondary request-btn"
                        type="button"
                    >
                        가족 연동 요청 보내기
                    </button>

                </div>

            `;



            // 요청 보내기 버튼
            const requestBtn = document.querySelector(".request-btn");



            requestBtn.addEventListener("click", async function () {


                try {


                    const requestResponse = await fetch(
                        "/api/families/requests/",
                        {
                            method: "POST",
                            credentials: "include",
                            headers: {
                                "Content-Type": "application/json",
                            },
                            body: JSON.stringify({
                                username: user.username
                            }),
                        }
                    );



                    const requestResult = await requestResponse.json();



                    if (!requestResult.success) {

                        alert(requestResult.message);

                        return;

                    }



                    alert("가족 연동 요청을 보냈습니다.");

                    getSentRequests();



                } catch(error) {

                    console.error(
                        "가족 요청 오류:",
                        error
                    );

                }


            });



        } catch(error) {

            console.error(
                "사용자 검색 오류:",
                error
            );

        }


    });





    // =========================
    // 연결된 가족 목록 조회
    // =========================

    async function getFamilyList() {


        try {


            const response = await fetch(
                "/api/families/",
                {
                    method: "GET",
                    credentials: "include",
                }
            );


            const result = await response.json();


            console.log(
                "연결된 가족:",
                result
            );


        } catch(error) {


            console.error(
                "가족 목록 조회 실패:",
                error
            );


        }


    }





    // =========================
    // 받은 요청 조회
    // =========================

    async function getReceivedRequests() {


        try {


            const response = await fetch(
                "/api/families/requests/received/",
                {
                    method: "GET",
                    credentials: "include",
                }
            );


            const result = await response.json();


            console.log(
                "받은 요청:",
                result
            );


        } catch(error) {


            console.error(
                "받은 요청 조회 실패:",
                error
            );


        }


    }





    // =========================
    // 보낸 요청 조회
    // =========================

    async function getSentRequests() {


        try {


            const response = await fetch(
                "/api/families/requests/sent/",
                {
                    method: "GET",
                    credentials: "include",
                }
            );


            const result = await response.json();


            console.log(
                "보낸 요청:",
                result
            );


        } catch(error) {


            console.error(
                "보낸 요청 조회 실패:",
                error
            );


        }


    }





    // 페이지 접속 시 실행

    getFamilyList();

    getReceivedRequests();

    getSentRequests();



});