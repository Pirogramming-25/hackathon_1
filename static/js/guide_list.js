/* static/js/guide_list.js */

document.addEventListener('DOMContentLoaded', () => {
    
    // ==========================
    // 필터 버튼 활성화 토글 기능
    // ==========================
    
    const filterBtns = document.querySelectorAll('.filter-btn');
    
    filterBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            // 1. 모든 버튼에서 'active' 클래스를 제거합니다.
            filterBtns.forEach(b => b.classList.remove('active'));
            
            // 2. 현재 클릭한 버튼에만 'active' 클래스를 추가합니다.
            btn.classList.add('active');
            
            // 프론트 시연용 확인 코드 (콘솔창)
            console.log(`${btn.textContent} 정렬 선택됨`);
        });
    });

});