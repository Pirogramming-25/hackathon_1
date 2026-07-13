// ============ 홈(검색화면) 전용 JS ============

document.addEventListener('DOMContentLoaded', function () {
  var searchInput = document.getElementById('searchInput');
  var hintChips = document.querySelectorAll('.hint-chip');
  var quickAskBtn = document.getElementById('quickAskBtn');

  // 힌트 예시를 누르면 검색창에 바로 채워주기 (노인 사용자가 직접 타이핑하지 않아도 되게)
  hintChips.forEach(function (chip) {
    chip.addEventListener('click', function () {
      var fillText = chip.getAttribute('data-fill');
      if (searchInput && fillText) {
        searchInput.value = fillText;
        searchInput.focus();
      }
    });
  });

  // '+' 버튼: 질문을 바로 등록하고 싶을 때 누르는 버튼
  // 로그인 상태면 질문 등록 페이지로, 비로그인이면 로그인 페이지(?next=)로 이동
  if (quickAskBtn) {
    quickAskBtn.addEventListener('click', function () {
      if (window.DDOKDI_IS_AUTHENTICATED) {
        window.location.href = window.DDOKDI_QUESTION_CREATE_URL;
      } else {
        window.location.href =
          window.DDOKDI_LOGIN_URL + '?next=' + encodeURIComponent(window.DDOKDI_QUESTION_CREATE_URL);
      }
    });
  }
});