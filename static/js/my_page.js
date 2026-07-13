/* =====================================
   똑디 마이페이지
   static/js/my_page.js
===================================== */


document.addEventListener("DOMContentLoaded", function () {


    const buttons = document.querySelectorAll(".btn");


    buttons.forEach(function(button) {


        button.addEventListener("click", function() {

            this.classList.add("clicked");

        });


    });


});