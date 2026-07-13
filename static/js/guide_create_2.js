/* static/js/guid_create_2.js */

document.addEventListener('DOMContentLoaded', function() {
    const canvasContainer = document.getElementById('canvasContainer');
    const mainImage = document.getElementById('mainImage');
    const saveCompleteBtn = document.getElementById('saveCompleteBtn');

    // [프론트엔드 테스트용] 임시 이미지 삽입
    // 백엔드와 연결하여 실제 이미지가 들어올 때는 아래 한 줄을 지워주세요!
    mainImage.src = 'https://via.placeholder.com/800x450.png?text=클릭해서+주석을+달아보세요';

    // 1. 캔버스 클릭 시 주석(동그라미+텍스트박스) 추가
    canvasContainer.addEventListener('click', function(e) {
        // 이미 생성된 주석 래퍼(동그라미, 입력창, 버튼)를 클릭했을 때는 새 주석이 안 생기게 방지
        if (e.target.closest('.annotation-wrapper')) {
            return;
        }

        // 클릭한 위치 (컨테이너 기준 좌표) 계산
        const rect = canvasContainer.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;

        // 주석 요소들을 하나로 묶어줄 래퍼(Wrapper) 생성
        const wrapper = document.createElement('div');
        wrapper.className = 'annotation-wrapper';
        wrapper.style.position = 'absolute';
        wrapper.style.left = `${x}px`;
        wrapper.style.top = `${y}px`;
        // 동그라미 중심을 클릭한 곳에 맞추기 위해 래퍼 자체 크기는 0으로 설정
        wrapper.style.width = '0';
        wrapper.style.height = '0';
        wrapper.style.zIndex = '10';

        // ① 빨간 동그라미 생성
        const circle = document.createElement('div');
        circle.className = 'annotation-circle';

        // ② 텍스트 입력창 생성
        const input = document.createElement('input');
        input.type = 'text';
        input.className = 'annotation-input';
        input.placeholder = '설명을 입력하세요';
        
        // 입력창 클릭 시 버블링 방지 (타이핑 하려고 클릭했을 때 새 동그라미 안 생기게)
        input.addEventListener('click', function(e) {
            e.stopPropagation();
        });

        // ③ 삭제(X) 버튼 생성
        const deleteBtn = document.createElement('button');
        deleteBtn.className = 'annotation-delete';
        deleteBtn.innerHTML = 'X';
        deleteBtn.title = '주석 삭제';
        // X 버튼 위치 조정 (동그라미의 우측 상단)
        deleteBtn.style.top = '-40px';
        deleteBtn.style.left = '20px';
        
        deleteBtn.addEventListener('click', function(e) {
            e.stopPropagation();
            wrapper.remove(); // 래퍼(주석 세트) 전체 삭제
        });

        // 래퍼에 조립
        wrapper.appendChild(circle);
        wrapper.appendChild(input);
        wrapper.appendChild(deleteBtn);

        // 캔버스에 추가
        canvasContainer.appendChild(wrapper);

        // 주석이 생성되자마자 바로 글씨를 쓸 수 있게 포커스!
        input.focus();
    });

    // 2. 완성하기 버튼 클릭 이벤트
    saveCompleteBtn.addEventListener('click', function() {
        // 화면에 있는 모든 텍스트 입력창 가져오기
        const annotations = document.querySelectorAll('.annotation-input');
        let isAllFilled = true;
        
        annotations.forEach(input => {
            if(input.value.trim() === '') {
                isAllFilled = false;
            }
        });

        // 주석을 달았는데 글씨를 안 쓴 경우 막기
        if (!isAllFilled && annotations.length > 0) {
            alert('비어있는 주석이 있습니다. 설명을 모두 입력해주세요!');
            return;
        }

        // 실제로는 여기서 캔버스 위의 좌표(x, y)와 텍스트들을 모아서 백엔드로(form submit) 전송합니다.
        alert('설명서가 성공적으로 완성되었습니다! 🎉 (프론트 시연용)');
        
        // window.location.href = '/guides/list'; // 완료 후 목록 페이지로 이동 처리
    });
});