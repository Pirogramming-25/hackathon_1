/* static/js/guide_list.js */

document.addEventListener('DOMContentLoaded', () => {
    const searchInput = document.getElementById('guideSearchInput');
    const guideGrid = document.getElementById('guideGrid');
    const statusText = document.getElementById('guideListStatus');
    const filterBtns = document.querySelectorAll('.filter-btn');
    const params = new URLSearchParams(window.location.search);
    const keyword = (params.get('q') || '').trim();
    let currentSort = 'latest';

    searchInput.value = keyword;

    function createGuideCard(guide) {
        const card = document.createElement('a');
        card.className = 'guide-card';
        card.href = `/api/guides/${guide.id}/`;

        const imageWrap = document.createElement('div');
        imageWrap.className = 'card-image-placeholder';

        if (guide.images && guide.images.length > 0) {
            const image = document.createElement('img');
            image.src = guide.images[0].image;
            image.alt = `${guide.title} 대표 이미지`;
            image.loading = 'lazy';
            imageWrap.appendChild(image);
        } else {
            const icon = document.createElement('span');
            icon.className = 'material-symbols-rounded card-placeholder-icon';
            icon.textContent = 'description';
            imageWrap.appendChild(icon);
        }

        const title = document.createElement('h3');
        title.className = 'card-title';
        title.textContent = guide.title;

        card.append(imageWrap, title);
        return card;
    }

    async function loadGuides() {
        guideGrid.replaceChildren();
        statusText.hidden = false;
        statusText.textContent = '설명서를 불러오는 중입니다.';

        const apiParams = new URLSearchParams({ sort: currentSort });
        if (keyword) {
            apiParams.set('search', keyword);
        }

        try {
            const response = await fetch(`/api/guides/?${apiParams.toString()}`, {
                headers: { Accept: 'application/json' },
                credentials: 'include',
            });
            const body = await response.json();

            if (!response.ok || !body.success) {
                throw new Error(body.message || '설명서 목록을 불러오지 못했습니다.');
            }

            const payload = body.data || {};
            const guides = Array.isArray(payload) ? payload : (payload.results || []);

            if (guides.length === 0) {
                statusText.textContent = keyword
                    ? `'${keyword}'에 해당하는 설명서가 없습니다.`
                    : '등록된 설명서가 없습니다.';
                return;
            }

            statusText.hidden = true;
            guides.forEach((guide) => guideGrid.appendChild(createGuideCard(guide)));
        } catch (error) {
            statusText.textContent = error.message || '설명서 목록을 불러오지 못했습니다.';
        }
    }

    filterBtns.forEach((btn) => {
        btn.addEventListener('click', () => {
            filterBtns.forEach((item) => item.classList.remove('active'));
            btn.classList.add('active');
            currentSort = btn.dataset.sort;
            loadGuides();
        });
    });

    loadGuides();
});
