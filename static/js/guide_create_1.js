/* static/js/guide_create_1.js */

document.addEventListener('DOMContentLoaded', function() {
    const imageInput = document.getElementById('imageInput');
    const previewArea = document.getElementById('previewArea');
    const nextBtn = document.querySelector('.next-btn');
    const form = document.querySelector('.guide-form');

    // 1. 파일 선택 및 미리보기 생성
    imageInput.addEventListener('change', function(e) {
        const files = Array.from(e.target.files);

        // 20장 제한 확인
        if (files.length > 20) {
            alert('사진은 최대 20장까지만 업로드할 수 있습니다.');
            // 20장까지만 잘라서 다시 input에 담기
            const dataTransfer = new DataTransfer();
            files.slice(0, 20).forEach(file => dataTransfer.items.add(file));
            imageInput.files = dataTransfer.files;
        }

        // 기존 미리보기 초기화
        previewArea.innerHTML = '';

        const finalFiles = Array.from(imageInput.files);

        finalFiles.forEach((file, index) => {
            const reader = new FileReader();

            reader.onload = function(e) {
                // 미리보기 카드 생성
                const previewWrapper = document.createElement('div');
                previewWrapper.style.position = 'relative';
                previewWrapper.style.width = '120px';
                previewWrapper.style.height = '120px';
                previewWrapper.style.borderRadius = '12px';
                previewWrapper.style.overflow = 'hidden';
                previewWrapper.style.boxShadow = 'var(--shadow-card)';
                previewWrapper.style.border = '1px solid var(--color-border)';

                // 이미지 생성
                const img = document.createElement('img');
                img.src = e.target.result;
                img.style.width = '100%';
                img.style.height = '100%';
                img.style.objectFit = 'cover';

                // 삭제 버튼 생성
                const deleteBtn = document.createElement('button');
                deleteBtn.innerHTML = '<span class="material-symbols-rounded" style="font-size: 16px;">close</span>';
                deleteBtn.style.position = 'absolute';
                deleteBtn.style.top = '4px';
                deleteBtn.style.right = '4px';
                deleteBtn.style.width = '24px';
                deleteBtn.style.height = '24px';
                deleteBtn.style.backgroundColor = 'rgba(0, 0, 0, 0.6)';
                deleteBtn.style.color = 'white';
                deleteBtn.style.border = 'none';
                deleteBtn.style.borderRadius = '50%';
                deleteBtn.style.cursor = 'pointer';
                deleteBtn.style.display = 'flex';
                deleteBtn.style.alignItems = 'center';
                deleteBtn.style.justifyContent = 'center';

                // X 버튼 클릭 시 해당 파일 제거
                deleteBtn.onclick = function(event) {
                    event.preventDefault(); // 폼 제출 방지
                    
                    const dt = new DataTransfer();
                    const currentFiles = Array.from(imageInput.files);
                    
                    // 현재 클릭된 요소 제외하고 다시 담기
                    currentFiles.splice(index, 1);
                    currentFiles.forEach(f => dt.items.add(f));
                    imageInput.files = dt.files;
                    
                    // 화면에서 요소 지우기
                    previewWrapper.remove();
                };

                previewWrapper.appendChild(img);
                previewWrapper.appendChild(deleteBtn);
                previewArea.appendChild(previewWrapper);
            };

            reader.readAsDataURL(file);
        });
    });

    // 2. '다음 단계' 버튼 클릭 시 유효성 검사 및 폼 제출
    nextBtn.addEventListener('click', function(e) {
        e.preventDefault(); // 기본 링크 이동(a 태그) 막기
        
        const title = document.getElementById('title').value.trim();
        const category = document.getElementById('category').value;
        
        if (!title) {
            alert('설명서 제목을 입력해주세요.');
            document.getElementById('title').focus();
            return;
        }
        
        if (category === '분야를 선택해주세요.') {
            alert('분야를 선택해주세요.');
            document.getElementById('category').focus();
            return;
        }
        
        if (imageInput.files.length === 0) {
            alert('최소 1장 이상의 화면 사진을 추가해주세요.');
            return;
        }
        
        // 데이터가 장고로 안전하게 넘어가도록 폼 서밋 실행
        form.submit();
    });
});