/* static/js/guide_list.js */

document.addEventListener('DOMContentLoaded', () => {
    const searchInput = document.getElementById('guideSearchInput');
    const searchForm = document.getElementById('guideSearchForm');
    const backButton = document.getElementById('guideBackBtn');
    const guideGrid = document.getElementById('guideGrid');
    const pageTitle = document.getElementById('guideListTitle');
    const emptyContainer = document.getElementById('guideListEmpty');
    const statusText = document.getElementById('guideListStatus');
    const questionGoButton = document.getElementById('questionGoBtn');
    const filterBtns = document.querySelectorAll('.filter-btn');
    const pagination = document.getElementById('guidePagination');
    const prevPageButton = document.getElementById('prevPageBtn');
    const nextPageButton = document.getElementById('nextPageBtn');
    const currentPageText = document.getElementById('currentPageText');
    const params = new URLSearchParams(window.location.search);
    let keyword = (params.get('q') || '').trim();
    let currentSort = 'latest';
    let currentPage = 1;
    let searchTimer = null;
    let requestController = null;

    pageTitle.textContent = '설명서 목록';
    document.title = '설명서 목록 - 똑디';

    backButton.addEventListener('click', () => {
        if (window.history.length > 1) {
            window.history.back();
            return;
        }

        window.location.href = '/';
    });

    searchInput.value = keyword;

    searchForm.addEventListener('submit', (event) => {
        event.preventDefault();
        window.clearTimeout(searchTimer);
        applySearch(searchInput.value);
    });

    searchInput.addEventListener('input', () => {
        window.clearTimeout(searchTimer);
        searchTimer = window.setTimeout(() => {
            applySearch(searchInput.value);
        }, 300);
    });

    function applySearch(value) {
        const nextKeyword = value.trim();
        if (nextKeyword === keyword) {
            return;
        }

        keyword = nextKeyword;
        const nextUrl = keyword
            ? `/guides/?q=${encodeURIComponent(keyword)}`
            : '/guides/';
        window.history.replaceState({}, '', nextUrl);
        loadGuides(1);
    }

    function createGuideCard(guide) {
        const card = document.createElement('a');
        card.className = 'guide-card';
        card.href = `/guides/${guide.id}/`;

        const imageWrap = document.createElement('div');
        imageWrap.className = 'card-image-placeholder';

        const visibility = document.createElement('span');
        visibility.className = `visibility-badge ${guide.visibility === 'PRIVATE' ? 'is-private' : 'is-public'}`;
        visibility.textContent = guide.visibility === 'PRIVATE' ? '비공개' : '공개';
        imageWrap.appendChild(visibility);

        const thumbnailUrl = guide.images?.[0]?.image;

        if (thumbnailUrl) {
            const image = document.createElement('img');
            image.src = thumbnailUrl;
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

    async function loadGuides(page = 1) {
        if (requestController) {
            requestController.abort();
        }
        requestController = new AbortController();

        guideGrid.replaceChildren();
        pagination.hidden = true;
        emptyContainer.hidden = false;
        questionGoButton.hidden = true;
        statusText.hidden = false;
        statusText.textContent = '설명서를 불러오는 중입니다.';

        const apiParams = new URLSearchParams({
            sort: currentSort,
            page: String(page),
        });
        if (keyword) {
            apiParams.set('search', keyword);
        }

        try {
            const response = await fetch(`/api/guides/?${apiParams.toString()}`, {
                headers: { Accept: 'application/json' },
                credentials: 'include',
                signal: requestController.signal,
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
                questionGoButton.hidden = false;
                return;
            }

            statusText.hidden = true;
            emptyContainer.hidden = true;
            guides.forEach((guide) => guideGrid.appendChild(createGuideCard(guide)));

            currentPage = page;
            const pageSize = payload.page_size || guides.length;
            const totalPages = Math.max(1, Math.ceil(payload.count / pageSize));
            currentPageText.textContent = `${currentPage} / ${totalPages}`;
            prevPageButton.disabled = !payload.previous;
            nextPageButton.disabled = !payload.next;
            pagination.hidden = !payload.previous && !payload.next;
        } catch (error) {
            if (error.name === 'AbortError') {
                return;
            }
            statusText.textContent = error.message || '설명서 목록을 불러오지 못했습니다.';
        }
    }

    filterBtns.forEach((btn) => {
        btn.addEventListener('click', () => {
            filterBtns.forEach((item) => item.classList.remove('active'));
            btn.classList.add('active');
            currentSort = btn.dataset.sort;
            loadGuides(1);
        });
    });

    prevPageButton.addEventListener('click', () => {
        if (currentPage > 1) {
            loadGuides(currentPage - 1);
            window.scrollTo({ top: 0, behavior: 'smooth' });
        }
    });

    nextPageButton.addEventListener('click', () => {
        loadGuides(currentPage + 1);
        window.scrollTo({ top: 0, behavior: 'smooth' });
    });

    loadGuides(1);
});
