document.addEventListener('DOMContentLoaded', () => {
    const guideId = window.location.pathname.split('/').filter(Boolean).pop();
    const content = document.getElementById('guideDetailContent');
    const statusText = document.getElementById('detailStatus');
    const title = document.getElementById('guideTitle');
    const meta = document.getElementById('guideMeta');
    const steps = document.getElementById('guideSteps');
    const stepNav = document.getElementById('stepNav');
    const stepNavArea = document.getElementById('stepNavArea');
    const backButton = document.getElementById('detailBackBtn');
    const saveButton = document.getElementById('saveBtn');
    const likeButton = document.getElementById('likeBtn');
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    backButton.addEventListener('click', () => {
        if (window.history.length > 1) {
            window.history.back();
        } else {
            window.location.href = '/guides/';
        }
    });

    function updateActionButton(button, active, activeText, inactiveText) {
        button.classList.toggle('active', active);
        button.querySelector('.action-label').textContent = active ? activeText : inactiveText;
    }

    function createStep(imageData, index) {
    const section = document.createElement('section');
    section.id = `step${index + 1}`;
    section.className = 'step-section';

    const card = document.createElement('div');
    card.className = 'step-card';

    // 이미지가 실제로 있을 때만 img 생성
    if (imageData.image) {
        const image = document.createElement('img');
        image.className = 'step-image';
        image.src = imageData.image;
        image.alt = `${index + 1}단계 이미지`;
        image.loading = 'lazy';
        card.appendChild(image);
    }

    // 이미지가 없어도 설명은 출력
    if (imageData.description) {
        const description = document.createElement('p');
        description.className = 'step-desc';
        description.textContent = imageData.description;
        card.appendChild(description);
    }

    section.appendChild(card);
    return section;
}

    function createStepLink(index) {
        const link = document.createElement('a');
        link.href = `#step${index + 1}`;
        link.className = `step-link${index === 0 ? ' active' : ''}`;
        link.textContent = String(index + 1);
        link.addEventListener('click', (event) => {
            event.preventDefault();
            document.querySelector(link.hash).scrollIntoView({ behavior: 'smooth', block: 'start' });
            stepNav.querySelectorAll('.step-link').forEach((item) => item.classList.remove('active'));
            link.classList.add('active');
        });
        return link;
    }

    async function toggleAction(action, button) {
        if (!window.DDOKDI_IS_AUTHENTICATED) {
            const next = encodeURIComponent(window.location.pathname);
            window.location.href = `${window.DDOKDI_LOGIN_URL}?next=${next}`;
            return;
        }

        button.disabled = true;
        try {
            const response = await fetch(`/api/guides/${guideId}/${action}/`, {
                method: 'POST',
                credentials: 'include',
                headers: {
                    Accept: 'application/json',
                    'X-CSRFToken': csrfToken,
                },
            });
            const body = await response.json();
            if (!response.ok || !body.success) {
                throw new Error(body.message || '요청을 처리하지 못했습니다.');
            }

            if (action === 'scrap') {
                updateActionButton(saveButton, body.data.is_scrapped, '저장 완료', '저장하기');
            } else {
                updateActionButton(likeButton, body.data.is_liked, '도움 완료', '도움이 됐어요');
            }
        } catch (error) {
            window.alert(error.message);
        } finally {
            button.disabled = false;
        }
    }

    saveButton.addEventListener('click', () => toggleAction('scrap', saveButton));
    likeButton.addEventListener('click', () => toggleAction('like', likeButton));

    async function loadGuide() {
        try {
            const response = await fetch(`/api/guides/${guideId}/`, {
                headers: { Accept: 'application/json' },
                credentials: 'include',
            });
            const body = await response.json();
            if (!response.ok || !body.success) {
                throw new Error(body.message || '설명서를 불러오지 못했습니다.');
            }

            const guide = body.data;
            document.title = `${guide.title} - 똑디`;
            title.textContent = guide.title;
            meta.textContent = `${guide.author} · 조회 ${guide.view_count}`;
            updateActionButton(saveButton, guide.is_scrapped, '저장 완료', '저장하기');
            updateActionButton(likeButton, guide.is_liked, '도움 완료', '도움이 됐어요');

            if (guide.images.length === 0) {
                const empty = document.createElement('p');
                empty.className = 'detail-empty';
                empty.textContent = '등록된 설명 단계가 없습니다.';
                steps.appendChild(empty);
                stepNavArea.hidden = true;
            } else {
                guide.images.forEach((imageData, index) => {
                    steps.appendChild(createStep(imageData, index));
                    stepNav.appendChild(createStepLink(index));
                });
            }

            statusText.hidden = true;
            content.hidden = false;
        } catch (error) {
            statusText.textContent = error.message || '설명서를 불러오지 못했습니다.';
        }
    }

    loadGuide();
});
