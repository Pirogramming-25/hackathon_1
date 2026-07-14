# hackathon_1
피로그래밍 25기 해커톤 1조 레포입니다.
# 똑디 (DDOKDI)

> **디지털 사용이 막막한 순간, 화면을 보며 한 단계씩 따라가는 디지털 설명서 플랫폼**

피로그래밍 25기 해커톤 **1조** 프로젝트입니다.

`똑디`는 **똑똑한 디지털 설명서**의 줄임말입니다.  
디지털 서비스 이용에 어려움을 겪는 사용자가 이미지 중심 설명서를 찾아보고, 필요한 설명서가 없으면 질문을 등록하며, 유용한 답변을 다시 설명서로 축적할 수 있도록 만들었습니다.

---

## 🔥 기획 배경

병원 예약, 금융 업무, 정부 서비스 신청 등 일상적인 절차가 빠르게 온라인으로 전환되고 있습니다. 하지만 디지털 환경에 익숙하지 않은 사용자에게는 작은 버튼 하나를 찾는 일도 큰 장벽이 됩니다.

기존의 텍스트 중심 안내는 실제 화면에서 **어디를 눌러야 하는지** 전달하기 어렵고, 같은 문제가 반복해서 질문되는 한계가 있습니다. 똑디는 화면 이미지, 단계별 설명, 이미지 주석 기능을 결합하고, 한 번 해결된 답변을 재사용 가능한 설명서로 전환합니다.

---

## 🔄 핵심 흐름

```text
설명서 검색
    ↓
단계별 이미지 설명서 확인
    ↓
원하는 설명서가 없으면 질문 등록
    ↓
다른 사용자가 이미지와 함께 답변
    ↓
질문 작성자가 답변 선택
    ↓
답변을 새로운 설명서로 승격
```

단순한 Q&A에서 끝나지 않고, **한 사람의 해결 경험을 모두가 활용할 수 있는 설명서로 남기는 것**이 핵심입니다.

---

## ✨ 주요 기능

### 1. 단계별 이미지 설명서

- 제목·단계 설명·카테고리 기반 검색
- 최신순·도움순·저장순 정렬 및 페이지네이션
- 단계별 이미지와 설명 제공
- 공개 설명서는 비회원도 조회 가능
- 설명서 좋아요, 저장, 조회 수 제공

### 2. 이미지 주석 기반 작성

- 설명서 이미지를 최대 20장까지 단계별 등록
- 동그라미, 화살표, 안내 문구 추가
- 실행 취소, 전체 지우기, 원본 복원
- Canvas 편집 결과를 이미지에 합성해 서버 저장
- JPG, JPEG, PNG, WEBP 지원 및 파일당 5MB 제한

### 3. 질문·답변과 설명서 승격

- 질문당 최대 5장, 답변당 최대 4장의 이미지 첨부
- 이미지별 설명과 노출 순서 관리
- 질문 작성자의 해결 완료 처리
- 답변 작성자의 답변 수정·삭제
- 질문 작성자가 답변 하나를 선택
- 답변 본문과 이미지를 새로운 설명서 단계로 복사
- 하나의 질문에서 하나의 설명서만 생성

### 4. 개인 저장소와 마이페이지

- 내가 만든 설명서 조회
- 저장한 설명서 조회
- 내가 등록한 질문 조회
- 내가 작성한 답변 API 제공
- 회원 정보 및 비밀번호 변경
- 기본 모드·쉬운 모드 설정

### 5. 가족 연동과 비공개 공유

- 아이디 기반 사용자 검색
- 가족 요청 전송·수락·거절·해제
- 수락된 가족 관계에 따른 비공개 설명서 접근
- 특정 가족 사용자에게 설명서 개별 공유

---

## 🛠 기술 스택

| 구분 | 기술 |
|---|---|
| Backend | Python 3.12, Django 4.2.30, Django REST Framework 3.16.1 |
| Frontend | Django Template, Vanilla JavaScript, HTML5, CSS3, Canvas API |
| Authentication | Django Session Authentication, CSRF |
| Database | SQLite(Local), PostgreSQL(Deploy) |
| Storage | Local FileSystem, Cloudinary |
| Deployment | Gunicorn, WhiteNoise, Docker, Docker Compose |
| Collaboration | Git, GitHub, Notion |

---

## ⚙️ 핵심 기술 구현

- **서버 렌더링과 REST API 결합**  
  Django Template로 페이지를 구성하고, Vanilla JavaScript에서 DRF API를 호출합니다.

- **이미지 주석 합성**  
  Canvas API로 동그라미·화살표·텍스트를 그린 뒤 결과를 새로운 이미지 파일로 변환해 업로드합니다.

- **데이터 무결성 보장**  
  데이터베이스 제약조건으로 질문당 하나의 선택 답변만 허용하고, 승격된 설명서와 원본 답변을 `OneToOneField`로 연결합니다.

- **트랜잭션 기반 이미지 저장**  
  질문·답변·설명서 생성 및 답변 승격 과정을 트랜잭션으로 처리해 일부 데이터만 저장되는 문제를 방지합니다.

- **권한 기반 설명서 조회**  
  공개 여부, 작성자, 가족 관계, 개별 공유 여부를 기준으로 서버에서 조회 권한을 제한합니다.

- **검색 및 목록 최적화**  
  `Q`, `Count`, `Exists`, `OuterRef`, `select_related`, `prefetch_related`를 활용해 검색·정렬·좋아요·저장 상태를 처리합니다.

- **환경별 저장소 전환**  
  로컬에서는 SQLite와 파일 시스템을 사용하고, 배포 환경에서는 `DATABASE_URL`과 Cloudinary 설정에 따라 PostgreSQL·외부 이미지 저장소로 전환됩니다.

---

## 📂 프로젝트 구조

```text
hackathon_1/
├── accounts/      # 회원가입, 로그인, 사용자 정보
├── families/      # 가족 요청 및 관계 관리
├── guides/        # 설명서, 단계 이미지, 좋아요, 저장, 공유
├── questions/     # 질문, 답변, 선택 및 설명서 승격
├── config/        # 프로젝트 설정, URL, 공통 예외 처리
├── templates/     # Django 페이지 템플릿
├── static/        # CSS, JavaScript, 이미지 주석 편집기
├── Dockerfile
├── docker-compose.yml
├── manage.py
└── requirements.txt
```

---

## 🔌 주요 API

| Method | Endpoint | 기능 |
|---|---|---|
| `GET`, `POST` | `/api/guides/` | 설명서 목록 조회 및 등록 |
| `GET`, `PATCH`, `DELETE` | `/api/guides/<id>/` | 설명서 상세, 수정, 삭제 |
| `POST` | `/api/guides/<id>/like/` | 좋아요 토글 |
| `POST` | `/api/guides/<id>/scrap/` | 저장 토글 |
| `GET`, `POST` | `/api/questions/` | 질문 목록 조회 및 등록 |
| `POST` | `/api/questions/<id>/answers/` | 답변 등록 |
| `PATCH` | `/api/answers/<id>/accept/` | 답변 선택 |
| `POST` | `/api/guides/answers/<answer_id>/promote/` | 답변을 설명서로 승격 |
| `GET` | `/api/users/me/guides/` | 내가 만든 설명서 조회 |
| `GET` | `/api/users/me/scraps/` | 저장한 설명서 조회 |
| `GET`, `POST`, `PATCH`, `DELETE` | `/api/families/` | 가족 관계 관리 |

---

## 👥 팀 구성

| 이름 | 역할 | 담당 |
|---|---|---|
| **신예원** | 팀장 / Frontend | 홈·검색, 설명서 목록·상세·작성, 개인 저장소, 프로젝트 발표 |
| **김유겸** | Backend | 설명서·단계 이미지, 좋아요·저장, 나의 저장소 API |
| **임현아** | Frontend | 로그인·회원가입, 회원 정보, 가족 연동 화면 |
| **김민서** | Backend | 회원·세션 인증, 가족 관계 API, 초기 구조 설계, 배포 |
| **이주헌** | Backend / Frontend | 질문·답변 화면, 답변 선택·설명서 승격, 이미지 주석 연동 구현 등 |

---

## 🚀 실행 방법

### 로컬 실행

```bash
git clone https://github.com/Pirogramming-25/hackathon_1.git
cd hackathon_1

python -m venv venv
source venv/Scripts/activate   # Windows Git Bash
# source venv/bin/activate     # macOS / Linux

pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py runserver
```

접속 주소: `http://127.0.0.1:8000/`

### Docker 실행

```bash
cp .env.example .env
docker compose up --build
```

### 테스트

```bash
python manage.py test
```

---

## 🎯 프로젝트 목표

똑디는 디지털 사용법을 설명하는 데서 끝나지 않습니다.  
한 사용자의 질문과 다른 사용자의 답변이 새로운 설명서가 되고, 그 설명서가 또 다른 사용자의 어려움을 줄이는 선순환을 만듭니다.

> **한 사람의 해결 경험을 모두가 따라 할 수 있는 설명서로 만듭니다.**
> **💡 한 사람의 해결 경험을 모두가 따라 할 수 있는 설명서로 만듭니다.**
