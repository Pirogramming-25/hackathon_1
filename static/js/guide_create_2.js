/* static/js/guide_create_2.js */

document.addEventListener('DOMContentLoaded', function() {
    const mainImage = document.getElementById('mainImage');
    const annotateBtn = document.getElementById('annotateImageBtn');
    const saveCompleteBtn = document.getElementById('saveCompleteBtn');

    // [프론트엔드 테스트용] 임시 이미지 삽입
    // 백엔드/썸네일 연동 로직에서 실제 이미지가 들어올 때는 아래 한 줄을 지워주세요!
    mainImage.src = 'https://picsum.photos/800/450';

    // 현재 화면에 표시된 이미지에 주석(동그라미/화살표/텍스트)이 반영된 결과 파일.
    // 편집 안 했으면 null — 원본 그대로 업로드하면 됩니다.
    // 실제 제출(업로드) 로직에서는 이 값이 있으면 그걸, 없으면 원본 파일을 uploaded_images로 보내면 됩니다.
    // (썸네일별로 관리하려면 이미지 index를 key로 하는 객체로 바꿔서 써주세요.)
    window.currentGuideImageBakedFile = null;

    annotateBtn.addEventListener('click', async function() {
        const originalText = annotateBtn.textContent;
        annotateBtn.disabled = true;
        annotateBtn.textContent = '이미지 불러오는 중...';

        try {
            // 현재 표시된 이미지를 File 객체로 변환
            // (원본이 <input type="file">에서 온 File이든, blob: URL이든, 지금처럼
            //  테스트용 외부 URL이든 상관없이 동일하게 동작합니다.)
            const response = await fetch(mainImage.src);
            const blob = await response.blob();
            const currentFile = new File(
                [blob],
                'guide_image.png',
                { type: blob.type || 'image/png' }
            );

            annotateBtn.disabled = false;
            annotateBtn.textContent = originalText;

            const bakedFile = await openImageAnnotator(currentFile);

            if (!bakedFile) {
                return; // 취소한 경우 원본 유지
            }

            mainImage.src = URL.createObjectURL(bakedFile);
            window.currentGuideImageBakedFile = bakedFile;
        } catch (error) {
            console.error('이미지 불러오기 오류:', error);
            alert('이미지를 불러오지 못해 주석을 편집할 수 없습니다.');
            annotateBtn.disabled = false;
            annotateBtn.textContent = originalText;
        }
    });

    // 완성하기 버튼 클릭 이벤트
    saveCompleteBtn.addEventListener('click', function() {
        // 실제로는 여기서 window.currentGuideImageBakedFile(또는 원본 파일)과
        // 하단 설명(#bottomDesc)을 모아서 백엔드로 전송합니다.
        alert('설명서가 성공적으로 완성되었습니다! 🎉 (프론트 시연용)');

        // window.location.href = '/guides/list'; // 완료 후 목록 페이지로 이동 처리
    });
});