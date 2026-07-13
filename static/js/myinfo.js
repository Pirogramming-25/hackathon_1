/* =====================================
   똑디 나의 정보 페이지
   static/js/myinfo.js
===================================== */


document.addEventListener("DOMContentLoaded", function () {


    const editButtons = document.querySelectorAll(".edit-btn");



    editButtons.forEach(function (button) {


        button.addEventListener("click", function () {


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


                alert("정보가 저장되었습니다.");


            }



        });


    });


});